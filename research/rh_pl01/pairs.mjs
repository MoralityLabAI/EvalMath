// RH-PL-14: exact Kuratowski ordered-pair and singleton graph theorems.
import {transport} from './transport.mjs';
import {kernel} from './kernel.mjs';
function buildPairs(tr,k){
 function prepare(raw){
 const t=tr.prepare(raw),{p,ar,ns,apply,inst,nest,move,symmetric,trans,replace}=t,{imp,gen,neg}=ar,{E,M,A,F,O,X,fv,sub,split,exAt,qAt,hyp,ax,mp,generalize,abs,comp,left,right,conj,ui,introAt,exIntro,exElim,identity,contra}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const all=(xs,f)=>xs.reduceRight((r,x)=>gen(x,r),f),allP=(xs,q)=>xs.reduceRight((r,x)=>generalize(x,r),q),chain=(fs,f)=>fs.reduceRight((r,s)=>imp(s,r),f),and=fs=>fs.reduceRight((r,s)=>A(s,r));
 const refl=x=>ax(E(x,x));
 const witness=(q,x,fn)=>{const h=hyp(exAt(q.f,x));return exElim(q,x,h,fn(h))};
 function unpack(h,n){const r=[];for(let i=1;i<n;i++){r.push(left(h));h=right(h)}r.push(h);return r}
 function pack(fs,fn){const h=hyp(and(fs));return abs(h,fn(...unpack(h,fs.length)))}
 function explode(q,n,goal){
   assert(n.f===neg(q.f),'contradiction');
   const c=mp(n,ax(imp(n.f,imp(neg(goal),n.f))));
   return apply(ax(imp(c.f,imp(q.f,goal))),c,q)
 }
 function orLeft(q,r){const h=hyp(neg(q.f));return abs(h,explode(q,h,r))}
 function orRight(l,q){const h=hyp(neg(l));return abs(h,q)}
 function cases(q,l,r,fn1,fn2){
   assert(q.f===O(l,r),'disjunction');
   const h1=hyp(l),h2=hyp(r),a1=abs(h1,fn1(h1)),a2=abs(h2,fn2(h2)),goal=ns[a1.f].y;
   assert(ns[a2.f].y===goal,'case outputs');
   const h=hyp(neg(goal)),nl=mp(h,contra(a1)),rr=mp(nl,q),yes=mp(rr,a2);
   const truth=refl(0),ntruth=explode(yes,h,neg(truth.f)),bridge=abs(h,ntruth);
   return apply(ax(imp(bridge.f,imp(truth.f,goal))),bridge,truth)
 }
 const single=(s,x)=>gen(32,F(M(32,s),E(32,x))),double=(s,x,y)=>gen(32,F(M(32,s),O(E(32,x),E(32,y))));
 const pair=(z,x,y)=>split(exAt(p.at(8,x,y),z))[0],at=(g,x,y)=>p.at(g,x,y);
 const pairing=ax(gen(0,gen(1,X(2,gen(3,F(M(3,2),O(E(3,0),E(3,1))))))));
 assert(pairing.detail==='pairing','pairing axiom');
 const ext=ax(gen(0,gen(1,imp(gen(2,F(M(2,0),M(2,1))),E(0,1)))));
 const pow=ax(gen(0,X(1,gen(2,F(M(2,1),gen(3,imp(M(3,2),M(3,0))))))));
 assert(ext.detail==='extensionality'&&pow.detail==='power','fixed axioms');
 function setEq(x,y,point,z=98){const e=inst(ext,x,y);return mp(introAt(point(z),z,ns[e.f].x),e)}
 function doubleExists(x,y,s){return move(inst(pairing,x,y),X(s,double(s,x,y)))}
 function singleExists(x,s){
   return witness(doubleExists(x,x,s),51,h=>{
     const z=98,q=ui(h,z),l=M(z,51),r=E(z,x),hl=hyp(l),hr=hyp(r);
     const f=abs(hl,cases(mp(hl,left(q)),r,r,a=>a,b=>b));
     const g=abs(hr,mp(orLeft(hr,r),right(q)));
     const def=introAt(conj(f,g),z,single(51,x));
     return exIntro(X(s,single(s,x)),51,def)
   })
 }
 function componentMember(h,t,x,y=null){
   const q=ui(h,t);
   if(y===null)return mp(refl(x),right(q));
   assert(t===x||t===y,'component index');
   return mp(t===x?orLeft(refl(t),E(t,y)):orRight(E(t,x),refl(t)),right(q))
 }
 function pairComponents(z,x,y,s,d,hS,hD,hP){
   const u=97,mem=hyp(M(u,z)),q=ui(hP,u),dis=mp(mem,left(q)),target=O(single(u,x),double(u,x,y));
   const f=cases(dis,E(u,s),E(u,d),e=>{
     const moved=replace(hS,symmetric(e),single(99,x),99);return orLeft(moved,double(u,x,y))
   },e=>{
     const moved=replace(hD,symmetric(e),double(99,x,y),99);return orRight(single(u,x),moved)
   });
   const rev=hyp(target);
   const g=cases(rev,single(u,x),double(u,x,y),hs=>{
     const eq=setEq(u,s,v=>{const a=ui(hs,v),b=ui(hS,v);return conj(comp(left(a),right(b)),comp(left(b),right(a)))});
     return mp(orLeft(eq,E(u,d)),right(q))
   },hd=>{
     const eq=setEq(u,d,v=>{const a=ui(hd,v),b=ui(hD,v);return conj(comp(left(a),right(b)),comp(left(b),right(a)))});
     return mp(orRight(E(u,s),eq),right(q))
   });
   return introAt(conj(abs(mem,f),abs(rev,g)),u,pair(z,x,y))
 }
 const [x,y,u,v,z]=[40,41,42,43,44];
 const pairEx=X(z,pair(z,x,y));
 const pairProof=witness(singleExists(x,50),50,hs=>witness(doubleExists(x,y,52),52,hd=>witness(doubleExists(50,52,53),53,hp=>exIntro(pairEx,53,pairComponents(53,x,y,50,52,hs,hd,hp)))));
 assert(pairProof.f===pairEx,'pair existence');
 // Membership consequences of the pair definition.
 function inPairComponent(pf,c,def){return mp(def,right(ui(pf,c)))}
 function anyComponent(pf,c,inP,a,b,fnS,fnD){return cases(mp(inP,left(ui(pf,c))),single(c,a),double(c,a,b),fnS,fnD)}
 function firstEq(l,r){
   return witness(singleExists(x,50),50,s=>{
     const m=inPairComponent(l,50,orLeft(s,double(50,x,y)));
     return anyComponent(r,50,m,u,v,ss=>{
       const uu=componentMember(ss,u,u);return symmetric(mp(uu,left(ui(s,u))))
     },dd=>{
       const uu=componentMember(dd,u,u,v);return symmetric(mp(uu,left(ui(s,u))))
     })
   })
 }
 function secondIn(l,r,x,y,u,v){
   return witness(doubleExists(x,y,52),52,d=>{
     const m=inPairComponent(l,52,orRight(single(52,x),d)),ym=componentMember(d,y,x,y);
     return anyComponent(r,52,m,u,v,ss=>orLeft(mp(ym,left(ui(ss,y))),E(y,v)),dd=>mp(ym,left(ui(dd,y))))
   })
 }
 const inject=pack([pair(z,x,y),pair(z,u,v)],(l,r)=>{
   const e=firstEq(l,r),b=secondIn(l,r,x,y,u,v),d=secondIn(r,l,u,v,x,y);
   const second=cases(b,E(y,u),E(y,v),h=>{
     return cases(d,E(v,x),E(v,y),j=>trans(trans(h,symmetric(e)),symmetric(j)),j=>symmetric(j))
   },h=>h);
   return conj(e,second)
 });
 assert(ns[inject.f].y===A(E(x,u),E(y,v)),'pair injectivity');
 const W=45,P=46,Q=47;
 const subset=(s,t)=>gen(32,imp(M(32,s),M(32,t)));
 const power=(s,t)=>gen(32,F(M(32,t),subsetFor(32,s)));
 const subsetFor=(s,t)=>gen(31,imp(M(31,s),M(31,t)));
 // power predicate uses distinct binder 32 for subset element, 31
 // for members of the subset, matching the fixed power-set axiom up
 // to checked alpha conversion.
 const bound=pack([M(x,W),M(y,W),power(W,P),power(P,Q),pair(z,x,y)],(mx,my,pw,pq,hp)=>{
   const c=97,hc=hyp(M(c,z)),targ=ui(pw,c),subGoal=ns[right(targ).f].x;
   const inc=anyComponent(hp,c,hc,x,y,hs=>{
     const h=96,hm=hyp(M(h,c)),eq=mp(hm,left(ui(hs,h)));
     const mw=replace(mx,symmetric(eq),M(99,W),99);
     return introAt(abs(hm,mw),h,subGoal)
   },hd=>{
     const h=96,hm=hyp(M(h,c)),r=mp(hm,left(ui(hd,h)));
     const mw=cases(r,E(h,x),E(h,y),eq=>replace(mx,symmetric(eq),M(99,W),99),eq=>replace(my,symmetric(eq),M(99,W),99));
     return introAt(abs(hm,mw),h,subGoal)
   });
   const inP=mp(inc,right(targ)),q=ui(pq,z),subP=introAt(abs(hc,inP),c,ns[right(q).f].x);
   return mp(subP,right(q))
 });
 assert(ns[bound.f].y===M(z,Q),'pair bound');
 const graph=48;
 // The exact graph application relation for a singleton graph is a
 // conjunction of the two coordinate equalities.
 const sg=pack([single(graph,z),pair(z,x,y)],(s,pairxy)=>{
   const out=at(graph,u,v),hin=hyp(out);
   const f=witness(hin,50,h=>{
     const eq=mp(right(h),left(ui(s,50))),pairuv=replace(left(h),eq,pair(99,u,v),99);
     // The injectivity theorem is open; substitute its parameters
     // simultaneously by generalization followed by fresh instantiation.
     const inj=allP([x,y,u,v,z],inject);
     const prem=inst(inj,x,y,u,v,z);
     const eqs=mp(conj(pairxy,pairuv),prem);
     return conj(symmetric(left(eqs)),symmetric(right(eqs)))
   });
   const h=hyp(A(E(u,x),E(v,y)));
   let pairuv=replace(pairxy,symmetric(left(h)),pair(z,99,y),99);
   pairuv=replace(pairuv,symmetric(right(h)),pair(z,u,99),99);
   const mem=mp(refl(z),right(ui(s,z))),r=exIntro(out,z,conj(pairuv,mem));
   return conj(abs(hin,f),abs(h,r))
 });
 assert(ns[sg.f].y===F(at(graph,u,v),A(E(u,x),E(v,y))),'singleton graph equivalence');
 function get(name,pf,cap=0){const root=p.close(pf),r=cap?p.replay(root,cap):p.emit(root);return {name,raw:{nodes:ar.nodes,ids:r.ids,root:root.f,target:k.encode(ar.ast(root.f)),cost:r.cost},receipt:{name,target_bytes:ns[root.f].u,...r.cost,axioms:r.axioms,structural_replay:true,original_full_replay:!!r.original}}}
 function run(){return [get('ordered_pair_exists',pairProof,32000000),get('ordered_pair_injectivity',inject,32000000),get('ordered_pair_double_power_bound',bound,32000000),get('singleton_graph_application',sg,48000000)]}
 return {run,get,p,t,ar,ns,pair,single,double,pairProof,inject,bound,sg,singleExists,doubleExists,cases,pack,witness,allP,all,and,chain,explode,orLeft,orRight,refl};
 }
 return {prepare};
}
export const pairs=buildPairs(transport,kernel);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/pairs.mjs')){const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(pairs.prepare(raw).run().map(x=>x.receipt),null,2));}
