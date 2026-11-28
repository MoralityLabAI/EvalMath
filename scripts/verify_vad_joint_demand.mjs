// VAD-13A: retrospective replay with joint demand and transitive library costs.
import fs from 'node:fs';
function replay(d){
 const rows=[];
 for(const tc of ["4.19.0","4.35.0"])for(const metric of ["work_ms","seconds"])for(const family of ["F1","F2","F3","F4","F5"]){
  const lib=d.library;
  const closure=names=>{const seen=new Set();function go(n){if(seen.has(n))return;seen.add(n);for(const dep of lib[n].imports||[])go(dep)}for(const n of names)go(n);return [...seen].sort()};
  const items=d.instances.filter(i=>i.family===family).map(i=>{const s=i.strategies,b=s.S_decide||s.S_direct;return {split:i.split,seed:i.seed,base:b[tc][metric],lemma:s.S_lemma[tc][metric],baseNeed:closure(b[tc].imports||[]),need:closure(s.S_lemma[tc].imports||[])}});
  const cal=items.filter(i=>i.split==="cal").sort((a,b)=>a.seed-b.seed),test=items.filter(i=>i.split==="test").sort((a,b)=>a.seed-b.seed);
  for(const horizon of [4,8,16,20])for(const method of ["direct","min","joint","independent","frechet","demand"]){
   const hist=[...cal],built=new Set();let total=0,build=0,proof=0,uses=0;
   const price=n=>lib[n].results[tc][metric];
   function acquire(ns){for(const n of ns)if(!built.has(n)){built.add(n);build+=price(n)}}
   const targets=test.slice(0,horizon);
   for(let j=0;j<targets.length;j++){
    const t=targets[j];acquire(t.baseNeed);
    const miss=t.need.filter(n=>!built.has(n));
    const marg=miss.map(n=>(hist.filter(x=>x.need.includes(n)).length+1)/(hist.length+2));
    let p=0;
    if(miss.length===0)p=1;
    else if(method==="min")p=Math.min(...marg);
    else if(method==="joint")p=(hist.filter(x=>miss.every(n=>x.need.includes(n))).length+1)/(hist.length+2);
    else if(method==="independent")p=marg.reduce((a,b)=>a*b,1);
    else if(method==="frechet")p=Math.max(0,marg.reduce((a,b)=>a+b,0)-marg.length+1);
    else if(method==="demand")p=1;
    const gain=Math.max(0,hist.reduce((a,x)=>a+x.base-x.lemma,0)/hist.length);
    if(method!=="direct"&&miss.length&&(method==="demand"||p*(targets.length-j)*gain>miss.reduce((a,n)=>a+price(n),0)))acquire(miss);
    if(method!=="direct"&&t.need.every(n=>built.has(n))){proof+=t.lemma;uses++}else proof+=t.base;
    hist.push(t);
   }
   total=proof+build;rows.push({tc,metric,family,horizon,method,total,build,proof,uses});
  }
 }
 const summary=[];
 for(const tc of ["4.19.0","4.35.0"])for(const metric of ["work_ms","seconds"])for(const horizon of [4,8,16,20]){
  const rr=rows.filter(x=>x.tc===tc&&x.metric===metric&&x.horizon===horizon);const b=rr.filter(x=>x.method==="direct").reduce((a,x)=>a+x.total,0);
  summary.push({tc,metric,horizon,gains:Object.fromEntries(["direct","min","joint","independent","frechet","demand"].map(m=>[m,b/rr.filter(x=>x.method===m).reduce((a,x)=>a+x.total,0)]))});
 }
 return {protocol:"VAD-13A",evidence:"retrospective isolated-file timing replay; no persistent execution",rows,summary};
}
const d=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));console.log(JSON.stringify(replay(d),null,2));
