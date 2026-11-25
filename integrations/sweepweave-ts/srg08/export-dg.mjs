// SRG-08: split-safe Data Goblin supervised-data export.
// Only public training seed and full-information / identifiable decisions.
// Do not add current-only memory items: identical observations can have
// incompatible labels. Calibration and reserved evaluation are excluded.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';
import {makeSuite} from './curriculum.mjs';
import {promptFor} from './run-local.mjs';
const sha=x=>crypto.createHash("sha256").update(x).digest("hex");
const fail=m=>{throw Error("SRG08 DG: "+m);};
export function exportTrain(suite,promptFor){
 if(suite.split!=="train_public"||suite.seed!==0x53520801)fail("only registered public training split permitted");
 const rows=[];
 for(const [kind,tasks,labels] of [["author",suite.author,suite.authorGold],["player",suite.player.filter(t=>t.mode==="history"),suite.playerGold],["planning",suite.planning,suite.planningGold]]){
   const gold=new Map(labels.map(t=>[t.id,t]));
   for(const t of tasks){
     const g=gold.get(t.id);if(!g)fail("missing label");
     if(kind==="planning"&&g.actions.length!==1)fail("ambiguous training label");
     const answer=kind==="author"?{formula:g.formula}:{action:kind==="planning"?g.actions[0]:g.action};
     rows.push({id:"srg08/"+t.id,split:"train",task_family:"swmd_"+kind,source_world:t.world_id??t.id,
       evidence_class:"deterministic_reference_control",architecture_promotion_eligible:false,training_eligible:true,
       messages:[...promptFor(kind,t),{role:"assistant",content:JSON.stringify(answer)}]});
   }
 }
 if(new Set(rows.map(r=>r.id)).size!==rows.length)fail("duplicate rows");
 return rows;
}
function main(){
 const out=process.argv[2];if(!out)fail("usage: node export-dg.mjs <fresh-output-dir> [replicates]");
 const replicates=process.argv[3]===undefined?1:Number(process.argv[3]);
 const s=makeSuite({split:"train_public",seed:0x53520801,replicates,api,evaluate,verify:true});
 const rows=exportTrain(s,promptFor),data=rows.map(x=>JSON.stringify(x)).join("\n")+"\n";
 const counts={};for(const r of rows)counts[r.task_family]=(counts[r.task_family]??0)+1;
 fs.mkdirSync(out,{mode:0o700});fs.writeFileSync(path.join(out,"srg08_train.jsonl"),data,{flag:"wx",mode:0o600});
 const files={};
 for(const rel of ["./curriculum.mjs","./run-local.mjs","./export-dg.mjs","../srg05/swmd-runtime-v2.mjs","../srg04/swmd-runtime.mjs"])files[rel]=sha(fs.readFileSync(new URL(rel,import.meta.url)));
 const manifest={schema:"srg08.ingestion.v1",dataset_id:"evalmath-swmd-srg08-public-train",source_repository:"MoralityLabAI/EvalMath",split:"train_public",seed:0x53520801,replicates,format:"messages-jsonl",artifact:{path:"srg08_train.jsonl",sha256:sha(data),count:rows.length,counts},source_sha256:files,
 evidence_class:"deterministic_reference_control",architecture_promotion_eligible:false,model_inference_executed:false,policy:"Exclude calibration, reserved evaluation, current-only memory, all smoke and any unverified model attempts. Keep world siblings together; never random-split rows into a test set."};
 fs.writeFileSync(path.join(out,"manifest.json"),JSON.stringify(manifest,null,2)+"\n",{flag:"wx",mode:0o600});console.log(JSON.stringify(manifest,null,2));
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))main();
