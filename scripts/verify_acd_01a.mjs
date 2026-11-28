// ACD-01A exact finite cost pilot. Node.js 18+, no dependencies.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
const run = function run() {
  const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
  function rng(seed) {
    let x=seed>>>0;
    return n=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)%n};
  }
  function shuffle(a,r) {
    for(let i=a.length-1;i>0;i--){const j=r(i+1);[a[i],a[j]]=[a[j],a[i]]}
    return a;
  }
  function meter(){return {work:0}}
  function probe(x,p,c){c.work++;return (x>>>p)&1}
  function xor(a,b,c){c.work++;return a^b}
  function dot(a,b,c){
    c.work++;let x=a&b,z=0;
    while(x){z^=1;x&=x-1}return z;
  }
  function read(a,i,c){c.work++;return a[i]}
  function check(x,c){c.work++;return x}
  function basis(rows,d,c){
    const b=Array(d).fill(null);
    for(let i=0;i<rows.length;i++){
      let v=read(rows,i,c),w=1<<i;
      for(let p=d-1;p>=0;p--){
        if(!probe(v,p,c))continue;
        const a=read(b,p,c);
        if(a){v=xor(v,a.v,c);w=xor(w,a.w,c)}
        else{c.work++;b[p]={v,w};break}
      }
    }
    return b;
  }
  function reduce(t,b,d,c){
    let v=t,w=0;
    for(let p=d-1;p>=0;p--){
      if(!probe(v,p,c))continue;
      const a=read(b,p,c);
      if(a){v=xor(v,a.v,c);w=xor(w,a.w,c)}
    }
    return {v,w};
  }
  function verify(rows,t,cert,c){
    if(cert.member){
      if(!check(Number.isInteger(cert.w)&&cert.w>=0&&cert.w<(1<<rows.length),c))return false;
      let v=0;
      for(let i=0;i<rows.length;i++)if(probe(cert.w,i,c))v=xor(v,read(rows,i,c),c);
      return check(v===t,c);
    }
    if(!check(Number.isInteger(cert.y)&&cert.y>0,c))return false;
    for(let i=0;i<rows.length;i++)if(dot(read(rows,i,c),cert.y,c))return false;
    return check(dot(t,cert.y,c)===1,c);
  }
  function query(rows,t,b,d,c){
    const {v,w}=reduce(t,b,d,c);
    let cert;
    if(check(v===0,c))cert={member:true,w};
    else{
      let p=0;
      while(!probe(v,p,c))p++;
      let y=1<<p;
      for(let j=0;j<d;j++){
        const a=read(b,j,c);
        if(a&&dot(a.v,y,c))y=xor(y,1<<j,c);
      }
      cert={member:false,y};
    }
    assert(verify(rows,t,cert,c),"certificate rejected");
    return cert;
  }
  function audit(rows,b,d,c){
    for(let p=0;p<d;p++){
      const a=read(b,p,c);
      if(a&&(!check((a.v>>>p)===1,c)||!verify(rows,a.v,{member:true,w:a.w},c)))return false;
    }
    for(let i=0;i<rows.length;i++)
      if(!check(reduce(read(rows,i,c),b,d,c).v===0,c))return false;
    return true;
  }
  function world(d,r,seed){
    const g=rng(seed),v=Array.from({length:d},(_,i)=>1<<i);
    for(let j=0;j<5*d;j++){
      const a=g(d),b=g(d);if(a!==b)v[a]^=v[b];
    }
    const rows=v.slice(0,r);
    while(rows.length<d+3){
      let x=0,mask=g(1<<r);
      for(let i=0;i<r;i++)if((mask>>>i)&1)x^=v[i];
      rows.push(x);
    }
    return shuffle(rows,g);
  }
  function oracle(rows){
    let s=new Set([0]);
    for(const x of rows)for(const a of Array.from(s))s.add(x^a);
    return s;
  }
  const sizes=[1,2,4,8,16,32,64],rates=[64,128,256];
  const sums=sizes.map(n=>({n,fresh:0,cache:0,audited_cache:0,free_oracle:0,worlds_audited_cache_wins:0}));
  const budgets=[8,32].flatMap(n=>rates.map(rate=>({n,budget_per_requested_query:rate,fresh_closed:0,cache_closed:0,audited_cache_closed:0,requested:0})));
  const worlds=[];
  let nqueries=0,negative=0,rejections=0;
  for(const d of [6,8])for(const rank of [d/2,d-1,d])for(let rep=0;rep<4;rep++){
    const seed=10000+d*1000+rank*10+rep;
    const rows=world(d,rank,seed);
    const truth=oracle(rows);
    assert(truth.size===(1<<rank),"rank mismatch");
    const c=meter(),b=basis(rows,d,c),B=c.work;
    const ac=meter();
    assert(audit(rows,b,d,ac),"basis audit failed");
    const A=ac.work;
    const corrupt=b.map(x=>x&&({...x}));
    corrupt.find(x=>x).w=0;
    assert(!audit(rows,corrupt,d,meter()),"bad provenance accepted");rejections++;
    const nonzero=rows.findIndex(x=>x!==0);
    assert(!verify(rows,0,{member:true,w:1<<nonzero},meter()),"bad member certificate accepted");rejections++;
    assert(!verify(rows,0,{member:false,y:0},meter()),"bad nonmember certificate accepted");rejections++;
    const targets=shuffle(Array.from({length:1<<d},(_,i)=>i),rng(seed^0x9e3779b9));
    const costs=[];
    for(const t of targets){
      const q=meter(),cert=query(rows,t,b,d,q);
      assert(cert.member===truth.has(t),"oracle mismatch");
      // Rebuild independently per query and check identical answers and work.
      const f=meter(),fresh=basis(rows,d,f),freshCert=query(rows,t,fresh,d,f);
      assert(freshCert.member===cert.member&&f.work===B+q.work,"fresh accounting mismatch");
      costs.push(q.work);nqueries++;if(!cert.member)negative++;
    }
    const threshold=2+Math.floor(A/B);
    worlds.push({d,rank,rep,seed,rows,build:B,audit:A,first_strict_amortized_win:threshold,
      full_queries:targets.length,query_work_sum:costs.reduce((a,x)=>a+x,0)});
    for(const s of sums){
      const q=costs.slice(0,s.n).reduce((a,x)=>a+x,0);
      s.fresh+=s.n*B+q;s.cache+=B+q;s.audited_cache+=B+A+q;s.free_oracle+=q;
      s.worlds_audited_cache_wins+=Number(B+A+q<s.n*B+q);
      assert((B+A+q<s.n*B+q)===(s.n>=threshold),"threshold mismatch");
    }
    for(const s of budgets){
      const cap=s.n*s.budget_per_requested_query;
      let f=0,k=B,a=B+A,fc=0,kc=0,ac=0;
      for(const q of costs.slice(0,s.n)){
        f+=B+q;k+=q;a+=q;
        fc+=Number(f<=cap);kc+=Number(k<=cap);ac+=Number(a<=cap);
      }
      s.fresh_closed+=fc;s.cache_closed+=kc;s.audited_cache_closed+=ac;s.requested+=s.n;
    }
  }
  return {id:"ACD-01A",evidence:"finite verified synthetic mechanism",world_count:worlds.length,
    unique_world_target_pairs:nqueries,negative_pairs:negative,invalid_certificate_rejections:rejections,
    source_independent_oracle:"iterative exhaustive span closure",
    cost_unit:"one bitset probe, xor, parity, indexed read/write, or explicit check; offline oracle and loop/control overhead excluded",
    threshold_range:[Math.min(...worlds.map(w=>w.first_strict_amortized_win)),Math.max(...worlds.map(w=>w.first_strict_amortized_win))],
    aggregate_prefix_work:sums,budget_grid:budgets,worlds};
};
const receipt = {...run(), source_sha256:createHash('sha256').update(readFileSync(new URL(import.meta.url))).digest('hex')};
if(process.argv.includes('--check')) {
  const saved=JSON.parse(readFileSync(new URL('../output/evaluation_acd/acd_01a.json',import.meta.url),'utf8'));
  if(JSON.stringify(receipt)!==JSON.stringify(saved))throw Error('receipt mismatch');
  console.log('ACD-01A receipt verified');
} else console.log(JSON.stringify(receipt,null,2));
