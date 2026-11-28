// ACD-01B, dependency-free finite certificate benchmark (Node 18+).
import {readFileSync} from 'node:fs';
const run = function run() {
  const must=(x,m)=>{if(!x)throw Error(m)};
  const rand=seed=>{let x=seed>>>0;return n=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)%n}};
  const kinds=["graph","gf2","recurrence"], horizons=[1,4,16,32], caps=[64,256,1024];
  const policies=["direct","memo","eager","audited","lazy"];
  const meter=()=>({read:0,write:0,edge:0,check:0});
  const add=(a,b)=>Object.fromEntries(Object.keys(a).map(k=>[k,a[k]+b[k]]));
  const total=c=>Object.values(c).reduce((a,b)=>a+b,0);
  const read=(m,x)=>{m.read++;return x};
  const put=(m,o,k,v)=>{m.write++;o[k]=v};
  const check=(m,x)=>{m.check++;return x};
  const degree=(w,v,m)=>read(m,w.kind==="graph"?w.adj[v].length:w.kind==="gf2"?w.rows.length:1);
  function next(w,v,a,m){
    m.edge++;
    if(w.kind==="graph")return w.adj[v][a];
    if(w.kind==="gf2")return v^w.rows[a];
    return (w.a*v+w.b)%w.n;
  }
  function make(kind,split,id) {
    const seed=(split==="cal"?11000:91000)+kinds.indexOf(kind)*1000+id+1;
    const r=rand(seed),n=[16,32,64][id%3],src=kind==="gf2"?0:r(n);
    if(kind==="graph"){
      // calibration: split-cluster random edges; test: chain/cycle with long-range shortcuts.
      const adj=Array.from({length:n},()=>[]);
      for(let v=0;v<n;v++){
        const base=v<n/2?0:n/2;
        if(split==="cal"){
          for(let k=0;k<1+id%4;k++)adj[v].push(base+r(n/2));
          if(id%3===0)adj[v].push(r(n));
        }else{
          adj[v].push(base+(v-base+1)%(n/2));
          if(id%2)adj[v].push(base+r(n/2));
          if(id%3===0)adj[v].push(r(n));
        }
      }
      return {kind,split,id,seed,n,src,adj};
    }
    if(kind==="gf2"){
      const d=Math.log2(n),rank=1+id%d;
      const b=Array.from({length:d},(_,i)=>1<<i);
      for(let k=0;k<5*d;k++){const i=r(d),j=r(d);if(i!==j)b[i]^=b[j]}
      const rows=b.slice(0,rank);
      for(let k=0;k<(split==="cal"?2:5);k++){
        const mask=r(1<<rank);let v=0;
        for(let j=0;j<rank;j++)if((mask>>>j)&1)v^=b[j];
        rows.push(v);
      }
      return {kind,split,id,seed,n,src,rows,rank};
    }
    const a=split==="cal"?1+2*r(n/2):2*r(n/2);
    const b=r(n);
    return {kind,split,id,seed,n,src,a,b};
  }
  function oracle(w){
    if(w.kind==="gf2"){
      const s=new Set([0]);
      for(const g of w.rows)for(const v of [...s])s.add(v^g);
      must(s.size===2**w.rank,"rank mismatch");
      return s;
    }
    if(w.kind==="recurrence"){
      // Independent finite sequence bound; n+1 states force a repeat.
      const s=new Set();let v=w.src;
      for(let i=0;i<=w.n;i++){s.add(v);v=(w.a*v+w.b)%w.n}
      return s;
    }
    // Independent transitive-closure oracle.
    const R=Array.from({length:w.n},(_,i)=>Array.from({length:w.n},(_,j)=>i===j||w.adj[i].includes(j)));
    for(let k=0;k<w.n;k++)for(let i=0;i<w.n;i++)if(R[i][k])for(let j=0;j<w.n;j++)R[i][j] ||= R[k][j];
    return new Set(R[w.src].flatMap((x,j)=>x?[j]:[]));
  }
  function init(w,m){
    const parent=Object.create(null),queue=[];
    put(m,parent,w.src,[-1,-1]);put(m,queue,0,w.src);m.write++;
    return {parent,queue,head:0};
  }
  function step(w,s,m){
    const v=read(m,s.queue[s.head]);
    s.head++;m.write++;
    const d=degree(w,v,m);
    for(let a=0;a<d;a++){
      const u=next(w,v,a,m);
      if(read(m,s.parent[u])===undefined){
        put(m,s.parent,u,[v,a]);put(m,s.queue,s.queue.length,u);
      }
    }
  }
  const done=(s,m)=>check(m,s.head===s.queue.length);
  function expand(w,s,t,m){
    while(read(m,s.parent[t])===undefined&&!done(s,m))step(w,s,m);
  }
  function complete(w,s,m){while(!done(s,m))step(w,s,m)}
  function certificate(w,s,t,m){
    if(read(m,s.parent[t])===undefined){
      must(done(s,m),"negative before exhausted");
      const set=[];
      for(const v of s.queue)put(m,set,set.length,read(m,v));
      return {yes:false,set};
    }
    const path=[];let v=t;
    while(!check(m,v===w.src)){
      const [p,a]=read(m,s.parent[v]);
      put(m,path,path.length,a);v=p;
    }
    // Reverse traversal writes are charged, including the resulting path.
    const f=[];
    for(let i=path.length-1;i>=0;i--)put(m,f,f.length,read(m,path[i]));
    return {yes:true,path:f};
  }
  function verify(w,t,c,m){
    if(c.yes){
      let v=w.src;
      for(const a of c.path){
        if(!check(m,Number.isInteger(a)&&a>=0&&a<degree(w,v,m)))return false;
        v=next(w,v,a,m);
      }
      return check(m,v===t);
    }
    const s=Object.create(null);
    for(const v of c.set){
      if(!check(m,Number.isInteger(v)&&v>=0&&v<w.n))return false;
      put(m,s,v,true);
    }
    if(!check(m,read(m,s[w.src])===true&&read(m,s[t])!==true))return false;
    for(const v of c.set)for(let a=0,d=degree(w,v,m);a<d;a++)if(!check(m,read(m,s[next(w,v,a,m)])===true))return false;
    return true;
  }
  function audit(w,s,m){
    // Check all path certificates and closure of the entire index, no target labels.
    const members=Object.create(null);
    for(const v of s.queue){
      if(!verify(w,v,certificate(w,s,v,m),m))return false;
      put(m,members,v,true);
    }
    for(const v of s.queue)for(let a=0,d=degree(w,v,m);a<d;a++)if(!check(m,read(m,members[next(w,v,a,m)])===true))return false;
    return check(m,read(m,members[w.src])===true);
  }
  function evalPolicy(w,targets,policy,truth){
    const m=meter(),mem=Object.create(null);
    let state=null;
    if(["eager","audited","lazy"].includes(policy)){
      state=init(w,m);
      if(policy!=="lazy")complete(w,state,m);
      if(policy==="audited")must(audit(w,state,m),"audit failed");
    }
    const cumulative=[],answers=[];
    for(const t of targets){
      let c;
      if(policy==="memo")c=read(m,mem[t]);
      if(c===undefined){
        const s=state??init(w,m);
        if(policy!=="eager"&&policy!=="audited")expand(w,s,t,m);
        c=certificate(w,s,t,m);
        if(policy==="memo")put(m,mem,t,c);
      }
      must(verify(w,t,c,m),"invalid proof");
      must(c.yes===truth.has(t),"oracle mismatch");
      answers.push(c.yes);
      cumulative.push(total(m));
    }
    return {work:total(m),categories:m,cumulative,answers};
  }
  const records=[],auditCounts={worlds:0,uniqueWorldTargets:0,negativeWorldTargets:0,invalidRejected:0};
  for(const split of ["cal","test"])for(const kind of kinds)for(let id=0;id<12;id++){
    const w=make(kind,split,id),truth=oracle(w);
    auditCounts.worlds++;
    // exhaustive per-world correctness independent of stream sampling
    const all=Array.from({length:w.n},(_,i)=>i);
    const exact=evalPolicy(w,all,"audited",truth);
    must(exact.answers.length===w.n,"incomplete census");
    auditCounts.uniqueWorldTargets+=w.n;
    auditCounts.negativeWorldTargets+=w.n-truth.size;
    must(!verify(w,(w.src+1)%w.n,{yes:true,path:[]},meter()),"bad path accepted");
    must(!verify(w,w.src,{yes:false,set:[w.src]},meter()),"bad exclusion accepted");
    must(!verify(w,(w.src+1)%w.n,{yes:false,set:[]},meter()),"bad closure accepted");
    auditCounts.invalidRejected+=3;
    const g=rand(w.seed^0xdecafbad);
    const targets=Array.from({length:32},()=>g(w.n));
    for(const n of horizons){
      const chosen=targets.slice(0,n),result={};
      for(const p of policies){
        const x=evalPolicy(w,chosen,p,truth);
        result[p]={work:x.work,closed:caps.map(c=>x.cumulative.filter(v=>v<=c*n).length),categories:x.categories};
      }
      records.push({split,kind,id,n,states:w.n,reachable:truth.size,result});
    }
  }
  // Leave one mathematical family out of calibration. The selector sees only the announced horizon.
  // Selection itself is charged one abstract table lookup per stream, via an explicit offset on prefixes.
  // Since a single extra work unit could change a boundary, rerun selected streams to compute exact caps.
  const selector={},summary=[];
  for(const hold of kinds){
    selector[hold]={};
    for(const n of horizons){
      const train=records.filter(r=>r.split==="cal"&&r.kind!==hold&&r.n===n);
      const cost=Object.fromEntries(policies.map(p=>[p,train.reduce((s,r)=>s+r.result[p].work,0)]));
      selector[hold][n]={policy:policies.reduce((a,b)=>cost[a]<=cost[b]?a:b),calibrationWork:cost,calibrationWorlds:train.length};
    }
  }
  for(const r of records.filter(r=>r.split==="test")){
    const p=selector[r.kind][r.n].policy;
    const w=make(r.kind,"test",r.id),g=rand(w.seed^0xdecafbad),targets=Array.from({length:r.n},()=>g(w.n)),truth=oracle(w);
    const x=evalPolicy(w,targets,p,truth);
    r.result.selector={work:x.work+1,closed:caps.map(c=>x.cumulative.filter(v=>v+1<=c*r.n).length),categories:{...x.categories,read:x.categories.read+1},policy:p};
    const choose=policies[rand(w.seed^0xabcdef01^r.n)(policies.length)];
    const y=evalPolicy(w,targets,choose,truth);
    r.result.random={work:y.work+1,closed:caps.map(c=>y.cumulative.filter(v=>v+1<=c*r.n).length),categories:{...y.categories,read:y.categories.read+1},policy:choose};
    must(x.work===r.result[p].work,"selector replay");
  }
  for(const n of horizons){
    const test=records.filter(r=>r.split==="test"&&r.n===n);
    const results={};
    for(const p of [...policies,"selector","random"]){
      results[p]={work:test.reduce((s,r)=>s+r.result[p].work,0),closed:caps.map((_,i)=>test.reduce((s,r)=>s+r.result[p].closed[i],0)),winsVsLazy:test.filter(r=>r.result[p].work<r.result.lazy.work).length,lossesVsLazy:test.filter(r=>r.result[p].work>r.result.lazy.work).length,categories:test.reduce((s,r)=>add(s,r.result[p].categories),meter())};
    }
    summary.push({horizon:n,worlds:test.length,requested:test.length*n,results});
  }
  const familySummary=kinds.map(kind=>({kind,horizons:horizons.map(n=>{
    const test=records.filter(r=>r.split==="test"&&r.kind===kind&&r.n===n);
    return {n,selected:selector[kind][n].policy,work:Object.fromEntries([...policies,"selector","random"].map(p=>[p,test.reduce((s,r)=>s+r.result[p].work,0)]))};
  })}));
  return {id:"ACD-01B",status:"exploratory synthetic finite mechanism",auditCounts,caps,selector,summary,familySummary,records};
};
const fingerprint = function fingerprint(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16).padStart(8,"0")};
const result={...run(),function_fingerprint: fingerprint(run.toString())};
if(process.argv.includes('--check')){
 const saved=JSON.parse(readFileSync(new URL('../output/evaluation_acd/acd_01b.json',import.meta.url),'utf8'));
 if(JSON.stringify(result)!==JSON.stringify(saved))throw Error('receipt mismatch');
 console.log('ACD-01B receipt verified');
}else console.log(JSON.stringify(result,null,2));
