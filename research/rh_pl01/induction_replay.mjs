// RH-PL-10: expanded replay of both large graph-predicate induction instances.
import {kernel} from './kernel.mjs';
import {induction} from './induction.mjs';
import {readFileSync} from 'node:fs';
const p=induction.prepare(readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8')),ar=p.ar;
const k=kernel;
const cases=[['no_zero_denominator',ar.neg(p.at(8,0,4))],['graph_agreement',ar.intern(k.Q(33,k.Q(34,k.I(k.A(k.M(33,1),k.A(k.M(34,1),k.A(ar.ast(p.at(8,0,33)),ar.ast(p.at(5,0,34))))),k.E(33,34)))))]];
for(const [name,phi] of cases){
 const root=p.close(p.prove(phi).source0),r=p.replay(root,80000000);
 if(!r.original)throw Error('not replayed');
 console.log(JSON.stringify({name,...r.cost,original_kernel_replay:r.original,root_bytes:ar.nodes[root.f].u}));
}
