// RH-PL-17: independent certificate replay and exact statement fidelity.
// Usage: node research/rh_pl01/numerator_audit.mjs [--output receipt.json]
//        ... --emit INDEX > certificate.json
import {kernel} from './kernel.mjs';
import {certificate,verifyCertificate} from './joint_audit.mjs';
import {auditMutations} from './ordinal_audit.mjs';
import {simultaneousSubstitution} from './denominator_audit.mjs';
import {recursionExistence} from './recursion_existence.mjs';
import {transport} from './transport.mjs';
import {denominator} from './denominator.mjs';
import {numerator} from './numerator.mjs';
import {numeratorBridge} from './numerator_bridge.mjs';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {dirname,relative,resolve} from 'node:path';

const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../..');
const assert=(value,message)=>{if(!value)throw Error(message)};
const hash=(kind,data)=>createHash(kind).update(data).digest('hex'),sha=data=>hash('sha256',data);
const encoded=formula=>kernel.encode(formula),equal=(a,b)=>encoded(a)===encoded(b);
const and=items=>items.reduceRight((rest,item)=>kernel.A(item,rest));
const all=(xs,body)=>xs.reduceRight((f,x)=>kernel.Q(x,f),body);
const chain=(items,body)=>items.reduceRight((f,h)=>kernel.I(h,f),body);
const frozen={
 'kernel.mjs':'35da89e237ecbd1a807ade3fffb39ffd57890ace',
 'rh_target.txt':'a55f16f293a784ca91d9d52d65cbaea1e89f80dc',
 'rh_target_compact.txt':'98fb1ce81784556af2f6dff8d0d6b31d9c69d7e5'
};
const sourceSlots={0:37,1:60,2:6,3:7,4:8,7:62,8:61};

function frozenBlobs(){
 return Object.fromEntries(Object.entries(frozen).map(([name,expected])=>{
   const data=readFileSync(resolve(here,name));
   const actual=hash('sha1',Buffer.concat([Buffer.from('blob '+data.length+'\0'),data]));
   assert(actual===expected,'frozen file changed: '+name);return [name,actual];
 }));
}
function sourceHashes(){
 const paths=new Set();
 function visit(path){
   path=resolve(path);if(paths.has(path))return;paths.add(path);
   if(!path.endsWith('.mjs'))return;
   const source=readFileSync(path,'utf8');
   for(const match of source.matchAll(/(?:from\s+|import\s*\()(['"])(\.[^'"]+\.(?:mjs|js|json))\1/g))visit(resolve(dirname(path),match[2]));
 }
 for(const file of ['numerator_audit.mjs',...Object.keys(frozen)])visit(resolve(here,file));
 return Object.fromEntries([...paths].sort().map(path=>[relative(repo,path),sha(readFileSync(path))]));
}
function split(f){
 assert(f[0]==='n'&&f[1][0]==='i'&&f[1][2][0]==='n','conjunction shape');
 return [f[1][1],f[1][2][1]];
}
function unpack(f,count){
 const out=[];for(let i=1;i<count;i++){const [first,rest]=split(f);out.push(first);f=rest}out.push(f);return out;
}
function existsBody(f){
 assert(f[0]==='n'&&f[1][0]==='a'&&f[1][2][0]==='n','existential shape');
 return {variable:f[1][1],body:f[1][2][1]};
}
function stripUniversals(f){while(f[0]==='a')f=f[2];return f}
function implicationPremises(f,count){
 const out=[];for(let i=0;i<count;i++){assert(f[0]==='i','implication shape');out.push(f[1]);f=f[2]}return {premises:out,goal:f};
}

function references(raw){
 let frozenTarget=kernel.decode(raw.slice(0,-1));const binders=[];
 while(frozenTarget[0]==='a'){binders.push(frozenTarget[1]);frozenTarget=frozenTarget[2]}
 assert(JSON.stringify(binders)===JSON.stringify([0,1,2,3,4,5,6,7,8])&&frozenTarget[0]==='i','frozen outer target');
 const sourceClauses=unpack(frozenTarget[1],22);
 const clauses=sourceClauses.map(f=>simultaneousSubstitution(f,sourceSlots));

 // Read totality, functionality, the canonical graph relation, and the
 // base predicate from the prior PL-13 normalized theorem itself.
 const old=recursionExistence.prepare(raw),oldRoot=stripUniversals(kernel.decode(old.raw.target));
 const oldNormal=existsBody(oldRoot[2]);assert(oldNormal.variable===5,'PL13 graph variable');
 const oldParts=unpack(oldNormal.body,4),normal=simultaneousSubstitution(oldNormal.body,{1:37,5:62,6:60,8:8});
 const [total,functional,base]=unpack(normal,4);
 const totalBody=stripUniversals(oldParts[0]);
 const canonicalAt=split(existsBody(totalBody[2]).body)[1];
 const oldStep=implicationPremises(stripUniversals(oldParts[3]),7);
 const canonicalSucc=oldStep.premises[4];
 const at=(graph,x,y)=>simultaneousSubstitution(canonicalAt,{5:graph,40:x,47:y});
 const succ=(x,y)=>simultaneousSubstitution(canonicalSucc,{40:x,49:y});

 // Observe the old numerator compiler's closed local theorem targets
 // through a delegating close() wrapper. The compiler and every proof
 // check run unchanged; no inference or axiom is substituted.
 const localTargets=[];
 const observer={prepare(input){
   const context=transport.prepare(input),close=context.p.close;
   context.p.close=(proof,...args)=>{
     const closed=close(proof,...args);localTargets.push(kernel.encode(context.ar.ast(closed.f)));return closed;
   };
   return context;
 }};
 const prior=numerator(observer,kernel,denominator,raw,'local');
 assert(localTargets.length===2&&prior.rows[1].name==='exact_numerator_successor_normalization','PL12 local normalization targets');
 const priorUpdate=stripUniversals(kernel.decode(localTargets[1]));
 assert(priorUpdate[0]==='i','PL12 numerator normalization implication');
 const oldUpdateGoal=priorUpdate[2];
 const updateGoal=simultaneousSubstitution(oldUpdateGoal,{...sourceSlots,51:49,52:42,53:43,54:44});
 const nat=x=>kernel.M(x,37);
 const update=all([40,49,42,43,44],chain([nat(40),nat(49),nat(42),nat(43),nat(44),succ(40,49),at(62,40,42),at(62,49,43),at(61,40,44)],updateGoal));
 const normalized=and([total,functional,base,update]);
 const natZero=nat(60),emptyZero=kernel.Q(23,kernel.N(kernel.M(23,60)));
 const checks={
   addition_numerator_slots_separate:equal(simultaneousSubstitution(kernel.M(3,7),sourceSlots),kernel.M(7,62)),
   multiplication_denominator_slots_separate:equal(simultaneousSubstitution(kernel.M(4,8),sourceSlots),kernel.M(8,61)),
   simultaneous_graph_swap:equal(simultaneousSubstitution(kernel.E(7,8),{7:8,8:7}),kernel.E(8,7)),
   bound_source_unchanged:equal(simultaneousSubstitution(kernel.Q(7,kernel.M(7,8)),sourceSlots),kernel.Q(7,kernel.M(7,61)))
 };
 // Freshen the binder when the incoming free addition parameter would
 // otherwise be captured; its old bound occurrences stay bound.
 const capture=simultaneousSubstitution(kernel.Q(7,kernel.M(7,3)),sourceSlots);
 checks.capture_avoided=capture[0]==='a'&&capture[1]!==7&&equal(capture[2],kernel.M(capture[1],7))&&kernel.free(capture).has(7);
 assert(Object.values(checks).every(Boolean),'substitution controls');
 return {sourceClauses,clauses,total,functional,base,update,normalized,natZero,emptyZero,
   exact:and([clauses[13],clauses[18],clauses[20]]),substitution_controls:checks,
   normalized_sources:{total_functionality_base:'RH-PL-13 normalized recurrence conclusion with initial value set to Z',
     update:'RH-PL-12 exact numerator successor normalization conclusion',
     prior_update_target_sha256:sha(localTargets[1]),prior_update_goal_sha256:sha(encoded(oldUpdateGoal)),
     prior_update_lines:prior.rows[1].lines,prior_update_unary:prior.rows[1].unary}};
}

function expectedTargets(ref){
 const entries=[
   ['normalized_numerator_totality_to_exact_clause_13',[ref.total,ref.functional],ref.clauses[13],[13]],
   ['normalized_numerator_base_to_exact_clause_18',[ref.natZero,ref.emptyZero,ref.total,ref.base],ref.clauses[18],[18]],
   ['normalized_numerator_update_to_exact_clause_20',[ref.clauses[0],ref.total,ref.clauses[14],ref.update],ref.clauses[20],[20]],
   ['normalized_numerator_to_exact_frozen_clauses',[ref.clauses[0],ref.natZero,ref.emptyZero,ref.clauses[14],ref.normalized],ref.exact,[13,18,20]]
 ];
 const targets=new Map(entries.map(([name,premises,goal,indices])=>[name,{premises,goal,indices,slots:sourceSlots}]));
 const originalSlots={0:0,1:1,2:2,3:3,4:4,7:7,8:8};
 const originalNormalized=simultaneousSubstitution(ref.normalized,{37:0,60:1,7:3,8:4,62:7,61:8});
 targets.set('normalized_numerator_to_original_frozen_slots',{
   premises:[ref.sourceClauses[0],kernel.M(1,0),kernel.Q(23,kernel.N(kernel.M(23,1))),ref.sourceClauses[14],originalNormalized],
   goal:and([ref.sourceClauses[13],ref.sourceClauses[18],ref.sourceClauses[20]]),indices:[13,18,20],slots:originalSlots
 });
 return targets;
}
function checkTarget(target,expected){
 const actual=stripUniversals(kernel.decode(target));
 assert(actual[0]==='i','theorem implication shape');
 assert(equal(actual[1],and(expected.premises)),'actual theorem antecedent differs from the audited statement');
 assert(equal(actual[2],expected.goal),'actual theorem consequent differs from the audited statement');
 return actual;
}
function fidelityRow(proof,expected,reference){
 const actual=checkTarget(proof.raw.target,expected),negative={};
 function reject(name,target){let error;try{checkTarget(target,expected)}catch(e){error=e.message}assert(error,'accepted statement mutant '+name);negative[name]=error}
 reject('wrong_conclusion',encoded(kernel.I(actual[1],kernel.E(0,0))));
 reject('dropped_first_premise',encoded(kernel.I(and(expected.premises.slice(1)),actual[2])));
 return {source_slots:expected.slots,source_clauses:expected.indices,
   clause_bytes:Object.fromEntries(expected.indices.map(i=>[i,encoded(simultaneousSubstitution(reference.sourceClauses[i],expected.slots)).length])),
   exact_antecedent_checked:true,exact_consequent_checked:true,
   antecedent_sha256:sha(encoded(actual[1])),consequent_sha256:sha(encoded(actual[2])),
   statement_negative_controls:negative};
}

export function auditNumerator(){
 const frozen_blobs=frozenBlobs(),raw=readFileSync(resolve(here,'rh_target.txt'),'utf8');
 const prepared=numeratorBridge.prepare(raw),proofs=prepared.run(),reference=references(raw),targets=expectedTargets(reference);
 assert(JSON.stringify(prepared.slots)===JSON.stringify(sourceSlots),'source slot drift');
 assert(proofs.length===targets.size,'unexpected theorem count');
 const rows=proofs.map(proof=>{
   const name=proof.name||proof.receipt.name,expected=targets.get(name);assert(expected,'unexpected theorem '+name);
   assert(JSON.stringify(proof.receipt.source_slot_mapping)===JSON.stringify(expected.slots),'theorem source-slot metadata drift');
   const target_fidelity=fidelityRow(proof,expected,reference),cert=certificate(proof.raw),replay=verifyCertificate(kernel,cert);
   assert(String(proof.receipt.lines)===String(replay.lines)&&String(proof.receipt.unary)===replay.unary&&String(proof.receipt.compact)===replay.compact,'producer byte count drift');
   return {...proof.receipt,independent_replay:replay,certificate_json_bytes:Buffer.byteLength(JSON.stringify(cert),'utf8'),
     target_sha256:sha(cert.target),target_fidelity,negative_controls:auditMutations(cert)};
 });
 return {schema_version:1,group:'numerator_bridge',evidence_level:'checked derivation in the frozen candidate Hilbert calculus',
   frozen_blobs,source_sha256:sourceHashes(),substitution_controls:reference.substitution_controls,normalized_sources:reference.normalized_sources,
   checks:{frozen_files_match:true,exact_antecedents_checked:true,exact_consequents_checked:true,
     independent_certificate_replay:true,byte_counts_recomputed:true,mutation_controls_rejected:true},
   rows,shared_nonpropositional_axiom_recognizer:true,joint_recurrence_existence:false,actual_rh_proof:false,finite_rh_upper_bound:false};
}
if(typeof process!=='undefined'&&process.argv[1]===fileURLToPath(import.meta.url)){
 const emit=process.argv.indexOf('--emit');
 if(emit>=0){
   frozenBlobs();const raw=readFileSync(resolve(here,'rh_target.txt'),'utf8'),rows=numeratorBridge.prepare(raw).run(),index=Number(process.argv[emit+1]||0);
   assert(Number.isInteger(index)&&rows[index],'unknown theorem index');
   process.stdout.write(JSON.stringify(certificate(rows[index].raw))+'\n');
 }else{
   const receipt=auditNumerator(),text=JSON.stringify(receipt,null,2)+'\n',output=process.argv.indexOf('--output');
   if(output>=0){assert(process.argv[output+1],'missing output path');writeFileSync(process.argv[output+1],text)}
   else process.stdout.write(text);
 }
}
