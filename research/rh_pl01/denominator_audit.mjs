// RH-PL-16: replay exact-denominator bridges and audit the literal frozen targets.
// Usage: node research/rh_pl01/denominator_audit.mjs bridge|normalize|equivalence|existence
//        ... --output receipt.json
//        ... --emit INDEX > certificate.json
import {kernel} from './kernel.mjs';
import {certificate,verifyCertificate} from './joint_audit.mjs';
import {auditMutations} from './ordinal_audit.mjs';
import {recursionExistence} from './recursion_existence.mjs';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {dirname,relative,resolve} from 'node:path';

const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../..');
const assert=(value,message)=>{if(!value)throw Error(message)};
const hash=(kind,data)=>createHash(kind).update(data).digest('hex');
const sha=data=>hash('sha256',data);
const encoded=formula=>kernel.encode(formula);
const equal=(a,b)=>encoded(a)===encoded(b);
const and=items=>items.reduceRight((rest,item)=>kernel.A(item,rest));
const frozen={
 'kernel.mjs':'35da89e237ecbd1a807ade3fffb39ffd57890ace',
 'rh_target.txt':'a55f16f293a784ca91d9d52d65cbaea1e89f80dc',
 'rh_target_compact.txt':'98fb1ce81784556af2f6dff8d0d6b31d9c69d7e5'
};

function frozenBlobs(){
 return Object.fromEntries(Object.entries(frozen).map(([name,expected])=>{
   const data=readFileSync(resolve(here,name));
   const actual=hash('sha1',Buffer.concat([Buffer.from('blob '+data.length+'\0'),data]));
   assert(actual===expected,'frozen file changed: '+name);return [name,actual];
 }));
}

function sourceHashes(entry){
 const paths=new Set();
 function visit(path){
   path=resolve(path);if(paths.has(path))return;paths.add(path);
   if(!path.endsWith('.mjs'))return;
   const source=readFileSync(path,'utf8');
   for(const match of source.matchAll(/(?:from\s+|import\s*\()(['"])(\.[^'"]+\.(?:mjs|js|json))\1/g)){
     visit(resolve(dirname(path),match[2]));
   }
 }
 for(const file of ['denominator_audit.mjs',entry,...Object.keys(frozen)])visit(resolve(here,file));
 return Object.fromEntries([...paths].sort().map(path=>[relative(repo,path),sha(readFileSync(path))]));
}

function split(formula){
 assert(formula[0]==='n'&&formula[1][0]==='i'&&formula[1][2][0]==='n','conjunction shape');
 return [formula[1][1],formula[1][2][1]];
}

function unpack(formula,count){
 const out=[];
 for(let i=1;i<count;i++){const [first,rest]=split(formula);out.push(first);formula=rest}
 out.push(formula);return out;
}

function existsBody(formula){
 assert(formula[0]==='n'&&formula[1][0]==='a'&&formula[1][2][0]==='n','existential shape');
 return {variable:formula[1][1],body:formula[1][2][1]};
}

function stripUniversals(formula){while(formula[0]==='a')formula=formula[2];return formula}

// A simultaneous AST traversal independent of the producer's temporary-variable
// substitution. Rename a bound variable only when an incoming free parameter
// would otherwise be captured. Bound occurrences of source parameters stay bound.
export function simultaneousSubstitution(formula,slots){
 const mapping=new Map(Object.entries(slots).map(([from,to])=>[Number(from),to]));
 for(const [from,to] of mapping)assert(Number.isSafeInteger(from)&&from>=0&&Number.isSafeInteger(to)&&to>=0,'invalid slot');
 const used=new Set([...mapping.keys(),...mapping.values()]);
 function collect(f){
   if(f[0]==='e'||f[0]==='m'){used.add(f[1]);used.add(f[2])}
   else if(f[0]==='n')collect(f[1]);
   else if(f[0]==='i'){collect(f[1]);collect(f[2])}
   else{used.add(f[1]);collect(f[2])}
 }
 collect(formula);let next=0;
 function fresh(){while(used.has(next))next++;used.add(next);return next++}
 function renameBound(f,from,to){
   if(f[0]==='e'||f[0]==='m')return [f[0],f[1]===from?to:f[1],f[2]===from?to:f[2]];
   if(f[0]==='n')return ['n',renameBound(f[1],from,to)];
   if(f[0]==='i')return ['i',renameBound(f[1],from,to),renameBound(f[2],from,to)];
   return f[1]===from?f:['a',f[1],renameBound(f[2],from,to)];
 }
 function walk(f,map){
   if(f[0]==='e'||f[0]==='m')return [f[0],map.get(f[1])??f[1],map.get(f[2])??f[2]];
   if(f[0]==='n')return ['n',walk(f[1],map)];
   if(f[0]==='i')return ['i',walk(f[1],map),walk(f[2],map)];
   let binder=f[1],body=f[2];const inner=new Map(map);inner.delete(binder);
   const free=kernel.free(body);
   if([...inner].some(([from,to])=>to===binder&&free.has(from))){
     const replacement=fresh();body=renameBound(body,binder,replacement);binder=replacement;
   }
   return ['a',binder,walk(body,inner)];
 }
 return walk(formula,mapping);
}

function alphaKey(formula,bound=[]){
 const variable=x=>{const at=bound.lastIndexOf(x);return at<0?['free',x]:['bound',bound.length-1-at]};
 if(formula[0]==='e'||formula[0]==='m')return [formula[0],variable(formula[1]),variable(formula[2])];
 if(formula[0]==='n')return ['n',alphaKey(formula[1],bound)];
 if(formula[0]==='i')return ['i',alphaKey(formula[1],bound),alphaKey(formula[2],bound)];
 return ['a',alphaKey(formula[2],[...bound,formula[1]])];
}

function substitutionControls(clauses){
 const {E,M,Q}=kernel,checks={};
 checks.overlapping_source_destination=equal(simultaneousSubstitution(M(4,8),{4:8,8:61}),M(8,61));
 checks.simultaneous_swap=equal(simultaneousSubstitution(E(4,8),{4:8,8:4}),E(8,4));
 const captured=simultaneousSubstitution(Q(8,M(4,8)),{4:8,8:61});
 checks.capture_avoided=JSON.stringify(alphaKey(captured))===JSON.stringify(alphaKey(Q(99,M(8,99))))&&kernel.free(captured).has(8);
 checks.bound_source_unchanged=equal(simultaneousSubstitution(Q(4,M(4,8)),{4:8,8:61}),Q(4,M(4,61)));
 checks.literal_slots_unchanged=clauses.every(f=>equal(simultaneousSubstitution(f,{0:0,1:1,2:2,4:4,8:8}),f));
 assert(Object.values(checks).every(Boolean),'substitution control failure');return checks;
}

function references(raw){
 let frozenTarget=kernel.decode(raw.slice(0,-1));const binders=[];
 while(frozenTarget[0]==='a'){binders.push(frozenTarget[1]);frozenTarget=frozenTarget[2]}
 assert(JSON.stringify(binders)===JSON.stringify([0,1,2,3,4,5,6,7,8])&&frozenTarget[0]==='i','frozen outer target');
 const clauses=unpack(frozenTarget[1],22);
 const old=recursionExistence.prepare(raw),oldRoot=stripUniversals(kernel.decode(old.raw.target));
 assert(oldRoot[0]==='i','PL13 recursion theorem');
 const normal=existsBody(oldRoot[2]);assert(normal.variable===5,'PL13 graph variable');
 function at(slots){
   for(const key of [0,1,2,4,8])assert(Number.isSafeInteger(slots[key]),'missing frozen slot '+key);
   const converted=clauses.map(f=>simultaneousSubstitution(f,slots));
   const normalized=simultaneousSubstitution(normal.body,{1:slots[0],5:slots[8],6:slots[2],8:slots[4]});
   const [total,functional,base,update]=unpack(normalized,4);
   return {slots,clauses:converted,normalized,total,functional,base,update,
     exact:and([converted[14],converted[19],converted[21]]),
     natZero:kernel.M(slots[1],slots[0]),emptyZero:kernel.Q(23,kernel.N(kernel.M(23,slots[1]))),
     natInitial:kernel.M(slots[2],slots[0])};
 }
 return {clauses,at,substitution_controls:substitutionControls(clauses)};
}

function expectedTargets(group,prepared,proofs,reference){
 const slots=prepared.slots||prepared.source_slots||prepared.frozen_slots;
 const ref=reference.at(slots),fixed=new Map();
 function add(name,premises,goal,indices){fixed.set(name,{slots,premises,goal,indices})}
 if(group==='bridge'){
   add('normalized_denominator_totality_to_exact_clause_14',[ref.total,ref.functional],ref.clauses[14],[14]);
   add('normalized_denominator_base_to_exact_clause_19',[ref.natZero,ref.emptyZero,ref.total,ref.base],ref.clauses[19],[19]);
   add('normalized_denominator_update_to_exact_clause_21',[ref.clauses[0],ref.total,ref.update],ref.clauses[21],[21]);
   add('normalized_denominator_to_exact_frozen_clauses',[ref.clauses[0],ref.natZero,ref.emptyZero,ref.natInitial,ref.normalized],ref.exact,[14,19,21]);
 }else if(group==='normalize'){
   add('exact_denominator_clauses_imply_normalized_recurrence',[ref.natZero,ref.emptyZero,ref.clauses[14],ref.clauses[19],ref.clauses[21]],ref.normalized,[14,19,21]);
 }else if(group==='equivalence'){
   add('normalized_denominator_equivalent_to_exact_frozen_clauses',[ref.clauses[0],ref.natZero,ref.emptyZero],kernel.F(ref.normalized,ref.exact),[14,19,21]);
 }else if(group==='existence'){
   const required={
     exact_denominator_exists_from_omega_and_multiplication:{slots:{0:37,1:60,2:6,4:8,8:61},premise_indices:[0,1,2,3,6],exists_graph:61},
     frozen_denominator_clauses_exist:{slots:{0:0,1:1,2:2,4:4,8:8},premise_indices:[0,1,2,3,4,6],exists_graph:8}
   };
   for(const [name,want] of Object.entries(required)){
     const spec=prepared.target_specs?.[name];assert(spec,'missing existence target specification '+name);
     assert(JSON.stringify(spec.slots)===JSON.stringify(want.slots),'existence slot specification drift');
     assert(JSON.stringify(spec.premise_indices)===JSON.stringify(want.premise_indices),'existence premise specification drift');
     assert(JSON.stringify(spec.clause_indices)===JSON.stringify([14,19,21])&&spec.exists_graph===want.exists_graph,'existence conclusion specification drift');
     const r=reference.at(want.slots);
     fixed.set(name,{slots:want.slots,premises:want.premise_indices.map(i=>r.clauses[i]),goal:kernel.X(want.exists_graph,r.exact),indices:[14,19,21]});
   }
 }else throw Error('unknown fidelity group');
 assert(proofs.length===fixed.size,'unexpected theorem count');
 return fixed;
}

function checkTarget(target,expected){
 const actual=stripUniversals(kernel.decode(target));
 assert(actual[0]==='i','theorem implication shape');
 assert(equal(actual[1],and(expected.premises)),'actual theorem antecedent differs from the audited statement');
 assert(equal(actual[2],expected.goal),'actual theorem consequent differs from the audited statement');
 return actual;
}

function fidelityRow(proof,expected,reference){
 const actual=checkTarget(proof.raw.target,expected),ref=reference.at(expected.slots);
 const negative={};
 function reject(name,target){let error;try{checkTarget(target,expected)}catch(e){error=e.message}assert(error,'accepted statement mutant '+name);negative[name]=error}
 reject('wrong_conclusion',encoded(kernel.I(actual[1],kernel.E(0,0))));
 reject('dropped_first_premise',encoded(kernel.I(and(expected.premises.slice(1)),actual[2])));
 return {source_slots:expected.slots,source_clauses:expected.indices,
   clause_bytes:Object.fromEntries(expected.indices.map(i=>[i,encoded(ref.clauses[i]).length])),
   exact_antecedent_checked:true,exact_consequent_checked:true,
   antecedent_sha256:sha(encoded(actual[1])),consequent_sha256:sha(encoded(actual[2])),
   statement_negative_controls:negative};
}

const groups={
 bridge:['denominator_bridge.mjs','denominatorBridge'],
 normalize:['denominator_normalize.mjs','denominatorNormalize'],
 equivalence:['denominator_equivalence.mjs','denominatorEquivalence'],
 existence:['denominator_existence.mjs','denominatorExistence']
};

export async function auditDenominator(group){
 assert(Object.hasOwn(groups,group),'unknown theorem group');
 const frozen_blobs=frozenBlobs(),[entry,name]=groups[group],module=await import('./'+entry);
 const raw=readFileSync(resolve(here,'rh_target.txt'),'utf8'),prepared=module[name].prepare(raw),proofs=prepared.run();
 const reference=references(raw),targets=expectedTargets(group,prepared,proofs,reference);
 const rows=proofs.map(proof=>{
   const name=proof.name||proof.receipt.name,expected=targets.get(name);assert(expected,'unexpected theorem name '+name);
   const target_fidelity=fidelityRow(proof,expected,reference),cert=certificate(proof.raw),replay=verifyCertificate(kernel,cert);
   assert(String(proof.receipt.lines)===String(replay.lines)&&String(proof.receipt.unary)===replay.unary&&String(proof.receipt.compact)===replay.compact,'producer byte count drift');
   return {...proof.receipt,independent_replay:replay,certificate_json_bytes:Buffer.byteLength(JSON.stringify(cert),'utf8'),
     target_sha256:sha(cert.target),target_fidelity,negative_controls:auditMutations(cert)};
 });
 return {schema_version:1,group,evidence_level:'checked derivation in the frozen candidate Hilbert calculus',
   frozen_blobs,source_sha256:sourceHashes(entry),substitution_controls:reference.substitution_controls,
   checks:{frozen_files_match:true,exact_antecedents_checked:true,exact_consequents_checked:true,
     independent_certificate_replay:true,byte_counts_recomputed:true,mutation_controls_rejected:true},
   rows,shared_nonpropositional_axiom_recognizer:true,actual_rh_proof:false,finite_rh_upper_bound:false};
}

if(typeof process!=='undefined'&&process.argv[1]===fileURLToPath(import.meta.url)){
 const group=process.argv[2]||'bridge',emit=process.argv.indexOf('--emit');
 assert(Object.hasOwn(groups,group),'unknown theorem group');
 if(emit>=0){
   frozenBlobs();const [file,name]=groups[group],module=await import('./'+file);
   const raw=readFileSync(resolve(here,'rh_target.txt'),'utf8'),rows=module[name].prepare(raw).run(),index=Number(process.argv[emit+1]||0);
   assert(rows[index],'unknown theorem index');process.stdout.write(JSON.stringify(certificate(rows[index].raw))+'\n');
 }else{
   const receipt=await auditDenominator(group),text=JSON.stringify(receipt,null,2)+'\n',output=process.argv.indexOf('--output');
   if(output>=0){assert(process.argv[output+1],'missing output path');writeFileSync(process.argv[output+1],text)}
   else process.stdout.write(text);
 }
}
