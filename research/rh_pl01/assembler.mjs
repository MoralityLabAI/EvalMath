// RH-PL-08: checked Hilbert deduction and dependency-proof assembly.
import {kernel} from './kernel.mjs';
import {spine} from './spine.mjs';
function buildAssembler(k,sp){
 const {E,M,I,Q,encode,decode,axiom,free,subst}=k;
 const eq=(a,b)=>encode(a)===encode(b);
 function assert(ok,msg){if(!ok)throw Error(msg)}
 function book(hypotheses=[],imports=[]){
   const seen=new Map(),incoming=new Map(),lines=[];
   const H=new Set(hypotheses.map(encode)),T=new Set(imports.map(encode));
   const blocked=new Set(hypotheses.flatMap(f=>[...free(f)]));
   function insert(f){
     const s=encode(f);seen.set(s,f);lines.push(f);
     if(f[0]==='i'){const dest=encode(f[2]);const arr=incoming.get(dest)||[];arr.push(f);incoming.set(dest,arr)}
   }
   // Imports are already-derived theorems, not local hypotheses.
   // They must be justified separately by the caller's checked DAG.
   for(const f of imports)insert(f);
   function classify(f){
     const s=encode(f);
     if(H.has(s))return {rule:'hypothesis'};
     if(T.has(s))return {rule:'import'};
     if(axiom(f))return {rule:'axiom'};
     if(f[0]==='a'&&!blocked.has(f[1])&&seen.has(encode(f[2])))return {rule:'gen',premise:f[2]};
     const imp=(incoming.get(s)||[]).find(a=>seen.has(encode(a[1])));
     if(imp)return {rule:'mp',antecedent:imp[1],imp};
     if(seen.has(s))return {rule:'repeat'};
     throw Error('unjustified line: '+s.slice(0,80));
   }
   function add(f){
     const r=classify(f);
     if(!seen.has(encode(f)))insert(f);
     return r;
   }
   return {seen,lines,add,has:f=>seen.has(encode(f))};
 }
 function closeFree(lines,target){
   assert(lines.length>0&&eq(lines.at(-1),target),'closure target');
   const out=lines.slice();let t=target;
   const xs=[...free(t)].sort((a,b)=>b-a);
   for(const x of xs){t=Q(x,t);out.push(t)}
   return {lines:out,target:t};
 }
 function proofText(lines,enc=encode){return lines.map(enc).join('\n')+'\n'}
 function verifyOpen(lines,target){
   const c=closeFree(lines,target);
   return k.verify(proofText(c.lines),encode(c.target));
 }
 function trim(lines,target){
   const idx=lines.findIndex(f=>eq(f,target));
   assert(idx>=0,'target absent');return lines.slice(0,idx+1);
 }
 // Checked Hilbert deduction theorem. Local input may depend on one
 // hypothesis H and explicitly listed imported theorems. The returned
 // derivation is unconditional relative to the very same imports.
 function discharge(H,input,target,imports=[]){
   const before=book([H],imports),out=book([],imports);
   assert(input.length>0&&eq(input.at(-1),target),'input target');
   function add(...fs){for(const f of fs)out.add(f)}
   function identity(P){
     const pp=I(P,P),a=I(P,I(pp,P)),b=I(P,pp);
     add(a,b,I(a,I(b,pp)),I(b,pp),pp);
   }
   // An import may not have appeared as an explicit input line before
   // MP uses it. Pre-lift every declared import; in DAG assembly all
   // imported theorems must independently exist.
   for(const f of imports){add(I(f,I(H,f)),I(H,f))}
   for(const f of input){
     const r=before.add(f),hf=I(H,f);
     if(out.has(hf))continue;
     if(r.rule==='hypothesis'){identity(H);continue}
     if(r.rule==='axiom'||r.rule==='import'){add(f,I(f,hf),hf);continue}
     if(r.rule==='mp'){
       const a=r.antecedent,ha=I(H,a),hi=I(H,r.imp);
       assert(out.has(ha)&&out.has(hi),'missing lifted MP premise');
       add(I(hi,I(ha,hf)),I(ha,hf),hf);continue;
     }
     if(r.rule==='gen'){
       const x=f[1],hpre=I(H,r.premise),g=Q(x,hpre);
       assert(out.has(hpre)&&!free(H).has(x),'generalization side condition');
       add(g,I(g,hf),hf);continue;
     }
     throw Error('unlifted repeated line');
   }
   const result=I(H,target),local=out.lines.slice(imports.length);
   // A declared import could already equal result. Represent that fact
   // with a local repeat; the assembler checks the imported proof.
   if(!local.some(f=>eq(f,result)))local.push(result);
   return {lines:trim(local,result),target:result};
 }
 // Exact checked union of dependency proofs. No chunk may rely on a
 // theorem outside its declared direct dependencies; the entire
 // expanded proof is checked again by the original kernel.
 function assemble(chunks,root){
   const byId=new Map();
   for(const c of chunks){assert(!byId.has(c.id),'duplicate chunk');byId.set(c.id,c)}
   const active=new Set(),finished=new Map(),order=[],global=book();
   let naiveLines=0,naiveUnary=0,naiveCompact=0;
   function visit(id){
     if(finished.has(id))return finished.get(id);
     assert(!active.has(id),'dependency cycle');active.add(id);
     const c=byId.get(id);assert(c,'missing chunk');
     assert(new Set(c.deps).size===c.deps.length,'duplicate dependency');
     const imports=c.deps.map(visit);
     assert(c.lines.length>0&&eq(c.lines.at(-1),c.target),'chunk conclusion mismatch');
     const local=book([],imports);
     for(const f of c.lines){local.add(f);global.add(f);naiveLines++;naiveUnary+=encode(f).length+1;naiveCompact+=sp.compact(f).length+1}
     assert(global.has(c.target),'global target missing');
     active.delete(id);finished.set(id,c.target);order.push(id);
     return c.target;
   }
   const target=visit(root),lines=trim(global.lines,target);
   assert(verifyOpen(lines,target),'original kernel rejected assembled proof');
   return {target,lines,order,naiveLines,naiveUnary,naiveCompact};
 }
 function stripPrefix(f){
   const vars=[];let body=f;
   while(body[0]==='a'){vars.push(body[1]);body=body[2]}
   assert(body[0]==='i','target shape');
   return {vars,body,hypothesis:body[1],claim:body[2]};
 }
 function wrapBody(f,lines){
   const {vars,body}=stripPrefix(f);
   assert(verifyOpen(lines,body),'invalid body proof');
   const out=book();for(const l of lines)out.add(l);
   let t=body;
   for(const x of vars.slice().reverse()){t=Q(x,t);out.add(t)}
   assert(eq(t,f),'target mismatch');
   const proof=trim(out.lines,f);
   assert(k.verify(proofText(proof),encode(f)),'wrapped proof rejected');
   return proof;
 }
 function cost(lines){
   return {lines:lines.length,unary:proofText(lines).length,compact:proofText(lines,sp.compact).length};
 }
 function run(raw){
   const target=decode(raw.slice(0,-1));
   assert(encode(target)+'\n'===raw&&!free(target).size,'target roundtrip');
   const {vars,body,hypothesis:D,claim:C}=stripPrefix(target);
   assert(vars.length===9,'expected nine binders');
   const prefix=[];let f=body;
   for(const x of vars.slice().reverse()){f=Q(x,f);prefix.push(f)}
   const overhead=cost(prefix);
   const R=E(0,0),P=M(0,0),A=Q(0,R),B=Q(1,A);
   const id=discharge(P,[P],P);
   assert(verifyOpen(id.lines,id.target),'identity');
   const mp=discharge(P,[P,R,I(R,I(P,R)),I(P,R),R],R);
   assert(verifyOpen(mp.lines,mp.target),'MP control');
   // Explicit nontrivial MP using H as an antecedent:
   const K=I(P,I(R,P));
   const mp2=discharge(P,[P,K,I(R,P),R,P],P);
   assert(verifyOpen(mp2.lines,mp2.target),'lifted MP');
   const H=E(0,0), G=Q(1,H);
   const gen=discharge(H,[H,G],G);
   assert(verifyOpen(gen.lines,gen.target),'lifted generalization');
   // Actual DAG: first branch universally closes R, second branch
   // derives A -> R using R and K. A third branch derives a quantified
   // implication from R; root derives B from A and then discharges
   // via a genuinely checked lemma. Repeated R lines are deduplicated.
   const K1=I(R,I(A,R)),K2=I(R,I(B,R));
   const chunks=[
     {id:'base',deps:[],lines:[R],target:R},
     {id:'a',deps:['base'],lines:[R,A],target:A},
     {id:'bridge',deps:['base'],lines:[R,K1,I(A,R)],target:I(A,R)},
     {id:'other',deps:['base'],lines:[R,K2,I(B,R)],target:I(B,R)},
     {id:'root',deps:['a','bridge','other'],lines:[R,A,B],target:B},
   ];
   const dag=assemble(chunks,'root');
   assert(dag.naiveUnary>=cost(dag.lines).unary,'dag costs');
   // Exact RH payload calibration: use the complete Definitions AST
   // to prove a tautological control with the same nine binder prefix.
   // The true Claim is deliberately NOT replaced in the frozen target.
   const ctrl=discharge(D,[D],D);
   let ctrlTarget=ctrl.target;
   for(const x of vars.slice().reverse())ctrlTarget=Q(x,ctrlTarget);
   const ctrlProof=wrapBody(ctrlTarget,ctrl.lines);
   const ctrlCost=cost(ctrlProof);
   assert(k.verify(proofText(ctrlProof),encode(ctrlTarget)),'full-payload control');
   // Exact frozen-target tautology; a theorem of pure logic, not RH.
   const frozenIdentity=discharge(target,[target],target);
   assert(k.verify(proofText(frozenIdentity.lines),encode(frozenIdentity.target)),'frozen identity');
   // Negative controls.
   const bads=[
     ()=>discharge(P,[P,Q(0,P)],Q(0,P)), // illegal generalization
     ()=>discharge(P,[R,M(1,1)],M(1,1)), // unjustified line
     ()=>assemble([{id:'bad',deps:[],lines:[P],target:P}],'bad'),
     ()=>assemble([{id:'bad',deps:['absent'],lines:[R],target:R}],'bad'),
     ()=>assemble([{id:'x',deps:['y'],lines:[R],target:R},{id:'y',deps:['x'],lines:[R],target:R}],'x'),
     ()=>assemble([{id:'x',deps:[],lines:[R],target:A}],'x'),
     ()=>assemble([{id:'base',deps:[],lines:[R],target:R},{id:'a',deps:[],lines:[A],target:A}],'a'),
     ()=>wrapBody(target,[R]),
     ()=>assemble([{id:'x',deps:[],lines:[R],target:R},{id:'x',deps:[],lines:[R],target:R}],'x')
   ];
   let rejected=0;for(const bad of bads){let ok=false;try{bad()}catch{ok=true}assert(ok,'negative accepted');rejected++}
   // Parametric controls: generated valid local derivations involving
   // assumptions, MP and quantification, checked by the original kernel.
   const pool=[P,R,M(0,1),M(1,2),I(P,R),Q(0,P),E(2,2),Q(1,M(0,1))];
   let lifted=0,totalBytes=0;
   for(const h of pool)for(const g of pool){
     const K=I(h,I(g,h));
     const steps=[h,K,I(g,h)];
     const result=discharge(h,steps,I(g,h));
     assert(verifyOpen(result.lines,result.target),'parametric MP');lifted++;totalBytes+=cost(result.lines).unary;
     for(let x=0;x<3;x++)if(!free(h).has(x)){
       const end=Q(x,I(g,h)),res=discharge(h,[...steps,end],end);
       assert(verifyOpen(res.lines,res.target),'parametric generalization');lifted++;totalBytes+=cost(res.lines).unary;
     }
   }
   return {target_blob:raw.length,outer_binders:vars,body:{unary:encode(body).length,compact:sp.compact(body).length},
     definitions:{unary:encode(D).length,compact:sp.compact(D).length},claim:{unary:encode(C).length,compact:sp.compact(C).length},
     wrapper_overhead:overhead,full_payload_control:ctrlCost,frozen_target_identity:cost(frozenIdentity.lines),
     modular_control:{order:dag.order,naive_lines:dag.naiveLines,naive_unary:dag.naiveUnary,naive_compact:dag.naiveCompact,assembled:cost(dag.lines)},
     small_controls:{identity:cost(id.lines),mp:cost(mp.lines),mp2:cost(mp2.lines),gen:cost(gen.lines)},
     parametric_checked:lifted,parametric_unary_bytes:totalBytes,negative_rejected:rejected,actual_rh_proof:false};
 }
 return {book,verifyOpen,discharge,assemble,stripPrefix,wrapBody,cost,run};
}
export const assembler=buildAssembler(kernel,spine);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/assembler.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(assembler.run(raw),null,2));
}
