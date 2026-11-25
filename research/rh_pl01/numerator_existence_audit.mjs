// RH-PL-18: independently replay the numerator and joint graph constructions,
// checking complete closed statements against the frozen target and prior
// normalized interfaces. No producer predicate builder defines an audit target.
import {kernel} from './kernel.mjs';
import {certificate,verifyCertificate} from './joint_audit.mjs';
import {auditMutations} from './ordinal_audit.mjs';
import {simultaneousSubstitution} from './denominator_audit.mjs';
import {recursionExistence} from './recursion_existence.mjs';
import {transport} from './transport.mjs';
import {denominator} from './denominator.mjs';
import {numerator} from './numerator.mjs';
import {jointRecurrenceExistence} from './joint_recurrence_existence.mjs';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {dirname,relative,resolve} from 'node:path';

const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../..');
const assert=(ok,message)=>{if(!ok)throw Error(message)};
const hash=(kind,data)=>createHash(kind).update(data).digest('hex'),sha=data=>hash('sha256',data);
const encoded=f=>kernel.encode(f),equal=(a,b)=>encoded(a)===encoded(b);
const and=items=>items.reduceRight((rest,item)=>kernel.A(item,rest));
const all=(xs,f)=>xs.reduceRight((rest,x)=>kernel.Q(x,rest),f);
const chain=(items,f)=>items.reduceRight((rest,item)=>kernel.I(item,rest),f);
const close=f=>all([...kernel.free(f)].sort((a,b)=>a-b),f);
const slots={0:37,1:60,2:6,3:7,4:8,7:62,8:61};
const literalSlots={0:0,1:1,2:2,3:3,4:4,7:7,8:8};
const frozen={
 'kernel.mjs':'35da89e237ecbd1a807ade3fffb39ffd57890ace',
 'rh_target.txt':'a55f16f293a784ca91d9d52d65cbaea1e89f80dc',
 'rh_target_compact.txt':'98fb1ce81784556af2f6dff8d0d6b31d9c69d7e5'
};
function frozenBlobs(){
 return Object.fromEntries(Object.entries(frozen).map(([name,want])=>{
   const data=readFileSync(resolve(here,name));
   const actual=hash('sha1',Buffer.concat([Buffer.from('blob '+data.length+'\0'),data]));
   assert(actual===want,'frozen file changed: '+name);return [name,actual];
 }));
}
function sourceHashes(){
 const paths=new Set();
 function visit(path){
   path=resolve(path);if(paths.has(path))return;paths.add(path);
   if(!path.endsWith('.mjs'))return;
   for(const m of readFileSync(path,'utf8').matchAll(/(?:from\s+|import\s*\()(['"])(\.[^'"]+\.(?:mjs|js|json))\1/g))visit(resolve(dirname(path),m[2]));
 }
 for(const file of ['numerator_existence_audit.mjs',...Object.keys(frozen)])visit(resolve(here,file));
 return Object.fromEntries([...paths].sort().map(path=>[relative(repo,path),sha(readFileSync(path))]));
}
function split(f){
 assert(f[0]==='n'&&f[1][0]==='i'&&f[1][2][0]==='n','conjunction shape');
 return [f[1][1],f[1][2][1]];
}
function unpack(f,count){
 const out=[];for(let i=1;i<count;i++){const [x,y]=split(f);out.push(x);f=y}out.push(f);return out;
}
function existsBody(f){
 assert(f[0]==='n'&&f[1][0]==='a'&&f[1][2][0]==='n','existential shape');
 return {variable:f[1][1],body:f[1][2][1]};
}
function strip(f){while(f[0]==='a')f=f[2];return f}
function implicationParts(f,count){
 const premises=[];for(let i=0;i<count;i++){assert(f[0]==='i','implication shape');premises.push(f[1]);f=f[2]}
 return {premises,goal:f};
}

function references(raw){
 let target=kernel.decode(raw.slice(0,-1));const binders=[];
 while(target[0]==='a'){binders.push(target[1]);target=target[2]}
 assert(JSON.stringify(binders)==='[0,1,2,3,4,5,6,7,8]'&&target[0]==='i','frozen target shape');
 const original=unpack(target[1],22),clauses=original.map(f=>simultaneousSubstitution(f,slots));

 // The first three normalized properties come from the old PL-13 theorem,
 // with its initial value set to the natural zero parameter.
 const old=recursionExistence.prepare(raw);
 const oldRoot=strip(kernel.decode(old.raw.target)),oldNormal=existsBody(oldRoot[2]);
 assert(oldNormal.variable===5,'PL13 graph binder');
 const oldParts=unpack(oldNormal.body,4);
 const [total,functional,base]=unpack(simultaneousSubstitution(oldNormal.body,{1:37,5:62,6:60,8:8}),4);
 const oldTotal=strip(oldParts[0]),canonicalAt=split(existsBody(oldTotal[2]).body)[1];
 const canonicalSucc=implicationParts(strip(oldParts[3]),7).premises[4];
 const at=(g,x,y)=>simultaneousSubstitution(canonicalAt,{5:g,40:x,47:y});
 const succ=(x,y)=>simultaneousSubstitution(canonicalSucc,{40:x,49:y});

 // The existential multiply-then-add witness is the conclusion of PL-12's
 // independently compiled local numerator normalization theorem.
 const localTargets=[];
 const observer={prepare(input){
   const context=transport.prepare(input),originalClose=context.p.close;
   context.p.close=(proof,...args)=>{
     const closed=originalClose(proof,...args);localTargets.push(encoded(context.ar.ast(closed.f)));return closed;
   };
   return context;
 }};
 const prior=numerator(observer,kernel,denominator,raw,'local');
 assert(localTargets.length===2&&prior.rows[1].name==='exact_numerator_successor_normalization','PL12 local targets');
 const local=strip(kernel.decode(localTargets[1]));assert(local[0]==='i','PL12 implication');
 const updateGoal=simultaneousSubstitution(local[2],{...slots,51:49,52:42,53:43,54:44});
 const nat=x=>kernel.M(x,37);
 const update=all([40,49,42,43,44],chain([nat(40),nat(49),nat(42),nat(43),nat(44),succ(40,49),at(62,40,42),at(62,49,43),at(61,40,44)],updateGoal));
 return {original,clauses,normalized:and([total,functional,base,update]),normalized_sources:{
   total_functionality_base:'RH-PL-13 normalized recurrence theorem with seed Z',
   update:'RH-PL-12 exact numerator successor normalization theorem',
   prior_update_target_sha256:sha(localTargets[1]),prior_normalized_target_sha256:sha(old.raw.target)
 }};
}
function targets(ref){
 const map=new Map();
 function add(name,indices,goal,sourceSlots,clauseIndices){
   const clauses=sourceSlots===slots?ref.clauses:ref.original,premises=indices.map(i=>clauses[i]);
   const statement=kernel.I(and(premises),goal);
   map.set(name,{indices,premises,goal,slots:sourceSlots,clauseIndices,closed:close(statement)});
 }
 add('normalized_numerator_graph_exists',[0,1,5,6,14],kernel.X(62,ref.normalized),slots,[]);
 add('exact_numerator_exists_given_total_denominator',[0,1,2,5,6,14],kernel.X(62,and([13,18,20].map(i=>ref.clauses[i]))),slots,[13,18,20]);
 add('frozen_numerator_clauses_exist_given_total_denominator',[0,1,2,5,6,14],kernel.X(7,and([13,18,20].map(i=>ref.original[i]))),literalSlots,[13,18,20]);
 const indices=[0,1,2,3,4,5,6],block=[13,14,18,19,20,21];
 add('joint_exact_numerator_denominator_graphs_exist',indices,kernel.X(61,kernel.X(62,and(block.map(i=>ref.clauses[i])))),slots,block);
 add('frozen_joint_numerator_denominator_clauses_exist',indices,kernel.X(8,kernel.X(7,and(block.map(i=>ref.original[i])))),literalSlots,block);
 return map;
}
function checkTarget(target,expected){
 const actual=kernel.decode(target);
 assert(equal(actual,expected.closed),'complete closed theorem differs from the independently audited statement');
 const body=strip(actual);
 assert(body[0]==='i'&&equal(body[1],and(expected.premises))&&equal(body[2],expected.goal),'actual antecedent or consequent differs');
 return body;
}
function fidelity(proof,expected){
 const actual=checkTarget(proof.raw.target,expected),negative={};
 function reject(name,formula){
   let error;try{checkTarget(encoded(close(formula)),expected)}catch(e){error=e.message}
   assert(error,'accepted statement mutant '+name);negative[name]=error;
 }
 reject('wrong_conclusion',kernel.I(actual[1],kernel.E(0,0)));
 reject('dropped_first_premise',kernel.I(and(expected.premises.slice(1)),actual[2]));
 reject('existential_witness_made_universal',kernel.I(actual[1],existsBody(actual[2]).body));
 return {source_slots:expected.slots,source_premise_indices:expected.indices,source_clause_indices:expected.clauseIndices,
   complete_universal_closure_checked:true,exact_antecedent_checked:true,exact_consequent_checked:true,
   antecedent_sha256:sha(encoded(actual[1])),consequent_sha256:sha(encoded(actual[2])),
   statement_negative_controls:negative};
}
function prepareRows(raw){
 const joint=jointRecurrenceExistence.prepare(raw);
 return [...joint.numerator.run(),...joint.run()];
}
export function auditNumeratorExistence(){
 const frozen_blobs=frozenBlobs(),raw=readFileSync(resolve(here,'rh_target.txt'),'utf8');
 const proofs=prepareRows(raw),reference=references(raw),expected=targets(reference);
 assert(proofs.length===expected.size,'unexpected proof count');
 const rows=proofs.map(proof=>{
   const want=expected.get(proof.name||proof.receipt.name);assert(want,'unexpected proof name');
   assert(JSON.stringify(proof.receipt.source_slots)===JSON.stringify(want.slots),'source slot metadata drift');
   assert(JSON.stringify(proof.receipt.source_premise_indices)===JSON.stringify(want.indices),'source premise metadata drift');
   const target_fidelity=fidelity(proof,want),cert=certificate(proof.raw),replay=verifyCertificate(kernel,cert);
   assert(String(proof.receipt.lines)===String(replay.lines)&&String(proof.receipt.unary)===replay.unary&&String(proof.receipt.compact)===replay.compact,'producer byte count drift');
   return {...proof.receipt,independent_replay:replay,target_sha256:sha(cert.target),target_fidelity,
     certificate_json_bytes:Buffer.byteLength(JSON.stringify(cert),'utf8'),negative_controls:auditMutations(cert)};
 });
 return {schema_version:1,group:'numerator_and_joint_existence',
   evidence_level:'checked derivation in the frozen candidate Hilbert calculus',
   frozen_blobs,source_sha256:sourceHashes(),normalized_sources:reference.normalized_sources,
   checks:{frozen_files_match:true,complete_closed_targets_checked:true,exact_antecedents_checked:true,
     exact_consequents_checked:true,independent_certificate_replay:true,byte_counts_recomputed:true,mutation_controls_rejected:true},
   rows,shared_nonpropositional_axiom_recognizer:true,joint_recurrence_existence:true,
   actual_rh_proof:false,finite_rh_upper_bound:false};
}
if(typeof process!=='undefined'&&process.argv[1]===fileURLToPath(import.meta.url)){
 const emit=process.argv.indexOf('--emit');
 if(emit>=0){
   frozenBlobs();const rows=prepareRows(readFileSync(resolve(here,'rh_target.txt'),'utf8'));
   const index=Number(process.argv[emit+1]||0);assert(Number.isInteger(index)&&rows[index],'unknown theorem index');
   process.stdout.write(JSON.stringify(certificate(rows[index].raw))+'\n');
 }else{
   const receipt=auditNumeratorExistence(),text=JSON.stringify(receipt,null,2)+'\n',output=process.argv.indexOf('--output');
   if(output>=0){assert(process.argv[output+1],'missing output path');writeFileSync(process.argv[output+1],text)}
   else process.stdout.write(text);
 }
}
