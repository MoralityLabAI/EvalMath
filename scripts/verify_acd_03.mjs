// ACD-03 exact invariant synthesis, Node 18+.
import {readFileSync} from 'node:fs';
const run = function run(){
 const must=(x,m)=>{if(!x)throw Error(m)};
 const dims=[5,6,7,8],families=["subspace","weight","full"],arms=["fresh","lazy","linear","quadratic","staged"],caps=[128,512,2048];
 const rng=seed=>{let x=seed>>>0;return n=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)%n}};
 const meter=()=>[0,0,0,0],rd=(c,x)=>(c[0]++,x),wr=(c,o,k,x)=>(c[1]++,o[k]=x),op=(c,x)=>(c[2]++,x),ck=(c,x)=>(c[3]++,x),work=c=>c.reduce((a,b)=>a+b,0);
 const bit=(c,v,i)=>op(c,(v>>>i)&1);
 const bigbit=(c,v,i)=>op(c,(v>>BigInt(i))&1n);
 function applyRaw(a,x,c){
   let v=rd(c,a.b);
   for(let i=0;i<a.cols.length;i++)if(bit(c,x,i))v=op(c,v^rd(c,a.cols[i]));
   return v;
 }
 function make(d,f,split,id){
   const seed=(split==="cal"?1700000:7200000)+10000*d+100*families.indexOf(f)+id+1,r=rng(seed),n=1<<d;
   const cols=Array.from({length:d},(_,i)=>1<<i);
   for(let k=0;k<(split==="cal"?3:9)*d;k++){
     const i=r(d),j=r(d);if(i!==j)cols[i]^=cols[j];
   }
   const off=r(n);
   const enc=Array.from({length:n},(_,x)=>cols.reduce((a,v,i)=>((x>>>i)&1)?a^v:a,off));
   must(new Set(enc).size===n,"noninvertible encoding");
   const dec=[];enc.forEach((v,i)=>dec[v]=i);
   let src=r(n),hidden=[];
   if(f==="weight"){
     const weight=1+r(d-1),perm=Array.from({length:d},(_,i)=>i);
     for(let i=d-1;i>0;i--){const j=r(i+1);[perm[i],perm[j]]=[perm[j],perm[i]]}
     src=perm.slice(0,weight).reduce((v,i)=>v|(1<<i),0);
     for(let i=1;i<d;i++){
       const j=split==="cal"?i-1:0,k=i;
       hidden.push(x=>((x>>>j)^(x>>>k))&1?x^(1<<j)^(1<<k):x);
     }
   }else{
     const rank=f==="full"?d:1+r(d-1);
     for(let i=0;i<rank;i++)hidden.push(x=>x^(1<<i));
   }
   const actions=hidden.map(h=>{
     const fn=x=>enc[h(dec[x])],b=fn(0);
     return {b,cols:Array.from({length:d},(_,i)=>fn(1<<i)^b)};
   });
   const q=rng(seed^0xcafe1234),targets=Array.from({length:n},(_,i)=>i);
   for(let i=n-1;i>0;i--){const j=q(i+1);[targets[i],targets[j]]=[targets[j],targets[i]]}
   return {d,f,split,id,seed,n,s:enc[src],actions,hidden,enc,dec,targets:targets.slice(0,16)};
 }
 function truth(w){
   // Independent orbit using generator-space transitions, with fixed-point set expansion.
   let s=new Set([w.dec[w.s]]);
   for(;;){const next=new Set(s);for(const v of s)for(const h of w.hidden)next.add(h(v));if(next.size===s.size)break;s=next}
   return new Set([...s].map(v=>w.enc[v]));
 }
 function lift(x,d,k,c){
   let z=BigInt(x);
   if(k===2)for(let i=0,j=d;i<d;i++)for(let h=i+1;h<d;h++,j++){
     if(bit(c,x,i)&&bit(c,x,h))z=op(c,z|(1n<<BigInt(j)));
   }
   return z;
 }
 function makeLift(w,k,c){
   const m=k===1?w.d:w.d*(w.d+1)/2;
   const maps=[];
   for(const a of w.actions){
     if(k===1){
       const cols=[];for(const v of a.cols)wr(c,cols,cols.length,BigInt(rd(c,v)));
       wr(c,maps,maps.length,{b:BigInt(rd(c,a.b)),cols});continue;
     }
     const b=lift(rd(c,a.b),w.d,k,c),unit=[],cols=[];
     for(let i=0;i<w.d;i++){
       const v=lift(op(c,a.b^rd(c,a.cols[i])),w.d,k,c);wr(c,unit,i,v);
       wr(c,cols,i,op(c,v^b));
     }
     for(let i=0;i<w.d;i++)for(let j=i+1;j<w.d;j++){
       const x=op(c,op(c,a.b^rd(c,a.cols[i]))^rd(c,a.cols[j]));
       const v=lift(x,w.d,k,c);
       wr(c,cols,cols.length,op(c,op(c,op(c,v^rd(c,unit[i]))^rd(c,unit[j]))^b));
     }
     must(cols.length===m,"lift size");
     wr(c,maps,maps.length,{b,cols});
   }
   return {m,maps};
 }
 function lin(a,x,c){
   let v=0n;
   for(let i=0;i<a.cols.length;i++)if(bigbit(c,x,i))v=op(c,v^rd(c,a.cols[i]));
   return v;
 }
 function af(a,x,c){return op(c,lin(a,x,c)^rd(c,a.b))}
 function reduce(v,b,c){
   for(let i=b.length-1;i>=0;i--)if(bigbit(c,v,i)){
     const row=rd(c,b[i]);if(row!==undefined)v=op(c,v^row);
   }
   return v;
 }
 function add(v,b,q,c){
   v=reduce(v,b,c);
   if(ck(c,v===0n))return false;
   let i=b.length-1;while(!bigbit(c,v,i))i--;
   must(rd(c,b[i])===undefined,"occupied pivot");
   wr(c,b,i,v);wr(c,q,q.length,v);return true;
 }
 function auditHull(o,c){
   const {s,b,maps}=o;
   for(let i=0;i<b.length;i++){
     const v=rd(c,b[i]);if(v===undefined)continue;
     if(!ck(c,(v>>BigInt(i))===1n))return false;
     for(const a of maps)if(!ck(c,reduce(lin(a,v,c),b,c)===0n))return false;
   }
   for(const a of maps)if(!ck(c,reduce(op(c,af(a,s,c)^s),b,c)===0n))return false;
   return true;
 }
 function hull(w,k,c){
   const {m,maps}=makeLift(w,k,c),s=lift(w.s,w.d,k,c),b=new Array(m),q=[];
   for(const a of maps)add(op(c,af(a,s,c)^s),b,q,c);
   for(let i=0;i<q.length;i++){
     const v=rd(c,q[i]);for(const a of maps)add(lin(a,v,c),b,q,c);
   }
   const o={k,m,maps,s,b,rank:q.length};
   must(auditHull(o,c),"invariant audit");
   return o;
 }
 function excluded(w,t,o,c){
   return ck(c,reduce(op(c,lift(t,w.d,o.k,c)^o.s),o.b,c)!==0n);
 }
 function init(w,c){
   const p=[],q=[];wr(c,p,w.s,[-1,-1]);wr(c,q,0,w.s);c[1]++;
   return {p,q,h:0};
 }
 function bfs(w,t,st,c){
   while(rd(c,st.p[t])===undefined&&!ck(c,st.h===st.q.length)){
     const u=rd(c,st.q[st.h]);st.h++;c[1]++;
     for(let j=0;j<w.actions.length;j++){
       const v=applyRaw(rd(c,w.actions[j]),u,c);
       if(rd(c,st.p[v])===undefined){wr(c,st.p,v,[u,j]);wr(c,st.q,st.q.length,v)}
     }
   }
   if(rd(c,st.p[t])!==undefined){
     const p=[],r=[];let u=t;
     while(!ck(c,u===w.s)){const [v,j]=rd(c,st.p[u]);wr(c,r,r.length,j);u=v}
     for(let j=r.length-1;j>=0;j--)wr(c,p,p.length,rd(c,r[j]));
     return {yes:true,p};
   }
   const set=[];for(const v of st.q)wr(c,set,set.length,rd(c,v));
   return {yes:false,set};
 }
 function verify(w,t,z,c){
   if(z.yes){
     let v=w.s;
     for(const j of z.p){
       if(!ck(c,Number.isInteger(j)&&j>=0&&j<w.actions.length))return false;
       v=applyRaw(rd(c,w.actions[j]),v,c);
     }
     return ck(c,v===t);
   }
   const seen=[];
   for(const v of z.set){
     if(!ck(c,Number.isInteger(v)&&v>=0&&v<w.n))return false;
     wr(c,seen,v,true);
   }
   if(!ck(c,rd(c,seen[w.s])===true&&rd(c,seen[t])!==true))return false;
   for(const v of z.set)for(const a of w.actions)if(!ck(c,rd(c,seen[applyRaw(a,v,c)])===true))return false;
   return true;
 }
 function solve(w,p,oracle){
   const c=meter(),cum=[],counts={invariant:0,bfsPositive:0,bfsNegative:0};
   let l=null,q=null,st=null;
   if(p==="linear"||p==="staged")l=hull(w,1,c);
   if(p==="quadratic")q=hull(w,2,c);
   for(const t of w.targets){
     let z=l!==null&&excluded(w,t,l,c);
     if(!z&&p==="staged"&&q===null)q=hull(w,2,c);
     if(!z&&q!==null)z=excluded(w,t,q,c);
     if(z){
       must(!oracle.has(t),"unsound invariant exclusion");counts.invariant++;
     }else{
       if(p==="fresh"||st===null)st=init(w,c);
       const a=bfs(w,t,st,c);
       must(verify(w,t,a,c)&&a.yes===oracle.has(t),"wrong BFS proof");
       counts[a.yes?"bfsPositive":"bfsNegative"]++;
     }
     cum.push(work(c));
   }
   return {work:work(c),cats:c,closed:caps.map(b=>cum.filter(x=>x<=b*w.targets.length).length),counts};
 }
 const audit={worlds:0,pairs:0,negative:0,linearExclusions:0,quadraticExclusions:0,quadraticOnly:0,neither:0,liftMapChecks:0,invalidRejected:0},records=[];
 for(const split of ["cal","test"])for(const d of dims)for(const f of families)for(let id=0;id<(split==="cal"?6:12);id++){
   const w=make(d,f,split,id),o=truth(w),c=meter(),l=hull(w,1,c),q=hull(w,2,c);
   audit.worlds++;
   const counts={pairs:w.n,negative:0,linearExclusions:0,quadraticExclusions:0,quadraticOnly:0,neither:0};
   for(let x=0;x<w.n;x++){
     const hidden=w.dec[x];
     for(let j=0;j<w.actions.length;j++){
       const v=applyRaw(w.actions[j],x,c);
       must(v===w.enc[w.hidden[j](hidden)],"raw conjugation error");
       must(af(l.maps[j],lift(x,d,1,c),c)===lift(v,d,1,c),"linear lift mismatch");
       must(af(q.maps[j],lift(x,d,2,c),c)===lift(v,d,2,c),"quadratic lift mismatch");
       audit.liftMapChecks+=2;
     }
     const a=excluded(w,x,l,c),b=excluded(w,x,q,c),negative=!o.has(x);
     must(!a||negative,"linear false exclusion");must(!b||negative,"quadratic false exclusion");must(!a||b,"lift lost linear separator");
     counts.negative+=Number(negative);counts.linearExclusions+=Number(a);counts.quadraticExclusions+=Number(b);counts.quadraticOnly+=Number(!a&&b);counts.neither+=Number(negative&&!b);
   }
   for(const k of Object.keys(counts))audit[k]+=counts[k];
   must(!excluded(w,w.s,l,c)&&!excluded(w,w.s,q,c),"source excluded");
   // Empty candidate hull cannot pass when any action moves the source.
   must(!auditHull({...l,b:new Array(l.m)},c),"false invariant accepted");
   must(!verify(w,w.s^1,{yes:true,p:[]},c),"false empty path");
   must(!verify(w,w.s,{yes:false,set:[w.s]},c),"false cut");
   audit.invalidRejected+=3;
   const results={};for(const p of arms)results[p]=solve(w,p,o);
   records.push({split,d,f,id,seed:w.seed,orbit:o.size,rank1:l.rank,rank2:q.rank,counts,results});
 }
 const calibration={};
 for(const d of dims){
   const rr=records.filter(r=>r.split==="cal"&&r.d===d),cost={};
   for(const p of arms)cost[p]=rr.reduce((s,r)=>s+r.results[p].work,0);
   const best=arms.reduce((a,b)=>cost[a]<=cost[b]?a:b),oracle=rr.reduce((s,r)=>s+Math.min(...arms.map(p=>r.results[p].work)),0);
   calibration[d]={best,cost,oracle,headroom:cost[best]-oracle,screen:5*(cost[best]-oracle)>=cost[best]};
 }
 for(const r of records.filter(r=>r.split==="test"))r.results.dispatch=r.results[calibration[r.d].best];
 function summarize(rr){
   const result={worlds:rr.length,requested:rr.length*16,counts:{negative:0,linearExclusions:0,quadraticExclusions:0,quadraticOnly:0,neither:0},arms:{},oracleWork:0,oracleClosed:[0,0,0],dimensionOnlyOracle:0};
   for(const r of rr){
     for(const k of Object.keys(result.counts))result.counts[k]+=r.counts[k];
     result.oracleWork+=Math.min(...arms.map(p=>r.results[p].work));
     for(let i=0;i<caps.length;i++)result.oracleClosed[i]+=Math.max(...arms.map(p=>r.results[p].closed[i]));
   }
   for(const d of dims){
     const dd=rr.filter(r=>r.d===d);
     result.dimensionOnlyOracle+=Math.min(...arms.map(p=>dd.reduce((s,r)=>s+r.results[p].work,0)));
   }
   for(const p of [...arms,"dispatch"]){
     const v={work:0,closed:[0,0,0],cats:[0,0,0,0],invariant:0,bfsPositive:0,bfsNegative:0};
     for(const r of rr){
       const a=r.results[p];v.work+=a.work;for(let i=0;i<3;i++)v.closed[i]+=a.closed[i];for(let i=0;i<4;i++)v.cats[i]+=a.cats[i];
       for(const k of Object.keys(a.counts))v[k]+=a.counts[k];
     }
     result.arms[p]=v;
   }
   return result;
 }
 const test=records.filter(r=>r.split==="test"),overall=summarize(test);
 const screen=Object.values(calibration).some(x=>x.screen);
 const screened=summarize(test.filter(r=>calibration[r.d].screen));
 const gate=screen&&20*(screened.oracleClosed[1]-screened.arms.dispatch.closed[1])>=screened.requested;
 return {id:"ACD-03",status:"finite invariant synthesis",audit,calibration,caps,overall,screened,gate,byFamily:Object.fromEntries(families.map(f=>[f,summarize(test.filter(r=>r.f===f))])),byDimension:Object.fromEntries(dims.map(d=>[d,summarize(test.filter(r=>r.d===d))])),records};
};
const fingerprint = function fingerprint(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16).padStart(8,"0")};
const receipt={...run(),function_fingerprint:fingerprint(run.toString())};
if(process.argv.includes('--check')){
 const saved=JSON.parse(readFileSync(new URL('../output/evaluation_acd/acd_03.json',import.meta.url),'utf8'));
 if(JSON.stringify(receipt)!==JSON.stringify(saved))throw Error('receipt mismatch');
 console.log('ACD-03 receipt verified');
}else console.log(JSON.stringify(receipt,null,2));
