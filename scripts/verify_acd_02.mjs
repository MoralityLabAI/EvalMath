// ACD-02A/B/C. Dependency-free Node.js 18+.
import {readFileSync} from 'node:fs';
const run = function run(){
  const must=(x,m)=>{if(!x)throw Error(m)};
  const names=["F","R","Fresh","H","H2","H4","PF4","PR4","PF8","PR8"],regimes=["source","target","uniform","source-target","target-source"];
  const caps=[128,256,512],overheads=[1,8,32];
  const rng=seed=>{let x=seed>>>0;return n=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)%n}};
  const met=()=>[0,0,0,0];
  const read=(c,x)=>(c[0]++,x),write=(c,o,k,x)=>(c[1]++,o[k]=x),edge=(c,x)=>(c[2]++,x),check=(c,x)=>(c[3]++,x);
  const work=c=>c[0]+c[1]+c[2]+c[3];
  function world(stratum,regime,split,i){
    const seed=(split==="cal"?2300000:9300000)+10000*stratum+100*regime+i+1;
    const r=rng(seed),n=i%2?64:32,cap=stratum%2?8:2,dense=stratum>=2;
    const adj=Array.from({length:n},()=>[]);
    for(let v=0;v<n;v++){
      const group=split==="cal"?8:4,base=Math.floor(v/group)*group;
      const a=adj[v];
      a.push(base+(v-base+1)%group);
      for(let j=0;j<(dense?5:1);j++)a.push(base+r(group));
      if(v%group===0&&v+group<n&&r(4)!==0)a.push(v+group);
      if(dense&&v%group===1&&v>=group&&r(3)===0)a.push(v-group);
      if(split==="test"&&v%group===2&&r(4)===0)a.push(r(n));
    }
    const q=rng(seed^0x9e3779b9),sh=q(n),th=q(n),queries=[];
    for(let j=0;j<32;j++){
      const hotSource=regime===0||(regime===3&&j<16)||(regime===4&&j>=16);
      const hotTarget=regime===1||(regime===4&&j<16)||(regime===3&&j>=16);
      const s=hotSource&&q(8)!==0?sh:q(n);
      const t=hotTarget&&q(8)!==0?th:q(n);
      queries.push([s,t]);
    }
    return {stratum,regime,split,i,seed,n,cap,adj,queries};
  }
  function oracle(w){
    const R=Array.from({length:w.n},(_,i)=>{const a=new Uint8Array(w.n);a[i]=1;for(const j of w.adj[i])a[j]=1;return a});
    for(let k=0;k<w.n;k++)for(let i=0;i<w.n;i++)if(R[i][k])for(let j=0;j<w.n;j++)R[i][j]|=R[k][j];
    return R;
  }
  function transpose(w,c){
    const a=Array.from({length:w.n},()=>[]);c[1]+=w.n;
    for(let u=0;u<w.n;u++)for(let j=0,d=read(c,w.adj[u].length);j<d;j++){
      const v=edge(c,w.adj[u][j]),list=read(c,a[v]);write(c,list,list.length,[u,j]);
    }
    return a;
  }
  function state(root,n,c){
    // Sparse parent table; arrays are indexed by original vertices.
    const p=[],q=[];write(c,p,root,[-1,-1]);write(c,q,0,root);c[1]++;
    return {root,p,q,h:0};
  }
  function expand(w,st,t,reverse,rev,c){
    while(read(c,st.p[t])===undefined&&!check(c,st.h===st.q.length)){
      const v=read(c,st.q[st.h]);st.h++;c[1]++;
      const list=read(c,reverse?rev[v]:w.adj[v]);
      for(let j=0,d=read(c,list.length);j<d;j++){
        const item=edge(c,list[j]),u=reverse?item[0]:item,a=reverse?item[1]:j;
        if(read(c,st.p[u])===undefined){write(c,st.p,u,[v,a]);write(c,st.q,st.q.length,u)}
      }
    }
  }
  function certify(w,st,s,t,rev,c){
    const dest=rev?s:t;
    if(read(c,st.p[dest])!==undefined){
      const p=[];
      for(let v=dest;!check(c,v===st.root);){
        const [u,a]=read(c,st.p[v]);write(c,p,p.length,a);v=u;
      }
      if(rev)return {yes:true,p};
      const path=[];for(let j=p.length-1;j>=0;j--)write(c,path,path.length,read(c,p[j]));
      return {yes:true,p:path};
    }
    must(check(c,st.h===st.q.length),"unexhausted cut");
    const set=[];
    if(rev){
      for(let v=0;v<w.n;v++)if(read(c,st.p[v])===undefined)write(c,set,set.length,v);
    }else for(const v of st.q)write(c,set,set.length,read(c,v));
    return {yes:false,set};
  }
  function verify(w,s,t,z,c){
    if(z.yes){
      let v=s;
      for(const a of z.p){
        if(!check(c,Number.isInteger(a)&&a>=0&&a<read(c,w.adj[v].length)))return false;
        v=edge(c,w.adj[v][a]);
      }
      return check(c,v===t);
    }
    const seen=new Uint8Array(w.n);
    for(const v of z.set){
      if(!check(c,Number.isInteger(v)&&v>=0&&v<w.n))return false;
      write(c,seen,v,1);
    }
    if(!check(c,read(c,seen[s])===1&&read(c,seen[t])===0))return false;
    for(const v of z.set)for(let j=0,d=read(c,w.adj[v].length);j<d;j++){
      if(!check(c,read(c,seen[edge(c,w.adj[v][j])])===1))return false;
    }
    return true;
  }
  function solve(w,policy,R){
    const c=met(),cache=new Map(),freqS=[],freqT=[],cum=[];
    let reverseIndex=null,ds=0,dt=0,chosen=null;
    const adaptive=policy[0]==="H"||policy[0]==="P";
    for(let i=0;i<w.queries.length;i++){
      const [s,t]=w.queries[i],fk=s,rk=w.n+t;
      let rev=policy==="R";
      if(adaptive){
        const fs=read(c,freqS[s])??0,ft=read(c,freqT[t])??0;
        if(check(c,fs===0)){ds++;c[1]++}
        if(check(c,ft===0)){dt++;c[1]++}
        write(c,freqS,s,fs+1);write(c,freqT,t,ft+1);
        if(policy[0]==="H"){
          const f=read(c,cache.has(fk)),r=read(c,cache.has(rk));
          const min=policy==="H4"?4:policy==="H2"?2:1;
          if(check(c,f!==r))rev=r;
          else if(check(c,f&&r))rev=check(c,ft>fs);
          else rev=check(c,ft+1>=min)&&check(c,ft>fs);
        }else{
          const k=Number(policy.slice(2));
          if(check(c,i<k))rev=policy[1]==="R";
          else{
            if(check(c,chosen===null)){
              // ds/dt currently include this query: use exactly the preceding prefix.
              chosen=check(c,(dt-Number(ft===0))<(ds-Number(fs===0)));c[1]++;
            }
            rev=read(c,chosen);
          }
        }
      }
      if(rev&&check(c,reverseIndex===null))reverseIndex=transpose(w,c);
      const key=rev?rk:fk,root=rev?t:s;
      let st=policy==="Fresh"?undefined:read(c,cache.get(key));
      if(st===undefined){
        st=state(root,w.n,c);
        if(policy!=="Fresh"){
          if(check(c,cache.size>=w.cap)){const old=read(c,cache.keys().next().value);cache.delete(old);c[1]++}
          cache.set(key,st);c[1]++;
        }
      }else{
        cache.delete(key);c[1]++;cache.set(key,st);c[1]++;
      }
      expand(w,st,rev?s:t,rev,reverseIndex,c);
      const z=certify(w,st,s,t,rev,c);
      must(verify(w,s,t,z,c),"invalid certificate");
      must(Number(z.yes)===R[s][t],"incorrect answer");
      cum.push(work(c));
    }
    const closed=extra=>caps.map(b=>cum.filter((v,i)=>v+extra*(i+1)<=b*32).length);
    return {work:work(c),cats:c,closed:closed(0),overhead:overheads.map(closed)};
  }
  const audit={worlds:0,pairs:0,certificateChecks:0,invalidRejected:0},records=[];
  for(const split of ["cal","test"])for(let st=0;st<4;st++)for(let regime=0;regime<5;regime++)for(let i=0;i<(split==="cal"?8:12);i++){
    const w=world(st,regime,split,i),R=oracle(w),c=met(),rev=transpose(w,c);
    audit.worlds++;
    for(let s=0;s<w.n;s++){
      const f=state(s,w.n,c),r=state(s,w.n,c);
      for(let t=0;t<w.n;t++){
        expand(w,f,t,false,null,c);const a=certify(w,f,s,t,false,c);
        must(verify(w,s,t,a,c)&&Number(a.yes)===R[s][t],"forward census");
        expand(w,r,t,true,rev,c);const b=certify(w,r,t,s,true,c);
        must(verify(w,t,s,b,c)&&Number(b.yes)===R[t][s],"reverse census");
        audit.pairs++;audit.certificateChecks+=2;
      }
    }
    must(!verify(w,0,1,{yes:true,p:[]},c),"empty wrong path");
    must(!verify(w,0,1,{yes:false,set:[]},c),"empty cut");
    must(!verify(w,0,0,{yes:false,set:[0]},c),"self cut");
    audit.invalidRejected+=3;
    const results={};
    for(const p of names)results[p]=solve(w,p,R);
    records.push({split,stratum:st,regime:regimes[regime],i,seed:w.seed,n:w.n,cap:w.cap,results});
  }
  const selection=[];
  for(let st=0;st<4;st++){
    const rr=records.filter(r=>r.split==="cal"&&r.stratum===st),cost={};
    for(const p of names)cost[p]=rr.reduce((s,r)=>s+r.results[p].work,0);
    const best=names.reduce((a,b)=>cost[a]<=cost[b]?a:b);
    const fixed=["F","R","Fresh"].reduce((a,b)=>cost[a]<=cost[b]?a:b);
    const oracle=rr.reduce((s,r)=>s+Math.min(...names.map(p=>r.results[p].work)),0);
    selection.push({stratum:st,best,fixed,calibrationCosts:cost,oracle,headroom:cost.H-oracle,screen:5*(cost.H-oracle)>=cost.H});
  }
  const test=records.filter(r=>r.split==="test");
  for(const r of test){const s=selection[r.stratum];r.results.selector=r.results[s.best];r.results.fixed=r.results[s.fixed]}
  function summary(rr){
    const out={worlds:rr.length,requested:32*rr.length,arms:{},oracleWork:0,oracleClosed:[0,0,0],stratumOnlyOracleWork:0};
    for(const p of [...names,"selector","fixed"]){
      let cost=0,wins=0,losses=0,worst=0;
      const closed=[0,0,0],cats=[0,0,0,0],overhead=overheads.map(()=>[0,0,0]);
      for(const r of rr){
        const v=r.results[p],delta=v.work-r.results.H.work;cost+=v.work;
        wins+=Number(delta<0);losses+=Number(delta>0);worst=Math.max(worst,delta);
        for(let j=0;j<3;j++){closed[j]+=v.closed[j];for(let k=0;k<overheads.length;k++)overhead[k][j]+=v.overhead[k][j]}
        for(let j=0;j<4;j++)cats[j]+=v.cats[j];
      }
      out.arms[p]={work:cost,closed,wins,losses,worstExcess:worst,cats,overheadClosed:overhead};
    }
    for(const r of rr){
      out.oracleWork+=Math.min(...names.map(p=>r.results[p].work));
      for(let j=0;j<3;j++)out.oracleClosed[j]+=Math.max(...names.map(p=>r.results[p].closed[j]));
    }
    for(let st=0;st<4;st++){
      const ss=rr.filter(r=>r.stratum===st);
      out.stratumOnlyOracleWork+=Math.min(...names.map(p=>ss.reduce((s,r)=>s+r.results[p].work,0)));
    }
    out.netHindsightHeadroom=overheads.map(o=>out.arms.H.work-out.oracleWork-o*out.requested);
    return out;
  }
  const overall=summary(test),screened=summary(test.filter(r=>selection[r.stratum].screen));
  const gate=screened.worlds>0&&screened.arms.selector.closed[1]>screened.arms.H.closed[1]&&screened.arms.selector.work<=screened.arms.H.work;
  const perRegime=Object.fromEntries(regimes.map(reg=>[reg,summary(test.filter(r=>r.regime===reg))]));
  const perStratum=selection.map(s=>summary(test.filter(r=>r.stratum===s.stratum)));
  return {id:"ACD-02",status:"finite synthetic pilot",audit,caps,overheads,selection,overall,screened,gate,perRegime,perStratum,records};
};
const fingerprint = function fingerprint(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16).padStart(8,"0")};
const receipt={...run(),function_fingerprint:fingerprint(run.toString())};
if(process.argv.includes('--check')){
 const saved=JSON.parse(readFileSync(new URL('../output/evaluation_acd/acd_02.json',import.meta.url),'utf8'));
 if(JSON.stringify(receipt)!==JSON.stringify(saved))throw Error('receipt mismatch');
 console.log('ACD-02 receipt verified');
}else console.log(JSON.stringify(receipt,null,2));
