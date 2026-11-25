// SRG-08 materializer and strict submission verifier; no model/network calls.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';
import {makeSuite,scoreFormula} from './curriculum.mjs';

const publicSeeds={train_public:0x53520801,calibration_public:0x53520802};
const smoke=0x53520803;
const fail=m=>{throw Error("SRG08 local: "+m);};
const jsonl=xs=>xs.map(x=>JSON.stringify(x)).join("\n")+"\n";
const digest=s=>crypto.createHash("sha256").update(s).digest("hex");
function readRows(p){return fs.readFileSync(p,"utf8").split(/\r?\n/).filter(Boolean).map(s=>JSON.parse(s));}
function index(rows){
 const entries=new Map(),dup=new Set();
 for(const row of rows){if(!row||typeof row.id!=="string")fail("invalid submission id");if(entries.has(row.id))dup.add(row.id);else entries.set(row.id,row);}
 return {entries,dup};
}
export function scoreRows(suite,kind,rows,api,evaluate){
 if(!["author","player","planning","stream"].includes(kind))fail("invalid kind");
 const {entries,dup}=index(rows),cases=new Map(suite.cases.map(c=>[c.id,c]));
 const tasks=kind==="stream"?suite.player.filter(x=>x.mode==="history"):suite[kind];
 const labels=new Map((kind==="stream"?suite.playerGold:suite[kind+"Gold"]).map(g=>[g.id,g]));
 const expected=new Set(tasks.map(x=>x.id)),counts={},groups={},results=[];
 let binary=0,binaryTotal=0,grid=0,gridTotal=0,runtime=0,runtimeTotal=0;
 for(const t of tasks){
   const r=entries.get(t.id),g=labels.get(t.id);if(!g)fail("missing verifier gold");
   let status="missing",detail={},ok=false;
   if(dup.has(t.id))status="duplicate";
   else if(r){
     try{
       if(kind==="author"){
         if(Object.keys(r).sort().join(",")!=="formula,id")fail("invalid formula record");
         detail=scoreFormula(api,evaluate,cases.get(t.id),r.formula,true);
         ok=detail.errors===0&&detail.grid===detail.grid_total&&detail.binary===detail.binary_total&&detail.runtime===detail.runtime_total;
       }else{
         if(Object.keys(r).sort().join(",")!=="action,id"||typeof r.action!=="string"||!t.observation.actions.some(a=>a.id===r.action))fail("illegal action");
         ok=g.actions?g.actions.includes(r.action):r.action===g.action;
       }
       status=ok?"pass":"fail";
     }catch{status="rejected";}
   }
   if(kind==="author"){
     const c=cases.get(t.id);binaryTotal+=c.truth.length;gridTotal+=c.probes.length;runtimeTotal+=c.probes.length;
     binary+=detail.binary??0;grid+=detail.grid??0;runtime+=detail.runtime??0;
   }
   counts[status]=(counts[status]??0)+1;
   const key=kind==="author"?g.family+"/K"+g.k:kind==="planning"?g.mode+"/H"+g.h+"/budget"+g.budget:g.family+"/K"+g.k+"/"+(kind==="stream"?"stream":g.mode);
   const group=groups[key]??={correct:0,total:0};group.correct+=Number(ok);group.total++;
   results.push({id:t.id,status,correct:ok,...detail});
 }
 return {kind,counts,correct:counts.pass??0,total:tasks.length,unknown_ids:[...entries.keys()].filter(id=>!expected.has(id)),groups,results,
   ...(kind==="author"?{binary,binary_total:binaryTotal,grid,grid_total:gridTotal,runtime,runtime_total:runtimeTotal}:{})};
}
function root(){return fs.realpathSync(fileURLToPath(new URL("../../../",import.meta.url)));}
function outside(p){const full=path.join(fs.realpathSync(path.dirname(path.resolve(p))),path.basename(path.resolve(p))),rel=path.relative(root(),full);return rel===".."||rel.startsWith(".."+path.sep)||path.isAbsolute(rel);}
function write(p,s){fs.writeFileSync(p,s,{flag:"wx",mode:0o600});}
function generate(split,out,replicates){
 if(!out)fail("output required");
 let seed=publicSeeds[split];
 if(split==="evaluation_private"){
   if(!outside(out))fail("private evaluation must be outside the repository");
   do{seed=crypto.randomBytes(4).readUInt32LE(0);}while(!seed||seed===smoke||Object.values(publicSeeds).includes(seed));
 }
 if(!seed)fail("unknown split");
 const s=makeSuite({split,seed,replicates,api,evaluate,verify:true});
 fs.mkdirSync(out,{mode:0o700});const input=path.join(out,"model_input"),gold=path.join(out,"verifier");
 fs.mkdirSync(input,{mode:0o700});fs.mkdirSync(gold,{mode:0o700});
 const manifest={schema:"srg08.local.v1",split,seed,replicates,inputs:{},gold:{},generator_sha256:digest(fs.readFileSync(new URL("./curriculum.mjs",import.meta.url))),runtime_sha256:digest(fs.readFileSync(new URL("../srg05/swmd-runtime-v2.mjs",import.meta.url))),expression_sha256:digest(fs.readFileSync(new URL("../srg04/swmd-runtime.mjs",import.meta.url)))};
 for(const k of ["author","player","planning"]){
   const a=jsonl(s[k]),b=jsonl(s[k+"Gold"]);write(path.join(input,k+".jsonl"),a);write(path.join(gold,k+"_gold.jsonl"),b);
   manifest.inputs[k]={count:s[k].length,sha256:digest(a)};manifest.gold[k]={count:s[k+"Gold"].length,sha256:digest(b)};
 }
 write(path.join(gold,"manifest.json"),JSON.stringify(manifest,null,2)+"\n");write(path.join(gold,"receipt.json"),JSON.stringify(s.receipt,null,2)+"\n");
 console.log(JSON.stringify({split,counts:Object.fromEntries(Object.entries(manifest.inputs).map(([k,v])=>[k,v.count])),stream:s.player.filter(t=>t.mode==="history").length,output:path.resolve(out)},null,2));
}
function verifyManifest(dir,m){
 if(m.schema!=="srg08.local.v1"||!m.inputs||!m.gold)fail("invalid manifest");
 for(const [key,url] of [["generator_sha256","./curriculum.mjs"],["runtime_sha256","../srg05/swmd-runtime-v2.mjs"],["expression_sha256","../srg04/swmd-runtime.mjs"]])if(m[key]!==digest(fs.readFileSync(new URL(url,import.meta.url))))fail("runtime drift "+key);
 for(const k of ["author","player","planning"]){
   const a=fs.readFileSync(path.join(dir,"model_input",k+".jsonl")),b=fs.readFileSync(path.join(dir,"verifier",k+"_gold.jsonl"));
   if(digest(a)!==m.inputs[k].sha256||digest(b)!==m.gold[k].sha256)fail("dataset hash mismatch "+k);
 }
}
const main=process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(main){
 const [cmd,a,b,c]=process.argv.slice(2);
 if(cmd==="generate")generate(a,b,c===undefined?1:Number(c));
 else if(cmd==="score"){
   if(!b||!c)fail("score needs kind, directory and submissions");
   const m=JSON.parse(fs.readFileSync(path.join(b,"verifier","manifest.json"),"utf8"));verifyManifest(b,m);
   const s=makeSuite({split:m.split,seed:m.seed,replicates:m.replicates,api,evaluate,verify:false});
   console.log(JSON.stringify(scoreRows(s,a,readRows(c),api,evaluate),null,2));
 }else fail("usage: generate <split> <new-dir> [replicates] | score <author|player|planning|stream> <suite-dir> <submissions.jsonl>");
}
