import fs from 'node:fs';
import path from 'node:path';
import * as api from './swmd-runtime-v2.mjs';
function buildGym(api){
 const {compileV2,initialV2,observeV2,stepV2,applyLinePatch}=api;
 const families=["reaction_sign","belief_keyring","comparator","dependent_write_order","weak_effect","late_windfall","spool_activation","event_prerequisite","cue_visibility","direct_admission"];
 const q=JSON.stringify;
 const C=x=>"C("+x+")",P=x=>"P("+x+")";
 const varline=(k,x,v="public")=>`VAR ${k} = ${x} | ${v}`;
 const spool=(id,active,members)=>`SPOOL ${id} | A:${active?"TRUE":"FALSE"} | E:${members.join(",")}`;
 const enc=(id,lo,hi,index,gate="TRUE",priority="C(0)",n=id,t=id)=>`ENC ${id} turn=${lo}..${hi} | I:${index} | A:${gate} | Q:${priority} | N:${q(n)} | T:${q(t)}`;
 const opt=(id,t="Continue",v="TRUE",p="TRUE")=>`OPT ${id} | V:${v} | P:${p} | T:${q(t)}`;
 const rx=(o,id,to,e="NONE",d="C(0)",g="TRUE",t="The record is updated.")=>`ORX ${o}/${id} -> ${to} | E:${e} | D:${d} | G:${g} | T:${q(t)}`;
 const set=(key,v)=>`SET ${key} = ${v}`;
 const header=(id,vars)=>["# SWMD-SRG/2",`id: ${id}`,`title: "Civic ledger ${id}"`,`about: "Synthetic causal authoring exercise."`,"start: opening","turn-base: 0","tie: first","direct: strict",...vars];
 const fmt=x=>Number(x.toFixed(6));
 function fixture(f,i){
   const m=fmt(.08+i*.01), id="sw_"+f.replaceAll("_","")+"_"+i;
   let rows=[],bad="",good="",field="",probes=[],intent="",scoreMode="trajectory";
   function mark(line,clean,fld){if(bad)throw Error("two repair sites");bad=line;good=clean;field=fld;rows.push(line);}
   const basic=[varline("a.x",0),varline("a.cue",0),varline("a.cue[b]",0,"hidden"),varline("a.cue[b][c]",0,"hidden")];
   const endings=[enc("yes",1,1,1,"TRUE","C(1)","Accepted","The expected branch is taken."),enc("no",1,1,2,"TRUE","C(0)","Rejected","The other branch is taken.")];
   if(f==="reaction_sign"||f==="belief_keyring"){
     rows=[...header(id,basic),spool("main",true,["opening","yes","no"]),enc("opening",0,0,0),opt("act","Ask for a commitment.")];
     const right=f==="reaction_sign"?P("a.cue"):P("a.cue[b][c]");
     const wrong=f==="reaction_sign"?`MUL(${right},C(-1))`:P("a.cue[b]");
     mark(rx("act","r_yes","yes","NONE",wrong),rx("act","r_yes","yes","NONE",right),"D");
     rows.push(rx("act","r_no","no"),...endings);
     for(const sign of [-1,1])probes.push({initial:{"a.cue":sign*m,"a.cue[b]":-sign*m,"a.cue[b][c]":sign*m},actions:["act"],end:sign>0?"yes":"no"});
     intent=f==="reaction_sign"?"A positive cue must favor acceptance, and a negative cue must favor rejection.":"The second-order cue a.cue[b][c] determines acceptance. The first-order cue a.cue[b] is an independent distractor.";
   }else if(f==="comparator"){
     rows=[...header(id,basic),spool("main",true,["opening","yes","no"]),enc("opening",0,0,0),opt("act"),rx("act","r_act","wild")];
     mark(enc("yes",1,1,1,"LE(P(a.cue),C(0))","C(1)"),enc("yes",1,1,1,"GE(P(a.cue),C(0))","C(1)"),"A");
     rows.push(enc("no",1,1,2));
     for(const sign of [-1,0,1])probes.push({initial:{"a.cue":sign*m},actions:["act"],end:sign>=0?"yes":"no"});
     intent="The preferred ending is admitted exactly when the cue is nonnegative, including equality. Otherwise use the fallback.";
   }else if(f==="dependent_write_order"){
     rows=[...header(id,basic),spool("main",true,["opening","yes"]),enc("opening",0,0,0),opt("act","Update the ledger.")];
     const a=set("a.x",`ADD(P(a.x),${C(m)})`),b=set("a.cue",P("a.x"));
     mark(rx("act","r_act","yes",b+"; "+a),rx("act","r_act","yes",a+"; "+b),"E");rows.push(endings[0]);
     for(const x of [-m,0,m])probes.push({initial:{"a.x":x},actions:["act"],end:"yes",values:{"a.x":fmt(x+m),"a.cue":fmt(x+m)}});
     intent="Update a.x by the declared amount, then copy the updated value to a.cue. Both registers must agree.";
   }else if(f==="weak_effect"||f==="late_windfall"){
     const ids=["opening","stage1","stage2","stage3","yes"];
     rows=[...header(id,basic),spool("main",true,ids)];
     for(let j=0;j<4;j++){
       rows.push(enc(ids[j],j,j,j),opt("act"+j,"Perform the scheduled contribution."));
       const make=amount=>rx("act"+j,"r"+j,ids[j+1],set("a.x",`ADD(P(a.x),${C(amount)})`));
       if(j===3)mark(make(f==="weak_effect"?fmt(m/4):fmt(4*m)),make(m),"E");else rows.push(make(m));
     }
     rows.push(enc("yes",4,4,4,`GE(P(a.x),${C(fmt(3.5*m))})`));
     probes.push({initial:{},actions:["act0","act1","act2","act3"],end:"yes",max_energy_share:.5,values:{"a.x":fmt(4*m)}});
     intent="Four scheduled contributions have equal size "+m+". Meet the terminal threshold and keep the largest squared step-energy share at most 1/2. Preserve the preceding three contributions.";
   }else if(f==="spool_activation"){
     rows=[...header(id,basic),spool("main",true,["opening","no"]),spool("later",false,["yes"]),enc("opening",0,0,0),opt("act","Ratify the schedule.")];
     mark(rx("act","r_act","wild","SPOOL later = FALSE"),rx("act","r_act","wild","SPOOL later = TRUE"),"E");
     rows.push(...endings);probes.push({initial:{},actions:["act"],end:"yes"});
     intent="Ratification activates the later spool; its higher-priority ending should be selected by wild routing.";
   }else if(f==="event_prerequisite"){
     rows=[...header(id,basic),spool("main",true,["opening","yes","no"]),enc("opening",0,0,0),opt("verify","Verify the ledger."),rx("verify","r_verify","wild"),opt("skip","Skip verification."),rx("skip","r_skip","wild")];
     mark(enc("yes",1,1,1,"SEEN(r_skip)","C(1)"),enc("yes",1,1,1,"SEEN(r_verify)","C(1)"),"A");
     rows.push(endings[1]);probes.push({initial:{},actions:["verify"],end:"yes"},{initial:{},actions:["skip"],end:"no"});
     intent="The preferred route requires an actual verification reaction in the event history. Skipping must lead to the fallback.";
   }else if(f==="cue_visibility"){
     rows=header(id,[varline("a.x",0)]);
     mark(varline("a.cue",0,"hidden"),varline("a.cue",0,"public"),"visibility");
     rows.push(spool("main",true,["opening","yes","no"]),enc("opening",0,0,0),opt("positive","Choose the positive report."),
       rx("positive","rp_yes","yes","NONE","C(1)","GE(P(a.cue),C(0))"),rx("positive","rp_no","no","NONE","C(1)","LT(P(a.cue),C(0))"),
       opt("negative","Choose the negative report."),
       rx("negative","rn_yes","yes","NONE","C(1)","LT(P(a.cue),C(0))"),rx("negative","rn_no","no","NONE","C(1)","GE(P(a.cue),C(0))"),...endings);
     probes=[{initial:{"a.cue":m},end:"yes"},{initial:{"a.cue":-m},end:"yes"}];scoreMode="observation_oracle";
     intent="The player must be able to distinguish the two equally likely reports before the irreversible choice. Reveal only the cue; preserve all rewards and transition formulas.";
   }else if(f==="direct_admission"){
     rows=[...header(id,basic),spool("main",true,["opening","yes"]),enc("opening",0,0,0),opt("act","Complete the prepared step."),rx("act","r_act","yes",set("a.x",C(m)))];
     mark(enc("yes",2,2,1,`GE(P(a.x),${C(m)})`),enc("yes",1,1,1,`GE(P(a.x),${C(m)})`),"window");
     probes.push({initial:{},actions:["act"],end:"yes",values:{"a.x":m}});intent="The prepared action reaches its successor at turn 1. The destination's admission window must allow that turn while preserving the numeric gate.";
   }else throw Error("unknown family");
   const index=rows.indexOf(bad),source=rows.join("\n")+"\n",patch={line:index+1,before:bad,after:good};
   let prefix,suffix;
   if(field==="visibility"){prefix=bad.slice(0,bad.lastIndexOf(" | ")+3);suffix="";}
   else if(field==="window"){prefix=bad.slice(0,bad.indexOf("turn=")+5);suffix=bad.slice(bad.indexOf(" | I:"));}
   else{const a=bad.indexOf(" | "+field+":")+4+field.length;const b=bad.indexOf(" | ",a);prefix=bad.slice(0,a);suffix=bad.slice(b);}
   if(!bad.startsWith(prefix)||!good.startsWith(prefix)||!bad.endsWith(suffix)||!good.endsWith(suffix))throw Error("bad patch scope "+f);
   const scope={line:index+1,field,prefix,suffix};
   const body=bad.slice(prefix.length,bad.length-suffix.length);
   let shamBody=body;
   if(field==="D")shamBody=`ADD(${body},C(0))`;
   else if(field==="A")shamBody=`AND(${body},TRUE)`;
   else if(field==="E")shamBody=body+"; SET a.x = P(a.x)";
   else if(field==="window")shamBody="02..02";
   else if(field==="visibility")shamBody=body+" ";
   const sham={line:index+1,before:bad,after:prefix+shamBody+suffix};
   return {id,family:f,template_index:i,source,intent,scope,probes,scoreMode,patch,sham};
 }
 function stateAt(w,p){const s=initialV2(w);for(const [k,v] of Object.entries(p.initial)){if(!Object.hasOwn(s.values,k))throw Error("bad declared probe");s.values[k]=v;}return s;}
 function score(source,task){
   const w=compileV2(source);
   if(task.scoreMode==="observation_oracle"){
     const cells=new Map();
     for(const p of task.probes){const s=stateAt(w,p),obs=observeV2(w,s),key=JSON.stringify(obs);
       if(!cells.has(key))cells.set(key,{actions:obs.actions.map(a=>a.id),rows:[]});
       cells.get(key).rows.push(Object.fromEntries(obs.actions.map(a=>{let n=0;try{n=Number(stepV2(w,s,a.id).next.encounter===p.end);}catch{}return [a.id,n];})));
     }
     let numerator=0;for(const c of cells.values())numerator+=Math.max(...c.actions.map(a=>c.rows.reduce((n,r)=>n+r[a],0)),0);
     return {passed:numerator,total:task.probes.length,cells:cells.size};
   }
   let passed=0,diagnostics=[];
   for(const p of task.probes){
     let s=stateAt(w,p),energies=[];
     try{
       for(const a of p.actions){const b=stepV2(w,s,a);energies.push(b.squared_step_energy);s=b.next;}
       const total=energies.reduce((a,b)=>a+b,0),share=total?Math.max(...energies)/total:0;
       const ok=s.encounter===p.end&&(!p.values||Object.entries(p.values).every(([k,v])=>Math.abs(s.values[k]-v)<1e-10))&&(p.max_energy_share===undefined||share<=p.max_energy_share+1e-12);
       passed+=Number(ok);diagnostics.push({end:s.encounter,energy_share:share,passed:ok});
     }catch(e){diagnostics.push({error:String(e),passed:false});}
   }
   return {passed,total:task.probes.length,diagnostics};
 }
 function verifyPatch(task,patch){
   const {scope}=task;
   if(patch.line!==scope.line||!patch.after.startsWith(scope.prefix)||!patch.after.endsWith(scope.suffix))throw Error("patch outside allowed scope");
   const body=patch.after.slice(scope.prefix.length,patch.after.length-scope.suffix.length);
   if(body.includes(" | ")||/[\r\n]/.test(body))throw Error("patch breaks record scope");
   return score(applyLinePatch(task.source,patch),task);
 }
 const results=[],publicRows=[],goldRows=[];
 for(const f of families)for(let i=0;i<8;i++){
   const task=fixture(f,i),bad=score(task.source,task),repair=verifyPatch(task,task.patch),sham=verifyPatch(task,task.sham);
   if(repair.passed!==repair.total||bad.passed>=bad.total||sham.passed!==bad.passed)throw Error("fixture separation failed "+task.id+" "+JSON.stringify({bad,repair,sham}));
   let invalidRejected=false;try{verifyPatch(task,{...task.patch,line:task.patch.line+1});}catch{invalidRejected=true;}if(!invalidRejected)throw Error("out-of-scope patch accepted");
   // Public pedagogical task, not a sealed holdout. Family names remain in IDs
   // for debugging, so these are unsuitable as blind diagnostic evals.
   publicRows.push({id:task.id,split:i<6?"train_public":"calibration_public",source:task.source,intent:task.intent,allowed_edit:task.scope,
     author_visible_probes:task.probes,score_mode:task.scoreMode,output_contract:"one {line,before,after} patch; keep all other source bytes unchanged"});
   goldRows.push({id:task.id,family:f,repair:task.patch,sham:task.sham,defective:bad,repaired:repair,sham_result:sham});
   results.push({id:task.id,family:f,defective:bad.passed,repaired:repair.passed,sham:sham.passed,total:repair.total});
 }
 const by_family={};for(const r of results){const row=by_family[r.family]??={tasks:0,defective:0,repaired:0,sham:0,total:0};row.tasks++;for(const k of ["defective","repaired","sham","total"])row[k]+=r[k];}
 return {publicRows,goldRows,receipt:{evidence:"public deterministic synthetic repair controls, no model inference",tasks:results.length,families:families.length,by_family,
   all_gold_repairs_pass:results.every(r=>r.repaired===r.total),all_defects_fail_some_probe:results.every(r=>r.defective<r.total),all_shams_preserve_defect:results.every(r=>r.sham===r.defective),
   probes_total:results.reduce((n,r)=>n+r.total,0),defective_passes:results.reduce((n,r)=>n+r.defective,0),repaired_passes:results.reduce((n,r)=>n+r.repaired,0),sham_passes:results.reduce((n,r)=>n+r.sham,0)}};
}
const out=process.argv[2];if(!out)throw Error('Usage: node build-authoring-gym.mjs <output-directory>');
const r=buildGym(api);fs.mkdirSync(out,{recursive:true});
for(const [name,rows] of [['author_tasks.jsonl',r.publicRows],['author_gold.jsonl',r.goldRows]])fs.writeFileSync(path.join(out,name),rows.map(x=>JSON.stringify(x)).join('\n')+'\n');
fs.writeFileSync(path.join(out,'repair_receipt.json'),JSON.stringify(r.receipt,null,2)+'\n');
