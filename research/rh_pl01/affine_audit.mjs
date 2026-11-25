// RH-PL-18: independent replay and complete statement checks for the affine
// numerator relation and its realization as an exact natural binary graph.
// Usage: node research/rh_pl01/affine_audit.mjs [--output receipt.json]
//        ... --emit INDEX > certificate.json
import {kernel} from './kernel.mjs';
import {certificate,verifyCertificate} from './joint_audit.mjs';
import {auditMutations} from './ordinal_audit.mjs';
import {simultaneousSubstitution} from './denominator_audit.mjs';
import {numeratorStep} from './numerator_step.mjs';
import {binaryGraph} from './binary_graph.mjs';
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
const free=f=>[...kernel.free(f)].sort((a,b)=>a-b);
const close=f=>all(free(f),f);
const sourceSlots={0:37,1:60,2:6,3:7,4:8,7:62,8:61};
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
   const source=readFileSync(path,'utf8');
   for(const m of source.matchAll(/(?:from\s+|import\s*\()(['"])(\.[^'"]+\.(?:mjs|js|json))\1/g))visit(resolve(dirname(path),m[2]));
 }
 for(const file of ['affine_audit.mjs',...Object.keys(frozen)])visit(resolve(here,file));
 return Object.fromEntries([...paths].sort().map(path=>[relative(repo,path),sha(readFileSync(path))]));
}
function split(f){
 assert(f[0]==='n'&&f[1][0]==='i'&&f[1][2][0]==='n','conjunction shape');
 return [f[1][1],f[1][2][1]];
}
function unpack(f,count){
 const out=[];for(let i=1;i<count;i++){const [x,y]=split(f);out.push(x);f=y}out.push(f);return out;
}
function inst(f,...xs){
 for(const x of xs){assert(f[0]==='a','universal application shape');f=kernel.subst(f[2],f[1],x)}
 return f;
}
function strip(f){while(f[0]==='a')f=f[2];return f}
function firstApplication(f){
 assert(f[0]==='i'&&f[2][0]==='i','natural functionality implications');
 return split(f[2][1])[0];
}

function references(raw){
 assert(raw.endsWith('\n'),'frozen target LF');
 let target=kernel.decode(raw.slice(0,-1));const binders=[];
 while(target[0]==='a'){binders.push(target[1]);target=target[2]}
 assert(JSON.stringify(binders)==='[0,1,2,3,4,5,6,7,8]'&&target[0]==='i','frozen target shape');
 const original=unpack(target[1],22),clauses=original.map(f=>simultaneousSubstitution(f,sourceSlots));
 const {E,M,N,I,Q,X,A,O,F}=kernel,nat=x=>M(x,37);
 // Application formulas come from the actual functionality clauses in
 // the frozen target. The producer's predicate constructors are unused.
 const graph1=(clause,x,u)=>firstApplication(inst(split(clause)[1],x,u,x));
 const graph2=(clause,x,y,u)=>firstApplication(inst(split(clause)[1],x,y,u,x));
 const den=(x,u)=>graph1(clauses[14],x,u);
 const mul=(x,y,u)=>graph2(clauses[6],x,y,u),add=(x,y,u)=>graph2(clauses[5],x,y,u);
 const empty=y=>Q(23,N(M(23,y)));
 const succ=(x,y)=>Q(23,F(M(23,y),O(M(23,x),E(23,x))));
 const relation=(y,a,b)=>O(A(empty(y),E(a,b)),
   X(110,A(nat(110),X(111,A(nat(111),X(112,A(nat(112),
     and([succ(110,y),den(110,111),mul(y,a,112),add(112,111,b)]))))))));
 const totalRelation=all([70,71],I(A(nat(70),nat(71)),X(72,A(nat(72),relation(70,71,72)))));
 const functionalRelation=all([70,71,72,73],I(and([nat(70),nat(71),nat(72),nat(73)]),
   I(A(relation(70,71,72),relation(70,71,73)),E(72,73))));
 const total2=g=>simultaneousSubstitution(original[6],{0:37,4:g});
 const app=(g,y,a,b)=>graph2(total2(g),y,a,b);
 const relationSpec=g=>all([70,71,72],I(and([nat(70),nat(71),nat(72)]),
   F(app(g,70,71,72),relation(70,71,72))));
 const unguardedSpec=g=>all([70,71,72],F(app(g,70,71,72),relation(70,71,72)));
 const helper=(x,y,a,b,d)=>({
   premises:[clauses[0],clauses[14],nat(x),nat(y),nat(a),nat(b),nat(d),succ(x,y),relation(y,a,b),den(x,d)],
   goal:X(113,A(nat(113),A(mul(y,a,113),add(113,d,b))))
 });
 const substitution_controls={
   addition_numerator_slots_separate:equal(simultaneousSubstitution(M(3,7),sourceSlots),M(7,62)),
   multiplication_denominator_slots_separate:equal(simultaneousSubstitution(M(4,8),sourceSlots),M(8,61)),
   simultaneous_graph_swap:equal(simultaneousSubstitution(E(7,8),{7:8,8:7}),E(8,7)),
   bound_source_unchanged:equal(simultaneousSubstitution(Q(7,M(7,8)),sourceSlots),Q(7,M(7,61)))
 };
 const capture=simultaneousSubstitution(Q(7,M(7,3)),sourceSlots);
 substitution_controls.capture_avoided=capture[0]==='a'&&capture[1]!==7&&
   equal(capture[2],M(capture[1],7))&&kernel.free(capture).has(7);
 assert(Object.values(substitution_controls).every(Boolean),'substitution controls');
 return {original,clauses,nat,den,mul,add,succ,relation,totalRelation,functionalRelation,total2,app,
   relationSpec,unguardedSpec,helper,substitution_controls};
}

function expectedTargets(ref){
 const result=new Map(),sourcePremises=[0,14,6,5],premises=sourcePremises.map(i=>ref.clauses[i]);
 function add(name,premises,goal,indices,extra={}){
   const body=premises?kernel.I(and(premises),goal):goal;
   result.set(name,{premises,goal,indices,body,closed:close(body),...extra});
 }
 add('affine_numerator_step_total_on_naturals',premises,ref.totalRelation,sourcePremises);
 add('affine_numerator_step_single_valued_on_naturals',premises,ref.functionalRelation,sourcePremises);
 add('affine_numerator_step_total_and_single_valued',premises,kernel.A(ref.totalRelation,ref.functionalRelation),sourcePremises);
 const helper=ref.helper(80,81,82,83,84);
 add('affine_numerator_successor_step_to_normalized_update',helper.premises,helper.goal,[0,14]);
 add('bounded_natural_binary_relation_realization',null,kernel.X(64,ref.relationSpec(64)),[],
   {unguardedGoal:kernel.X(64,ref.unguardedSpec(64)),graphWitness:64});
 const graphGoal=kernel.X(64,kernel.A(ref.total2(64),ref.relationSpec(64)));
 add('total_functional_binary_relation_graph_exists',[ref.totalRelation,ref.functionalRelation],graphGoal,[],{graphWitness:64});
 add('affine_step_binary_graph_exists',premises,graphGoal,sourcePremises,{graphWitness:64});
 return result;
}
function checkTarget(target,expected){
 const actual=kernel.decode(target);
 assert(equal(actual,expected.closed),'complete closed theorem differs from the independently audited statement');
 const body=strip(actual);
 if(expected.premises){
   assert(body[0]==='i'&&equal(body[1],and(expected.premises)),'actual theorem antecedent differs');
   assert(equal(body[2],expected.goal),'actual theorem consequent differs');
 }else assert(equal(body,expected.goal),'actual theorem existential conclusion differs');
 return body;
}
function fidelity(proof,expected){
 const actual=checkTarget(proof.raw.target,expected),negative={};
 function reject(name,formula){
   let error;try{checkTarget(encoded(formula),expected)}catch(e){error=e.message}
   assert(error,'accepted statement mutant '+name);negative[name]=error;
 }
 const wrongGoal=kernel.E(0,0);
 reject('wrong_conclusion',close(expected.premises?kernel.I(actual[1],wrongGoal):wrongGoal));
 if(expected.premises)reject('dropped_first_premise',close(kernel.I(and(expected.premises.slice(1)),expected.goal)));
 else reject('dropped_natural_domain_guard',close(expected.unguardedGoal));
 assert(expected.closed[0]==='a','expected nonempty universal closure');
 reject('removed_universal_closure_binder',expected.closed[2]);
 return {source_slots:sourceSlots,source_premise_indices:expected.indices,
   source_application_clause_indices:[5,6,14],graph_witness_variable:expected.graphWitness??null,
   complete_universal_closure_checked:true,universal_parameters:free(expected.body),
   exact_antecedent_checked:expected.premises?true:null,exact_consequent_checked:true,
   antecedent_sha256:expected.premises?sha(encoded(actual[1])):null,
   consequent_sha256:sha(encoded(expected.goal)),statement_negative_controls:negative};
}
function replayRow(proof,expected){
 const target_fidelity=fidelity(proof,expected),cert=certificate(proof.raw),replay=verifyCertificate(kernel,cert);
 assert(String(proof.receipt.lines)===String(replay.lines)&&String(proof.receipt.unary)===replay.unary&&
   String(proof.receipt.compact)===replay.compact,'producer byte count drift');
 return {...proof.receipt,independent_replay:replay,target_sha256:sha(cert.target),target_fidelity,
   certificate_json_bytes:Buffer.byteLength(JSON.stringify(cert),'utf8'),negative_controls:auditMutations(cert)};
}

function prepareRows(raw){
 const step=numeratorStep.prepare(raw),graph=binaryGraph.prepare(raw,step.ctx,{relation:step.relation,W:37,T:64});
 assert(graph.totalRelation===step.totalRelation&&graph.functionalRelation===step.functionalRelation,'relation composition interface');
 const composed=step.ctx.get('affine_step_binary_graph_exists',step.ctx.p.logic.comp(step.result,graph.result));
 Object.assign(composed.receipt,{source_clauses:[0,14,6,5],source_slots:sourceSlots,
   natural_domain_variable:37,graph_witness_variable:64,exact_total2_from_frozen_clause_6:true,
   denominator_recurrence_premise_required:false,actual_rh_proof:false});
 return {step,graph,proofs:[...step.run(),...graph.run(),composed]};
}

function boundaryControl(step,reference){
 // The old normalized update helper used an output binder at 70. Call the
 // new helper with its successor argument in that slot and replay the proof.
 const [x,y,a,b,d]=[74,70,71,72,73],{ctx}=step,p=step.predicates;
 const premises=[p.omega,p.clause(14),p.nat(x),p.nat(y),p.nat(a),p.nat(b),p.nat(d),
   ctx.t.succ(x,y),step.relation(y,a,b),p.gb(61,x,d)];
 const proof=ctx.pack(premises,(hw,dt,mx,my,ma,mb,md,hs,hr,hd)=>
   step.successorUpdateAt(hw,dt,x,y,a,b,d,mx,my,ma,mb,md,hs,hr,hd));
 const ref=reference.helper(x,y,a,b,d),body=kernel.I(and(ref.premises),ref.goal);
 const expected={...ref,body,closed:close(body),indices:[0,14]};
 assert(equal(ctx.ar.ast(proof.f),body),'argument70 helper open statement');
 const actualGoal=ctx.ar.ast(ctx.ns[proof.f].y),goalFree=free(actualGoal);
 assert(JSON.stringify(goalFree)==='[7,8,37,70,71,72,73]','argument70 helper free variables');
 const row=replayRow(ctx.get('affine_successor_update_preserves_free_argument_70',proof),expected);
 const captured=kernel.X(70,kernel.A(reference.nat(70),kernel.A(reference.mul(y,a,70),reference.add(70,d,b))));
 let rejected;
 try{checkTarget(encoded(close(kernel.I(and(ref.premises),captured))),expected)}catch(error){rejected=error.message}
 assert(rejected&&!kernel.free(captured).has(70),'capture mutant must bind the argument and fail fidelity');
 row.target_fidelity.statement_negative_controls.output_binder_captures_argument_70=rejected;
 return {parameters:{predecessor:x,successor:y,input:a,output:b,denominator_value:d},
   output_witness_binder:113,expected_goal_free_variables:[7,8,37,70,71,72,73],
   actual_goal_free_variables:goalFree,complete_open_statement_checked:true,independent_certificate_replay:true,row};
}

export function auditAffine(){
 const frozen_blobs=frozenBlobs(),raw=readFileSync(resolve(here,'rh_target.txt'),'utf8');
 const prepared=prepareRows(raw),reference=references(raw),expected=expectedTargets(reference);
 assert(JSON.stringify(prepared.step.source_slots)===JSON.stringify(sourceSlots),'source slot metadata drift');
 assert(prepared.step.relation_source===encoded(reference.relation(70,71,72)),'affine relation source drift');
 assert(prepared.graph.W===37&&prepared.graph.T===64,'binary graph parameter drift');
 assert(prepared.proofs.length===expected.size,'unexpected primary theorem count');
 const rows=prepared.proofs.map(proof=>{
   const want=expected.get(proof.name||proof.receipt.name);assert(want,'unexpected theorem');
   if(proof.receipt.source_clauses)assert(JSON.stringify(proof.receipt.source_clauses)===JSON.stringify(want.indices),'premise metadata drift');
   return replayRow(proof,want);
 });
 const argument70_boundary_control=boundaryControl(prepared.step,reference);
 return {schema_version:1,group:'affine_relation_and_binary_graph',
   evidence_level:'checked derivation in the frozen candidate Hilbert calculus',
   frozen_blobs,source_sha256:sourceHashes(),source_slots:sourceSlots,
   relation_definition:{source_application_clause_indices:[5,6,14],
     successor_witness_variables:[110,111,112],formula_sha256:sha(encoded(reference.relation(70,71,72))),
     formula_bytes:encoded(reference.relation(70,71,72)).length,
     zero_case:'empty(y) and a=b',successor_case:'natural x,d,u with Succ(x,y), DEN(x,d), MUL(y,a,u), ADD(u,d,b)'},
   graph_definition:{natural_domain_variable:37,graph_witness_variable:64,
     exact_total2_source_clause:6,exact_application_iff_relation_on_naturals:true,
     carrier:'W union P(P(W))',outer_bound:'P(P(carrier))'},
   substitution_controls:reference.substitution_controls,
   checks:{frozen_files_match:true,complete_closed_targets_checked:true,exact_antecedents_checked:true,
     exact_consequents_checked:true,independent_certificate_replay:true,byte_counts_recomputed:true,
     mutation_controls_rejected:true,argument70_boundary_replayed:true},
   rows,argument70_boundary_control,shared_nonpropositional_axiom_recognizer:true,
   denominator_recurrence_premise_required:false,numerator_recurrence_existence_included:false,
   joint_recurrence_existence:false,actual_rh_proof:false,finite_rh_upper_bound:false};
}
if(typeof process!=='undefined'&&process.argv[1]===fileURLToPath(import.meta.url)){
 const emit=process.argv.indexOf('--emit');
 if(emit>=0){
   frozenBlobs();const {proofs}=prepareRows(readFileSync(resolve(here,'rh_target.txt'),'utf8'));
   const index=Number(process.argv[emit+1]||0);assert(Number.isInteger(index)&&proofs[index],'unknown theorem index');
   process.stdout.write(JSON.stringify(certificate(proofs[index].raw))+'\n');
 }else{
   const receipt=auditAffine(),text=JSON.stringify(receipt,null,2)+'\n',output=process.argv.indexOf('--output');
   if(output>=0){assert(process.argv[output+1],'missing output path');writeFileSync(process.argv[output+1],text)}
   else process.stdout.write(text);
 }
}
