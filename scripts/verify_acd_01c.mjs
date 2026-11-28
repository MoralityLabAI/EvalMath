// ACD-01C. Dependency-free Node.js 18+ verifier.
import {readFileSync} from 'node:fs';
const run = function run(){
  const must=(x,m)=>{if(!x)throw Error(m)};
  const families=["graph","gf2","recurrence"],ks=[0,1,2,4,8,1000000],caps=[32,128,512];
  const rng=seed=>{let x=seed>>>0;return n=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)%n}};
  const met=()=>({read:0,write:0,algebra:0,check:0});
  const read=(c,x)=>(c.read++,x),check=(c,x)=>(c.check++,x),alg=(c,x)=>(c.algebra++,x);
  const put=(c,o,k,x)=>{c.write++;o[k]=x};
  const sum=c=>Object.values(c).reduce((a,b)=>a+b,0);
  const bit=(c,v,i)=>alg(c,(v>>>i)&1);
  const dot=(c,a,b)=>{c.algebra++;let v=a&b,p=0;while(v){v&=v-1;p^=1}return p};
  const get=(c,o,k)=>read(c,o[k]);
  const deg=(w,v,c)=>read(c,w.kind==="graph"?w.adj[v].length:w.kind==="gf2"?w.rows.length:1);
  const next=(w,v,a,c)=>alg(c,w.kind==="graph"?w.adj[v][a]:w.kind==="gf2"?v^w.rows[a]:(w.a*v+w.b)%w.n);
  function make(kind,split,id){
    const seed=(split==="cal"?300000:800000)+10000*families.indexOf(kind)+id+1;
    const r=rng(seed),n=[8,16,32][id%3],d=Math.log2(n);
    if(kind==="graph"){
      const adj=Array.from({length:n},()=>[]);
      for(let v=0;v<n;v++){
        const base=v<n/2?0:n/2;
        if(split==="cal"){
          for(let j=0;j<1+id%3;j++)adj[v].push(base+r(n/2));
          if(id%4===0)adj[v].push(r(n));
        }else{
          // Short SCC cycles, forward bridges, and optional backward chords.
          const block=4,lo=Math.floor(v/block)*block;
          adj[v].push(lo+(v-lo+1)%block);
          if(v%block===0&&v+block<n&&id%3!==1)adj[v].push(v+block);
          if(id%4===0)adj[v].push(r(n));
          if(id%5===0&&v>=block)adj[v].push(v-block);
        }
      }
      return {kind,split,id,n,d,seed,adj};
    }
    if(kind==="gf2"){
      const rank=1+(Math.floor(id/3)%d),b=Array.from({length:d},(_,i)=>1<<i);
      for(let j=0;j<5*d;j++){const a=r(d),q=r(d);if(a!==q)b[a]^=b[q]}
      const rows=b.slice(0,rank);
      for(let j=0;j<(split==="cal"?1:4);j++){
        const mask=r(1<<rank);let v=0;
        for(let k=0;k<rank;k++)if((mask>>>k)&1)v^=b[k];
        rows.push(v);
      }
      return {kind,split,id,n,d,seed,rows,rank};
    }
    const a=split==="cal"?1+2*r(n/2):2*r(n/2);
    return {kind,split,id,n,d,seed,a,b:r(n)};
  }
  function stream(w){
    const r=rng(w.seed^0xa5ac1234),length=[1,4,16,32][r(4)],locality=w.id%3;
    const common=r(w.n),other=r(w.n);
    return Array.from({length},()=>[locality===0?common:locality===1?(r(4)?common:other):r(w.n),r(w.n)]);
  }
  function truth(w){
    if(w.kind==="gf2"){
      const s=new Set([0]);for(const x of w.rows)for(const y of [...s])s.add(x^y);
      must(s.size===2**w.rank,"rank");
      return (a,b)=>s.has(a^b);
    }
    if(w.kind==="recurrence"){
      const sets=Array.from({length:w.n},(_,s)=>{const z=new Set();for(let i=0;i<=w.n;i++){z.add(s);s=(w.a*s+w.b)%w.n}return z});
      return (a,b)=>sets[a].has(b);
    }
    const R=Array.from({length:w.n},(_,i)=>Array.from({length:w.n},(_,j)=>i===j||w.adj[i].includes(j)));
    for(let k=0;k<w.n;k++)for(let i=0;i<w.n;i++)if(R[i][k])for(let j=0;j<w.n;j++)R[i][j] ||= R[k][j];
    return (a,b)=>R[a][b];
  }
  function verify(w,s,t,z,c){
    if(z.type==="path"){
      let v=s;
      for(const a of z.path){if(!check(c,Number.isInteger(a)&&a>=0&&a<deg(w,v,c)))return false;v=next(w,v,a,c)}
      return check(c,v===t);
    }
    if(z.type==="cut"){
      let mask=0;
      for(const v of z.vertices){if(!check(c,Number.isInteger(v)&&v>=0&&v<w.n))return false;mask=alg(c,mask|(1<<v))}
      if(!check(c,bit(c,mask,s)===1&&bit(c,mask,t)===0))return false;
      for(const v of z.vertices)for(let j=0,k=deg(w,v,c);j<k;j++)if(!check(c,bit(c,mask,next(w,v,j,c))===1))return false;
      return true;
    }
    if(w.kind!=="gf2")return false;
    if(z.type==="coeff"){
      if(!check(c,Number.isInteger(z.mask)&&z.mask>=0&&z.mask<(1<<w.rows.length)))return false;
      let v=s;
      for(let i=0;i<w.rows.length;i++)if(bit(c,z.mask,i))v=alg(c,v^get(c,w.rows,i));
      return check(c,v===t);
    }
    if(z.type==="separator"){
      if(!check(c,Number.isInteger(z.y)&&z.y>0&&z.y<w.n))return false;
      for(let i=0;i<w.rows.length;i++)if(dot(c,get(c,w.rows,i),z.y))return false;
      return check(c,dot(c,alg(c,s^t),z.y)===1);
    }
    return false;
  }
  const yes=z=>z.type==="path"||z.type==="coeff";
  function init(s,c){
    const p=Object.create(null),q=[];
    put(c,p,s,[-1,-1]);put(c,q,0,s);c.write++;
    return {p,q,h:0};
  }
  function path(s,t,st,c){
    const rev=[],p=[];
    for(let v=t;!check(c,v===s);){
      const [u,a]=get(c,st.p,v);put(c,rev,rev.length,a);v=u;
    }
    for(let j=rev.length-1;j>=0;j--)put(c,p,p.length,get(c,rev,j));
    return {type:"path",path:p};
  }
  function bfs(w,s,t,st,c,allow=null){
    while(get(c,st.p,t)===undefined&&!check(c,st.h===st.q.length)){
      const v=get(c,st.q,st.h);st.h++;c.write++;
      for(let a=0,d=deg(w,v,c);a<d;a++){
        const u=next(w,v,a,c);
        if(get(c,st.p,u)===undefined&&(!allow||allow(u))){
          put(c,st.p,u,[v,a]);put(c,st.q,st.q.length,u);
        }
      }
    }
    if(get(c,st.p,t)!==undefined)return path(s,t,st,c);
    must(!allow,"pruned path missing");
    const vertices=[];for(const v of st.q)put(c,vertices,vertices.length,read(c,v));
    return {type:"cut",vertices};
  }
  function gfBuild(w,c){
    const b=Array(w.d).fill(null);c.write+=w.d;
    for(let i=0;i<w.rows.length;i++){
      let v=get(c,w.rows,i),mask=1<<i;
      for(let p=w.d-1;p>=0;p--){
        if(!bit(c,v,p))continue;
        const a=get(c,b,p);
        if(a){v=alg(c,v^a.v);mask=alg(c,mask^a.mask)}
        else{put(c,b,p,{v,mask});break}
      }
    }
    return b;
  }
  function gfQuery(w,s,t,b,c){
    let v=alg(c,s^t),mask=0;
    for(let p=w.d-1;p>=0;p--){
      if(!bit(c,v,p))continue;
      const a=get(c,b,p);
      if(a){v=alg(c,v^a.v);mask=alg(c,mask^a.mask)}
    }
    if(check(c,v===0))return {type:"coeff",mask};
    let p=0;while(!bit(c,v,p))p++;
    let y=1<<p;
    for(let j=0;j<w.d;j++){const a=get(c,b,j);if(a&&dot(c,a.v,y))y=alg(c,y^(1<<j))}
    return {type:"separator",y};
  }
  function graphBuild(w,c){
    // Kosaraju SCCs, followed by reachability in the condensation DAG.
    const rev=Array.from({length:w.n},()=>[]),seen=Array(w.n).fill(false),order=[];c.write+=2*w.n;
    for(let v=0;v<w.n;v++)for(let j=0,d=deg(w,v,c);j<d;j++){
      const u=next(w,v,j,c),a=get(c,rev,u);put(c,a,a.length,v);
    }
    function visit(v){
      put(c,seen,v,true);
      for(let j=0,d=deg(w,v,c);j<d;j++){const u=next(w,v,j,c);if(!get(c,seen,u))visit(u)}
      put(c,order,order.length,v);
    }
    for(let v=0;v<w.n;v++)if(!get(c,seen,v))visit(v);
    const comp=Array(w.n).fill(-1);c.write+=w.n;let k=0;
    function mark(v){
      put(c,comp,v,k);
      const a=get(c,rev,v);for(const u of a)if(get(c,comp,read(c,u))===-1)mark(u);
    }
    for(let i=order.length-1;i>=0;i--){const v=get(c,order,i);if(get(c,comp,v)===-1){mark(v);k++}}
    const adj=Array(k).fill(0),reach=Array(k).fill(null);c.write+=2*k;
    for(let v=0;v<w.n;v++){
      const a=get(c,comp,v);
      for(let j=0,d=deg(w,v,c);j<d;j++){
        const b=get(c,comp,next(w,v,j,c));
        if(!check(c,a===b))put(c,adj,a,alg(c,get(c,adj,a)|(1<<b)));
      }
    }
    function closure(a){
      const cached=get(c,reach,a);if(cached!==null)return cached;
      let mask=1<<a;const edges=get(c,adj,a);
      for(let b=0;b<k;b++)if(bit(c,edges,b))mask=alg(c,mask|closure(b));
      put(c,reach,a,mask);return mask;
    }
    for(let a=0;a<k;a++)closure(a);
    return {comp,reach};
  }
  function graphQuery(w,s,t,o,c){
    const a=get(c,o.comp,s),b=get(c,o.comp,t),mask=get(c,o.reach,a);
    if(bit(c,mask,b)){
      const allow=u=>bit(c,get(c,o.reach,get(c,o.comp,u)),b)===1;
      return bfs(w,s,t,init(s,c),c,allow);
    }
    const vertices=[];
    for(let v=0;v<w.n;v++)if(bit(c,mask,get(c,o.comp,v)))put(c,vertices,vertices.length,v);
    return {type:"cut",vertices};
  }
  function orbitBuild(w,c){
    // Each functional-graph cycle shares its orbit mask; preperiod nodes
    // inherit the successor's orbit plus themselves.
    const reach=Array(w.n).fill(null),active=Array(w.n).fill(-1);c.write+=2*w.n;
    for(let s=0;s<w.n;s++){
      if(get(c,reach,s)!==null)continue;
      const p=[];let v=s;
      while(get(c,reach,v)===null&&get(c,active,v)===-1){
        put(c,active,v,p.length);put(c,p,p.length,v);v=next(w,v,0,c);
      }
      let mask=get(c,reach,v),stop=p.length;
      if(mask===null){
        stop=get(c,active,v);mask=0;
        for(let j=stop;j<p.length;j++)mask=alg(c,mask|(1<<get(c,p,j)));
        for(let j=stop;j<p.length;j++)put(c,reach,get(c,p,j),mask);
      }
      for(let j=stop-1;j>=0;j--){const u=get(c,p,j);mask=alg(c,mask|(1<<u));put(c,reach,u,mask)}
      for(const u of p)put(c,active,read(c,u),-1);
    }
    return reach;
  }
  function orbitQuery(w,s,t,o,c){
    const mask=get(c,o,s);
    if(bit(c,mask,t)){
      const path=[];let v=s;
      while(!check(c,v===t)){put(c,path,path.length,0);v=next(w,v,0,c)}
      return {type:"path",path};
    }
    const vertices=[];for(let v=0;v<w.n;v++)if(bit(c,mask,v))put(c,vertices,vertices.length,v);
    return {type:"cut",vertices};
  }
  function build(w,c){return w.kind==="graph"?graphBuild(w,c):w.kind==="gf2"?gfBuild(w,c):orbitBuild(w,c)}
  function specialized(w,s,t,o,c){return w.kind==="graph"?graphQuery(w,s,t,o,c):w.kind==="gf2"?gfQuery(w,s,t,o,c):orbitQuery(w,s,t,o,c)}
  function solve(w,queries,mode,k,oracle){
    const c=met(),cache=Object.create(null),cum=[];let o=null;
    if(mode==="eager")o=build(w,c);
    for(let i=0;i<queries.length;i++){
      const [s,t]=queries[i];
      if(mode==="switch"){c.check++;if(i===k)o=build(w,c)}
      let z;
      if(o!==null)z=specialized(w,s,t,o,c);
      else{
        let st=mode==="fresh"?undefined:get(c,cache,s);
        if(st===undefined){st=init(s,c);if(mode!=="fresh")put(c,cache,s,st)}
        z=bfs(w,s,t,st,c);
      }
      must(verify(w,s,t,z,c),"bad certificate");
      must(yes(z)===oracle(s,t),"oracle mismatch");
      cum.push(sum(c));
    }
    return {work:sum(c),closed:caps.map(b=>cum.filter(x=>x<=b*queries.length).length),categories:c};
  }
  const audit={worlds:0,pairs:0,negativePairs:0,invalidRejected:0,certifiedPairChecks:0},records=[];
  for(const split of ["cal","test"])for(const kind of families)for(let id=0;id<(split==="cal"?18:36);id++){
    const w=make(kind,split,id),oracle=truth(w),c=met(),o=build(w,c);
    audit.worlds++;
    for(let s=0;s<w.n;s++){
      const st=init(s,c);
      for(let t=0;t<w.n;t++){
        const expected=oracle(s,t),a=specialized(w,s,t,o,c),b=bfs(w,s,t,st,c);
        must(verify(w,s,t,a,c)&&yes(a)===expected,"specialized census");
        must(verify(w,s,t,b,c)&&yes(b)===expected,"lazy census");
        audit.pairs++;audit.negativePairs+=Number(!expected);audit.certifiedPairChecks+=2;
      }
    }
    must(!verify(w,0,1,{type:"path",path:[]},c),"bad path");
    must(!verify(w,0,1,{type:"cut",vertices:[]},c),"bad cut");
    must(!verify(w,0,0,{type:"cut",vertices:[0]},c),"bad self cut");
    audit.invalidRejected+=3;
    if(kind==="gf2"){
      must(!verify(w,0,1,{type:"coeff",mask:0},c),"bad coeff");
      must(!verify(w,0,0,{type:"separator",y:0},c),"bad separator");
      audit.invalidRejected+=2;
    }
    const q=stream(w),results={};
    for(const p of ["fresh","lazy","eager"])results[p]=solve(w,q,p,0,oracle);
    for(const k of ks)results["k"+k]=solve(w,q,"switch",k,oracle);
    records.push({split,kind,id,seed:w.seed,n:w.n,horizon:q.length,locality:id%3,results});
  }
  const calibration={};
  for(const kind of families){
    const train=records.filter(r=>r.split==="cal"&&r.kind===kind),cost={};
    for(const p of ["fresh","lazy","eager",...ks.map(k=>"k"+k)])cost[p]=train.reduce((v,r)=>v+r.results[p].work,0);
    const dispatch=["fresh","lazy","eager"].reduce((a,b)=>cost[a]<=cost[b]?a:b);
    const online=ks.map(k=>"k"+k).reduce((a,b)=>cost[a]<=cost[b]?a:b);
    calibration[kind]={dispatch,online,cost};
  }
  const test=records.filter(r=>r.split==="test");
  for(const r of test){
    const {dispatch,online}=calibration[r.kind];
    r.results.dispatch=r.results[dispatch];
    r.results.online=r.results[online];
  }
  function summarize(rr){
    const result={worlds:rr.length,requested:rr.reduce((a,r)=>a+r.horizon,0),arms:{}};
    for(const p of ["fresh","lazy","eager","dispatch","online"]){
      const regrets=rr.map(r=>r.results[p].work-r.results.dispatch.work);
      const cats=met();for(const r of rr)for(const k of Object.keys(cats))cats[k]+=r.results[p].categories[k];
      result.arms[p]={work:sum(cats),closed:caps.map((_,i)=>rr.reduce((v,r)=>v+r.results[p].closed[i],0)),wins:regrets.filter(x=>x<0).length,losses:regrets.filter(x=>x>0).length,worstExcess:Math.max(0,...regrets),categories:cats};
    }
    return result;
  }
  const overall=summarize(test),f=overall.arms;
  const gate=f.online.closed[1]>f.lazy.closed[1]&&f.online.closed[1]>f.dispatch.closed[1]&&f.online.work<=f.dispatch.work;
  return {id:"ACD-01C",status:"finite synthetic algorithm selection pilot",audit,caps,calibration,overall,byFamily:Object.fromEntries(families.map(k=>[k,summarize(test.filter(r=>r.kind===k))])),byHorizon:Object.fromEntries([1,4,16,32].map(h=>[h,summarize(test.filter(r=>r.horizon===h))])),gate,records};
};
const fingerprint = function fingerprint(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16).padStart(8,"0")};
const receipt={...run(),function_fingerprint:fingerprint(run.toString())};
if(process.argv.includes('--check')){
 const saved=JSON.parse(readFileSync(new URL('../output/evaluation_acd/acd_01c.json',import.meta.url),'utf8'));
 if(JSON.stringify(receipt)!==JSON.stringify(saved))throw Error('receipt mismatch');
 console.log('ACD-01C receipt verified');
}else console.log(JSON.stringify(receipt,null,2));
