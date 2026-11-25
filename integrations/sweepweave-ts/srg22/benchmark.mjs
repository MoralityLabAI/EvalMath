const check=(x,m)=>{if(!x)throw Error(m)},sum=a=>a.reduce((s,x)=>s+x,0),mean=a=>sum(a)/a.length,dot=(a,b)=>sum(a.map((x,i)=>x*b[i]));
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

function geometry(){
 const check=(x,m)=>{if(!x)throw Error("SRG22 "+m)},sum=a=>a.reduce((s,x)=>s+x,0),mean=a=>sum(a)/a.length,dot=(a,b)=>sum(a.map((x,i)=>x*b[i])),close=(a,b,t=1e-9)=>Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b)),same=(a,b)=>a.length===b.length&&a.every((x,i)=>close(x,b[i],1e-10));
 const legal=(w,t,e)=>w.steps[t].order.filter(a=>a==="collect"||a==="switch"&&e>0||a==="recharge"&&e<w.C);
 function step(w,t,m,e,a){const s=w.steps[t],nm=s.maps[a][m],ne=e+Number(a==="recharge")-Number(a==="switch"),running=a==="collect"?s.rewards[m]:0,terminal=t===w.H-1&&nm===w.target&&ne>0?w.B:0;return{m:nm,e:ne,r:running+terminal,running,terminal}}
 function reaction(w,G,T){
  const nodes=[],by=new Map(),layers=Array.from({length:w.H+1},()=>[]),unit=[],weighted=[];
  function node(t,m,e){const k=[t,m,e].join(":");if(!by.has(k)){by.set(k,nodes.length);layers[t].push(nodes.length);nodes.push({t,m,e,edges:[],v:0})}return by.get(k)}
  node(0,w.initial,1);
  for(let t=0;t<w.H;t++)for(const i of layers[t]){const n=nodes[i];for(const a of legal(w,t,n.e)){const q=step(w,t,n.m,n.e,a),j=node(t+1,q.m,q.e);n.edges.push({j,...q});unit.push([i,j,1]);weighted.push([i,j,1+q.r])}n.v=Math.max(...n.edges.map(a=>a.r))}
  T.edges+=unit.length;const u=G.moments(G.graph(nodes.length,unit)),v=G.moments(G.graph(nodes.length,weighted)),nom=3*w.H+w.B;
  function flow(first=-1,collect=false){const p=Array(nodes.length).fill(0);p[0]=1;let running=0,terminal=0,pos=0,neg=0,sq=0,maxpos=0,positive=0,firstabs=0,lastabs=0,rmean=0,rsq=0,vmean=0,range=0;
   for(let t=0;t<w.H;t++){check(close(sum(layers[t].map(i=>p[i])),1),"flow mass");T.flow_checks++;
    for(const i of layers[t]){const n=nodes[i],edges=t===0&&first>=0?[n.edges[first]]:n.edges,weight=p[i]/edges.length;
     if(collect){const r=edges.map(a=>a.r+nodes[a.j].v-n.v);maxpos+=p[i]*Math.max(0,...r);vmean+=p[i]*n.v;range+=p[i]*(Math.max(...edges.map(a=>a.r))-Math.min(...edges.map(a=>a.r)))}
     for(const a of edges){T.flow_edges++;p[a.j]+=weight;running+=weight*a.running;terminal+=weight*a.terminal;if(collect){const rho=a.r+nodes[a.j].v-n.v;pos+=weight*Math.max(0,rho);neg+=weight*Math.max(0,-rho);sq+=weight*rho*rho;positive+=weight*Number(rho>0);if(t===0)firstabs+=weight*Math.abs(rho);if(t===w.H-1)lastabs+=weight*Math.abs(rho);rmean+=weight*a.r;rsq+=weight*a.r*a.r}}
    }
   }check(close(sum(layers[w.H].map(i=>p[i])),1),"terminal mass");T.flow_checks++;
   if(collect){check(close(pos-neg,running+terminal-nodes[0].v)&&close(rmean,running+terminal),"telescope");T.telescopes++}
   return{running,terminal,pos,neg,sq,maxpos,positive,firstabs,lastabs,rmean,rsq,vmean,range};
  }
  const f=flow(-1,true),probs=nodes[0].edges.map((_,i)=>flow(i,false).terminal/w.B);check(close(mean(probs),f.terminal/w.B),"mixture");T.root_mixtures++;
  return {base:[w.H,w.W,w.C,w.B,Number(w.initial===w.target),mean(w.steps.flatMap(s=>s.rewards)),w.steps[0].rewards[w.initial],Math.max(...w.steps.at(-1).rewards)],size:[u.n,u.m,v.mean_weight],unit:u.features,weighted:v.features,
   local:[f.rmean/w.H/nom,Math.sqrt(f.rsq/w.H)/nom,f.vmean/w.H/nom,f.range/w.H/nom,f.terminal/nom,f.running/nom,Math.max(...probs)-Math.min(...probs)],
   residual:[f.pos/w.H/nom,f.neg/w.H/nom,Math.sqrt(f.sq/w.H)/nom,f.maxpos/w.H/nom,f.positive/w.H,f.firstabs/nom,f.lastabs/nom,Math.max(...nodes[0].edges.map(a=>a.r+nodes[a.j].v-nodes[0].v))/nom]};
 }
 function rollout(w,rs,mode){const map=new Map(rs.map(r=>[[r.t,r.m,r.e].join(":"),r]));let m=w.initial,e=1,v=0;for(let t=0;t<w.H;t++){const a=map.get([t,m,e].join(":")).controls[mode],q=step(w,t,m,e,a);m=q.m;e=q.e;v+=q.r}return v}
 function reactionData(api,G,seed,reps){const data=[],T={edges:0,flow_edges:0,flow_checks:0,telescopes:0,root_mixtures:0,source_oracle:0,target_pairs:0,target_feature_changes:0,zero_regret:0},pairs=new Map();
  for(const w of api.worlds(seed,reps)){const f=reaction(w,G,T),key=[w.H,w.W,w.C,w.B,w.rep].join(":"),prev=pairs.get(key)??[];
   for(const g of prev){T.target_pairs++;check(same(f.unit,g.unit),"target unit");T.target_feature_changes+=Number(!same(f.local.concat(f.residual),g.local.concat(g.residual)))}prev.push(f);pairs.set(key,prev);
   const rs=api.rows(w),opt=rs[0].max,nom=3*w.H+w.B;check(rollout(w,rs,"oracle")===opt,"oracle");T.source_oracle++;
   const y=Object.fromEntries(["d1","d2","d4"].map(m=>{const loss=opt-rollout(w,rs,m);check(loss>=0,"regret");if(w.H<=Number(m.slice(1))){check(loss===0,"full depth zero");T.zero_regret++}return[m,loss/nom]}));data.push({rep:w.rep,stratum:`H${w.H}_W${w.W}`,...f,y});
  }return{data,tests:T};
 }
 function parity(x){x^=x>>>16;x^=x>>>8;x^=x>>>4;return(0x6996>>>(x&15))&1}
 function rank(masks){const piv=Array(6).fill(0);let r=0;for(let m of masks)for(let j=5;j>=0&&m;j--)if(m&(1<<j)){if(piv[j])m^=piv[j];else{piv[j]=m;r++;break}}return r}
 function likelihood(w,i,h,x){const a=w.agents[i];let l=1;for(let j=0;j<4;j++)l*=parity(x&a.masks[j])===((h>>>j)&1)?a.q:4-a.q;return l}
 function epistemic(w,G,T){
  const ms=[w.target,...w.agents.flatMap(a=>a.masks)],cls=new Map(),ids=Array.from({length:w.W},(_,x)=>{const k=ms.map(m=>parity(x&m)).join("");if(!cls.has(k))cls.set(k,cls.size);return cls.get(k)}),targets=Array.from({length:w.W},(_,x)=>parity(x&w.target));
  let n=cls.size;const edges=[],histories=[],correct=[];
  for(let i=0;i<=w.D;i++){const rows=[],acc=Array(w.W).fill(0),mass=Array(w.W).fill(0);
   for(let h=0;h<16;h++){const l=Array.from({length:w.W},(_,x)=>likelihood(w,i,h,x));T.likelihood_evaluations+=w.W;const m=sum(l);if(!m)continue;const q1=dot(l,targets),p=q1/m,a=Number(2*q1>m),v=n++,cm=Array(cls.size).fill(0);
    for(let x=0;x<w.W;x++){cm[ids[x]]+=l[x];mass[x]+=l[x];if(a===targets[x])acc[x]+=l[x]/256}for(let u=0;u<cm.length;u++)if(cm[u])edges.push([u,v,cm[u]/(w.W*256*(w.D+1))]);rows.push({l,m,p,a,posterior:l.map(x=>x/m)});
   }check(mass.every(x=>x===256),"likelihood");T.likelihood_checks+=w.W;histories.push(rows);correct.push(acc);
  }
  check(close(sum(edges.map(a=>a[2])),1),"joint mass");T.graph_mass++;const g=G.moments(G.graph(n,edges)),rs=histories[0],standalone=correct.map(mean),p=rs.map(r=>r.m/(w.W*256)),features=rs.map(r=>r.posterior.map(Math.sqrt)),mu=Array(w.W).fill(0);
  for(let i=0;i<rs.length;i++)for(let j=0;j<w.W;j++)mu[j]+=p[i]*features[i][j];const centered=features.map(f=>f.map((v,j)=>v-mu[j]));let tr=0,tr2=0;
  for(let i=0;i<rs.length;i++){tr+=p[i]*dot(centered[i],centered[i]);for(let j=0;j<rs.length;j++)tr2+=p[i]*p[j]*dot(centered[i],centered[j])**2}
  const entropy=-sum(rs.map((r,i)=>p[i]*sum(r.posterior.map(v=>v?v*Math.log2(v):0)))),belief=[tr2>1e-24?tr*tr/tr2:0,entropy,new Set(rs.map(r=>r.posterior.join(","))).size];
  const rootRank=rank(w.agents[0].masks),unionRank=rank(w.agents.flatMap(a=>a.masks)),targetIn=Number(rank([...w.agents[0].masks,w.target])===rootRank),counts=w.agents.map(a=>a.masks.filter(k=>k===w.target).length);
  let direct=0,gap=0,variance=0,res=0,pos=0,neg=0,sq=0,positive=0,later=0,laterpos=0;
  for(let i=0;i<rs.length;i++){const r=rs[i],weight=p[i],d=Math.max(r.p,1-r.p),a1=dot(r.posterior,correct[1]),rho=a1-w.fee/8-d,alignment=w.D>=2?Math.max(...correct.slice(2).map(c=>dot(r.posterior,c)))-a1:0;
   direct+=weight*d;gap+=weight*Math.abs(2*r.p-1);variance+=weight*r.p*(1-r.p);res+=weight*rho;pos+=weight*Math.max(0,rho);neg+=weight*Math.max(0,-rho);sq+=weight*rho*rho;positive+=weight*Number(rho>1e-12);later+=weight*alignment;laterpos+=weight*Math.max(0,alignment);
  }
  check(close(direct,standalone[0])&&close(res,pos-neg),"delegation residual");T.residual_checks++;
  return{base:[w.K,w.R,w.D,w.fee,Number(w.profile==="late"),rootRank,unionRank,targetIn,counts[0],mean(counts),mean(w.agents.map(a=>a.q))],size:[g.n,g.m,g.mean_weight],weighted:g.features,belief,local:[direct,gap,variance,mean(standalone),Math.max(...standalone.slice(1)),standalone[1]],residual:[res,pos,neg,Math.sqrt(sq),positive,later,laterpos],fee:w.fee};
 }
 function epistemicData(api,G,seed,reps){const data=[],T={likelihood_evaluations:0,likelihood_checks:0,graph_mass:0,residual_checks:0,padding:0,fee_pairs:0,fee_shift:0,zero_regret:0,source_oracle:0},pads=new Map(),fees=new Map();
  for(const w of api.worlds(seed,reps)){const f=epistemic(w,G,T),key=[w.K,w.R,w.D,w.profile,w.rep].join(":"),olds=fees.get(key)??[];
   for(const g of olds){check(same(f.weighted,g.weighted)&&same(f.local,g.local),"fee invariance");T.fee_pairs++;check(close(f.residual[0]-g.residual[0],-(w.fee-g.fee)/8),"fee shift");T.fee_shift++}olds.push(f);fees.set(key,olds);
   if(w.R===2){const k=[w.D,w.fee,w.profile,w.rep].join(":"),g=pads.get(k);if(g){check(same(f.local.concat(f.residual),g.local.concat(g.residual))&&same(f.weighted,g.weighted),"padding");T.padding++}else pads.set(k,f)}
   const {rows:rs,full}=api.rows(w),den=w.W*256**(w.D+1),opt=sum(rs.map(r=>r.max));check(opt===sum(full.levels[0].u),"oracle");T.source_oracle++;
   const y=Object.fromEntries(["d1","last","factor"].map(m=>{const loss=opt-sum(rs.map(r=>r.q[r.controls[m]]));check(loss>=0,"regret");if(m==="d1"&&w.D===1){check(loss===0,"one-link zero");T.zero_regret++}return[m,loss/(8*den)]}));data.push({rep:w.rep,D:w.D,stratum:`K${w.K}_R${w.R}_D${w.D}`,...f,y});
  }return{data,tests:T};
 }
 return{reactionData,epistemicData};
}
function prediction(data,domain){
 const fs={mean:()=>[],structural:r=>r.base,size:r=>r.base.concat(r.size),local:r=>r.base.concat(r.size,r.local),directed:r=>r.base.concat(r.size,r.local,r.residual)};
 if(domain==="reaction")fs.spectral=r=>r.base.concat(r.size,r.unit,r.weighted);else{fs.spectral=r=>r.base.concat(r.size,r.weighted);fs.belief=r=>r.base.concat(r.size,r.belief)}
 const tapes=[...new Set(data.map(r=>r.rep))],out={};
 for(const y of Object.keys(data[0].y)){const results={};
  for(const [name,feature] of Object.entries(fs)){const pred=Array(data.length),per_tape=[];let se=0,ae=0,baseSe=0,deepSe=0,deepN=0;
   for(const rep of tapes){const train=data.filter(r=>r.rep!==rep),model=fit(train,feature,y);let s=0,n=0;
    for(let i=0;i<data.length;i++){const r=data[i];if(r.rep!==rep)continue;const p=model.predict(r),v=r.y[y],err=(p-v)**2;check(Number.isFinite(p),"prediction");pred[i]=p;s+=err;ae+=Math.abs(p-v);baseSe+=(model.mean-v)**2;n++;if(r.D>=2){deepSe+=err;deepN++}}se+=s;per_tape.push({rep,n,rmse:Math.sqrt(s/n)})}
   results[name]={rmse:Math.sqrt(se/data.length),mae:ae/data.length,r2:baseSe?1-se/baseSe:null,deep_rmse:deepN?Math.sqrt(deepSe/deepN):null,per_tape,...stratified(data,pred,y)};
  }
  for(const r of Object.values(results)){r.relative_reduction=1-r.rmse/results.size.rmse;r.tapes_improved=r.per_tape.filter((t,i)=>t.rmse<results.size.per_tape[i].rmse-1e-12).length;r.relative_vs_local=1-r.rmse/results.local.rmse;r.relative_vs_spectral=1-r.rmse/results.spectral.rmse}out[y]=results;
 }
 const v=out.d1.directed;return{outcomes:out,primary:{relative_reduction:v.relative_reduction,tapes_improved:v.tapes_improved,tapes:tapes.length,pass:v.relative_reduction>=.05&&v.tapes_improved>=.75*tapes.length,relative_vs_local:v.relative_vs_local,relative_vs_spectral:v.relative_vs_spectral}};
}
function run(r18,r20,r21,old){
 const {reactionData,epistemicData}=geometry(),cohorts={},baseline_checks=[];
 for(const [name,rs,es] of [["original",r18.SEED,r20.SEED],["fresh",0x53522218,0x53522220]]){
  const r=reactionData(r18,r21,rs,r18.REPS),e=epistemicData(r20,r21,es,r20.REPS),rp=prediction(r.data,"reaction"),ep=prediction(e.data,"epistemic");
  if(name==="original")for(const [domain,p] of [["reaction",rp],["epistemic",ep]])for(const [y,rs] of Object.entries(p.outcomes)){const a=rs.size.rmse,b=old.prediction[domain].outcomes[y].size.rmse;check(Math.abs(a-b)<=1e-9,"baseline drift");baseline_checks.push({domain,outcome:y,absolute_rmse_diff:Math.abs(a-b)})}
  cohorts[name]={reaction:{seed:rs,worlds:r.data.length,tests:r.tests,prediction:rp},epistemic:{seed:es,worlds:e.data.length,tests:e.tests,prediction:ep}};
 }
 const gate={reaction:cohorts.original.reaction.prediction.primary.pass&&cohorts.fresh.reaction.prediction.primary.pass,epistemic:cohorts.original.epistemic.prediction.primary.pass&&cohorts.fresh.epistemic.prediction.primary.pass};return{schema:"srg22.receipt.v1",cohorts,baseline_checks,gate,promote:gate.reaction&&gate.epistemic};
}
export {run};
