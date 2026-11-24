// NFAS-03 exact primal-dual robust audits and order-coupling oracle.
// node scripts/verify_nfas03.mjs --check
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
function runNFAS03(){
 const check=(v,m)=>{if(!v)throw Error(m)};
 const abs=x=>x<0n?-x:x;
 const gcd=(a,b)=>{a=abs(a);b=abs(b);while(b)[a,b]=[b,a%b];return a||1n};
 const F=(a,b=1n)=>{a=BigInt(a);b=BigInt(b);check(b!==0n,"zero denominator");if(b<0n){a=-a;b=-b}const g=gcd(a,b);return [a/g,b/g]};
 const add=(a,b)=>F(a[0]*b[1]+b[0]*a[1],a[1]*b[1]);
 const sub=(a,b)=>F(a[0]*b[1]-b[0]*a[1],a[1]*b[1]);
 const mul=(a,b)=>F(a[0]*b[0],a[1]*b[1]);
 const cmp=(a,b)=>{const d=a[0]*b[1]-b[0]*a[1];return d<0n?-1:d>0n?1:0};
 const str=a=>a[0]+"/"+a[1];
 const z=F(0),one=F(1);
 const bit=(m,i)=>(m>>i)&1;
 const den=2048n;
 const ZERO=()=>[0n,0n];
 function worlds(weights,a){
   const w=[];
   for(let x=0;x<4;x++)for(let y=0;y<4;y++)for(let v=0;v<4;v++){
     const h=bit(x^y,0)+bit(x^y,1);
     const mass=BigInt(a**h*(8-a)**(2-h));
     if(!mass)continue;
     const vals=weights.map((p,i)=>p[bit(v,i)]);
     w.push({x,y,v,mass,vals,obs:[bit(y,0)*2+bit(v,0),4+bit(y,1)*2+bit(v,1)],u:vals.map((t,i)=>BigInt(t*(1-bit(x,i)))),r:[BigInt(bit(x,1)),BigInt(bit(x,0))]});
   }
   check(w.reduce((s,w)=>s+w.mass,0n)*2n===den,"world normalization");return w;
 }
 function cellScores(ws){
   const cells=Array.from({length:8},()=>Array.from({length:2},()=>[ZERO(),ZERO()])); // cell, action, order kernel
   for(const w of ws)for(let o=0;o<2;o++)for(let k=0;k<2;k++){
     const i=k?1-o:o;
     for(let mode=0;mode<2;mode++){
       const d=bit(w.x,o)-bit(w.x,1-o);
       const m=w.mass*BigInt(d===0?1:(mode===0?d>0:d<0)?2:0);
       const c=cells[w.obs[o]][k][mode];
       c[0]+=m*w.u[i];c[1]+=m*w.r[i];
     }
   }
   return cells;
 }
 function stats(cells,ps){
   const out=[[z,z],[z,z]];
   for(let j=0;j<8;j++)for(let k=0;k<2;k++)for(let mode=0;mode<2;mode++)for(let t=0;t<2;t++)
     out[mode][t]=add(out[mode][t],mul(k?ps[j]:sub(one,ps[j]),F(cells[j][k][mode][t])));
   return out;
 }
 const mix=(a,b,t)=>add(mul(a,t),mul(b,sub(one,t)));
 const min=(a,b)=>cmp(a,b)<=0?a:b;
 const max=(a,b)=>cmp(a,b)>=0?a:b;
 function coefficients(c,lambda,scalar){
   const [a,b]=c;
   const d=a.map((v,i)=>v.map((x,t)=>b[i][t]-x));
   const A=d[0][0]-d[1][0], B=-lambda*(d[0][1]-d[1][1]), C=d[1][0]-lambda*d[1][1];
   return scalar?[A+B,0n,C]:[A,B,C];
 }
 function dual(cells,lambda,t,s){
   let out=z;
   for(const c of cells){
     const v=c.map(([f,g])=>sub(mix(F(f[0]),F(g[0]),t),mul(F(lambda),mix(F(f[1]),F(g[1]),s))));
     out=add(out,max(v[0],v[1]));
   }return out;
 }
 function solve(cells,lambda,scalar){
   const cs=cells.map(c=>coefficients(c,lambda,scalar));
   const points=[];
   if(scalar){
     points.push([z,z],[one,one]);
     for(const [a,,c] of cs)if(a){const t=F(-c,a);if(cmp(t,z)>=0&&cmp(t,one)<=0)points.push([t,t]);}
   }else{
     const lines=[...cs,[1n,0n,0n],[1n,0n,-1n],[0n,1n,0n],[0n,1n,-1n]];
     for(let i=0;i<lines.length;i++)for(let j=i+1;j<lines.length;j++){
       const [a,b,c]=lines[i],[d,e,f]=lines[j];const det=a*e-b*d;if(!det)continue;
       const t=F(b*f-c*e,det),s=F(c*d-a*f,det);
       if([t,s].every(v=>cmp(v,z)>=0&&cmp(v,one)<=0))points.push([t,s]);
     }
   }
   let best=null;
   for(const [t,s] of points){const v=dual(cells,lambda,t,s);if(!best||cmp(v,best.v)<0)best={t,s,v};}
   check(best,"missing dual");
   const {t,s,v}=best;
   const ps=[],ties=[];
   for(let i=0;i<8;i++){
     const [a,b,c]=cs[i];const d=add(add(mul(F(a),t),mul(F(b),s)),F(c));
     ps.push(cmp(d,z)>0?one:z);if(cmp(d,z)===0)ties.push(i);
   }
   // For a minimizer of the dual, the active primal face intersects the
   // complementary-slackness halfspaces. Find a vertex of that intersection.
   // At most two probabilities need be fractional.
   const ds=cells.map(([a,b])=>{
     const delta=(c,j)=>c[0][j]-c[1][j];
     const u=delta(b,0)-delta(a,0),r=delta(b,1)-delta(a,1);
     return scalar?[u-lambda*r]:[u,r];
   });
   function differences(ps){
     const [[uf,rf],[us,rs]]=stats(cells,ps);
     return scalar?[sub(sub(uf,us),mul(F(lambda),sub(rf,rs)))]:[sub(uf,us),sub(rf,rs)];
   }
   function valid(p){
     if(p.some(x=>cmp(x,z)<0||cmp(x,one)>0))return false;
     const d=differences(p);
     const uok=cmp(t,z)===0?cmp(d[0],z)>=0:cmp(t,one)===0?cmp(d[0],z)<=0:cmp(d[0],z)===0;
     if(scalar)return uok;
     const rok=cmp(s,z)===0?cmp(d[1],z)<=0:cmp(s,one)===0?cmp(d[1],z)>=0:cmp(d[1],z)===0;
     return uok&&rok;
   }
   let witness=null;
   outer:for(let m=0;m<2**ties.length;m++){
     const p=ps.slice();ties.forEach((i,j)=>p[i]=bit(m,j)?one:z);
     if(valid(p)){witness=p;break;}
     for(const i of ties){
       const q=p.slice();q[i]=z;const d=differences(q);
       for(let a=0;a<d.length;a++)if(ds[i][a]){
         const cand=q.slice();cand[i]=mul(F(-1n,ds[i][a]),d[a]);
         if(valid(cand)){witness=cand;break outer;}
       }
     }
     if(!scalar)for(let j=0;j<ties.length;j++)for(let k=j+1;k<ties.length;k++){
       const i=ties[j],l=ties[k],q=p.slice();q[i]=q[l]=z;const [du,dr]=differences(q);
       const [a,b]=ds[i],[c,d]=ds[l];const det=a*d-b*c;if(!det)continue;
       q[i]=mul(F(1n,det),sub(mul(F(c),dr),mul(F(d),du)));
       q[l]=mul(F(1n,det),sub(mul(F(b),du),mul(F(a),dr)));
       if(valid(q)){witness=q;break outer;}
     }
   }
   check(witness,"no primal witness");
   const [[uf,rf],[us,rs]]=stats(cells,witness);
   const payoff=scalar?min(sub(uf,mul(F(lambda),rf)),sub(us,mul(F(lambda),rs))):sub(min(uf,us),mul(F(lambda),max(rf,rs)));
   check(cmp(payoff,v)===0,"primal dual gap");
   let deterministic=null;
   for(let m=0;m<256;m++){
     const p=Array.from({length:8},(_,i)=>bit(m,i)?one:z);
     const [[u0,r0],[u1,r1]]=stats(cells,p);
     const val=scalar?min(sub(u0,mul(F(lambda),r0)),sub(u1,mul(F(lambda),r1))):sub(min(u0,u1),mul(F(lambda),max(r0,r1)));
     if(!deterministic||cmp(val,deterministic.v)>0)deterministic={m,v:val};
   }
   const norm=x=>str(mul(x,F(1n,den)));
   return {dual_weights:[str(t),str(s)],action1_probabilities:witness.map(str),value:norm(v),deterministic_value:norm(deterministic.v),deterministic_mask:deterministic.m,gain:norm(sub(v,deterministic.v)),utility_floor:norm(min(uf,us)),risk_ceiling:norm(max(rf,rs)),by_kernel:[{utility:norm(uf),risk:norm(rf)},{utility:norm(us),risk:norm(rs)}],dual_vertices:points.length};
 }
 function payoff(w,i,lambda){return w.u[i]-lambda*w.r[i]}
 function evalOrder(ws,policy,lambda,weights,sampleAware){
   // sample index 0..3, iid copy of value vector, public to the scheduler.
   const independent=0; // use denominator 8192 = 4 samples * 2 orders * 1024 worlds
   let random=0n,full=0n,valuesOnly=0n;
   for(let s=0;s<4;s++){
     const byV=Array.from({length:4},()=>[0n,0n]);
     for(const w of ws){
       const vals=[0,1].map(o=>payoff(w,policy(w,o,s,weights)?1-o:o,lambda));
       random+=w.mass*(vals[0]+vals[1]);
       full+=2n*w.mass*(vals[0]<vals[1]?vals[0]:vals[1]);
       for(let o=0;o<2;o++)byV[w.v][o]+=w.mass*vals[o];
     }
     for(const [a,b] of byV)valuesOnly+=2n*(a<b?a:b);
   }
   check(full<=valuesOnly&&valuesOnly<=random,"scheduler hierarchy");
   const d=4n*den;
   return {independent:str(F(random,d)),values_and_samples_aware:str(F(valuesOnly,d)),full_world_aware:str(F(full,d))};
 }
 function fullChecks(ws,lambda){
   let best=null;
   for(let m=0;m<256;m++){
     let n=0n;
     for(const w of ws){const a=payoff(w,bit(m,w.obs[0])?1:0,lambda),b=payoff(w,bit(m,w.obs[1])?0:1,lambda);n+=w.mass*(a<b?a:b);}
     if(!best||n>best.n)best={m,n};
   }
   // Coupling identity checked independently for 64 deterministic grids
   // of audit-identity probabilities. z_i integer in [0,4].
   let checked=0;
   for(let seed=0;seed<64;seed++){
     const p=Array.from({length:8},(_,i)=>(seed*(i+3)+i*i+Math.floor(seed/7))%5);
     let priv=0n,publicSum=0n;
     for(const w of ws){
       const t0=BigInt(p[w.obs[0]]),t1=BigInt(p[w.obs[1]]);
       const a=payoff(w,0,lambda),b=payoff(w,1,lambda);
       const q0=t0*a+(4n-t0)*b,q1=t1*a+(4n-t1)*b;
       priv+=w.mass*(q0<q1?q0:q1);
       for(let t=1;t<=4;t++){
         const v0=t<=Number(t0)?a:b,v1=t<=Number(t1)?a:b;
         publicSum+=w.mass*(v0<v1?v0:v1);
       }
     }
     check(priv===publicSum&&priv<=4n*best.n,"coupling identity");checked++;
   }
   return {best_value:str(F(best.n,den/2n)),best_mask:best.m,coupling_checks:checked};
 }
 let instances=[],lp=0,couplings=0;
 for(const weights of [[[1,3],[1,3]],[[1,5],[2,6]]])for(const a of [0,2,4]){
   const ws=worlds(weights,a),cells=cellScores(ws);
   const objectives=[];
   for(const lambda of [1n,2n,4n,8n]){
     const scalar=solve(cells,lambda,true),rectangular=solve(cells,lambda,false);lp+=2;
     const full=fullChecks(ws,lambda);couplings+=full.coupling_checks;
     const sampleThreshold=evalOrder(ws,(w,o,s)=>w.vals[o]>Math.max(...weights.map((p,i)=>p[bit(s,i)]))?0:1,lambda,weights,true);
     const fixed=evalOrder(ws,(w,o)=>o===0?0:1,lambda,weights,false);
     objectives.push({lambda:Number(lambda),scalar,rectangular,fully_informed:full,sample_threshold:sampleThreshold,fixed_identity:fixed});
   }
   instances.push({weights,epsilon:str(F(a,8)),objectives});
 }
 return {schema:"nfas-03-v1",lp_certificates:lp,deterministic_comparisons:lp*256,coupling_checks:couplings,instances};
}
const bytes=readFileSync(fileURLToPath(import.meta.url));
const source_git_blob_sha=createHash("sha1").update("blob "+bytes.length+"\0").update(bytes).digest("hex");
const receipt={source_git_blob_sha,...runNFAS03()};
if(process.argv.includes("--check")){
 const expected=JSON.parse(readFileSync(new URL("../output/nfas03.json",import.meta.url),"utf8"));
 if(JSON.stringify(expected)!==JSON.stringify(receipt))throw Error("receipt mismatch");
 console.log("NFAS-03 receipt verified");
}else console.log(JSON.stringify(receipt,null,2));
