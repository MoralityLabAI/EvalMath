// Stage public model inputs separately from verifier-only labels.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {build,score,DEFAULT_SEED,DEFAULT_REPS} from './benchmark.mjs';
const fail=m=>{throw Error("SRG16 local: "+m);};
const hash=b=>crypto.createHash("sha256").update(b).digest("hex");
const jsonl=rows=>rows.map(x=>JSON.stringify(x)).join("\n")+"\n";
const sourceHash=()=>hash(fs.readFileSync(new URL('./benchmark.mjs',import.meta.url)));
function stage(out,seed=DEFAULT_SEED,reps=DEFAULT_REPS){
 const e=build(seed,reps),dir=path.resolve(out);
 fs.mkdirSync(dir,{mode:0o700});
 fs.mkdirSync(path.join(dir,"model_input"),{mode:0o700});
 fs.mkdirSync(path.join(dir,"verifier"),{mode:0o700});
 const files={"model_input/planning.jsonl":jsonl(e.tasks),"verifier/planning_gold.jsonl":jsonl(e.gold)};
 const m={schema:"srg16.stage.v1",role:"public diagnostic unless seed kept private and independently frozen",seed,reps,roots:e.roots.length,rows:e.tasks.length,source_sha256:sourceHash(),files:{}};
 for(const [f,s] of Object.entries(files)){
  fs.writeFileSync(path.join(dir,f),s,{flag:"wx",mode:0o600});m.files[f]={sha256:hash(s),bytes:Buffer.byteLength(s)};
 }
 fs.writeFileSync(path.join(dir,"verifier/manifest.json"),JSON.stringify(m,null,2)+"\n",{flag:"wx",mode:0o600});
 console.log(JSON.stringify({output:dir,roots:m.roots,rows:m.rows},null,2));
}
function grade(dir,submission){
 const m=JSON.parse(fs.readFileSync(path.join(dir,"verifier/manifest.json"),"utf8"));
 if(m.schema!=="srg16.stage.v1"||m.source_sha256!==sourceHash())fail("source/schema drift");
 const e=build(m.seed,m.reps);
 if(e.tasks.length!==m.rows||e.roots.length!==m.roots)fail("manifest counts");
 const files={"model_input/planning.jsonl":jsonl(e.tasks),"verifier/planning_gold.jsonl":jsonl(e.gold)};
 for(const [f,s] of Object.entries(files)){
  const raw=fs.readFileSync(path.join(dir,f));if(hash(raw)!==m.files[f].sha256||hash(s)!==m.files[f].sha256||raw.length!==m.files[f].bytes)fail("corpus drift "+f);
 }
 const rows=fs.readFileSync(submission,"utf8").split(/\r?\n/).filter(x=>x.trim()).map(line=>{
  try{return JSON.parse(line);}catch{return null;}
 });
 console.log(JSON.stringify(score(e,rows),null,2));
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [cmd,a,b,c,...rest]=process.argv.slice(2);
 if(rest.length)fail("too many args");
 if(cmd==="stage"&&a)stage(a,b===undefined?DEFAULT_SEED:Number(b),c===undefined?DEFAULT_REPS:Number(c));
 else if(cmd==="score"&&a&&b&&c===undefined)grade(a,b);
 else fail("stage <new-dir> [uint32 seed] [reps] | score <staged-dir> <submissions.jsonl>");
}
