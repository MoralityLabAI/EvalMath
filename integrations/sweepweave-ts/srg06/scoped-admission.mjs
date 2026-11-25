// SRG-06: route-scoped temporal admission for the signed SRG/2 runtime.
// This adapter preserves original wild windows. It is opt-in and must be
// bound to a pinned source by the caller's manifest/hash verification.
import {stepV2} from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';

const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const numericOnly=node=>node.op!=="pointer"||!node.key.startsWith("__srg.");
function walk(node){return numericOnly(node)&&(node.args??[]).every(walk);}
export function directWindowManifest(world){
  const pages=Object.values(world.pages),earliest=Object.fromEntries(pages.map(p=>[p.id,Infinity]));
  earliest[world.start]=world.turnBase;
  for(let i=0;i<pages.length;i++)for(const p of pages)for(const o of Object.values(p.options))for(const r of o.reactions){
    if(r.to!=="wild")earliest[r.to]=Math.min(earliest[r.to],earliest[p.id]+1);
  }
  const windows=pages.filter(p=>Number.isFinite(earliest[p.id])&&earliest[p.id]<p.lo).map(p=>({id:p.id,original_earliest:p.lo,direct_earliest:earliest[p.id],latest:p.hi}));
  return {profile:"SRG06/direct-window/1",world_id:world.id,turn_base:world.turnBase,
    derivation:"shortest direct-edge path from start, ignoring guard feasibility and wild edges",
    wild_policy:"original windows unchanged",windows};
}
export function makeScopedStepper(world,manifest){
  if(world.direct!=="explicit"||JSON.stringify(manifest)!==JSON.stringify(directWindowManifest(world)))throw Error("SRG06: manifest does not match world");
  const lower=Object.fromEntries(manifest.windows.map(p=>[p.id,p.direct_earliest]));
  const reactions=new Map();
  for(const p of Object.values(world.pages)){
    if(!walk(p.gate))throw Error("SRG06: scoped adapter requires numeric-only encounter admission predicates");
    for(const o of Object.values(p.options))for(const r of o.reactions)reactions.set(r.id,r);
  }
  return (state,action)=>{
    const branch=stepV2(world,state,action),r=reactions.get(branch.id),target=world.pages[branch.next.encounter],n=branch.next;
    if(branch.guard_admitted)return {...branch,scoped_admission:{admitted:true,exception:null}};
    if(r.to==="wild"||r.to!==target.id||!own(lower,target.id)||n.turn>=target.lo||n.turn<lower[target.id]||n.turn>target.hi||
      !Object.values(world.spools).some(sp=>n.spools[sp.id]&&sp.members.includes(target.id))||
      !evaluate(target.gate,n.values))throw Error("SRG06: scoped admission blocked");
    return {...branch,scoped_admission:{admitted:true,exception:"direct_early_window",original_earliest:target.lo,direct_earliest:lower[target.id],arrival:n.turn}};
  };
}
