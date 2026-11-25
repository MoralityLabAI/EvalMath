function core(){
 const check=(x,m)=>{if(!x)throw Error("SRG24: "+m)},sum=a=>a.reduce((s,x)=>s+x,0),mean=a=>a.length?sum(a)/a.length:null,close=(a,b)=>Math.abs(a-b)<=1e-9*Math.max(1,Math.abs(a),Math.abs(b)),seeds=[0x53522401,0x53522402],REPS=4,PROPOSALS=32;
 const modes=["d1","d2","terminal","uniform","beam","d4","held_min"],arms=["robust","mean","d1","random"],tiers=["low","mid","high"];
 const key=(t,m,e)=>[t,m,e].join(":"),legal=(w,t,e)=>w.steps[t].order.filter(a=>a==="collect"||a==="switch"&&e>0||a==="recharge"&&e<w.C);
 function step(w,t,m,e,a,cut=-1){const s=w.steps[t],nm=t===cut?m:s.maps[a][m],ne=e+Number(a==="recharge")-Number(a==="switch"),r=(a==="collect"?s.rewards[m]:0)+(t===w.H-1&&nm===w.target&&ne>0?w.B:0);return{m:nm,e:ne,r}}
 function rng(seed){let x=seed>>>0||1;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0}}
 function mix(w,seed,proposal,salt=0){return(seed^Math.imul(w.rep+1,0x9e3779b9)^Math.imul(w.H,0x85ebca6b)^Math.imul(w.W,0xc2b2ae35)^Math.imul(w.C,0x27d4eb2f)^Math.imul(proposal+1,0x165667b1)^salt)>>>0}
 function variant(w,seed,i){
  const r=rng(mix(w,seed,i)),steps=w.steps.map(s=>({...s,rewards:s.rewards.slice()})),edits=[];
  if(i)for(let k=0;k<(i<=16?2:4);k++){const t=r()%w.H,a=r()%w.W,b0=r()%(w.W-1),b=b0>=a?b0+1:b0;[steps[t].rewards[a],steps[t].rewards[b]]=[steps[t].rewards[b],steps[t].rewards[a]];edits.push([t,a,b])}
  const out={...w,steps,id:w.id+"_p"+i};return{w:out,edits,i};
 }
 function scope(w,v){
  check(JSON.stringify({...w,id:null,steps:null})===JSON.stringify({...v,id:null,steps:null}),"world scope");
  for(let t=0;t<w.H;t++){
   const a=w.steps[t],b=v.steps[t];check(JSON.stringify({...a,rewards:null})===JSON.stringify({...b,rewards:null}),"reaction scope");
   check(JSON.stringify(a.rewards.slice().sort())===JSON.stringify(b.rewards.slice().sort()),"stage histogram");
  }
 }
 function guard(w,cut=-1,T){
  const memo=new Map();function value(t,m,e){if(t===w.H)return 0;const k=key(t,m,e);if(memo.has(k))return memo.get(k).max;const q=Object.fromEntries(legal(w,t,e).map(a=>{const n=step(w,t,m,e,a,cut);return[a,n.r+value(t+1,n.m,n.e)]})),v=Object.values(q),z={q,max:Math.max(...v),info:Math.max(...v)>Math.min(...v)};memo.set(k,z);T.guard_states++;return z.max}
  const opt=value(0,w.initial,1),root=memo.get(key(0,w.initial,1));T.guard_dp++;
  return {opt,q:root.q,rows:memo.size,informative:[...memo.values()].filter(r=>r.info).length};
 }
 function certify(w,T){const g=guard(w,-1,T);let sensitive=0;for(let t=0;t<w.H;t++){const c=guard(w,t,T);sensitive+=Number(Object.keys(g.q).some(a=>g.q[a]!==c.q[a]))}return{opt:g.opt,rows:g.rows,info:g.informative/g.rows,sensitive}}

 function uniformPolicy(w){
  const memo=new Map();
  function v(t,m,e){if(t===w.H)return 0;const k=key(t,m,e);if(memo.has(k))return memo.get(k);const a=legal(w,t,e),q=mean(a.map(a=>{const n=step(w,t,m,e,a);return n.r+v(t+1,n.m,n.e)}));memo.set(k,q);return q}
  return(t,m,e)=>{const a=legal(w,t,e),q=a.map(a=>{const n=step(w,t,m,e,a);return n.r+v(t+1,n.m,n.e)}),hi=Math.max(...q);return a[q.findIndex(x=>Math.abs(x-hi)<1e-12)]};
 }

 function runtimeCheck(w,R,api,T){
  const compiled=api.compileV2(R.swmd(w));T.fixtures++;let front=[{s:api.initialV2(compiled),m:w.initial,e:1,earned:0}];
  for(let t=0;t<w.H;t++){const next=new Map();for(const {s,m,e,earned} of front){
   T.states++;const o=api.observeV2(compiled,s),a=legal(w,t,e);check(o.status==="decision"&&o.turn===t&&Object.keys(o.values).length===5&&o.values["cargo.mode"]*8===m&&o.values["cargo.energy"]*2===e&&o.values["cargo.target"]*8===w.target&&o.values["cargo.cap"]*2===w.C&&o.values["cargo.bonus"]*64===w.B,"runtime public");
   check(JSON.stringify(o.actions.map(x=>x.id))===JSON.stringify(a.map(x=>`a${t}_${x}`)),"runtime menu");
   for(const act of a){const n=step(w,t,m,e,act),ns=api.stepV2(compiled,s,`a${t}_${act}`).next,earned2=earned+n.r;T.transitions++;check(ns.values["cargo.mode"]*8===n.m&&ns.values["cargo.energy"]*2===n.e&&ns.values["cargo.score"]*64===earned2,"runtime payoff");if(t===w.H-1){check(api.observeV2(compiled,ns).status==="terminal","runtime terminal");T.terminal++}const k=n.m+":"+n.e;if(!next.has(k))next.set(k,{s:ns,m:n.m,e:n.e,earned:earned2})}
  }front=[...next.values()]}
 }


 const trainModes=["d1","d2","terminal"];
 function training(w,cert,T){
  const out={},nom=3*w.H+w.B;
  for(const mode of trainModes){
   const terminal=mode==="terminal",d=terminal?w.H:Number(mode.slice(1)),memo=new Map();
   function q(t,m,e,h){return legal(w,t,e).map(a=>{const n=step(w,t,m,e,a),r=terminal?(t===w.H-1&&n.m===w.target&&n.e>0?w.B:0):n.r;return[a,r+val(t+1,n.m,n.e,h-1)]})}
   function val(t,m,e,h){if(t===w.H||h===0)return 0;const k=key(t,m,e)+":"+h;if(memo.has(k))return memo.get(k);T.training_states++;const v=Math.max(...q(t,m,e,h).map(x=>x[1]));memo.set(k,v);return v}
   let m=w.initial,e=1,earned=0;
   for(let t=0;t<w.H;t++){const scores=q(t,m,e,Math.min(d,w.H-t)),hi=Math.max(...scores.map(x=>x[1])),a=scores.find(x=>x[1]===hi)[0],n=step(w,t,m,e,a);earned+=n.r;m=n.m;e=n.e;T.training_decisions++}
   check(earned<=cert.opt,"training oracle bound");out[mode]=(cert.opt-earned)/nom;
  }
  return out;
 }
 function compare(a,b,field,base){return a[field]-b[field]||Math.abs(b.guard.opt-base.opt)-Math.abs(a.guard.opt-base.opt)||a.guard.sensitive-b.guard.sensitive||a.guard.info-b.guard.info||a.i-b.i}
 function dominates(a,b,base){
  const x=[a.robust,-Math.abs(a.guard.opt-base.opt),a.guard.sensitive,a.guard.info],y=[b.robust,-Math.abs(b.guard.opt-base.opt),b.guard.sensitive,b.guard.info];
  return x.every((v,i)=>v>=y[i])&&x.some((v,i)=>v>y[i]);
 }
 function freeze(R){
  const cohorts=[];
  for(const seed of seeds){
   const T={bases:0,proposals:0,duplicates:0,unique:0,scope_checks:0,guard_dp:0,guard_states:0,utility_fail:0,info_fail:0,causal_fail:0,feasible:0,training_states:0,training_decisions:0,pool_ge3:0,eligible:0,frontier_points:0,pareto_checks:0},groups=[];
   for(const w of R.worlds(seed,REPS)){
    if(w.H<6||w.W<4||w.target>1)continue;
    T.bases++;const baseline=certify(w,T),candidates=[],pool=[],seen=new Set();
    for(let i=0;i<=PROPOSALS;i++){
     T.proposals++;const c=variant(w,seed,i),sig=JSON.stringify(c.w.steps.map(s=>s.rewards));
     if(seen.has(sig)){T.duplicates++;continue}seen.add(sig);T.unique++;scope(w,c.w);T.scope_checks++;
     const g=i?certify(c.w,T):baseline,feas=[Math.abs(g.opt-baseline.opt)<=1,g.info+1e-12>=Math.max(.85,baseline.info-.03),g.sensitive>=Math.max(w.H-1,baseline.sensitive-1)];
     T.utility_fail+=Number(!feas[0]);T.info_fail+=Number(!feas[1]);T.causal_fail+=Number(!feas[2]);
     const tr=training(c.w,g,T),values=trainModes.map(m=>tr[m]),row={i,edits:c.edits,guard:g,feasible:feas.every(Boolean),fail:feas.map(x=>!x),training:tr,robust:Math.min(...values),mean:mean(values),d1:tr.d1,random:rng(mix(w,seed,i,0xa5310b71))()/4294967296};
     if(row.feasible){T.feasible++;pool.push(row)}candidates.push(row);
    }
    const frontier=pool.filter(a=>!pool.some(b=>dominates(b,a,baseline)));T.frontier_points+=frontier.length;
    for(const a of pool){const nondominated=frontier.includes(a);check(nondominated?!pool.some(b=>dominates(b,a,baseline)):frontier.some(b=>dominates(b,a,baseline)),"Pareto frontier");T.pareto_checks++}
    const eligiblePool=pool.length>=3;T.pool_ge3+=Number(eligiblePool);
    let selections=null,gap=null;
    if(eligiblePool){
     selections={};
     for(const arm of arms){
      const a=pool.slice().sort((x,y)=>compare(x,y,arm,baseline));
      const hi=arm==="robust"?frontier.slice().sort((x,y)=>compare(x,y,arm,baseline)).at(-1):a.at(-1);
      check(arm!=="robust"||hi.robust===a.at(-1).robust,"frontier high");
      selections[arm]=[a[0].i,a[Math.floor(a.length/2)].i,hi.i];
      if(arm==="robust")gap=hi.robust-a[0].robust;
     }
    }
    const eligible=eligiblePool&&gap>=.025;T.eligible+=Number(eligible);
    groups.push({id:w.id,H:w.H,W:w.W,C:w.C,B:w.B,rep:w.rep,target:w.target,baseline,candidates,frontier:frontier.map(r=>r.i),selections,robust_gap:gap,eligible});
   }
   cohorts.push({seed,tests:T,groups});
  }
  return {schema:"srg24.freeze.v1",training_reasoners:trainModes,reserved_reasoners:["uniform","beam","d4"],cohorts};
 }
 function beam(w,T){
  let front=[{m:w.initial,e:1,earned:0}];
  for(let t=0;t<w.H;t++){
   const next=[];for(const p of front)for(const a of legal(w,t,p.e)){const n=step(w,t,p.m,p.e,a);next.push({m:n.m,e:n.e,earned:p.earned+n.r,serial:next.length});T.beam_expansions++}
   next.sort((a,b)=>b.earned-a.earned||a.serial-b.serial);front=next.slice(0,2);
  }return front[0].earned;
 }
 function evaluate(w,R,c,T){
  const rs=R.rows(w),root=rs[0],nom=3*w.H+w.B,g=c.guard;
  check(root.max===g.opt&&rs.length===g.rows&&close(rs.filter(r=>r.range>0).length/rs.length,g.info),"guard/source drift");T.oracle_checks++;
  const map=new Map(rs.map(r=>[key(r.t,r.m,r.e),r])),uniform=uniformPolicy(w),out={};
  for(const m of ["d1","d2","terminal","d4","uniform","oracle"]){
   let s=w.initial,e=1,v=0;
   for(let t=0;t<w.H;t++){const a=m==="uniform"?uniform(t,s,e):map.get(key(t,s,e)).controls[m];check(legal(w,t,e).includes(a),"illegal control");const n=step(w,t,s,e,a);s=n.m;e=n.e;v+=n.r}
   check(v<=root.max,"control bound");if(m==="oracle")check(v===root.max,"oracle replay");else{out[m]=(root.max-v)/nom;if(trainModes.includes(m)){check(out[m]===c.training[m],"training replay");T.training_replays++}}
  }
  const earned=beam(w,T);check(earned<=root.max,"beam bound");out.beam=(root.max-earned)/nom;out.held_min=Math.min(out.uniform,out.beam);out.train_min=Math.min(...trainModes.map(m=>out[m]));return out;
 }
 function audit(frozen,R,api){
  const cohorts=[];
  for(const c of frozen.cohorts){
   const T={oracle_checks:0,training_replays:0,beam_expansions:0,fixtures:0,states:0,transitions:0,terminal:0,packet_checks:0},all=new Map([...R.worlds(c.seed,REPS)].map(w=>[w.id,w])),groups=[],covered=new Set(),summary={};
   for(const g of c.groups){
    const w=all.get(g.id),evals=new Map();check(w&&w.H===g.H&&w.W===g.W&&w.target===g.target,"source root");
    for(const r of g.candidates){const v=variant(w,c.seed,r.i);check(JSON.stringify(v.edits)===JSON.stringify(r.edits),"edit drift");evals.set(r.i,evaluate(v.w,R,r,T))}
    const selected=g.selections&&Object.fromEntries(arms.map(a=>[a,g.selections[a].map(i=>({i,regret:evals.get(i),guard:g.candidates.find(r=>r.i===i).guard}))]));
    if(g.eligible){
     for(const arm of arms){
      const x=selected[arm],a=summary[arm]??={count:0,modes:{},guard:{opt_min_delta:Infinity,opt_max_delta:-Infinity,min_info:Infinity,min_sensitive_margin:Infinity}};a.count++;
      for(const y of x){const z=y.guard;a.guard.opt_min_delta=Math.min(a.guard.opt_min_delta,z.opt-g.baseline.opt);a.guard.opt_max_delta=Math.max(a.guard.opt_max_delta,z.opt-g.baseline.opt);a.guard.min_info=Math.min(a.guard.min_info,z.info);a.guard.min_sensitive_margin=Math.min(a.guard.min_sensitive_margin,z.sensitive-Math.max(w.H-1,g.baseline.sensitive-1))}
      for(const m of [...modes,"train_min"]){const b=a.modes[m]??={low:0,mid:0,high:0,positive:0,monotone:0},[l,k,h]=x.map(z=>z.regret[m]);b.low+=l;b.mid+=k;b.high+=h;b.positive+=Number(h>l);b.monotone+=Number(l<=k&&k<=h)}
     }
     const cell=[w.H,w.W,w.C,w.B].join(":");if(!covered.has(cell)){covered.add(cell);for(const i of g.selections.robust){const v=variant(w,c.seed,i).w;runtimeCheck(v,R,api,T);for(const r of R.rows(v,undefined,undefined,true)){check(r.task.id===r.id&&r.task.observation.actions.some(a=>a.id===r.controls.oracle),"packet");T.packet_checks++}}}
    }
    groups.push({id:g.id,eligible:g.eligible,selected,candidate_outcomes:[...evals].map(([i,regret])=>({i,regret}))});
   }
   for(const a of Object.values(summary))for(const b of Object.values(a.modes)){for(const k of tiers)b[k]/=a.count;b.high_low=b.high-b.low;b.positive_fraction=b.positive/a.count;b.monotone_fraction=b.monotone/a.count}
   const coverage=c.tests.eligible/c.tests.bases,d=summary.robust?.modes,s=summary.d1?.modes;
   const avg=a=>(a.uniform.high_low+a.beam.high_low)/2;
   const gates={coverage:coverage>=.60,uniform_gap:!!d&&d.uniform.high_low>=.01,beam_gap:!!d&&d.beam.high_low>=.01,uniform_positive:!!d&&d.uniform.positive_fraction>=.50,beam_positive:!!d&&d.beam.positive_fraction>=.50,over_d1:!!d&&!!s&&avg(d)-avg(s)>=.005};
   cohorts.push({seed:c.seed,coverage,summary,tests:T,runtime_cells:covered.size,gates,pass:Object.values(gates).every(Boolean),groups});
  }
  return {schema:"srg24.audit.v1",cohorts,promote:cohorts.every(c=>c.pass)};
 }

 function stage(frozen,R,cohort,tier){
  check(tiers.includes(tier)&&Number.isInteger(cohort)&&cohort>=0&&cohort<frozen.cohorts.length,"stage args");
  const c=frozen.cohorts[cohort],all=new Map([...R.worlds(c.seed,REPS)].map(w=>[w.id,w])),rows=[];
  for(const g of c.groups.filter(g=>g.eligible)){
   const w=variant(all.get(g.id),c.seed,g.selections.robust[tiers.indexOf(tier)]).w;
   for(const r of R.rows(w,undefined,undefined,true)){r.task.id=`${cohort}_${tier}_${r.id}`;rows.push({task:r.task,gold:{id:r.task.id,winners:r.winners,q:r.q,t:r.t,m:r.m,e:r.e},w})}
  }return rows;
 }
 function score(frozen,R,cohort,tier,submissions){
  const rows=stage(frozen,R,cohort,tier),seen=new Map(),dups=new Set();let malformed=0,valid=0,correct=0,informative=0,informative_correct=0,earned=0,opt=0,completed=0;
  for(const s of submissions){if(!s||typeof s.id!=="string"){malformed++;continue}if(seen.has(s.id))dups.add(s.id);else seen.set(s.id,s)}
  const grouped=new Map();for(const r of rows){const g=r.gold,x=seen.get(g.id),a=x&&!dups.has(g.id)&&Object.keys(x).sort().join(",")==="action,id"&&typeof x.action==="string"&&Object.hasOwn(g.q,x.action)?x.action:null,info=Math.max(...Object.values(g.q))>Math.min(...Object.values(g.q)),ok=a!==null&&g.winners.includes(a);valid+=Number(a!==null);correct+=Number(ok);informative+=Number(info);informative_correct+=Number(ok&&info);seen.delete(g.id);const arr=grouped.get(r.w.id)??[];arr.push({...r,a});grouped.set(r.w.id,arr)}
  for(const rs of grouped.values()){const w=rs[0].w,map=new Map(rs.map(r=>[key(r.gold.t,r.gold.m,r.gold.e),r])),root=rs[0].gold;opt+=Math.max(...Object.values(root.q));let m=w.initial,e=1,t=0;for(;t<w.H;t++){const a=map.get(key(t,m,e)).a;if(a===null)break;const n=step(w,t,m,e,a);earned+=n.r;m=n.m;e=n.e}completed+=Number(t===w.H)}
  return{rows:rows.length,valid,correct,informative,informative_correct,earned,opt,completed,worlds:grouped.size,malformed,duplicates:dups.size,unknown:seen.size};
 }

 return{freeze,audit,stage,score};
}
export const {freeze,audit,stage,score}=core();
