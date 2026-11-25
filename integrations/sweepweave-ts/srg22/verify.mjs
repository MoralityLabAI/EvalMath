import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as r18 from '../srg18/benchmark.mjs';
import * as r20 from '../srg20/benchmark.mjs';
import * as r21 from '../srg21/benchmark.mjs';
import {run} from './benchmark.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../../../output/evaluation_storyworld_reasoning/'+p,import.meta.url),'utf8'));
const expected=read('srg22_directed_geometry.json'),actual=run(r18,r20,r21,read('srg21_dirac_audit.json'));
function cmp(a,b,k='root'){if(typeof a==='number'&&typeof b==='number'&&(!Number.isInteger(a)||!Number.isInteger(b))){assert.ok(Math.abs(a-b)<=1e-8*Math.max(1,Math.abs(b)),k);return}if(a&&b&&typeof a==='object'&&typeof b==='object'){assert.deepEqual(Object.keys(a),Object.keys(b));for(const key of Object.keys(a))cmp(a[key],b[key],k+'.'+key)}else assert.deepEqual(a,b,k)}
cmp(actual,expected);console.log(JSON.stringify({status:'pass',gate:actual.gate,promote:actual.promote},null,2));
