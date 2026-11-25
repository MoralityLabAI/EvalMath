// SRG-16 synthetic, fully specified finite-prior planning diagnostic.
const check=(v,m)=>{if(!v)throw Error("SRG16: "+m);};
export const DEFAULT_SEED=0x53521601, DEFAULT_REPS=32;
export const GRID=Object.freeze({H:[4,8],density:[1,2,4],q8:[5,7,8],J:[1,5],K:[8,32]});
const kinds=["commit0","commit1","audit"];
const parity=xs=>xs.reduce((a,b)=>a^b,0);
const id=(i,a)=>"s"+i+"_"+a;
function rng(seed){
 let x=seed>>>0;check(x!==0,"zero seed");
 return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};
}
const mean=xs=>xs.reduce((a,b)=>a+b,0)/xs.length;
export function configs(){
 const out=[];
 for(const H of GRID.H)for(const density of GRID.density)for(const q8 of GRID.q8)for(const J of GRID.J)for(const K of GRID.K)
 out.push({H,density,q8,J,K,n:H*density/4});
 return out;
}
function root(c,seed,rep){
 // Same random tape across all factors for each replicate: nuisance padding,
 // difficulty and precision do not change the schedule or stakes.
 const rand=rng((seed^Math.imul(rep+1,0x9e3779b9))>>>0||1);
 const tape=Array.from({length:8},()=>({
  priority:rand(),weight:1+2*(rand()&1),noise:rand()&7,
  bits:Array.from({length:32},()=>rand()&1),
  order:kinds.map(a=>({a,r:rand()})).sort((a,b)=>a.r-b.r).map(x=>x.a)
 }));
 const active=new Set(tape.slice(0,c.H).map((t,i)=>({i,r:t.priority})).sort((a,b)=>a.r-b.r).slice(0,c.n).map(t=>t.i));
 const slots=tape.slice(0,c.H).map((t,i)=>{
  const y=t.bits.slice(0,c.K),x=y.slice(0,c.J);x[0]^=Number(t.noise>=c.q8);
  return {active:active.has(i),weight:active.has(i)?t.weight:0,y,x,target:parity(x),order:t.order};
 });
 return {c,rep,slots,rows:new Map()};
}
// Every quantity is dyadic; IEEE doubles are exact at these small horizons.
export function value(n,b,q8){
 check(Number.isInteger(n)&&n>=0&&n<=8&&(b===0||b===1)&&[5,7,8].includes(q8),"value args");
 const q=q8/8,table=[[0,0]];
 for(let m=1;m<=n;m++){
  const [v0,v1]=table[m-1];
  table.push([2*q+v0,mean([1,3].map(w=>Math.max(q*w+v1,w+v0)))]);
 }
 return table[n][b];
}
function scores(r,i,b){
 const {c,slots}=r,t=slots[i],n=slots.slice(i+1).filter(s=>s.active).length,q=c.q8/8;
 const out={};
 for(const a of t.order){
  if(a==="audit"&&!b)continue;
  const v=value(n,b,c.q8);
  out[id(i,a)]=!t.active?v:a==="audit"?t.weight+value(n,b-1,c.q8):
   v+t.weight*(Number(a.slice(-1))===parity(t.y.slice(0,c.J))?q:1-q);
 }
 return out;
}
function packet(r,i,b,key){
 const {c,slots}=r,t=slots[i],names={commit0:"Route to dock 0",commit1:"Route to dock 1",audit:"Delegate to the trusted technician"};
 return {id:key,kind:"storyworld_policy",action_budget:c.H-i,root_horizon:c.H,
  goal:"Maximize the expected total number of weighted cargo units correctly routed by the end of the shift.",
  task:"The schedule is public. Each active slot has K observed independent fair bits; only the first J matter. The true first bit equals its observed bit with probability q8/8, otherwise it is flipped. The next J-1 true bits equal the observed bits. The correct dock is XOR (parity) of the J true bits. All slot bits, first-bit errors and stakes are independent across slots. Active future stakes are independently 1 or 3 with equal probability; the current stake is shown. Correct routing earns the stake, incorrect routing earns zero. One audit credit is available per shift: delegating in an active slot guarantees correct routing and spends it; delegating is unavailable when no credit remains. At a neutral slot every legal action earns zero and leaves the credit intact. Every action advances one slot. No score or true bits are revealed before the shift ends. Optimize the entire remaining shift.",
  rules:{H:c.H,K:c.K,J:c.J,q8:c.q8,future_active_stake_distribution:[1,3],schedule:slots.map(s=>s.active?1:0)},
  observation:{encounter:"slot_"+i,turn:i,status:"decision",values:{observed_bits:t.y,active:Number(t.active),stake:t.weight,audit_credit:b},
   actions:t.order.filter(a=>a!=="audit"||b).map(a=>({id:id(i,a),text:names[a]}))},
  output_contract:"Return one legal action ID."};
}
export function build(seed=DEFAULT_SEED,reps=DEFAULT_REPS){
 check(Number.isSafeInteger(seed)&&seed>0&&seed<=0xffffffff&&Number.isSafeInteger(reps)&&reps>=1&&reps<=256,"seed/reps");
 const roots=[],tasks=[],gold=[];
 let serial=0;
 for(const c of configs())for(let rep=0;rep<reps;rep++){
  const r=root(c,seed,rep);roots.push(r);
  for(let i=0;i<c.H;i++){
   const bs=r.slots.slice(0,i).some(s=>s.active)?[1,0]:[1];
   for(const b of bs){
    const key="srg16_"+(++serial).toString(36).padStart(6,"0"),t=packet(r,i,b,key),s=scores(r,i,b);
    const hi=Math.max(...Object.values(s)),lo=Math.min(...Object.values(s));
    const g={id:key,scores:s,winners:Object.keys(s).filter(a=>s[a]===hi),informative:hi>lo,range:hi-lo};
    check(g.informative===r.slots[i].active,"unexpected tie structure");
    tasks.push(t);gold.push(g);r.rows.set(i+":"+b,{t,g});
   }
  }
 }
 return {seed,reps,roots,tasks,gold};
}
export function controls(e,name){
 return e.roots.flatMap(r=>[...r.rows.values()].map(({t,g})=>{
  const i=t.observation.turn,{active,observed_bits,stake,audit_credit}=t.observation.values;
  const a=id(i,"commit"+parity(observed_bits.slice(0,r.c.J)));
  const bad=id(i,"commit"+(1-parity(observed_bits.slice(0,r.c.J))));
  const action=name==="oracle"?g.winners[0]:name==="first"?t.observation.actions[0].id:
   name==="commit"?a:name==="wrong"?bad:name==="greedy"?(active&&audit_credit&&r.c.q8<8?id(i,"audit"):a):null;
  check(action,"unknown control");
  return {id:t.id,action};
 }));
}
export function apply(r,i,b,action){
 const t=r.slots[i],a=action.slice(action.indexOf("_")+1);
 check(action===id(i,a)&&kinds.includes(a)&&(a!=="audit"||b),"illegal transition");
 if(!t.active)return {b,earned:0};
 return {b:b-Number(a==="audit"),earned:(a==="audit"||Number(a.slice(-1))===t.target)?t.weight:0};
}
export function rollout(r,policy){
 let b=1,earned=0,stopped=false,missed=0,audits=0;
 for(let i=0;i<r.c.H;i++){
  const row=r.rows.get(i+":"+b),a=policy.get(row.t.id);
  if(!a){stopped=true;break;}
  const next=apply(r,i,b,a);earned+=next.earned;audits+=b-next.b;
  missed+=Number(r.slots[i].active&&next.earned===0);b=next.b;
 }
 const possible=r.slots.reduce((s,t)=>s+t.weight,0);
 return {earned,possible,stopped,success:!stopped&&earned===possible,audits,missed};
}
const empty=()=>({roots:0,slots:0,opportunities:0,rows:0,informative_rows:0,correct:0,informative_correct:0,valid:0,range:0,regret:0,earned:0,possible:0,successes:0,stopped:0,audits:0,oracle_expected:0,full_expected:0});
export function score(e,submissions){
 check(Array.isArray(submissions),"submissions");
 const seen=new Map(),dups=new Set(),expected=new Set(e.tasks.map(t=>t.id)),policy=new Map();
 let malformed=0;
 for(const s of submissions){
  if(!s||typeof s.id!=="string"){malformed++;continue;}
  if(seen.has(s.id))dups.add(s.id);else seen.set(s.id,s);
 }
 for(const g of e.gold){
  const s=seen.get(g.id);
  if(s&&!dups.has(g.id)&&Object.keys(s).sort().join(",")==="action,id"&&typeof s.action==="string"&&Object.hasOwn(g.scores,s.action))policy.set(g.id,s.action);
 }
 const total=empty(),groups=new Map();
 for(const r of e.roots){
  const key=JSON.stringify(r.c),agg=groups.get(key)??empty();groups.set(key,agg);
  const run=rollout(r,policy),{c}=r;
  for(const a of [agg,total]){
   a.roots++;a.slots+=c.H;a.opportunities+=c.n;
   a.earned+=run.earned;a.possible+=run.possible;a.successes+=Number(run.success);a.stopped+=Number(run.stopped);a.audits+=run.audits;
   a.oracle_expected+=value(c.n,1,c.q8);a.full_expected+=2*c.n;
   for(const {g} of r.rows.values()){
    const act=policy.get(g.id),ok=!!act&&g.winners.includes(act);
    a.rows++;a.informative_rows+=Number(g.informative);a.correct+=Number(ok);a.informative_correct+=Number(ok&&g.informative);a.valid+=Number(!!act);
    a.range+=g.range;a.regret+=act?Math.max(...Object.values(g.scores))-g.scores[act]:g.range;
   }
  }
 }
 const finish=a=>({...a,raw_accuracy:a.correct/a.rows,informative_accuracy:a.informative_correct/a.informative_rows,
  realized_utility:a.earned/a.possible,structural_density:a.opportunities/a.slots,enumerated_density:a.informative_rows/a.rows,
  normalized_local_regret:a.range?a.regret/a.range:null,all_success_rate:a.successes/a.roots,
  prior_oracle_fraction:a.oracle_expected/a.full_expected});
 return {total:finish(total),groups:[...groups].map(([k,v])=>({config:JSON.parse(k),...finish(v)})),
  submission:{malformed,duplicates:[...dups].length,unknown_ids:[...seen.keys()].filter(k=>!expected.has(k)).length,missing_or_invalid:e.tasks.length-policy.size}};
}
// Independently enumerate future stake histories, current observed parity
// (0/1 equiprobable) and error states (eight equally likely words).
export function brute(n,b,q8){
 if(!n)return 0;
 let mass=0;
 for(const w of [1,3])for(const y of [0,1]){
  const vals=[];
  for(const a of (b?kinds:kinds.slice(0,2))){
   let immediate=0;
   for(let err=0;err<8;err++){
    const target=y^Number(err>=q8);
    immediate+=(a==="audit"||Number(a.slice(-1))===target)?w:0;
   }
   vals.push(immediate/8+brute(n-1,b-Number(a==="audit"),q8));
  }
  mass+=Math.max(...vals);
 }
 return mass/4;
}
// A private per-root SWMD-SRG/2 replay fixture; never pass source to the
// model. Only its declared public projection and the public prior are used.
export function swmd(r){
 const {c,slots}=r,p=i=>"page_"+i,lines=["# SWMD-SRG/2","id: SRG16-docks","title: \"The dock shift\"","about: \"Route cargo under a limited audit budget.\"","start: "+p(0),"turn-base: 0","tie: first","direct: strict"];
 const add=(k,v,vis)=>lines.push("VAR "+k+" = "+v+" | "+vis);
 add("shift.credit",1,"public");add("shift.earned",0,"hidden");
 add("shift.active",Number(slots[0].active),"public");add("shift.stake",slots[0].weight/4,"public");
 for(let j=0;j<c.K;j++)add("signal.bit"+j,1-2*slots[0].y[j],"public");
 for(let i=0;i<c.H;i++){
  add("future.active"+i,Number(slots[i].active),"hidden");add("future.stake"+i,slots[i].weight/4,"hidden");
  for(let j=0;j<c.K;j++)add("future.y"+i+"_"+j,1-2*slots[i].y[j],"hidden");
  for(let j=0;j<c.J;j++)add("latent.x"+i+"_"+j,1-2*slots[i].x[j],"hidden");
 }
 lines.push("SPOOL shift_spool | A:TRUE | E:"+Array.from({length:c.H+1},(_,i)=>p(i)).join(","));
 for(let i=0;i<=c.H;i++){
  lines.push("ENC "+p(i)+" turn="+i+".."+i+" | I:"+i+" | A:TRUE | Q:C(0) | N:"+JSON.stringify(i===c.H?"Shift complete":"Dock slot "+i)+" | T:"+JSON.stringify(i===c.H?"Cargo routing is complete.":"Choose a routing action."));
  if(i===c.H)break;
  const t=slots[i],expr=c.J===1?"P(latent.x"+i+"_0)":"MUL("+Array.from({length:c.J},(_,j)=>"P(latent.x"+i+"_"+j+")").join(",")+")";
  // MUL in SWMD supports n-ary terms; credit and cumulative utility are bounded.
  for(const a of t.order){
   const opt=id(i,a),audit=a==="audit";
   lines.push("OPT "+opt+" | V:TRUE | P:"+(audit?"EQ(P(shift.credit),C(1))":"TRUE")+" | T:"+JSON.stringify(a));
   for(const win of t.active&&!audit?[true,false]:[t.active]){
    const writes=[];
    if(win)writes.push("SET shift.earned = ADD(P(shift.earned),C("+t.weight/(4*c.H)+"))");
    if(t.active&&audit)writes.push("SET shift.credit = C(0)");
    if(i+1<c.H){
     writes.push("SET shift.active = P(future.active"+(i+1)+")","SET shift.stake = P(future.stake"+(i+1)+")");
     for(let j=0;j<c.K;j++)writes.push("SET signal.bit"+j+" = P(future.y"+(i+1)+"_"+j+")");
    }
    let guard="TRUE";
    if(t.active&&!audit){const eq="EQ("+expr+",C("+(a==="commit0"?1:-1)+"))";guard=win?eq:"NOT("+eq+")";}
    lines.push("ORX "+opt+"/rx_"+opt+"_"+Number(win)+" -> "+p(i+1)+" | E:"+(writes.join("; ")||"NONE")+" | D:C(0) | G:"+guard+" | T:\"The cargo is sent. Outcome is recorded for end of shift.\"");
   }
  }
 }
 return lines.join("\n")+"\n";
}
export function verifySWMD(e,api){
 let fixtures=0,transitions=0,energyMax=0;
 // One representative per factorial cell; both extreme branches and policy
 // paths are exercised, with all legal one-step counterfactuals at each visit.
 for(const r of e.roots.filter(x=>x.rep===0)){
  const w=api.compileV2(swmd(r));fixtures++;
  for(const mode of ["oracle","first","commit","wrong","greedy"]){
   let s=api.initialV2(w),b=1,earned=0;
   for(let i=0;i<r.c.H;i++){
    const {t,g}=r.rows.get(i+":"+b),o=api.observeV2(w,s);
    check(o.status==="decision"&&o.turn===i&&o.values["shift.credit"]===b&&o.values["shift.stake"]*4===r.slots[i].weight&&o.values["shift.active"]===Number(r.slots[i].active),"runtime observation");
    check(Object.keys(o.values).length===r.c.K+3,"hidden coordinate leaked");
    for(let j=0;j<r.c.K;j++)check(o.values["signal.bit"+j]===1-2*r.slots[i].y[j],"runtime signal");
    check(JSON.stringify(o.actions.map(x=>x.id))===JSON.stringify(t.observation.actions.map(x=>x.id)),"runtime menu");
    const good=id(i,"commit"+parity(r.slots[i].y.slice(0,r.c.J)));
    const a=mode==="oracle"?g.winners[0]:mode==="first"?o.actions[0].id:mode==="commit"?good:mode==="wrong"?id(i,"commit"+(1-parity(r.slots[i].y.slice(0,r.c.J)))):r.slots[i].active&&b&&r.c.q8<8?id(i,"audit"):good;
    for(const opt of o.actions){
     const ref=apply(r,i,b,opt.id),step=api.stepV2(w,s,opt.id);transitions++;
     check(step.next.values["shift.credit"]===ref.b&&step.next.values["shift.earned"]*(4*r.c.H)===earned+ref.earned,"runtime transition");
     energyMax=Math.max(energyMax,step.squared_step_energy);
     if(opt.id===a){var chosen=step.next;var nxt=ref;}
    }
    s=chosen;b=nxt.b;earned+=nxt.earned;
   }
   check(api.observeV2(w,s).status==="terminal","runtime terminal");
  }
 }
 return {fixtures,transitions,max_squared_step_energy:energyMax};
}
export function verify(e){
 let bruteChecks=0,matched=0;
 for(const q of GRID.q8)for(let n=0;n<=4;n++)for(const b of [0,1]){
  check(value(n,b,q)===brute(n,b,q),"brute value mismatch");bruteChecks++;
  check(value(n,b,q)<=2*n,"full-information ceiling");
 }
 const by=new Map();
 for(const r of e.roots){
  const {H,density,q8,J,K}=r.c,key=[H,density,r.rep].join(":");
  const sig=JSON.stringify(r.slots.map(s=>[s.active,s.weight,s.y.slice(0,8),s.order]));
  if(by.has(key)){check(by.get(key)===sig,"matched tape drift");matched++;}else by.set(key,sig);
 }
 const oracle=score(e,controls(e,"oracle")),wrong=score(e,controls(e,"wrong"));
 check(oracle.total.correct===e.tasks.length&&oracle.total.stopped===0&&oracle.total.regret===0,"oracle replay");
 check(wrong.total.informative_correct===0&&wrong.total.correct===wrong.total.rows-wrong.total.informative_rows,"wrong control");
 const invalid=score(e,[]);
 check(invalid.total.correct===0&&invalid.total.stopped===e.roots.length&&invalid.total.earned===0,"missing control");
 const malformed=score(e,[{id:e.tasks[0].id,action:e.tasks[0].observation.actions[0].id},{id:e.tasks[0].id,action:e.tasks[0].observation.actions[0].id},{id:e.tasks[1].id,action:"illegal"},{id:"unknown",action:"x"},null]);
 check(malformed.submission.duplicates===1&&malformed.submission.unknown_ids===1&&malformed.submission.malformed===1&&malformed.total.valid===0,"invalid controls");
 return {brute_checks:bruteChecks,matched_tapes:matched,missing_and_invalid:"pass",oracle_and_wrong:"pass"};
}
