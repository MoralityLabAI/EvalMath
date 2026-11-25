// SRG-15 local stage and full-policy scoring. Node 20+, no model calls.
// The SRG-08 planning runner can answer each public observation-history row.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {analyze,scorePolicy} from './belief-policy.mjs';
const fail=m=>{throw Error("SRG15 local: "+m);};
const hash=b=>crypto.createHash("sha256").update(b).digest("hex");
const jsonl=rows=>rows.map(x=>JSON.stringify(x)).join("\n")+"\n";
const root=fileURLToPath(new URL('../../../',import.meta.url));
const worldPath='integrations/sweepweave-ts/srg13/fixtures/reservoir-dogs-evidence-chain-candidate.swmd.md';
const receiptPath='output/evaluation_storyworld_reasoning/srg15_belief_policy.json';
export function informativeScore(exported,submissions,scorePolicy){
 const base=scorePolicy(exported,submissions),entries=new Map(),duplicate=new Set();
 for(const r of submissions){if(entries.has(r.id))duplicate.add(r.id);else entries.set(r.id,r);}
 const metrics={all_tie_rows:0,zero_optimum_rows:0,informative_rows:0,informative_correct:0,informative_mass:0,informative_correct_mass:0,positive_rows:0,positive_correct:0,positive_optimum_mass:0,credited_positive_mass:0};
 for(const g of exported.gold){
   const vals=Object.values(g.scores),hi=Math.max(...vals),lo=Math.min(...vals),r=entries.get(g.id);
   const valid=r&&!duplicate.has(g.id)&&Object.keys(r).sort().join(",")==="action,id"&&typeof r.action==="string"&&Object.hasOwn(g.scores,r.action);
   const correct=valid&&g.winners.includes(r.action);
   metrics.all_tie_rows+=Number(hi===lo);
   metrics.zero_optimum_rows+=Number(hi===0);
   if(hi>lo){metrics.informative_rows++;metrics.informative_correct+=Number(correct);metrics.informative_mass+=g.mass;metrics.informative_correct_mass+=correct?g.mass:0;}
   if(hi>0){metrics.positive_rows++;metrics.positive_correct+=Number(correct);metrics.positive_optimum_mass+=hi;metrics.credited_positive_mass+=valid?g.scores[r.action]:0;}
 }
 return {...base,decision_quality:metrics};
}
function pinned(){
 const receipt=JSON.parse(fs.readFileSync(path.join(root,receiptPath),"utf8"));
 for(const [p,sha] of Object.entries(receipt.source_blobs)){
   const b=fs.readFileSync(path.join(root,p));
   const got=crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex");
   if(got!==sha)fail("source drift "+p);
 }
 const result=analyze({api,source:fs.readFileSync(path.join(root,worldPath),"utf8")});
 const {source_blobs,scorer,...expected}=receipt;
 if(JSON.stringify(result.receipt)!==JSON.stringify(expected))fail("oracle receipt drift");
 const e=result.exported;
 if(jsonl(e.tasks)!==fs.readFileSync(new URL('./public/planning_tasks.jsonl',import.meta.url),"utf8")||jsonl(e.gold)!==fs.readFileSync(new URL('./public/planning_gold.jsonl',import.meta.url),"utf8"))fail("public corpus drift");
 return e;
}
function stage(out){
 const e=pinned(),p=path.resolve(out);fs.mkdirSync(p,{mode:0o700});
 fs.mkdirSync(path.join(p,"model_input"),{mode:0o700});fs.mkdirSync(path.join(p,"verifier"),{mode:0o700});
 const files={"model_input/planning.jsonl":jsonl(e.tasks),"verifier/planning_gold.jsonl":jsonl(e.gold)};
 const manifest={schema:"srg15.public_policy.v1",role:"public diagnostic; no secret test",mode:e.mode,h:e.h,roots:e.roots.length,files:{},source_sha256:hash(fs.readFileSync(new URL('./belief-policy.mjs',import.meta.url))),receipt_sha256:hash(fs.readFileSync(path.join(root,receiptPath)))};
 for(const [f,data] of Object.entries(files)){fs.writeFileSync(path.join(p,f),data,{flag:"wx",mode:0o600});manifest.files[f]={sha256:hash(data),bytes:Buffer.byteLength(data)};}
 fs.writeFileSync(path.join(p,"verifier/manifest.json"),JSON.stringify(manifest,null,2)+"\n",{flag:"wx",mode:0o600});
 console.log(JSON.stringify({tasks:e.tasks.length,roots:e.roots.length,mode:e.mode,h:e.h,output:p},null,2));
}
function score(dir,sub){
 const m=JSON.parse(fs.readFileSync(path.join(dir,"verifier/manifest.json"),"utf8"));
 if(m.schema!=="srg15.public_policy.v1"||m.source_sha256!==hash(fs.readFileSync(new URL('./belief-policy.mjs',import.meta.url)))||m.receipt_sha256!==hash(fs.readFileSync(path.join(root,receiptPath))))fail("manifest drift");
 for(const f of ["model_input/planning.jsonl","verifier/planning_gold.jsonl"])if(hash(fs.readFileSync(path.join(dir,f)))!==m.files[f].sha256)fail("file drift "+f);
 const e=pinned();
 if(hash(jsonl(e.tasks))!==m.files["model_input/planning.jsonl"].sha256||hash(jsonl(e.gold))!==m.files["verifier/planning_gold.jsonl"].sha256)fail("recomputed corpus drift");
 const rows=fs.readFileSync(sub,"utf8").split(/\r?\n/).filter(Boolean).map(JSON.parse);
 console.log(JSON.stringify(informativeScore(e,rows,scorePolicy),null,2));
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [cmd,a,b]=process.argv.slice(2);
 if(cmd==="stage"&&a)stage(a);
 else if(cmd==="score"&&a&&b)score(a,b);
 else fail("stage <new-dir> | score <staged-dir> <submissions.jsonl>");
}
