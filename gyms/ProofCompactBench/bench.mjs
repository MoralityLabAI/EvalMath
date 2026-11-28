import fs from "node:fs";
import path from "node:path";
import {createHash} from "node:crypto";
import {library} from "./core.mjs";
const L=library(),[cmd,...args]=process.argv.slice(2);
const write=(file,rs)=>fs.writeFileSync(file,rs.map(x=>JSON.stringify(x)).join("\n")+"\n",{flag:"wx"});
const read=f=>fs.readFileSync(f,"utf8").split(/\r?\n/).filter(Boolean).map(JSON.parse);
const digest=f=>createHash("sha256").update(fs.readFileSync(f)).digest("hex");
if(cmd==="self-test"){console.log(JSON.stringify(L.selfTest(),null,2));}
else if(cmd==="build-public"||cmd==="build-private"){
  const [dir,seedText,countText]=args;
  if(!dir)throw Error("output directory required");
  let seed=0x50434231,count=96;
  if(cmd==="build-private"){
    if(!seedText||!countText||!/^\d+$/.test(seedText)||!/^\d+$/.test(countText))throw Error("private mode requires operator-provided seed and count");
    seed=Number(seedText);count=Number(countText);
    if(!Number.isSafeInteger(seed)||seed<1||seed>0xffffffff||[0x50434231,0x91bf73a5].includes(seed)||count<1||count>512)throw Error("private seed/count bounds");
  }
  fs.mkdirSync(dir,{recursive:false});
  const rows=[];
  for(let i=0;i<count;i++){
    const split=cmd==="build-private"?"private":i<64?"train":i<80?"calibration":"dev_test";
    // Private roots carry distinct identifiers; a fresh seed is not a guarantee of semantic novelty.
    const root=cmd==="build-private"?i+100000:i;
    rows.push(...L.generate(root,seed,split,split==="private"||split==="dev_test"));
  }
  const files=[];
  for(const split of [...new Set(rows.map(r=>r.split))]){
    const rs=rows.filter(r=>r.split===split);
    const packet=path.join(dir,split+".public.jsonl"),gold=path.join(dir,split+".gold.jsonl");
    write(packet,rs.map(L.packet));write(gold,rs);
    for(const file of [packet,gold])files.push({file:path.basename(file),sha256:digest(file),rows:rs.length});
  }
  const receipt={schema:"proofcompactbench-build-v1",mode:cmd,files,seed_commitment:createHash("sha256").update(String(seed)).digest("hex"),training_ready:false,admitted_tokens:0};
  fs.writeFileSync(path.join(dir,"manifest.json"),JSON.stringify(receipt,null,2)+"\n",{flag:"wx"});console.log(JSON.stringify(receipt,null,2));
}else if(cmd==="grade"){
  const [gold,pred,out]=args;if(!gold||!pred||!out)throw Error("grade GOLD.jsonl PRED.jsonl OUT.json");
  const result=L.gradeAll(read(gold),read(pred));
  fs.writeFileSync(out,JSON.stringify({schema:"proofcompactbench-score-v1",gold_sha256:digest(gold),predictions_sha256:digest(pred),...result},null,2)+"\n",{flag:"wx"});console.log(JSON.stringify({total:result.total,valid:result.valid,optimal:result.optimal,missing:result.missing,mean_score:result.mean_score},null,2));
}else if(cmd==="export-train"){
  const [gold,out]=args;const rows=read(gold);
  if(!rows.length||rows.some(r=>r.split!=="train"||!r.training_eligible||!L.grade(r,r.answer).optimal))throw Error("only verified train roots can be exported");
  write(out,rows.map(r=>({schema:"datagoblin.proofcompactbench.v1",id:r.id,root:r.root,split:r.split,family:r.family,prompt:L.packet(r),response:r.answer,claim_type:r.claim_type,verification:"exact synthetic oracle",admission_status:"pending_collator_tokenizer",training_ready:false})));
}else throw Error("self-test | build-public DIR | build-private DIR SEED COUNT | grade GOLD PRED OUT | export-train GOLD OUT");
