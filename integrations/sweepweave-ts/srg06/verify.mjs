import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';
function research(api,evaluate,source){
 const {compileV2,initialV2,observeV2,stepV2,auditV2}=api;
 const w=compileV2(source),strict=compileV2(source.replace("direct: explicit","direct: strict"));
 const pages=Object.values(w.pages),coords=Object.keys(w.coordinates),byReaction=new Map();
 for(const p of pages)for(const o of Object.values(p.options))for(const r of o.reactions)byReaction.set(r.id,{from:p.id,r});
 const add=(o,k,n=1)=>o[k]=(o[k]??0)+n,copy=x=>JSON.parse(JSON.stringify(x));
 const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 const round=x=>Number(x.toFixed(9));
 const percentile=(a,q)=>{const b=[...a].sort((x,y)=>x-y);return b.length?round(b[Math.floor(q*(b.length-1))]):null;};
 const goal="page_secret_undercover_truce",sirens="page_sirens_at_the_rollup_door";
 const clock="char_white.Phase_Clock",loyal="char_white.Crew_Loyalty",sus="char_pink.Rat_Suspicion",sad="char_blonde.Sadistic_Escalation";
 const targetKeys=[clock,loyal,sus,sad],targetSet=new Set(targetKeys);
 // Pure structural minimum from direct-edge graph. It deliberately ignores
 // reaction feasibility, numeric gates and wild edges; it is a lower bound
 // before the first wild route, not a reachability certificate.
 const earliest=Object.fromEntries(pages.map(p=>[p.id,Infinity]));earliest[w.start]=w.turnBase;
 for(let pass=0;pass<pages.length;pass++)for(const {from,r} of byReaction.values())if(r.to!=="wild")earliest[r.to]=Math.min(earliest[r.to],earliest[from]+1);
 const edits=pages.filter(p=>Number.isFinite(earliest[p.id])&&earliest[p.id]<p.lo).map(p=>({id:p.id,old:p.lo,direct_lower:earliest[p.id],latest:p.hi}));
 const newLo=Object.fromEntries(edits.map(e=>[e.id,e.direct_lower]));
 let patched=source.replace("direct: explicit","direct: strict");
 for(const e of edits){const old=`ENC ${e.id} turn=${e.old}..${e.latest} |`,replacement=`ENC ${e.id} turn=${e.direct_lower}..${e.latest} |`;if(patched.split(old).length!==2)throw Error("unexpected source line");patched=patched.replace(old,replacement);}
 const wide=compileV2(patched);
 // A deliberately separate admission certificate for explicit links.
 // Preserve every original wild candidate and priority; no production source
 // changes. Reject numeric/spool/late failures rather than waive them.
 function reasons(next,target){
   const p=w.pages[target],out=[];
   if(next.turn<p.lo)out.push("early");
   if(next.turn>p.hi)out.push("late");
   if(!Object.values(w.spools).some(sp=>next.spools[sp.id]&&sp.members.includes(target)))out.push("spool");
   if(!evaluate(p.gate,next.values))out.push("predicate");
   return out;
 }
 function scopedStep(s,id){
   const b=stepV2(w,s,id),r=byReaction.get(b.id).r;
   if(b.guard_admitted)return b;
   const why=reasons(b.next,b.next.encounter),p=w.pages[b.next.encounter];
   if(r.to==="wild"||!eq(why,["early"])||b.next.turn<(newLo[p.id]??p.lo))throw Error("SRG06: scoped admission blocked");
   return b;
 }
 const channel=k=>k.includes("Phase_Clock")?"clock":k.includes("][")?"p2":k.includes("[")?"p1":"actual";
 const clamp=(x,lo,hi)=>Math.max(lo,Math.min(hi,x));
 function distance(v,includeClock=true){
   return (includeClock?Math.max(0,.55-v[clock])**2:0)
     +(v[loyal]-clamp(v[loyal],-.53,.77))**2+Math.max(0,.08-v[sus])**2+Math.max(0,v[sad]-.35)**2;
 }
 function energies(a,b){
   const out={clock:0,actual:0,p1:0,p2:0,goal_continuous:0,all:0};
   for(const k of coords){const e=(b.values[k]-a.values[k])**2;out[channel(k)]+=e;out.all+=e;if(k!==clock&&targetSet.has(k))out.goal_continuous+=e;}
   return out;
 }
 function sequence(seed,n){
   let rng=seed>>>0;const next=()=>rng=(Math.imul(rng,1664525)+1013904223)>>>0;
   return Array.from({length:n},()=>Array.from({length:24},next));
 }
 function campaign(world,seq,mode,collect=false){
   let s=initialV2(world);const trace=[],roots=[];
   for(const ix of seq){const o=observeV2(world,s);if(o.status!=="decision")return {end:o.status==="terminal"?s.encounter:o.status,trace,roots};
     if(collect&&s.encounter===sirens)roots.push(copy(s));
     const id=o.actions[ix%o.actions.length].id;
     try{
       const b=mode==="scoped"?scopedStep(s,id):stepV2(world,s,id);
       trace.push({from:s.encounter,action:id,reaction:b.id,to:b.next.encounter,turn:b.next.turn,guard:b.guard_admitted,reason:collect?reasons(b.next,b.next.encounter):[],energy:collect?energies(s,b.next):null,goal_before:collect?distance(s.values,false):null,goal_after:collect?distance(b.next.values,false):null});
       s=b.next;
     }catch(err){if(/blocked_destination|no_wild_destination|scoped admission blocked|no eligible reaction/.test(String(err)))return {end:String(err).split(": ").at(-1),trace,roots};throw err;}
   }
   return {end:"timeout",trace,roots};
 }
 const signatures=t=>t.trace.map(x=>[x.from,x.action,x.reaction,x.to,x.turn]);
 function runSet(seed,n){
   const stats={seed,n,original_endings:{},strict_endings:{},global_window_endings:{},scoped_endings:{},strict_terminations:0,global_window_terminations:0,scoped_terminations:0,original_terminations:0,global_window_path_changes:0,scoped_path_changes:0,global_window_ending_changes:0,scoped_ending_changes:0,violations:0,violation_reasons:{},violation_targets:{},violation_edges:{},selected_steps:0};
   const geom={total:{clock:0,actual:0,p1:0,p2:0,goal_continuous:0,all:0},maxAll:[],maxGoal:[],secretMaxAll:[],secretMaxGoal:[],maxProgress:[],secretMaxProgress:[],zeroGoalMovement:0,goalProgressPositive:0,goalProgressNegative:0,gateSatisfiedTerminal:0,byEvent:{}};
   const roots=[];
   for(const seq of sequence(seed,n)){
     const o=campaign(w,seq,"original",true),s=campaign(strict,seq,"strict"),g=campaign(wide,seq,"wide"),r=campaign(w,seq,"scoped");
     for(const [k,v] of [["original",o],["strict",s],["global_window",g],["scoped",r]]){add(stats[k+"_endings"],v.end);if(w.pages[v.end]&&Object.keys(w.pages[v.end].options).length===0)stats[k+"_terminations"]++;}
     stats.global_window_path_changes+=Number(!eq(signatures(o),signatures(g)));stats.scoped_path_changes+=Number(!eq(signatures(o),signatures(r)));
     stats.global_window_ending_changes+=Number(o.end!==g.end);stats.scoped_ending_changes+=Number(o.end!==r.end);
     roots.push(...o.roots);
     stats.selected_steps+=o.trace.length;
     for(const e of o.trace){
       if(e.guard!==(e.reason.length===0))throw Error("admission classification mismatch");
       if(!e.guard){stats.violations++;add(stats.violation_reasons,e.reason.join("+"));add(stats.violation_targets,e.to);add(stats.violation_edges,e.from+" -> "+e.to);}
       for(const k of Object.keys(geom.total))geom.total[k]+=e.energy[k];
       const rec=geom.byEvent[e.from]??={n:0,all:0,goal_continuous:0};rec.n++;rec.all+=e.energy.all;rec.goal_continuous+=e.energy.goal_continuous;
     }
     const share=(k)=>{const a=o.trace.map(e=>e.energy[k]),sum=a.reduce((x,y)=>x+y,0);return sum?Math.max(...a)/sum:null;};
     const a=share("all"),b=share("goal_continuous");
     if(a!==null)geom.maxAll.push(a);if(b!==null)geom.maxGoal.push(b);else geom.zeroGoalMovement++;
     const prog=o.trace.map(e=>e.goal_before-e.goal_after),pos=prog.reduce((x,y)=>x+Math.max(0,y),0);
     geom.goalProgressPositive+=pos;geom.goalProgressNegative+=prog.reduce((x,y)=>x+Math.max(0,-y),0);
     const p=pos?Math.max(...prog.map(x=>Math.max(0,x)))/pos:null;if(p!==null)geom.maxProgress.push(p);
     if(o.end===goal){if(a!==null)geom.secretMaxAll.push(a);if(b!==null)geom.secretMaxGoal.push(b);if(p!==null)geom.secretMaxProgress.push(p);geom.gateSatisfiedTerminal+=Number(o.trace.at(-1).goal_after<=1e-15);}
   }
   return {stats,geometry:{total_energy:Object.fromEntries(Object.entries(geom.total).map(([k,v])=>[k,round(v)])),energy_share:Object.fromEntries(["clock","actual","p1","p2","goal_continuous"].map(k=>[k,round(geom.total[k]/geom.total.all)])),path_max_step_share:{all_median:percentile(geom.maxAll,.5),all_p90:percentile(geom.maxAll,.9),goal_median:percentile(geom.maxGoal,.5),goal_p90:percentile(geom.maxGoal,.9),secret_all_median:percentile(geom.secretMaxAll,.5),secret_goal_median:percentile(geom.secretMaxGoal,.5),positive_goal_progress_median:percentile(geom.maxProgress,.5),secret_positive_goal_progress_median:percentile(geom.secretMaxProgress,.5)},zero_goal_movement_paths:geom.zeroGoalMovement,positive_progress:round(geom.goalProgressPositive),negative_progress:round(geom.goalProgressNegative),secret_terminal_goal_continuous_satisfied:geom.gateSatisfiedTerminal,top_mean_goal_energy_events:Object.entries(geom.byEvent).map(([id,r])=>({id,n:r.n,mean:round(r.goal_continuous/r.n)})).sort((a,b)=>b.mean-a.mean).slice(0,5)},roots};
 }
 const cal=runSet(0x53524705,64),val=runSet(0x53524706,128);
 if(cal.stats.violations!==312)throw Error("SRG05 crosswalk failed");
 // One-step task: enter secret truce from a reachable sirens state. No claim
 // about the full campaign utility, hidden intent, or model ability.
 function reads(node,set=new Set()){
   if(node.op==="pointer"&&coords.includes(node.key))set.add(node.key);
   for(const a of node.args??[])reads(a,set);return set;
 }
 function union(dst,src){for(const k of src)dst.add(k);return dst;}
 function support(s){
   const p=w.pages[s.encounter],need=new Set();
   const nextTurn=s.turn+1;
   for(const o of Object.values(p.options)){
     union(need,reads(o.visible));union(need,reads(o.performable));
     for(const r of o.reactions){
       union(need,reads(r.gate));union(need,reads(r.desirability));
       const post=new Set();
       // For this pinned sirens fixture no reaction changes spools. Include
       // every potentially available candidate's gate and priority, not just
       // the observed winning route. History/spools/time are fixed context.
       if(r.effects.some(e=>e.kind!=="number")||r.to!=="wild")throw Error("unexpected sirens reaction");
       for(const q of pages)if(!s.visited.includes(q.id)&&q.lo<=nextTurn&&nextTurn<=q.hi&&Object.values(w.spools).some(sp=>s.spools[sp.id]&&sp.members.includes(q.id))){
         union(post,reads(q.gate));union(post,reads(q.priority));
       }
       for(const e of [...r.effects].reverse())if(post.has(e.key)){post.delete(e.key);union(post,reads(e.value));}
       union(need,post);
     }
   }
   return [...need].sort();
 }
 function label(s){
   const o=observeV2(w,s),actions=o.actions.map(x=>x.id),win=[];
   for(const a of actions)try{if(stepV2(w,s,a).next.encounter===goal)win.push(a);}catch{}
   return {state:s,actions,win,support:support(s)};
 }
 const calRows=cal.roots.map(label),valRows=val.roots.map(label);
 const u=new Set(),freq={};for(const row of calRows){union(u,row.support);for(const k of row.support)add(freq,k);}
 const order=[...targetKeys.filter(k=>u.has(k)),...[...u].filter(k=>!targetSet.has(k)).sort((a,b)=>(freq[b]??0)-(freq[a]??0)||a.localeCompare(b)),...coords.filter(k=>!u.has(k))];
 const valUnion=new Set();for(const row of valRows)union(valUnion,row.support);
 function cellKey(r,keys,bits){const n=2**bits;return JSON.stringify([r.actions,...keys.map(k=>Math.min(n-1,Math.floor((r.state.values[k]+1)*n/2)))]);}
 function cells(rows,keys,bits){
   const groups=new Map();
   for(const r of rows){const k=cellKey(r,keys,bits);if(!groups.has(k))groups.set(k,{actions:r.actions,counts:Object.fromEntries(r.actions.map(x=>[x,0])),n:0});const g=groups.get(k);g.n++;for(const a of r.win)g.counts[a]++;}
   return groups;
 }
 function best(g){return [...g.actions].sort((a,b)=>g.counts[b]-g.counts[a]||a.localeCompare(b))[0];}
 function profile(keys,bits){
   const cg=cells(calRows,keys,bits),vg=cells(valRows,keys,bits),fallback=cells(calRows,[],bits);
   let oracle=0,pred=0,unseen=0;
   for(const g of vg.values())oracle+=Math.max(...Object.values(g.counts),0);
   for(const r of valRows){const g=cg.get(cellKey(r,keys,bits));if(!g)unseen++;const f=g??fallback.get(cellKey(r,[],bits));const choice=f?best(f):[...r.actions].sort()[0];pred+=Number(r.win.includes(choice));}
   return {k:keys.length,bits,cal_cells:cg.size,val_cells:vg.size,val_oracle:oracle,calibrated_lookup:pred,unseen,denominator:valRows.length};
 }
 const curve=[0,1,2,4,8,16,32,50].filter(k=>k<=coords.length).map(k=>profile(order.slice(0,k),2));
 const precision=[0,1,2,3,4,6,8].map(b=>profile(order.slice(0,Math.min(8,order.length)),b));
 const publicKeys=coords.filter(k=>w.coordinates[k].visibility==="public");
 const publicProfile=profile(publicKeys,2),fullProfile=profile(coords,2);
 let interventionChecks=0,mismatches=0;
 function signature(s){const o=observeV2(w,s);return o.actions.map(a=>{try{const b=stepV2(w,s,a.id);return [a.id,b.id,b.next.encounter];}catch(e){return [a.id,"error",String(e)];}});}
 for(const r of valRows.slice(0,16)){const absent=coords.filter(k=>!r.support.includes(k)),before=signature(r.state);for(const k of absent)for(const x of [-1,1]){const s=copy(r.state);s.values[k]=x;interventionChecks++;mismatches+=Number(!eq(before,signature(s)));}}
 const difficulty={task:"one-step secret-truce entry at sirens (snapshot only)",calibration_roots:calRows.length,validation_roots:valRows.length,calibration_full_information_success:calRows.filter(r=>r.win.length).length,validation_full_information_success:valRows.filter(r=>r.win.length).length,calibration_support_union:[...u].sort(),validation_support_union:[...valUnion].sort(),support_size_min:Math.min(...valRows.map(r=>r.support.length)),support_size_max:Math.max(...valRows.map(r=>r.support.length)),static_feature_order:order,quantized_k_curve:curve,k8_precision_curve:precision,public_profile:publicProfile,full_profile:fullProfile,absent_coordinate_interventions:interventionChecks,absent_coordinate_route_mismatches:mismatches};
 if(mismatches)throw Error("support intervention mismatch");
 return {evidence:"source-pinned finite sampled authoring audit and snapshot oracle; binary64",edits,calibration:cal.stats,validation:val.stats,geometry:{calibration:cal.geometry,validation:val.geometry},difficulty,checks:{srg05_reproduced:true,all_calibration_bypasses_early:cal.stats.violation_reasons.early===cal.stats.violations,scoped_calibration_preserves_paths:cal.stats.scoped_path_changes===0,scoped_validation_preserves_paths:val.stats.scoped_path_changes===0,absent_interventions_preserve_signature:mismatches===0},patched};
}
const root=fileURLToPath(new URL('../../../',import.meta.url));
const blobs={"integrations/sweepweave-ts/srg04/swmd-runtime.mjs":"ba4401a824f8cfdb4ae25525973a989c0047168e","integrations/sweepweave-ts/srg05/swmd-runtime-v2.mjs":"a687ad75e3c88683936b4b3d24324ced3f4cf874","integrations/sweepweave-ts/srg05/fixtures/reservoir-dogs.swmd.srg.md":"cb174a3efb031eaa046b01a2acc526ef7d122345"};
for(const [p,sha] of Object.entries(blobs)){const b=fs.readFileSync(path.join(root,p));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('source blob mismatch '+p);}
const source=fs.readFileSync(path.join(root,"integrations/sweepweave-ts/srg05/fixtures/reservoir-dogs.swmd.srg.md"),'utf8');
const {patched,...data}=research(api,evaluate,source);
const receipt=JSON.stringify({source_blobs:blobs,...data},null,2)+'\n';
if(process.argv[2])fs.writeFileSync(process.argv[2],receipt);else process.stdout.write(receipt);
if(process.argv[3])fs.writeFileSync(process.argv[3],patched);
