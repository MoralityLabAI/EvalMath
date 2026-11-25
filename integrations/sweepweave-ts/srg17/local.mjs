// Node 20+ model-facing staging and verifier scoring.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {corpus,score,SEED} from './planning.mjs';
import {buildBelief,scoreBelief,ESEED} from './epistemic.mjs';
import {buildOrder,scoreOrder,OSEED} from './order-witness.mjs';
const fail=m=>{throw Error("SRG17 local: "+m);};
const hash=b=>crypto.createHash("sha256").update(b).digest("hex");
const jsonl=rows=>rows.map(x=>JSON.stringify(x)).join("\n")+"\n";
const sources=()=>Object.fromEntries(["planning.mjs","epistemic.mjs","order-witness.mjs","local.mjs"].map(f=>[f,hash(fs.readFileSync(new URL("./"+f,import.meta.url)))]));
const defaults={planning:[SEED,1],belief:[ESEED,16],order:[OSEED,1]};
function build(kind,seed,reps){
 if(!Object.hasOwn(defaults,kind)||!Number.isInteger(seed)||seed<=0||seed>0xffffffff||!Number.isInteger(reps)||reps<1)fail("family/seed/reps");
 if(kind==="planning")return corpus(seed,reps,true);
 if(kind==="belief")return buildBelief(seed,reps,false);
 return buildOrder(seed,reps);
}
function stage(dir,kind,seed,reps){
 if(!Object.hasOwn(defaults,kind))fail("unknown family");
 seed=seed===undefined?defaults[kind][0]:Number(seed);reps=reps===undefined?defaults[kind][1]:Number(reps);
 const e=build(kind,seed,reps),p=path.resolve(dir);
 fs.mkdirSync(p,{mode:0o700});fs.mkdirSync(path.join(p,"model_input"),{mode:0o700});fs.mkdirSync(path.join(p,"verifier"),{mode:0o700});
 const files={"model_input/planning.jsonl":jsonl(e.tasks),"verifier/planning_gold.jsonl":jsonl(e.gold)};
 const m={schema:"srg17.stage.v1",kind,seed,reps,rows:e.tasks.length,source_hashes:sources(),files:{}};
 for(const [f,s] of Object.entries(files)){fs.writeFileSync(path.join(p,f),s,{flag:"wx",mode:0o600});m.files[f]={sha256:hash(s),bytes:Buffer.byteLength(s)};}
 fs.writeFileSync(path.join(p,"verifier/manifest.json"),JSON.stringify(m,null,2)+"\n",{flag:"wx",mode:0o600});
 console.log(JSON.stringify({kind,rows:e.tasks.length,output:p},null,2));
}
function grade(dir,submission){
 const m=JSON.parse(fs.readFileSync(path.join(dir,"verifier/manifest.json"),"utf8"));
 if(m.schema!=="srg17.stage.v1"||JSON.stringify(m.source_hashes)!==JSON.stringify(sources()))fail("source drift");
 const e=build(m.kind,m.seed,m.reps);
 if(e.tasks.length!==m.rows)fail("count drift");
 for(const [f,s] of Object.entries({"model_input/planning.jsonl":jsonl(e.tasks),"verifier/planning_gold.jsonl":jsonl(e.gold)})){
  const raw=fs.readFileSync(path.join(dir,f));if(raw.length!==m.files[f].bytes||hash(raw)!==m.files[f].sha256||hash(s)!==m.files[f].sha256)fail("corpus drift "+f);
 }
 const sub=fs.readFileSync(submission,"utf8").split(/\r?\n/).filter(x=>x.trim()).map(x=>{try{return JSON.parse(x);}catch{return null;}});
 const result=m.kind==="planning"?score(e,sub):m.kind==="belief"?scoreBelief(e,sub):scoreOrder(e,sub);
 console.log(JSON.stringify({family:m.kind,...result},null,2));
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [cmd,a,b,c,d,...rest]=process.argv.slice(2);
 if(rest.length)fail("too many args");
 if(cmd==="stage"&&a&&b)stage(a,b,c,d);
 else if(cmd==="score"&&a&&b&&c===undefined)grade(a,b);
 else fail("stage <new-dir> <planning|belief|order> [uint32 seed] [reps] | score <staged-dir> <submissions.jsonl>");
}
