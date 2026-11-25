// RH-PL-08: propositional proof templates and actual frozen definition interfaces.
import {kernel} from './kernel.mjs';
import {spine} from './spine.mjs';
import {assembler} from './assembler.mjs';
function buildInterfaces(k,sp,a){
 const {E,M,N,I,Q,A,encode,decode,free,axiom}=k;
 const eq=(x,y)=>encode(x)===encode(y);
 function assert(ok,msg){if(!ok)throw Error(msg)}
 function finish(lines,target){
   const out=a.book();for(const l of lines)out.add(l);
   const idx=out.lines.findIndex(l=>eq(l,target));assert(idx>=0,'target not found');
   const proof=out.lines.slice(0,idx+1);
   assert(a.verifyOpen(proof,target),'kernel rejected template');
   return {lines:proof,target};
 }
 function explosion(p,q){
   const h=N(p),c=I(N(q),h),K=I(h,c),C=I(c,I(p,q));
   const d=a.discharge(h,[h,K,c,C,I(p,q)],I(p,q));
   return finish(d.lines,d.target);
 }
 function dne(p){
   const h=N(N(p)),g=N(p),v=N(h),e=explosion(g,v);
   const imp=I(g,v),C=I(imp,I(h,p));
   const local=a.discharge(h,[h,e.target,imp,C,I(h,p),p],p,[e.target]);
   return finish([...e.lines,...local.lines],I(h,p));
 }
 function dni(p){
   const q=N(N(p)),d=dne(N(p)),C=I(d.target,I(p,q));
   return finish([...d.lines,C,I(p,q)],I(p,q));
 }
 function elim(p,q,left){
   const r=I(p,N(q)),h=N(r),goal=left?p:q,neg=N(goal),D=dni(r);
   const first=left?explosion(p,N(q)):{lines:[I(neg,r)],target:I(neg,r)};
   const L=a.discharge(neg,[neg,first.target,r,D.target,N(h)],N(h),[first.target,D.target]);
   const C=I(L.target,I(h,goal));
   return finish([...first.lines,...D.lines,...L.lines,C,I(h,goal)],I(A(p,q),goal));
 }
 const P=M(0,0),R=M(1,1),left=elim(P,R,true),right=elim(P,R,false);
 function instantiate(template,p,q){
   function walk(f){
     if(eq(f,P))return p;if(eq(f,R))return q;
     if(f[0]==='n')return N(walk(f[1]));
     if(f[0]==='i')return I(walk(f[1]),walk(f[2]));
     throw Error('unexpected template atom');
   }
   return {lines:template.lines.map(walk),target:walk(template.target)};
 }
 function split(d){
   assert(d[0]==='n'&&d[1][0]==='i'&&d[1][2][0]==='n','not expanded conjunction');
   return [d[1][1],d[1][2][1]];
 }
 function join(root,middle,last,lines){
   const ab=I(root,middle),bc=I(middle,last),abc=I(root,bc),ac=I(root,last);
   const K=I(bc,abc),S=I(abc,I(ab,ac));
   return finish([...lines,K,abc,S,I(ab,ac),ac],ac);
 }
 function closeNine(proof,vars){
   let target=proof.target;for(const x of vars.slice().reverse())target=Q(x,target);
   const lines=a.wrapBody(target,proof.lines);
   return {target,lines};
 }
 function run(raw){
   const F=decode(raw.slice(0,-1));assert(encode(F)+'\n'===raw,'target');
   const {vars,hypothesis:D}=a.stripPrefix(F);
   const [omega,tail]=split(D),[zeroInOmega,tail2]=split(tail);
   // Check actual expanded definition interfaces, no RH assertion.
   const first=instantiate(left,omega,tail);
   const omegaProof=closeNine(first,vars);
   const tailProof=instantiate(right,omega,tail);
   const secondLocal=instantiate(left,zeroInOmega,tail2);
   const second=join(D,tail,zeroInOmega,[...tailProof.lines,...secondLocal.lines]);
   const zeroProof=closeNine(second,vars);
   const clauses=[];let remainder=D;
   // The compiler's and() is right-associated. The exact number of
   // top-level conjuncts is fixed by the pinned compiler, since a final
   // conjunct can itself have conjunction syntax.
   for(let i=0;i<21;i++){const [p,q]=split(remainder);clauses.push(p);remainder=q}
   clauses.push(remainder);
   // Rebuild the declared top-level conjunction exactly.
   assert(eq(clauses.reduceRight((p,q)=>A(q,p)),D),'definition reconstruction');
   const small=[];
   for(const [name,t] of [['left',left],['right',right]]){
     assert(a.verifyOpen(t.lines,t.target),'template rejected');
     small.push({name,...a.cost(t.lines)});
   }
   // Check meta-substitution on a set of small arbitrary quantified
   // formulas too, using the original checker.
   const pool=[P,R,E(0,0),N(R),Q(0,M(0,1)),I(P,R)];
   let substitutionChecks=0;
   for(const p of pool)for(const q of pool)for(const t of [left,right]){
     const z=instantiate(t,p,q);assert(a.verifyOpen(z.lines,z.target),'instantiated template');substitutionChecks++;
   }
   return {top_level_definition_clauses:clauses.length,clause_sizes:clauses.map((f,i)=>({index:i,unary:encode(f).length,compact:sp.compact(f).length})),
     templates:small,meta_substitution_checks:substitutionChecks,
     actual_interfaces:[{name:'Definitions imply least-inductive Omega',...a.cost(omegaProof.lines),target_unary:encode(omegaProof.target).length,target_compact:sp.compact(omegaProof.target).length},{name:'Definitions imply zero belongs to Omega',...a.cost(zeroProof.lines),target_unary:encode(zeroProof.target).length,target_compact:sp.compact(zeroProof.target).length}],
     actual_rh_proof:false};
 }
 return {explosion,dne,dni,elim,instantiate,split,join,run};
}
export const interfaces=buildInterfaces(kernel,spine,assembler);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/interfaces.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(interfaces.run(raw),null,2));
}
