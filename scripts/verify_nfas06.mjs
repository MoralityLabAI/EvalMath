// NFAS-06 exact endpoint certificates and fixed-marginal interpolation.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
function nfas06(){
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const orders=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
 const corr=[[[0,0,0],[0,0,1]],[[0,1,1],[1,0,0]],[[1,1,0],[0,1,0]]];
 const local=Array.from({length:3},(_,i)=>corr.map(([y,g])=>[y[i],g[i]]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]));
 const worlds=[];
 for(const a of local[0])for(const b of local[1])for(const c of local[2])worlds.push([[a[0],b[0],c[0]],[a[1],b[1],c[1]]]);
 const isCorr=worlds.map(w=>corr.some(v=>String(v)===String(w)));
 assert(isCorr.filter(Boolean).length===3,"correlation support");
 const first=Array.from({length:6},(_,i)=>[i>>1,i&1]);
 const keys=first.concat(first.flatMap(a=>first.filter(b=>a[0]!==b[0]).map(b=>a.concat(b))));
 const idx=k=>keys.findIndex(h=>String(h)===String(k));
 const gcd=(a,b)=>{while(b)[a,b]=[b,a%b];return Math.abs(a)||1};
 const frac=(a,b)=>{const g=gcd(a,b);return `${a/g}/${b/g}`};
 // Exact integer doubled stopping realization. x_h and z_hj share denominator 2.
 const p=Array(30).fill(0);
 for(const j of [0,3,4,7,8,11,12,14,16,18,20,22,25,26,29])p[j]=1;
 for(let j=0;j<30;j++){
   assert(p[j]>=0&&p[j]<=2,"stop interval");
   if(j>=6)assert(p[j]+p[idx(keys[j].slice(0,2))]<=2,"stop flow");
 }
 function direct(policy,d){
   return worlds.map(([y,g])=>Math.min(...orders.map(([i,j,k])=>{
     const x=policy[idx([i,y[i]])],z=policy[idx([i,y[i],j,y[j]])];
     return x*g[i]+z*g[j]+(d-x-z)*g[k];
   })));
 }
 const scores=direct(p,2);
 const P=scores.reduce((s,x)=>s+x,0),C=scores.reduce((s,x,i)=>s+(isCorr[i]?x:0),0);
 assert(P===20&&C===3,"private endpoint values");
 // LP with 30 realization variables and 27 lower bound variables.
 const A=[],B=[],N=57;
 for(let j=0;j<30;j++){
   const row=Array(N).fill(0);row[j]=1;
   if(j>=6)row[idx(keys[j].slice(0,2))]=1;
   A.push(row);B.push(1);
 }
 for(let w=0;w<worlds.length;w++){
   const [y,g]=worlds[w];
   for(const [i,j,k] of orders){
     const row=Array(N).fill(0);
     row[30+w]=1;row[idx([i,y[i]])]=g[k]-g[i];row[idx([i,y[i],j,y[j]])]=g[k]-g[j];
     A.push(row);B.push(g[k]);
   }
 }
 const productDual=[30,36,42,48,54,60,67,72,78,84,91,96,105,110,114,123,126,137,138,145,150,156,165,168,175,183,188];
 const corrDual=[36,40,114,117,176,178];
 function verifyDual(support,weights,den,expected){
   const q=A.map((_,i)=>Number(support.includes(i)));
   for(let j=0;j<N;j++){
     const goal=j<30?0:weights[j-30];
     assert(A.reduce((s,r,i)=>s+q[i]*r[j],0)>=den*goal,"dual inequality "+j);
   }
   const upper=B.reduce((s,b,i)=>s+b*q[i],0);
   assert(upper===expected,"dual objective");
   assert(den*scores.reduce((s,v,i)=>s+v*weights[i],0)===2*upper,"primal dual equality");
   return {nonzero_dual_rows:support,denominator:den,objective:frac(upper,den)};
 }
 const dualP=verifyDual(productDual,worlds.map(()=>1),1,10);
 const dualC=verifyDual(corrDual,isCorr.map(Number),2,3);
 // Public optimality proof: a deterministic policy's score is 1 iff it
 // selects a good item in every permutation. For each first decision mask,
 // represent each still-possible successful world by its conjunction of
 // requirements on second decisions; conflicting requirements are impossible.
 let firstMasks=0,nodes=0,pruned=0,maxProduct=0,maxCorr=0,publicPolicy=null,publicCorrPolicy=null;
 function search(which){
   let best=0,bestPolicy=null,visit=0,prune=0;
   const relevant=worlds.map((_,i)=>i).filter(i=>which==="product"||isCorr[i]);
   const fixed=keys.map(h=>Number(h.length===2?h[0]===0:h[0]!==0&&h[2]===0));
   const v=direct(fixed,1);
   best=relevant.reduce((s,i)=>s+v[i],0);bestPolicy=fixed;
   for(let mask=0;mask<64;mask++){
     firstMasks++;
     const terms=[];
     for(const w of relevant){
       const [y,g]=worlds[w];let must1=0,must0=0,possible=true;
       for(const [i,j,k] of orders){
         if((mask>>idx([i,y[i]]))&1){if(!g[i]){possible=false;break;}continue;}
         if(!g[j]&&!g[k]){possible=false;break;}
         if(g[j]!==g[k]){
           const bit=1<<(idx([i,y[i],j,y[j]])-6);
           if(g[j])must1|=bit;else must0|=bit;
         }
       }
       if(possible&&!(must1&must0))terms.push({must1,must0});
     }
     function dfs(remaining,ones,zeros){
       visit++;
       if(remaining.length<=best){prune++;return}
       const conflicts=Array(24).fill(0);
       let union1=0,union0=0;
       for(const t of remaining){union1|=t.must1;union0|=t.must0;}
       let clash=union1&union0;
       if(!clash){
         best=remaining.length;
         const policy=Array.from({length:30},(_,i)=>i<6?((mask>>i)&1):((union1>>(i-6))&1));
         // zero unreachable second decisions (mandatory realization flow).
         for(let j=6;j<30;j++)if(policy[idx(keys[j].slice(0,2))])policy[j]=0;
         assert(relevant.reduce((s,i)=>s+direct(policy,1)[i],0)===best,"deterministic witness");
         bestPolicy=policy;return;
       }
       for(let j=0;j<24;j++)if(clash&(1<<j)){
         const bit=1<<j;let a=0,b=0;
         for(const t of remaining){if(t.must1&bit)a++;if(t.must0&bit)b++;}
         conflicts[j]=Math.min(a,b);
       }
       let j=conflicts.indexOf(Math.max(...conflicts));const bit=1<<j;
       const one=remaining.filter(t=>!(t.must0&bit)).map(t=>({must1:t.must1&~bit,must0:t.must0}));
       const zero=remaining.filter(t=>!(t.must1&bit)).map(t=>({must1:t.must1,must0:t.must0&~bit}));
       // Preserve already assigned bits in final witness.
       function rec(rem,o,z){
         visit++;
         if(rem.length<=best){prune++;return}
         let u=0,v=0;for(const t of rem){u|=t.must1;v|=t.must0;}
         let x=u&v;
         if(!x){
           best=rem.length;
           const policy=Array.from({length:30},(_,i)=>i<6?((mask>>i)&1):(((u|o)>>(i-6))&1));
           for(let j=6;j<30;j++)if(policy[idx(keys[j].slice(0,2))])policy[j]=0;
           const score=direct(policy,1);
           assert(relevant.reduce((s,i)=>s+score[i],0)===best,"public witness");
           bestPolicy=policy;return;
         }
         let bit=x&-x;
         rec(rem.filter(t=>!(t.must0&bit)).map(t=>({must1:t.must1&~bit,must0:t.must0})),o|bit,z);
         rec(rem.filter(t=>!(t.must1&bit)).map(t=>({must1:t.must1,must0:t.must0&~bit})),o,z|bit);
       }
       rec(one,ones|bit,zeros);rec(zero,ones,zeros|bit);
     }
     dfs(terms,0,0);
   }
   const score=direct(bestPolicy,1);
   assert(relevant.reduce((s,i)=>s+score[i],0)===best,"public direct");
   nodes+=visit;pruned+=prune;
   return {value_count:best,policy:bestPolicy,nodes:visit,pruned:prune};
 }
 const pubP=search("product"),pubC=search("correlated");
 assert(pubP.value_count===9&&pubC.value_count===1,"public endpoints");
 // Fixed audit A is simultaneously optimal; all marginals are preserved.
 const fixed=keys.map(h=>Number(h.length===2?h[0]===0:h[0]!==0&&h[2]===0));
 const fs=direct(fixed,1);
 assert(fs.reduce((s,x)=>s+x,0)===9&&fs.reduce((s,x,i)=>s+(isCorr[i]?x:0),0)===1,"common public optimum");
 const grid=[];
 for(let a=0;a<=20;a++){
   // P_alpha = (1-alpha) U_27 + alpha U_3.
   const weights=isCorr.map(x=>20-a+9*a*Number(x)),D=540;
   assert(weights.reduce((s,x)=>s+x,0)===D,"normalized");
   for(let i=0;i<3;i++)for(const type of local[i]){
     assert(worlds.reduce((s,[y,g],j)=>s+(y[i]===type[0]&&g[i]===type[1]?weights[j]:0),0)===D/3,"fixed marginal");
   }
   const privateNumerator=scores.reduce((s,v,i)=>s+v*weights[i],0);
   const publicNumerator=fs.reduce((s,v,i)=>s+v*weights[i],0);
   assert(privateNumerator===400+7*a&&publicNumerator===180,"affine envelope");
   grid.push({alpha:frac(a,20),private:frac(privateNumerator,2*D),public:frac(publicNumerator,D),gap:frac(privateNumerator-2*publicNumerator,2*D)});
 }
 return {schema:"nfas-06-v1",local_types:local,worlds:worlds.length,correlated_worlds:3,product_private:"10/27",product_public:"1/3",correlated_private:"1/2",correlated_public:"1/3",private_realization_doubled:p,private_scores_doubled:scores,dual_product:dualP,dual_correlated:dualC,public_product:pubP,public_correlated:pubC,first_masks:firstMasks,search_nodes:nodes,pruned_nodes:pruned,grid};
}
const bytes=readFileSync(fileURLToPath(import.meta.url));
const source_git_blob_sha=createHash("sha1").update("blob "+bytes.length+"\0").update(bytes).digest("hex");
const receipt={source_git_blob_sha,...nfas06()};
if(process.argv.includes("--check")){
 const expected=JSON.parse(readFileSync(new URL("../output/nfas06.json",import.meta.url),"utf8"));
 if(JSON.stringify(receipt)!==JSON.stringify(expected))throw Error("receipt mismatch");
 console.log("NFAS-06 receipt verified");
}else console.log(JSON.stringify(receipt,null,2));
