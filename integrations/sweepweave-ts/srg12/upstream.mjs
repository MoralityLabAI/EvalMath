import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
function upstream(api,source){
const w=api.compileV2(source),goal="page_secret_undercover_truce",sirens="page_sirens_at_the_rollup_door",S="char_pink.Rat_Suspicion",B="char_blonde.Sadistic_Escalation",L="char_white.Crew_Loyalty";
const seeds=[0x53521101,0x53521102,0x53521103],n=128;
const dist=v=>(v[L]-Math.max(-.53,Math.min(.77,v[L])))**2+Math.max(0,.08-v[S])**2+Math.max(0,v[B]-.35)**2;
const rows={},gate={roots:0,passes:0,suspicion_fails:0,restraint_fails:0,loyalty_fails:0,selected_truce_zero_progress:0,selected_truce_count:0};
let instances=0;
for(const seed of seeds){let x=seed>>>0;const rand=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};for(let i=0;i<n;i++){let s=api.initialV2(w);const words=Array.from({length:24},rand);
for(const word of words){const ob=api.observeV2(w,s);if(ob.status!=="decision")break;
const a=api.auditV2(w,s).actions.map(o=>({id:o.id,b:o.branches.find(b=>b.id===o.selected)}));if(!a.length||a.some(o=>!o.b?.next))throw Error("missing branch");
const d0=dist(s.values),goals=a.map(o=>dist(o.b.next.values)),gap=Math.max(...goals)-Math.min(...goals);
const r=rows[s.encounter]??={prefix_instances:0,legal_actions:0,goal_coordinate_effect_actions:0,choice_goal_distance_range_sum:0,choice_goal_distance_range_max:0,nonzero_choice_range:0,improving_actions:0,worsening_actions:0,best_progress_sum:0,goal_coordinate_changes:{suspicion:0,restraint:0,loyalty:0}};
r.prefix_instances++;r.legal_actions+=a.length;r.choice_goal_distance_range_sum+=gap;r.choice_goal_distance_range_max=Math.max(r.choice_goal_distance_range_max,gap);r.nonzero_choice_range+=Number(gap>1e-12);r.best_progress_sum+=d0-Math.min(...goals);
for(let j=0;j<a.length;j++){const v=a[j].b.next.values,ds=v[S]!==s.values[S],db=v[B]!==s.values[B],dl=v[L]!==s.values[L];r.goal_coordinate_effect_actions+=Number(ds||db||dl);r.goal_coordinate_changes.suspicion+=Number(ds);r.goal_coordinate_changes.restraint+=Number(db);r.goal_coordinate_changes.loyalty+=Number(dl);r.improving_actions+=Number(goals[j]<d0-1e-12);r.worsening_actions+=Number(goals[j]>d0+1e-12);}
instances+=a.length;
if(s.encounter===sirens){gate.roots++;gate.passes+=Number(d0<1e-12);gate.suspicion_fails+=Number(s.values[S]<.08);gate.restraint_fails+=Number(s.values[B]>.35);gate.loyalty_fails+=Number(s.values[L]<-.53||s.values[L]>.77);const tr=a.find(o=>o.id.endsWith("_2"));gate.selected_truce_count++;gate.selected_truce_zero_progress+=Number(Math.abs(dist(tr.b.next.values)-d0)<1e-12);break;}
s=api.stepV2(w,s,ob.actions[Math.floor(word*ob.actions.length/4294967296)].id).next;
}}}
const summary=Object.entries(rows).map(([page,r])=>({page,...r,mean_choice_goal_distance_range:r.choice_goal_distance_range_sum/r.prefix_instances,mean_best_progress:r.best_progress_sum/r.prefix_instances})).sort((a,b)=>b.mean_choice_goal_distance_range-a.mean_choice_goal_distance_range);
return {evidence:"reused public development campaigns; one-step goal-gate geometry, not causal mediation over whole campaigns",seeds,campaigns:seeds.length*n,action_instances:instances,gate_at_first_sirens:gate,scenes:summary};
}
const root=fileURLToPath(new URL('../../../',import.meta.url));
const blobs={"integrations/sweepweave-ts/srg04/swmd-runtime.mjs":"ba4401a824f8cfdb4ae25525973a989c0047168e","integrations/sweepweave-ts/srg05/swmd-runtime-v2.mjs":"a687ad75e3c88683936b4b3d24324ced3f4cf874","integrations/sweepweave-ts/srg05/fixtures/reservoir-dogs.swmd.srg.md":"cb174a3efb031eaa046b01a2acc526ef7d122345"};
for(const [p,sha] of Object.entries(blobs)){const b=fs.readFileSync(path.join(root,p));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('blob drift '+p);}
const source=fs.readFileSync(path.join(root,"integrations/sweepweave-ts/srg05/fixtures/reservoir-dogs.swmd.srg.md"),'utf8');
const result={...upstream(api,source),source_blobs:blobs};
const prior=JSON.parse(fs.readFileSync(path.join(root,'output/evaluation_storyworld_reasoning/srg12_upstream.json'),'utf8'));
if(JSON.stringify(result)!==JSON.stringify(prior))throw Error('receipt drift');console.log(JSON.stringify({reproduced:true,action_instances:result.action_instances,gate:result.gate_at_first_sirens},null,2));
