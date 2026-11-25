function core(){
 const check=(v,m)=>{if(!v)throw Error("SRG21: "+m)},sum=a=>a.reduce((s,x)=>s+x,0),mean=a=>sum(a)/a.length,dot=(a,b)=>sum(a.map((x,i)=>x*b[i])),close=(a,b,t=1e-9)=>Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b));
 function graph(n,edges){
  const adj=Array.from({length:n},()=>new Map()),degree=Array(n).fill(0);let weight=0;
  for(const [u,v,w] of edges){check(u!==v&&w>0&&Number.isFinite(w),"edge");adj[u].set(v,(adj[u].get(v)??0)+w);adj[v].set(u,(adj[v].get(u)??0)+w);degree[u]+=w;degree[v]+=w;weight+=w}
  return{n,edges,adj,degree,weight};
 }
 function components(g){const seen=new Set();let c=0;for(let v=0;v<g.n;v++){if(seen.has(v))continue;c++;const q=[v];seen.add(v);while(q.length){const u=q.pop();for(const w of g.adj[u].keys())if(!seen.has(w)){seen.add(w);q.push(w)}}}return c}
 function moments(g){
  const {n,degree,adj}=g,nz=degree.filter(x=>x>0).length,norm=adj.map((a,i)=>new Map([...a].map(([j,w])=>[j,w/Math.sqrt(degree[i]*degree[j])])));
  let a2=0,a3=0,a4=0,raw2=sum(degree.map(d=>d*d)),raw3=sum(degree.map(d=>d**3)),rawTri=0;
  for(let i=0;i<n;i++){
   const p=new Map();for(const [j,w] of norm[i]){a2+=w*w;for(const [k,v] of norm[j])p.set(k,(p.get(k)??0)+w*v)}
   for(const [k,v] of p){a4+=v*v;a3+=v*(norm[i].get(k)??0)}
   for(const [j,w] of adj[i]){raw2+=w*w;raw3+=3*degree[i]*w*w;for(const [k,v] of adj[j])rawTri+=w*v*(adj[i].get(k)??0)}
  }
  const t1=nz,t2=nz+a2,t3=nz+3*a2-a3,t4=nz+6*a2-4*a3+a4,c=components(g),raw1=sum(degree);raw3-=rawTri;
  const out={n,m:g.edges.length,mean_weight:g.weight/g.edges.length,components:c,vertex_nullity:c,dirac_nullity:g.edges.length-n+2*c,t1,t2,t3,t4,effective_rank:t2?t1*t1/t2:0,raw1,raw2,raw3,
   features:[t2/n,t3/n,t4/n,t2?t1*t1/(t2*n):0,raw1?raw2*n/(raw1*raw1):0,raw1?raw3*n*n/(raw1**3):0]};
  check(out.dirac_nullity>=0&&t2>=t1-1e-10&&t4>=0,"moment bounds");
  return out;
 }
 function applyL(g,x,normalized=false){
  const y=Array(g.n).fill(0);for(const [u,v,w] of g.edges){const a=normalized?x[u]/Math.sqrt(g.degree[u]):x[u],b=normalized?x[v]/Math.sqrt(g.degree[v]):x[v],z=w*(a-b);y[u]+=normalized?z/Math.sqrt(g.degree[u]):z;y[v]-=normalized?z/Math.sqrt(g.degree[v]):z}return y;
 }
 function energyCheck(g){
  const x=Array.from({length:g.n},(_,i)=>((i*17+5)%23-11)/11);
  for(const norm of [false,true]){
   const energy=sum(g.edges.map(([u,v,w])=>w*((norm?x[u]/Math.sqrt(g.degree[u]):x[u])-(norm?x[v]/Math.sqrt(g.degree[v]):x[v]))**2));
   check(close(dot(x,applyL(g,x,norm)),energy),"incidence energy");
  }
  const m=moments(g),rev=moments(graph(g.n,g.edges.map(([u,v,w])=>[v,u,w])));
  check(m.features.every((v,i)=>close(v,rev.features[i])),"orientation");
  return 1;
 }
 function eigenReference(g){
  const n=g.n,A=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?(g.degree[i]>0?1:0):-(g.adj[i].get(j)??0)/(g.degree[i]&&g.degree[j]?Math.sqrt(g.degree[i]*g.degree[j]):1)));
  const original=A.map(a=>a.slice());let it=0,off=0;
  for(;it<100*n*n;it++){
   let p=0,q=0;off=0;for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)if(Math.abs(A[i][j])>off){off=Math.abs(A[i][j]);p=i;q=j}
   if(off<1e-13)break;
   const phi=.5*Math.atan2(2*A[p][q],A[q][q]-A[p][p]),c=Math.cos(phi),s=Math.sin(phi),a=A[p][p],b=A[q][q],z=A[p][q];
   A[p][p]=c*c*a-2*s*c*z+s*s*b;A[q][q]=s*s*a+2*s*c*z+c*c*b;A[p][q]=A[q][p]=0;
   for(let k=0;k<n;k++)if(k!==p&&k!==q){const u=A[k][p],v=A[k][q];A[k][p]=A[p][k]=c*u-s*v;A[k][q]=A[q][k]=s*u+c*v}
  }
  check(off<1e-11,"Jacobi convergence");const eig=A.map((r,i)=>r[i]).sort((a,b)=>a-b),m=moments(g);
  check(eig.filter(x=>Math.abs(x)<1e-9).length===m.vertex_nullity,"spectral nullity");for(let k=1;k<=4;k++)check(close(sum(eig.map(x=>x**k)),m[`t${k}`]),"eigen moment");
  return{eigenvalues:eig,gap:eig.find(x=>x>1e-9)??null,offdiag_residual:off,iterations:it};
 }
 function selftest(){
  const cases=[["path3",graph(3,[[0,1,1],[1,2,1]]),[0,1,2]],["triangle",graph(3,[[0,1,1],[1,2,1],[2,0,1]]),[0,1.5,1.5]],["parallel",graph(2,[[0,1,1],[0,1,2]]),[0,2]],["two_components",graph(4,[[0,1,1],[2,3,2]]),[0,0,2,2]]];
  const result={};for(const [name,g,expected] of cases){energyCheck(g);const e=eigenReference(g);check(e.eigenvalues.every((x,i)=>close(x,expected[i])),"reference spectrum "+name);result[name]={...e,dirac_nullity:moments(g).dirac_nullity}}
  return result;
 }
 function reactionStep(w,t,m,e,a,cut=-1){
  const s=w.steps[t],nm=t===cut?m:s.maps[a][m],ne=e+Number(a==="recharge")-Number(a==="switch"),r=(a==="collect"?s.rewards[m]:0)+(t===w.H-1&&nm===w.target&&ne>0?w.B:0);return[nm,ne,r];
 }
 function legal(w,t,e){return w.steps[t].order.filter(a=>a==="collect"||a==="switch"&&e>0||a==="recharge"&&e<w.C)}
 function reactionGraph(w,cut=-1){
  const nodes=new Map(),id=(t,m,e)=>{const k=[t,m,e].join(":");if(!nodes.has(k))nodes.set(k,nodes.size);return nodes.get(k)},edges=[],weighted=[];let states=[[w.initial,1]];id(0,w.initial,1);
  for(let t=0;t<w.H;t++){const next=new Map();for(const [m,e] of states){const u=id(t,m,e);for(const a of legal(w,t,e)){const [nm,ne,r]=reactionStep(w,t,m,e,a,cut),v=id(t+1,nm,ne);edges.push([u,v,1]);weighted.push([u,v,1+r]);next.set(nm+":"+ne,[nm,ne])}}states=[...next.values()]}
  return{unit:graph(nodes.size,edges),weighted:graph(nodes.size,weighted)};
 }
 function reactionQ(w,cut=-1){
  const memo=new Map();function val(t,m,e){if(t===w.H)return 0;const k=[t,m,e].join(":");if(memo.has(k))return memo.get(k);const q=legal(w,t,e).map(a=>{const [nm,ne,r]=reactionStep(w,t,m,e,a,cut);return r+val(t+1,nm,ne)});const v=Math.max(...q);memo.set(k,v);return v}
  return Object.fromEntries(legal(w,0,1).map(a=>{const [m,e,r]=reactionStep(w,0,w.initial,1,a,cut);return[a,r+val(1,m,e)]}));
 }
 function reactionValue(w,rs,mode){
  const index=new Map(rs.map(r=>[[r.t,r.m,r.e].join(":"),r]));let m=w.initial,e=1,v=0;for(let t=0;t<w.H;t++){const a=index.get([t,m,e].join(":")).controls[mode],n=reactionStep(w,t,m,e,a);[m,e]=n;v+=n[2]}return v;
 }
 const winner=q=>{const hi=Math.max(...Object.values(q));return Object.keys(q).filter(a=>q[a]===hi)};
 const same=(a,b)=>a.length===b.length&&a.every((v,i)=>close(v,b[i],1e-10)),dist=(a,b)=>Math.sqrt(sum(a.map((v,i)=>(v-b[i])**2)));
 function parity(x){x^=x>>>16;x^=x>>>8;x^=x>>>4;return (0x6996>>>(x&15))&1}
 function rank(masks){const piv=Array(6).fill(0);let r=0;for(let m of masks)for(let j=5;j>=0&&m;j--)if(m&(1<<j)){if(piv[j])m^=piv[j];else{piv[j]=m;r++;break}}return r}
 function epistemicGraph(w,full){
  const masks=[w.target,...w.agents.flatMap(a=>a.masks)],classes=new Map(),ids=Array.from({length:w.W},(_,x)=>{const sig=masks.map(m=>parity(x&m)).join("");if(!classes.has(sig))classes.set(sig,classes.size);return classes.get(sig)});
  let n=classes.size;const edges=[];
  for(let i=0;i<=w.D;i++)for(const row of full.levels[i].rows){
   const v=n++,mass=Array(classes.size).fill(0);for(let x=0;x<w.W;x++)mass[ids[x]]+=row.l[x];
   for(let u=0;u<mass.length;u++)if(mass[u])edges.push([u,v,mass[u]/(w.W*256*(w.D+1))]);
  }
  check(close(sum(edges.map(e=>e[2])),1),"epistemic joint mass");
  return graph(n,edges);
 }
 function beliefGeometry(w,rs){
  const p=rs.map(r=>r.m/(w.W*256)),features=rs.map(r=>r.p.map(Math.sqrt)),mu=Array(w.W).fill(0);
  for(let i=0;i<rs.length;i++)for(let j=0;j<w.W;j++)mu[j]+=p[i]*features[i][j];
  const z=features.map(x=>x.map((v,j)=>v-mu[j]));let t=0,t2=0;
  for(let i=0;i<z.length;i++){t+=p[i]*dot(z[i],z[i]);for(let j=0;j<z.length;j++)t2+=p[i]*p[j]*dot(z[i],z[j])**2}
  const entropy=-sum(rs.map((r,i)=>p[i]*sum(r.p.map(v=>v?v*Math.log2(v):0))));
  return{pr:t2>1e-24?t*t/t2:0,entropy,classes:new Set(rs.map(r=>r.p.join(","))).size};
 }
 function reactionData(api){
  const data=[],cuts=[],groups=new Map(),tests={energy:0,target_invariance:0,source_q:0,source_oracle:0,cut_probes:0,cut_unit_invariant_q_change:0,cut_weighted_invariant_q_change:0},pairs={pairs:0,strict_reversals:0},summary={worlds:0,n:0,m:0,unit_rank:0,weighted_rank:0};let ref=null;
  for(const w of api.worlds()){
   const rs=api.rows(w),root=rs[0],q=reactionQ(w),nom=3*w.H+w.B,graphs=reactionGraph(w),u=moments(graphs.unit),v=moments(graphs.weighted);
   check(Object.keys(q).every(a=>q[a]===root.q[a]),"reaction Q source");tests.source_q++;check(reactionValue(w,rs,"oracle")===root.max,"source oracle");tests.source_oracle++;
   if(w.rep===0){energyCheck(graphs.unit);energyCheck(graphs.weighted);tests.energy+=2;if(!ref&&w.H===2&&w.W===2)ref={unit:eigenReference(graphs.unit),weighted:eigenReference(graphs.weighted)}}
   const base=[w.H,w.W,w.C,w.B,Number(w.initial===w.target),mean(w.steps.flatMap(s=>s.rewards)),w.steps[0].rewards[w.initial],Math.max(...w.steps.at(-1).rewards)];
   const size=[u.n,u.m,v.mean_weight],targetKey=[w.H,w.W,w.C,w.B,w.rep].join(":"),g=groups.get(targetKey)??{u:u.features,others:[]};
   if(g.others.length){check(same(g.u,u.features)&&g.n===u.n&&g.m===u.m,"target topology");tests.target_invariance++}else{g.n=u.n;g.m=u.m}
   for(const old of g.others){pairs.pairs++;if(old.length===1&&root.winners.length===1&&old[0]!==root.winners[0])pairs.strict_reversals++}
   g.others.push(root.winners);groups.set(targetKey,g);
   const y=Object.fromEntries(["d1","d2","d4"].map(m=>[m,(root.max-reactionValue(w,rs,m))/nom]));
   data.push({rep:w.rep,stratum:`H${w.H}_W${w.W}`,base,size,unit:u.features,weighted:v.features,y});
   summary.worlds++;summary.n+=u.n;summary.m+=u.m;summary.unit_rank+=u.effective_rank;summary.weighted_rank+=v.effective_rank;
   if(w.rep===0)for(let j=0;j<w.H;j++){
    const cq=reactionQ(w,j),cg=reactionGraph(w,j),cu=moments(cg.unit),cv=moments(cg.weighted),changed=Object.keys(q).some(a=>q[a]!==cq[a]),du=dist(u.features,cu.features),dv=dist(v.features,cv.features);
    cuts.push({changed,du,dv});tests.cut_probes++;tests.cut_unit_invariant_q_change+=Number(changed&&du<1e-10);tests.cut_weighted_invariant_q_change+=Number(changed&&dv<1e-10);
   }
  }
  return{data,cuts,tests,pairs,summary,reference:ref};
 }
 function epistemicData(api){
  const data=[],groups=new Map(),pads=new Map(),tests={energy:0,fee_invariance:0,padding_invariance:0,source_oracle:0},pairs={pairs:0,strict_reversals:0},summary={worlds:0,n:0,m:0,rank:0,belief_pr:0};let ref=null;
  for(const w of api.worlds()){
   const {rows:rs,full}=api.rows(w),g=epistemicGraph(w,full),m=moments(g),bg=beliefGeometry(w,rs),den=w.W*256**(w.D+1),opt=sum(rs.map(r=>r.max));check(opt===sum(full.levels[0].u),"source oracle");tests.source_oracle++;
   if(w.rep===0){energyCheck(g);tests.energy++;if(!ref&&w.K===2&&w.D===1)ref=eigenReference(g)}
   const rootRank=rank(w.agents[0].masks),unionRank=rank(w.agents.flatMap(a=>a.masks)),targetIn=Number(rank([...w.agents[0].masks,w.target])===rootRank),directCounts=w.agents.map(a=>a.masks.filter(k=>k===w.target).length);
   const base=[w.K,w.R,w.D,w.fee,Number(w.profile==="late"),rootRank,unionRank,targetIn,directCounts[0],mean(directCounts),mean(w.agents.map(a=>a.q))];
   const size=[m.n,m.m,m.mean_weight],k=[w.K,w.R,w.D,w.profile,w.rep].join(":"),old=groups.get(k)??{m:m.features,n:m.n,edges:m.m,rows:[]};
   if(old.rows.length){check(same(old.m,m.features)&&old.n===m.n&&old.edges===m.m,"fee graph");tests.fee_invariance++}
   for(const rr of old.rows)for(let i=0;i<rs.length;i++){const a=rr[i],b=rs[i].winners;pairs.pairs++;pairs.strict_reversals+=Number(a.length===1&&b.length===1&&a[0]!==b[0])}
   old.rows.push(rs.map(r=>r.winners));groups.set(k,old);
   if(w.R===2){const key=[w.D,w.fee,w.profile,w.rep].join(":"),sig=pads.get(key);if(sig){check(same(sig.features,m.features)&&sig.n===m.n&&sig.m===m.m&&close(sig.pr,bg.pr),"quotient padding");tests.padding_invariance++}else pads.set(key,{features:m.features,n:m.n,m:m.m,pr:bg.pr})}
   const y={};for(const mode of ["d1","last","factor"])y[mode]=(opt-sum(rs.map(r=>r.q[r.controls[mode]])))/(8*den);
   data.push({rep:w.rep,stratum:`K${w.K}_R${w.R}_D${w.D}`,base,size,weighted:m.features,belief:[bg.pr,bg.entropy,bg.classes],y});
   summary.worlds++;summary.n+=m.n;summary.m+=m.m;summary.rank+=m.effective_rank;summary.belief_pr+=bg.pr;
  }
  return{data,tests,pairs,summary,reference:ref};
 }
 function solveLinear(A,b){
  const n=b.length,M=A.map((a,i)=>a.concat(b[i]));
  for(let k=0;k<n;k++){let p=k;for(let i=k+1;i<n;i++)if(Math.abs(M[i][k])>Math.abs(M[p][k]))p=i;[M[k],M[p]]=[M[p],M[k]];check(Math.abs(M[k][k])>1e-12,"linear pivot");const d=M[k][k];for(let j=k;j<=n;j++)M[k][j]/=d;for(let i=0;i<n;i++)if(i!==k){const d=M[i][k];for(let j=k;j<=n;j++)M[i][j]-=d*M[k][j]}}
  return M.map(r=>r[n]);
 }
 function fit(train,feature,y){
  const X=train.map(feature),Y=train.map(r=>r.y[y]),p=X[0].length,mu=Array.from({length:p},(_,j)=>mean(X.map(x=>x[j]))),sd=mu.map((m,j)=>Math.sqrt(mean(X.map(x=>(x[j]-m)**2)))||1),ym=mean(Y);
  const C=Array.from({length:p},(_,i)=>Array.from({length:p},(_,j)=>Number(i===j))),b=Array(p).fill(0);
  const transform=x=>x.map((v,i)=>(v-mu[i])/sd[i]);
  for(let i=0;i<X.length;i++){const x=transform(X[i]);for(let j=0;j<p;j++){b[j]+=x[j]*(Y[i]-ym);for(let k=0;k<p;k++)C[j][k]+=x[j]*x[k]}}
  const beta=p?solveLinear(C,b):[];
  return{predict:r=>ym+dot(transform(feature(r)),beta),mean:ym};
 }
 function ranks(x){const ids=x.map((v,i)=>[v,i]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]),out=Array(x.length);for(let i=0;i<ids.length;){let j=i+1;while(j<ids.length&&ids[j][0]===ids[i][0])j++;const r=(i+j-1)/2;for(let k=i;k<j;k++)out[ids[k][1]]=r;i=j}return out}
 function corr(x,y){const a=mean(x),b=mean(y),u=x.map(v=>v-a),v=y.map(v=>v-b),den=Math.sqrt(dot(u,u)*dot(v,v));return den?dot(u,v)/den:null}
 function stratified(rows,pred,y){
  const g=new Map();for(let i=0;i<rows.length;i++){const k=rows[i].stratum,a=g.get(k)??{x:[],y:[]};a.x.push(pred[i]);a.y.push(rows[i].y[y]);g.set(k,a)}
  let total=0,n=0,used=0;for(const a of g.values()){const c=corr(ranks(a.x),ranks(a.y));if(c!==null){total+=c*a.x.length;n+=a.x.length;used++}}
  return{weighted_spearman:n?total/n:null,strata:used,observations:n};
 }
 function prediction(data,domain){
  const features={mean:()=>[],structural:r=>r.base,size:r=>r.base.concat(r.size)};
  if(domain==="reaction"){features.unit=r=>r.base.concat(r.size,r.unit);features.weighted=r=>r.base.concat(r.size,r.unit,r.weighted)}
  else{features.epistemic=r=>r.base.concat(r.size,r.weighted);features.belief=r=>r.base.concat(r.size,r.belief)}
  const tapes=[...new Set(data.map(r=>r.rep))],out={};
  for(const y of Object.keys(data[0].y)){
   const results={};
   for(const [name,feature] of Object.entries(features)){
    const pred=Array(data.length),per_tape=[];let se=0,ae=0,baseSe=0;
    for(const rep of tapes){
     const train=data.filter(r=>r.rep!==rep),model=fit(train,feature,y);let s=0,n=0;
     for(let i=0;i<data.length;i++){const r=data[i];if(r.rep!==rep)continue;const p=model.predict(r),v=r.y[y];check(Number.isFinite(p),"prediction");pred[i]=p;s+=(p-v)**2;ae+=Math.abs(p-v);baseSe+=(model.mean-v)**2;n++}
     se+=s;per_tape.push({rep,n,rmse:Math.sqrt(s/n)});
    }
    results[name]={rmse:Math.sqrt(se/data.length),mae:ae/data.length,r2:baseSe?1-se/baseSe:null,per_tape,...stratified(data,pred,y)};
   }
   const base=results.size;for(const [name,r] of Object.entries(results)){r.relative_rmse_reduction_vs_size=1-r.rmse/base.rmse;r.tapes_improved_vs_size=r.per_tape.filter((t,i)=>t.rmse<base.per_tape[i].rmse-1e-12).length}
   out[y]=results;
  }
  const main=out.d1,arm=domain==="reaction"?"weighted":"epistemic",v=main[arm];
  return{outcomes:out,primary:{arm,relative_reduction:v.relative_rmse_reduction_vs_size,tapes_improved:v.tapes_improved_vs_size,tapes:tapes.length,pass:v.relative_rmse_reduction_vs_size>=.05&&v.tapes_improved_vs_size>=.75*tapes.length}};
 }
 function auc(rows,key){const values=rows.map(r=>r[key]),rs=ranks(values),n=rows.filter(r=>r.changed).length,m=rows.length-n;return n&&m?(sum(rs.filter((_,i)=>rows[i].changed))-n*(n-1)/2)/(n*m):null}
 function run(r18,r20){
  const reference=selftest(),r=reactionData(r18),e=epistemicData(r20),rp=prediction(r.data,"reaction"),ep=prediction(e.data,"epistemic");
  const cut={probes:r.cuts.length,changed:r.cuts.filter(x=>x.changed).length,auc_unit:auc(r.cuts,"du"),auc_weighted:auc(r.cuts,"dv"),unit_invariant_q_change:r.tests.cut_unit_invariant_q_change,weighted_invariant_q_change:r.tests.cut_weighted_invariant_q_change};
  const clean=d=>({tests:d.tests,pairs:d.pairs,summary:d.summary,reference:d.reference});
  return{schema:"srg21.receipt.v1",reference,reaction:clean(r),epistemic:clean(e),cuts:cut,prediction:{reaction:rp,epistemic:ep},promote:rp.primary.pass&&ep.primary.pass};
 }
 return {run,moments,graph,eigenReference};
}
export const {run,moments,graph,eigenReference}=core();
