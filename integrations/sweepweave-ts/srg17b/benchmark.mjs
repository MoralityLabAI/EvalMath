function core(){
 const check=(x,m)=>{if(!x)throw Error(m)},seed0=0x53521701,reps0=16;
 const modes=["oracle","greedy","first","always_route","always_audit","bank"],parity=a=>a.reduce((x,y)=>x^y,0);
 function rng(seed){let x=seed>>>0||1;return n=>{const lim=Math.floor(4294967296/n)*n;do{x^=x<<13;x^=x>>>17;x^=x<<5}while((x>>>0)>=lim);return (x>>>0)%n}}
 function shuffle(a,r){a=a.slice();for(let i=a.length-1;i>0;i--){let j=r(i+1);[a[i],a[j]]=[a[j],a[i]]}return a}
 function tape(seed,rep){const r=rng((seed^Math.imul(rep+1,0x9e3779b9))>>>0);return shuffle([0,1,2,3],r).map((slot,rank)=>({slot,rank,noise:r(10),bits:Array.from({length:8},()=>r(2)),order:shuffle(["bank","route","audit","dock0","dock1","wait0","wait1"],r),mode:r(2),trap:r(2)})).sort((a,b)=>a.slot-b.slot)}
 function* worlds(seed=seed0,reps=reps0){
  check(Number.isInteger(seed)&&seed>0&&seed<=0xffffffff&&Number.isInteger(reps)&&reps>0&&reps<=256,"seed/reps");let cell=0;
  for(const H of [1,2,4,8])for(const density of [1,2,3])for(const q10 of [6,8,10])for(const K of [1,2,4,8])for(const gap of(H===1?[0]:[0,10,25,50])){
   for(let rep=0;rep<reps;rep++)for(const tape0 of tape(seed,rep)){
    const y=tape0.bits.slice(0,K),x=y.slice();x[0]^=Number(tape0.noise>=q10);
    const route=9*q10,audit=route+(q10<10&&tape0.mode?4:-4),best=Math.max(route,audit),bank=tape0.trap?best+4:best-gap;
    check(bank>0&&bank<=100&&audit<=90,"bounds");
    yield {c:{H,density,q10,K,gap},t:tape0,rep,cell,active:tape0.rank<density,y,x,route,audit,bank,id:`c${cell}r${rep}s${tape0.slot}`};
   }cell++;
  }
 }
 function channels(w,t){return t===0||!w.active?["start"]:["bank","route","audit"]}
 function legal(w,t,ch){const a=!w.active||ch==="bank"||t>0&&t<w.c.H-1?["wait0","wait1"]:t===0?(w.c.H===1?["bank","dock0","dock1","audit"]:["bank","route","audit"]):["dock0","dock1"];return w.t.order.filter(x=>a.includes(x))}
 function signal(w,t,ch){return w.active&&(w.c.H===1||t===w.c.H-1&&ch!=="bank")?(ch==="audit"?w.x:w.y):null}
 function pay(w,t,ch,a){if(!w.active||a.startsWith("wait"))return 0;if(a==="bank")return w.bank;if(w.c.H===1&&a==="audit")return w.audit;if(a.startsWith("dock"))return Number(a.at(-1))===parity(w.x)?(ch==="audit"?w.audit:90):0;return 0}
 function q(w,t,ch,a){
  if(!w.active||a.startsWith("wait"))return w.active&&ch==="route"?w.route:w.active&&ch==="audit"?w.audit:0;
  if(["bank","route","audit"].includes(a))return w[a];
  const hit=Number(a.at(-1))===parity(signal(w,t,ch));
  return ch==="audit"?(hit?w.audit:0):(hit?w.route:90-w.route);
 }
 function rows(w){
  const out=[];for(let t=0;t<w.c.H;t++)for(const ch of channels(w,t)){
   const a=legal(w,t,ch),scores=Object.fromEntries(a.map(a=>[a,q(w,t,ch,a)])),hi=Math.max(...Object.values(scores)),lo=Math.min(...Object.values(scores)),id=`${w.id}t${t}${ch}`;
   const task={id,kind:"storyworld_policy",action_budget:w.c.H-t,root_horizon:w.c.H,goal:"Maximize total expected cargo points by the end of this independent contract.",
    task:"The bank pays its stated points immediately and closes the opportunity. For H>1 reserve and technician each pay zero now and open a routing decision at the last turn. Ordinary routing pays 90 points for a correct dock; audited routing pays audited_points. Wrong routing pays zero. The correct dock is the XOR of the K true bits. The ordinary signal is correct except that its first bit independently disagrees with probability 1-q10/10. The audited signal is exact. For H=1, the ordinary signal is visible immediately, and technician pays the audited points immediately. Inactive and closed contracts pay zero on all wait actions. Intermediate waits change only the turn.",
    rules:{H:w.c.H,K:w.c.K,q10:w.c.q10,bank_points:w.bank,audited_points:w.audit,ordinary_points:90},observation:{encounter:ch,turn:t,status:"decision",values:{active:Number(w.active),signal:signal(w,t,ch)},actions:a.map(id=>({id,text:{bank:"Take bank payment",route:"Reserve ordinary routing",audit:"Hire technician",dock0:"Route to dock zero",dock1:"Route to dock one",wait0:"Wait at post A",wait1:"Wait at post B"}[id]}))},output_contract:"Return one legal action ID."};
   out.push({id,t,ch,scores,hi,lo,winners:a.filter(k=>scores[k]===hi),task});
  }return out;
 }
 function choose(w,r,m){const a=Object.keys(r.scores);if(m==="first")return a[0];if((m==="greedy"&&r.t===0&&w.c.H>1||m==="bank")&&a.includes("bank"))return "bank";if(m==="always_route"&&a.includes("route"))return "route";if(m==="always_audit"&&a.includes("audit"))return "audit";return r.winners[0]}
 const valid=(r,a)=>typeof a==="string"&&Object.hasOwn(r.scores,a);
 function rollout(w,rs,policy){let ch="start",earned=0,rootQ=0,complete=true;for(let t=0;t<w.c.H;t++){const r=rs.find(r=>r.t===t&&r.ch===ch),a=policy(r);if(!valid(r,a)){complete=false;break}if(!t)rootQ=r.scores[a];earned+=pay(w,t,ch,a);if(!t&&w.active&&w.c.H>1)ch=a}return{earned,rootQ,complete}}
 function brute(w){
  let route=0,audit=0;for(let y=0;y<2;y++){const a=[0,0],b=[0,0];for(let err=0;err<10;err++){const x=y^Number(err>=w.c.q10);for(let k=0;k<2;k++){a[k]+=Number(k===x)*90;b[k]+=Number(k===y)*w.audit}}route+=Math.max(...a);audit+=Math.max(...b)}
  let v={bank:w.bank,route:route/20,audit:audit/20};for(let t=w.c.H-2;t>0;t--)v=Object.fromEntries(Object.entries(v).map(([k,x])=>[k,Math.max(x,x)]));return v;
 }
 function empty(){return {contracts:0,active:0,rows:0,informative:0,correct:0,informative_correct:0,valid:0,earned:0,rootQ:0,oracleQ:0,greedyQ:0,positive_gap_contracts:0,positive_gap:0,positive_recovered:0,trap_regret:0,completed:0}}
 function add(a,w,rs,policy){const run=rollout(w,rs,policy),r=rs[0],g=r.scores[choose(w,r,"greedy")],gap=r.hi-g;a.contracts++;a.active+=Number(w.active);a.earned+=run.earned;a.rootQ+=run.rootQ;a.oracleQ+=r.hi;a.greedyQ+=g;a.completed+=Number(run.complete);
  if(gap>0){a.positive_gap_contracts++;a.positive_gap+=gap;a.positive_recovered+=run.rootQ-g}if(w.active&&w.t.trap)a.trap_regret+=r.hi-run.rootQ;
  for(const r of rs){const x=policy(r),v=valid(r,x),ok=v&&r.winners.includes(x),info=r.hi>r.lo;a.rows++;a.valid+=Number(v);a.correct+=Number(ok);a.informative+=Number(info);a.informative_correct+=Number(info&&ok)}
 }
 function finish(a){const d=(x,y)=>y?x/y:null;return {...a,raw_accuracy:d(a.correct,a.rows),informative_accuracy:d(a.informative_correct,a.informative),realized_per_active:d(a.earned,100*a.active),root_oracle_continuation_fraction:d(a.rootQ,100*a.active),positive_gap_recovery:d(a.positive_recovered,a.positive_gap),global_root_regret:a.oracleQ-a.rootQ}}
 function experiment(seed=seed0,reps=reps0,submissions=null){
  const total={},groups={},tests={brute:0,gap:0,matched:0,oracle:0},sig=new Map(),seen=new Map(),dups=new Set();let cells=0,contracts=0,malformed=0;
  if(submissions!==null)for(const s of submissions){if(!s||typeof s.id!=="string"){malformed++;continue}if(seen.has(s.id))dups.add(s.id);else seen.set(s.id,s)}
  for(const w of worlds(seed,reps)){
   cells=Math.max(cells,w.cell+1);contracts++;const rs=rows(w),r=rs[0],gap=r.hi-r.scores[choose(w,r,"greedy")],b=brute(w);
   if(w.active&&w.c.H>1){check(r.scores.bank===b.bank&&r.scores.route===b.route&&r.scores.audit===b.audit,"brute");tests.brute++;check(gap===(w.t.trap?0:w.c.gap),"gap");tests.gap++}else check(gap===0,"H1/inactive gap");
   const k=w.rep+":"+w.t.slot,s=JSON.stringify(w.t);if(sig.has(k)){check(sig.get(k)===s,"tape");tests.matched++}else sig.set(k,s);
   check(rollout(w,rs,r=>choose(w,r,"oracle")).complete,"oracle");tests.oracle++;
   const key=JSON.stringify(w.c);
   for(const m of submissions===null?modes:["submitted"]){
    const policy=m==="submitted"?r=>{const s=seen.get(r.id);return s&&!dups.has(r.id)&&Object.keys(s).sort().join(",")==="action,id"?s.action:null}:r=>choose(w,r,m);
    add(total[m]??=empty(),w,rs,policy);add((groups[key]??={})[m]??=empty(),w,rs,policy);
   }
   if(submissions!==null)for(const r of rs)seen.delete(r.id);
  }
  const summary={schema:"srg17b.receipt.v1",seed,reps,cells,contracts,tests,controls:Object.fromEntries(Object.entries(total).map(([k,a])=>[k,finish(a)])),groups:Object.entries(groups).map(([k,v])=>({config:JSON.parse(k),controls:Object.fromEntries(Object.entries(v).map(([m,a])=>[m,finish(a)]))}))};
  if(submissions!==null)summary.submission={unknown:seen.size,malformed,duplicates:dups.size};return summary;
 }
 function swmd(w){
  const H=w.c.H,p=(t,ch)=>`p${t}_${ch}`,pages=[];for(let t=0;t<H;t++)for(const ch of channels(w,t))pages.push([t,ch]);
  const L=["# SWMD-SRG/2","id: SRG17B-contract","title: \"Cargo contract\"","about: \"Choose a contract and settle the cargo.\"","start: "+p(0,"start"),"turn-base: 0","tie: first","direct: strict","VAR cargo.earned = 0 | hidden","VAR cargo.active = "+Number(w.active),"VAR cargo.target = "+(1-2*parity(w.x))+" | hidden"];
  L[L.length-2]+=" | public";const initial=signal(w,0,"start");
  for(let j=0;j<w.c.K;j++)L.push(`VAR signal.bit${j} = ${initial?1-2*initial[j]:0} | public`,`VAR private.y${j} = ${1-2*w.y[j]} | hidden`,`VAR private.x${j} = ${1-2*w.x[j]} | hidden`);
  L.push("SPOOL contract_spool | A:TRUE | E:"+pages.map(([t,ch])=>p(t,ch)).concat("done").join(","));
  for(const [t,ch] of pages){L.push(`ENC ${p(t,ch)} turn=${t}..${t} | I:${t} | A:TRUE | Q:C(0) | N:"Cargo contract" | T:"Choose a legal action."`);
   for(const a of legal(w,t,ch)){const id=`${p(t,ch)}_${a}`,next=t===0&&w.active&&H>1?a:ch,dest=t===H-1?"done":p(t+1,next),dock=a.startsWith("dock");L.push(`OPT ${id} | V:TRUE | P:TRUE | T:${JSON.stringify(a)}`);
    for(const win of dock?[true,false]:[false]){const earned=dock?(win?(ch==="audit"?w.audit:90):0):pay(w,t,ch,a),writes=[];if(earned)writes.push(`SET cargo.earned = ADD(P(cargo.earned),C(${earned/100}))`);
     if(t+1===H-1&&w.active&&next!=="bank")for(let j=0;j<w.c.K;j++)writes.push(`SET signal.bit${j} = P(private.${next==="audit"?"x":"y"}${j})`);
     const eq=`EQ(P(cargo.target),C(${a==="dock0"?1:-1}))`,guard=dock?(win?eq:`NOT(${eq})`):"TRUE";
     L.push(`ORX ${id}/rx_${id}_${Number(win)} -> ${dest} | E:${writes.join("; ")||"NONE"} | D:C(0) | G:${guard} | T:"Action recorded."`);
    }
   }
  }L.push(`ENC done turn=${H}..${H} | I:${H} | A:TRUE | Q:C(0) | N:"Complete" | T:"Contract closed."`);return L.join("\n")+"\n";
 }
 function runtimeCheck(api,seed=seed0){let fixtures=0,transitions=0;for(const w of worlds(seed,1)){if(w.t.rank!==0&&w.t.rank!==3)continue;const compiled=api.compileV2(swmd(w));fixtures++;const visited=new Set();
  function walk(s,t,ch,earned){if(t===w.c.H){check(api.observeV2(compiled,s).status==="terminal","terminal");return}const key=t+":"+ch;if(visited.has(key))return;visited.add(key);
   const o=api.observeV2(compiled,s),obs=signal(w,t,ch),acts=legal(w,t,ch);check(o.status==="decision"&&o.turn===t&&Object.keys(o.values).length===w.c.K+1&&o.values["cargo.active"]===Number(w.active),"runtime public");for(let j=0;j<w.c.K;j++)check(o.values[`signal.bit${j}`]===(obs?1-2*obs[j]:0),"signal");check(JSON.stringify(o.actions.map(x=>x.id))===JSON.stringify(acts.map(a=>`p${t}_${ch}_${a}`)),"menu");
   for(const a of acts){const n=api.stepV2(compiled,s,`p${t}_${ch}_${a}`).next,e=earned+pay(w,t,ch,a);transitions++;check(Math.abs(n.values["cargo.earned"]*100-e)<1e-8,"reward");walk(n,t+1,t===0&&w.active&&w.c.H>1?a:ch,e)}
  }walk(api.initialV2(compiled),0,"start",0);
 }return{fixtures,transitions}}
 return {seed0,reps0,worlds,rows,choose,experiment,swmd,runtimeCheck};
}
export const {seed0,reps0,worlds,rows,choose,experiment,swmd,runtimeCheck}=core();
