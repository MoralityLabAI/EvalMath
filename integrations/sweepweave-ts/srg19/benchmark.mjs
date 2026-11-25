function core(){
 const check=(v,m)=>{if(!v)throw Error("SRG19: "+m)},SEED=0x53521901,REPS=8;
 const names=["work0","work1","probe"],modes=["first","d1","d2","d4","map","no_probe","oracle"],grid={H:[2,4,5],f:[0,1],q:[2,3,4],B:[4,8]},scale=d=>16**d;
 function gcd(a,b){while(b){const c=a%b;a=b;b=c}return a}
 function canonical(x,y){const g=gcd(x,y);check(g>0,"zero belief");return [x/g,y/g,g]}
 function rng(seed){let x=seed>>>0||1;return n=>{const lim=Math.floor(4294967296/n)*n;do{x^=x<<13;x^=x>>>17;x^=x<<5}while((x>>>0)>=lim);return (x>>>0)%n}}
 function shuffle(a,r){a=a.slice();for(let i=a.length-1;i>0;i--){const j=r(i+1);[a[i],a[j]]=[a[j],a[i]]}return a}
 function tape(seed,rep){const r=rng((seed^Math.imul(rep+1,0x9e3779b9))>>>0);return {p:1+r(3),initialWord:r(4),steps:Array.from({length:5},()=>({b:r(2),flip:r(2),r0:1+r(3),r1:1+r(3),order:shuffle(names,r),noise:Object.fromEntries(names.map(a=>[a,r(4)])),obs:Object.fromEntries(names.map(a=>[a,r(4)]))}))}}
 function* bases(seed=SEED,reps=REPS){check(Number.isInteger(seed)&&seed>0&&seed<=0xffffffff&&Number.isInteger(reps)&&reps>0&&reps<=256,"seed/reps");let cell=0;
  for(const H of grid.H)for(const f of grid.f)for(const q of grid.q)for(const B of grid.B){
   for(let rep=0;rep<reps;rep++){const t=tape(seed,rep),[x,y]=canonical(4-t.p,t.p);yield{H,f,q,B,rep,cell,id:`c${cell}r${rep}`,prior:[x,y],p:t.p,initialWord:t.initialWord,steps:t.steps.slice(0,H)}}
   cell++;
  }
 }
 function* worlds(seed=SEED,reps=REPS){for(const b of bases(seed,reps))for(const target of [0,1])yield{...b,target,id:`${b.id}g${target}`}}
 function legal(w,t,e,no=false){return w.steps[t].order.filter(a=>a!=="probe"||e&&!no)}
 function running(w,t,z,a){const s=w.steps[t];return a==="work0"&&z===s.b?s.r0:a==="work1"&&z!==s.b?s.r1:0}
 function flip(w,t,a){return w.steps[t].flip^Number(a==="work1")}
 function branches(w,t,e,x,y,a,sham=false){
  const fl=flip(w,t,a),f=w.f,ne=e-Number(a==="probe"),u=(fl?y:x)*(4-f)+(fl?x:y)*f,v=(fl?x:y)*(4-f)+(fl?y:x)*f;
  const q=a==="probe"&&!sham?4:w.q,signal=[[u*q,v*(4-q)],[u*(4-q),v*q]],out=[];
  let mass=0;
  for(let o=0;o<2;o++){const [a,b]=signal[o];mass+=a+b;if(a+b){const [nx,ny,g]=canonical(a,b);check(nx*g===a&&ny*g===b,"posterior");out.push({o,x:nx,y:ny,g,e:ne,mass:a+b})}}
  check(u+v===4*(x+y)&&mass===16*(x+y),"mass conservation");
  const reward=x*running(w,t,0,a)+y*running(w,t,1,a),terminal=t===w.H-1?(w.target?v:u)*w.B:0;
  return {reward,terminal,out,u,v,ne};
 }
 function solve(w,{no=false,sham=false}={}){
  const memo=new Map();
  function value(t,e,x,y,d){if(t===w.H||!d)return 0;const k=[t,e,x,y,d].join(":");if(memo.has(k))return memo.get(k);const n=Math.max(...Object.values(scores(t,e,x,y,d)));check(Number.isSafeInteger(n),"exact integer bound");memo.set(k,n);return n}
  function scores(t,e,x,y,d){
   return Object.fromEntries(legal(w,t,e,no).map(a=>{const b=branches(w,t,e,x,y,a,sham);let n=b.reward*scale(d)+b.terminal*4*scale(d-1);
    if(d>1&&t+1<w.H)for(const v of b.out)n+=v.g*value(t+1,v.e,v.x,v.y,d-1);
    check(Number.isSafeInteger(n),"Q integer");return[a,n]}));
  }
  return {value,scores};
 }
 function best(q){const max=Math.max(...Object.values(q)),winners=Object.keys(q).filter(a=>q[a]===max);return{max,winners,range:max-Math.min(...Object.values(q))}}
 // Independent direct conditional-probability recursion, without memoization,
 // canonical masses, or transition helper. Floating point is only a cross-check.
 function brute(w,t,e,p){
  if(t===w.H)return 0;
  let hi=-1;
  for(const a of names){
   if(a==="probe"&&!e)continue;
   const s=w.steps[t],r=a==="work0"?(s.b?p:1-p)*s.r0:a==="work1"?(s.b?1-p:p)*s.r1:0;
   const pre=(s.flip^Number(a==="work1"))?1-p:p,pp=pre*(1-w.f/4)+(1-pre)*w.f/4;
   let val=r;
   if(t===w.H-1)val+=w.B*(w.target?pp:1-pp);
   else {const q=(a==="probe"?4:w.q)/4;
    for(const o of [0,1]){const n=pp*(o?q:1-q),z=(1-pp)*(o?1-q:q),prob=n+z;if(prob>0)val+=prob*brute(w,t+1,e-Number(a==="probe"),n/prob)}
   }
   hi=Math.max(hi,val);
  }return hi;
 }
 const key=(t,e,x,y)=>[t,e,x,y].join(":");
 function rows(w,s=solve(w),np=solve(w,{no:true}),includeTask=false){
  let front=[{e:1,x:w.prior[0],y:w.prior[1]}];const out=[];
  for(let t=0;t<w.H;t++){
   const next=new Map();
   for(const {e,x,y} of front){
    const d=w.H-t,q=s.scores(t,e,x,y,d),b=best(q),id=`${w.id}t${t}e${e}p${x}_${y}`,controls={first:Object.keys(q)[0],oracle:b.winners[0],no_probe:best(np.scores(t,e,x,y,d)).winners[0],map:best(s.scores(t,e,Number(x>=y),Number(y>x),d)).winners[0]};
    for(const k of [1,2,4])controls[`d${k}`]=best(s.scores(t,e,x,y,Math.min(k,d))).winners[0];
    const row={id,t,e,x,y,q,...b,controls};
    if(includeTask)row.task={id,kind:"storyworld_policy",goal:"Maximize expected total points through the final reaction.",task:"Mode z is hidden and binary. The supplied posterior masses give its exact current distribution. Work0 earns r0 iff z equals desired mode b; work1 earns r1 iff z differs from b. Probe earns zero, spends its one credit, and has the same phase map as work0. Each action first XORs the old mode with flip (work0/probe) or 1-flip (work1), then independently flips with probability f/4. A new binary signal matches the new mode with probability q/4 after work, or certainty after probe. The final reaction earns an additional B if the new mode matches target; no further decision follows. Running rewards and latent modes remain hidden. All transitions and signals are independent conditional on their inputs. Update beliefs after future observations and choose one legal action ID.",action_budget:d,root_horizon:w.H,rules:{H:w.H,f_quarters:w.f,q_quarters:w.q,terminal_bonus:w.B,target:w.target,remaining_reactions:w.steps.slice(t).map(({b,flip,r0,r1})=>({b,flip,r0,r1}))},observation:{encounter:"turn_"+t,turn:t,status:"decision",values:{probe_credit:e,posterior_masses:[x,y]},actions:Object.keys(q).map(id=>({id,text:{work0:"Work route zero",work1:"Work route one",probe:"Probe the mode"}[id]}))},output_contract:"Return one legal action ID."};
    out.push(row);
    if(t+1<w.H)for(const a of Object.keys(q))for(const z of branches(w,t,e,x,y,a).out)next.set(key(t+1,z.e,z.x,z.y),z);
   }front=[...next.values()];
  }return out;
 }
 const valid=(r,a)=>typeof a==="string"&&Object.hasOwn(r.q,a);
 function evaluatePolicy(w,rs,policy){
  const by=new Map(rs.map(r=>[key(r.t,r.e,r.x,r.y),r])),memo=new Map();
  function go(t,e,x,y){
   if(t===w.H)return [0,0,0];
   const k=key(t,e,x,y);if(memo.has(k))return memo.get(k);
   const r=by.get(k),a=policy(r),d=w.H-t;if(!valid(r,a))return [0,0,0];
   const b=branches(w,t,e,x,y,a);let n=b.reward*scale(d)+b.terminal*4*scale(d-1),p=Number(a==="probe")*(x+y)*scale(d),completion=t===w.H-1?(x+y)*scale(d):0;
   if(t+1<w.H)for(const v of b.out){const [z,u,c]=go(t+1,v.e,v.x,v.y);n+=v.g*z;p+=v.g*u;completion+=v.g*c}
   check(Number.isSafeInteger(n)&&Number.isSafeInteger(p)&&Number.isSafeInteger(completion),"policy exact");const result=[n,p,completion];memo.set(k,result);return result;
  }
  return go(0,1,...w.prior);
 }
 function empty(){return {roots:0,rows:0,informative:0,correct:0,informative_correct:0,valid:0,root_correct:0,strict_roots:0,strict_correct:0,expected_utility_scaled:0,oracle_scaled:0,nominal_scaled:0,expected_probe_scaled:0,expected_complete_scaled:0,root_regret_scaled:0}}
 // Common exact denominator 4*16^5 for all roots and conditions.
 const DEN=4*scale(5);
 function units(n,w){const k=DEN/((w.prior[0]+w.prior[1])*scale(w.H));check(Number.isSafeInteger(k),"unit scale");return n*k}
 function add(a,w,rs,policy,run){
  const root=rs[0],choice=policy(root),ok=valid(root,choice)&&root.winners.includes(choice),strict=root.winners.length===1;
  a.roots++;a.root_correct+=Number(ok);a.strict_roots+=Number(strict);a.strict_correct+=Number(strict&&ok);
  a.expected_utility_scaled+=units(run[0],w);a.oracle_scaled+=units(root.max,w);a.nominal_scaled+=(3*w.H+w.B)*DEN;a.expected_probe_scaled+=units(run[1],w);a.expected_complete_scaled+=units(run[2],w);a.root_regret_scaled+=units(root.max-(valid(root,choice)?root.q[choice]:0),w);
  check(run[0]<=root.max&&run[1]<=(w.prior[0]+w.prior[1])*scale(w.H),"policy bound");
  for(const r of rs){const c=policy(r),v=valid(r,c),good=v&&r.winners.includes(c),info=r.range>0;a.rows++;a.informative+=Number(info);a.correct+=Number(good);a.informative_correct+=Number(good&&info);a.valid+=Number(v)}
  return {choice,ok,strict};
 }
 function finish(a){const div=(x,y)=>y?x/y:null;return {...a,expected_points:a.expected_utility_scaled/DEN,oracle_points:a.oracle_scaled/DEN,oracle_fraction:div(a.expected_utility_scaled,a.oracle_scaled),nominal_utility:div(a.expected_utility_scaled,a.nominal_scaled),root_accuracy:div(a.root_correct,a.roots),raw_accuracy:div(a.correct,a.rows),informative_accuracy:div(a.informative_correct,a.informative),strict_root_accuracy:div(a.strict_correct,a.strict_roots),expected_probe_rate:a.expected_probe_scaled/(DEN*a.roots),expected_completion_rate:a.expected_complete_scaled/(DEN*a.roots)}}
 function entropy(p){return p===0||p===1?0:-p*Math.log2(p)-(1-p)*Math.log2(1-p)}
 function info(w,t,e,x,y,a,sham=false){
  const b=branches(w,t,e,x,y,a,sham),p=b.v/(b.u+b.v);let h=0,varpost=0,chord=0;
  for(const z of b.out){const prob=z.mass/(16*(x+y)),q=z.y/(z.x+z.y);h+=prob*entropy(q);varpost+=prob*q*(1-q);chord+=prob*((Math.sqrt(p)-Math.sqrt(q))**2+(Math.sqrt(1-p)-Math.sqrt(1-q))**2)}
  return {entropy_gain:entropy(p)-h,variance_gain:p*(1-p)-varpost,expected_squared_chord:chord};
 }
 function experiment(seed=SEED,reps=REPS,submissions=null){
  const total={},groups={},tests={brute_roots:0,oracle_rollouts:0,sham_equals_no_probe:0,probe_monotonicity:0,blackwell_pairs:0,matched_prior_and_reactions:0,convex_q_checks:0},voi={roots:0,positive_probe_value:0,probe_value_scaled:0,passive_gain_scaled:0,passive_positive:0,strict_q_reversals:0,target_pairs:0,target_reversals:0,sham_root_reversals:0,prior_boundary_pairs:0,prior_boundary_reversals:0,prior_boundary_chord_sum:0,prior_boundary_chord_min:null,absolute_q_slope_sum:0,slope_checks:0,probe_entropy_gain:0,ordinary_entropy_gain:0,probe_variance_gain:0,ordinary_variance_gain:0,probe_squared_chord:0,ordinary_squared_chord:0,geometry_roots:0};
  const matched=new Map(),prevQ=new Map(),prevTarget=new Map(),seen=new Map(),dups=new Set();let roots=0,cells=0,malformed=0;
  if(submissions!==null)for(const s of submissions){if(!s||typeof s.id!=="string"){malformed++;continue}if(seen.has(s.id))dups.add(s.id);else seen.set(s.id,s)}
  for(const w of worlds(seed,reps)){
   roots++;cells=Math.max(cells,w.cell+1);
   const s=solve(w),np=solve(w,{no:true}),sh=solve(w,{sham:true}),rs=rows(w,s,np),root=rs[0],d=w.H,[x,y]=w.prior,den=(x+y)*scale(d),nr=np.value(0,1,x,y,d),sv=sh.value(0,1,x,y,d),sq=best(sh.scores(0,1,x,y,d));
   const g=groups[`H${w.H}_q${w.q}_f${w.f}`]??={};
   check(nr===sv,"sham must equal no-probe");tests.sham_equals_no_probe++;check(root.max>=nr,"probe value negative");tests.probe_monotonicity++;
   voi.roots++;voi.positive_probe_value+=Number(root.max>nr);voi.probe_value_scaled+=units(root.max-nr,w);
   voi.sham_root_reversals+=Number(root.winners.length===1&&sq.winners.length===1&&root.winners[0]!==sq.winners[0]);
   if(w.H===2||w.rep===0){check(Math.abs(root.max/den-brute(w,0,1,y/(x+y)))<1e-9,"independent brute");tests.brute_roots++}
   const tapeKey=[w.H,w.rep].join(":"),sig=JSON.stringify([w.prior,w.steps]);if(matched.has(tapeKey)){check(matched.get(tapeKey)===sig,"matched tapes");tests.matched_prior_and_reactions++}else matched.set(tapeKey,sig);
   const qKey=[w.H,w.f,w.B,w.rep,w.target].join(":"),old=prevQ.get(qKey);
   if(old){check(w.q===old.q+1&&root.max>=old.value,"Blackwell order");tests.blackwell_pairs++;voi.passive_gain_scaled+=units(root.max-old.value,w);voi.passive_positive+=Number(root.max>old.value);voi.strict_q_reversals+=Number(root.winners.length===1&&old.winners.length===1&&root.winners[0]!==old.winners[0])}
   prevQ.set(qKey,{q:w.q,value:root.max,winners:root.winners});
   const tk=[w.cell,w.rep].join(":");
   if(!w.target)prevTarget.set(tk,root.winners);else{const old=prevTarget.get(tk);voi.target_pairs++;voi.target_reversals+=Number(old.length===1&&root.winners.length===1&&old[0]!==root.winners[0]);prevTarget.delete(tk)}
   const priors=[[3,1],[1,1],[1,3]],qs=priors.map(([a,b])=>s.scores(0,1,a,b,d)),bs=qs.map(best);
   for(const a of Object.keys(qs[0])){check(4*qs[1][a]<=qs[0][a]+qs[2][a],"Q convexity");tests.convex_q_checks++;for(let i=0;i<2;i++){const l=qs[i][a]/((priors[i][0]+priors[i][1])*scale(d)),r=qs[i+1][a]/((priors[i+1][0]+priors[i+1][1])*scale(d));voi.absolute_q_slope_sum+=4*Math.abs(r-l);voi.slope_checks++}}
   for(let i=0;i<2;i++){voi.prior_boundary_pairs++;if(bs[i].winners.length===1&&bs[i+1].winners.length===1&&bs[i].winners[0]!==bs[i+1].winners[0]){const p=(i+1)/4,q=(i+2)/4,h=Math.hypot(Math.sqrt(p)-Math.sqrt(q),Math.sqrt(1-p)-Math.sqrt(1-q));voi.prior_boundary_reversals++;voi.prior_boundary_chord_sum+=h;voi.prior_boundary_chord_min=voi.prior_boundary_chord_min===null?h:Math.min(h,voi.prior_boundary_chord_min)}}
   // Both channels observe the identical post-work0 phase distribution.
   const a=info(w,0,1,x,y,"probe"),b=info(w,0,1,x,y,"work0");
   check(a.entropy_gain+1e-12>=b.entropy_gain&&a.variance_gain+1e-12>=b.variance_gain,"information ordering");
   voi.geometry_roots++;voi.probe_entropy_gain+=a.entropy_gain;voi.ordinary_entropy_gain+=b.entropy_gain;voi.probe_variance_gain+=a.variance_gain;voi.ordinary_variance_gain+=b.variance_gain;voi.probe_squared_chord+=a.expected_squared_chord;voi.ordinary_squared_chord+=b.expected_squared_chord;
   for(const m of submissions===null?modes:["submitted"]){
    const policy=m==="submitted"?r=>{const s=seen.get(r.id);return s&&!dups.has(r.id)&&Object.keys(s).sort().join(",")==="action,id"?s.action:null}:r=>r.controls[m];
    const run=evaluatePolicy(w,rs,policy);add(total[m]??=empty(),w,rs,policy,run);add(g[m]??=empty(),w,rs,policy,run);
    if(m==="oracle"){check(run[0]===root.max&&run[2]===den,"oracle eval");tests.oracle_rollouts++}
    if(m==="no_probe")check(run[0]===nr&&run[1]===0,"no probe eval");
   }
   if(submissions!==null)for(const r of rs)seen.delete(r.id);
  }
  const out={schema:"srg19.receipt.v1",seed,reps,cells,roots,exact_common_denominator:DEN,tests,voi,controls:Object.fromEntries(Object.entries(total).map(([m,a])=>[m,finish(a)])),groups:Object.fromEntries(Object.entries(groups).map(([k,v])=>[k,Object.fromEntries(Object.entries(v).map(([m,a])=>[m,finish(a)]))]))};
  if(submissions!==null)out.submission={malformed,duplicates:dups.size,unknown:seen.size};return out;
 }
 function sampled(w,t,z,e,a){const s=w.steps[t],nz=z^flip(w,t,a)^Number(s.noise[a]<w.f),q=a==="probe"?4:w.q,o=nz^Number(s.obs[a]>=q),ne=e-Number(a==="probe"),reward=running(w,t,z,a)+(t===w.H-1&&nz===w.target?w.B:0);return{z:nz,e:ne,o:t===w.H-1?-1:o,reward}}
 function initial(w){return Number(w.initialWord<w.p)}
 function swmd(w){
  const L=["# SWMD-SRG/2","id: SRG19-belief-chain","title: \"Noisy cargo chain\"","about: \"Hidden phase and public signals.\"","start: p0","turn-base: 0","tie: first","direct: strict",`VAR cargo.mode = ${initial(w)} | hidden`,"VAR cargo.credit = 1 | public","VAR cargo.signal = -1 | public","VAR cargo.score = 0 | hidden"];
  L.push("SPOOL chain | A:TRUE | E:"+Array.from({length:w.H+1},(_,i)=>"p"+i).join(","));
  for(let t=0;t<=w.H;t++){
   L.push(`ENC p${t} turn=${t}..${t} | I:${t} | A:TRUE | Q:C(0) | N:"Noisy cargo chain" | T:${JSON.stringify(t===w.H?"Complete":JSON.stringify({b:w.steps[t].b,flip:w.steps[t].flip,r0:w.steps[t].r0,r1:w.steps[t].r1,f:w.f,q:w.q,target:w.target,B:w.B,prior:w.prior}))}`);
   if(t===w.H)break;
   for(const a of w.steps[t].order){
    const id=`a${t}_${a}`;L.push(`OPT ${id} | V:TRUE | P:${a==="probe"?"EQ(P(cargo.credit),C(1))":"TRUE"} | T:${JSON.stringify(a)}`);
    for(const z of [0,1])for(const e of [0,1]){
     if(!legal(w,t,e).includes(a))continue;
     const n=sampled(w,t,z,e,a),g=`AND(EQ(P(cargo.mode),C(${z})),EQ(P(cargo.credit),C(${e})))`,writes=[`SET cargo.mode = C(${n.z})`,`SET cargo.credit = C(${n.e})`,`SET cargo.signal = C(${n.o})`,`SET cargo.score = ADD(P(cargo.score),C(${n.reward/32}))`];
     L.push(`ORX ${id}/rx_${id}_${z}_${e} -> p${t+1} | E:${writes.join("; ")} | D:C(0) | G:${g} | T:"Reaction executed."`);
    }
   }
  }return L.join("\n")+"\n";
 }
 function runtimeCheck(api,seed=SEED){
  let fixtures=0,states=0,transitions=0,terminal=0,posterior_support=0;
  for(const base of bases(seed,1)){
   const w={...base,target:0},compiled=api.compileV2(swmd(w));fixtures++;
   let front=[{s:api.initialV2(compiled),z:initial(w),e:1,o:-1,earned:0,x:w.prior[0],y:w.prior[1]}];
   for(let t=0;t<w.H;t++){
    const next=new Map();
    for(const {s,z,e,o,earned,x,y} of front){
     states++;const obs=api.observeV2(compiled,s),acts=legal(w,t,e);check(obs.status==="decision"&&obs.turn===t&&Object.keys(obs.values).length===2&&obs.values["cargo.credit"]===e&&obs.values["cargo.signal"]===o,"public observation");
     check(JSON.stringify(obs.actions.map(a=>a.id))===JSON.stringify(acts.map(a=>`a${t}_${a}`)),"menu");
     for(const a of acts){
      const n=sampled(w,t,z,e,a),ns=api.stepV2(compiled,s,`a${t}_${a}`).next,ne=earned+n.reward;transitions++;
      check(ns.values["cargo.mode"]===n.z&&ns.values["cargo.credit"]===n.e&&ns.values["cargo.signal"]===n.o&&ns.values["cargo.score"]*32===ne,"tape transition");
      if(t===w.H-1){check(api.observeV2(compiled,ns).status==="terminal","terminal");terminal++;continue}
      const b=branches(w,t,e,x,y,a).out.find(v=>v.o===n.o);check(b&&(n.z?b.y:b.x)>0,"posterior support");posterior_support++;
      const k=[n.z,n.e,n.o,b.x,b.y].join(":");if(!next.has(k))next.set(k,{s:ns,...n,earned:ne,x:b.x,y:b.y});
     }
    }front=[...next.values()];
   }
  }return {fixtures,states,transitions,terminal,posterior_support};
 }
 function scorerCheck(seed=SEED){
  const all=Array.from(worlds(seed,1)).flatMap(w=>rows(w).map(r=>({id:r.id,action:r.controls.oracle}))),id=all[0].id;
  const missing=experiment(seed,1,[]),bad=experiment(seed,1,[null,{id,action:all[0].action},{id,action:all[0].action},{id:all[1].id,action:"illegal"},{id:all[2].id,action:["work0"]},{id:"unknown",action:"work0"}]);
  check(missing.controls.submitted.valid===0&&missing.controls.submitted.expected_utility_scaled===0&&missing.controls.submitted.expected_complete_scaled===0,"missing");
  check(bad.controls.submitted.valid===0&&bad.submission.duplicates===1&&bad.submission.unknown===1&&bad.submission.malformed===1,"malformed");
  const full=experiment(seed,1,all);check(full.controls.submitted.expected_utility_scaled===full.controls.submitted.oracle_scaled&&full.controls.submitted.correct===full.controls.submitted.rows,"submitted oracle");
  return {missing:"pass",malformed:"pass",submitted_oracle:"pass",oracle_submissions:all.length};
 }
 return {SEED,REPS,grid,modes,worlds,rows,experiment,swmd,runtimeCheck,scorerCheck};
}
export const {SEED,REPS,grid,modes,worlds,rows,experiment,swmd,runtimeCheck,scorerCheck}=core();
