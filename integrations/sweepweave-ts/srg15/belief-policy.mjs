// SRG-15B: exact empirical finite belief-state policy oracle on frozen SRG-13.
// All projections use only declared public coordinates and/or visible history.
// Full-state tree is verifier-only; continuation respects the same observation
// channel at every step, with perfect memory of projected observations.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
const G="page_secret_undercover_truce",F="page_sirens_at_the_rollup_door";
const LEDGER=["char_pink.Timeline_Record","char_pink.Radio_Record","char_pink.Review_Request"];
const GOALKEYS=["char_pink.Rat_Suspicion","char_blonde.Sadistic_Escalation","char_white.Crew_Loyalty"];
const fail=m=>{throw Error("SRG15B: "+m);},same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const sum=(a,f)=>a.reduce((n,x)=>n+f(x),0),own=(o,k)=>Object.hasOwn(o,k);
const best=s=>{const value=Math.max(...Object.values(s));return {value,winners:Object.keys(s).filter(k=>s[k]===value)};};
export const CONTRACT=Object.freeze({
 calibration:{seed:0x53521521,n:128},validation:{seed:0x53521522,n:128},prefix_budget:24,horizons:[1,3],
 modes:["menu","ledger","goal2","goal4","goal8","goal_exact","public2","public4","public_exact","public_history"],
 exported_mode:"goal4",exported_horizon:3,
 prior:"uniform unit mass over reached first-sirens campaign roots in each fixed cohort, multiplicities retained",
 semantics:"history-aware exact finite empirical belief oracle; grouped public projections at each continuation; separate full-state ceiling and calibration-fitted lookup on unseen cohort",
 disclaimer:"fixed public diagnostic, not a population optimum, private test, real model inference, or promotion of the frozen SRG13 candidate"
});
function seqs(c){let x=c.seed>>>0;const r=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};return Array.from({length:c.n},()=>Array.from({length:CONTRACT.prefix_budget},r));}
function group(a,f){const m=new Map();for(const x of a){const k=f(x);if(!m.has(k))m.set(k,[]);m.get(k).push(x);}return [...m.values()];}
const terminal=(w,s)=>Object.keys(w.pages[s.encounter].options).length===0;
function build(api,w,s,h,prefix,counts){
 const o=api.observeV2(w,s);counts.nodes++;
 const n={ob:o,prefix,terminal:o.status==="terminal",reward:o.status==="terminal"&&s.encounter===G?1:0,children:{},full:0};
 if(n.terminal){n.full=n.reward;return n;}
 if(h===0)return n;
 if(o.status!=="decision")fail("dead end");
 for(const a of o.actions){
   const b=api.stepV2(w,s,a.id);
   const nextPrefix=[...prefix,{encounter:o.encounter,action:a.id,reaction_text:b.text}];
   n.children[a.id]=build(api,w,b.next,h-1,nextPrefix,counts);
 }
 n.full=Math.max(...Object.values(n.children).map(x=>x.full));return n;
}
function roots(api,w,c){
 const out=[],counts={campaigns:c.n,roots:0,missed:0,nodes:0},paths=seqs(c);
 for(const words of paths){
   let s=api.initialV2(w),history=[];
   for(const word of words){
     if(s.encounter===F){out.push(build(api,w,s,3,history,counts));break;}
     const o=api.observeV2(w,s);if(o.status!=="decision")break;
     const a=o.actions[Math.floor(word*o.actions.length/4294967296)],b=api.stepV2(w,s,a.id);
     history.push({encounter:o.encounter,action:a.id,reaction_text:b.text});s=b.next;
   }
 }
 counts.roots=out.length;counts.missed=c.n-out.length;
 if(!out.length)fail("no first sirens roots");return {roots:out,counts};
}
function quant(x,b){const n=2**b;return Math.min(n-1,Math.floor((x+1)*n/2));}
function projection(n,mode){
 const o=n.ob,v=o.values,values={};
 const get=k=>{if(!own(v,k))fail("projection uses nonpublic "+k);return v[k];};
 if(mode!=="menu")for(const k of LEDGER)values[k]=get(k);
 if(mode.startsWith("goal")||mode.startsWith("public")){
   const bits=mode.endsWith("exact")||mode==="public_history"?null:Number(mode.match(/\d+$/)?.[0]);
   if(bits!==null&&!Number.isInteger(bits))fail("precision");
   const keys=mode.startsWith("goal")?GOALKEYS:Object.keys(v).filter(k=>!LEDGER.includes(k)).sort();
   for(const k of keys)values[k]=bits===null?get(k):quant(get(k),bits);
 }
 const ob={world_id:o.world_id,encounter:o.encounter,turn:o.turn,title:o.title,text:o.text,status:o.status,actions:o.actions,values};
 return mode==="public_history"?{...ob,prefix:n.prefix}:ob;
}
function full(n,h){
 if(n.terminal)return n.reward;if(!h)return 0;
 return Math.max(...Object.values(n.children).map(c=>full(c,h-1)));
}
function oracle(roots,mode,h,{makeTasks=false}={}){
 let nodes=0,serial=0,privileged=0;
 const policy=new Map(),tasks=[],gold=[],keyFor=(remaining,hist)=>JSON.stringify([remaining,hist]);
 function solve(rs,remaining,hist){
   nodes++;
   if(rs.every(x=>x.terminal))return sum(rs,x=>x.reward);
   if(!remaining)return sum(rs,x=>x.terminal?x.reward:0);
   if(rs.some(x=>x.terminal))fail("mixed terminal cell");
   const ids=Object.keys(rs[0].children);
   if(!ids.length||rs.some(x=>!same(Object.keys(x.children),ids)))fail("unequal observed menus");
   const scores={};
   for(const a of ids){
     const next=rs.map(x=>x.children[a]),parts=group(next,n=>JSON.stringify(projection(n,mode)));
     scores[a]=sum(parts,g=>solve(g,remaining-1,[...hist,{action:a,observation:projection(g[0],mode)}]));
   }
   const b=best(scores),key=keyFor(remaining,hist);
   if(policy.has(key))fail("duplicate policy cell");
   policy.set(key,{action:b.winners[0],winners:b.winners,mass:rs.length,scores});
   if(makeTasks){
     const id="srg15_"+mode+"_h"+h+"_cell"+(++serial),ob=projection(rs[0],mode);
     tasks.push({id,kind:"storyworld_policy",action_budget:remaining,root_horizon:h,observation:ob,history:hist.slice(0,-1),
       goal:"Reach page_secret_undercover_truce within the remaining action budget. Other endings or unfinished paths pay zero. Choose a legal action using only this observation channel and its observed history.",
       observation_contract:mode==="goal4"?"Public investigation records are exact; the three goal coordinates are dyadic bin indices 0..15 for equal-width intervals on [-1,1]. No other numeric coordinates are shown. Earlier projected observations and chosen actions remain available.":"Declared public observation projection.",
       output_contract:"Return one legal action ID."});
     gold.push({id,key,mass:rs.length,winners:b.winners,scores});
   }
   return b.value;
 }
 const parts=group(roots,n=>JSON.stringify(projection(n,mode)));
 const numerator=sum(parts,g=>solve(g,h,[{observation:projection(g[0],mode)}]));
 const fullValue=sum(roots,n=>full(n,h));
 for(const g of parts){
   const ids=Object.keys(g[0].children),scores=ids.map(a=>sum(g,n=>full(n.children[a],h-1)));
   privileged+=Math.max(...scores);
 }
 if(numerator>privileged||privileged>fullValue)fail("observation ceiling");
 return {mode,h,numerator,denominator:roots.length,full:fullValue,privileged,root_cells:parts.length,policy_cells:policy.size,nodes,policy,tasks,gold};
}
function deploy(roots,mode,h,policy,menuFallback){
 const o={successes:0,roots:roots.length,decisions:0,unseen:0,menu_fallback:0,first_action_fallback:0,root_unseen:0,root_hits:0};
 for(const root of roots){
   let n=root,hist=[{observation:projection(root,mode)}],menuHist=[{observation:projection(root,"menu")}];
   for(let left=h;left>0&&!n.terminal;left--){
     const ids=Object.keys(n.children),entry=policy.get(JSON.stringify([left,hist]));
     let a=entry?.action;
     o.decisions++;
     if(left===h){o.root_unseen+=Number(!entry);o.root_hits+=Number(!!entry);}
     if(!a){
       o.unseen++;a=menuFallback?.get(JSON.stringify([left,menuHist]))?.action;
       if(a)o.menu_fallback++;else{a=ids[0];o.first_action_fallback++;}
     }
     if(!ids.includes(a))fail("policy action unavailable");
     n=n.children[a];hist.push({action:a,observation:projection(n,mode)});menuHist.push({action:a,observation:projection(n,"menu")});
   }
   o.successes+=n.terminal?n.reward:0;
 }
 return o;
}
function compact(o){const {policy,tasks,gold,...r}=o;return r;}
export function analyze({api=runtime,source,exportTasks=true}){
 const w=api.compileV2(source),cal=roots(api,w,CONTRACT.calibration),val=roots(api,w,CONTRACT.validation),results=[];
 let exported=null;
 for(const h of CONTRACT.horizons){
   const trainMenu=oracle(cal.roots,"menu",h);
   for(const mode of CONTRACT.modes){
     const tr=mode==="menu"?trainMenu:oracle(cal.roots,mode,h),te=oracle(val.roots,mode,h,{makeTasks:exportTasks&&mode===CONTRACT.exported_mode&&h===CONTRACT.exported_horizon});
     const check=deploy(val.roots,mode,h,te.policy,null);
     if(check.successes!==te.numerator||check.unseen)fail("optimal observation policy replay");
     const transfer=deploy(val.roots,mode,h,tr.policy,trainMenu.policy);
     if(transfer.successes>te.numerator)fail("transfer exceeds empirical optimum");
     if(te.tasks.length){exported={tasks:te.tasks,gold:te.gold,roots:val.roots,mode,h};}
     results.push({mode,h,calibration:compact(tr),validation:compact(te),transfer,oracle_replay:check});
   }
   const rows=results.filter(x=>x.h===h);
   for(const dataset of ["calibration","validation"]){
     const find=m=>rows.find(r=>r.mode===m)[dataset].numerator;
     for(const chain of [["menu","ledger","goal2","goal4","goal8","goal_exact","public_exact","public_history"],["ledger","goal2","public2","public4","public_exact"]]){
       for(let i=1;i<chain.length;i++)if(find(chain[i])<find(chain[i-1]))fail("nested channel monotonicity "+dataset+" "+chain[i]);
     }
   }
 }
 return {receipt:{evidence:"exact finite empirical observation-policy oracle and frozen calibration transfer; no model calls",contract:CONTRACT,calibration:cal.counts,validation:val.counts,results},exported};
}
export function scorePolicy(exported,submissions){
 const {tasks,gold,roots,mode,h}=exported,entries=new Map(),dup=new Set(),expected=new Set(tasks.map(x=>x.id)),policy=new Map(),counts={};
 for(const r of submissions){if(!r||typeof r.id!=="string")fail("submission ID");if(entries.has(r.id))dup.add(r.id);else entries.set(r.id,r);}
 const labels=new Map(gold.map(x=>[x.id,x]));
 let correct=0,firstActionRegret=0,policyRows=0;
 for(const t of tasks){
   const g=labels.get(t.id),r=entries.get(t.id);if(!g)fail("missing label");
   let status="missing";
   if(dup.has(t.id))status="duplicate";
   else if(r){
     if(Object.keys(r).sort().join(",")!=="action,id"||typeof r.action!=="string"||!own(g.scores,r.action))status="rejected";
     else{status=g.winners.includes(r.action)?"pass":"fail";policy.set(g.key,{action:r.action});policyRows++;}
   }
   const optimum=Math.max(...Object.values(g.scores));firstActionRegret+=optimum-(policy.has(g.key)?g.scores[policy.get(g.key).action]:0);
   correct+=Number(status==="pass");counts[status]=(counts[status]??0)+1;
 }
 // Missing or rejected action stops the actual rollout, with zero utility.
 let successes=0,decisions=0,stopped=0;
 for(const root of roots){
   let n=root,hist=[{observation:projection(root,mode)}],valid=true;
   for(let left=h;left>0&&!n.terminal;left--){
     const a=policy.get(JSON.stringify([left,hist]))?.action;decisions++;
     if(!a||!own(n.children,a)){valid=false;stopped++;break;}
     n=n.children[a];hist.push({action:a,observation:projection(n,mode)});
   }
   successes+=valid&&n.terminal?n.reward:0;
 }
 return {rows:tasks.length,counts,correct,first_action_regret_mass:firstActionRegret,policy_rows:policyRows,actual_rollout:{successes,roots:roots.length,decisions,stopped},unknown_ids:[...entries.keys()].filter(x=>!expected.has(x))};
}
