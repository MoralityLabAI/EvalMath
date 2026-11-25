// RH-PL-17: deterministic verifier-instrument calibration for the gym preflight.
// Four prerequisite certificates belong to one shared construction family.
import {kernel} from './kernel.mjs';
import {pairs} from './pairs.mjs';
import {certificate,verifyCertificate} from './joint_audit.mjs';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {dirname,relative,resolve} from 'node:path';

const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../..');
const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
const hash=(kind,data)=>createHash(kind).update(data).digest('hex'),sha=data=>hash('sha256',data);
const unit='rh-prefix-recurrence-family';
const frozen={
 'kernel.mjs':'35da89e237ecbd1a807ade3fffb39ffd57890ace',
 'rh_target.txt':'a55f16f293a784ca91d9d52d65cbaea1e89f80dc',
 'rh_target_compact.txt':'98fb1ce81784556af2f6dff8d0d6b31d9c69d7e5'
};
// Anchors from the initial instrument measurements. Every certificate is
// regenerated and checked before its identity is compared with this record.
const certificateAnchors={
 ordered_pair_exists:'cbbf27a5c3f6e3182a4e61614731c84f958b1c43dce5b88908d0790baa159e49',
 ordered_pair_injectivity:'fbbb1db4b95e07dfac5beef4710f0ddb1ec8faf1bee75c0c1e27521ba3feae72',
 ordered_pair_double_power_bound:'f5e81c2462e232e3f1567e85ac5c3d208fe596ade57e6f4c7d69eeb8d3a76890',
 singleton_graph_application:'99983f15ad4120c79d46a7e06ae6268eadd16daf4bfeb0a04c37a24d4433aef6'
};

function frozenBlobs(){
 return Object.fromEntries(Object.entries(frozen).map(([name,expected])=>{
   const data=readFileSync(resolve(here,name)),actual=hash('sha1',Buffer.concat([Buffer.from('blob '+data.length+'\0'),data]));
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
 for(const file of ['gym_preflight.mjs','pairs_receipt.json',...Object.keys(frozen)])visit(resolve(here,file));
 for(const file of ['scripts/prepare_rh_compactification_preflight.py',
   'skills/evalmath-mechinterp-power/scripts/preflight.py','skills/evalmath-mechinterp-power/SKILL.md'])visit(resolve(repo,file));
 return Object.fromEntries([...paths].sort().map(path=>[relative(repo,path),sha(readFileSync(path))]));
}

export function calibrateGymInstrument(){
 const frozen_blobs=frozenBlobs(),raw=readFileSync(resolve(here,'rh_target.txt'),'utf8');
 const prior=JSON.parse(readFileSync(resolve(here,'pairs_receipt.json'),'utf8'));
 assert(prior.target_git_blob===frozen_blobs['rh_target.txt'],'pair receipt target identity');
 const proofs=pairs.prepare(raw).run();
 assert(proofs.length===4,'expected four prerequisite certificates');
 const observations=proofs.map(proof=>{
   const theorem=proof.receipt.name,stored=prior.rows.find(row=>row.name===theorem);
   assert(stored&&Object.hasOwn(certificateAnchors,theorem),'unexpected prerequisite theorem');
   assert(proof.receipt.original_full_replay===true,'original pair checker replay');
   const serialized=JSON.stringify(certificate(proof.raw));
   const repeatedSerialization=JSON.stringify(certificate(proof.raw));
   assert(serialized===repeatedSerialization,'certificate emission is not identical');
   const first=verifyCertificate(kernel,JSON.parse(serialized));
   const repeat=verifyCertificate(kernel,JSON.parse(repeatedSerialization));
   assert(JSON.stringify(first)===JSON.stringify(repeat),'repeated replay changed');
   assert(JSON.stringify(first)===JSON.stringify(stored.independent_replay),'prior pair replay changed');
   assert(String(proof.receipt.lines)===String(first.lines)&&String(proof.receipt.unary)===first.unary&&String(proof.receipt.compact)===first.compact,'producer and replay counts differ');
   assert(Buffer.byteLength(serialized)===stored.certificate_json_bytes,'prior certificate byte count changed');
   const certificate_sha256=sha(serialized);
   assert(certificate_sha256===certificateAnchors[theorem],'initial certificate identity changed');
   return {theorem,first,repeat,certificate_sha256};
 });
 const firstPasses=observations.length,repeatPasses=observations.length;
 return {schema:'EvalMath/rh-compactification-instrument-calibration/v1',
   evidence_level:'deterministic verifier instrument calibration only',
   unit_id:unit,construction_families:1,units_independent:false,
   observation_count:observations.length,certificate_replay_calls:2*observations.length,
   observation_units:Object.fromEntries(observations.map(row=>[row.theorem,unit])),
   observations,instrument_paired_completion_delta:String((repeatPasses-firstPasses)/observations.length),
   neural_model_run:false,neural_effect_estimate:null,causal_sham_calibrated:false,
   heldout_sealed:false,confirmation_allocated:false,confirmation_data_opened:false,
   scope:'Four prerequisite certificates are repeated observations within one shared RH construction family. Identity replay calibrates the verifier instrument only; it does not estimate a neural loop effect or calibrate a causal sham distribution.',
   checks:{genuine_certificates_regenerated:true,original_pair_checker_replays:true,
     each_certificate_replayed_twice:true,certificate_serializations_identical:true,
     replay_results_identical:true,initial_measurements_preserved:true,
     producer_counts_match:true,prior_receipt_matches:true,frozen_files_match:true},
   frozen_blobs,source_sha256:sourceHashes()};
}
if(typeof process!=='undefined'&&process.argv[1]===fileURLToPath(import.meta.url)){
 const result=calibrateGymInstrument(),text=JSON.stringify(result,null,2)+'\n',output=process.argv.indexOf('--output');
 if(output>=0){
   assert(process.argv[output+1],'missing output path');const path=resolve(process.argv[output+1]);
   mkdirSync(dirname(path),{recursive:true});writeFileSync(path,text);
 }else process.stdout.write(text);
}
