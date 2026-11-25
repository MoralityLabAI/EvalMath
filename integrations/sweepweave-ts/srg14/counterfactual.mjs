// SRG-14: full-history choice swaps on the frozen SRG-13 candidate.
// The intervention is one legal choice at a reached prefix, followed by
// the same exogenous policy words indexed by decision number. No state or
// formula edits are made to the authored world.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';

export const CONTRACT=Object.freeze({
  cohorts:[{seed:0x53521411,campaigns:128},{seed:0x53521412,campaigns:128}],
  maxActions:24, horizons:[1,3],
  sites:[
    {page:"page_pink_ambush_theory",investigation:[0],label:"timeline"},
    {page:"page_cadillac_trunk",investigation:[2],label:"radio"},
    {page:"page_eddie_and_blonde_story",investigation:[1,2],label:"review"}
  ],
  goal:"page_secret_undercover_truce",
  sirens:"page_sirens_at_the_rollup_door",
  truce:"opt_page_sirens_at_the_rollup_door_2",
  ledger:["char_pink.Timeline_Record","char_pink.Radio_Record","char_pink.Review_Request"],
  readiness:"char_white.Truce_Coordination",
  prior:"uniform over each fixed cohort's xorshift32 streams; descriptive finite policy interventions, not a human-play distribution",
  objective:"binary terminal utility: secret ending=1, other endings=0; no inferred moral preference",
  intervention:"first visit to each of three upstream encounters on the factual trajectory; enumerate every legal action, then use common random words at the same absolute decision index",
  horizon:"exact full-state existential reachability, h actions from first sirens; no observation-restricted policy or model performance claimed",
  deletion:"set only the three ledger coordinates to zero at the first sirens state, retain all other numeric state/history; controlled readout, not natural indirect effect"
});
const G=CONTRACT.goal,F=CONTRACT.sirens,T=CONTRACT.truce,K=CONTRACT.ledger,R=CONTRACT.readiness;
const S="char_pink.Rat_Suspicion",B="char_blonde.Sadistic_Escalation",L="char_white.Crew_Loyalty";
const fail=m=>{throw Error("SRG14: "+m);},same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const sum=(a,f)=>a.reduce((n,x)=>n+f(x),0),mean=(a,f)=>a.length?sum(a,f)/a.length:null;
const clone=x=>JSON.parse(JSON.stringify(x));
const own=(x,k)=>Object.hasOwn(x,k);
const coord=(v,k)=>v[k]??0;
const term=(w,s)=>Object.keys(w.pages[s.encounter].options).length===0;
const dist=v=>(v[L]-Math.max(-.53,Math.min(.77,v[L])))**2+Math.max(0,.08-v[S])**2+Math.max(0,v[B]-.35)**2;
const bit=x=>Number(Boolean(x));
const count=(o,k,n=1)=>o[k]=(o[k]??0)+n;
function sequences(c){
 let x=c.seed>>>0;const next=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};
 return Array.from({length:c.campaigns},()=>Array.from({length:CONTRACT.maxActions},next));
}
function actionIndex(id){const n=Number(id.slice(id.lastIndexOf("_")+1));if(!Number.isInteger(n))fail("option suffix");return n;}
function legal(api,w,s){return api.observeV2(w,s).actions.map(a=>a.id);}
function selected(api,w,s,word){
 const a=legal(api,w,s);if(!a.length)fail("empty action menu");return a[Math.floor(word*a.length/4294967296)];
}
function route(api,w,s,a){const b=api.stepV2(w,s,a);if(!b.next)fail("blocked route");return b;}
function stepRecord(s,a,b){return {from:s.encounter,action:a,reaction:b.id,to:b.next.encounter,turn:s.turn,energy:b.squared_step_energy,goal_progress:dist(s.values)-dist(b.next.values)};}
function roll(api,w,initial,words,start=0,forced=null,collect=false){
 let s=initial,firstSirens=null,firstSirensIndex=null,trace=[],prefixes={};
 for(let j=start;j<words.length;j++){
   if(term(w,s))return {end:s.encounter,complete:true,firstSirens,firstSirensIndex,trace,prefixes};
   if(s.encounter===F&&firstSirens===null){firstSirens=s;firstSirensIndex=j;}
   const site=CONTRACT.sites.find(p=>p.page===s.encounter);
   if(collect&&site&&!own(prefixes,site.label))prefixes[site.label]={s,j};
   const a=j===start&&forced!==null?forced:selected(api,w,s,words[j]);
   if(!legal(api,w,s).includes(a))fail("forced action illegal");
   const b=route(api,w,s,a);trace.push(stepRecord(s,a,b));s=b.next;
 }
 if(s.encounter===F&&firstSirens===null){firstSirens=s;firstSirensIndex=words.length;}
 return {end:term(w,s)?s.encounter:"timeout",complete:term(w,s),firstSirens,firstSirensIndex,trace,prefixes};
}
function reach(api,w,s,h,stats){
 stats.nodes++;
 if(term(w,s))return s.encounter===G;
 if(h===0)return false;
 // Do not short circuit: exact bounded tree enumeration for the receipt.
 let yes=false;for(const a of legal(api,w,s))yes=reach(api,w,route(api,w,s,a).next,h-1,stats)||yes;
 return yes;
}
function goalAudit(api,w,s,h,stats){
 const actions=legal(api,w,s),out={};
 for(const a of actions)out[a]=reach(api,w,route(api,w,s,a).next,h-1,stats);
 const winning=Object.keys(out).filter(a=>out[a]);
 return {attainable:winning.length>0,unique:winning.length===1,truce:winning.includes(T),unique_truce:winning.length===1&&winning[0]===T,winners:winning};
}
function deleted(s){
 const v={...s.values};for(const k of K)if(own(v,k))v[k]=0;return {...s,values:v};
}
function snapshot(api,w,s,stats){
 if(!s)return {reached:false,h1:{attainable:false,unique:false,truce:false,unique_truce:false,winners:[]},h3:{attainable:false,unique:false,truce:false,unique_truce:false,winners:[]},
  noLedgerH1:{attainable:false,unique:false,truce:false,unique_truce:false,winners:[]},ledger:[0,0,0],gateDistance:null,suspicion:null,readiness:0,targetMargin:null};
 const h1=goalAudit(api,w,s,1,stats),h3=goalAudit(api,w,s,3,stats);
 if(h1.attainable&&!h3.attainable||h1.truce&&!h3.truce)fail("horizon monotonicity");
 const noLedgerH1=goalAudit(api,w,deleted(s),1,stats);
 const b=route(api,w,s,T),rank=b.routing.candidates,goal=rank.find(x=>x.id===G);
 const others=rank.filter(x=>x.id!==G);
 const margin=goal&&others.length?goal.score-others[0].score:null;
 return {reached:true,h1,h3,noLedgerH1,ledger:K.map(k=>coord(s.values,k)),gateDistance:dist(s.values),suspicion:s.values[S],readiness:coord(b.next.values,R),targetMargin:margin};
}
function outcome(api,w,r,stats){
 const x=snapshot(api,w,r.firstSirens,stats);
 return {...x,complete:r.complete,ending:r.end,random_goal:r.end===G,steps:r.trace.length,
  future_energy:sum(r.trace,x=>x.energy),future_goal_progress:sum(r.trace,x=>x.goal_progress)};
}
const FLAGS=["reached","complete","random_goal","h1_attainable","h1_truce","h1_unique_truce","h3_attainable","h3_truce","noLedgerH1_unique_truce"];
function flag(r,k){
 if(k.startsWith("h1_"))return bit(r.h1[k.slice(3)]);
 if(k.startsWith("h3_"))return bit(r.h3[k.slice(3)]);
 if(k.startsWith("noLedgerH1_"))return bit(r.noLedgerH1[k.slice(11)]);
 return bit(r[k]);
}
function initSite(){return {prefixes:0,paired_prefixes:0,arms:0,complete_arms:0,reached_arms:0,factual_replay_checks:0,
 intervention_vs_factual:{swaps:0,first_reaction_changes:0,first_destination_changes:0,ending_changes:0,goal_gains:0,goal_losses:0,h1_gains:0,h1_losses:0,h3_gains:0,h3_losses:0,unique_truce_gains:0,unique_truce_losses:0},
 exact_choice_pair:{pairs:0,h1_disagreement:0,h3_disagreement:0,unique_truce_disagreement:0,random_goal_disagreement:0},
 contrast:{prefixes:0,investigation_arms:0,other_arms:0,totals:Object.fromEntries(FLAGS.map(k=>[k,0])),same_history_at_sirens:0,ledger_delta:[0,0,0],readiness_delta:0,goal_distance_delta:0,goal_distance_pairs:0,
  paired_truce_gains:0,paired_truce_losses:0,paired_h3_gains:0,paired_h3_losses:0,all_ledger_deleted_gain_pairs:0,all_ledger_deleted_loss_pairs:0,pairs:0},
 action_distribution:{},upstream_effect:{trials:0,mean_goal_distance_range:0,max_goal_distance_range:0,nonzero_goal_distance_range:0,max_energy_ratio:0},
 by_action:{}};
}
function recordSwap(o,a,b){
 const z=o.intervention_vs_factual;z.swaps++;z.first_reaction_changes+=bit(a.first.reaction!==b.first.reaction);z.first_destination_changes+=bit(a.first.to!==b.first.to);
 z.ending_changes+=bit(a.result.ending!==b.result.ending);
 for(const [name,g,l] of [["random_goal","goal_gains","goal_losses"],["h1_attainable","h1_gains","h1_losses"],["h3_attainable","h3_gains","h3_losses"],["h1_unique_truce","unique_truce_gains","unique_truce_losses"]]){
   const d=flag(a.result,name)-flag(b.result,name);z[g]+=bit(d>0);z[l]+=bit(d<0);
 }
}
function byAction(o,a){
 const z=o.by_action[a.id]??={arms:0,reached:0,complete:0,random_goal:0,h1_attainable:0,h1_truce:0,h1_unique_truce:0,h3_attainable:0,h3_truce:0,ledger_sum:[0,0,0]};
 z.arms++;for(const k of Object.keys(z))if(FLAGS.includes(k))z[k]+=flag(a.result,k);
 for(let j=0;j<3;j++)z.ledger_sum[j]+=a.result.ledger[j];
}
function contrast(o,site,arms){
 const inv=arms.filter(a=>site.investigation.includes(actionIndex(a.id))),other=arms.filter(a=>!site.investigation.includes(actionIndex(a.id)));
 if(!inv.length||!other.length)return;
 const c=o.contrast;c.prefixes++;c.investigation_arms+=inv.length;c.other_arms+=other.length;
 // Each factual prefix carries one unit weight; within each group average
 // over its available choices. This avoids over-weighting review's two arms.
 for(const k of FLAGS)c.totals[k]+=mean(inv,a=>flag(a.result,k))-mean(other,a=>flag(a.result,k));
 for(let j=0;j<3;j++)c.ledger_delta[j]+=mean(inv,a=>a.result.ledger[j])-mean(other,a=>a.result.ledger[j]);
 c.readiness_delta+=mean(inv,a=>a.result.readiness)-mean(other,a=>a.result.readiness);
 for(const a of inv)for(const b of other){
   c.pairs++;const d=flag(a.result,"h1_unique_truce")-flag(b.result,"h1_unique_truce"),e=flag(a.result,"h3_attainable")-flag(b.result,"h3_attainable");
   c.paired_truce_gains+=bit(d>0);c.paired_truce_losses+=bit(d<0);c.paired_h3_gains+=bit(e>0);c.paired_h3_losses+=bit(e<0);
   const z=flag(a.result,"noLedgerH1_unique_truce")-flag(b.result,"noLedgerH1_unique_truce");
   c.all_ledger_deleted_gain_pairs+=bit(z>0);c.all_ledger_deleted_loss_pairs+=bit(z<0);
   if(a.result.reached&&b.result.reached){c.goal_distance_pairs++;c.goal_distance_delta+=a.result.gateDistance-b.result.gateDistance;
     c.same_history_at_sirens+=bit(same(a.sirensHistory,b.sirensHistory));}
 }
}
function summarizeSite(o){
 const c=o.contrast;
 return {...o,contrast:{...c,mean_delta:Object.fromEntries(FLAGS.map(k=>[k,c.prefixes?c.totals[k]/c.prefixes:null])),
  mean_ledger_delta:c.ledger_delta.map(x=>c.prefixes?x/c.prefixes:null),mean_readiness_delta:c.prefixes?c.readiness_delta/c.prefixes:null,
  mean_goal_distance_delta_over_reached_pairs:c.goal_distance_pairs?c.goal_distance_delta/c.goal_distance_pairs:null},
  upstream_effect:{...o.upstream_effect,mean_goal_distance_range:o.upstream_effect.trials?o.upstream_effect.mean_goal_distance_range/o.upstream_effect.trials:null}};
}
export function evaluateWorld({api=runtime,source,cohort,worldLabel}){
 const w=api.compileV2(source),seqs=sequences(cohort),stats={nodes:0},sites=Object.fromEntries(CONTRACT.sites.map(p=>[p.label,initSite()]));
 const factual={campaigns:seqs.length,completed:0,secret:0,sirens:0,h1:0,h3:0,unique_truce:0,unique_truce_without_ledger:0};
 const rows=[],tasks=[],gold=[];let invariantChecks=0;
 for(let i=0;i<seqs.length;i++){
   const words=seqs[i],r=roll(api,w,api.initialV2(w),words,0,null,true),actual=outcome(api,w,r,stats);
   factual.completed+=bit(r.complete);factual.secret+=bit(r.end===G);factual.sirens+=bit(actual.reached);factual.h1+=bit(actual.h1.attainable);factual.h3+=bit(actual.h3.attainable);factual.unique_truce+=bit(actual.h1.unique_truce);factual.unique_truce_without_ledger+=bit(actual.noLedgerH1.unique_truce);
   for(const site of CONTRACT.sites){
     const p=r.prefixes[site.label];if(!p)continue;
     const o=sites[site.label],ob=api.observeV2(w,p.s),actualAction=selected(api,w,p.s,words[p.j]),arms=[];
     o.prefixes++;
     for(const a of ob.actions){
       const result=roll(api,w,p.s,words,p.j,a.id),x=outcome(api,w,result,stats),first=result.trace[0];
       arms.push({id:a.id,first,result:x,sirensHistory:result.firstSirens?result.firstSirens.seen:null});
       o.arms++;o.complete_arms+=bit(x.complete);o.reached_arms+=bit(x.reached);count(o.action_distribution,a.id);byAction(o,arms.at(-1));
     }
     const factualArm=arms.find(a=>a.id===actualAction);
     if(!factualArm||factualArm.result.ending!==actual.ending||factualArm.result.complete!==actual.complete||
       !same(factualArm.result.h1,actual.h1)||!same(factualArm.result.h3,actual.h3)||!same(factualArm.result.ledger,actual.ledger)||
       factualArm.result.steps!==r.trace.length-p.j)fail("factual suffix replay mismatch");
     o.factual_replay_checks++;invariantChecks++;
     for(const a of arms)if(a.id!==actualAction)recordSwap(o,a,factualArm);
     for(let a=0;a<arms.length;a++)for(let b=a+1;b<arms.length;b++){
       const x=arms[a].result,y=arms[b].result,z=o.exact_choice_pair;z.pairs++;
       z.h1_disagreement+=bit(x.h1.attainable!==y.h1.attainable);z.h3_disagreement+=bit(x.h3.attainable!==y.h3.attainable);
       z.unique_truce_disagreement+=bit(x.h1.unique_truce!==y.h1.unique_truce);z.random_goal_disagreement+=bit(x.random_goal!==y.random_goal);
     }
     const v=arms.map(a=>a.first.goal_progress),range=Math.max(...v)-Math.min(...v);
     const u=o.upstream_effect;u.trials++;u.mean_goal_distance_range+=range;u.max_goal_distance_range=Math.max(u.max_goal_distance_range,range);u.nonzero_goal_distance_range+=bit(range>1e-12);
     const e=arms.map(a=>a.first.energy),min=Math.min(...e);if(min>0)u.max_energy_ratio=Math.max(u.max_energy_ratio,Math.max(...e)/min);
     contrast(o,site,arms);
     o.paired_prefixes+=bit(arms.some(a=>site.investigation.includes(actionIndex(a.id)))&&arms.some(a=>!site.investigation.includes(actionIndex(a.id))));
     const winners=arms.filter(a=>a.result.h3.attainable).map(a=>a.id);
     // Diagnostic packet: deliberately expose the future policy words and
     // complete source-free prefix state only to the steward, not a model.
     // A future model task needs its own declared observation oracle.
     rows.push({trial:i,site:site.label,encounter:p.s.encounter,turn:p.s.turn,factual:actualAction,arms:arms.map(({sirensHistory,...a})=>a),h3_winners:winners});
   }
 }
 const result={world:worldLabel,cohort,factual,sites:Object.fromEntries(Object.entries(sites).map(([k,v])=>[k,summarizeSite(v)])),
  counts:{decision_prefixes:rows.length,arms:sum(rows,r=>r.arms.length),invariantChecks,reachability_nodes:stats.nodes}};
 return {result,rows};
}
