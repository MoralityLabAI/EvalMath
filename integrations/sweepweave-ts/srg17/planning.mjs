// SRG-17A: public-prior resource planning with matched K and interaction width.
const ck=(v,m)=>{if(!v)throw Error("SRG17: "+m);};
export const SEED=0x53521701,REPS=8;
const Hs=[8,16,32],ds=[1,4,8],qs=[5,7,8],Js=[1,8,32],Ks=[8,32,128,1024];
const modes=["oracle","greedy","premium","commit","first","wrong"],acts=["dock0","dock1","audit"];
const parity=a=>a.reduce((x,y)=>x^y,0),id=(i,a)=>"s"+i+"_"+a;
function rng(seed){let x=seed>>>0||1;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};}
export function configs(pilot=false){
 const out=[];
 for(const H of Hs)for(const d of ds)for(const q8 of qs)for(const J of Js)for(const K of Ks)for(const profile of ["rising","falling"]){
  if(J>K)continue;
  if(pilot&&[H!==16,d!==4,q8!==5,J!==8,K!==32].filter(Boolean).length>1&&!(H===8&&d===8&&q8===5&&J===8&&K===32)&&!(H===32&&d===1&&q8===5&&J===8&&K===32))continue;
  const n=H*d/8;out.push({H,d,q8,J,K,profile,n,B:Math.max(1,Math.floor(n/4))});
 }
 return out;
}
export function tape(seed,rep){
 const r=rng(seed^Math.imul(rep+1,0x9e3779b9));
 return Array.from({length:32},()=>({priority:r(),w:r()&1,error:r()&7,signal:Array.from({length:32},()=>r()&1),pad:Array.from({length:1024},()=>r()&1),order:acts.map(a=>[r(),a]).sort((a,b)=>a[0]-b[0]).map(x=>x[1])}));
}
export function dp(supports,B,q,mode="oracle"){
 const T=Array.from({length:supports.length+1},()=>Array(B+1).fill(0));
 for(let i=supports.length-1;i>=0;i--)for(let b=0;b<=B;b++){
  const f=T[i+1][b],g=b?T[i+1][b-1]:0;
  T[i][b]=supports[i].reduce((sum,w)=>sum+(w===0?f:!b||mode==="commit"?q*w+f:mode==="greedy"?(q===1?q*w+f:w+g):Math.max(q*w+f,w+g)),0)/2;
 }
 return T;
}
export function root(c,t){
 const active=new Set(t.slice(0,c.H).map((x,i)=>({i,r:x.priority})).sort((a,b)=>a.r-b.r).slice(0,c.n).map(x=>x.i));
 const ix=Array.from({length:c.J},(_,j)=>Math.floor((j+.5)*c.K/c.J));ck(new Set(ix).size===c.J,"indices");
 let rank=0;
 const slots=t.slice(0,c.H).map((x,i)=>{
  const on=active.has(i),low=on&&(c.profile==="rising"?rank<Math.floor(c.n/2):rank>=Math.ceil(c.n/2));
  const support=on?(low?[1,3]:[1,15]):[0,0];if(on)rank++;
  const y=parity(x.signal.slice(0,c.J));return {on,support,w:support[x.w],y,target:y^Number(x.error>=c.q8),signal:x.signal,pad:x.pad,order:x.order};
 });
 ck(rank===c.n,"active count");
 const supports=slots.map(s=>s.support),q=c.q8/8;
 return {c,slots,supports,ix,q,T:dp(supports,c.B,q)};
}
function row(r,i,b){
 const s=r.slots[i],f=r.T[i+1][b],g=b?r.T[i+1][b-1]:0,legal=s.order.filter(a=>a!=="audit"||b),scores={};
 for(const a of legal)scores[a]=!s.on?f:a==="audit"?s.w+g:(Number(a.slice(-1))===s.y?r.q:1-r.q)*s.w+f;
 const hi=Math.max(...Object.values(scores)),lo=Math.min(...Object.values(scores));
 ck((hi>lo)===s.on,"opportunity");return {legal,scores,hi,lo,winners:legal.filter(a=>scores[a]===hi)};
}
function states(r,i){return Array.from({length:Math.min(r.c.B,r.slots.slice(0,i).filter(s=>s.on).length)+1},(_,j)=>r.c.B-j);}
function choice(r,i,b,m,z){
 const s=r.slots[i],a="dock"+s.y;
 if(m==="oracle")return z.winners[0];if(m==="first")return z.legal[0];if(m==="commit")return a;if(m==="wrong")return "dock"+(1-s.y);
 if(m==="greedy")return s.on&&b&&r.q<1?"audit":a;
 if(m==="premium")return s.on&&b&&r.q<1&&s.w===15?"audit":a;
 throw Error("control");
}
const empty=()=>({roots:0,slots:0,opportunities:0,rows:0,informative:0,correct:0,informative_correct:0,regret:0,range:0,earned:0,conditional:0,possible:0,perfect:0,stopped:0,prior_full:0,prior_oracle:0,prior_greedy:0});
function add(a,b){for(const k of Object.keys(a))a[k]+=b[k];}
function finish(a){return {...a,raw_accuracy:a.correct/a.rows,informative_accuracy:a.informative_correct/a.informative,utility:a.earned/a.possible,conditional_utility:a.conditional/a.possible,local_regret:a.regret/a.range,prior_oracle_fraction:a.prior_oracle/a.prior_full,prior_greedy_fraction:a.prior_greedy/a.prior_full};}
function metric(r,pick){
 const {c,slots}=r,a=empty();a.roots=1;a.slots=c.H;a.opportunities=c.n;
 a.possible=slots.reduce((s,x)=>s+x.w,0);a.prior_full=slots.reduce((s,x)=>s+(x.support[0]+x.support[1])/2,0);
 a.prior_oracle=r.T[0][c.B];a.prior_greedy=dp(r.supports,c.B,r.q,"greedy")[0][c.B];
 for(let i=0;i<c.H;i++)for(const b of states(r,i)){
  const z=row(r,i,b),x=pick(i,b,z),ok=z.winners.includes(x),inf=z.hi>z.lo;
  a.rows++;a.informative+=Number(inf);a.correct+=Number(ok);a.informative_correct+=Number(ok&&inf);
  a.range+=z.hi-z.lo;a.regret+=Object.hasOwn(z.scores,x)?z.hi-z.scores[x]:z.hi-z.lo;
 }
 let b=c.B;
 for(let i=0;i<c.H;i++){
  const z=row(r,i,b),x=pick(i,b,z),s=slots[i];if(!z.legal.includes(x)){a.stopped=1;break;}
  if(!s.on)continue;
  b-=Number(x==="audit");
  a.earned+=(x==="audit"||Number(x.slice(-1))===s.target)?s.w:0;
  a.conditional+=(x==="audit"?1:Number(x.slice(-1))===s.y?r.q:1-r.q)*s.w;
 }
 a.perfect=Number(!a.stopped&&a.earned===a.possible);return a;
}
export function analyze(seed=SEED,reps=REPS){
 const cs=configs(),ts=Array.from({length:reps},(_,i)=>tape(seed,i)),total=Object.fromEntries(modes.map(m=>[m,empty()])),groups=[],matched=new Map();let pairs=0;
 for(const c of cs){
  const g=Object.fromEntries(modes.map(m=>[m,empty()]));
  for(let rep=0;rep<reps;rep++){
   const r=root(c,ts[rep]),sig=JSON.stringify([r.slots.map(s=>[s.on,s.support,s.w,s.order]),r.T]),k=[c.H,c.d,c.q8,c.profile,rep].join("/");
   if(matched.has(k)){ck(matched.get(k)===sig,"matched prior");pairs++;}else matched.set(k,sig);
   for(const m of modes){const v=metric(r,(i,b,z)=>choice(r,i,b,m,z));add(g[m],v);add(total[m],v);}
  }
  groups.push({config:c,controls:g});
 }
 const o=total.oracle,w=total.wrong;ck(o.correct===o.rows&&o.regret===0&&w.informative_correct===0&&o.prior_oracle>=o.prior_greedy,"controls");
 return {seed,reps,conditions:cs.length,matched_comparisons:pairs,total:Object.fromEntries(modes.map(m=>[m,finish(total[m])])),groups};
}
function packet(r,i,b,key){
 const s=r.slots[i],z=row(r,i,b),bits=s.pad.slice(0,r.c.K);r.ix.forEach((k,j)=>bits[k]=s.signal[j]);ck(parity(r.ix.map(k=>bits[k]))===s.y,"padding");
 return {id:key,kind:"storyworld_policy",root_horizon:r.c.H,action_budget:r.c.H-i,
 goal:"Maximize expected total weighted cargo delivered correctly by the end of the shift.",
 task:"Each remaining slot has the public stake distribution shown below (two equiprobable values, independent across slots). A neutral slot has stake 0; all actions there yield zero and preserve audit credits. Current stake is observed. The observed signal is a bit string, indexed from zero. XOR the bits at the listed causal indices to predict dock 0 or 1. Conditional on this parity, the correct dock equals that prediction with probability q8/8; otherwise it is opposite. Errors and future signals/stakes are independent. Correct routing yields the stake, wrong routing zero. Audit guarantees correct delivery and spends one credit on an active slot; no audit is legal with zero credits. No outcome feedback before the end. Each action advances one slot. Remaining stake distributions are public; future draws are hidden.",
 rules:{q8:r.c.q8,K:r.c.K,causal_indices:r.ix,remaining_stake_supports:r.supports.slice(i)},
 observation:{encounter:"slot_"+i,turn:i,status:"decision",values:{signal:bits.join(""),stake:s.w,audit_credits:b},actions:z.legal.map(a=>({id:id(i,a),text:a==="audit"?"Spend an audit credit":a==="dock0"?"Route to dock 0":"Route to dock 1"}))},output_contract:"Return one legal action ID."};
}
const key=(ci,rep,i,b)=>"srg17p_"+ci+"_"+rep+"_"+i+"_"+b;
export function corpus(seed=SEED,reps=1,pilot=true){
 ck(Number.isInteger(seed)&&seed>0&&seed<=0xffffffff&&Number.isInteger(reps)&&reps>=1&&reps<=8,"corpus args");
 const cs=configs(pilot),ts=Array.from({length:reps},(_,i)=>tape(seed,i)),roots=[],tasks=[],gold=[];
 for(const [ci,c] of cs.entries())for(let rep=0;rep<reps;rep++){
  const r=root(c,ts[rep]);roots.push({r,ci,rep});
  for(let i=0;i<c.H;i++)for(const b of states(r,i)){
   const k=key(ci,rep,i,b),z=row(r,i,b);tasks.push(packet(r,i,b,k));
   gold.push({id:k,winners:z.winners.map(a=>id(i,a)),scores:Object.fromEntries(z.legal.map(a=>[id(i,a),z.scores[a]])),informative:z.hi>z.lo});
  }
 }
 return {roots,tasks,gold};
}
export function score(e,sub){
 const map=new Map(),dups=new Set(),ids=new Set(e.tasks.map(t=>t.id));let malformed=0,valid=0;
 for(const s of sub){if(!s||typeof s.id!=="string"){malformed++;continue;}if(map.has(s.id))dups.add(s.id);else map.set(s.id,s);}
 const total=empty(),groups=new Map();
 for(const {r,ci,rep} of e.roots){
  const chosen=new Map();
  for(let i=0;i<r.c.H;i++)for(const b of states(r,i)){
   const k=key(ci,rep,i,b),s=map.get(k),z=row(r,i,b);
   if(s&&!dups.has(k)&&Object.keys(s).sort().join(",")==="action,id"&&typeof s.action==="string"&&z.legal.some(a=>id(i,a)===s.action)){chosen.set(i+":"+b,s.action.slice(s.action.indexOf("_")+1));valid++;}
  }
  const a=metric(r,(i,b)=>chosen.get(i+":"+b)),g=groups.get(ci)??{config:r.c,metrics:empty()};add(total,a);add(g.metrics,a);groups.set(ci,g);
 }
 return {total:finish(total),groups:[...groups.values()].map(g=>({config:g.config,...finish(g.metrics)})),submission:{valid,malformed,duplicates:dups.size,unknown:[...map.keys()].filter(k=>!ids.has(k)).length,missing_or_invalid:e.tasks.length-valid}};
}
function brute(s,B,q8,i=0){
 if(i===s.length)return 0;
 let v=0;
 for(const w of s[i])for(const y of [0,1]){
  const vals=(B?acts:acts.slice(0,2)).map(a=>{
   let pay=0;for(let e=0;e<8;e++)pay+=(a==="audit"||Number(a.slice(-1))===(y^Number(e>=q8)))?w:0;
   return pay/8+brute(s,B-Number(w>0&&a==="audit"),q8,i+1);
  });v+=Math.max(...vals);
 }
 return v/4;
}
export function verify(){
 let bruteChecks=0,paddingChecks=0,horizonChecks=0;
 for(const s of [[[1,3]],[[1,3],[1,15]],[[0,0],[1,15],[1,3]],[[1,3],[1,15],[1,15],[0,0]]])for(const q8 of qs)for(const b of [0,1,2]){
  ck(brute(s,b,q8)===dp(s,b,q8/8)[0][b],"brute oracle");bruteChecks++;
 }
 const t=tape(SEED,0);
 for(const c of configs()){
  const r=root(c,t);
  for(let i=0;i<c.H;i++){const p=packet(r,i,c.B,"test");ck(p.observation.values.signal.length===c.K,"padding length");paddingChecks++;}
  ck(dp(r.slots.filter(s=>s.on).map(s=>s.support),c.B,r.q)[0][c.B]===r.T[0][c.B],"neutral spacing");horizonChecks++;
 }
 const e=corpus(),o=score(e,e.gold.map(g=>({id:g.id,action:g.winners[0]}))),m=score(e,[]);
 ck(o.total.correct===e.tasks.length&&o.total.stopped===0&&o.total.regret===0&&o.submission.valid===e.tasks.length,"oracle replay");
 ck(m.total.correct===0&&m.total.earned===0&&m.total.stopped===e.roots.length,"missing");
 const bad=score(e,[{id:e.tasks[0].id,action:e.gold[0].winners[0]},{id:e.tasks[0].id,action:e.gold[0].winners[0]},null,{id:"unknown",action:"x"},{id:e.tasks[1].id,action:"bad"}]);
 ck(bad.submission.valid===0&&bad.submission.duplicates===1&&bad.submission.malformed===1&&bad.submission.unknown===1,"malformed");
 return {bruteChecks,paddingChecks,horizonChecks,pilot_roots:e.roots.length,pilot_rows:e.tasks.length,scoring:"pass"};
}
