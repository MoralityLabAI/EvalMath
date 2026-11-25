// SRG-13: provenance-separated evidence chain and bounded truce coordination.
// Candidate authoring hypothesis; no production world changes.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
import {evaluate as evalExpr} from '../srg04/swmd-runtime.mjs';
const GOAL="page_secret_undercover_truce",SIRENS="page_sirens_at_the_rollup_door",TRUCE="opt_page_sirens_at_the_rollup_door_2";
const S="char_pink.Rat_Suspicion",B="char_blonde.Sadistic_Escalation",L="char_white.Crew_Loyalty";
export const LEDGER=["char_pink.Timeline_Record","char_pink.Radio_Record","char_pink.Review_Request"];
export const READY="char_white.Truce_Coordination";
const NEW=[...LEDGER,READY];
const C=x=>"C("+Number(x.toFixed(8))+")",P=k=>"P("+k+")",mul=(...args)=>"MUL("+args.join(",")+")",add=(...args)=>"ADD("+args.join(",")+")";
const fail=m=>{throw Error("SRG13: "+m);},same=(a,b)=>JSON.stringify(a)===JSON.stringify(b),sum=(a,f)=>a.reduce((n,x)=>n+f(x),0);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export const CONTRACT=Object.freeze({
 development:[{seed:0x53521101,n:128},{seed:0x53521102,n:128},{seed:0x53521103,n:128}],
 validation:[{seed:0x53521311,n:256},{seed:0x53521312,n:256}],
 grid:{upstream:[0,.04,.08,.12],pair_scale:[1,2],priority:[0,1,2,3,4],offset:[-.15,-.1,-.05,0]},
 target:{opportunity_min:.125,opportunity_max:.2,unique_min:.7,unique_truce_share_min:.5,low_margin_max:.2,margin:.03,max_existing_coordinate_adjustment:.12,max_ledger_coordinate_step:.125,max_edited_step_energy_ratio:2.5,max_priority_boost:.5},
 interpretation:"Ledger is investigative work/readiness, not verified guilt or posterior probability. Generic late review prose supports only a request credit; the new cooperation effect is an author-review hypothesis. No gate changes."
});
// Explicit reaction provenance. Assign maximum once (revisits cannot mint
// more credit). All entries identify what the original prose supports.
const CREDIT=Object.freeze({
 rxn_page_pink_ambush_theory_0_0:[0,.125,"timestamps enumerated"],
 rxn_page_pink_ambush_theory_0_2:[0,.0625,"unverified accusation"],
 rxn_page_cadillac_trunk_2_0:[1,.125,"radio inspected; exposure, not identity"],
 rxn_page_cadillac_trunk_2_1:[1,.0625,"radio in hand, no verified new conclusion"],
 rxn_page_cadillac_trunk_2_2:[1,.03125,"radio inquiry without an answer"],
 rxn_page_eddie_and_blonde_story_1_0:[2,.0625,"powder-burn audit requested"],
 rxn_page_eddie_and_blonde_story_1_1:[2,.0625,"powder-burn audit requested"],
 rxn_page_eddie_and_blonde_story_1_2:[2,.0625,"powder-burn audit requested"],
 rxn_page_eddie_and_blonde_story_2_0:[2,.09375,"timeline check requested"],
 rxn_page_eddie_and_blonde_story_2_1:[2,.09375,"timeline check requested"],
 rxn_page_eddie_and_blonde_story_2_2:[2,.09375,"timeline check requested"]
});
function readiness(v,pairScale){
 const [a,b,c]=LEDGER.map(k=>v[k]*8);
 return .125*Math.min(1,pairScale*(a*b+a*c+b*c)/2);
}
function readinessFormula(pairScale){
 const [a,b,c]=LEDGER.map(P);
 return mul(C(.125),"MIN(C(1),"+mul(C(32*pairScale),add(mul(a,b),mul(a,c),mul(b,c)))+")");
}
function distance(v){return (v[L]-clamp(v[L],-.53,.77))**2+Math.max(0,.08-v[S])**2+Math.max(0,v[B]-.35)**2;}
function field(line,label,next){
 const m=line.match(new RegExp(" \\| "+label+":(.*?) \\| "+next+":"));
 if(!m)fail("missing "+label);
 return m[1];
}
function putField(line,label,next,value){const old=field(line,label,next);return line.replace(" | "+label+":"+old+" | "+next+":"," | "+label+":"+value+" | "+next+":");}
export function patch(source,p,{ledger=true}={}){
 const rows=source.split("\n"),changes=[];
 for(let i=0;i<rows.length;i++){
   const before=rows[i];let after=before;
   if(before.startsWith("ORX ")){
     const id=before.split(" -> ")[0].split("/")[1];
     let e=field(before,"E","D");
     const spec=CREDIT[id];
     if(ledger&&spec){
       const [j,v]=spec,k=LEDGER[j];e+="; SET "+k+" = MAX("+P(k)+","+C(v)+")";
     }
     // Only bounded changes to existing S effects; action 0_0 gives actual
     // timestamps, radio inspection prevents part of the original decrease.
     // Late review preserves suspicion only when an earlier record exists.
     if(p.upstream){
       const es=e.split("; "),j=es.findIndex(x=>x.startsWith("SET "+S+" = "));
       if(id==="rxn_page_pink_ambush_theory_0_0"){
         if(j<0||es[j].split("C(0.11)").length!==2)fail("timeline S");
         es[j]=es[j].replace("C(0.11)",C(.11+p.upstream/2));
       }
       if(id==="rxn_page_cadillac_trunk_2_0"){
         if(j<0||es[j].split("C(-0.09)").length!==2)fail("radio S");
         es[j]=es[j].replace("C(-0.09)",C(-.09+p.upstream/2));
       }
       if(id.startsWith("rxn_page_eddie_and_blonde_story_2_")){
         if(j<0||es[j].split("C(-0.09)").length!==2)fail("review S");
         // Previous timeline/radio credit is a prerequisite for preserving
         // unresolved suspicion. No claim that the generic prose proves guilt.
         es[j]=es[j].replace("C(-0.09)",add(C(-.09),mul(C(p.upstream), "MIN(C(1),"+mul(C(8),add(P(LEDGER[0]),P(LEDGER[1])))+")")));
       }
       e=es.join("; ");
     }
     if(ledger&&before.startsWith("ORX opt_"+SIRENS+"_"))e+="; SET "+READY+" = "+(before.startsWith("ORX "+TRUCE+"/")?readinessFormula(p.pair_scale):"C(0)");
     after=putField(before,"E","D",e);
   }
   if(before.startsWith("ENC "+GOAL+" ")&&(p.priority||p.offset)){
     const old=field(before,"Q","N");if(old.split("C(0.22)").length!==2)fail("original priority");
     const base=old.replace("C(0.22)",C(.22+p.offset));
     after=putField(before,"Q","N",p.priority?add(base,mul(C(p.priority),P(READY))):base);
   }
   if(before!==after){changes.push({line:i+1,before,after});rows[i]=after;}
 }
 if(ledger){
   const index=rows.findIndex(x=>x.startsWith("SPOOL "));if(index<0)fail("missing spools");
   rows.splice(index,0,...NEW.map(k=>"VAR "+k+" = 0 | public"));
 }
 return {source:rows.join("\n"),changes,added_variables:ledger?NEW:[]};
}
function words(c){let x=c.seed>>>0;const r=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};return Array.from({length:c.n},()=>Array.from({length:24},r));}
function project(s){return Object.fromEntries(Object.entries(s.values).filter(([k])=>!NEW.includes(k)));}
function originalState(s){return {...s,values:project(s)};}
function originalAction(api,w,s,id){return api.stepV2(w,originalState(s),id);}
function scopeCheck(old,newWorld){
 const ok=(a,b)=>{if(!same(a,b))fail("scope changed");};
 ok(old.id,newWorld.id);ok(old.spools,newWorld.spools);
 for(const k of Object.keys(old.coordinates))ok(old.coordinates[k],newWorld.coordinates[k]);
 if(Object.keys(newWorld.coordinates).length!==Object.keys(old.coordinates).length+NEW.length)fail("coordinates");
 for(const [id,p] of Object.entries(old.pages)){
   const v=newWorld.pages[id];ok(p.gate,v.gate);ok(p.lo,v.lo);ok(p.hi,v.hi);ok(p.index,v.index);ok(p.text,v.text);ok(p.title,v.title);
   if(id!==GOAL)ok(p.priority,v.priority);
   ok(Object.keys(p.options),Object.keys(v.options));
   for(const [oid,a] of Object.entries(p.options)){
     const b=v.options[oid];ok(a.visible,b.visible);ok(a.performable,b.performable);ok(a.text,b.text);
     ok(a.reactions.map(x=>x.id),b.reactions.map(x=>x.id));
     for(let i=0;i<a.reactions.length;i++){
       const x=a.reactions[i],y=b.reactions[i];ok(x.to,y.to);ok(x.gate,y.gate);ok(x.desirability,y.desirability);ok(x.text,y.text);
       if(!CREDIT[x.id]&&!oid.startsWith("opt_"+SIRENS+"_")&&!x.id.startsWith("rxn_page_eddie_and_blonde_story_2_"))ok(x.effects,y.effects);
       if(y.effects.length<x.effects.length)fail("lost effect");
       for(let j=0;j<x.effects.length;j++){ok(x.effects[j].kind,y.effects[j].kind);ok(x.effects[j].key,y.effects[j].key);
         if(x.effects[j].key!==S||(!CREDIT[x.id]&&!x.id.startsWith("rxn_page_eddie_and_blonde_story_2_")))ok(x.effects[j].value,y.effects[j].value);
       }
     }
   }
 }
}
function collect(api,w,old,seqs,upstream){
 const roots=[],scope={edited_steps:0,max_edited_energy_ratio:0,max_existing_adjustment:0,max_ledger_step:0,selected_steps:0,goal_progress_by_source:{},increment_energy_by_source:{},nonzero_ledger_writes:0};
 for(let trial=0;trial<seqs.length;trial++){
   let s=api.initialV2(w),prefixEnergy=0,contributions=Array(3).fill(0),seen=[];
   for(let j=0;j<seqs[trial].length;j++){
     if(s.encounter===SIRENS){roots.push({s,trial,prefixEnergy,contributions,seen});break;}
     const o=api.observeV2(w,s);if(o.status!=="decision")break;
     const a=o.actions[Math.floor(seqs[trial][j]*o.actions.length/4294967296)],b=api.stepV2(w,s,a.id),base=originalAction(api,old,s,a.id);
     if(base.id!==b.id||base.next.encounter!==b.next.encounter)fail("same-state reaction/route outside sirens");
     const delta=Math.max(...Object.keys(old.coordinates).map(k=>Math.abs(base.next.values[k]-b.next.values[k])));
     const ld=Math.max(...NEW.map(k=>Math.abs(s.values[k]-b.next.values[k])));
     scope.selected_steps++;
     if(delta>1e-12||ld>1e-12){
       scope.edited_steps++;scope.max_existing_adjustment=Math.max(scope.max_existing_adjustment,delta);
       scope.max_ledger_step=Math.max(scope.max_ledger_step,ld);
       const ratio=base.squared_step_energy?b.squared_step_energy/base.squared_step_energy:Infinity;
       scope.max_edited_energy_ratio=Math.max(scope.max_edited_energy_ratio,ratio);
       const key=s.encounter;scope.goal_progress_by_source[key]=(scope.goal_progress_by_source[key]??0)+distance(base.next.values)-distance(b.next.values);
       scope.increment_energy_by_source[key]=(scope.increment_energy_by_source[key]??0)+NEW.reduce((n,k)=>n+(b.next.values[k]-s.values[k])**2,0);
     }
     for(let k=0;k<3;k++)if(b.next.values[LEDGER[k]]!==s.values[LEDGER[k]]){
       if(!CREDIT[b.id]||CREDIT[b.id][0]!==k||b.next.values[LEDGER[k]]!==Math.max(s.values[LEDGER[k]],CREDIT[b.id][1]))fail("provenance update");
       contributions[k]++;scope.nonzero_ledger_writes++;
     }
     if(CREDIT[b.id])seen.push(b.id);
     prefixEnergy+=b.squared_step_energy;s=b.next;
   }
 }
 return {roots,scope,upstream};
}
function capture(api,w,roots,old,pairScale){
 return roots.map(r=>({r,actions:api.auditV2(w,r.s).actions.map(o=>{
   const b=o.branches.find(b=>b.id===o.selected);
   if(!b?.next||!b.routing.candidates.length)fail("missing wild branch");
   const want=o.id===TRUCE?readiness(r.s.values,pairScale):0;
   if(Math.abs(b.next.values[READY]-want)>1e-12)fail("readiness formula");
   const prior=originalAction(api,old,r.s,o.id);
   if(prior.id!==b.id||!same(prior.next.values,project(b.next)))fail("sirens original numeric changed");
   return {id:o.id,reaction:b.id,post:b.next.values,candidates:b.routing.candidates,energy:b.squared_step_energy,base_energy:prior.squared_step_energy};
 })}));
}
function rank(c,boost){return c.map(x=>({...x,score:x.score+(x.id===GOAL?boost:0)})).sort((a,b)=>b.score-a.score||a.index-b.index);}
function profile(records,p,scope,{ranked=false}={}){
 const o={roots:records.length,actions:0,opportunities:0,unique:0,unique_truce:0,truce_wins:0,winning_actions:0,low_margin:0,gate_eligible_truce:0,truce_ready:0,truce_ready_and_eligible:0,
 alias:0,unique_truce_with_two_sources:0,ledger_positive_distribution:{},max_readiness:0,max_final_energy_ratio:0,max_final_ledger_step:0,max_priority_boost:0,scope};
 for(const x of records){const wins=[],rs=[],r=x.r.s;
   const support=LEDGER.filter(k=>r.values[k]>0).length;o.ledger_positive_distribution[support]=(o.ledger_positive_distribution[support]??0)+1;
   for(const a of x.actions){
     const ready=a.post[READY],c=ranked?a.candidates:rank(a.candidates,p.offset+ready*p.priority);
     o.actions++;rs.push({id:a.id,c});
     o.max_final_energy_ratio=Math.max(o.max_final_energy_ratio,a.base_energy?a.energy/a.base_energy:Infinity);
     o.max_final_ledger_step=Math.max(o.max_final_ledger_step,Math.abs(ready-r.values[READY]));
     o.max_priority_boost=Math.max(o.max_priority_boost,ready*p.priority);
     if(a.id===TRUCE){
       const eligible=c.some(x=>x.id===GOAL);o.gate_eligible_truce+=Number(eligible);o.truce_ready+=Number(ready>0);o.truce_ready_and_eligible+=Number(ready>0&&eligible);
       o.max_readiness=Math.max(o.max_readiness,ready);if(ready>0&&support<2)fail("single-source coordination");
     }
     if(c[0].id===GOAL){wins.push(a.id);o.winning_actions++;o.truce_wins+=Number(a.id===TRUCE);if(c.length>1&&c[0].score-c[1].score<CONTRACT.target.margin)o.low_margin++;}
   }
   const tr=rs.find(x=>x.id===TRUCE);if(!tr)fail("missing truce");
   o.alias+=Number(rs.some(x=>x.id!==TRUCE&&same(x.c,tr.c)));
   o.opportunities+=Number(wins.length>0);o.unique+=Number(wins.length===1);
   if(wins.length===1&&wins[0]===TRUCE){o.unique_truce++;o.unique_truce_with_two_sources+=Number(support>=2);}
 }
 o.opportunity_rate=o.opportunities/o.roots;o.unique_fraction=o.opportunities?o.unique/o.opportunities:0;o.unique_truce_share=o.unique?o.unique_truce/o.unique:0;o.low_margin_fraction=o.winning_actions?o.low_margin/o.winning_actions:0;
 const t=CONTRACT.target;
 o.checks={opportunity:o.opportunity_rate>=t.opportunity_min&&o.opportunity_rate<=t.opportunity_max,unique:o.unique_fraction>=t.unique_min,
 unique_truce:o.unique_truce_share>=t.unique_truce_share_min,margin:o.low_margin_fraction<=t.low_margin_max,
 warrant:o.unique_truce===o.unique_truce_with_two_sources,existing_displacement:scope.max_existing_adjustment<=t.max_existing_coordinate_adjustment+1e-12,ledger_step:Math.max(scope.max_ledger_step,o.max_final_ledger_step)<=t.max_ledger_coordinate_step+1e-12,energy:Math.max(scope.max_edited_energy_ratio,o.max_final_energy_ratio)<=t.max_edited_step_energy_ratio,priority_budget:o.max_priority_boost<=t.max_priority_boost+1e-12};
 o.pass=Object.values(o.checks).every(Boolean);return o;
}
function auditCompiled(api,w,cache,p){
 let checks=0,forced=0,maxScoreError=0,maxStateError=0;
 for(const r of cache){
   const fresh=api.auditV2(w,r.r.s).actions;
   for(const a of r.actions){
     const o=fresh.find(x=>x.id===a.id),b=o.branches.find(b=>b.id===o.selected);
     const expected=rank(a.candidates,p.offset+a.post[READY]*p.priority);
     if(a.reaction!==o.selected||!same(expected.map(c=>c.id),b.routing.candidates.map(c=>c.id)))fail("compiled rank/selection");
     for(const c of expected){const z=b.routing.candidates.find(x=>x.id===c.id);maxScoreError=Math.max(maxScoreError,Math.abs(z.score-c.score));}
     for(const k of Object.keys(a.post))maxStateError=Math.max(maxStateError,Math.abs(a.post[k]-b.next.values[k]));
     for(const branch of o.branches){if(!branch.next)fail("forced branch missing");if(Math.abs(branch.next.values[READY]-(a.id===TRUCE?readiness(r.r.s.values,p.pair_scale):0))>1e-12)fail("forced readiness");forced++;}
     checks++;
   }
 }
 if(maxScoreError>1e-12||maxStateError>1e-12)fail("compiled numerical mismatch");
 return {checks,forced,maxScoreError,maxStateError};
}
function aliasOriginal(api,w,seq){
 let roots=0,alias=0,unique=0,opportunities=0,unique_truce=0;
 for(const xs of seq){let s=api.initialV2(w);for(const n of xs){
   if(s.encounter===SIRENS){
     const a=api.auditV2(w,s).actions.map(o=>({id:o.id,b:o.branches.find(b=>b.id===o.selected)})),tr=a.find(x=>x.id===TRUCE);
     const wins=a.filter(x=>x.b.next.encounter===GOAL);
     roots++;alias+=Number(a.some(x=>x.id!==TRUCE&&same(x.b.routing.candidates,tr.b.routing.candidates)));opportunities+=Number(wins.length>0);unique+=Number(wins.length===1);unique_truce+=Number(wins.length===1&&wins[0].id===TRUCE);break;
   }
   const o=api.observeV2(w,s);if(o.status!=="decision")break;s=api.stepV2(w,s,o.actions[Math.floor(n*o.actions.length/4294967296)].id).next;
 }}
 return {roots,alias,opportunities,unique,unique_truce};
}
function replay(api,w,seq){
 let completed=0,secret=0,timeout=0,all={};
 for(const xs of seq){let s=api.initialV2(w);for(const n of xs){const o=api.observeV2(w,s);if(o.status!=="decision")break;s=api.stepV2(w,s,o.actions[Math.floor(n*o.actions.length/4294967296)].id).next;}
 const o=api.observeV2(w,s);completed+=Number(o.status==="terminal");secret+=Number(s.encounter===GOAL);timeout+=Number(o.status==="decision");all[s.encounter]=(all[s.encounter]??0)+1;}
 return {campaigns:seq.length,completed,secret,timeout,endings:all};
}
function ablations(api,w,records,p){
 let probes=0,zero_single=0,original_unique=0,all_deleted_truce_losses=0,unique_source_necessity=[0,0,0],zero_source_effect=0;
 for(const row of records){
   const s=row.r.s,a=api.stepV2(w,s,TRUCE),ready=a.next.values[READY],unique=a.next.encounter===GOAL&&api.observeV2(w,s).actions.filter(o=>o.id!==TRUCE).every(o=>api.stepV2(w,s,o.id).next.encounter!==GOAL);
   original_unique+=Number(unique);
   for(let i=0;i<8;i++){
     const t={...s,values:{...s.values}};for(let j=0;j<3;j++)if(!(i>>>j&1))t.values[LEDGER[j]]=0;
     const b=api.stepV2(w,t,TRUCE),expected=readiness(t.values,p.pair_scale);
     if(Math.abs(b.next.values[READY]-expected)>1e-12)fail("ablation readiness");
     if(LEDGER.filter(k=>t.values[k]>0).length<2){if(b.next.values[READY]!==0)fail("single source");zero_single++;}
     if(i===0){zero_source_effect+=Number(b.next.values[READY]===0);if(unique&&b.next.encounter!==GOAL)all_deleted_truce_losses++;}
     for(let j=0;j<3;j++)if(i===(7^(1<<j))&&unique&&b.next.encounter!==GOAL)unique_source_necessity[j]++;
     probes++;
   }
 }
 return {probes,zero_single,zero_source_effect,original_unique,all_deleted_truce_losses,unique_source_necessity};
}
export function runSuite({source,api=runtime,validate=true}){
 const old=api.compileV2(source),dev=CONTRACT.development.map(c=>({c,seq:words(c)})),grid=[],caches=new Map();
 for(const upstream of CONTRACT.grid.upstream)for(const pair_scale of CONTRACT.grid.pair_scale){
   const p=patch(source,{upstream,pair_scale,priority:0,offset:0}),w=api.compileV2(p.source);scopeCheck(old,w);
   const rows=dev.map(d=>{const c=collect(api,w,old,d.seq,upstream);return {c,cache:capture(api,w,c.roots,old,pair_scale)};});caches.set([upstream,pair_scale].join(","),rows);
   for(const priority of CONTRACT.grid.priority)for(const offset of CONTRACT.grid.offset){const params={upstream,pair_scale,priority,offset},metrics=rows.map(r=>profile(r.cache,params,r.c.scope));
     grid.push({...params,metrics,full:sum(metrics,m=>Number(m.pass)),checks:sum(metrics,m=>Object.values(m.checks).filter(Boolean).length),edit_cost:Math.round(upstream/.04)+priority+Math.round(Math.abs(offset)/.05)+pair_scale-1});
   }
 }
 const ranked=[...grid].sort((a,b)=>b.full-a.full||b.checks-a.checks||a.edit_cost-b.edit_cost||a.upstream-b.upstream||a.pair_scale-b.pair_scale||a.priority-b.priority||a.offset-b.offset);
 const selected=ranked[0],feasible=grid.filter(x=>x.full===dev.length).length,params={upstream:selected.upstream,pair_scale:selected.pair_scale,priority:selected.priority,offset:selected.offset};
 const p=patch(source,params),w=api.compileV2(p.source);scopeCheck(old,w);
 const development=dev.map((d,i)=>{
   const r=caches.get([selected.upstream,selected.pair_scale].join(","))[i];
   return {cohort:d.c,original:aliasOriginal(api,old,d.seq),selected:selected.metrics[i],runtime:auditCompiled(api,w,r.cache,params)};
 });
 const validation=[];
 if(validate)for(const c of CONTRACT.validation){
   const seq=words(c),zeroWorld=api.compileV2(patch(source,{...params,priority:0,offset:0}).source),z=collect(api,zeroWorld,old,seq,selected.upstream),cache=capture(api,zeroWorld,z.roots,old,params.pair_scale);
   const actual=capture(api,w,z.roots,old,params.pair_scale),metrics=profile(actual,params,z.scope,{ranked:true});
   const expected=profile(cache,params,z.scope);
   if(!same(metrics,expected))fail("compiled metric drift");
   validation.push({cohort:c,original:aliasOriginal(api,old,seq),selected:metrics,runtime:auditCompiled(api,w,cache,params),
     ablations:ablations(api,w,cache,params),baseline_campaign:replay(api,old,seq),candidate_campaign:replay(api,w,seq)});
 }
 const outcome=feasible>0&&validate&&validation.every(v=>v.selected.pass&&v.candidate_campaign.completed===v.cohort.n)?"PASS_FINITE":"FAIL";
 return {receipt:{evidence:"public reused development and fresh-seed finite validation; candidate authoring hypothesis; no model calls",contract:CONTRACT,provenance:CREDIT,grid_size:grid.length,feasible_count:feasible,selected:{...params,full:selected.full,checks:selected.checks,edit_cost:selected.edit_cost},grid,development,validation,outcome},
   candidate:p.source,patch_manifest:{changes:p.changes,added_variables:p.added_variables}};
}
