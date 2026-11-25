// SRG-08 local OpenAI-compatible llama.cpp model runner. No verifier files read.
// Supports Bonsai/Inky servers and an explicit fixed-width streamed memory arm.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const fail=m=>{throw Error("SRG08 runner: "+m);};
const hash=s=>crypto.createHash("sha256").update(s).digest("hex");
const clean=s=>JSON.parse(s.trim());
export function validateOutput(kind,content,task,limit){
 const obj=clean(content);
 if(!obj||typeof obj!=="object"||Array.isArray(obj))fail("expected object");
 if(kind==="memory"){
   if(Object.keys(obj).join(",")!=="memory"||!Number.isSafeInteger(obj.memory)||obj.memory<0||obj.memory>=limit)fail("memory outside fixed register");
   return obj;
 }
 if(kind==="author"){
   if(Object.keys(obj).join(",")!=="formula"||typeof obj.formula!=="string"||!obj.formula.trim()||obj.formula.length>16000||/[\r\n|;]/.test(obj.formula))fail("invalid formula");
   return {id:task.id,formula:obj.formula};
 }
 if(Object.keys(obj).join(",")!=="action"||typeof obj.action!=="string"||!task.observation.actions.some(a=>a.id===obj.action))fail("illegal action");
 return {id:task.id,action:obj.action};
}
export function promptFor(kind,task){
 const output=kind==="author"?'{"formula":"GE(...)"}':'{"action":"one legal action ID"}';
 const instruction=kind==="author"?"Synthesize the specified SWMD boolean expression. Use only declared coordinates. Read the exact equality rule and example inputs.":"Choose the optimal legal action given only the supplied observation, task rules, budget and any supplied history.";
 return [{role:"system",content:instruction+" Return exactly one JSON object of form "+output+". No markdown or additional fields."},{role:"user",content:JSON.stringify(task)}];
}
export async function runTask(kind,task,request,memoryBits=0){
 let events=[];
 async function call(messages,tag){
   const result=await request(messages);
   if(typeof result?.content!=="string")fail("missing model response");
   events.push({stage:tag,content:result.content,usage:result.usage??null,elapsed_ms:result.elapsed_ms??null});
   return result.content;
 }
 try{
   if(kind!=="stream"){
     const content=await call(promptFor(kind,task),"decision");
     return {submission:validateOutput(kind,content,task),events,status:"submitted"};
   }
   if(task.mode!=="history"||!Array.isArray(task.history)||!Number.isInteger(memoryBits)||memoryBits<0||memoryBits>16)fail("invalid streaming task or budget");
   const limit=2**memoryBits,history=task.history.slice(1);let memory=0;
   // Only the explicit integer register persists between fresh stateless
   // requests. Never send the transcript, task ID, future query, or prior raw
   // outputs to the update model. System/user prompts are rebuilt each step.
   if(memoryBits>0)for(let i=0;i<history.length;i++){
     const cue=history[i].values["ledger.cue"];
     if(cue!==.5&&cue!==-.5)fail("invalid cue");
     const packet={rule:task.task,cue_number:i+1,total_cues:history.length,cue,memory,memory_bits:memoryBits,memory_min:0,memory_max:limit-1};
     const messages=[{role:"system",content:'Update the fixed-width memory register so you can answer the final report. The future query is unavailable. Return exactly {"memory": integer} within the specified range. No other fields.'},{role:"user",content:JSON.stringify(packet)}];
     memory=validateOutput("memory",await call(messages,"cue"+(i+1)),task,limit).memory;
   }
   const packet={rule:task.task,memory,memory_bits:memoryBits,total_cues:history.length,observation:task.observation};
   const messages=[{role:"system",content:'Use only the retained register and final public observation. Return exactly {"action":"one legal action ID"}. No additional fields.'},{role:"user",content:JSON.stringify(packet)}];
   return {submission:validateOutput("player",await call(messages,"final"),task),events,status:"submitted",memory_bits:memoryBits,final_memory:memory};
 }catch(e){return {submission:null,events,status:"rejected_or_error",error:String(e).slice(0,1000),...(kind==="stream"?{memory_bits:memoryBits}:{})};}
}
function options(argv){
 const args={};for(let i=0;i<argv.length;i+=2){const k=argv[i];if(!k.startsWith("--")||i+1>=argv.length||Object.hasOwn(args,k))fail("arguments must be unique --key value pairs");args[k]=argv[i+1];}
 for(const k of Object.keys(args))if(!["--suite","--kind","--endpoint","--model","--out","--memory-bits","--max-tasks","--max-tokens","--timeout-ms","--run-label","--checkpoint-sha256","--runtime-label","--pass-count"].includes(k))fail("unknown option "+k);
 for(const k of ["--suite","--kind","--model","--out","--run-label","--checkpoint-sha256","--runtime-label"])if(!args[k])fail("missing "+k);
 if(!/^[0-9a-f]{64}$/i.test(args["--checkpoint-sha256"]))fail("checkpoint SHA-256 required");
 if(!["author","player","planning","stream"].includes(args["--kind"]))fail("invalid kind");
 const u=new URL(args["--endpoint"]??"http://127.0.0.1:8080/v1/chat/completions");
 if(!["http:","https:"].includes(u.protocol)||!["localhost","127.0.0.1","[::1]"].includes(u.hostname)||u.username||u.password||u.search||u.hash||!u.pathname.endsWith("/chat/completions"))fail("local loopback chat completions endpoint required");
 const int=(k,d,lo,hi)=>{const v=args[k]===undefined?d:Number(args[k]);if(!Number.isSafeInteger(v)||v<lo||v>hi)fail("invalid "+k);return v;};
 return {suite:args["--suite"],kind:args["--kind"],model:args["--model"],endpoint:u.href,out:args["--out"],label:args["--run-label"],checkpoint_sha256:args["--checkpoint-sha256"],runtime_label:args["--runtime-label"],pass_count:args["--pass-count"]===undefined?null:int("--pass-count",1,1,128),memoryBits:int("--memory-bits",0,0,16),maxTasks:int("--max-tasks",100000,1,100000),maxTokens:int("--max-tokens",1024,16,8192),timeout:int("--timeout-ms",180000,1000,1800000)};
}
async function main(){
 const cfg=options(process.argv.slice(2));
 // No manifest, gold or verifier directory access here.
 const input=path.join(cfg.suite,"model_input",cfg.kind==="stream"?"player.jsonl":cfg.kind+".jsonl"),raw=fs.readFileSync(input,"utf8");
 let tasks=raw.split(/\r?\n/).filter(Boolean).map(s=>JSON.parse(s));
 if(cfg.kind==="stream")tasks=tasks.filter(t=>t.mode==="history");
 tasks=tasks.slice(0,cfg.maxTasks);
 fs.mkdirSync(cfg.out,{mode:0o700});
 const tracePath=path.join(cfg.out,"attempts.jsonl"),subPath=path.join(cfg.out,"submissions.jsonl");
 fs.writeFileSync(tracePath,"",{flag:"wx",mode:0o600});fs.writeFileSync(subPath,"",{flag:"wx",mode:0o600});
 const manifest={schema:"srg08.model_run.v1",evidence:"model inference requested against explicitly configured local endpoint",kind:cfg.kind,run_label:cfg.label,model:cfg.model,checkpoint_sha256:cfg.checkpoint_sha256,runtime_label:cfg.runtime_label,declared_pass_count:cfg.pass_count,endpoint:cfg.endpoint,input_sha256:hash(raw),input_path:path.basename(input),ordered_task_ids:tasks.map(t=>t.id),memory_bits:cfg.kind==="stream"?cfg.memoryBits:null,max_tokens:cfg.maxTokens,temperature:0,timeout_ms:cfg.timeout,started_at:new Date().toISOString(),task_limit:cfg.maxTasks};
 fs.writeFileSync(path.join(cfg.out,"run_manifest.json"),JSON.stringify(manifest,null,2)+"\n",{flag:"wx",mode:0o600});
 const request=async messages=>{
   const start=Date.now(),res=await fetch(cfg.endpoint,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:cfg.model,messages,temperature:0,max_tokens:cfg.maxTokens,stream:false}),redirect:"error",signal:AbortSignal.timeout(cfg.timeout)});
   if(!res.ok)fail("server HTTP "+res.status);
   const body=await res.json();
   return {content:body.choices?.[0]?.message?.content,usage:body.usage??null,elapsed_ms:Date.now()-start};
 };
 let submitted=0;
 for(const t of tasks){
   const out=await runTask(cfg.kind,t,request,cfg.memoryBits);
   fs.appendFileSync(tracePath,JSON.stringify({id:t.id,...out})+"\n");
   if(out.submission){fs.appendFileSync(subPath,JSON.stringify(out.submission)+"\n");submitted++;}
 }
 fs.writeFileSync(path.join(cfg.out,"summary.json"),JSON.stringify({attempted:tasks.length,submitted,rejected_or_error:tasks.length-submitted,finished_at:new Date().toISOString()},null,2)+"\n",{flag:"wx",mode:0o600});
 console.log(JSON.stringify({attempted:tasks.length,submitted,output:cfg.out},null,2));
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await main();
