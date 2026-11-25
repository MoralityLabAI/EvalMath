// RH-PL-14: reproduce independent proof-certificate verification.
import {kernel} from './kernel.mjs';
import {pairs} from './pairs.mjs';
import {prefixBase} from './prefix_base.mjs';
import {prefixFamily} from './prefix_family.mjs';
import {append} from './append.mjs';
import {certificate,verifyCertificate} from './joint_audit.mjs';
import {readFileSync} from 'node:fs';
const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
const which=process.argv[2]||'pairs';
let proofs;
if(which==='pairs')proofs=pairs.prepare(raw).run();
else if(which==='base'){
 const out=prefixBase.prepare(raw), family=prefixFamily.prepare(raw);
 let body=kernel.decode(family.raw.target);
 while(body[0]==='a')body=body[2];
 for(let i=0;i<3;i++){if(body[0]!=='n'||body[1][0]!=='a'||body[1][2][0]!=='n')throw Error('family shape');body=body[1][2][1];}
 function split(f){if(f[0]!=='n'||f[1][0]!=='i'||f[1][2][0]!=='n')throw Error('conjunction');return [f[1][1],f[1][2][1]]}
 if(kernel.encode(split(split(body)[1])[1])!==out.famSpec)throw Error('family predicate drift');
 proofs=[out];
}else if(which==='append')proofs=append.prepare(raw).run();
else throw Error('unknown theorem group');
const emit=process.argv.indexOf('--emit');
if(emit>=0){
 const index=Number(process.argv[emit+1]||0);if(!proofs[index])throw Error('unknown theorem index');
 process.stdout.write(JSON.stringify(certificate(proofs[index].raw))+'\n');
}else console.log(JSON.stringify(proofs.map(p=>{const cert=certificate(p.raw);return {name:p.receipt.name,...verifyCertificate(kernel,cert),certificate_json_bytes:JSON.stringify(cert).length}}),null,2));
