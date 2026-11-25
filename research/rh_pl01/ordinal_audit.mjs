// RH-PL-15: independent certificate replay, exact predicate fidelity, and provenance.
// Usage: node research/rh_pl01/ordinal_audit.mjs ordinals|base|extension|overlap|total|recursion
//        ... --emit INDEX > certificate.json
//        ... --output receipt.json
import {kernel} from './kernel.mjs';
import {certificate,verifyCertificate} from './joint_audit.mjs';
import {prefixFamily} from './prefix_family.mjs';
import {recursionExistence} from './recursion_existence.mjs';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {dirname,relative,resolve} from 'node:path';

const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../..');
const assert=(value,message)=>{if(!value)throw Error(message)};
const digest=(kind,data)=>createHash(kind).update(data).digest('hex');
const gitBlob=data=>digest('sha1',Buffer.concat([Buffer.from('blob '+data.length+'\0'),data]));
const frozen={
 'kernel.mjs':'35da89e237ecbd1a807ade3fffb39ffd57890ace',
 'rh_target.txt':'a55f16f293a784ca91d9d52d65cbaea1e89f80dc',
 'rh_target_compact.txt':'98fb1ce81784556af2f6dff8d0d6b31d9c69d7e5'
};

function checkFrozen(){
 const result={};
 for(const [name,expected] of Object.entries(frozen)){
   const actual=gitBlob(readFileSync(resolve(here,name)));
   assert(actual===expected,'frozen file changed: '+name);result[name]=actual;
 }
 return result;
}

function sourceHashes(entries){
 const seen=new Set();
 function visit(path){
   path=resolve(path);if(seen.has(path))return;seen.add(path);
   if(!path.endsWith('.mjs'))return;
   const source=readFileSync(path,'utf8');
   for(const match of source.matchAll(/(?:from\s+|import\s*\()(['"])(\.[^'"]+\.(?:mjs|js|json))\1/g)){
     visit(resolve(dirname(path),match[2]));
   }
 }
 for(const name of entries)visit(resolve(here,name));
 for(const name of Object.keys(frozen))visit(resolve(here,name));
 return Object.fromEntries([...seen].sort().map(path=>[relative(repo,path),digest('sha256',readFileSync(path))]));
}

// Count bytes from the certificate syntax, without using the producer's costs.
// This is also used to repair mutant receipts before testing proof validity.
function nodeCosts(nodes){
 const unary=[0n],compact=[0n],v=x=>BigInt(x<36?1:2+x.toString(36).length);
 for(let i=1;i<nodes.length;i++){
   const [tag,x,y]=nodes[i];
   if(tag==='e'||tag==='m'){unary.push(5n+BigInt(x)+BigInt(y));compact.push(1n+v(x)+v(y))}
   else if(tag==='n'){unary.push(1n+unary[x]);compact.push(1n+compact[x])}
   else if(tag==='i'){unary.push(1n+unary[x]+unary[y]);compact.push(1n+compact[x]+compact[y])}
   else if(tag==='a'){unary.push(3n+BigInt(x)+unary[y]);compact.push(1n+v(x)+compact[y])}
   else throw Error('cost node tag');
 }
 return {unary,compact};
}

function recost(cert,lines){
 const {unary,compact}=nodeCosts(cert.nodes);
 return {...cert,lines,claimed:{lines:lines.length,
   unary:String(lines.reduce((n,i)=>n+unary[i]+1n,0n)),
   compact:String(lines.reduce((n,i)=>n+compact[i]+1n,0n))}};
}

export function auditMutations(cert){
 const rejected={};
 function reject(name,mutant,expected){
   let message;
   try{verifyCertificate(kernel,mutant)}catch(error){message=error.message}
   assert(message,'accepted mutant: '+name);
   if(expected)assert(message.startsWith(expected),'wrong rejection for '+name+': '+message);
   rejected[name]=message;
 }
 reject('incorrect_byte_count',{...cert,claimed:{...cert.claimed,unary:String(BigInt(cert.claimed.unary)+1n)}},'cost mismatch');
 reject('different_target',{...cert,target:cert.target+'x'},'target mismatch');
 const cyclic=cert.nodes.slice();cyclic[1]=['n',1];
 reject('cyclic_formula',{...cert,nodes:cyclic},'negation child');
 const duplicate=cert.nodes.concat([cert.nodes[1]]);
 reject('duplicate_syntax',{...cert,nodes:duplicate},'noncanonical duplicate node');
 reject('duplicate_proof_line',recost(cert,[cert.lines[0],...cert.lines]),'invalid or duplicate line');
 // Removing a proof premise must fail at derivability, not at the final
 // receipt comparison. Search a short prefix for a necessary line because
 // some emitted lines can also be justified by a different valid rule.
 let removed=null;
 for(let index=0;index<Math.min(32,cert.lines.length-1);index++){
   const mutant=recost(cert,cert.lines.filter((_,i)=>i!==index));
   try{verifyCertificate(kernel,mutant)}catch(error){
     if(error.message.startsWith('unjustified line ')){removed={index,message:error.message};break}
     throw error;
   }
 }
 assert(removed,'no essential premise found in the checked prefix');
 rejected.missing_essential_premise={removed_line:removed.index,error:removed.message,costs_recomputed:true};
 return rejected;
}

function split(f){
 assert(f[0]==='n'&&f[1][0]==='i'&&f[1][2][0]==='n','conjunction shape');
 return [f[1][1],f[1][2][1]];
}

function referencePredicates(raw){
 const family=prefixFamily.prepare(raw);let body=kernel.decode(family.raw.target);
 while(body[0]==='a')body=body[2];
 for(let i=0;i<3;i++){
   assert(body[0]==='n'&&body[1][0]==='a'&&body[1][2][0]==='n','family existential shape');
   body=body[1][2][1];
 }
 const spec=split(split(body)[1])[1];assert(spec[0]==='a'&&spec[1]===0,'family graph binder');
 const forward=split(spec[2])[0];assert(forward[0]==='i','family forward direction');
 const good=split(forward[2])[1];
 return {good,famSpec:spec};
}

function contains(root,needle){
 const wanted=kernel.encode(needle),todo=[root];
 while(todo.length){
   const f=todo.pop();if(kernel.encode(f)===wanted)return true;
   if(f[0]==='n')todo.push(f[1]);else if(f[0]==='i')todo.push(f[1],f[2]);else if(f[0]==='a')todo.push(f[2]);
 }
 return false;
}

function fidelity(raw,prepared,rows,group){
 if(group==='ordinals')return null;
 if(group==='recursion'){
   const reference=recursionExistence.prepare(raw);let previous=kernel.decode(reference.raw.target);
   while(previous[0]==='a')previous=previous[2];
   assert(previous[0]==='i','PL-13 recurrence implication shape');
   assert(Number.isSafeInteger(prepared.omega_variable),'missing recurrence Omega variable');
   const goal=kernel.subst(previous[2],1,prepared.omega_variable),encoded=kernel.encode(goal);
   assert(prepared.normalized_goal===encoded,'normalized goal differs from RH-PL-13');
   for(const row of rows){
     let root=kernel.decode(row.raw.target);while(root[0]==='a')root=root[2];
     assert(root[0]==='i'&&kernel.encode(root[2])===encoded,'actual recurrence conclusion differs from RH-PL-13');
   }
   return {kind:'normalized_recurrence_goal',goal_bytes:encoded.length,goal_sha256:digest('sha256',encoded),
     omega_variable:prepared.omega_variable,matches_rh_pl13_exactly:true,actual_root_conclusions_checked:rows.length};
 }
 const expected=referencePredicates(raw),source=prepared.good_source||prepared.good_predicate;
 assert(typeof source==='string','missing Good predicate fidelity export');
 assert(source===kernel.encode(expected.good),'Good predicate differs from RH-PL-13');
 const familySource=prepared.famSpec||prepared.family_source;
 if(familySource)assert(familySource===kernel.encode(expected.famSpec),'family specification differs from RH-PL-13');
 const checked=[];
 for(const row of rows){
   const instances=prepared.good_target_instances?.[row.name||row.receipt.name]||prepared.good_instances||(group==='overlap'?
     (row.name==='bounded_good_prefix_family_compatibility'?[{graph:0,omega:37}]:[{graph:60,omega:1},{graph:61,omega:1}]):null);
   assert(instances?.length,'missing actual target Good instances');
   const root=kernel.decode(row.raw.target);
   for(const {graph,omega} of instances){
     const wanted=kernel.subst(kernel.subst(expected.good,37,omega),0,graph);
     assert(contains(root,wanted),'theorem target omits exact Good('+graph+') at W'+omega);
   }
   checked.push({name:row.name||row.receipt.name,instances});
 }
 return {good_predicate_bytes:source.length,good_source_sha256:digest('sha256',source),
   matches_rh_pl13_exactly:true,actual_target_instances:checked,
   family_specification_matches:familySource?true:null};
}

const groups={ordinals:['ordinals.mjs','ordinals'],base:['prefix_base.mjs','prefixBase','strong'],extension:['prefix_extension.mjs','prefixExtension'],overlap:['prefix_overlap.mjs','prefixOverlap'],total:['prefix_total.mjs','prefixTotal'],recursion:['prefix_recursion.mjs','prefixRecursion']};
const proofRows=(prepared,method)=>method?[prepared[method]()]:prepared.run();

export async function auditGroup(group){
 assert(Object.hasOwn(groups,group),'unknown theorem group');
 const frozen_blobs=checkFrozen(),[file,name,method]=groups[group],module=await import('./'+file);
 const raw=readFileSync(resolve(here,'rh_target.txt'),'utf8'),prepared=module[name].prepare(raw),proofs=proofRows(prepared,method);
 const predicate_fidelity=fidelity(raw,prepared,proofs,group);
 const rows=proofs.map(proof=>{
   const cert=certificate(proof.raw),replayed=verifyCertificate(kernel,cert);
   assert(String(proof.receipt.lines)===String(replayed.lines)&&String(proof.receipt.unary)===replayed.unary&&String(proof.receipt.compact)===replayed.compact,'producer receipt cost drift');
   return {...proof.receipt,independent_replay:replayed,
     certificate_json_bytes:Buffer.byteLength(JSON.stringify(cert),'utf8'),
     target_sha256:digest('sha256',cert.target),negative_controls:auditMutations(cert)};
 });
 return {schema_version:1,evidence_level:'checked derivation in the frozen candidate Hilbert calculus',
   group,frozen_blobs,source_sha256:sourceHashes(['ordinal_audit.mjs',file,'prefix_family.mjs']),
   checks:{frozen_files_match:true,independent_certificate_replay:true,byte_counts_recomputed:true,
     mutation_controls_rejected:true,predicate_fidelity:predicate_fidelity===null||predicate_fidelity.matches_rh_pl13_exactly},
   predicate_fidelity,rows,shared_nonpropositional_axiom_recognizer:true,
   actual_rh_proof:false,finite_rh_upper_bound:false};
}

if(typeof process!=='undefined'&&process.argv[1]===fileURLToPath(import.meta.url)){
 const group=process.argv[2]||'ordinals',emit=process.argv.indexOf('--emit');
 if(emit>=0){
   assert(Object.hasOwn(groups,group),'unknown theorem group');checkFrozen();
   const [file,name,method]=groups[group],module=await import('./'+file),raw=readFileSync(resolve(here,'rh_target.txt'),'utf8');
   const rows=proofRows(module[name].prepare(raw),method),index=Number(process.argv[emit+1]||0);
   assert(rows[index],'unknown theorem index');process.stdout.write(JSON.stringify(certificate(rows[index].raw))+'\n');
 }else{
   const result=await auditGroup(group),text=JSON.stringify(result,null,2)+'\n',out=process.argv.indexOf('--output');
   if(out>=0){assert(process.argv[out+1],'missing output path');writeFileSync(process.argv[out+1],text)}
   else process.stdout.write(text);
 }
}
