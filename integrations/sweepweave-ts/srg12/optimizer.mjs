// SRG-12: bounded causal effect/contrast optimizer for Reservoir Dogs.
// Original SRG/2 mechanics; no new flags, destinations, gates or prose edits.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
import {evaluate as evalExpr} from '../srg04/swmd-runtime.mjs';
const GOAL="page_secret_undercover_truce",SIRENS="page_sirens_at_the_rollup_door",TRUCE="opt_page_sirens_at_the_rollup_door_2";
const S="char_pink.Rat_Suspicion",B="char_blonde.Sadistic_Escalation",L="char_white.Crew_Loyalty";
const fail=m=>{throw Error("SRG12: "+m);},same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const sum=(a,f)=>a.reduce((n,x)=>n+f(x),0),clamp=(x,a,b)=>Math.max(a,Math.min(b,x)),nudge=(x,a)=>clamp(x*(1-Math.abs(a))+a,-1,1);
const C=x=>"C("+Number(x.toFixed(6))+")",P=k=>"P("+k+")";
export const CONTRACT=Object.freeze({
 development:[{seed:0x53521101,campaigns:128},{seed:0x53521102,campaigns:128},{seed:0x53521103,campaigns:128}],
 validation:[{seed:0x53521211,campaigns:192},{seed:0x53521212,campaigns:192}],
 grid:{bias:[0,.025,.05,.075,.1,.125],recognition:[0,.25,.5,.75],restraint:[0,.25,.5,.75],reaction:[0,.1,.2]},
 target:{opportunity_min:.125,opportunity_max:.2,unique_fraction_min:.7,low_margin_fraction_max:.2,margin:.03,
 unique_truce_share_min:.5,non_goal_route_change_fraction_max:.1,max_added_coordinate_displacement:.12,max_selected_energy_ratio:1.75,max_goal_distance_increase_vs_baseline:.025},
 scope:"truce option only: append bounded recognition and restraint effects, add signed suspicion term to reaction scores; optional secret Q bias",
 note:"public development uses inspected SRG11 seeds; validation fresh by seed, not independently authored or sealed"
});
function distance(v){return (v[L]-clamp(v[L],-.53,.77))**2+Math.max(0,.08-v[S])**2+Math.max(0,v[B]-.35)**2;}
function energy(a,b){return sum(Object.keys(a),k=>(a[k]-b[k])**2);}
function words(c){let x=c.seed>>>0;const r=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};return Array.from({length:c.campaigns},()=>Array.from({length:24},r));}
function firstRoots(api,w,c){
 const seq=words(c),roots=[];
 for(let i=0;i<seq.length;i++){let s=api.initialV2(w),prefixEnergy=0;
   for(const n of seq[i]){
     if(s.encounter===SIRENS){roots.push({s,trial:i,prefixEnergy});break;}
     const o=api.observeV2(w,s);if(o.status!=="decision")break;
     const b=api.stepV2(w,s,o.actions[Math.floor(n*o.actions.length/4294967296)].id);prefixEnergy+=b.squared_step_energy;s=b.next;
   }
 }
 return {roots,seq};
}
function numeric(n){if(n.op==="pointer"&&n.key.startsWith("__srg."))fail("event-dependent encounter formula");for(const a of n.args??[])numeric(a);}
function available(w,s){
 const ids=new Set();for(const p of Object.values(w.spools))if(s.spools[p.id])for(const id of p.members)if(!s.visited.includes(id)){
   const e=w.pages[id];if(s.turn+1>=e.lo&&s.turn+1<=e.hi)ids.add(id);
 }
 return [...ids].map(id=>w.pages[id]);
}
function rank(c,bias){return c.map(x=>({...x,score:x.score+(x.id===GOAL?bias:0)})).sort((a,b)=>b.score-a.score||a.index-b.index);}
function candidates(pages,v,evaluate,bias=0){
 const c=rank(pages.filter(p=>evaluate(p.gate,v)).map(p=>({id:p.id,index:p.index,score:evaluate(p.priority,v)})),bias);
 if(!c.length)fail("no eligible wild encounter");return c;
}
function capture(api,w,roots,evaluate){
 for(const p of Object.values(w.pages)){numeric(p.gate);numeric(p.priority);}
 return roots.map(r=>{
   const pages=available(w,r.s),actions=api.auditV2(w,r.s).actions.map(a=>{
     const base=a.branches.find(b=>b.id===a.selected);
     if(!base?.next||!base.routing.candidates.length)fail("invalid selected branch");
     if(!same(candidates(pages,base.next.values,evaluate).map(x=>x.id),base.routing.candidates.map(x=>x.id)))fail("wild cache mismatch");
     return {id:a.id,scores:a.scores,branches:a.branches,base};
   });
   if(actions.length!==3||!actions.some(a=>a.id===TRUCE))fail("unexpected menu");
   return {...r,pages,actions};
 });
}
function modify(pre,post,p){
 const v={...post},support=Math.max(0,pre[S]);
 v[B]=nudge(v[B],-Math.min(.12,p.restraint*support)*Math.max(0,v[B]));
 v[S]=nudge(v[S],Math.min(.12,p.recognition*support));return v;
}
function select(a,pre,gamma){
 if(a.id!==TRUCE||!gamma)return a.base;
 let best=-Infinity,id=null;
 for(const s of a.scores)if(s.eligible){
   const v=s.score+(s.id.endsWith("_1")?-1:1)*gamma*pre[S];if(v>best){best=v;id=s.id;}
 }
 return a.branches.find(b=>b.id===id);
}
function row(a,r,br,v,cand){
 return {id:a.id,base:a.base.next.encounter,reaction:br.id,baseReaction:a.base.id,cand,energy:energy(r.s.values,v),baseEnergy:a.base.squared_step_energy,
 added:Math.max(Math.abs(v[S]-br.next.values[S]),Math.abs(v[B]-br.next.values[B])),
 before:distance(r.s.values),after:distance(v),baseAfter:distance(a.base.next.values),prefixEnergy:r.prefixEnergy};
}
function cached(records,evaluate,p){
 return records.map(r=>({trial:r.trial,actions:r.actions.map(a=>{
   const br=select(a,r.s.values,p.reaction),v=a.id===TRUCE?modify(r.s.values,br.next.values,p):br.next.values;
   return row(a,r,br,v,a.id===TRUCE?candidates(r.pages,v,evaluate):a.base.routing.candidates);
 })}));
}
function profile(rows,p){
 const o={params:p,roots:rows.length,actions:0,opportunities:0,unique:0,unique_truce:0,chosen:0,low_margin:0,eligible:0,route_changes:0,non_goal_route_changes:0,truce_actions:0,reaction_changes:0,
 max_added_displacement:0,max_energy_ratio:0,max_goal_distance_increase:0,truce_mean_progress:0,truce_baseline_mean_progress:0,truce_mean_step_share:0,winning_truce:0};
 for(const r of rows){const wins=[];
   for(const a of r.actions){const cs=rank(a.cand,p.bias),win=cs[0].id;
     o.actions++;o.eligible+=Number(cs.some(x=>x.id===GOAL));o.route_changes+=Number(win!==a.base);o.non_goal_route_changes+=Number(win!==a.base&&win!==GOAL&&a.base!==GOAL);
     if(win===GOAL){wins.push(a.id);o.chosen++;if(cs.length>1&&cs[0].score-cs[1].score<CONTRACT.target.margin)o.low_margin++;}
     if(a.id===TRUCE){o.truce_actions++;o.reaction_changes+=Number(a.reaction!==a.baseReaction);o.winning_truce+=Number(win===GOAL);
       o.max_added_displacement=Math.max(o.max_added_displacement,a.added);o.max_energy_ratio=Math.max(o.max_energy_ratio,a.baseEnergy?a.energy/a.baseEnergy:a.energy?Infinity:1);
       o.max_goal_distance_increase=Math.max(o.max_goal_distance_increase,a.after-a.baseAfter);o.truce_mean_progress+=a.before-a.after;o.truce_baseline_mean_progress+=a.before-a.baseAfter;o.truce_mean_step_share+=a.energy/(a.prefixEnergy+a.energy);
     }
   }
   o.opportunities+=Number(wins.length>0);o.unique+=Number(wins.length===1);o.unique_truce+=Number(wins.length===1&&wins[0]===TRUCE);
 }
 for(const k of ["truce_mean_progress","truce_baseline_mean_progress","truce_mean_step_share"])o[k]/=o.truce_actions;
 o.opportunity_rate=o.opportunities/o.roots;o.unique_fraction=o.opportunities?o.unique/o.opportunities:0;o.unique_truce_share=o.unique?o.unique_truce/o.unique:0;o.low_margin_fraction=o.chosen?o.low_margin/o.chosen:0;
 const t=CONTRACT.target;
 o.checks={opportunity:o.opportunity_rate>=t.opportunity_min&&o.opportunity_rate<=t.opportunity_max,unique:o.unique_fraction>=t.unique_fraction_min,
 unique_truce:o.unique_truce_share>=t.unique_truce_share_min,margin:o.low_margin_fraction<=t.low_margin_fraction_max,
 scope:o.non_goal_route_changes/o.truce_actions<=t.non_goal_route_change_fraction_max,displacement:o.max_added_displacement<=t.max_added_coordinate_displacement+1e-12,
 energy:o.max_energy_ratio<=t.max_selected_energy_ratio,goal_progress:o.max_goal_distance_increase<=t.max_goal_distance_increase_vs_baseline&&o.truce_mean_progress>=o.truce_baseline_mean_progress-1e-12};
 o.pass=Object.values(o.checks).every(Boolean);return o;
}
function patch(source,p){
 const lines=source.split("\n"),patches=[];
 const apply=(i,after)=>{if(after!==lines[i]){patches.push({line:i+1,before:lines[i],after});lines[i]=after;}};
 const i=lines.findIndex(s=>s.startsWith("ENC "+GOAL+" "));if(i<0)fail("missing goal");
 if(p.bias){const m=lines[i].match(/ \| Q:(.*?) \| N:/);if(!m||m[1].split("C(0.22)").length!==2)fail("unexpected Q");apply(i,lines[i].replace(" | Q:"+m[1]+" | N:"," | Q:"+m[1].replace("C(0.22)",C(.22+p.bias))+" | N:"));}
 for(let j=0;j<lines.length;j++)if(lines[j].startsWith("ORX "+TRUCE+"/")){
   const old=lines[j],m=old.match(/ \| E:(.*?) \| D:(.*?) \| G:/);if(!m)fail("truce line");
   let e=m[1],d=m[2];if(e.includes("SET "+S+" =")||e.includes("SET "+B+" ="))fail("unexpected original write");
   // Restraint reads original suspicion before the appended recognition write.
   if(p.restraint)e+="; SET "+B+" = CLAMP(NUDGE("+P(B)+",MUL(C(-1),MIN(C(0.12),MUL("+C(p.restraint)+",MAX(C(0),"+P(S)+"))),MAX(C(0),"+P(B)+"))))";
   if(p.recognition)e+="; SET "+S+" = CLAMP(NUDGE("+P(S)+",MIN(C(0.12),MUL("+C(p.recognition)+",MAX(C(0),"+P(S)+")))))";
   if(p.reaction){const sign=old.split(" -> ")[0].endsWith("_1")?-1:1;d="ADD("+d+",MUL("+C(sign*p.reaction)+","+P(S)+"))";}
   apply(j,old.replace(" | E:"+m[1]+" | D:"+m[2]+" | G:"," | E:"+e+" | D:"+d+" | G:"));
 }
 return {source:lines.join("\n"),patches};
}
function compare(api,evaluate,w,v,records,p){
 let checked=0,nonTruceNumeric=0,routeChanges=0,reactionChanges=0,maxDelta=0,maxScoreError=0,forcedBranchChecks=0;
 const rows=[];
 for(const r of records){
   if(!same(api.observeV2(v,r.s),api.observeV2(w,r.s)))fail("observation changed");
   const packet=api.auditV2(v,r.s),acts=[];
   for(const old of r.actions){
     const n=packet.actions.find(x=>x.id===old.id),br=n.branches.find(x=>x.id===n.selected);
     const forced=select(old,r.s.values,p.reaction),expected=old.id===TRUCE?modify(r.s.values,forced.next.values,p):forced.next.values;
     const cs=candidates(r.pages,expected,evaluate,p.bias);
     if(n.selected!==forced.id||!same(cs.map(x=>x.id),br.routing.candidates.map(x=>x.id))||br.next.encounter!==cs[0].id)fail("cached/compiled selection");
     for(const k of Object.keys(expected))maxDelta=Math.max(maxDelta,Math.abs(expected[k]-br.next.values[k]));
     for(const c of cs){const b=br.routing.candidates.find(x=>x.id===c.id);maxScoreError=Math.max(maxScoreError,Math.abs(c.score-b.score));}
     for(const prior of old.branches){
       const actual=n.branches.find(b=>b.id===prior.id);if(!actual?.next)fail("forced branch disappeared");
       const z=old.id===TRUCE?modify(r.s.values,prior.next.values,p):prior.next.values;
       const cs=candidates(r.pages,z,evaluate,p.bias);
       if(!same(cs.map(x=>x.id),actual.routing.candidates.map(x=>x.id)))fail("forced routing mismatch");
       for(const k of Object.keys(z))maxDelta=Math.max(maxDelta,Math.abs(z[k]-actual.next.values[k]));forcedBranchChecks++;
     }
     if(old.id!==TRUCE){if(!same(old.scores,n.scores)||!same(old.base.writes,br.writes)||!same(old.base.next.values,br.next.values))fail("outside truce numeric change");nonTruceNumeric++;}
     routeChanges+=Number(old.base.next.encounter!==br.next.encounter);reactionChanges+=Number(old.base.id!==n.selected);checked++;
     acts.push(row(old,r,forced,br.next.values,br.routing.candidates));
   }
   rows.push({trial:r.trial,actions:acts});
 }
 if(maxDelta>1e-12||maxScoreError>1e-12)fail("numeric mismatch");
 return {checked,forcedBranchChecks,nonTruceNumeric,routeChanges,reactionChanges,maxDelta,maxScoreError,metrics:profile(rows,{...p,bias:0})};
}
function replay(api,w,v,seqs){
 const roll=(w,seq)=>{let s=api.initialV2(w),trace=[];for(const n of seq){const o=api.observeV2(w,s);if(o.status!=="decision")return {end:s.encounter,complete:o.status==="terminal",trace};const b=api.stepV2(w,s,o.actions[Math.floor(n*o.actions.length/4294967296)].id);trace.push([s.encounter,b.id,b.next.encounter,s.turn]);s=b.next;}return {end:"timeout",complete:false,trace};};
 const o={campaigns:seqs.length,baseline_complete:0,candidate_complete:0,baseline_goal:0,candidate_goal:0,changed_endings:0,pre_sirens_prefix_changes:0};
 for(const seq of seqs){const a=roll(w,seq),b=roll(v,seq);o.baseline_complete+=Number(a.complete);o.candidate_complete+=Number(b.complete);o.baseline_goal+=Number(a.end===GOAL);o.candidate_goal+=Number(b.end===GOAL);o.changed_endings+=Number(a.end!==b.end);
   const prefix=t=>{const i=t.findIndex(r=>r[0]===SIRENS);return i<0?t:t.slice(0,i);};o.pre_sirens_prefix_changes+=Number(!same(prefix(a.trace),prefix(b.trace)));
 }
 if(o.pre_sirens_prefix_changes)fail("prefix change");return o;
}
export function runSuite({api=runtime,evaluate=evalExpr,source,validate=true}){
 const w=api.compileV2(source),dev=CONTRACT.development.map(c=>{const data=firstRoots(api,w,c);return {c,data,records:capture(api,w,data.roots,evaluate)};});
 const grid=[];
 for(const recognition of CONTRACT.grid.recognition)for(const restraint of CONTRACT.grid.restraint)for(const reaction of CONTRACT.grid.reaction){
   const cache=dev.map(d=>cached(d.records,evaluate,{recognition,restraint,reaction}));
   for(const bias of CONTRACT.grid.bias){
     const p={bias,recognition,restraint,reaction},metrics=cache.map(r=>profile(r,p));
     grid.push({params:p,cost:Number((bias/.025+recognition/.25+restraint/.25+reaction/.1).toFixed(6)),full:sum(metrics,r=>Number(r.pass)),passCount:sum(metrics,r=>Object.values(r.checks).filter(Boolean).length),metrics});
   }
 }
 // Exact constraints first. If infeasible, retain best diagnostic candidate,
 // never promote it. Tie break is frozen before validation.
 const ranked=[...grid].sort((a,b)=>b.full-a.full||b.passCount-a.passCount||a.cost-b.cost||a.params.bias-b.params.bias||a.params.reaction-b.params.reaction||a.params.recognition-b.params.recognition||a.params.restraint-b.params.restraint);
 const selected=ranked[0],feasible=grid.filter(g=>g.full===dev.length).length,baseline=grid.find(g=>Object.values(g.params).every(x=>x===0));
 const candidate=patch(source,selected.params),v=api.compileV2(candidate.source);
 const development=dev.map((d,i)=>({cohort:d.c,baseline:baseline.metrics[i],selected:selected.metrics[i],runtime:compare(api,evaluate,w,v,d.records,selected.params)}));
 const validation=[];
 if(validate)for(const c of CONTRACT.validation){
   const d=firstRoots(api,w,c),records=capture(api,w,d.roots,evaluate),runtime=compare(api,evaluate,w,v,records,selected.params),base=compare(api,evaluate,w,w,records,{bias:0,recognition:0,restraint:0,reaction:0});
   validation.push({cohort:c,baseline:base.metrics,selected:runtime.metrics,runtime,full_replay:replay(api,w,v,d.seq)});
 }
 const outcome=feasible>0&&development.every(d=>d.runtime.metrics.pass)&&validate&&validation.every(d=>d.selected.pass&&d.full_replay.candidate_complete===d.full_replay.campaigns)?"PASS":"FAIL";
 return {receipt:{evidence:"bounded public development-selected causal edit; fresh-seed public validation; no model inference",contract:CONTRACT,grid_size:grid.length,feasible_count:feasible,selected:{params:selected.params,cost:selected.cost,full:selected.full,passCount:selected.passCount},baseline:{full:baseline.full,passCount:baseline.passCount},development,validation,outcome,top_candidates:ranked.slice(0,12).map(({metrics,...r})=>r)},candidate:candidate.source,patches:candidate.patches};
}
