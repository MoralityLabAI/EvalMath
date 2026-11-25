function core(){
 const check=(v,m)=>{if(!v)throw Error("SRG25: "+m)},sum=a=>a.reduce((s,x)=>s+x,0),dot=(a,b)=>sum(a.map((x,i)=>x*b[i])),mean=a=>sum(a)/a.length,close=(a,b,t=1e-9)=>Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b)),policies=["d1","d2","terminal","uniform","beam","d4"],targets=policies.slice(3),anchors=policies.slice(0,3);
 const freshSeeds=[0x53522501,0x53522502],arms=["structural","scalar","pca1","pca2","pca3","raw"];
 function join(freezes,audits){
  const rows=[],groups=[],tests={bases:0,unique:0,feasible:0,joined:0,training_replays:0,source_baseline:0}; 
  for(let c=0;c<2;c++){const f=freezes[c].cohort,a=audits[c],map=new Map(a.groups.map(g=>[g.id,g]));check(map.size===f.groups.length&&a.seed===f.seed,"cohort join");
   for(const g of f.groups){tests.bases++;const z=map.get(g.id);check(z&&z.eligible===g.eligible,"base join");const outcomes=new Map(z.candidate_outcomes.map(x=>[x.i,x.regret]));check(outcomes.size===g.candidates.length,"candidate join");const feasible=g.candidates.filter(x=>x.feasible),group=[];
    for(const x of g.candidates){tests.unique++;const y=outcomes.get(x.i);check(y&&policies.every(m=>Number.isFinite(y[m])&&y[m]>=0&&y[m]<=1),"policy values");tests.joined++;
     for(const m of anchors){check(x.training[m]===y[m],"training replay");tests.training_replays++}
     if(x.i===0){check(x.guard.opt===g.baseline.opt&&x.guard.rows===g.baseline.rows&&x.guard.info===g.baseline.info&&x.guard.sensitive===g.baseline.sensitive,"baseline guard");tests.source_baseline++}
     if(!x.feasible)continue;tests.feasible++;
     const nom=3*g.H+g.B,v=policies.map(m=>y[m]);
     for(const p of v)check(close(p*nom,Math.round(p*nom)),"integer regret");
     const row={cohort:c,tape:`${c}:${g.rep}`,baseId:`${c}:${g.id}`,proposal:x.i,w:1/feasible.length,nom,base:[g.H,g.W,g.C,g.B,x.guard.opt/nom,x.guard.info,x.guard.sensitive/g.H,x.edits.length],v};
     rows.push(row);group.push(row);
    }if(group.length)groups.push(group);
   }
  }
  check(tests.feasible===rows.length&&tests.unique===tests.joined&&groups.length>0,"joined counts");return{rows,groups,tests};
 }
 function covariance(rows,feature){
  const X=rows.map(feature),weights=rows.map(r=>r.w),W=sum(weights),n=X[0].length,mu=Array.from({length:n},(_,j)=>sum(X.map((v,i)=>weights[i]*v[j]))/W),C=Array.from({length:n},()=>Array(n).fill(0));
  for(let k=0;k<X.length;k++){const x=X[k].map((v,j)=>v-mu[j]);for(let i=0;i<n;i++)for(let j=0;j<n;j++)C[i][j]+=weights[k]*x[i]*x[j]/W}
  return{mu,C,W};
 }
 function eig(C){
  const n=C.length,A=C.map(x=>x.slice()),U=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>Number(i===j)));let residual=0,steps=0;
  for(;steps<100*n*n;steps++){
   let p=0,q=0;residual=0;for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)if(Math.abs(A[i][j])>residual){residual=Math.abs(A[i][j]);p=i;q=j}
   if(residual<1e-14)break;
   const phi=.5*Math.atan2(2*A[p][q],A[q][q]-A[p][p]),c=Math.cos(phi),s=Math.sin(phi),a=A[p][p],b=A[q][q],z=A[p][q];
   A[p][p]=c*c*a-2*s*c*z+s*s*b;A[q][q]=s*s*a+2*s*c*z+c*c*b;A[p][q]=A[q][p]=0;
   for(let k=0;k<n;k++){if(k!==p&&k!==q){const u=A[k][p],v=A[k][q];A[k][p]=A[p][k]=c*u-s*v;A[k][q]=A[q][k]=s*u+c*v}const u=U[k][p],v=U[k][q];U[k][p]=c*u-s*v;U[k][q]=s*u+c*v}
  }
  const order=Array.from({length:n},(_,i)=>i).sort((a,b)=>A[b][b]-A[a][a]),values=order.map(i=>A[i][i]),vectors=order.map(i=>{const v=U.map(r=>r[i]),j=v.reduce((a,x,b)=>Math.abs(x)>Math.abs(v[a])?b:a,0);return v.map(x=>v[j]<0?-x:x)});
  check(residual<1e-12&&values.every(x=>x>=-1e-9),"PSD/convergence");
  let orth=0,recon=0;
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){orth=Math.max(orth,Math.abs(dot(vectors[i],vectors[j])-Number(i===j)));recon=Math.max(recon,Math.abs(C[i][j]-sum(values.map((v,k)=>v*vectors[k][i]*vectors[k][j]))))}
  check(orth<1e-9&&recon<1e-9&&close(sum(values),sum(C.map((r,i)=>r[i]))),"eigen verification");
  return{values,vectors,orthogonality_error:orth,reconstruction_error:recon,residual,steps};
 }
 const profile=r=>r.v.map(x=>x-mean(r.v)),anchor=r=>r.v.slice(0,3);
 function spectrum(rows,feature){
  const {C,mu,W}=covariance(rows,feature),e=eig(C),v=e.values.map(x=>Math.max(0,x)),tr=sum(v),ss=sum(v.map(x=>x*x)),perm=Array.from({length:C.length},(_,i)=>C.length-1-i),pe=eig(perm.map(i=>perm.map(j=>C[i][j])));check(pe.values.every((x,i)=>close(x,e.values[i])),"column permutation");
  return{rows:rows.length,weight:W,mean:mu,covariance:C,eigenvalues:e.values,singular_values:v.map(Math.sqrt),variance_fraction:v.map(x=>tr?x/tr:0),participation_rank:ss?tr*tr/ss:0,rank1_residual_fraction:tr?1-v[0]/tr:0,loadings:e.vectors,checks:{orthogonality_error:e.orthogonality_error,reconstruction_error:e.reconstruction_error,permutation:"pass",trace:"pass",psd:"pass"}};
 }
 function pairAudit(groups){
  const pairs={},collisions={same_anchor_mean:0,heldout_gap_ge_005:0,by_target:Object.fromEntries(targets.map(x=>[x,0]))};
  for(let i=0;i<policies.length;i++)for(let j=i+1;j<policies.length;j++)pairs[policies[i]+"/"+policies[j]]={strict_both:0,reversed:0,total:0};
  for(const g of groups)for(let i=0;i<g.length;i++)for(let j=i+1;j<g.length;j++){
   const a=g[i],b=g[j],d=a.v.map((v,k)=>Math.round((v-b.v[k])*a.nom));
   for(let k=0;k<d.length;k++)for(let l=k+1;l<d.length;l++){const p=pairs[policies[k]+"/"+policies[l]];p.total++;p.strict_both+=Number(d[k]!==0&&d[l]!==0);p.reversed+=Number(d[k]*d[l]<0)}
   if(sum(d.slice(0,3))===0){collisions.same_anchor_mean++;let hit=false;for(let k=3;k<6;k++)if(Math.abs(d[k])/a.nom>=.05){collisions.by_target[policies[k]]++;hit=true}collisions.heldout_gap_ge_005+=Number(hit)}
  }
  return{pairs,collisions};
 }
 function kmeans(rows){
  const train=rows.filter(r=>r.cohort===0),test=rows.filter(r=>r.cohort===1),X=train.map(profile),W=sum(train.map(r=>r.w)),mu=Array.from({length:6},(_,j)=>sum(X.map((x,i)=>x[j]*train[i].w))/W),dist=(a,b)=>sum(a.map((x,i)=>(x-b[i])**2)),pick=scores=>scores.reduce((a,v,i)=>v>scores[a]?i:a,0);
  const centers=[X[pick(X.map(x=>dist(x,mu)))].slice()];while(centers.length<3)centers.push(X[pick(X.map(x=>Math.min(...centers.map(c=>dist(x,c)))))].slice());
  function assign(x){const d=centers.map(c=>dist(x,c));return d.indexOf(Math.min(...d))}
  let prev=[],iterations=0;for(;iterations<100;iterations++){
   const labels=X.map(assign);if(labels.every((x,i)=>x===prev[i]))break;prev=labels;
   for(let k=0;k<3;k++){const ids=labels.map((v,i)=>v===k?i:-1).filter(i=>i>=0),w=sum(ids.map(i=>train[i].w));check(w>0,"empty cluster");centers[k]=Array.from({length:6},(_,j)=>sum(ids.map(i=>train[i].w*X[i][j]))/w)}
  }
  check(iterations<100,"kmeans convergence");
  const describe=rs=>centers.map((c,k)=>{const group=rs.filter(r=>assign(profile(r))===k),w=sum(group.map(r=>r.w));return{rows:group.length,base_weight:w,fraction:w/sum(rs.map(r=>r.w)),mean_regret:policies.map((_,j)=>w?sum(group.map(r=>r.w*r.v[j]))/w:null)}});
  return{iterations,centers,train:describe(train),test:describe(test)};
 }
 function linear(A,b){
  const n=b.length,M=A.map((r,i)=>r.concat(b[i]));
  for(let k=0;k<n;k++){let p=k;for(let i=k+1;i<n;i++)if(Math.abs(M[i][k])>Math.abs(M[p][k]))p=i;[M[k],M[p]]=[M[p],M[k]];const d=M[k][k];check(Math.abs(d)>1e-12,"ridge pivot");for(let j=k;j<=n;j++)M[k][j]/=d;for(let i=0;i<n;i++)if(i!==k){const d=M[i][k];for(let j=k;j<=n;j++)M[i][j]-=d*M[k][j]}}return M.map(r=>r[n]);
 }
 function models(train){
  const pca=covariance(train,anchor),E=eig(pca.C),N=train.length,W=sum(train.map(r=>r.w)),w=train.map(r=>r.w*N/W);
  const fs={structural:r=>r.base,scalar:r=>r.base.concat(mean(anchor(r))),raw:r=>r.base.concat(anchor(r))};
  for(let k=1;k<=3;k++)fs["pca"+k]=r=>r.base.concat(E.vectors.slice(0,k).map(v=>dot(v,anchor(r).map((x,j)=>x-pca.mu[j]))));
  const out={};
  for(const name of arms){
   const feature=fs[name],X=train.map(feature),n=X[0].length,mu=Array.from({length:n},(_,j)=>sum(X.map((r,i)=>w[i]*r[j]))/N),sd=mu.map((m,j)=>Math.sqrt(sum(X.map((r,i)=>w[i]*(r[j]-m)**2))/N)||1),norm=x=>x.map((v,j)=>(v-mu[j])/sd[j]),Z=X.map(norm),C=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>Number(i===j)));
   for(let i=0;i<N;i++)for(let j=0;j<n;j++)for(let k=0;k<n;k++)C[j][k]+=w[i]*Z[i][j]*Z[i][k];
   out[name]=targets.map((_,k)=>{const y=train.map(r=>r.v[k+3]),ym=sum(y.map((v,i)=>w[i]*v))/N,b=Array(n).fill(0);for(let i=0;i<N;i++)for(let j=0;j<n;j++)b[j]+=w[i]*Z[i][j]*(y[i]-ym);const beta=linear(C,b);
    return{mean:ym,predict:r=>ym+dot(norm(feature(r)),beta),params:{ym,mu,sd,beta}};
   });
  }
  return{models:out,pca:{mu:pca.mu,values:E.values,vectors:E.vectors},params:Object.fromEntries(arms.map(a=>[a,out[a].map(x=>x.params)]))};
 }
 function empty(){return{w:0,n:0,se:0,ae:0,baseSe:0}}
 function add(A,r,p,y,mu){check(Number.isFinite(p),"prediction");A.w+=r.w;A.n++;A.se+=r.w*(p-y)**2;A.ae+=r.w*Math.abs(p-y);A.baseSe+=r.w*(mu-y)**2}
 function metric(a){return{rows:a.n,base_weight:a.w,rmse:Math.sqrt(a.se/a.w),mae:a.ae/a.w,r2:a.baseSe?1-a.se/a.baseSe:null}}
 function collect(sets){
  const A={},byTape={},byCohort={};
  for(const {test,fit} of sets)for(const r of test){const tape=byTape[r.tape]??={},co=byCohort[r.cohort]??={};
   for(const arm of arms)for(let k=0;k<targets.length;k++){
    const m=targets[k],p=fit.models[arm][k],z=p.predict(r);
    for(const g of [A,tape,co]){const a=(g[arm]??={})[m]??=empty();add(a,r,z,r.v[k+3],p.mean)}
   }
  }
  const finish=g=>Object.fromEntries(arms.map(a=>{const by=Object.fromEntries(targets.map(m=>[m,metric(g[a][m])]));return[a,{targets:by,macro_rmse:mean(targets.map(m=>by[m].rmse))}]}));
  const metrics=finish(A),tapes=Object.fromEntries(Object.entries(byTape).map(([k,v])=>[k,finish(v)])),cohorts=Object.fromEntries(Object.entries(byCohort).map(([k,v])=>[k,finish(v)]));
  const gain=1-metrics.pca2.macro_rmse/metrics.scalar.macro_rmse,perTarget=Object.fromEntries(targets.map(m=>[m,1-metrics.pca2.targets[m].rmse/metrics.scalar.targets[m].rmse])),improved=Object.values(tapes).filter(t=>t.pca2.macro_rmse<t.scalar.macro_rmse-1e-12).length;
  return{metrics,tapes,cohorts,primary:{macro_reduction:gain,target_reductions:perTarget,tapes_improved:improved,tapes:Object.keys(tapes).length,pass:gain>=.05&&Object.values(perTarget).every(x=>x>=-.02)}};
 }
 function cross(rows){const tapes=[...new Set(rows.map(r=>r.tape))];return collect(tapes.map(t=>({test:rows.filter(r=>r.tape===t),fit:models(rows.filter(r=>r.tape!==t))})))}
 const legal=(w,t,e)=>w.steps[t].order.filter(a=>a==="collect"||a==="switch"&&e>0||a==="recharge"&&e<w.C),key=(t,m,e)=>`${t}:${m}:${e}`;
 function step(w,t,m,e,a,cut=-1){const s=w.steps[t],nm=t===cut?m:s.maps[a][m],ne=e+Number(a==="recharge")-Number(a==="switch"),r=(a==="collect"?s.rewards[m]:0)+(t===w.H-1&&nm===w.target&&ne>0?w.B:0);return{m:nm,e:ne,r}}
 function guard(w,cut=-1){const memo=new Map();function val(t,m,e){if(t===w.H)return 0;const k=key(t,m,e);if(memo.has(k))return memo.get(k).max;const q=Object.fromEntries(legal(w,t,e).map(a=>{const n=step(w,t,m,e,a,cut);return[a,n.r+val(t+1,n.m,n.e)]})),v=Object.values(q),max=Math.max(...v);memo.set(k,{q,max,info:max>Math.min(...v)});return max}const opt=val(0,w.initial,1);return{opt,q:memo.get(key(0,w.initial,1)).q,rows:memo.size,info:[...memo.values()].filter(r=>r.info).length/memo.size}}
 function uniform(w){const memo=new Map();function v(t,m,e){if(t===w.H)return 0;const k=key(t,m,e);if(memo.has(k))return memo.get(k);const x=mean(legal(w,t,e).map(a=>{const n=step(w,t,m,e,a);return n.r+v(t+1,n.m,n.e)}));memo.set(k,x);return x}return(t,m,e)=>{const as=legal(w,t,e),q=as.map(a=>{const n=step(w,t,m,e,a);return n.r+v(t+1,n.m,n.e)}),hi=Math.max(...q);return as[q.findIndex(x=>Math.abs(x-hi)<1e-12)]}}
 function beam(w){let front=[{m:w.initial,e:1,r:0}];for(let t=0;t<w.H;t++){const next=[];for(const p of front)for(const a of legal(w,t,p.e)){const n=step(w,t,p.m,p.e,a);next.push({m:n.m,e:n.e,r:p.r+n.r,i:next.length})}next.sort((a,b)=>b.r-a.r||a.i-b.i);front=next.slice(0,2)}return front[0].r}
 function fresh(R,seed,c){
  const rows=[],tests={worlds:0,guard_dp:0,source_oracle:0,control_bounds:0};
  for(const w of R.worlds(seed,8)){if(w.H<6||w.W<4||w.target>1)continue;tests.worlds++;const g=guard(w),rs=R.rows(w),nom=3*w.H+w.B;tests.guard_dp++;check(g.opt===rs[0].max&&g.rows===rs.length&&close(g.info,rs.filter(r=>r.range>0).length/rs.length),"fresh guard");
   let sensitive=0;for(let t=0;t<w.H;t++){const z=guard(w,t);tests.guard_dp++;sensitive+=Number(Object.keys(g.q).some(a=>g.q[a]!==z.q[a]))}
   const map=new Map(rs.map(r=>[key(r.t,r.m,r.e),r])),u=uniform(w);
   function rollout(mode){if(mode==="beam")return beam(w);let m=w.initial,e=1,r=0;for(let t=0;t<w.H;t++){const a=mode==="uniform"?u(t,m,e):map.get(key(t,m,e)).controls[mode],n=step(w,t,m,e,a);m=n.m;e=n.e;r+=n.r}return r}
   check(rollout("oracle")===g.opt,"fresh oracle");tests.source_oracle++;
   const v=policies.map(m=>{const n=rollout(m);check(n<=g.opt,"fresh upper");tests.control_bounds++;return(g.opt-n)/nom});
   rows.push({cohort:c,tape:`${c}:${w.rep}`,baseId:`${c}:${w.id}`,proposal:0,w:1,nom,base:[w.H,w.W,w.C,w.B,g.opt/nom,g.info,sensitive/w.H,0],v});
  }return{rows,tests};
 }
 function run(R,freezes,audits){
  const {rows,groups,tests}=join(freezes,audits),original=rows.filter(r=>r.proposal===0).map(r=>({...r,w:1})),geometry={full:spectrum(rows,r=>r.v),relative:spectrum(rows,profile),original:spectrum(original,r=>r.v)},C=geometry.full.covariance;
  const correlations=C.map((r,i)=>r.map((v,j)=>C[i][i]&&C[j][j]?v/Math.sqrt(C[i][i]*C[j][j]):null));
  const pair=pairAudit(groups),clusters=kmeans(rows),cv=cross(rows),frozen=models(rows),fresh_results=[];
  for(let i=0;i<freshSeeds.length;i++){const f=fresh(R,freshSeeds[i],i+2);fresh_results.push({seed:freshSeeds[i],tests:f.tests,geometry:spectrum(f.rows,r=>r.v),prediction:collect([{test:f.rows,fit:frozen}])})}
  cv.primary.pass&&=cv.primary.tapes_improved>=6&&cv.primary.tapes===8;
  return{schema:"srg25.receipt.v1",policies,tests:{...tests,nonempty_bases:groups.length,original_feasible:original.length},geometry,correlations,pair,clusters,cv,frozen_fit:{pca:frozen.pca,params:frozen.params},fresh:fresh_results,promote:cv.primary.pass&&fresh_results.every(r=>r.prediction.primary.pass)};
 }
 return{run};
}
export const {run}=core();
