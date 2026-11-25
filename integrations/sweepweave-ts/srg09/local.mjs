// SRG-09 public diagnostic staging and weighted submission scorer.
// The finite evidence tape is public; this is NOT a sealed evaluation.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';
import {runSuite,KEYS} from './curriculum.mjs';
const fail=m=>{throw Error("SRG09 local: "+m);};
const own=(x,k)=>Object.hasOwn(x,k);
const seed=0x53520901;
const hash=x=>crypto.createHash("sha256").update(x).digest("hex");
const jsonl=a=>a.map(x=>JSON.stringify(x)).join("\n")+"\n";
const rows=p=>fs.readFileSync(p,"utf8").split(/\r?\n/).filter(Boolean).map(JSON.parse);
function index(a){const entries=new Map(),duplicates=new Set();for(const r of a){if(!r||typeof r.id!=="string")fail("invalid submission id");if(entries.has(r.id))duplicates.add(r.id);else entries.set(r.id,r);}return {entries,duplicates};}
function add(o,k,n=1){o[k]=(o[k]??0)+n;}
function accumulator(){return {rows:0,correct:0,mass:0,correct_mass:0,utility_numerator:0,optimal_numerator:0,regret_numerator:0,counts:{}};}
function accumulate(a,r){a.rows++;a.correct+=Number(r.status==="pass");a.mass+=r.mass;a.correct_mass+=r.status==="pass"?r.mass:0;a.utility_numerator+=r.utility_numerator;a.optimal_numerator+=r.optimal_numerator;a.regret_numerator+=r.optimal_numerator-r.utility_numerator;add(a.counts,r.status);}
export function scoreEvidence(suite,submissions){
 const {entries,duplicates}=index(submissions),labels=new Map(suite.gold.map(x=>[x.id,x])),expected=new Set(suite.tasks.map(x=>x.id)),total=accumulator(),groups={},results=[];
 if(labels.size!==expected.size||expected.size!==suite.tasks.length)fail("bad task IDs");
 for(const t of suite.tasks){
   const g=labels.get(t.id),r=entries.get(t.id);if(!g)fail("missing gold");
   let status="missing",value=0;
   if(duplicates.has(t.id))status="duplicate";
   else if(r){
     if(Object.keys(r).sort().join(",")!=="action,id"||typeof r.action!=="string"||!t.observation.actions.some(a=>a.id===r.action)||!own(g.scores,r.action))status="rejected";
     else{value=g.scores[r.action];status=g.actions.includes(r.action)?"pass":"fail";}
   }
   const rec={id:t.id,status,mass:g.mass,utility_numerator:value,optimal_numerator:Math.max(...Object.values(g.scores))};
   results.push(rec);accumulate(total,rec);
   const key=g.mode+"/"+g.meta_mode+"/H"+g.budget,group=groups[key]??=accumulator();accumulate(group,rec);
 }
 return {kind:"evidence",...total,expected_utility:total.utility_numerator/total.mass,optimal_utility:total.optimal_numerator/total.mass,groups,unknown_ids:[...entries.keys()].filter(x=>!expected.has(x)),results};
}
export function scoreRepairs(suite,submissions){
 const {entries,duplicates}=index(submissions),expected=new Set(suite.repairs.map(r=>r.id)),results=[],counts={};
 let passed=0,total=0,weighted=0,weighted_total=0,intervention_passed=0,intervention_total=0;
 for(const r of suite.repairs){
   const p=entries.get(r.id);let status="missing",n=0,m=0,inter=0,provenance=false;
   if(duplicates.has(r.id))status="duplicate";
   else if(p)try{
     if(Object.keys(p).sort().join(",")!=="after,before,id,line")fail("patch fields");
     const out=r.score({line:p.line,before:p.before,after:p.after});n=out.pass;m=out.weighted;inter=out.intervention_pass;provenance=out.provenance_exact;status=out.contract_pass?"pass":"fail";
   }catch{status="rejected";}
   const d=r.stats.gold.total;passed+=n;total+=d;weighted+=m;weighted_total+=16384;intervention_passed+=inter;intervention_total+=r.stats.gold.intervention_total;
   add(counts,status);results.push({id:r.id,status,passed:n,total:d,weighted:m,weighted_total:16384,intervention_passed:inter,intervention_total:r.stats.gold.intervention_total,provenance_exact:provenance});
 }
 return {kind:"author",counts,passed,total,weighted,weighted_total,intervention_passed,intervention_total,unknown_ids:[...entries.keys()].filter(id=>!expected.has(id)),results};
}
function make(){return runSuite({api,evaluate,seed});}
function put(p,data){fs.writeFileSync(p,data,{flag:"wx",mode:0o600});}
function stage(suite,out){
 fs.mkdirSync(out,{mode:0o700});const inp=path.join(out,"model_input"),ver=path.join(out,"verifier");fs.mkdirSync(inp,{mode:0o700});fs.mkdirSync(ver,{mode:0o700});
 const manifest={schema:"srg09.public.v1",evidence:"public diagnostic; no private evaluation",seed,source_sha256:{},files:{}};
 for(const rel of ["./curriculum.mjs","./local.mjs","../srg05/swmd-runtime-v2.mjs","../srg04/swmd-runtime.mjs"])manifest.source_sha256[rel]=hash(fs.readFileSync(new URL(rel,import.meta.url)));
 // planning.jsonl is compatible with the SRG08 local action runner.
 for(const [rel,a] of [["model_input/planning.jsonl",suite.tasks],["model_input/author.jsonl",suite.repairs.map(r=>r.task)],["verifier/planning_gold.jsonl",suite.gold],["verifier/author_gold.jsonl",suite.repairs.map(r=>({id:r.id,...r.patch}))]]){
   const data=jsonl(a);put(path.join(out,rel),data);manifest.files[rel]={count:a.length,sha256:hash(data)};
 }
 put(path.join(ver,"manifest.json"),JSON.stringify(manifest,null,2)+"\n");put(path.join(ver,"receipt.json"),JSON.stringify(suite.receipt,null,2)+"\n");return manifest;
}
function verifyStaged(dir){
 const m=JSON.parse(fs.readFileSync(path.join(dir,"verifier","manifest.json"),"utf8"));
 if(m.schema!=="srg09.public.v1"||m.seed!==seed)fail("manifest");
 for(const [rel,sha] of Object.entries(m.source_sha256))if(hash(fs.readFileSync(new URL(rel,import.meta.url)))!==sha)fail("source drift");
 for(const [rel,x] of Object.entries(m.files))if(hash(fs.readFileSync(path.join(dir,rel)))!==x.sha256)fail("data drift");
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [cmd,a,b,c]=process.argv.slice(2);
 if(cmd==="stage"){if(!a)fail("missing new output path");console.log(JSON.stringify(stage(make(),a),null,2));}
 else if(cmd==="score"){
   if(!["evidence","author"].includes(a)||!b||!c)fail("score <evidence|author> <suite-dir> <submissions.jsonl>");
   verifyStaged(b);const suite=make(),sub=rows(c);console.log(JSON.stringify(a==="evidence"?scoreEvidence(suite,sub):scoreRepairs(suite,sub),null,2));
 }else fail("stage <new-output-dir> | score <evidence|author> <suite-dir> <submissions.jsonl>");
}
