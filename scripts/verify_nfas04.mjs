// NFAS-04: exact rational LP certificates and complete-history public-policy search.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
function nfas04(){
 const check=(v,m)=>{if(!v)throw Error(m)};
 const perms=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
 const clean=[[[0,0,0],2],[[0,1,1],0],[[1,1,0],1]];
 const signals=Array.from({length:8},(_,v)=>[v>>2&1,v>>1&1,v&1]);
 const first=Array.from({length:6},(_,i)=>[i>>1,i&1]);
 const keys=first.concat(first.flatMap(a=>first.filter(b=>a[0]!==b[0]).map(b=>a.concat(b))));
 const idx=k=>keys.findIndex(x=>String(x)===String(k));
 const baseCert={pden:2,p:[[0,1],[3,1],[4,1],[8,1],[11,2],[16,2],[18,1],[25,1],[26,2],[30,64],[31,64],[32,64]],dden:2,q:[[18,64],[30,1],[34,1],[36,1],[38,1],[44,1],[46,1]]};
 const certs=[
 ...["full","latent","signal"].map(mode=>({a:0,mode,...baseCert})),
 {a:0,mode:"blind",pden:1,p:[[8,1],[11,1],[16,1],[18,1],[25,1],[26,1],[30,128]],dden:1,q:[[11,64],[30,1]]},
 {a:1,mode:"full",pden:1,p:[[4,1],[5,1],[8,1],[9,1],[12,1],[13,1],[16,1],[17,1],[20,1],[21,1],[30,27],[31,9],[32,9],[33,3],[34,9],[35,3],[36,3],[37,1]],dden:27,q:[[30,1],[31,10],[33,3],[34,13],[37,9],[40,18],[42,6],[44,21],[51,27],[54,27],[64,27],[68,27],[75,27],[81,27],[84,27],[95,27],[96,7],[98,7],[99,4],[101,9],[106,27],[108,27],[119,27],[120,18],[122,9],[127,27],[132,27],[138,6],[139,21],[145,27],[150,18],[152,9],[156,27],[164,14],[166,1],[167,12],[173,27]]},
 {a:1,mode:"latent",pden:63,p:[[0,31],[1,15],[2,15],[3,31],[4,31],[5,15],[8,32],[9,32],[11,48],[12,16],[14,16],[16,48],[18,32],[19,32],[24,32],[25,32],[26,48],[29,16],[30,1728],[31,1728],[32,1728]],dden:7,q:[[8,96],[9,32],[18,96],[19,32],[24,32],[25,96],[31,3],[32,1],[34,3],[36,3],[38,3],[41,1],[43,1],[44,3],[47,3]]},
 {a:1,mode:"signal",pden:2,p:[[0,1],[3,1],[4,1],[8,1],[9,1],[11,2],[16,2],[18,1],[19,1],[24,1],[25,1],[26,2],[30,30],[31,18],[32,18],[33,30],[34,18],[35,6],[36,30],[37,18]],dden:2,q:[[30,1],[34,1],[36,2],[42,2],[48,1],[51,1],[56,2],[60,2],[68,1],[70,1],[73,2]]},
 {a:1,mode:"blind",pden:1,p:[[0,1],[4,1],[11,1],[16,1],[18,1],[19,1],[26,1],[30,96]],dden:1,q:[[11,32],[30,1]]},
 {a:2,mode:"full",pden:1,p:[[4,1],[5,1],[8,1],[9,1],[12,1],[13,1],[16,1],[17,1],[20,1],[21,1],[30,8],[31,8],[32,8],[33,8],[34,8],[35,8],[36,8],[37,8]],dden:1,q:[[31,1],[36,1],[46,1],[48,1],[55,1],[61,1],[68,1],[73,1],[78,1],[84,1],[95,1],[96,1],[102,1],[108,1],[116,1],[120,1],[127,1],[132,1],[138,1],[146,1],[151,1],[157,1],[167,1],[169,1]]},
 {a:2,mode:"latent",pden:1,p:[[0,1],[5,1],[12,1],[13,1],[15,1],[16,1],[17,1],[19,1],[22,1],[23,1],[30,32],[31,32]],dden:1,q:[[34,1],[41,1],[47,1]]},
 {a:2,mode:"signal",pden:1,p:[[30,8],[31,8],[32,8],[33,8],[34,8],[35,8],[36,8],[37,8]],dden:1,q:[[30,1],[36,1],[42,1],[48,1],[54,1],[60,1],[66,1],[72,1]]},
 {a:2,mode:"blind",pden:1,p:[[30,64]],dden:1,q:[[30,1]]}];
 const gcd=(a,b)=>{while(b)[a,b]=[b,a%b];return Math.abs(a)||1};
 const frac=(a,b)=>{let g=gcd(a,b);return `${a/g}/${b/g}`};
 const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
 const dense=(pairs,n)=>{const v=Array(n).fill(0);for(const [i,x] of pairs){check(i>=0&&i<n&&v[i]===0&&Number.isSafeInteger(x)&&x>=0,"sparse cert");v[i]=x}return v};
 function group(a,mode){
   const groups=new Map();
   clean.forEach(([x,g],w)=>signals.forEach(y=>{
     const h=x.filter((b,i)=>b!==y[i]).length,m=a**h*(4-a)**(3-h);
     if(!m)return;
     const key=mode==="full"?`${w}:${y}`:mode==="latent"?String(w):mode==="signal"?String(y):"all";
     if(!groups.has(key))groups.set(key,[]);
     groups.get(key).push({y,g,m,w});
   }));
   const out=[...groups.values()];check(out.flat().reduce((a,b)=>a+b.m,0)===192,"mass");return out;
 }
 function lp(groups){
   const n=30+groups.length,A=[],B=[],c=Array(n).fill(0);for(let j=30;j<n;j++)c[j]=1;
   for(let k=0;k<30;k++){
     const row=Array(n).fill(0);row[k]=1;if(k>=6)row[idx(keys[k].slice(0,2))]=1;
     A.push(row);B.push(1);
   }
   for(let t=0;t<groups.length;t++)for(const [i,j,k] of perms){
     const row=Array(n).fill(0);row[30+t]=1;let b=0;
     for(const {y,g,m} of groups[t]){
       row[idx([i,y[i]])]+=m*(Number(k===g)-Number(i===g));
       row[idx([i,y[i],j,y[j]])]+=m*(Number(k===g)-Number(j===g));
       b+=m*Number(k===g);
     }
     A.push(row);B.push(b);
   }
   return {A,B,c};
 }
 // Deterministic complete-history policies. First actions enumerate 64 masks.
 // Second history choices are solved by exact branch and bound. Each order's
 // optimistic residual sum is an upper bound for every completion.
 function publicOpt(groups,A,B,upper,primal){
   const rows=A.slice(30),b=B.slice(30),n=rows.length;
   let best=-1,bestPolicy=null,nodes=0,pruned=0,masks=0;
   const score=vals=>{let s=0;for(let i=0;i<n;i+=6)s+=Math.min(...vals.slice(i,i+6));return s};
   function evaluate(p){
     const vals=rows.map((r,i)=>b[i]-dot(r.slice(0,30),p));return score(vals);
   }
   for(let i=0;i<3;i++){
     const p=keys.map(k=>Number(k.length===2?k[0]===i:k[0]!==i&&k[2]===i));
     const u=evaluate(p);if(u>best){best=u;bestPolicy=p}
   }
   if(primal.slice(0,30).every(x=>x===0||x===1)){let p=primal.slice(0,30);let u=evaluate(p);if(u>best){best=u;bestPolicy=p}}
   for(let mask=0;mask<64&&best<upper;mask++){
     masks++;
     const p=Array(30).fill(0);
     for(let i=0;i<6;i++)p[i]=mask>>i&1;
     let vals=rows.map((r,i)=>b[i]-dot(r.slice(0,6),p.slice(0,6)));
     const cols=[];
     for(let j=6;j<30;j++){
       if(p[idx(keys[j].slice(0,2))])continue;
       const col=rows.map(r=>-r[j]);if(col.some(x=>x))cols.push({j,col,weight:col.reduce((s,x)=>s+Math.abs(x),0)});
     }
     cols.sort((a,b)=>b.weight-a.weight||a.j-b.j);
     const optimistic=vals.map((v,k)=>v+cols.reduce((s,c)=>s+Math.max(0,c.col[k]),0));
     function dfs(k){
       nodes++;if(score(optimistic)<=best){pruned++;return}
       if(k===cols.length){best=score(vals);bestPolicy=p.slice();return}
       const {j,col}=cols[k];
       for(let i=0;i<n;i++)optimistic[i]-=Math.max(0,col[i]);
       // Choose the larger optimistic branch first.
       for(let i=0;i<n;i++)optimistic[i]+=col[i];
       const hi=score(optimistic);
       for(let i=0;i<n;i++)optimistic[i]-=col[i];
       const lo=score(optimistic);
       for(const a of hi>lo?[1,0]:[0,1]){
         p[j]=a;if(a)for(let i=0;i<n;i++){vals[i]+=col[i];optimistic[i]+=col[i]}
         if(best<upper)dfs(k+1);
         if(a)for(let i=0;i<n;i++){vals[i]-=col[i];optimistic[i]-=col[i]}
       }
       p[j]=0;
       for(let i=0;i<n;i++)optimistic[i]+=Math.max(0,col[i]);
     }
     dfs(0);
   }
   check(bestPolicy!==null&&best===evaluate(bestPolicy)&&best<=upper,"public witness");
   return {value:frac(best,192),mass:best,policy:bestPolicy,first_masks_searched:masks,nodes,pruned,lp_integer_upper:upper};
 }
 const results=[];
 for(const cert of certs){
   const {a,mode,pden,dden}=cert,groups=group(a,mode),{A,B,c}=lp(groups);
   const p=dense(cert.p,c.length),q=dense(cert.q,B.length);
   check(pden>0&&dden>0,"denominators");
   for(let i=0;i<A.length;i++)check(dot(A[i],p)<=B[i]*pden,"primal constraint");
   for(let j=0;j<c.length;j++)check(A.reduce((s,r,i)=>s+r[j]*q[i],0)>=c[j]*dden,"dual constraint");
   const pn=dot(c,p),dn=dot(B,q);
   check(pn*dden===dn*pden,"duality");
   const pub=publicOpt(groups,A,B,Math.floor(pn/pden),p.map(x=>x/pden));
   // Direct independent evaluation of private and public policies, rather
   // than using constraint matrix to compute the expected worst payoff.
   function direct(policy,d){
     let s=0;
     for(const worlds of groups){
       const scores=perms.map(([i,j,k])=>worlds.reduce((sum,{y,g,m})=>{
         const x=policy[idx([i,y[i]])],z=policy[idx([i,y[i],j,y[j]])];
         return sum+m*(x*Number(i===g)+z*Number(j===g)+(d-x-z)*Number(k===g));
       },0));
       s+=Math.min(...scores);
     }
     return s;
   }
   check(direct(p,pden)===pn,"independent private oracle");
   check(direct(pub.policy,1)===pub.mass,"independent public oracle");
   results.push({epsilon:frac(a,4),scheduler:mode,private:frac(pn,192*pden),public:pub.value,gap:frac(pn-pden*pub.mass,192*pden),public_certificate:pub,private_certificate:cert});
 }
 // Information-set nesting holds for private and public games.
 for(let a=0;a<3;a++){
   const r=results.slice(4*a,4*a+4);
   const f=s=>{let [x,y]=s.split("/").map(Number);return x/y};
   for(const k of ["private","public"])check(f(r[0][k])<=Math.min(f(r[1][k]),f(r[2][k]))&&Math.max(f(r[1][k]),f(r[2][k]))<=f(r[3][k]),"filtration order");
 }
 check(results[0].private==="1/2"&&results[0].public==="1/3","strict gap");
 return {schema:"nfas-04-v1",worlds:clean,probability_mass:192,lp_certificates:results.length,public_optimality_checks:results.length,results};
}
const bytes=readFileSync(fileURLToPath(import.meta.url));
const source_git_blob_sha=createHash("sha1").update("blob "+bytes.length+"\0").update(bytes).digest("hex");
const receipt={source_git_blob_sha,...nfas04()};
if(process.argv.includes("--check")){
 const expected=JSON.parse(readFileSync(new URL("../output/nfas04.json",import.meta.url),"utf8"));
 if(JSON.stringify(expected)!==JSON.stringify(receipt))throw Error("receipt mismatch");
 console.log("NFAS-04 receipt verified");
}else console.log(JSON.stringify(receipt,null,2));
