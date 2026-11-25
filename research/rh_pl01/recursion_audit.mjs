// RH-PL-13: independent replay of each portable recursion certificate.
import {kernel} from './kernel.mjs';
import {gluing} from './gluing.mjs';
import {recursionExistence} from './recursion_existence.mjs';
import {prefixFamily} from './prefix_family.mjs';
import {certificate,verifyCertificate} from './joint_audit.mjs';
import {readFileSync} from 'node:fs';
const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
const which=process.argv[2]||'existence';
let proof;
if(which==='union'||which==='glue')proof=gluing.prepare(raw).cert(which);
else if(which==='family')proof=prefixFamily.prepare(raw).raw;
else if(which==='existence')proof=recursionExistence.prepare(raw).raw;
else throw Error('unknown proof');
const cert=certificate(proof);
if(process.argv.includes('--emit'))process.stdout.write(JSON.stringify(cert)+'\n');
else console.log(JSON.stringify({...verifyCertificate(kernel,cert),certificate_json_bytes:JSON.stringify(cert).length},null,2));
