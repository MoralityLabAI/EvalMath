// NFAS-02 exact finite policy and support-function oracle.
// node scripts/verify_nfas02.mjs --check
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
function runNFAS02(){
 const assert=(x,msg)=>{if(!x)throw Error(msg)};
 const gcd=(a,b)=>{a=Math.abs(a);b=Math.abs(b);while(b){[a,b]=[b,a%b]}return a||1};
 const frac=(a,b)=>{const g=gcd(a,b);return `${a/g}/${b/g}`};
 const bit=(m,i)=>(m>>i)&1;
 const modes=["independent","failure_first","success_first"];
 const den=32*64; // 4 latent states * 4 value states * 8^2 noise * 2 order
 function states(weights,a,mode){
   const rows=[];
   for(let x=0;x<4;x++)for(let y=0;y<4;y++)for(let v=0;v<4;v++)for(let o=0;o<2;o++){
     const h=bit(x^y,0)+bit(x^y,1);
     const w0=a**h*(8-a)**(2-h);
     const u=bit(x,o),z=bit(x,1-o);
     const ow=mode==="independent"||u===z?1:((mode==="failure_first"?u>z:u<z)?2:0);
     const w=w0*ow;if(w===0)continue;
     const values=weights.map((pair,i)=>pair[bit(v,i)]);
     rows.push({x,y,v,o,w,online:o*4+bit(y,o)*2+bit(v,o),offline:o*16+y*4+v, acts:[o,1-o].map(i=>({u:values[i]*(1-bit(x,i)),r:bit(x,1-i)}))});
   }
   assert(rows.reduce((s,e)=>s+e.w,0)===den,"normalization");
   return rows;
 }
 function bins(rows,key,size){
   const cells=Array.from({length:size},()=>[[0,0],[0,0]]);
   for(const e of rows)for(let k=0;k<2;k++){cells[e[key]][k][0]+=e.w*e.acts[k].u;cells[e[key]][k][1]+=e.w*e.acts[k].r;}
   return cells;
 }
 function evaluate(rows,choose,key="online"){
   let u=0,r=0;
   for(const e of rows){const a=e.acts[choose(e[key])];u+=e.w*a.u;r+=e.w*a.r;}
   return {u,r};
 }
 function optimum(cells,p,q){
   let u=0,r=0;const choices=[];
   for(const [a,b] of cells){
     const sa=q*a[0]-p*a[1],sb=q*b[0]-p*b[1];
     const k=sa>sb||sa===sb&&a[1]<=b[1]?0:1;
     const selected=k?b:a;u+=selected[0];r+=selected[1];choices.push(k);
   }
   return {u,r,choices};
 }
 function pareto(points){
   const best=new Map();
   for(const p of points)if(!best.has(p.r)||best.get(p.r).u<p.u)best.set(p.r,p);
   const ordered=[...best.values()].sort((a,b)=>a.r-b.r);
   let u=-Infinity;return ordered.filter(p=>{if(p.u<=u)return false;u=p.u;return true});
 }
 function frontier(cells){
   const slopes=new Map([["0/1",[0,1]]]);
   for(const [a,b] of cells){let p=a[0]-b[0],q=a[1]-b[1];if(q===0||p*q<=0)continue;if(q<0){p=-p;q=-q}const g=gcd(p,q);slopes.set(frac(p,q),[p/g,q/g]);}
   const breaks=[...slopes.values()].sort((a,b)=>a[0]*b[1]-b[0]*a[1]);
   const probes=breaks.slice();
   for(let i=1;i<breaks.length;i++){const [a,b]=breaks[i-1],[c,d]=breaks[i];probes.push([a+c,b+d]);}
   const last=breaks.at(-1);probes.push([last[0]+last[1],last[1]]);
   return pareto(probes.map(([p,q])=>optimum(cells,p,q))).map(({u,r})=>({u,r}));
 }
 const format=({u,r})=>({utility:frac(u,den),residual:frac(r,den)});
 function maskPolicy(m){return k=>bit(m,k);}
 function maskFrom(choices){return choices.reduce((m,k,i)=>m+(k<<i),0);}
 const grid=[0,2,4]; // epsilon 0, 1/4, 1/2
 const types=[[[1,3],[1,3]],[[1,5],[2,6]]];
 let instances=[],policyChecks=0,supportChecks=0,baselineChecks=0;
 for(const weights of types)for(const a of grid){
   const byMode={};
   for(const mode of modes){
     const rows=states(weights,a,mode),online=bins(rows,"online",8),offline=bins(rows,"offline",32);
     const policies=Array.from({length:256},(_,m)=>({...evaluate(rows,maskPolicy(m)),m}));
     for(const p of policies){
       let u=0,r=0;for(let k=0;k<8;k++){const t=online[k][bit(p.m,k)];u+=t[0];r+=t[1];}
       assert(u===p.u&&r===p.r,"policy aggregation");policyChecks++;
     }
     const fOn=frontier(online),fOff=frontier(offline);
     for(const [p,q] of [[0,1],[1,2],[1,1],[2,1],[4,1],[8,1],[64,1]]){
       const on=optimum(online,p,q),off=optimum(offline,p,q);
       const brute=Math.max(...policies.map(t=>q*t.u-p*t.r));
       assert(q*on.u-p*on.r===brute,"online support");
       assert(q*off.u-p*off.r>=brute,"offline domination");
       assert(Math.max(...fOn.map(t=>q*t.u-p*t.r))===brute,"online frontier support");
       assert(Math.max(...fOff.map(t=>q*t.u-p*t.r))===q*off.u-p*off.r,"offline frontier support");
       supportChecks++;
     }
     // Always audit the first or second identity independently of order.
     for(let i=0;i<2;i++){
       const fixed=evaluate(rows,k=>(k>>2)===i?0:1);
       assert(fixed.r===den/2&&fixed.u*4===den*(weights[i][0]+weights[i][1]),"fixed audit baseline");
       baselineChecks++;
     }
     byMode[mode]={rows,online,offline,policies,fOn,fOff};
   }
   const blind=byMode.independent;
   const frozen=maskFrom(optimum(blind.online,2,1).choices);
   const frozenTransfer=Object.fromEntries(modes.map(mode=>[mode,format(byMode[mode].policies[frozen])]));
   const robust=pareto(blind.policies.map(({m})=>({m,u:Math.min(...modes.map(k=>byMode[k].policies[m].u)),r:Math.max(...modes.map(k=>byMode[k].policies[m].r))})));
   const robust2=robust.reduce((best,v)=>v.u-2*v.r>best.u-2*best.r?v:best,robust[0]);
   // This robust certificate uses a deterministic common policy and the
   // rectangle (minimum utility, maximum residual), not min(U-lambda R).
   const first=Object.fromEntries(modes.map(k=>[k,format(byMode[k].policies[0])]));
   const second=Object.fromEntries(modes.map(k=>[k,format(byMode[k].policies[255])]));
   instances.push({weights,epsilon:frac(a,8),frontiers:Object.fromEntries(modes.map(k=>[k,{online:byMode[k].fOn.map(format),offline:byMode[k].fOff.map(format),lambda2_online:format(optimum(byMode[k].online,2,1)),lambda2_offline:format(optimum(byMode[k].offline,2,1))}])),blind_lambda2_mask:frozen,frozen_transfer:frozenTransfer,always_first:first,always_second:second,robust_deterministic_pareto:robust.map(({m,u,r})=>({mask:m,...format({u,r})})),robust_lambda2:{mask:robust2.m,...format(robust2),by_mode:Object.fromEntries(modes.map(k=>[k,format(byMode[k].policies[robust2.m])]))}});
 }
 // Two identical independent sequential blocks with fixed quota 1 in each.
 // Full frontier is the Minkowski sum; at fixed lambda, local choices
 // suffice (past block information is independent of the next block).
 // Double points from the single-block symmetric instance.
 const base=instances.find(i=>i.epsilon==="1/4");
 const twice=s=>{const [a,b]=s.split("/").map(Number);return frac(2*a,b)};
 const twoBlock=Object.fromEntries(modes.map(k=>[k,Object.fromEntries(["online","offline"].map(key=>[key,base.frontiers[k][key].map(p=>({utility:twice(p.utility),residual:twice(p.residual)}))]))]));
 // Structural side-channel witness: order alone, no observation of X:
 // failure-first audit first leaves both-fail cases (1/4) unverified;
 // success-first audit first leaves any-fail cases (3/4) unverified.
 const pure=instances.find(i=>i.epsilon==="1/2");
 assert(pure.always_first.failure_first.residual==="1/4","failure-first witness");
 assert(pure.always_first.success_first.residual==="3/4","success-first witness");
 return {schema:"nfas-02-v1",probability_denominator:den,policy_checks:policyChecks,support_checks:supportChecks,fixed_baseline_checks:baselineChecks,instances,two_block_identical_frontiers:twoBlock};
}
const bytes=readFileSync(fileURLToPath(import.meta.url));
const source_git_blob_sha=createHash("sha1").update("blob "+bytes.length+"\0").update(bytes).digest("hex");
const receipt={source_git_blob_sha,...runNFAS02()};
if(process.argv.includes("--check")){
 const expected=JSON.parse(readFileSync(new URL("../output/nfas02.json",import.meta.url),"utf8"));
 if(JSON.stringify(expected)!==JSON.stringify(receipt))throw Error("receipt mismatch");
 console.log("NFAS-02 receipt verified");
}else console.log(JSON.stringify(receipt,null,2));
