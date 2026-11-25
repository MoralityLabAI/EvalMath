import fs from 'node:fs';
import assert from 'node:assert/strict';
import {verify,auditAuthored,REAL} from './certificate.mjs';
const root=new URL('../../../',import.meta.url);
const expected=JSON.parse(fs.readFileSync(new URL('output/evaluation_storyworld_reasoning/srg_ac01_authoring_certificate.json',root),"utf8"));
const [cmd,file,...extra]=process.argv.slice(2);
if(extra.length)throw Error("verify | audit <SWMD source>");
if(cmd==="verify"&&!file){
 assert.deepEqual(verify(),expected.cubes,"cube receipt drift");
 for(const {path,...e} of expected.real)assert.deepEqual(auditAuthored(fs.readFileSync(new URL(path,root),"utf8"),e.contract),e,"authored receipt drift "+path);
 console.log(JSON.stringify({status:"pass",fixtures:expected.cubes.fixtures,roots:expected.cubes.roots,edges:expected.cubes.edges,worlds:expected.real.map(w=>({world:w.world,probes:w.probes,invalid:w.invalid}))},null,2));
}else if(cmd==="audit"&&file){
 console.log(JSON.stringify(auditAuthored(fs.readFileSync(file,"utf8"),REAL),null,2));
}else throw Error("verify | audit <SWMD source>; audit defaults to the Reservoir Dogs target contract");
