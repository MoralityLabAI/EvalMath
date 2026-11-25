// SRG-11: bounded authoring optimization. Separate reference selection,
// runtime verification, frozen validation, and explicit author intent.
import * as api0 from '../srg05/swmd-runtime-v2.mjs';
import {tapes,compileSource,evaluateConfig} from '../srg10/curriculum.mjs';

const fail=m=>{throw Error("SRG11: "+m);};
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const sum=(a,f)=>a.reduce((n,x)=>n+f(x),0);
const QS=["x","y","q"],ORD=QS.flatMap(a=>QS.filter(b=>b!==a).map(b=>[a,b]));
const D=131072;
function group(a,f){const m=new Map();for(const r of a){const k=f(r);if(!m.has(k))m.set(k,[]);m.get(k).push(r);}return [...m.values()];}
function best(scores){const value=Math.max(...Object.values(scores));return {value,winners:Object.keys(scores).filter(k=>scores[k]===value),scores};}
function reference(c,view,h,order=null){
 const ts=tapes(c);
 function rec(rs,used,h,seq){
   const n=sum(rs,r=>r.m),p=sum(rs,r=>r.t===1?r.m:0),cost=used.length*c.cost;
   const scores={positive:16*p-cost*n,negative:16*(n-p)-cost*n,settle:(c.settle-cost)*n};
   if(h>1)for(const k of QS.filter(k=>!used.includes(k)&&(seq===null||seq[0]===k))){
     scores[k]=sum(group(rs,r=>r[k]),g=>rec(g,[...used,k],h-1,seq===null?null:seq.slice(1)).value);
   }
   return best(scores);
 }
 const cells=group(ts,r=>view==="analyst"?r.a:view==="reviewer"?r.b:view==="joint"?r.a+","+r.b:"blind").map(rs=>{
   const v=rec(rs,[],h,order),scores=Object.values(v.scores).sort((a,b)=>b-a),mass=sum(rs,r=>r.m);
   return {a:rs[0].a,mass,...v,margin_numerator:scores[0]-scores[1]};
 });
 return {numerator:sum(cells,r=>r.value),denominator:D,cells};
}
export const ECONOMICS=Object.freeze({
 baseline:{cost:2,settle:12},
 calibration:[
 {a:7,b:6,strong:7,weak:4,aux:7},
 {a:6,b:6,strong:8,weak:4,aux:7},
 {a:7,b:5,strong:7,weak:5,aux:8}],
 validation:[
 {a:6,b:7,strong:7,weak:4,aux:6},
 {a:8,b:5,strong:8,weak:5,aux:7},
 {a:5,b:6,strong:6,weak:5,aux:6},
 {a:7,b:7,strong:8,weak:6,aux:8}],
 target:{minimum_query_cost:1,blind_h1_unique_settle:true,blind_h3_unique_q:true,analyst_h2_context_choice:true,minimum_adaptive_gain:1,minimum_analyst_margin:2},
 grid:{cost:[1,2,3],settle:[7,8,9,10,11,12]}
});
function economicMetrics(c){
 const blind1=reference(c,"blind",1),blind3=reference(c,"blind",3),analyst=reference(c,"analyst",2);
 const fixed=Math.max(...ORD.map(order=>reference(c,"blind",3,order).numerator));
 const checks={positive_cost:c.cost>=1,settlement:blind1.cells.every(x=>same(x.winners,["settle"])),
   context_query:blind3.cells.every(x=>same(x.winners,["q"])),
   specialist:analyst.cells.every(x=>same(x.winners,[x.a>0?"x":"y"])),
   adaptive_gain:blind3.numerator-fixed>=D,
   margin:analyst.cells.every(x=>x.margin_numerator>=2*x.mass)};
 return {config:c,checks,pass:Object.values(checks).every(Boolean),blind_h1:blind1.numerator/D,blind_h3:blind3.numerator/D,blind_fixed:fixed/D,
   gain:(blind3.numerator-fixed)/D,analyst_h2:analyst.numerator/D,analyst_min_margin:Math.min(...analyst.cells.map(x=>x.margin_numerator/x.mass))};
}
function economicRow(params,scenarios){
 const rows=scenarios.map(s=>economicMetrics({family:"specialist",...s,...params}));
 return {params,edit_distance:Math.abs(params.cost-ECONOMICS.baseline.cost)+Math.abs(params.settle-ECONOMICS.baseline.settle),
   passed:rows.filter(x=>x.pass).length,total:rows.length,rows};
}
function runtimeCheck(api,c,tag){
 const r=evaluateConfig(api,c,tag),expected=economicMetrics(c);
 for(const [view,h,value] of [["blind",1,expected.blind_h1],["blind",3,expected.blind_h3],["analyst",2,expected.analyst_h2]]){
   const x=r.out.find(x=>x.view===view&&x.h===h);
   if(x.numerator/x.denominator!==value)fail("optimizer/runtime mismatch");
   if(view==="blind"&&h===3&&x.fixed_numerator/x.denominator!==expected.blind_fixed)fail("fixed mismatch");
 }
 return r.checks;
}
function economics(api){
 const grid=ECONOMICS.grid.cost.flatMap(cost=>ECONOMICS.grid.settle.map(settle=>economicRow({cost,settle},ECONOMICS.calibration)));
 const feasible=grid.filter(r=>r.passed===r.total).sort((a,b)=>a.edit_distance-b.edit_distance||a.params.cost-b.params.cost||b.params.settle-a.params.settle);
 if(!feasible.length)fail("no feasible calibration candidate");
 const selected=feasible[0],baseline=economicRow(ECONOMICS.baseline,ECONOMICS.calibration);
 // Selection stops here. Never select on validation outcomes.
 const validation={baseline:economicRow(ECONOMICS.baseline,ECONOMICS.validation),selected:economicRow(selected.params,ECONOMICS.validation)};
 const checks=[];for(const [i,row] of [...selected.rows,...validation.selected.rows].entries())checks.push(runtimeCheck(api,row.config,"srg11_econ_"+i));
 // Probability/payoff sidecar remains the authority. Source prose is compiled
 // from those parameters; the old SWMD runtime has no numeric utility field.
 const cases=selected.rows.map((r,i)=>({config:r.config,view:"blind",source:compileSource(r.config,"blind","srg11_econ_"+i),payoff_contract:{correct:16,incorrect:0,settled:r.config.settle,query_cost:r.config.cost,unfinished:"negative incurred query cost"}}));
 return {receipt:{contract:ECONOMICS,grid,feasible_count:feasible.length,baseline,selected,validation,runtime_checks:checks},cases};
}

const GOAL="page_secret_undercover_truce",SIRENS="page_sirens_at_the_rollup_door";
const OLD_BIAS="C(0.22)";
export const STORY=Object.freeze({
 calibration:{seed:0x53521101,campaigns:128},
 validation:[{seed:0x53521102,campaigns:256},{seed:0x53521103,campaigns:256}],
 deltas:[-.1,-.05,0,.025,.05,.075,.1,.125,.15,.2,.3],
 target:{opportunity_min:.125,opportunity_max:.2,unique_fraction_min:.7,low_margin_fraction_max:.2,margin:.03},
 scope:"single secret-ending priority bias; all eligibility, effects, other scores and prose frozen"
});
function random(seed){let x=seed>>>0;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};}
function campaignWords(seed,n){const r=random(seed);return Array.from({length:n},()=>Array.from({length:24},r));}
function firstRoots(api,w,c){
 const roots=[],words=campaignWords(c.seed,c.campaigns);
 for(let i=0;i<words.length;i++){
   let s=api.initialV2(w);
   for(let t=0;t<words[i].length;t++){
     if(s.encounter===SIRENS){roots.push({s,trial:i,t});break;}
     const o=api.observeV2(w,s);if(o.status!=="decision")break;
     s=api.stepV2(w,s,o.actions[Math.floor(words[i][t]*o.actions.length/4294967296)].id).next;
   }
 }
 return {roots,words};
}
function capture(api,w,roots){
 return roots.map(r=>({trial:r.trial,actions:api.auditV2(w,r.s).actions.map(a=>{
   const b=a.branches.find(b=>b.id===a.selected);
   if(!b||!b.next||!b.routing.candidates.length)fail("expected eligible wild branch");
   return {id:a.id,reaction:b.id,route:b.next.encounter,candidates:b.routing.candidates,energy:b.squared_step_energy};
 })}));
}
function rank(candidates,delta){
 return candidates.map(c=>({...c,score:c.score+(c.id===GOAL?delta:0)})).sort((a,b)=>b.score-a.score||a.index-b.index);
}
function profile(records,delta){
 let opportunities=0,unique=0,chosen=0,eligible=0,all=0,low=0,changed=0,non_target_changes=0;
 for(const row of records){
   let wins=0;
   for(const a of row.actions){
     const c=rank(a.candidates,delta),win=c[0].id;
     eligible+=Number(c.some(x=>x.id===GOAL));all++;wins+=Number(win===GOAL);
     changed+=Number(win!==a.route);non_target_changes+=Number(win!==a.route&&win!==GOAL&&a.route!==GOAL);
     if(win===GOAL&&c.length>1&&c[0].score-c[1].score<STORY.target.margin)low++;
   }
   opportunities+=Number(wins>0);unique+=Number(wins===1);chosen+=wins;
 }
 const result={delta,roots:records.length,opportunities,unique,chosen,eligible,all,low_margin:low,changed,non_target_changes,
   opportunity_rate:opportunities/records.length,unique_fraction:opportunities?unique/opportunities:0,low_margin_fraction:chosen?low/chosen:0};
 const t=STORY.target;
 result.checks={opportunity:result.opportunity_rate>=t.opportunity_min&&result.opportunity_rate<=t.opportunity_max,
   unique:result.unique_fraction>=t.unique_fraction_min,margin:result.low_margin_fraction<=t.low_margin_fraction_max,scope:non_target_changes===0};
 result.pass=Object.values(result.checks).every(Boolean);return result;
}
function patchBias(source,delta){
 const lines=source.split("\n"),i=lines.findIndex(s=>s.startsWith("ENC "+GOAL+" "));
 if(i<0)fail("secret ending missing");
 const before=lines[i],m=before.match(/ \| Q:(.*?) \| N:/);
 if(!m||m[1].split(OLD_BIAS).length!==2)fail("unexpected priority");
 const next=m[1].replace(OLD_BIAS,"C("+Number((.22+delta).toFixed(6))+")");
 lines[i]=before.replace(" | Q:"+m[1]+" | N:"," | Q:"+next+" | N:");
 return {source:lines.join("\n"),patch:{line:i+1,before,after:lines[i]},old_priority:m[1],new_priority:next};
}
function runtimeStory(api,original,candidate,records,roots,delta){
 let checks=0,unaffected=0,routeChanges=0,energyChanges=0,maxNumeric=0,maxScoreError=0;
 for(let i=0;i<roots.length;i++){
   const originalObs=api.observeV2(original,roots[i].s),newObs=api.observeV2(candidate,roots[i].s);
   if(!same(originalObs,newObs))fail("observation changed");
   const a=api.auditV2(original,roots[i].s).actions,b=api.auditV2(candidate,roots[i].s).actions;
   for(let j=0;j<a.length;j++){
     const x=a[j],y=b[j],z=records[i].actions[j];
     if(!same(x.scores,y.scores)||x.selected!==y.selected||x.id!==y.id||!same(x.branches.map(b=>b.id),y.branches.map(b=>b.id)))fail("reaction score changed");
     const expected=rank(z.candidates,delta);
     const x1=x.branches.find(b=>b.id===x.selected),y1=y.branches.find(b=>b.id===y.selected);
     if(expected[0].id!==y1.next.encounter||!same(expected.map(c=>c.id),y1.routing.candidates.map(c=>c.id)))fail("cached ranking/runtime disagreement");
     for(const k of Object.keys(x1.next.values))maxNumeric=Math.max(maxNumeric,Math.abs(x1.next.values[k]-y1.next.values[k]));
     energyChanges+=Number(x1.squared_step_energy!==y1.squared_step_energy);
     if(!same(x1.writes,y1.writes)||!same(x1.next.values,y1.next.values))fail("state changed");
     if(!same(x1.routing.candidates.map(c=>c.id).sort(),y1.routing.candidates.map(c=>c.id).sort()))fail("gate changed");
     for(const c of expected){const d=y1.routing.candidates.find(x=>x.id===c.id);maxScoreError=Math.max(maxScoreError,Math.abs(c.score-d.score));}
     routeChanges+=Number(x1.next.encounter!==y1.next.encounter);
     unaffected+=Number(x1.next.encounter===y1.next.encounter);
     checks++;
   }
 }
 if(maxScoreError>1e-12||maxNumeric!==0||energyChanges)fail("scope invariant");
 return {checks,unaffected,routeChanges,energyChanges,maxNumeric,maxScoreError};
}
function fullReplay(api,w,v,words){
 const term=x=>Object.keys(w.pages[x].options).length===0;
 function roll(world,seq){let s=api.initialV2(world),trace=[];for(const n of seq){const o=api.observeV2(world,s);if(o.status!=="decision")return {end:s.encounter,terminal:term(s.encounter),trace};const a=o.actions[Math.floor(n*o.actions.length/4294967296)],b=api.stepV2(world,s,a.id);trace.push([s.encounter,a.id,b.id,b.next.encounter,b.next.turn]);s=b.next;}return {end:"timeout",terminal:false,trace};}
 const m={campaigns:words.length,baseline_complete:0,candidate_complete:0,baseline_goal:0,candidate_goal:0,changed_endings:0,changed_paths:0,pre_sirens_prefix_changes:0};
 for(const seq of words){const a=roll(w,seq),b=roll(v,seq);m.baseline_complete+=Number(a.terminal);m.candidate_complete+=Number(b.terminal);m.baseline_goal+=Number(a.end===GOAL);m.candidate_goal+=Number(b.end===GOAL);m.changed_endings+=Number(a.end!==b.end);m.changed_paths+=Number(!same(a.trace,b.trace));
   const pre=tr=>{const i=tr.findIndex(x=>x[0]===SIRENS);return i<0?tr:tr.slice(0,i);};
   m.pre_sirens_prefix_changes+=Number(!same(pre(a.trace),pre(b.trace)));
 }
 if(m.pre_sirens_prefix_changes)fail("upstream route changed");
 return m;
}
function story(api,source){
 const w=api.compileV2(source),cal=firstRoots(api,w,STORY.calibration),rows=capture(api,w,cal.roots);
 const grid=STORY.deltas.map(d=>profile(rows,d)),feasible=grid.filter(x=>x.pass).sort((a,b)=>Math.abs(a.delta)-Math.abs(b.delta)||a.delta-b.delta);
 if(!feasible.length)fail("no story candidate");
 const selected=feasible[0],patched=patchBias(source,selected.delta),v=api.compileV2(patched.source);
 // Frozen selection: validation seeds are not used above.
 const validation=[];
 for(const c of STORY.validation){
   const data=firstRoots(api,w,c),r=capture(api,w,data.roots);
   validation.push({cohort:c,baseline:profile(r,0),selected:profile(r,selected.delta),
     runtime:runtimeStory(api,w,v,r,data.roots,selected.delta),full_replay:fullReplay(api,w,v,data.words)});
 }
 const sham=source.replace(" | Q:"+patched.old_priority+" | N:"," | Q:ADD("+patched.old_priority+",C(0)) | N:");
 const shamW=api.compileV2(sham),shamChecks=runtimeStory(api,w,shamW,rows,cal.roots,0);
 if(shamChecks.routeChanges)fail("sham changed route");
 return {receipt:{contract:STORY,grid,feasible_count:feasible.length,baseline:profile(rows,0),selected,
   patch:patched.patch,calibration_runtime:runtimeStory(api,w,v,rows,cal.roots,selected.delta),sham:shamChecks,validation},
   patched:patched.source};
}
export function runSuite({api=api0,source}){
 const econ=economics(api),s=story(api,source);
 return {receipt:{evidence:"bounded calibration-selected authoring edits; deterministic public validation, no model calls",economics:econ.receipt,story:s.receipt},economicCases:econ.cases,patched:s.patched};
}
