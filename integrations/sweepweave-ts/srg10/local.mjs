// SRG-10: fresh local generation and weighted planning scorer.
// Uses the SRG-08 local loopback planning runner. No model calls here.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {runSuite} from './curriculum.mjs';
const fail=m=>{throw Error("SRG10 local: "+m);};
const hash=x=>crypto.createHash("sha256").update(x).digest("hex");
const jsonl=a=>a.map(x=>JSON.stringify(x)).join("\n")+"\n";
const rows=p=>fs.readFileSync(p,"utf8").split(/\r?\n/).filter(Boolean).map(JSON.parse);
const write=(p,s)=>fs.writeFileSync(p,s,{flag:"wx",mode:0o600});
const root=()=>fs.realpathSync(fileURLToPath(new URL('../../../',import.meta.url)));
const sourceFiles=["./curriculum.mjs","./local.mjs","../srg05/swmd-runtime-v2.mjs","../srg04/swmd-runtime.mjs"];
function outsideRepo(p){
 const abs=path.join(fs.realpathSync(path.dirname(path.resolve(p))),path.basename(p)),r=path.relative(root(),abs);
 return r===".."||r.startsWith(".."+path.sep)||path.isAbsolute(r);
}
function totals(){return {rows:0,mass:0,correct:0,correct_mass:0,utility_numerator:0,optimal_numerator:0,regret_numerator:0,counts:{}};}
function add(a,r){a.rows++;a.mass+=r.mass;a.correct+=Number(r.status==="pass");a.correct_mass+=r.status==="pass"?r.mass:0;a.utility_numerator+=r.utility_numerator;a.optimal_numerator+=r.optimal_numerator;a.regret_numerator+=r.optimal_numerator-r.utility_numerator;a.counts[r.status]=(a.counts[r.status]??0)+1;}
export function scoreRows(s,rows){
 const labels=new Map(s.gold.map(x=>[x.id,x])),expected=new Set(s.tasks.map(t=>t.id)),entries=new Map(),dup=new Set(),groups={},total=totals(),results=[];
 if(labels.size!==s.tasks.length||expected.size!==s.tasks.length)fail("duplicate task IDs");
 for(const r of rows){if(!r||typeof r.id!=="string")fail("submission id");if(entries.has(r.id))dup.add(r.id);else entries.set(r.id,r);}
 for(const t of s.tasks){
   const g=labels.get(t.id),r=entries.get(t.id);if(!g)fail("missing gold");
   let status="missing",value=0;
   if(dup.has(t.id))status="duplicate";
   else if(r){
     if(Object.keys(r).sort().join(",")!=="action,id"||typeof r.action!=="string"||!t.observation.actions.some(a=>a.id===r.action)||!Object.hasOwn(g.scores,r.action))status="rejected";
     else{value=g.scores[r.action];status=g.actions.includes(r.action)?"pass":"fail";}
   }
   const optimal=Math.max(...Object.values(g.scores));
   const rec={id:t.id,status,mass:g.mass,utility_numerator:value,optimal_numerator:optimal};
   if(optimal<0||value>optimal)fail("invalid payoff accounting");
   add(total,rec);add(groups[[g.family,g.view,g.stage,"H"+g.h].join("/")]??=totals(),rec);results.push(rec);
 }
 return {kind:"adaptive_evidence",...total,expected_utility:total.utility_numerator/total.mass,optimal_utility:total.optimal_numerator/total.mass,expected_regret:total.regret_numerator/total.mass,groups,unknown_ids:[...entries.keys()].filter(k=>!expected.has(k)),results};
}
function generate(split,out,replicates){
 if(!out)fail("output path");
 let seed;
 if(split==="calibration_public")seed=0x53521001;
 else if(split==="evaluation_private"){
   if(!outsideRepo(out))fail("private output must be outside EvalMath checkout");
   do{seed=crypto.randomBytes(4).readUInt32LE(0);}while(!seed||[0x53521001,0x53521002].includes(seed));
 }else fail("split");
 const s=runSuite({split,seed,replicates,api});
 fs.mkdirSync(out,{mode:0o700});fs.mkdirSync(path.join(out,"model_input"),{mode:0o700});fs.mkdirSync(path.join(out,"verifier"),{mode:0o700});
 const manifest={schema:"srg10.local.v1",split,seed,replicates,source_sha256:{},files:{}};
 for(const f of sourceFiles)manifest.source_sha256[f]=hash(fs.readFileSync(new URL(f,import.meta.url)));
 for(const [p,a] of [["model_input/planning.jsonl",s.tasks],["verifier/planning_gold.jsonl",s.gold]]){
   const data=jsonl(a);write(path.join(out,p),data);manifest.files[p]={count:a.length,sha256:hash(data)};
 }
 write(path.join(out,"verifier/receipt.json"),JSON.stringify(s.receipt,null,2)+"\n");
 write(path.join(out,"verifier/manifest.json"),JSON.stringify(manifest,null,2)+"\n");
 console.log(JSON.stringify({split,replicates,tasks:s.tasks.length,output:path.resolve(out)},null,2));
}
function score(out,sub){
 const m=JSON.parse(fs.readFileSync(path.join(out,"verifier/manifest.json"),"utf8"));
 if(m.schema!=="srg10.local.v1")fail("manifest");
 for(const f of sourceFiles)if(hash(fs.readFileSync(new URL(f,import.meta.url)))!==m.source_sha256[f])fail("source drift "+f);
 for(const f of ["model_input/planning.jsonl","verifier/planning_gold.jsonl"])if(hash(fs.readFileSync(path.join(out,f)))!==m.files[f].sha256)fail("data drift "+f);
 const s=runSuite({split:m.split,seed:m.seed,replicates:m.replicates,api});
 if(hash(jsonl(s.tasks))!==m.files["model_input/planning.jsonl"].sha256||hash(jsonl(s.gold))!==m.files["verifier/planning_gold.jsonl"].sha256)fail("regenerated corpus drift");
 console.log(JSON.stringify(scoreRows(s,rows(sub)),null,2));
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [cmd,a,b,c]=process.argv.slice(2);
 if(cmd==="generate")generate(a,b,c===undefined?1:Number(c));
 else if(cmd==="score"){if(!a||!b)fail("score requires suite and submissions");score(a,b);}
 else fail("generate <calibration_public|evaluation_private> <fresh-dir> [replicates] | score <suite-dir> <submissions.jsonl>");
}
