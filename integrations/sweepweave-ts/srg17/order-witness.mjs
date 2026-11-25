// SRG-17C: equal-prior, equal-multiset order-swap planning witnesses.
import {dp} from './planning.mjs';
const ck=(v,m)=>{if(!v)throw Error("SRG17C: "+m);};
export const OSEED=0x53521703;
function rng(seed){let x=seed>>>0||1;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};}
export function buildOrder(seed=OSEED,reps=8){
 ck(Number.isInteger(reps)&&reps>0&&reps<=64,"reps");
 const random=rng(seed),tasks=[],gold=[],pairs=[],used=new Set();
 const uid=()=>{let s;do{s="srg17o_"+random().toString(16).padStart(8,"0")+random().toString(16).padStart(8,"0");}while(used.has(s));used.add(s);return s;};
 for(const H of [4,8,16,32])for(const q8 of [5,7])for(const m of [8,16,32])for(let rep=0;rep<reps;rep++){
  const q=q8/8,l=1,h=2*m-l,w=m+Math.floor((h-m)/4);ck(m<w&&w<(m+h)/2,"strict threshold");
  const times=Array.from({length:H-1},(_,i)=>[random(),i+1]).sort((a,b)=>a[0]-b[0]).slice(0,2).map(x=>x[1]).sort((a,b)=>a-b);
  const y=random()&1,order=["dock0","dock1","audit"].map(a=>[random(),a]).sort((a,b)=>a[0]-b[0]).map(x=>x[1]),ids=[];
  for(const volatileFirst of [true,false]){
   const supports=Array.from({length:H-1},()=>[0,0]);
   supports[times[0]-1]=volatileFirst?[l,h]:[m,m];supports[times[1]-1]=volatileFirst?[m,m]:[l,h];
   const T=dp(supports,1,q),scores={audit:w+T[0][0],["dock"+y]:q*w+T[0][1],["dock"+(1-y)]:(1-q)*w+T[0][1]};
   const winners=order.filter(a=>scores[a]===Math.max(...Object.values(scores)));
   ck(winners.length===1&&winners[0]===(volatileFirst?"dock"+y:"audit"),"reversal");
   const expectedFutureBonus=(1-q)*(volatileFirst?(h+m)/2:m);
   ck(T[0][1]-T[0][0]===expectedFutureBonus,"closed form");
   const id=uid();ids.push(id);
   tasks.push({id,kind:"storyworld_policy",root_horizon:H,action_budget:H,
    goal:"Maximize expected total weighted cargo delivered correctly over the shift.",
    task:"The current stake is known. Each future slot has two equiprobable possible stakes (independent across slots); a zero slot has no reward and preserves the credit. Each active slot reveals its current stake and a predicted correct dock. That prediction is independently correct with probability q8/8. Correct routing earns the stake; incorrect routing earns zero. The single audit credit guarantees correct routing, and is consumed only when used on an active slot. Each action advances one slot. No outcome feedback before the end. Choose the current action assuming optimal permitted-information decisions thereafter.",
    rules:{q8,future_stake_supports:supports},observation:{encounter:"current",turn:0,status:"decision",values:{stake:w,predicted_dock:y,audit_credits:1},actions:order.map(a=>({id:a,text:a==="audit"?"Spend the audit credit":"Route to dock "+a.slice(-1)}))},output_contract:"Return one legal action ID."});
   gold.push({id,answer:winners[0],scores,full:w+2*m,H,q8,m,volatileFirst});
  }
  const [a,b]=gold.slice(-2);ck(a.full===b.full&&a.answer!==b.answer,"matched pair");
  const regret=Math.max(...Object.values(a.scores))+Math.max(...Object.values(b.scores))-Math.max(...order.map(x=>a.scores[x]+b.scores[x]));
  ck(regret>0,"order blind regret");
  pairs.push({ids,regret,full:a.full+b.full,H,q8,m});
 }
 // Mix rows so paired position and arm order cannot be used directly.
 const shuffled=tasks.map(t=>[random(),t]).sort((a,b)=>a[0]-b[0]).map(x=>x[1]);
 return {tasks:shuffled,gold,pairs};
}
export function scoreOrder(e,sub){
 const map=new Map(),dup=new Set(),ids=new Set(e.gold.map(g=>g.id));let malformed=0;
 for(const s of sub){if(!s||typeof s.id!=="string"){malformed++;continue;}if(map.has(s.id))dup.add(s.id);else map.set(s.id,s);}
 const valid=g=>{const s=map.get(g.id);return !!s&&!dup.has(g.id)&&Object.keys(s).sort().join(",")==="action,id"&&Object.hasOwn(g.scores,s.action);};
 const correct=new Set(e.gold.filter(g=>valid(g)&&map.get(g.id).action===g.answer).map(g=>g.id));
 const regret=e.gold.reduce((v,g)=>v+Math.max(...Object.values(g.scores))-(valid(g)?g.scores[map.get(g.id).action]:0),0);
 return {rows:e.gold.length,correct:correct.size,valid:e.gold.filter(valid).length,paired_correct:e.pairs.filter(p=>p.ids.every(id=>correct.has(id))).length,pairs:e.pairs.length,first_action_regret:regret,malformed,duplicates:dup.size,unknown:[...map.keys()].filter(k=>!ids.has(k)).length};
}
export function summarizeOrder(e){
 const perfect=scoreOrder(e,e.gold.map(g=>({id:g.id,action:g.answer})));
 const audit=scoreOrder(e,e.gold.map(g=>({id:g.id,action:"audit"})));
 const wait=scoreOrder(e,e.tasks.map(t=>({id:t.id,action:"dock"+t.observation.values.predicted_dock})));
 const lower=e.pairs.reduce((s,p)=>s+p.regret,0),full=e.pairs.reduce((s,p)=>s+p.full,0);
 ck(perfect.correct===e.gold.length&&perfect.paired_correct===e.pairs.length&&perfect.first_action_regret===0,"oracle");
 ck(audit.correct===e.pairs.length&&wait.correct===e.pairs.length&&audit.paired_correct===0&&wait.paired_correct===0,"order blind");
 const missing=scoreOrder(e,[]);ck(missing.correct===0&&missing.valid===0,"missing");
 return {pairs:e.pairs.length,rows:e.gold.length,order_blind_accuracy_bound:.5,order_blind_pair_accuracy_bound:0,order_blind_regret_lower_bound:lower,normalized_regret_lower_bound:lower/full,controls:{oracle:perfect,audit,wait}};
}
