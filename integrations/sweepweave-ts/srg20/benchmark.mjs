function core(){
 const check=(v,m)=>{if(!v)throw Error("SRG20: "+m)},SEED=0x53522001,REPS=8,L=4,S=256,DEN=64*S**4;
 const modes=["first","direct","d1","d2","d3","last","factor","oracle"],actions=["route0","route1","delegate"];
 const parity=x=>{x^=x>>>16;x^=x>>>8;x^=x>>>4;return (0x6996>>>(x&15))&1};
 function gcd(a,b){while(b){const c=a%b;a=b;b=c}return a}
 function rng(seed){let x=seed>>>0||1;return n=>{const lim=Math.floor(4294967296/n)*n;do{x^=x<<13;x^=x>>>17;x^=x<<5}while((x>>>0)>=lim);return (x>>>0)%n}}
 function tape(seed,rep){const r=rng((seed^Math.imul(rep+1,0x9e3779b9))>>>0);return{latent:r(64),agents:Array.from({length:4},()=>({first:r(65536),third:r(65536),fourth:r(65536),flag:r(2),words:Array.from({length:4},()=>r(4))}))}}
 function* worlds(seed=SEED,reps=REPS){
  check(Number.isInteger(seed)&&seed>0&&seed<=0xffffffff&&Number.isInteger(reps)&&reps>=1&&reps<=256,"seed/reps");let cell=0;
  for(const K of [2,4,6])for(const R of [...new Set([2,K])])for(const D of [1,2,3])for(const fee of [0,1,2])for(const profile of ["equal","late"]){
   for(let rep=0;rep<reps;rep++){
    const t=tape(seed,rep),W=1<<K,target=(1<<R)-1;
    const agents=t.agents.slice(0,D+1).map((a,i)=>{const mask=1+a.first%target;return{masks:[mask,mask,i>=2?target:1+a.third%target,i>=1&&a.flag?target:1+a.fourth%target],q:profile==="late"&&i>=2?4:3,words:a.words}});
    yield{K,R,D,fee,profile,rep,cell,W,target,agents,latent:t.latent&(W-1),id:`c${cell}r${rep}`};
   }cell++;
  }
 }
 function rank(masks){const piv=Array(6).fill(0);let r=0;for(let m of masks){for(let j=5;j>=0&&m;j--)if(m&(1<<j)){if(piv[j])m^=piv[j];else{piv[j]=m;r++;break}}}return r}
 function weights(w,i,h){const a=w.agents[i];return Array.from({length:w.W},(_,x)=>{let v=1;for(let j=0;j<L;j++)v*=parity(x&a.masks[j])===((h>>>j)&1)?a.q:4-a.q;return v})}
 const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),sum=a=>a.reduce((s,x)=>s+x,0);
 function best(q){const max=Math.max(...Object.values(q)),winners=Object.keys(q).filter(a=>q[a]===max);return{max,winners,range:max-Math.min(...Object.values(q))}}
 function qvalues(w,i,last,weights0,successor){
  const scale=S**(last-i),q={route0:0,route1:0};
  for(let x=0;x<w.W;x++)q[`route${parity(x&w.target)}`]+=weights0[x]*8*scale;
  if(i<last)q.delegate=dot(weights0,successor)-w.fee*scale*sum(weights0);
  for(const v of Object.values(q))check(Number.isSafeInteger(v),"integer Q");return q;
 }
 function model(w,last=w.D){
  const levels=[];let successor=null,likelihoodChecks=0;
  for(let i=last;i>=0;i--){
   const u=Array(w.W).fill(0),rows=[],mass=Array(w.W).fill(0),scale=S**(last-i);
   for(let h=0;h<16;h++){
    const l=weights(w,i,h),m=sum(l);for(let x=0;x<w.W;x++)mass[x]+=l[x];if(!m)continue;
    const q=qvalues(w,i,last,l,successor),b=best(q),a=b.winners[0];rows.push({h,l,m,q,...b,a});
    for(let x=0;x<w.W;x++)u[x]+=l[x]*(a==="delegate"?successor[x]-w.fee*scale:Number(parity(x&w.target)===Number(a.at(-1)))*8*scale);
   }
   for(let x=0;x<w.W;x++){check(mass[x]===S,"history mass");check(Number.isSafeInteger(u[x]),"conditional integer");likelihoodChecks++}
   check(sum(u)===sum(rows.map(r=>r.max)),"utility recurrence");
   levels[i]={u,rows,policy:new Map(rows.map(r=>[r.h,r.a]))};successor=u;
  }return{levels,likelihoodChecks,last};
 }
 function distribution(l){const m=sum(l);check(m>0,"zero posterior");return l.map(x=>x/m)}
 function lastPosterior(w,h){const a=w.agents[0];return distribution(Array.from({length:w.W},(_,x)=>parity(x&a.masks[L-1])===((h>>>(L-1))&1)?a.q:4-a.q))}
 function factorPosterior(w,p){const b=Array.from({length:w.K},(_,j)=>sum(p.map((v,x)=>((x>>>j)&1)*v)));return Array.from({length:w.W},(_,x)=>b.reduce((v,t,j)=>v*(((x>>>j)&1)?t:1-t),1))}
 function approximateChoice(w,p,successor){
  const sc=S**w.D,q={route0:0,route1:0,delegate:dot(p,successor)/sc-w.fee};
  for(let x=0;x<w.W;x++)q[`route${parity(x&w.target)}`]+=8*p[x];
  const hi=Math.max(...Object.values(q));return actions.find(a=>q[a]>=hi-1e-12);
 }
 function publicRules(w){return{hidden_bits:w.K,target_mask:w.target,prior:"uniform over integers 0..2^K-1",fee:w.fee,route_correct_points:8,agents:w.agents.map(({masks,q})=>({masks,precision_quarters:q})),delegation_links:w.D}}
 function task(w,r,kind){
  const id=`${w.id}h${r.h}`,history=Array.from({length:L},(_,j)=>(r.h>>>j)&1),common="The hidden K-bit integer is uniform. Its target is XOR parity of the bits selected by target_mask. Each agent sees four private parity observations of its public masks, independently correct with probability precision_quarters/4 conditional on the hidden integer. Each agent precommits to a policy maximizing expected points using only its own history. A route earns 8 iff its route bit equals target, otherwise zero. Delegating subtracts fee and uses the next agent's fixed policy (including any later delegation). Successors never observe earlier histories or selection. Last agent must route; ties use route0, route1, delegate order. You are A0. All masks index bits by ordinary integer bit operations.";
  if(kind==="inference")return{id,kind:"storyworld_inference",goal:"Infer the posterior of the hidden integer from A0's evidence.",task:common+" Return JSON with probabilities in integer-state order, summing to one.",rules:publicRules(w),observation:{history},output_contract:"Return probabilities as an array of length 2^K."};
  return{id,kind:"storyworld_policy",goal:"Maximize expected net route points.",task:common+(kind==="posterior"?" The exact posterior masses of A0 are supplied.":" Your four observations are supplied in mask order.")+" Return one legal action ID.",action_budget:w.D+1,root_horizon:w.D+1,rules:publicRules(w),observation:{encounter:"agent0",turn:0,status:"decision",values:kind==="posterior"?{posterior_masses:r.l}:{history},actions:actions.map(id=>({id,text:{route0:"Choose route zero",route1:"Choose route one",delegate:"Delegate to next agent"}[id]}))},output_contract:"Return one legal action ID."};
 }
 function rows(w,includeTask=false){
  const full=model(w),models=Array.from({length:3},(_,i)=>i+1>=w.D?full:model(w,i+1)),successor=full.levels[1].u,root=full.levels[0].rows;
  const out=root.map(r=>{
   const p=distribution(r.l),last=lastPosterior(w,r.h),factor=factorPosterior(w,p),direct=best({route0:r.q.route0,route1:r.q.route1}).winners[0],controls={first:"route0",direct,oracle:r.a,last:approximateChoice(w,last,successor),factor:approximateChoice(w,factor,successor)};
   for(let i=0;i<3;i++)controls[`d${i+1}`]=models[i].levels[0].policy.get(r.h);
   const rr={...r,id:`${w.id}h${r.h}`,p,last,factor,controls};
   if(includeTask)for(const k of ["history","posterior","inference"])rr[k]=task(w,r,k);
   return rr;
  });
  return{rows:out,full,models};
 }
 function explicit(w,levels,i,x){
  // Independent history enumeration conditional on a fixed latent state.
  let v=0;for(let h=0;h<16;h++){
   let prob=1;const a=w.agents[i];for(let j=0;j<4;j++){const match=parity(x&a.masks[j])===((h>>>j)&1);prob*=match?a.q/4:1-a.q/4}
   if(!prob)continue;const action=levels[i].policy.get(h);
   v+=prob*(action==="delegate"?explicit(w,levels,i+1,x)-w.fee:Number(parity(x&w.target)===Number(action.at(-1)))*8);
  }return v;
 }
 function geometry(w,rs){
  const mass=rs.map(r=>r.m/(w.W*S)),features=rs.map(r=>r.p.map(Math.sqrt)),mean=Array(w.W).fill(0);
  for(let i=0;i<rs.length;i++)for(let x=0;x<w.W;x++)mean[x]+=mass[i]*features[i][x];
  const centered=features.map(f=>f.map((v,x)=>v-mean[x]));
  const tr=sum(centered.map((f,i)=>mass[i]*dot(f,f)));let tr2=0;
  for(let i=0;i<rs.length;i++)for(let j=0;j<rs.length;j++)tr2+=mass[i]*mass[j]*dot(centered[i],centered[j])**2;
  const cls=new Set(rs.map(r=>{const g=r.l.reduce(gcd,0);return r.l.map(v=>v/g).join(",")}));
  const entropy=sum(rs.map((r,i)=>mass[i]*-sum(r.p.map(p=>p?p*Math.log2(p):0))));
  return{root_rank:rank(w.agents[0].masks),union_rank:rank(w.agents.flatMap(a=>a.masks)),target_in_root_span:Number(rank([...w.agents[0].masks,w.target])===rank(w.agents[0].masks)),classes:cls.size,entropy_bits:entropy,perplexity:2**entropy,participation_ratio:tr2>1e-24?tr*tr/tr2:0};
 }
 function err(w,p,q){let tv=0,hell=0,target=0;for(let x=0;x<w.W;x++){tv+=Math.abs(p[x]-q[x]);hell+=Math.sqrt(p[x]*q[x]);if(parity(x&w.target))target+=p[x]-q[x]}return{tv:tv/2,hellinger2:Math.max(0,1-hell),target_abs:Math.abs(target)}}
 function empty(){return{worlds:0,rows:0,informative:0,strict:0,correct:0,informative_correct:0,strict_correct:0,valid:0,weighted_correct:0,weighted_informative:0,weighted_informative_correct:0,weighted_strict:0,weighted_strict_correct:0,weighted_valid:0,expected_utility_scaled:0,oracle_scaled:0,delegation_mass:0}}
 function add(a,w,rs,policy){
  a.worlds++;let util=0;const d=DEN/(w.W*S**(w.D+1));
  for(const r of rs){const action=policy(r),v=typeof action==="string"&&Object.hasOwn(r.q,action),ok=v&&r.winners.includes(action),info=r.range>0,strict=r.winners.length===1,m=r.m*DEN/(w.W*S);
   a.rows++;a.informative+=Number(info);a.strict+=Number(strict);a.correct+=Number(ok);a.informative_correct+=Number(info&&ok);a.strict_correct+=Number(strict&&ok);a.valid+=Number(v);a.weighted_correct+=ok?m:0;a.weighted_informative+=info?m:0;a.weighted_informative_correct+=info&&ok?m:0;a.weighted_strict+=strict?m:0;a.weighted_strict_correct+=strict&&ok?m:0;a.weighted_valid+=v?m:0;a.delegation_mass+=v&&action==="delegate"?m:0;
   const value=v?r.q[action]:0;util+=value*d;a.expected_utility_scaled+=value*d;a.oracle_scaled+=r.max*d;check(Number.isSafeInteger(a.expected_utility_scaled)&&Number.isSafeInteger(a.oracle_scaled),"aggregate exact");
  }return util;
 }
 function finish(a){const div=(x,y)=>y?x/y:null;return{...a,expected_points:a.expected_utility_scaled/DEN,expected_points_per_world:a.expected_utility_scaled/(DEN*a.worlds),oracle_fraction:div(a.expected_utility_scaled,a.oracle_scaled),mean_regret:(a.oracle_scaled-a.expected_utility_scaled)/(DEN*a.worlds),raw_accuracy:div(a.correct,a.rows),informative_accuracy:div(a.informative_correct,a.informative),weighted_accuracy:a.weighted_correct/(DEN*a.worlds),weighted_informative_accuracy:div(a.weighted_informative_correct,a.weighted_informative),weighted_strict_accuracy:div(a.weighted_strict_correct,a.weighted_strict),coverage:a.weighted_valid/(DEN*a.worlds),delegation_rate:a.delegation_mass/(DEN*a.worlds)}}
 function experiment(seed=SEED,reps=REPS,submissions=null,kind="policy"){
  const total={},groups={},geo={},inf={},pairs={eligible:0,conflicting_pairs:0,all_same_last:0,controls:{}},tests={likelihood_checks:0,oracle_worlds:0,explicit_conditional:0,explicit_root_actions:0,padding_worlds:0,history_permutation:0,direct_lower_bound:0,matched_parameters:0};
  const seen=new Map(),dups=new Set(),matched=new Map(),padding=new Map();let malformed=0,cells=0,nworlds=0,conflictRows=0,conflictMass=0,strictDepthReversals=0,positiveDelegationWorlds=0;const infModes=kind==="inference"?["submitted"]:["last","factor"];
  if(submissions!==null)for(const s of submissions){if(!s||typeof s.id!=="string"){malformed++;continue}if(seen.has(s.id))dups.add(s.id);else seen.set(s.id,s)}
  for(const w of worlds(seed,reps)){
   nworlds++;cells=Math.max(cells,w.cell+1);const result=rows(w),rs=result.rows,full=result.full,successor=full.levels[1].u,groupKey=`K${w.K}_R${w.R}_D${w.D}_fee${w.fee}_${w.profile}`,g=groups[groupKey]??={},z=geometry(w,rs),gz=geo[groupKey]??={worlds:0,root_rank:0,union_rank:0,target_in_root_span:0,classes:0,entropy_bits:0,perplexity:0,participation_ratio:0};
   gz.worlds++;for(const [k,v] of Object.entries(z))gz[k]+=v;
   tests.likelihood_checks+=full.likelihoodChecks+result.models.filter((m,i)=>m!==full&&result.models.indexOf(m)===i).reduce((s,m)=>s+m.likelihoodChecks,0);
   const oracle=sum(rs.map(r=>r.max)),direct=sum(rs.map(r=>Math.max(r.q.route0,r.q.route1)));check(oracle>=direct,"direct lower bound");tests.direct_lower_bound++;positiveDelegationWorlds+=Number(oracle>direct);
   const signature=JSON.stringify(w.agents.map(({masks,words})=>({masks,words}))),matchKey=[w.K,w.R,w.D,w.rep].join(":");if(matched.has(matchKey)){check(matched.get(matchKey)===signature,"matched parameters");tests.matched_parameters++}else matched.set(matchKey,signature);
   if(w.R===2){const key=[w.D,w.fee,w.profile,w.rep].join(":"),signature=JSON.stringify(rs.map(r=>[r.h,r.m/w.W,Object.values(r.q).map(x=>x/w.W),r.winners,r.controls]));if(padding.has(key)){check(padding.get(key)===signature,"padding");tests.padding_worlds++}else padding.set(key,signature)}
   if(w.K===2&&w.rep===0&&w.fee===1){
    for(let x=0;x<w.W;x++){const value=explicit(w,full.levels,1,x);check(value===successor[x]/S**w.D,"explicit conditional");tests.explicit_conditional++;
     check(explicit(w,full.levels,0,x)===full.levels[0].u[x]/S**(w.D+1),"explicit root conditional");tests.explicit_conditional++}
    for(const r of rs)for(const a of actions){let v=0;for(let x=0;x<w.W;x++)v+=r.l[x]*(a==="delegate"?explicit(w,full.levels,1,x)-w.fee:Number(parity(x&w.target)===Number(a.at(-1)))*8);
     check(v*S**w.D===r.q[a],"explicit root action");tests.explicit_root_actions++}
   }
   for(const r of rs){
    const swapped=(r.h&12)|((r.h&1)<<1)|((r.h&2)>>>1);check(weights(w,0,swapped).every((v,x)=>v===r.l[x]),"repeat evidence order");tests.history_permutation++;
    if(((r.h&1)^((r.h>>>1)&1))!==0){conflictRows++;conflictMass+=r.m/(w.W*S)}
    strictDepthReversals+=Number(r.winners.length===1&&r.controls.d1!==r.a&&w.D>=2);
    for(const m of infModes){
     const a=inf[m]??={weighted_mass:0,tv:0,hellinger2:0,target_abs:0,valid:0,rows:0},mass=r.m/(w.W*S);let p=r[m];
     if(m==="submitted"){const s=seen.get(r.id);p=s&&!dups.has(r.id)&&Object.keys(s).sort().join(",")==="id,probabilities"?s.probabilities:null}
     const v=Array.isArray(p)&&p.length===w.W&&p.every(x=>typeof x==="number"&&Number.isFinite(x)&&x>=0)&&Math.abs(sum(p)-1)<=1e-8;
     a.rows++;if(v){a.valid++;a.weighted_mass+=mass;const e=err(w,r.p,distribution(p));for(const k of ["tv","hellinger2","target_abs"])a[k]+=mass*e[k]}
    }
   }
   const policyFor=m=>m==="submitted"?r=>{const s=seen.get(r.id);return s&&!dups.has(r.id)&&Object.keys(s).sort().join(",")==="action,id"?s.action:null}:r=>r.controls[m];
   const chosen=submissions===null?modes:kind==="inference"?[]:["submitted"];
   for(const m of chosen){const policy=policyFor(m),u=add(total[m]??=empty(),w,rs,policy);add(g[m]??=empty(),w,rs,policy);if(m==="oracle"){check(u===oracle*DEN/(w.W*S**(w.D+1)),"oracle exact");tests.oracle_worlds++}}
   for(let i=0;i<rs.length;i++)for(let j=i+1;j<rs.length;j++){
    const a=rs[i],b=rs[j];if((a.h>>>3)!==(b.h>>>3))continue;pairs.all_same_last++;if(a.winners.length!==1||b.winners.length!==1||a.a===b.a)continue;pairs.eligible++;pairs.conflicting_pairs+=Number(((a.h&1)^((a.h>>>1)&1))!==((b.h&1)^((b.h>>>1)&1)));
    for(const m of chosen){const v=pairs.controls[m]??={both_correct:0,individual_correct:0,same_action:0},p=policyFor(m),x=p(a),y=p(b);v.both_correct+=Number(x===a.a&&y===b.a);v.individual_correct+=Number(x===a.a)+Number(y===b.a);v.same_action+=Number(x===y)}
   }
   if(submissions!==null)for(const r of rs)seen.delete(r.id);
  }
  const inference=Object.fromEntries(Object.entries(inf).map(([m,a])=>[m,{...a,mean_tv:a.weighted_mass?a.tv/a.weighted_mass:null,mean_hellinger2:a.weighted_mass?a.hellinger2/a.weighted_mass:null,mean_target_abs:a.weighted_mass?a.target_abs/a.weighted_mass:null,coverage:a.weighted_mass/nworlds}]));
  const out={schema:"srg20.receipt.v1",seed,reps,cells,worlds:nworlds,exact_common_denominator:DEN,tests,conflictRows,conflictMass,strictDepthReversals,positiveDelegationWorlds,controls:Object.fromEntries(Object.entries(total).map(([m,a])=>[m,finish(a)])),groups:Object.fromEntries(Object.entries(groups).map(([k,v])=>[k,Object.fromEntries(Object.entries(v).map(([m,a])=>[m,finish(a)]))])),geometry:geo,inference,pairs};
  if(submissions!==null)out.submission={unknown:seen.size,malformed,duplicates:dups.size};return out;
 }
 function sampledHistory(w,i){const a=w.agents[i];return a.masks.reduce((h,m,j)=>h|((parity(w.latent&m)^Number(a.words[j]>=a.q))<<j),0)}
 function swmd(w){
  const L=["# SWMD-SRG/2","id: SRG20-delegation","title: \"Private cargo reports\"","about: \"Delegate or route using the active agent's evidence.\"","start: p0","turn-base: 0","tie: first","direct: strict",`VAR cargo.target = ${parity(w.latent&w.target)} | hidden`,"VAR cargo.score = 0 | hidden","VAR cargo.actor = 0 | public"];
  const hs=w.agents.map((_,i)=>sampledHistory(w,i));
  for(let j=0;j<4;j++){L.push(`VAR signal.bit${j} = ${(hs[0]>>>j)&1} | public`);for(let i=1;i<=w.D;i++)L.push(`VAR private.a${i}bit${j} = ${(hs[i]>>>j)&1} | hidden`)}
  const pages=Array.from({length:w.D+1},(_,i)=>[`p${i}`,`done${i}`]).flat();L.push("SPOOL chain | A:TRUE | E:"+pages.join(","));
  for(let i=0;i<=w.D;i++){
   L.push(`ENC p${i} turn=${i}..${i} | I:${i} | A:TRUE | Q:C(0) | N:"Active agent" | T:${JSON.stringify(JSON.stringify({rules:publicRules(w),actor:i}))}`);
   for(const a of i===w.D?actions.slice(0,2):actions){
    const id=`a${i}_${a}`;L.push(`OPT ${id} | V:TRUE | P:TRUE | T:${JSON.stringify(a)}`);
    if(a==="delegate"){
     const writes=[`SET cargo.score = ADD(P(cargo.score),C(${-w.fee/16}))`,`SET cargo.actor = C(${(i+1)/4})`,...Array.from({length:4},(_,j)=>`SET signal.bit${j} = P(private.a${i+1}bit${j})`)];
     L.push(`ORX ${id}/rx_${id} -> p${i+1} | E:${writes.join("; ")} | D:C(0) | G:TRUE | T:"Delegated."`);
    }else for(const win of [0,1]){
     const eq=`EQ(P(cargo.target),C(${a.at(-1)}))`;
     L.push(`ORX ${id}/rx_${id}_${win} -> done${i} | E:SET cargo.score = ADD(P(cargo.score),C(${win/2})) | D:C(0) | G:${win?eq:`NOT(${eq})`} | T:"Route executed."`);
    }
   }
   L.push(`ENC done${i} turn=${i+1}..${i+1} | I:${i+1} | A:TRUE | Q:C(0) | N:"Complete" | T:"Shift complete."`);
  }return L.join("\n")+"\n";
 }
 function runtimeCheck(api,seed=SEED){
  let fixtures=0,states=0,transitions=0,terminal=0,oraclePaths=0;
  for(const w of worlds(seed,1)){
   const compiled=api.compileV2(swmd(w)),full=model(w);fixtures++;
   let s=api.initialV2(compiled),oracleActive=true,oracleScore=0;
   for(let i=0;i<=w.D;i++){
    states++;const o=api.observeV2(compiled,s),h=sampledHistory(w,i),acts=i===w.D?actions.slice(0,2):actions;
    check(o.status==="decision"&&o.turn===i&&Object.keys(o.values).length===5&&o.values["cargo.actor"]*4===i,"active view");
    for(let j=0;j<4;j++)check(o.values[`signal.bit${j}`]===((h>>>j)&1),"private history projection");
    check(JSON.stringify(o.actions.map(a=>a.id))===JSON.stringify(acts.map(a=>`a${i}_${a}`)),"runtime legal");
    const chosen=full.levels[i].policy.get(h);check(chosen!==undefined,"sample support");
    let next=null;
    for(const a of acts){
     const ns=api.stepV2(compiled,s,`a${i}_${a}`).next;transitions++;
     const expected=-i*w.fee+(a==="delegate"?-w.fee:Number(parity(w.latent&w.target)===Number(a.at(-1)))*8);
     check(ns.values["cargo.score"]*16===expected,"runtime payoff");
     if(a==="delegate")next=ns;else{check(api.observeV2(compiled,ns).status==="terminal","terminal");terminal++}
     if(oracleActive&&a===chosen&&a!=="delegate"){oracleScore=expected;oracleActive=false;oraclePaths++}
    }
    if(i<w.D)s=next;
   }check(!oracleActive&&Number.isInteger(oracleScore),"oracle path");
  }return{fixtures,states,transitions,terminal,oraclePaths};
 }
 function scorerCheck(seed=SEED){
  const all=Array.from(worlds(seed,1)).flatMap(w=>rows(w).rows.map(r=>({id:r.id,action:r.a}))),id=all[0].id;
  const missing=experiment(seed,1,[]),bad=experiment(seed,1,[null,{id,action:all[0].action},{id,action:all[0].action},{id:all[1].id,action:"illegal"},{id:all[2].id,action:["route0"]},{id:"unknown",action:"route0"}]);
  check(missing.controls.submitted.valid===0&&missing.controls.submitted.expected_utility_scaled===0,"missing");
  check(bad.controls.submitted.valid===0&&bad.submission.duplicates===1&&bad.submission.unknown===1&&bad.submission.malformed===1,"malformed");
  const full=experiment(seed,1,all);check(full.controls.submitted.expected_utility_scaled===full.controls.submitted.oracle_scaled&&full.controls.submitted.correct===full.controls.submitted.rows,"submitted oracle");
  const probs=Array.from(worlds(seed,1)).flatMap(w=>rows(w).rows.map(r=>({id:r.id,probabilities:r.p}))),pi=experiment(seed,1,probs,"inference");
  check(Math.abs(pi.inference.submitted.coverage-1)<1e-10&&pi.inference.submitted.mean_tv<1e-12,"inference scorer");
  const invalid=experiment(seed,1,[{id,probabilities:[1]}],"inference");check(invalid.inference.submitted.valid===0&&invalid.inference.submitted.mean_tv===null,"inference invalid");
  return{missing:"pass",malformed:"pass",submitted_oracle:"pass",inference:"pass",oracle_submissions:all.length};
 }
 return{SEED,REPS,modes,worlds,rows,experiment,swmd,runtimeCheck,scorerCheck};
}
export const {SEED,REPS,modes,worlds,rows,experiment,swmd,runtimeCheck,scorerCheck}=core();
