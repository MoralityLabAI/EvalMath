// ACD-04 exact direct polynomial and CEGIS synthesis, Node 18+.
import {readFileSync} from 'node:fs';
const run = function run(){
 const must=(x,m)=>{if(!x)throw Error(m)};
 const dims=[5,6,7,8],families=["translation","weight","reset"],arms=["lazy","linear","quadratic","global","cegis"],caps=[128,512,2048];
 const rng=seed=>{let x=seed>>>0;return n=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)%n}};
 const met=()=>[0,0,0,0],rd=(c,x)=>(c[0]++,x),wr=(c,o,k,x)=>(c[1]++,o[k]=x),op=(c,x)=>(c[2]++,x),ck=(c,x)=>(c[3]++,x),work=c=>c.reduce((a,b)=>a+b,0);
 const bit=(c,x,i)=>op(c,(x>>>i)&1),bb=(c,x,i)=>op(c,(x>>BigInt(i))&1n);
 function dot(a,b,c){let v=a&b,p=0;while(v){v&=v-1n;p^=1}return op(c,p)}
 function raw(a,x,c){let v=rd(c,a.b);for(let i=0;i<a.cols.length;i++)if(bit(c,x,i))v=op(c,v^rd(c,a.cols[i]));return v}
 function make(d,f,split,id){
   const seed=(split==="cal"?2700000:8200000)+10000*d+100*families.indexOf(f)+id+1,r=rng(seed),n=1<<d;
   const cols=Array.from({length:d},(_,i)=>1<<i);
   for(let k=0;k<(split==="cal"?4:10)*d;k++){const a=r(d),b=r(d);if(a!==b)cols[a]^=cols[b]}
   const off=r(n),enc=Array.from({length:n},(_,x)=>cols.reduce((a,v,i)=>((x>>>i)&1)?a^v:a,off));
   must(new Set(enc).size===n,"encoding");const dec=[];enc.forEach((x,i)=>dec[x]=i);
   const hidden=[];let src=r(n);
   if(f==="translation"){
     const k=1+r(d-1);for(let i=0;i<k;i++)hidden.push(x=>x^(1<<i));
   }else{
     const k=1+r(d-1),perm=Array.from({length:d},(_,i)=>i);
     for(let i=d-1;i>0;i--){const j=r(i+1);[perm[i],perm[j]]=[perm[j],perm[i]]}
     src=perm.slice(0,k).reduce((x,i)=>x|(1<<i),0);
     if(f==="weight"){
       for(let i=1;i<d;i++){const j=split==="cal"?i-1:0,h=i;hidden.push(x=>((x>>>j)^(x>>>h))&1?x^(1<<j)^(1<<h):x)}
     }else for(let i=0;i<d;i++)hidden.push(x=>x&~(1<<i));
   }
   const actions=hidden.map(h=>{const fn=x=>enc[h(dec[x])],b=fn(0);return {b,cols:Array.from({length:d},(_,i)=>fn(1<<i)^b)}});
   const targets=Array.from({length:n},(_,i)=>i),q=rng(seed^0xacd04000);
   for(let i=n-1;i>0;i--){const j=q(i+1);[targets[i],targets[j]]=[targets[j],targets[i]]}
   return {d,n,f,split,id,seed,s:enc[src],enc,dec,hidden,actions,targets:targets.slice(0,16)};
 }
 function oracle(w){
   let a=new Set([w.dec[w.s]]);
   for(;;){const b=new Set(a);for(const x of a)for(const h of w.hidden)b.add(h(x));if(a.size===b.size)break;a=b}
   return new Set([...a].map(x=>w.enc[x]));
 }
 const dim=(d,k)=>k===1?d:d*(d+1)/2;
 function phi(x,d,k,c){
   let v=BigInt(x);
   if(k===2)for(let i=0,j=d;i<d;i++)for(let h=i+1;h<d;h++,j++)if(bit(c,x,i)&&bit(c,x,h))v=op(c,v|(1n<<BigInt(j)));
   return v;
 }
 function anchors(d,k,c){
   const a=[];wr(c,a,0,0);for(let i=0;i<d;i++)wr(c,a,a.length,1<<i);
   if(k===2)for(let i=0;i<d;i++)for(let j=i+1;j<d;j++)wr(c,a,a.length,(1<<i)|(1<<j));
   return a;
 }
 function reduce(v,b,c){
   for(let i=b.length-1;i>=0;i--)if(bb(c,v,i)){const r=rd(c,b[i]);if(r!==undefined)v=op(c,v^r)}
   return v;
 }
 function add(v,b,c){
   v=reduce(v,b,c);if(ck(c,v===0n))return null;
   let j=b.length-1;while(!bb(c,v,j))j--;
   must(rd(c,b[j])===undefined,"pivot occupied");
   wr(c,b,j,v);return v;
 }
 function sep(u,b,c){
   const r=reduce(u,b,c);if(ck(c,r===0n))return null;
   let i=0;while(!bb(c,r,i))i++;
   let y=1n<<BigInt(i);
   for(let j=0;j<b.length;j++){const a=rd(c,b[j]);if(a!==undefined&&dot(a,y,c))y=op(c,y^(1n<<BigInt(j)))}
   must(dot(u,y,c)===1,"bad separator construction");
   return y;
 }
 function verifySep(y,u,b,c){
   if(!ck(c,typeof y==="bigint"&&y>0n&&y<(1n<<BigInt(b.length))))return false;
   if(!ck(c,dot(u,y,c)===1))return false;
   for(let j=0;j<b.length;j++){const a=rd(c,b[j]);if(a!==undefined&&!ck(c,dot(a,y,c)===0))return false}
   return true;
 }
 function delta(w,j,x,k,c){
   return op(c,phi(raw(rd(c,w.actions[j]),x,c),w.d,k,c)^phi(x,w.d,k,c));
 }
 function globalBuild(w,k,c){
   const a=anchors(w.d,k,c),m=dim(w.d,k),b=new Array(m),rows=[];
   for(let j=0;j<w.actions.length;j++)for(const x of a){const r=delta(w,j,rd(c,x),k,c);wr(c,rows,rows.length,r);add(r,b,c)}
   // Audit every anchor constraint against the final row span.
   for(const r of rows)must(ck(c,reduce(rd(c,r),b,c)===0n),"global row audit");
   return {b,k,rows,rank:b.filter(x=>x!==undefined).length};
 }
 function sourceBuild(w,k,c){
   const m=dim(w.d,k),maps=[],s=phi(w.s,w.d,k,c);
   for(const a of w.actions){
     const b=phi(rd(c,a.b),w.d,k,c),cols=[],unit=[];
     for(let i=0;i<w.d;i++){
       const v=phi(op(c,a.b^rd(c,a.cols[i])),w.d,k,c);wr(c,unit,i,v);wr(c,cols,i,op(c,v^b));
     }
     if(k===2)for(let i=0;i<w.d;i++)for(let j=i+1;j<w.d;j++){
       const x=op(c,op(c,a.b^rd(c,a.cols[i]))^rd(c,a.cols[j]));
       const v=phi(x,w.d,k,c);wr(c,cols,cols.length,op(c,op(c,op(c,v^rd(c,unit[i]))^rd(c,unit[j]))^b));
     }
     wr(c,maps,maps.length,{b,cols});
   }
   const lin=(a,x)=>{let v=0n;for(let i=0;i<a.cols.length;i++)if(bb(c,x,i))v=op(c,v^rd(c,a.cols[i]));return v};
   const disp=a=>op(c,op(c,lin(a,s)^rd(c,a.b))^s);
   const b=new Array(m),q=[];
   const insert=v=>{const r=add(v,b,c);if(r!==null)wr(c,q,q.length,r)};
   for(const a of maps)insert(disp(a));
   for(let i=0;i<q.length;i++){const v=rd(c,q[i]);for(const a of maps)insert(lin(a,v))}
   for(const a of maps)must(ck(c,reduce(disp(a),b,c)===0n),"displacement audit");
   for(let i=0;i<b.length;i++){
     const v=rd(c,b[i]);if(v===undefined)continue;
     must(ck(c,v>>BigInt(i)===1n),"pivot audit");
     for(const a of maps)must(ck(c,reduce(lin(a,v),b,c)===0n),"closure audit");
   }
   return {b,k,s,rank:q.length,maps};
 }
 function sourceEx(w,t,o,c){return ck(c,reduce(op(c,phi(t,w.d,o.k,c)^o.s),o.b,c)!==0n)}
 function queryGlobal(w,t,o,c){
   const u=op(c,phi(t,w.d,o.k,c)^o.s),y=sep(u,o.b,c);
   if(y===null)return false;
   must(verifySep(y,u,o.b,c),"global separator rejected");
   return true;
 }
 function newCegis(w,c){
   return {a:anchors(w.d,2,c),b:new Array(dim(w.d,2)),cache:[],valid:[],s:phi(w.s,w.d,2,c),proposals:0,counterexamples:0,anchorEvaluations:0,anchorChecks:0,reused:0};
 }
 function queryCegis(w,t,o,c){
   const u=op(c,phi(t,w.d,2,c)^o.s);
   for(const y of o.valid)if(ck(c,dot(rd(c,y),u,c)===1)){o.reused++;return true}
   for(;;){
     const y=sep(u,o.b,c);
     if(y===null)return false;
     o.proposals++;
     must(verifySep(y,u,o.b,c),"proposal fails existing constraints");
     let violation=null;
     outer:for(let j=0;j<w.actions.length;j++)for(let i=0;i<o.a.length;i++){
       const key=j*o.a.length+i;
       let r=rd(c,o.cache[key]);
       if(r===undefined){r=delta(w,j,rd(c,o.a[i]),2,c);wr(c,o.cache,key,r);o.anchorEvaluations++}
       o.anchorChecks++;
       if(!ck(c,dot(r,y,c)===0)){violation=r;break outer}
     }
     if(violation===null){wr(c,o.valid,o.valid.length,y);return true}
     must(add(violation,o.b,c)!==null,"nonindependent counterexample");
     o.counterexamples++;
     must(o.counterexamples<=o.b.length,"rank bound");
   }
 }
 function init(w,c){const p=[],q=[];wr(c,p,w.s,[-1,-1]);wr(c,q,0,w.s);c[1]++;return {p,q,h:0}}
 function bfs(w,t,st,c){
   while(rd(c,st.p[t])===undefined&&!ck(c,st.h===st.q.length)){
     const u=rd(c,st.q[st.h]);st.h++;c[1]++;
     for(let j=0;j<w.actions.length;j++){
       const v=raw(rd(c,w.actions[j]),u,c);
       if(rd(c,st.p[v])===undefined){wr(c,st.p,v,[u,j]);wr(c,st.q,st.q.length,v)}
     }
   }
   if(rd(c,st.p[t])!==undefined){
     const p=[],r=[];for(let u=t;!ck(c,u===w.s);){const [v,j]=rd(c,st.p[u]);wr(c,r,r.length,j);u=v}
     for(let i=r.length-1;i>=0;i--)wr(c,p,p.length,rd(c,r[i]));
     return {yes:true,p};
   }
   const set=[];for(const v of st.q)wr(c,set,set.length,rd(c,v));return {yes:false,set};
 }
 function verify(w,t,z,c){
   if(z.yes){let x=w.s;for(const j of z.p){if(!ck(c,Number.isInteger(j)&&j>=0&&j<w.actions.length))return false;x=raw(rd(c,w.actions[j]),x,c)}return ck(c,x===t)}
   const seen=[];for(const v of z.set){if(!ck(c,Number.isInteger(v)&&v>=0&&v<w.n))return false;wr(c,seen,v,true)}
   if(!ck(c,rd(c,seen[w.s])===true&&rd(c,seen[t])!==true))return false;
   for(const v of z.set)for(const a of w.actions)if(!ck(c,rd(c,seen[raw(a,v,c)])===true))return false;
   return true;
 }
 function solve(w,p,o){
   const c=met(),cum=[],counts={invariant:0,bfsPositive:0,bfsNegative:0};
   let h=null,g=null,ce=null,st=null;
   if(p==="linear"||p==="quadratic")h=sourceBuild(w,p==="linear"?1:2,c);
   if(p==="global"){g=globalBuild(w,2,c);g.s=phi(w.s,w.d,2,c)}
   if(p==="cegis")ce=newCegis(w,c);
   for(const t of w.targets){
     const z=h!==null?sourceEx(w,t,h,c):g!==null?queryGlobal(w,t,g,c):ce!==null?queryCegis(w,t,ce,c):false;
     if(z){must(!o.has(t),"false invariant exclusion");counts.invariant++}
     else {if(st===null)st=init(w,c);const a=bfs(w,t,st,c);must(verify(w,t,a,c)&&a.yes===o.has(t),"BFS verification");counts[a.yes?"bfsPositive":"bfsNegative"]++}
     cum.push(work(c));
   }
   return {work:work(c),cats:c,closed:caps.map(b=>cum.filter(v=>v<=b*w.targets.length).length),counts,
     ...(ce?{cegis:{proposals:ce.proposals,counterexamples:ce.counterexamples,anchorEvaluations:ce.anchorEvaluations,anchorChecks:ce.anchorChecks,reused:ce.reused,validated:ce.valid.length}}:{})};
 }
 const audit={worlds:0,pairs:0,negative:0,sourceLinear:0,sourceQuadratic:0,globalLinear:0,globalQuadratic:0,sourceOnly:0,quadraticGlobalOnly:0,rawActionChecks:0,globalRowChecks:0,invalidRejected:0},records=[];
 for(const split of ["cal","test"])for(const d of dims)for(const f of families)for(let id=0;id<(split==="cal"?6:12);id++){
   const w=make(d,f,split,id),o=oracle(w),c=met(),l=sourceBuild(w,1,c),q=sourceBuild(w,2,c),g1=globalBuild(w,1,c),g2=globalBuild(w,2,c),ce=newCegis(w,c);
   g1.s=phi(w.s,d,1,c);g2.s=phi(w.s,d,2,c);
   const counts={pairs:w.n,negative:0,sourceLinear:0,sourceQuadratic:0,globalLinear:0,globalQuadratic:0,sourceOnly:0,quadraticGlobalOnly:0};
   audit.worlds++;
   for(let x=0;x<w.n;x++){
     for(let j=0;j<w.actions.length;j++){
       must(raw(w.actions[j],x,c)===w.enc[w.hidden[j](w.dec[x])],"raw map mismatch");audit.rawActionChecks++;
       must(reduce(delta(w,j,x,1,c),g1.b,c)===0n&&reduce(delta(w,j,x,2,c),g2.b,c)===0n,"global anchor completeness");audit.globalRowChecks+=2;
     }
     const a=sourceEx(w,x,l,c),b=sourceEx(w,x,q,c),g=queryGlobal(w,x,g1,c),h=queryGlobal(w,x,g2,c),e=queryCegis(w,x,ce,c),neg=!o.has(x);
     must((!a||neg)&&(!b||neg)&&(!g||neg)&&(!h||neg),"unsound exclusion");
     must((!a||b)&&(!g||h)&&(!g||a)&&(!h||b)&&h===e,"hierarchy/CEGIS mismatch");
     counts.negative+=Number(neg);counts.sourceLinear+=Number(a);counts.sourceQuadratic+=Number(b);counts.globalLinear+=Number(g);counts.globalQuadratic+=Number(h);counts.sourceOnly+=Number(b&&!h);counts.quadraticGlobalOnly+=Number(h&&!g);
   }
   for(const k of Object.keys(counts))audit[k]+=counts[k];
   must(!verifySep(0n,1n,g2.b,c),"zero separator");
   must(!verifySep(1n,0n,g2.b,c),"identical target separator");
   // A deliberately violated polynomial: choose a set bit of a nonzero raw row.
   const badRow=g2.rows.find(x=>x!==0n);must(badRow!==undefined,"all identity");
   let i=0;while(((badRow>>BigInt(i))&1n)===0n)i++;
   must(!verifySep(1n<<BigInt(i),badRow,g2.b,c),"noninvariant separator");
   must(!verify(w,w.s^1,{yes:true,p:[]},c),"bad path");
   must(!verify(w,w.s,{yes:false,set:[w.s]},c),"bad cut");
   audit.invalidRejected+=5;
   const results={};for(const p of arms)results[p]=solve(w,p,o);
   must(results.global.counts.invariant===results.cegis.counts.invariant,"stream global/CEGIS mismatch");
   records.push({split,d,f,id,seed:w.seed,orbit:o.size,rankSource1:l.rank,rankSource2:q.rank,rankGlobal1:g1.rank,rankGlobal2:g2.rank,counts,results});
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
   const v={worlds:rr.length,requested:rr.length*16,counts:{negative:0,sourceLinear:0,sourceQuadratic:0,globalLinear:0,globalQuadratic:0,sourceOnly:0,quadraticGlobalOnly:0},arms:{},oracleWork:0,oracleClosed:[0,0,0],dimensionOnlyOracle:0,cegis:{proposals:0,counterexamples:0,anchorEvaluations:0,anchorChecks:0,reused:0,validated:0}};
   for(const r of rr){
     for(const k of Object.keys(v.counts))v.counts[k]+=r.counts[k];
     for(const k of Object.keys(v.cegis))v.cegis[k]+=r.results.cegis.cegis[k];
     v.oracleWork+=Math.min(...arms.map(p=>r.results[p].work));
     for(let i=0;i<caps.length;i++)v.oracleClosed[i]+=Math.max(...arms.map(p=>r.results[p].closed[i]));
   }
   for(const d of dims){const dd=rr.filter(r=>r.d===d);v.dimensionOnlyOracle+=Math.min(...arms.map(p=>dd.reduce((s,r)=>s+r.results[p].work,0)))}
   for(const p of [...arms,"dispatch"]){
     const a={work:0,closed:[0,0,0],cats:[0,0,0,0],invariant:0,bfsPositive:0,bfsNegative:0,winsVsDispatch:0,lossesVsDispatch:0,worstExcess:0};
     for(const r of rr){const z=r.results[p];a.work+=z.work;for(let i=0;i<3;i++)a.closed[i]+=z.closed[i];for(let i=0;i<4;i++)a.cats[i]+=z.cats[i];for(const k of Object.keys(z.counts))a[k]+=z.counts[k];const excess=z.work-r.results.dispatch.work;a.winsVsDispatch+=Number(excess<0);a.lossesVsDispatch+=Number(excess>0);a.worstExcess=Math.max(a.worstExcess,excess)}
     v.arms[p]=a;
   }
   return v;
 }
 const test=records.filter(r=>r.split==="test"),overall=summarize(test),screened=summarize(test.filter(r=>calibration[r.d].screen));
 const gate=screened.worlds>0&&20*(screened.oracleClosed[1]-screened.arms.dispatch.closed[1])>=screened.requested;
 return {id:"ACD-04",status:"finite symbolic synthesis",audit,caps,calibration,overall,screened,gate,byFamily:Object.fromEntries(families.map(f=>[f,summarize(test.filter(r=>r.f===f))])),byDimension:Object.fromEntries(dims.map(d=>[d,summarize(test.filter(r=>r.d===d))])),records};
};
const fingerprint = function fingerprint(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16).padStart(8,"0")};
const receipt={...run(),function_fingerprint:fingerprint(run.toString())};
if(process.argv.includes('--check')){
 const saved=JSON.parse(readFileSync(new URL('../output/evaluation_acd/acd_04.json',import.meta.url),'utf8'));
 if(JSON.stringify(receipt)!==JSON.stringify(saved))throw Error('receipt mismatch');
 console.log('ACD-04 receipt verified');
}else console.log(JSON.stringify(receipt,null,2));
