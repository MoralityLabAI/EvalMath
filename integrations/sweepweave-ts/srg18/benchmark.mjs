function core(){
 const check=(x,m)=>{if(!x)throw Error("SRG18: "+m)},SEED=0x53521801,REPS=16;
 const names=["collect","switch","recharge"],modes=["first","d1","d2","d4","terminal","oracle"];
 const grid={H:[2,4,6,8],W:[2,4,8],C:[1,2],B:[6,12]};
 function rng(seed){let x=seed>>>0||1;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0}}
 function order(keys,n){return Array.from({length:n},(_,i)=>i).sort((a,b)=>keys[a]-keys[b]||a-b)}
 function tape(seed,rep){const rand=rng((seed^Math.imul(rep+1,0x9e3779b9))>>>0);return {initial:rand(),steps:Array.from({length:8},()=>({maps:names.map(()=>Array.from({length:8},rand)),rewards:Array.from({length:8},rand),order:order(names.map(rand),3).map(i=>names[i])}))}}
 function* bases(seed=SEED,reps=REPS){
  check(Number.isInteger(seed)&&seed>0&&seed<=0xffffffff&&Number.isInteger(reps)&&reps>=1&&reps<=256,"seed/reps");
  let cell=0;for(const H of grid.H)for(const W of grid.W)for(const C of grid.C)for(const B of grid.B){
   for(let rep=0;rep<reps;rep++){const t=tape(seed,rep);yield {H,W,C,B,rep,cell,id:`c${cell}r${rep}`,initial:t.initial%W,steps:t.steps.slice(0,H).map(s=>({order:s.order,maps:Object.fromEntries(names.map((a,i)=>[a,order(s.maps[i],W)])),rewards:s.rewards.slice(0,W).map(x=>1+x%3)}))}}
   cell++;
  }
 }
 function legal(w,t,e){return w.steps[t].order.filter(a=>a==="collect"||a==="switch"&&e>0||a==="recharge"&&e<w.C)}
 function step(w,t,m,e,a,cut=-1){
  check(legal(w,t,e).includes(a),"illegal action");
  const nm=t===cut?m:w.steps[t].maps[a][m],ne=e+Number(a==="recharge")-Number(a==="switch");
  const running=a==="collect"?w.steps[t].rewards[m]:0,terminal=t===w.H-1&&nm===w.target&&ne>0?w.B:0;
  return {m:nm,e:ne,running,terminal,reward:running+terminal};
 }
 function solve(w,cut=-1,terminalOnly=false){
  const memo=new Map();
  function val(t,m,e,d){if(t===w.H||d===0)return 0;const k=[t,m,e,d].join(":");if(memo.has(k))return memo.get(k);const v=Math.max(...Object.values(q(t,m,e,d)));memo.set(k,v);return v}
  function q(t,m,e,d){return Object.fromEntries(legal(w,t,e).map(a=>{const n=step(w,t,m,e,a,cut);return[a,(terminalOnly?n.terminal:n.reward)+val(t+1,n.m,n.e,d-1)]}))}
  return {q,val};
 }
 function best(q){const max=Math.max(...Object.values(q)),winners=Object.keys(q).filter(a=>q[a]===max);return{max,winners,range:max-Math.min(...Object.values(q)),margin:winners.length===1?max-Math.max(...Object.values(q).filter(v=>v!==max)):0}}
 function brute(w,t,m,e){
  if(t===w.H)return 0;
  let hi=-1;for(const a of names){if(a==="switch"&&e===0||a==="recharge"&&e===w.C)continue;
   const phase=w.steps[t].maps[a][m],energy=a==="collect"?e:a==="switch"?e-1:e+1,points=(a==="collect"?w.steps[t].rewards[m]:0)+(t+1===w.H&&phase===w.target&&energy>=1?w.B:0);
   hi=Math.max(hi,points+brute(w,t+1,phase,energy));
  }return hi;
 }
 function* worlds(seed=SEED,reps=REPS){for(const b of bases(seed,reps))for(let target=0;target<b.W;target++)yield {...b,target,id:`${b.id}g${target}`}}
 function rows(w,s=solve(w),term=solve(w,-1,true),includeTask=false){
  const out=[],front=[[w.initial,1]];let states=front;
  for(let t=0;t<w.H;t++){
   const next=new Map();
   for(const [m,e] of states){
    const q=s.q(t,m,e,w.H-t),b=best(q),id=`${w.id}t${t}m${m}e${e}`;
    const controls={first:Object.keys(q)[0],oracle:b.winners[0],terminal:best(term.q(t,m,e,w.H-t)).winners[0]};
    for(const d of [1,2,4])controls[`d${d}`]=best(s.q(t,m,e,Math.min(d,w.H-t))).winners[0];
    const row={id,t,m,e,q,...b,controls};
    if(includeTask)row.task={id,kind:"storyworld_policy",goal:"Maximize total points by the end of the shift.",task:"At each turn choose a legal reaction. Each reaction maps the current mode through that turn's public table. Collect earns the listed points for the mode BEFORE the reaction, and leaves energy unchanged. Switch spends one energy and earns zero running points. Recharge adds one energy and earns zero running points. Switch is legal when energy is positive, recharge when energy is below the cap, collect always. After the final reaction, earn the terminal bonus if the new mode equals the target and the new energy is positive. The entire table is public and deterministic. Arrays are indexed from zero. Return one legal action ID.",action_budget:w.H-t,root_horizon:w.H,rules:{H:w.H,width:w.W,energy_cap:w.C,target:w.target,terminal_bonus:w.B,remaining_reactions:w.steps.slice(t).map(z=>({maps:z.maps,collect_points:z.rewards}))},observation:{encounter:"turn_"+t,turn:t,status:"decision",values:{mode:m,energy:e},actions:Object.keys(q).map(id=>({id,text:{collect:"Collect cargo",switch:"Switch route",recharge:"Recharge"}[id]}))},output_contract:"Return one legal action ID."};
    out.push(row);
    for(const a of Object.keys(q)){const n=step(w,t,m,e,a);next.set(n.m+":"+n.e,[n.m,n.e])}
   }states=[...next.values()];
  }return out;
 }
 function empty(){return{roots:0,rows:0,informative_rows:0,correct:0,informative_correct:0,valid:0,root_correct:0,strict_roots:0,strict_root_correct:0,earned:0,oracle_points:0,nominal_points:0,completed:0,regret:0,root_regret:0}}
 const valid=(r,a)=>typeof a==="string"&&Object.hasOwn(r.q,a);
 function add(a,w,rs,policy){
  const root=rs[0],choice=policy(root),rootValid=valid(root,choice),rootOK=rootValid&&root.winners.includes(choice),strict=root.winners.length===1;
  a.roots++;a.root_correct+=Number(rootOK);a.strict_roots+=Number(strict);a.strict_root_correct+=Number(strict&&rootOK);a.root_regret+=root.max-(rootValid?root.q[choice]:0);
  a.oracle_points+=root.max;a.nominal_points+=3*w.H+w.B;
  for(const r of rs){const c=policy(r),v=valid(r,c),ok=v&&r.winners.includes(c),info=r.range>0;a.rows++;a.valid+=Number(v);a.correct+=Number(ok);a.informative_rows+=Number(info);a.informative_correct+=Number(ok&&info)}
  const by=new Map(rs.map(r=>[[r.t,r.m,r.e].join(":"),r]));
  let m=w.initial,e=1,earned=0,complete=true;
  for(let t=0;t<w.H;t++){const r=by.get([t,m,e].join(":")),c=policy(r);if(!valid(r,c)){complete=false;break}const n=step(w,t,m,e,c);earned+=n.reward;m=n.m;e=n.e}
  a.earned+=earned;a.completed+=Number(complete);a.regret+=root.max-earned;
  check(earned<=root.max,"policy exceeds oracle");
  return {choice,rootOK,earned};
 }
 function finish(a){const d=(x,y)=>y?x/y:null;return {...a,raw_accuracy:d(a.correct,a.rows),informative_accuracy:d(a.informative_correct,a.informative_rows),root_accuracy:d(a.root_correct,a.roots),strict_root_accuracy:d(a.strict_root_correct,a.strict_roots),nominal_utility:d(a.earned,a.nominal_points),oracle_fraction:d(a.earned,a.oracle_points)}}
 function experiment(seed=SEED,reps=REPS,submissions=null){
  const total={},groups={},pairs={},cuts={},thresholds={},tests={brute_roots:0,brute_action_values:0,matched_bonus:0,matched_targets:0,oracle_complete:0};
  let roots=0,baseCount=0,cells=0,malformed=0;const seen=new Map(),dups=new Set(),matched=new Map();
  if(submissions!==null)for(const s of submissions){if(!s||typeof s.id!=="string"){malformed++;continue}if(seen.has(s.id))dups.add(s.id);else seen.set(s.id,s)}
  const controls=submissions===null?modes:["submitted"];
  for(const base of bases(seed,reps)){
   baseCount++;cells=Math.max(cells,base.cell+1);
   const key=[base.H,base.W,base.C,base.rep].join(":"),sig=JSON.stringify([base.initial,base.steps]);
   if(matched.has(key)){check(matched.get(key)===sig,"bonus tape mismatch");tests.matched_bonus++}else matched.set(key,sig);
   const gkey=`H${base.H}_W${base.W}`,group=groups[gkey]??={},pair=pairs[gkey]??={eligible:0,total_pairs:0,controls:{}},cut=cuts[gkey]??={probes:0,value_changed:0,q_changed:0,strict_reversal:0,all_stage_q_sensitive_roots:0,per_stage:{}},th=thresholds[gkey]??={roots:0,strict_roots:0,min:{},persistent:{},nonmonotone:0,full_only:0};
   const candidates=[];
   for(let target=0;target<base.W;target++){
    const w={...base,target,id:`${base.id}g${target}`},s=solve(w),rs=rows(w,s),r=rs[0];roots++;th.roots++;
    if(target)tests.matched_targets++;
    if(w.H<=4||w.rep===0){
     check(r.max===brute(w,0,w.initial,1),"brute root");tests.brute_roots++;
     for(const a of Object.keys(r.q)){const n=step(w,0,w.initial,1,a);check(r.q[a]===n.reward+brute(w,1,n.m,n.e),"brute action");tests.brute_action_values++}
    }
    const depth=Array.from({length:w.H},(_,i)=>r.winners.includes(best(s.q(0,w.initial,1,i+1)).winners[0]));
    check(depth.at(-1),"full threshold");
    if(r.winners.length===1){th.strict_roots++;const min=depth.indexOf(true)+1,lastBad=depth.lastIndexOf(false)+2;th.min[min]=(th.min[min]??0)+1;th.persistent[lastBad]=(th.persistent[lastBad]??0)+1;th.nonmonotone+=Number(min!==lastBad);th.full_only+=Number(min===w.H)}
    let all=true;
    for(let j=0;j<w.H;j++){
     const q=solve(w,j).q(0,w.initial,1,w.H),b=best(q),v=b.max!==r.max,d=Object.keys(q).some(a=>q[a]!==r.q[a]),rev=r.winners.length===1&&b.winners.length===1&&b.winners[0]!==r.winners[0],cs=cut.per_stage[j]??={probes:0,value_changed:0,q_changed:0,strict_reversal:0};
     for(const a of [cut,cs]){a.probes++;a.value_changed+=Number(v);a.q_changed+=Number(d);a.strict_reversal+=Number(rev)}all&&=d;
    }cut.all_stage_q_sensitive_roots+=Number(all);
    const runs={};
    for(const m of controls){
     const policy=m==="submitted"?r=>{const x=seen.get(r.id);return x&&!dups.has(r.id)&&Object.keys(x).sort().join(",")==="action,id"?x.action:null}:r=>r.controls[m];
     const a=add(total[m]??=empty(),w,rs,policy),b=add(group[m]??=empty(),w,rs,policy);check(a.earned===b.earned,"aggregate drift");runs[m]=a;
     if(m==="oracle"){check(a.earned===r.max&&a.rootOK,"oracle rollout");tests.oracle_complete++}
    }
    candidates.push({r,runs});
    if(submissions!==null)for(const row of rs)seen.delete(row.id);
   }
   for(let i=0;i<candidates.length;i++)for(let j=i+1;j<candidates.length;j++){
    pair.total_pairs++;const a=candidates[i],b=candidates[j];if(a.r.margin<1||b.r.margin<1||a.r.winners[0]===b.r.winners[0])continue;pair.eligible++;
    for(const m of controls){const p=pair.controls[m]??={both_correct:0,individual_correct:0,same_action:0,regret:0},x=a.runs[m],y=b.runs[m];p.both_correct+=Number(x.rootOK&&y.rootOK);p.individual_correct+=Number(x.rootOK)+Number(y.rootOK);p.same_action+=Number(x.choice===y.choice);p.regret+=a.r.max-x.earned+b.r.max-y.earned}
   }
  }
  const out={schema:"srg18.receipt.v1",seed,reps,cells,bases:baseCount,roots,tests,controls:Object.fromEntries(Object.entries(total).map(([m,a])=>[m,finish(a)])),groups:Object.fromEntries(Object.entries(groups).map(([k,v])=>[k,Object.fromEntries(Object.entries(v).map(([m,a])=>[m,finish(a)]))])),pairs,cuts,thresholds};
  if(submissions!==null)out.submission={malformed,duplicates:dups.size,unknown:seen.size};return out;
 }
 function swmd(w){
  const L=["# SWMD-SRG/2","id: SRG18-reaction-chain","title: \"Cargo reaction chain\"","about: \"Follow published reactions and maximize cargo points.\"","start: p0","turn-base: 0","tie: first","direct: strict",
   `VAR cargo.mode = ${w.initial/8} | public`,"VAR cargo.energy = 0.5 | public",`VAR cargo.target = ${w.target/8} | public`,`VAR cargo.cap = ${w.C/2} | public`,`VAR cargo.bonus = ${w.B/64} | public`,"VAR cargo.score = 0 | hidden"];
  L.push("SPOOL chain | A:TRUE | E:"+Array.from({length:w.H+1},(_,i)=>"p"+i).join(","));
  for(let t=0;t<=w.H;t++){
   L.push(`ENC p${t} turn=${t}..${t} | I:${t} | A:TRUE | Q:C(0) | N:"Cargo reaction" | T:${JSON.stringify(t===w.H?"Complete":"Public reaction table: "+JSON.stringify(w.steps[t]))}`);
   if(t===w.H)break;
   for(const a of w.steps[t].order){
    const id=`a${t}_${a}`,guard=a==="collect"?"TRUE":a==="switch"?"GT(P(cargo.energy),C(0))":"LT(P(cargo.energy),P(cargo.cap))";
    L.push(`OPT ${id} | V:TRUE | P:${guard} | T:${JSON.stringify(a)}`);
    for(let m=0;m<w.W;m++)for(let e=0;e<=w.C;e++){
     if(!legal(w,t,e).includes(a))continue;
     const n=step(w,t,m,e,a),g=`AND(EQ(P(cargo.mode),C(${m/8})),EQ(P(cargo.energy),C(${e/2})))`,writes=[`SET cargo.mode = C(${n.m/8})`,`SET cargo.energy = C(${n.e/2})`,`SET cargo.score = ADD(P(cargo.score),C(${n.reward/64}))`];
     L.push(`ORX ${id}/rx_${id}_${m}_${e} -> p${t+1} | E:${writes.join("; ")} | D:C(0) | G:${g} | T:"Reaction executed."`);
    }
   }
  }return L.join("\n")+"\n";
 }
 function runtimeCheck(api,seed=SEED){
  let fixtures=0,transitions=0,terminal=0,states=0;
  for(const base of bases(seed,1)){
   const w={...base,target:0},compiled=api.compileV2(swmd(w));fixtures++;
   let front=[{s:api.initialV2(compiled),m:w.initial,e:1,earned:0}];
   for(let t=0;t<w.H;t++){
    const next=new Map();
    for(const {s,m,e,earned} of front){
     states++;const o=api.observeV2(compiled,s),a=legal(w,t,e);
     check(o.status==="decision"&&o.turn===t&&Object.keys(o.values).length===5&&o.values["cargo.mode"]*8===m&&o.values["cargo.energy"]*2===e&&o.values["cargo.target"]*8===w.target&&o.values["cargo.cap"]*2===w.C&&o.values["cargo.bonus"]*64===w.B,"runtime observation");
     check(JSON.stringify(o.actions.map(x=>x.id))===JSON.stringify(a.map(x=>`a${t}_${x}`)),"runtime legal");
     for(const act of a){
      const n=step(w,t,m,e,act),ns=api.stepV2(compiled,s,`a${t}_${act}`).next,ne=earned+n.reward;transitions++;
      check(ns.values["cargo.mode"]*8===n.m&&ns.values["cargo.energy"]*2===n.e&&ns.values["cargo.score"]*64===ne,"runtime reaction");
      if(t===w.H-1){check(api.observeV2(compiled,ns).status==="terminal","terminal");terminal++}
      const k=n.m+":"+n.e;if(!next.has(k))next.set(k,{s:ns,m:n.m,e:n.e,earned:ne});
     }
    }front=[...next.values()];
   }
  }return{fixtures,states,transitions,terminal};
 }
 function scorerCheck(seed=SEED){
  const all=Array.from(worlds(seed,1)).flatMap(w=>rows(w).map(r=>({id:r.id,action:r.controls.oracle}))),id=all[0].id;
  const missing=experiment(seed,1,[]),malformed=experiment(seed,1,[null,{id,action:all[0].action},{id,action:all[0].action},{id:all[1].id,action:"illegal"},{id:all[2].id,action:["collect"]},{id:"unknown",action:"collect"}]);
  check(missing.controls.submitted.valid===0&&missing.controls.submitted.earned===0&&missing.controls.submitted.completed===0,"missing");
  check(malformed.controls.submitted.valid===0&&malformed.submission.duplicates===1&&malformed.submission.unknown===1&&malformed.submission.malformed===1,"malformed");
  const full=experiment(seed,1,all);check(full.controls.submitted.earned===full.controls.submitted.oracle_points&&full.controls.submitted.correct===full.controls.submitted.rows,"submitted oracle");
  return{missing:"pass",malformed:"pass",submitted_oracle:"pass",oracle_submissions:all.length};
 }
 return {SEED,REPS,grid,modes,bases,worlds,rows,experiment,swmd,runtimeCheck,scorerCheck};
}
export const {SEED,REPS,grid,modes,bases,worlds,rows,experiment,swmd,runtimeCheck,scorerCheck}=core();
