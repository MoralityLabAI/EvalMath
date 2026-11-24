// NFAS-01: exact finite oracles and certified entropy intervals.
// Run: node scripts/verify_nfas01.mjs [--check]
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
function runNFAS(){
  const check=(v,m)=>{if(!v)throw Error(m)};
  const S=10n**18n, K=24;
  const ceil=(a,b)=>(a+b-1n)/b;
  function series(a,b){
    let lo=0n, hi=0n, an=a, bn=b;
    for(let j=0;j<K;j++){
      const numerator=2n*S*an, denominator=bn*BigInt(2*j+1);
      lo+=numerator/denominator;hi+=ceil(numerator,denominator);
      an*=a*a;bn*=b*b;
    }
    // t <= 1/3; omitted tail < 10^-18 (for K=24).
    return [lo,hi+1n];
  }
  const ln2=series(1n,3n), logCache=new Map([[1,[0n,0n]]]), entropyCache=new Map();
  function ln(x){
    if(logCache.has(x))return logCache.get(x);
    let d=1,k=0;while(2*d<=x){d*=2;k++;}
    const [l,h]=series(BigInt(x-d),BigInt(x+d));
    const out=[l+BigInt(k)*ln2[0],h+BigInt(k)*ln2[1]];
    logCache.set(x,out);return out;
  }
  function ent(a,d){
    if(a===0||a===d)return [0n,0n];
    a=Math.min(a,d-a);
    const key=a+"/"+d;if(entropyCache.has(key))return entropyCache.get(key);
    const [l,h]=ln(d), [al,ah]=ln(a),[bl,bh]=ln(d-a);
    const A=BigInt(a),B=BigInt(d-a),D=BigInt(d);
    const out=[l-ceil(A*ah+B*bh,D),h-(A*al+B*bl)/D];
    entropyCache.set(key,out);return out;
  }
  const pop=x=>{let k=0;while(x){x&=x-1;k++;}return k};
  function transform(f,n,a,b){
    const v=f.slice();
    for(let i=0;i<n;i++){
      const step=1<<i;
      for(let j=0;j<v.length;j+=2*step)for(let k=0;k<step;k++){
        const l=v[j+k],r=v[j+k+step];v[j+k]=(b-a)*l+a*r;v[j+k+step]=a*l+(b-a)*r;
      }
    }
    return v;
  }
  function brutePosterior(f,n,a,b){
    return f.map((_,y)=>f.reduce((z,fx,x)=>{const h=pop(x^y);return z+fx*a**h*(b-a)**(n-h)},0));
  }
  let census=[], total=0, direct=0;
  for(let n=1;n<=4;n++){
    const N=1<<n;
    const limit=2**(N-1);
    for(let a=1;a<=3;a++){
      const b=8,D=b**n;
      const e=ent(a,b), boundLo=ln2[0]-e[1];
      let strict=0, equal=0, unresolved=0;
      const coordMasks=new Set();
      for(let i=0;i<n;i++){let mask=0;for(let x=0;x<N;x++)if((x>>i)&1)mask+=2**x;coordMasks.add(mask);}
      for(let m=0;m<limit;m++){
        // Take representative with f(0)=0. Complement gives second function.
        const mask=2*m;
        const f=Array.from({length:N},(_,x)=>(mask>>x)&1);
        const p=f.reduce((s,x)=>s+x,0);
        const v=transform(f,n,a,b);
        if(n<=3 || m%257===0){
          check(v.every((x,i)=>x===brutePosteriorOnce(f,n,a,b,i)),"posterior transform mismatch");direct+=2;
        }
        if(coordMasks.has(mask)){
          check(v.every(x=>x===a*D/b||x===(b-a)*D/b),"coordinate equality witness");
          check(p===N/2,"coordinate balance");equal+=2;continue;
        }
        let condLo=0n;for(const z of v)condLo+=ent(z,D)[0];
        const miHi=ent(p,N)[1]-floorDiv(condLo,BigInt(N));
        if(miHi<boundLo)strict+=2;else unresolved+=2;
      }
      check(strict+equal+unresolved===2**N,"census size");
      check(equal===2*n,"coordinate count");
      check(unresolved===0,"unresolved entropy comparison");
      census.push({n,epsilon:`${a}/8`,functions:2**N,strict,equal,unresolved});total+=2**N;
    }
  }
  function floorDiv(a,b){return a>=0n?a/b:-ceil(-a,b)}
  function brutePosteriorOnce(f,n,a,b,y){
    let s=0;for(let x=0;x<f.length;x++){const h=pop(x^y);s+=f[x]*a**h*(b-a)**(n-h)}return s;
  }
  const gcd=(a,b)=>{while(b){[a,b]=[b,a%b]}return a};
  const frac=(a,b)=>{let g=gcd(a,b);return `${a/g}/${b/g}`};
  function comb(n,k){let x=1;for(let i=1;i<=k;i++)x=x*(n-i+1)/i;return x}
  function groupNum(n,r,a,b){let s=0;for(let k=0;k<=n;k++)s+=comb(n,k)*Math.min(k,r);return a*r*2**n+(b-2*a)*s}
  function riskFormula(groups,a,b){
    let n=groups.reduce((s,g)=>s+g[0],0),num=0;
    for(const [size,r] of groups)num+=groupNum(size,r,a,b)*2**(n-size);
    return [BigInt(num),BigInt(b*2**n)];
  }
  function riskJoint(groups,a,b){
    const n=groups.reduce((s,g)=>s+g[0],0),N=1<<n;
    let start=0;const blocks=groups.map(([size,r])=>{let mask=((1<<size)-1)<<start;start+=size;return [mask,r]});
    const bases=Array.from({length:N},(_,s)=>s).filter(s=>blocks.every(([mask,r])=>pop(mask&s)===r));
    let sum=0n;
    for(let y=0;y<N;y++){
      const numer=Array(n).fill(0);
      for(let x=0;x<N;x++){
        const h=pop(x^y),w=a**h*(b-a)**(n-h);
        for(let i=0;i<n;i++)if(x>>i&1)numer[i]+=w;
      }
      let best=-1;
      for(const s of bases){let score=0;for(let i=0;i<n;i++)if(s>>i&1)score+=numer[i];best=Math.max(best,score);}
      sum+=BigInt(best);
    }
    return [sum,BigInt(N)*BigInt(b)**BigInt(n)];
  }
  let riskCases=0, examples=[];
  for(let n=1;n<=6;n++){
    const cases=[];
    for(let r=0;r<=n;r++)cases.push([[n,r]]);
    for(let split=1;split<n;split++)for(let r=0;r<=split;r++)for(let s=0;s<=n-split;s++)cases.push([[split,r],[n-split,s]]);
    for(const groups of cases)for(let a=0;a<=4;a++){
      const b=8,[x,d]=riskFormula(groups,a,b),[y,e]=riskJoint(groups,a,b);
      check(x*e===y*d,"matroid formula mismatch");riskCases++;
    }
  }
  for(const groups of [[[8,1]],[[8,2]],[[8,8]],[[4,1],[4,1]],[[4,2],[4,0]]]){
    const [x,d]=riskFormula(groups,2,8),r=groups.reduce((s,g)=>s+g[1],0);
    examples.push({groups,epsilon:"1/4",expected_failures:frac(x,d),per_selected:frac(x,d*BigInt(r))});
  }
  // Restricted rank-one, independent two-point values. Threshold is the
  // maximum of independent samples. Worst order takes smallest qualifier.
  const weights=[1,2,4,8],N=1<<weights.length;
  const values=s=>weights.filter((_,i)=>s>>i&1);
  let worst=0n,best=0n,opt=0n,reverseCases=0;
  function permute(v){
    if(v.length===0)return [[]];
    return v.flatMap((x,i)=>permute(v.filter((_,j)=>i!==j)).map(t=>[x,...t]));
  }
  const orders=permute([0,1,2,3]);
  for(let s=0;s<N;s++)for(let v=0;v<N;v++){
    const t=Math.max(0,...values(s)),live=values(v),qual=live.filter(x=>x>t);
    const w=qual.length?Math.min(...qual):0,b=qual.length?Math.max(...qual):0;
    const outcomes=orders.map(order=>{for(const i of order)if((v>>i&1)&&weights[i]>t)return weights[i];return 0});
    check(w===Math.min(...outcomes)&&b===Math.max(...outcomes),"order oracle mismatch");reverseCases+=orders.length;
    worst+=BigInt(w);best+=BigInt(b);opt+=BigInt(Math.max(0,...live));
  }
  return {schema:"nfas-01-v1",census,boolean_cases:total,independent_transform_cases:direct,matroid_cases:riskCases,examples,threshold:{weights,scenarios:N*N,orders_checked:reverseCases,worst_expected:frac(worst,BigInt(N*N)),best_expected:frac(best,BigInt(N*N)),offline_expected:frac(opt,BigInt(N*N)),worst_ratio:frac(worst,opt)},side_channel:{epsilon:"1/2",m:8,blind_risk:"1/2",order_reveals_error_candidate_risk:"255/256"}};
}
const file = fileURLToPath(import.meta.url);
const bytes = readFileSync(file);
const gitBlobSha = createHash("sha1").update("blob "+bytes.length+"\0").update(bytes).digest("hex");
const receipt = {source_git_blob_sha:gitBlobSha, ...runNFAS()};
if(process.argv.includes("--check")){
 const expected=JSON.parse(readFileSync(new URL("../output/nfas01.json", import.meta.url),"utf8"));
 if(JSON.stringify(receipt)!==JSON.stringify(expected))throw Error("receipt mismatch");
 console.log("NFAS-01 receipt verified");
}else console.log(JSON.stringify(receipt,null,2));
