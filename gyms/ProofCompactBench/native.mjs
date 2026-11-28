import fs from 'node:fs';
import {createHash} from 'node:crypto';
function nativeLibrary(){
 const must=(x,m)=>{if(!x)throw Error(m)};
 const metrics=["median_seconds","median_peak_rss_kib","olean_bytes"];
 const finite=x=>typeof x==="number"&&Number.isFinite(x)&&x>=0;
 const med=xs=>xs.slice().sort((a,b)=>a-b)[1];
 function make(receipt){
  must(receipt.schema==="grhc-native-factoring-v1"&&/version 4\.35\.0/.test(receipt.lean)&&receipt.uniformity_controls==="passed"&&receipt.scope==="synthetic Lean fixtures, compilation RSS/time; kernel replay separate; not GRH proof replay","native receipt status");
  const pairs=new Map();
  for(const r of receipt.rows){
   must(["seesaw","index"].includes(r.family)&&[8,32,128].includes(r.width)&&["inline","factored"].includes(r.variant),"unexpected task");
   must(r.kernel_replay==="passed"&&Array.isArray(r.axioms)&&new Set(r.axioms).size===r.axioms.length&&r.axioms.every(x=>x==="propext")&&/^[0-9a-f]{64}$/.test(r.source_sha256),"native acceptance");
   must(metrics.every(k=>finite(r[k]))&&r.olean_bytes>0&&r.median_peak_rss_kib>0,"cost");
   must(Array.isArray(r.compile_trials)&&r.compile_trials.length===3&&r.compile_trials.every(t=>finite(t.seconds)&&finite(t.peak_rss_kib)&&t.peak_rss_kib>0)&&r.median_seconds===med(r.compile_trials.map(t=>t.seconds))&&r.median_peak_rss_kib===med(r.compile_trials.map(t=>t.peak_rss_kib)),"trial accounting");
   const m=r.measurement;
   must(m&&Number.isSafeInteger(m.root_body_objects)&&m.root_body_objects>0&&Number.isSafeInteger(m.local_closure_body_objects)&&m.local_closure_body_objects>=m.root_body_objects&&Array.isArray(m.local_declarations)&&new Set(m.local_declarations.map(d=>d.name)).size===m.local_declarations.length&&m.local_declarations.every(d=>typeof d.name==="string"&&Number.isSafeInteger(d.body_objects)&&d.body_objects>=0),"body counts");
   must(m.local_declarations.reduce((a,x)=>a+x.body_objects,0)===m.local_closure_body_objects&&m.local_declarations.find(d=>d.name==="GRHCFixture.root")?.body_objects===m.root_body_objects,"body accounting");
   const id=`native-${r.family}-${r.width}`,p=pairs.get(id)??{};
   must(!p[r.variant],"duplicate candidate");p[r.variant]=r;pairs.set(id,p);
  }
  must(pairs.size===6,"missing fixture pairs");
  return [...pairs.entries()].map(([id,p])=>{
   must(p.inline&&p.factored&&p.inline.source_sha256!==p.factored.source_sha256&&JSON.stringify([...p.inline.axioms].sort())===JSON.stringify([...p.factored.axioms].sort()),"unmatched pair");
   const row={id,family:p.inline.family,width:p.inline.width,split:"native_public_development",task:"Choose inline or factored proof representation. Minimize total reachable local expression objects. The native runner holds the statement fixed and requires identical axiom sets and kernel replay. Return {variant:'inline'|'factored'}. Runtime/RSS and parent size are separately reported.",actions:["inline","factored"]};
   const costs=Object.fromEntries(Object.entries(p).map(([v,r])=>[v,{closure:r.measurement.local_closure_body_objects,parent:r.measurement.root_body_objects,compile_seconds:r.median_seconds,peak_rss_kib:r.median_peak_rss_kib,olean_bytes:r.olean_bytes,source_sha256:r.source_sha256}]));
   const optimum=Math.min(...Object.values(costs).map(c=>c.closure));
   return {packet:row,costs,optimum,axioms:p.inline.axioms};
  });
 }
 function score(rows,preds){
  const ids=new Set(rows.map(r=>r.packet.id)),map=new Map();for(const p of preds){must(p&&Object.keys(p).length===2&&ids.has(p.id)&&!map.has(p.id)&&Object.hasOwn(p,"answer"),"invalid prediction id");map.set(p.id,p.answer)}
  return rows.map(r=>{
   const a=map.get(r.packet.id),c=a&&Object.keys(a).length===1&&Object.hasOwn(a,"variant")&&Object.hasOwn(r.costs,a.variant)?r.costs[a.variant]:null;
   return {id:r.packet.id,valid:!!c,optimal:!!c&&c.closure===r.optimum,score:c?(r.optimum+1)/(c.closure+1):0,cost:c||null};
  });
 }
 function test(){
   const rows=[];for(const family of ["seesaw","index"])for(const width of [8,32,128])for(const variant of ["inline","factored"]){
    const n=variant==="inline"?100:105;rows.push({family,width,variant,source_sha256:(variant==="inline"?"a":"b").repeat(64),kernel_replay:"passed",axioms:family==="index"?["propext"]:[],median_seconds:0.1,median_peak_rss_kib:100,olean_bytes:100,compile_trials:Array.from({length:3},()=>({seconds:0.1,peak_rss_kib:100})),measurement:{root_body_objects:variant==="inline"?90:5,local_closure_body_objects:n,local_declarations:[{name:"GRHCFixture.root",body_objects:variant==="inline"?90:5},{name:"helper",body_objects:variant==="inline"?10:100}]}})
   }
   const receipt={schema:"grhc-native-factoring-v1",lean:"Lean (version 4.35.0)",uniformity_controls:"passed",scope:"synthetic Lean fixtures, compilation RSS/time; kernel replay separate; not GRH proof replay",rows},tasks=make(receipt);
   must(tasks.length===6&&tasks.every(r=>r.optimum===100),"closure scoring");
   must(score(tasks,tasks.map(r=>({id:r.packet.id,answer:{variant:"inline"}}))).every(r=>r.optimal),"inline control");
   must(score(tasks,tasks.map(r=>({id:r.packet.id,answer:{variant:"factored"}}))).every(r=>r.valid&&!r.optimal),"parent-only trap");
   must(score(tasks,[]).every(r=>r.score===0),"missing");
   let rejected=0;for(const change of [r=>r.rows[0].kernel_replay="failed",r=>r.rows[0].axioms=["propext"],r=>r.rows[0].measurement.local_closure_body_objects=1,r=>r.rows.pop()]){
     const copy=JSON.parse(JSON.stringify(receipt));change(copy);try{make(copy)}catch{rejected++}
   }
   must(rejected===4,"negative controls");return {status:"passed",synthetic_receipt_controls:8,native_cost_data:"not generated by test"};
 }
 return {make,score,test};
}
const L=nativeLibrary(),[mode,file,sha,preds]=process.argv.slice(2);
if(mode==="self-test")console.log(JSON.stringify(L.test(),null,2));
else{
 if(!["packets","grade"].includes(mode)||!file||!sha)throw Error("native.mjs packets RECEIPT SHA256 | grade RECEIPT SHA256 PRED.jsonl");
 const bytes=fs.readFileSync(file);if(createHash("sha256").update(bytes).digest("hex")!==sha)throw Error("trusted receipt hash mismatch");
 const tasks=L.make(JSON.parse(bytes.toString("utf8")));
 if(mode==="packets")for(const r of tasks)console.log(JSON.stringify(r.packet));
 else{
  if(!preds)throw Error("predictions required");
  const rows=L.score(tasks,fs.readFileSync(preds,"utf8").split(/\r?\n/).filter(Boolean).map(JSON.parse));
  console.log(JSON.stringify({schema:"proofcompactbench-native-menu-score-v1",receipt_sha256:sha,total:rows.length,valid:rows.filter(r=>r.valid).length,optimal:rows.filter(r=>r.optimal).length,rows},null,2));
 }
}
