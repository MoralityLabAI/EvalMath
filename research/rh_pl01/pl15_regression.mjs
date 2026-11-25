// RH-PL-15: preserve the published PL-13/14 proof receipts while exposing
// shared derivation contexts. Each group runs in a separate Node process.
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const groups=['append','base','gluing','recursion','family'];
const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
const canonical=x=>Array.isArray(x)?x.map(canonical):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;
const same=(x,y)=>JSON.stringify(canonical(x))===JSON.stringify(canonical(y));
const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
const targetBlob=createHash('sha1').update('blob '+Buffer.byteLength(raw)+'\0').update(raw).digest('hex');

async function runGroup(group){
 let actual,filename;
 if(group==='append'){
   const {append}=await import('./append.mjs');
   actual=append.prepare(raw).run().map(x=>x.receipt);filename='append_receipt.json';
 }else if(group==='base'){
   const {prefixBase}=await import('./prefix_base.mjs');
   actual=[prefixBase.prepare(raw).receipt];filename='prefix_base_receipt.json';
 }else if(group==='gluing'){
   const {gluing}=await import('./gluing.mjs');
   actual=gluing.prepare(raw).run().rows;filename='gluing_receipt.json';
 }else if(group==='recursion'){
   const {recursionExistence}=await import('./recursion_existence.mjs');
   actual=[recursionExistence.prepare(raw).receipt];filename='recursion_existence_receipt.json';
 }else if(group==='family'){
   const {prefixFamily}=await import('./prefix_family.mjs');
   actual=[prefixFamily.prepare(raw).receipt];filename='prefix_family_receipt.json';
 }else throw Error('unknown regression group: '+group);
 const recorded=JSON.parse(readFileSync(new URL('./'+filename,import.meta.url),'utf8'));
 assert(recorded.target_git_blob===targetBlob,'frozen target changed: '+group);
 const previous=recorded.rows||[recorded];
 assert(previous.length===actual.length,'theorem count changed: '+group);
 const rows=actual.map(row=>{
   const expected=previous.find(x=>x.name===row.name);
   assert(expected,'theorem missing from prior receipt: '+row.name);
   const fields=Object.keys(row);
   for(const key of fields)assert(same(row[key],expected[key]),'receipt field changed: '+row.name+'.'+key);
   return {name:row.name,compared_fields:fields,receipt_fields_identical:true};
 });
 return {group,target_git_blob:targetBlob,rows};
}

async function helperControls(){
 const {ordinals}=await import('./ordinals.mjs');
 const c=ordinals.prepare(raw),{p,ar}=c,{hyp,M,O,E}=p.logic,{succ}=c.t;
 const om=hyp(c.omega(37)),mn=hyp(M(60,37)),ss=hyp(succ(60,61));
 const controls=[
   ['transitivity_wrong_omega',()=>c.transAt(hyp(c.omega(38)),60,mn)],
   ['transitivity_wrong_index',()=>c.transAt(om,61,mn)],
   ['irreflexivity_wrong_membership_atom',()=>c.noSelfAt(om,60,hyp(E(60,37)))],
   ['predecessor_wrong_segment',()=>c.down(om,60,mn,62,63,hyp(succ(62,63)),hyp(c.le(63,61)))],
   ['freshness_wrong_successor',()=>c.fresh(om,60,mn,62,ss)]
 ];
 const rejected=controls.map(([name,fn])=>{
   let message=null;try{fn()}catch(error){message=String(error.message)}
   assert(message!==null,'invalid helper input accepted: '+name);
   return {name,rejected:true,error:message};
 });
 // The positive helper checks its exact output and keeps each assumption
 // visible until the caller supplies a deduction-theorem discharge.
 const valid=c.fresh(om,60,mn,61,ss);
 assert(valid.f===ar.neg(O(E(61,60),M(61,60))),'freshness statement changed');
 assert(valid.deps.has(om.id)&&valid.deps.has(mn.id)&&valid.deps.has(ss.id),'freshness assumptions lost');
 return {group:'helper_invariants',rejected,positive_freshness_preserves_assumptions:true};
}

const selected=process.argv[2]||'all';
if(selected==='all'){
 const results=[];
 for(const group of [...groups,'invariants']){
   const child=spawnSync(process.execPath,[fileURLToPath(import.meta.url),group],{encoding:'utf8',maxBuffer:4*1024*1024});
   assert(child.status===0,'regression child failed: '+group+'\n'+child.stderr);
   results.push(JSON.parse(child.stdout));
 }
 console.log(JSON.stringify({schema_version:1,target_git_blob:targetBlob,groups:results,previous_receipt_groups:groups.length,all_passed:true},null,2));
}else console.log(JSON.stringify(selected==='invariants'?await helperControls():await runGroup(selected)));
