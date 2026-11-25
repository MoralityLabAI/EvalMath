// RH-PL-10: checked separation-to-induction compiler using the frozen omega clause.
import {kernel} from './kernel.mjs';
import {spine} from './spine.mjs';
import {assembler} from './assembler.mjs';
import {interfaces} from './interfaces.mjs';
import {compression} from './compression.mjs';
function buildInduction(k,sp,a,it,c){
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 function prepare(raw){
 const prep=c.prepare(raw),ar=prep.ar,ns=ar.nodes,{intern,ast,imp,neg,gen}=ar;
 const E=(x,y)=>intern(k.E(x,y)),M=(x,y)=>intern(k.M(x,y)),A=(p,q)=>neg(imp(p,neg(q))),F=(p,q)=>A(imp(p,q),imp(q,p)),O=(p,q)=>imp(neg(p),q),X=(x,p)=>neg(gen(x,neg(p)));
 const fvCache=new Map(),subCache=new Map();
 function fv(f){if(fvCache.has(f))return fvCache.get(f);const n=ns[f];let v;if(n.tag==='e'||n.tag==='m')v=new Set([n.x,n.y]);else if(n.tag==='n')v=fv(n.x);else if(n.tag==='i')v=new Set([...fv(n.x),...fv(n.y)]);else{v=new Set(fv(n.y));v.delete(n.x)}fvCache.set(f,v);return v}
 function sub(f,x,t){if(x===t||!fv(f).has(x))return f;const key=f+':'+x+':'+t;if(subCache.has(key))return subCache.get(key);const n=ns[f];let z;if(n.tag==='e'||n.tag==='m')z=(n.tag==='e'?E:M)(n.x===x?t:n.x,n.y===x?t:n.y);else if(n.tag==='n')z=neg(sub(n.x,x,t));else if(n.tag==='i')z=imp(sub(n.x,x,t),sub(n.y,x,t));else{assert(n.x!==t,'capture');z=gen(n.x,sub(n.y,x,t))}subCache.set(key,z);return z}
 const split=f=>{const n=ns[f];assert(n.tag==='n'&&ns[n.x].tag==='i'&&ns[ns[n.x].y].tag==='n','not conjunction');return [ns[n.x].x,ns[ns[n.x].y].x]};
 function exParts(f){const n=ns[f];assert(n.tag==='n'&&ns[n.x].tag==='a'&&ns[ns[n.x].y].tag==='n','not exists');const q=ns[n.x];return [q.x,ns[q.y].x]}
 function qAt(f,t){const n=ns[f];assert(n.tag==='a','not universal');return sub(n.y,n.x,t)}
 function exAt(f,t){const [x,b]=exParts(f);return sub(b,x,t)}
 let pid=0;const axCache=new Map(),mpCache=new Map(),genCache=new Map(),absCache=new Map(),templateCache=new Map(),hypRegistry=new Map();
 function node(f,rule,parents,deps,detail){return {id:++pid,f,rule,parents,deps,detail}}
 function hyp(f){const p=node(f,'hyp',[],null);p.deps=new Set([p.id]);hypRegistry.set(p.id,f);return p}
 function ax(f){if(axCache.has(f))return axCache.get(f);const name=ar.prop(f)?'prop':k.axiom(ast(f));assert(name,'not an axiom: '+k.encode(ast(f)).slice(0,140));const p=node(f,'ax',[],new Set(),name);axCache.set(f,p);return p}
 function mp(p,q){const n=ns[q.f];assert(n.tag==='i'&&n.x===p.f,'MP mismatch');const key=p.id+':'+q.id;if(mpCache.has(key))return mpCache.get(key);const r=node(n.y,'mp',[p,q],new Set([...p.deps,...q.deps]));mpCache.set(key,r);return r}
 function generalize(x,p){assert([...p.deps].every(h=>!fv(hypRegistry.get(h)).has(x)),'generalization variable occurs in hypothesis');const key=x+':'+p.id;if(genCache.has(key))return genCache.get(key);const r=node(gen(x,p.f),'gen',[p],new Set(p.deps),x);genCache.set(key,r);return r}
 function identity(f){const pp=imp(f,f),u=ax(imp(f,imp(pp,f))),v=ax(imp(f,pp));const s=ax(imp(u.f,imp(v.f,pp)));return mp(v,mp(u,s))}
 function lift(h,p){return mp(p,ax(imp(p.f,imp(h,p.f))))}
 function abs(h,p){
   const key=h.id+':'+p.id;if(absCache.has(key))return absCache.get(key);
   let r;
   if(!p.deps.has(h.id))r=lift(h.f,p);
   else if(p===h)r=identity(h.f);
   else if(p.rule==='mp'){
     const [u,v]=p.parents,hu=abs(h,u),hv=abs(h,v),out=imp(h.f,p.f);
     r=mp(hu,mp(hv,ax(imp(hv.f,imp(hu.f,out)))));
   }else if(p.rule==='gen'){
     const x=p.detail,hh=abs(h,p.parents[0]),g=generalize(x,hh);
     r=mp(g,ax(imp(g.f,imp(h.f,p.f))));
   }else throw Error('unexpected abstraction dependency');
   assert(!r.deps.has(h.id)&&r.f===imp(h.f,p.f),'discharge failure');absCache.set(key,r);return r;
 }
 function comp(p,q){
   const l=ns[p.f],r=ns[q.f];assert(l.tag==='i'&&r.tag==='i'&&l.y===r.x,'composition mismatch');
   const u=mp(q,ax(imp(q.f,imp(l.x,q.f))));return mp(p,mp(u,ax(imp(u.f,imp(p.f,imp(l.x,r.y))))));
 }
 // Import the already checked purely propositional templates, substituting
 // exact arbitrary ASTs for the two atomic placeholders.
 const p0=intern(k.M(0,0)),q0=intern(k.M(1,1));
 const templates={left:it.elim(k.M(0,0),k.M(1,1),true).lines.map(intern),right:it.elim(k.M(0,0),k.M(1,1),false).lines.map(intern),dne:it.dne(k.M(0,0)).lines.map(intern),dni:it.dni(k.M(0,0)).lines.map(intern)};
 function templ(name,p,q=p){
   const key=name+':'+p+':'+q;if(templateCache.has(key))return templateCache.get(key);const cache=new Map(),seen=new Map(),incoming=new Map();
   function rep(f){if(f===p0)return p;if(f===q0)return q;if(cache.has(f))return cache.get(f);const n=ns[f];let z;if(n.tag==='n')z=neg(rep(n.x));else if(n.tag==='i')z=imp(rep(n.x),rep(n.y));else throw Error('template atom');cache.set(f,z);return z}
   let last;
   for(const f0 of templates[name]){const f=rep(f0);if(seen.has(f)){last=seen.get(f);continue}if(ar.prop(f))last=ax(f);else{const v=(incoming.get(f)||[]).find(v=>seen.has(ns[v.f].x));assert(v,'template MP');last=mp(seen.get(ns[v.f].x),v)}
     seen.set(f,last);if(ns[f].tag==='i'){const d=ns[f].y,arr=incoming.get(d)||[];arr.push(last);incoming.set(d,arr)}}
   templateCache.set(key,last);return last;
 }
 const dne=p=>templ('dne',p),dni=p=>templ('dni',p);
 function contra(p){const n=ns[p.f];assert(n.tag==='i','contra');const d=comp(comp(dne(n.x),p),dni(n.y));return mp(d,ax(imp(d.f,imp(neg(n.y),neg(n.x)))))}
 function left(p){const [x,y]=split(p.f);return mp(p,templ('left',x,y))}
 function right(p){const [x,y]=split(p.f);return mp(p,templ('right',x,y))}
 function conj(p,q){const h=hyp(imp(p.f,neg(q.f))),r=abs(h,mp(p,h)),c=contra(r);return mp(mp(q,dni(q.f)),c)}
 function ui(p,t){const f=qAt(p.f,t);return mp(p,ax(imp(p.f,f)))}
 function renameU(p,target){
   if(p.f===target)return p;
   const n=ns[target];assert(n.tag==='a'&&qAt(p.f,n.x)===n.y&&!fv(p.f).has(n.x),'bad universal renaming');
   const h=hyp(p.f),ren=abs(h,generalize(n.x,ui(h,n.x)));assert(ns[ren.f].y===target,'renaming target');return mp(p,ren);
 }
 function introAt(p,t,target){assert(qAt(target,t)===p.f,'universal body mismatch');return renameU(generalize(t,p),target)}
 function exIntro(target,t,p){
   assert(exAt(target,t)===p.f,'existential body mismatch');
   const u=ns[target].x,l=ax(imp(u,neg(p.f))),r=contra(l);return mp(mp(p,dni(p.f)),r);
 }
 function exElim(p,t,h,r){
   const [x,b]=exParts(p.f);assert(sub(b,x,t)===h.f,'existential witness mismatch');
   assert(!fv(r.f).has(t)&&!fv(p.f).has(t),'eigenvariable in conclusion or existence');
   assert([...p.deps,...[...r.deps].filter(i=>i!==h.id)].every(i=>!fv(hypRegistry.get(i)).has(t)),'eigenvariable in other assumption');
   const hToR=abs(h,r),cc=contra(hToR),g=generalize(t,cc),dist=mp(g,ax(imp(g.f,imp(neg(r.f),gen(t,neg(h.f))))));
   let q=dist;
   const orig=ns[p.f].x;
   if(ns[q.f].y!==orig){const z=hyp(ns[q.f].y),bridge=abs(z,renameU(z,orig));q=comp(q,bridge)}
   const notNot=mp(p,contra(q));return mp(notNot,dne(r.f));
 }
 function emit(root){
   assert(root.deps.size===0,'undischarged hypotheses');const visited=new Set(),seq=[],stack=[[root,false]];
   while(stack.length){const [n,post]=stack.pop();if(visited.has(n.id))continue;if(post){visited.add(n.id);seq.push(n);continue}stack.push([n,true]);for(let i=n.parents.length-1;i>=0;i--)stack.push([n.parents[i],false])}
   // Independent replay of the restricted proof grammar at the formula-ID
   // level; deduplicate only exact lines. Each rule's actual parent proof
   // must be available. Nonpropositional axioms are checked by the original
   // axiom recognizer, not trusted labels.
   const seen=new Set(),ids=[],axioms=new Map();let mpCount=0,genCount=0;
   for(const n of seq){assert(n.deps.size===0,'local assumption escaped');if(seen.has(n.f))continue;
     if(n.rule==='ax'){const name=ar.prop(n.f)?'propositional':k.axiom(ast(n.f));assert(name,'replay axiom');axioms.set(name,(axioms.get(name)||0)+1)}
     else if(n.rule==='mp'){const [p,q]=n.parents;assert(seen.has(p.f)&&seen.has(q.f)&&ns[q.f].tag==='i'&&ns[q.f].x===p.f&&ns[q.f].y===n.f,'replay MP');mpCount++}
     else if(n.rule==='gen'){const p=n.parents[0];assert(seen.has(p.f)&&n.f===gen(n.detail,p.f),'replay generalization');genCount++}
     else throw Error('hypothesis in theorem');
     seen.add(n.f);ids.push(n.f);
   }
   // A root may already occur earlier as a line. Every earlier line is
   // valid and truncating at the first root preserves derivability.
   const cut=ids.indexOf(root.f);assert(cut>=0,'root');const out=ids.slice(0,cut+1);
   return {ids:out,cost:ar.cost(out),axioms:Object.fromEntries(axioms),mpCount,genCount};
 }
 function close(p,order=[...fv(p.f)].sort((a,b)=>a-b)){for(const x of order.slice().reverse())p=generalize(x,p);return p}
 function replay(p,cap){
   const r=emit(p);assert(fv(p.f).size===0,'open replay target');
   if(r.cost.unary>cap)return {...r,original:false};
   const proof=r.ids.map(x=>k.encode(ast(x))).join('\n')+'\n';assert(proof.length===r.cost.unary,'cost drift');
   assert(k.verify(proof,k.encode(ast(p.f))),'original kernel replay');return {...r,original:true};
 }
 const frozen=prep.frozen,{hypothesis:D}=a.stripPrefix(frozen),omega0=intern(it.split(D)[0]),omegaW=sub(omega0,0,1);
 const [indW,leastW]=split(omegaW);
 function prove(phi){
   assert(fv(phi).has(0)&&[2,20,21,22,23,24,25,26,27].every(v=>!fv(phi).has(v)),'predicate parameter collision');
   const P=x=>sub(phi,0,x),empty=(x)=>gen(23,neg(M(23,x))),succ=(x,y)=>gen(23,F(M(23,y),O(M(23,x),E(23,x))));
   const base=gen(20,imp(A(empty(20),M(20,1)),P(20)));
   const step=gen(21,gen(22,imp(A(M(21,1),A(M(22,1),A(succ(21,22),P(21)))),P(22))));
   const w=hyp(omegaW),b=hyp(base),s=hyp(step),iw=left(w),least=right(w);
   assert(iw.f===indW&&least.f===leastW,'omega extraction');
   const sepBody=gen(0,F(M(0,2),A(M(0,1),phi))),sep=ax(X(2,sepBody)),hs=hyp(sepBody);
   assert(sep.detail==='separation','wrong separation axiom');
   const sepFor=x=>ui(hs,x);
   const inSubset=(x,mw,px)=>mp(conj(mw,px),right(sepFor(x)));
   const inOmega=(x,ms)=>mp(ms,left(sepFor(x)));
   const leastAt=ui(least,2),indS=ns[leastAt.f].x,[zeroS,stepS]=split(indS);
   // Establish zero witness in the separated subset.
   const zw=left(iw),z=26,hz=hyp(exAt(zw.f,z)),ze=left(hz),zm=right(hz);
   const bz=ui(b,z),bPrem=ns[bz.f].x,[bEmpty,bMem]=split(bPrem);
   assert(zm.f===bMem,'base membership');const pz=mp(conj(renameU(ze,bEmpty),zm),bz),zs=inSubset(z,zm,pz);
   const [sEmpty,sMem]=split(exAt(zeroS,z));assert(zs.f===sMem,'separated zero membership');
   const zsEx=exIntro(zeroS,z,conj(renameU(ze,sEmpty),zs));
   const zeroProof=exElim(zw,z,hz,zsEx);
   // Establish successor closure of the separated subset.
   const x=24,y=25,stepBody=qAt(stepS,x),hx=hyp(ns[stepBody].x),both=inOmega(x,hx),mw=left(both),px=right(both);
   const wNext=mp(mw,ui(right(iw),x)),hy=hyp(exAt(wNext.f,y)),my=left(hy),sy=right(hy);
   const st=ui(ui(s,x),y),[xm,rest]=split(ns[st.f].x),[ym,tail]=split(rest),[ss,pp]=split(tail);
   assert(mw.f===xm&&my.f===ym&&px.f===pp,'step premise');
   const py=mp(conj(mw,conj(my,conj(renameU(sy,ss),px))),st);
   const ys=inSubset(y,my,py),targetEx=ns[stepBody].y,[tm,ts]=split(exAt(targetEx,y));assert(ys.f===tm,'successor membership');
   const nextEx=exIntro(targetEx,y,conj(ys,renameU(sy,ts)));
   const next=exElim(wNext,y,hy,nextEx),stepProof=introAt(abs(hx,next),x,stepS);
   const inductive=conj(zeroProof,stepProof);assert(inductive.f===indS,'inductive subset');
   const subWS=mp(inductive,leastAt),t=27,hm=hyp(M(t,1)),mt=mp(hm,ui(subWS,t)),pt=right(inOmega(t,mt));
   const goal=generalize(t,abs(hm,pt)),noWitness=exElim(sep,2,hs,goal);
   const result=abs(w,abs(b,abs(s,noWitness)));
   assert(result.deps.size===0&&result.f===imp(omegaW,imp(base,imp(step,gen(t,imp(M(t,1),P(t)))))),'induction root');
   const source0=ui(generalize(1,result),0);
   assert(ns[source0.f].x===omega0,'actual frozen omega antecedent');
   return {result,source0,base,step,goal:goal.f,sep:sep.f};
 }
 function importClosed(ids,root){
   const seen=new Map(),incoming=new Map();
   for(const f of ids){let p;if(ar.prop(f))p=ax(f);else if(ns[f].tag==='a'&&seen.has(ns[f].y))p=generalize(ns[f].x,seen.get(ns[f].y));else{const q=(incoming.get(f)||[]).find(v=>seen.has(ns[v.f].x));assert(q,'import proof');p=mp(seen.get(ns[q.f].x),q)}seen.set(f,p);if(ns[f].tag==='i'){const d=ns[f].y,l=incoming.get(d)||[];l.push(p);incoming.set(d,l)}}assert(seen.has(root),'import root');return seen.get(root)
 }
 function pair(p,x,y){const single=(s,x)=>gen(32,F(M(32,s),E(32,x))),double=(s,x,y)=>gen(32,F(M(32,s),O(E(32,x),E(32,y))));return gen(31,F(M(31,p),O(single(31,x),double(31,x,y))))}
 const at=(g,x,y)=>X(30,A(pair(30,x,y),M(30,g)));
 function run(){
   const cases=[['membership',M(0,4)],['no_zero_denominator',neg(at(8,0,4))],['graph_agreement',gen(33,gen(34,imp(A(M(33,1),A(M(34,1),A(at(8,0,33),at(5,0,34)))),E(33,34))))]];
   const rows=[];let originalReplays=0;
   for(const [name,phi] of cases){const p=prove(phi),root=close(p.source0),r=replay(root,24000000);if(r.original)originalReplays++;
      rows.push({name,predicate_bytes:ns[phi].u,separation_cost:ns[p.sep].u+1,separation_compact:ns[p.sep].c+1,conclusion_bytes:ns[root.f].u,...r.cost,axioms:r.axioms,original_kernel_replay:r.original});
   }
   // Compose an exact, open D->omega interface with the actual membership
   // induction instance, then close all remaining free variables.
   const q=prep.build('unary',[0],false),op=importClosed(q.ids,q.roots[0]),ind=prove(cases[0][1]),bridge=close(comp(op,ind.source0)),r=replay(bridge,24000000);
   if(r.original)originalReplays++;
   const bads=[()=>sub(gen(4,M(0,4)),0,4),()=>generalize(4,hyp(M(0,4))),()=>prove(M(0,2)),()=>{const e=X(26,M(26,1));const h=hyp(M(26,1));exElim(hyp(e),26,h,h)}];
   let rejected=0;for(const f of bads){let ok=false;try{f()}catch{ok=true}assert(ok,'negative accepted');rejected++}
   return {omega_exact_source_bytes:ns[omega0].u,instances:rows,definition_bridge:{...r.cost,original_kernel_replay:r.original},original_kernel_replays:originalReplays,negative_rejected:rejected,formula_nodes:ns.length-1,proof_nodes:pid,actual_rh_proof:false};
 }
 return {prove,close,emit,replay,run,ar,omega0,omegaW,at,logic:{E,M,A,F,O,X,fv,sub,split,exAt,qAt,hyp,ax,mp,generalize,abs,comp,left,right,conj,ui,introAt,exIntro,exElim}};
 }
 return {prepare,run:raw=>prepare(raw).run()};
}
export const induction=buildInduction(kernel,spine,assembler,interfaces,compression);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/induction.mjs')){
 const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(induction.run(raw),null,2));
}
