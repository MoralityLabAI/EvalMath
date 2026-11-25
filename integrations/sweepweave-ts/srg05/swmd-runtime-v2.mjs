// SWMD-SRG/2: narrative, spools, explicit wild resolver and event history.
// Uses the reviewed SRG/1 typed signed-expression evaluator, no legacy stubs.
import { parseExpression, evaluate } from '../srg04/swmd-runtime.mjs';

const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const dict=()=>Object.create(null);
const ID=/^[A-Za-z_][\w-]*$/;
const KEY=/^[A-Za-z_][\w-]*\.[A-Za-z_][\w-]*(?:\[[A-Za-z_][\w-]*\]){0,2}$/;
const fail=m=>{throw Error("SWMD-SRG/2: "+m);};
const copy=x=>JSON.parse(JSON.stringify(x));
const bounded=x=>{if(typeof x!=="number"||!Number.isFinite(x)||Math.abs(x)>1)fail("invalid BNumber");return x;};
const freeze=x=>{if(x&&typeof x==="object"&&!Object.isFrozen(x)){Object.values(x).forEach(freeze);Object.freeze(x);}return x;};
const text=s=>{let x;try{x=JSON.parse(s);}catch{fail("invalid JSON prose");}if(typeof x!=="string")fail("expected prose string");return x;};
const reserved=k=>k.startsWith("__srg.");
const meta=(kind,id)=>"__srg."+kind+"_"+id;
const refs=(s)=>s.replace(/\b(SEEN|ACTIVE)\(\s*([A-Za-z_][\w-]*)\s*\)/g,(_,kind,id)=>"EQ(P("+meta(kind,id)+"),C(1))");

export function compileV2(source){
  if(typeof source!=="string"||source.length>4_000_000)fail("invalid source size");
  const lines=source.replace(/^\uFEFF/,"").split(/\r?\n/).map(s=>s.trim()).filter(Boolean);
  if(lines.shift()!=="# SWMD-SRG/2")fail("expected SWMD-SRG/2");
  const w={profile:"SWMD-SRG/2",source,coordinates:dict(),spools:dict(),pages:dict(),events:[]};
  const declared=new Set(), virtual=dict(), event=id=>{if(!ID.test(id)||id==="wild"||declared.has(id))fail("duplicate/invalid event "+id);declared.add(id);virtual[meta("SEEN",id)]={};};
  // Prescan event and spool IDs for forward references. No user-declared meta keys.
  for(const l of lines){let m;
    if((m=l.match(/^SPOOL (\S+) \|/))){if(!ID.test(m[1])||own(virtual,meta("ACTIVE",m[1])))fail("invalid spool ID");virtual[meta("ACTIVE",m[1])]={};}
    else if((m=l.match(/^ENC (\S+) /)))event(m[1]);
    else if((m=l.match(/^OPT (\S+) \|/)))event(m[1]);
    else if((m=l.match(/^ORX \S+\/(\S+) ->/)))event(m[1]);
  }
  w.events=[...declared];
  const expr=(s,t)=>parseExpression(refs(s),{...w.coordinates,...virtual},t);
  let page=null;
  const header=(k,v)=>{if(page||own(w,k))fail("duplicate/late "+k);w[k]=v;};
  for(const l of lines){let m;
    if((m=l.match(/^(id|start): (\S+)$/))){if(!ID.test(m[2]))fail("bad ID");header(m[1],m[2]);continue;}
    if((m=l.match(/^(title|about): (.+)$/))){header(m[1],text(m[2]));continue;}
    if((m=l.match(/^turn-base: ([01])$/))){header("turnBase",Number(m[1]));continue;}
    if((m=l.match(/^tie: (first|last)$/))){header("tie",m[1]);continue;}
    if((m=l.match(/^direct: (strict|explicit)$/))){header("direct",m[1]);continue;}
    if((m=l.match(/^VAR (\S+) = (\S+) \| (public|hidden)$/))){
      if(page||!KEY.test(m[1])||reserved(m[1])||own(w.coordinates,m[1])||!/^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?$/.test(m[2]))fail("invalid variable "+m[1]);
      w.coordinates[m[1]]={initial:bounded(Number(m[2])),literal:m[2],visibility:m[3]};continue;
    }
    if((m=l.match(/^SPOOL (\S+) \| A:(TRUE|FALSE) \| E:(\S+)$/))){
      if(page||own(w.spools,m[1]))fail("duplicate/late spool");
      const members=m[3].split(",");if(new Set(members).size!==members.length||members.some(x=>!ID.test(x)))fail("invalid spool members");
      w.spools[m[1]]={id:m[1],initial:m[2]==="TRUE",members};continue;
    }
    if((m=l.match(/^ENC (\S+) turn=(\d+)\.\.(\d+) \| I:(\d+) \| A:(.*?) \| Q:(.*?) \| N:(.*?) \| T:(.+)$/))){
      const lo=Number(m[2]),hi=Number(m[3]),index=Number(m[4]);if(!Number.isSafeInteger(lo)||!Number.isSafeInteger(hi)||!Number.isSafeInteger(index)||lo>hi)fail("bad encounter window");
      page={id:m[1],lo,hi,index,gate:expr(m[5],"b"),priority:expr(m[6],"n"),title:text(m[7]),text:text(m[8]),options:dict()};
      w.pages[m[1]]=page;continue;
    }
    if((m=l.match(/^OPT (\S+) \| V:(.*?) \| P:(.*?) \| T:(.+)$/))){
      if(!page)fail("option outside encounter");
      page.options[m[1]]={id:m[1],visible:expr(m[2],"b"),performable:expr(m[3],"b"),text:text(m[4]),reactions:[]};continue;
    }
    if((m=l.match(/^ORX (\S+)\/(\S+) -> (\S+) \| E:(.*?) \| D:(.*?) \| G:(.*?) \| T:(.+)$/))){
      const o=page&&page.options[m[1]];if(!o)fail("reaction outside option");
      const effects=m[4]==="NONE"?[]:m[4].split(/\s*;\s*/).map(s=>{
        let a=s.match(/^SET (\S+) = (.+)$/);if(a){if(!own(w.coordinates,a[1]))fail("undeclared write target");return {kind:"number",key:a[1],value:expr(a[2],"n")};}
        a=s.match(/^SPOOL (\S+) = (.+)$/);if(a){if(!own(w.spools,a[1]))fail("undeclared spool");return {kind:"spool",key:a[1],value:expr(a[2],"b")};}
        fail("unsupported effect "+s);
      });
      o.reactions.push({id:m[2],to:m[3],effects,desirability:expr(m[5],"n"),gate:expr(m[6],"b"),text:text(m[7])});continue;
    }
    fail("unrecognized record "+l.slice(0,100));
  }
  for(const k of ["id","title","about","start","turnBase","tie","direct"])if(!own(w,k))fail("missing header "+k);
  if(!own(w.pages,w.start))fail("missing start");
  if(!Object.values(w.spools).some(s=>s.initial))fail("no active initial spool");
  const memberSet=new Set();
  for(const s of Object.values(w.spools))for(const id of s.members){if(!own(w.pages,id))fail("unknown spool member");memberSet.add(id);}
  for(const p of Object.values(w.pages)){
    if(!memberSet.has(p.id))fail("unspooled encounter "+p.id);
    for(const o of Object.values(p.options)){
      if(!o.reactions.length)fail("empty reaction menu");
      for(const r of o.reactions)if(r.to!=="wild"&&!own(w.pages,r.to))fail("unknown destination "+r.to);
    }
  }
  return freeze(w);
}
function activeFor(w,s,id){return Object.values(w.spools).some(p=>s.spools[p.id]&&p.members.includes(id));}
function env(w,s){
  const v=Object.assign(dict(),s.values),seen=new Set(s.seen);
  for(const id of w.events)v[meta("SEEN",id)]=seen.has(id)?1:0;
  for(const id of Object.keys(w.spools))v[meta("ACTIVE",id)]=s.spools[id]?1:0;
  return v;
}
function val(w,s,x){return evaluate(x,env(w,s));}
function valid(w,s,id){const p=w.pages[id];return s.turn>=p.lo&&s.turn<=p.hi&&activeFor(w,s,id)&&val(w,s,p.gate);}
function recordSeen(s,id){if(!s.seen.includes(id))s.seen.push(id);}
export function initialV2(w){
  const s={encounter:w.start,turn:w.turnBase,values:dict(),spools:dict(),seen:[],visited:[]};
  for(const [k,v] of Object.entries(w.coordinates))s.values[k]=v.initial;
  for(const [k,v] of Object.entries(w.spools))s.spools[k]=v.initial;
  if(w.direct==="strict"&&!valid(w,s,w.start))fail("blocked start");
  recordSeen(s,w.start);s.visited.push(w.start);return s;
}
function assertState(w,s){
  if(!s||!own(w.pages,s.encounter)||!Number.isSafeInteger(s.turn)||s.turn<w.turnBase||!s.values||!s.spools||!Array.isArray(s.seen)||!Array.isArray(s.visited))fail("bad state");
  if(Object.keys(s.values).length!==Object.keys(w.coordinates).length||Object.keys(s.spools).length!==Object.keys(w.spools).length)fail("unexpected state fields");
  for(const k of Object.keys(w.coordinates)){if(!own(s.values,k))fail("missing value");bounded(s.values[k]);}
  for(const k of Object.keys(w.spools))if(!own(s.spools,k)||typeof s.spools[k]!=="boolean")fail("invalid spool state");
  if(new Set(s.seen).size!==s.seen.length||s.seen.some(x=>!w.events.includes(x))||!s.seen.includes(s.encounter)||!s.visited.includes(s.encounter)||s.visited.some(x=>!own(w.pages,x)||!s.seen.includes(x)))fail("invalid event history");
}
function menu(w,s){assertState(w,s);return Object.values(w.pages[s.encounter].options).filter(o=>val(w,s,o.visible)&&val(w,s,o.performable));}
export function observeV2(w,s){
  const options=menu(w,s),p=w.pages[s.encounter],values=dict();
  for(const [k,v] of Object.entries(w.coordinates))if(v.visibility==="public")values[k]=s.values[k];
  return {world_id:w.id,encounter:p.id,title:p.title,text:p.text,turn:s.turn,values,actions:options.map(o=>({id:o.id,text:o.text})),status:Object.keys(p.options).length===0?"terminal":options.length?"decision":"dead_end"};
}
function resolveWild(w,s){
  const ids=new Set();
  for(const p of Object.values(w.spools))if(s.spools[p.id])for(const id of p.members)if(!s.visited.includes(id))ids.add(id);
  const candidates=[...ids].filter(id=>valid(w,s,id)).map(id=>({id,score:val(w,s,w.pages[id].priority),index:w.pages[id].index}));
  // Stable spool/member insertion order breaks equal score + equal index.
  candidates.sort((a,b)=>b.score-a.score||a.index-b.index);
  return {target:candidates[0]?.id??null,candidates};
}
function branch(w,s,o,r){
  const n=copy(s),writes=[];
  for(const e of r.effects){
    const dst=e.kind==="spool"?n.spools:n.values,before=dst[e.key],after=val(w,n,e.value);
    if(e.kind==="spool"){if(typeof after!=="boolean")fail("nonboolean spool write");}else bounded(after);
    dst[e.key]=after;writes.push({kind:e.kind,key:e.key,before,after});
  }
  recordSeen(n,o.id);recordSeen(n,r.id);n.turn++;
  const routing=r.to==="wild"?resolveWild(w,n):{target:r.to,candidates:[]};
  const target=routing.target;
  const admitted=target!==null&&valid(w,n,target);
  const status=!target?"no_wild_destination":r.to!=="wild"&&!admitted&&w.direct==="strict"?"blocked_destination":"ok";
  if(status==="ok"){n.encounter=target;recordSeen(n,target);n.visited.push(target);}
  const energy=Object.keys(w.coordinates).reduce((a,k)=>a+(n.values[k]-s.values[k])**2,0);
  return {id:r.id,text:r.text,status,next:status==="ok"?n:null,writes,routing,guard_admitted:admitted,squared_step_energy:energy};
}
export function auditV2(w,s){
  return {world_id:w.id,profile:w.profile,pre:copy(s),actions:menu(w,s).map(o=>{
    const scores=o.reactions.map(r=>{const eligible=val(w,s,r.gate);return {id:r.id,eligible,score:eligible?val(w,s,r.desirability):null};});
    const eligible=scores.filter(x=>x.eligible);
    const max=eligible.length?Math.max(...eligible.map(x=>x.score)):null;
    const winners=eligible.filter(x=>x.score===max).map(x=>x.id);
    const selected=w.tie==="first"?winners[0]??null:winners[winners.length-1]??null;
    const branches=o.reactions.filter(r=>eligible.some(e=>e.id===r.id)).map(r=>branch(w,s,o,r));
    return {id:o.id,scores,winners,selected,branches,status:branches.find(b=>b.id===selected)?.status??"no_eligible_reaction"};
  })};
}
export function stepV2(w,s,id){
  const o=menu(w,s).find(o=>o.id===id);if(!o)fail("illegal action "+id);
  let chosen=null,best=-Infinity;
  for(const r of o.reactions)if(val(w,s,r.gate)){
    const score=val(w,s,r.desirability);if(score>best||(w.tie==="last"&&score===best)){best=score;chosen=r;}
  }
  if(!chosen)fail("no eligible reaction");
  const b=branch(w,s,o,chosen);if(b.status!=="ok")fail(b.status);
  return b;
}

// Optimized replay path above is independently checked against the full audit.
// Minimal targeted patch with exact line precondition; does not change world IDs.
export function applyLinePatch(source,patch){
  if(!patch||!Number.isSafeInteger(patch.line)||patch.line<1||typeof patch.before!=="string"||typeof patch.after!=="string"||/[\r\n]/.test(patch.after)||patch.before===patch.after)fail("bad patch");
  const lines=source.split("\n"),i=patch.line-1;
  if(lines[i]!==patch.before)fail("stale patch precondition");
  lines[i]=patch.after;return lines.join("\n");
}
