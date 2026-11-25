// RH-PL-14: append a graph entry using pairing and union; preserve bounded functionality.
import {pairs} from './pairs.mjs';
import {kernel} from './kernel.mjs';
function buildAppend(ps,k){
 function prepare(raw,sharedCtx){
 const ctx=sharedCtx||ps.prepare(raw),{p,t,ar,ns,pair,single,pairProof,bound,sg,singleExists,doubleExists,cases,pack,witness,allP,all,and,chain,explode,orLeft,orRight,refl}=ctx,{apply,inst,nest,move,symmetric,trans,replace}=t,{imp,gen,neg}=ar,{E,M,A,F,O,X,sub,split,exAt,hyp,ax,mp,generalize,abs,left,right,conj,ui,introAt,exIntro}=p.logic;
 const assert=(q,m)=>{if(!q)throw Error(m)};
 const [x,y,G,W,P,Q,pp,s,f,U]=[60,61,62,37,50,51,65,66,67,68],i=70,j=71,l=72,h=73,mark=99;
 const nat=x=>M(x,W),at=(g,x,y)=>p.at(g,x,y),subset=(s,q)=>gen(3,imp(M(3,s),M(3,q))),power=(s,q)=>gen(2,F(M(2,q),subset(2,s)));
 const relation=g=>all([i,j],F(at(g,i,j),O(at(G,i,j),A(E(i,x),E(j,y)))));
 const func=g=>all([i,j,l],chain([nat(i),nat(j),nat(l),at(g,i,j),at(g,i,l)],E(j,l)));
 const absent=gen(j,imp(nat(j),neg(at(G,x,j))));
 const goal=X(U,and([relation(U),subset(U,Q),func(U)]));
 const pairAll=allP([40,41],pairProof),bdAll=allP([40,41,44,45,46,47],bound),sgAll=allP([40,41,42,43,44,48],sg);
 const union=ax(gen(0,X(1,gen(2,F(M(2,1),X(3,A(M(3,0),M(2,3))))))));
 assert(union.detail==='union','fixed union');
 function derive(continuation){
   return witness(inst(pairAll,x,y),pp,hp=>witness(singleExists(pp,s),s,hs=>witness(doubleExists(G,s,f),f,hf=>witness(ui(union,f),U,hu=>{
     const member=(z)=>F(M(z,U),O(M(z,G),M(z,s)));
     function memAt(z){
       const q=ui(hu,z),hfwd=hyp(M(z,U)),loc=mp(hfwd,left(q));
       const fw=witness(loc,h,hw=>{
         const g=left(hw),mem=right(hw),eqs=mp(g,left(ui(hf,h)));
         return cases(eqs,E(h,G),E(h,s),e=>orLeft(replace(mem,e,M(z,mark),mark),M(z,s)),e=>orRight(M(z,G),replace(mem,e,M(z,mark),mark)))
       });
       const hr=hyp(O(M(z,G),M(z,s))),rhs=ns[right(q).f].x;
       const rv=cases(hr,M(z,G),M(z,s),mg=>{
         const gf=mp(orLeft(refl(G),E(G,s)),right(ui(hf,G)));
         return mp(exIntro(rhs,G,conj(gf,mg)),right(q))
       },ms=>{
         const sf=mp(orRight(E(s,G),refl(s)),right(ui(hf,s)));
         return mp(exIntro(rhs,s,conj(sf,ms)),right(q))
       });
       const out=conj(abs(hfwd,fw),abs(hr,rv));assert(out.f===member(z),'member append');return out
     }
     function graphRel(n,v){
       const srel=mp(conj(hs,hp),inst(sgAll,x,y,n,v,pp,s)),r=O(at(G,n,v),A(E(n,x),E(v,y)));
       const h1=hyp(at(U,n,v)),fw=witness(h1,74,ha=>{
         const pair=left(ha),m=right(ha),d=mp(m,left(memAt(74)));
         return cases(d,M(74,G),M(74,s),g=>orLeft(exIntro(at(G,n,v),74,conj(pair,g)),A(E(n,x),E(v,y))),ms=>orRight(at(G,n,v),mp(exIntro(at(s,n,v),74,conj(pair,ms)),left(srel))))
       });
       const h2=hyp(r),rv=cases(h2,at(G,n,v),A(E(n,x),E(v,y)),ag=>witness(ag,74,ha=>{
         const m=mp(orLeft(right(ha),M(74,s)),right(memAt(74)));return exIntro(at(U,n,v),74,conj(left(ha),m))
       }),eq=>witness(mp(eq,right(srel)),74,ha=>{
         const m=mp(orRight(M(74,G),right(ha)),right(memAt(74)));return exIntro(at(U,n,v),74,conj(left(ha),m))
       }));
       return conj(abs(h1,fw),abs(h2,rv))
     }
     const rel=allP([i,j],graphRel(i,j));assert(rel.f===relation(U),'graph relation');
     return continuation(hp,hs,memAt,rel)
   }))))
 }
 const basic=derive((hp,hs,memAt,rel)=>exIntro(X(U,relation(U)),U,rel));
 const premises=[nat(x),nat(y),power(W,P),power(P,Q),subset(G,Q),func(G),absent];
 const boundedFunctional=pack(premises,(mx,my,pw,pq,oldBound,oldFunc,noOut)=>derive((hp,hs,memAt,rel)=>{
   const bd=inst(bdAll,x,y,pp,W,P,Q);
   const [_,r1]=split(ns[bd.f].x),[__,r2]=split(r1),[pw0,r3]=split(r2),[pq0,___]=split(r3);
   const inQ=mp(nest(mx,my,move(pw,pw0),move(pq,pq0),hp),bd);
   const hm=hyp(M(i,U)),d=mp(hm,left(memAt(i)));
   const inBound=cases(d,M(i,G),M(i,s),mg=>mp(mg,ui(oldBound,i)),ms=>{
     const e=mp(ms,left(ui(hs,i)));return replace(inQ,symmetric(e),M(mark,Q),mark)
   });
   const bounded=introAt(abs(hm,inBound),i,subset(U,Q));
   const hs0=[nat(i),nat(j),nat(l),at(U,i,j),at(U,i,l)].map(hyp),[mi,mj,ml,aj,al]=hs0;
   const dj=mp(aj,left(inst(rel,i,j))),dl=mp(al,left(inst(rel,i,l)));
   const e=cases(dj,at(G,i,j),A(E(i,x),E(j,y)),jg=>{
     return cases(dl,at(G,i,l),A(E(i,x),E(l,y)),lg=>apply(inst(oldFunc,i,j,l),mi,mj,ml,jg,lg),le=>{
       const atx=replace(jg,left(le),at(G,mark,j),mark),n=mp(mj,ui(noOut,j));return explode(atx,n,E(j,l))
     })
   },je=>{
     return cases(dl,at(G,i,l),A(E(i,x),E(l,y)),lg=>{
       const atx=replace(lg,left(je),at(G,mark,l),mark),n=mp(ml,ui(noOut,l));return explode(atx,n,E(j,l))
     },le=>trans(right(je),symmetric(right(le))))
   });
   const fn=allP([i,j,l],hs0.reduceRight((r,h)=>abs(h,r),e));
   assert(fn.f===func(U)&&bounded.f===subset(U,Q),'append output');
   return exIntro(goal,U,nest(rel,bounded,fn))
 }));
 assert(ns[boundedFunctional.f].y===goal,'append theorem');
 return {ctx,basic,boundedFunctional,relation,func,absent,premises,goal,derive,run:()=>[ctx.get('append_graph_application_equivalence',basic),ctx.get('bounded_fresh_append_preserves_functionality',boundedFunctional)]};
 }
 return {prepare}
}
export const append=buildAppend(pairs,kernel);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/append.mjs')){const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(append.prepare(raw).run().map(x=>x.receipt),null,2));}
