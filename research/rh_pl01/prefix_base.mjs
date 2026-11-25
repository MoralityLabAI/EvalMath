// RH-PL-14: singleton zero prefix and base coverage of exact bounded family.
import {pairs} from './pairs.mjs';
import {kernel} from './kernel.mjs';
function buildPrefixBase(ps,k){
 function prepare(raw){
 const ctx=ps.prepare(raw),{p,t,ar,ns,pair,single,pairProof,bound,sg,singleExists,cases,pack,witness,allP,all,and,chain,explode,orLeft,orRight,refl}=ctx,{apply,inst,nest,move,symmetric,trans,replace,emptyUnique,empty,succ}=t,{imp,gen,neg,intern}=ar,{E,M,A,F,O,X,sub,split,qAt,exAt,hyp,mp,generalize,abs,left,right,conj,ui,introAt,exIntro,exElim}=p.logic;
 const assert=(q,m)=>{if(!q)throw Error(m)};
 let f=intern(k.decode(raw.slice(0,-1)));while(ns[f].tag==='a')f=ns[f].y;let rem=ns[f].x;const clauses=[];for(let j=0;j<21;j++){const [x,y]=split(rem);clauses.push(x);rem=y}clauses.push(rem);
 const W=37,C0=6,MUL=8,S=0,n=40,x=41,y=42,a=43,b=44,P=50,Q=51,K=53,Z=60,pp=61,g=62,nat=x=>M(x,W),at=(s,x,a)=>p.at(s,x,a);
 const mt=sub(sub(clauses[6],4,MUL),0,W);
 function mul(x,y,z){const q=[x,y,z,x].reduce((r,v)=>qAt(r,v),split(mt)[1]);return split(ns[ns[q].y].x)[0]}
 const subset=(s,q)=>gen(3,imp(M(3,s),M(3,q)));
 const powerDef=(s,q)=>gen(2,F(M(2,q),subset(2,s)));
 const dom=(s,x)=>X(45,A(nat(45),at(s,x,45)));
 const prefixDomain=s=>X(n,A(nat(n),gen(x,imp(nat(x),F(dom(s,x),O(E(x,n),M(x,n)))))));
 const functional=s=>all([x,a,b],chain([nat(x),nat(a),nat(b),at(s,x,a),at(s,x,b)],E(a,b)));
 const base=s=>all([x,a],chain([empty(x),nat(x),nat(a),at(s,x,a)],E(a,C0)));
 const step=s=>all([x,y,a,b],chain([nat(x),nat(y),nat(a),nat(b),succ(x,y),at(s,x,a),at(s,y,b)],mul(y,a,b)));
 const good=s=>and([prefixDomain(s),functional(s),base(s),step(s)]);
 const phi=good(S),famSpec=gen(0,F(M(0,K),A(subset(0,Q),phi)));
 const cover=i=>X(46,A(M(46,K),X(47,A(nat(47),at(46,i,47)))));
 const baseGoal=gen(20,imp(A(empty(20),nat(20)),cover(20)));
 const premises=[nat(Z),empty(Z),nat(C0),powerDef(W,P),powerDef(P,Q),famSpec];
 const pairAll=allP([40,41],pairProof),boundAll=allP([40,41,44,45,46,47],bound),sgAll=allP([40,41,42,43,44,48],sg);
 const result=pack(premises,(mz,ez,mc,pw,pq,family)=>{
   return witness(inst(pairAll,Z,C0),pp,hp=>witness(singleExists(pp,g),g,hs=>{
     function rel(i,j){
       const r=inst(sgAll,Z,C0,i,j,pp,g);
       const ans=mp(conj(hs,hp),r);assert(ans.f===F(at(g,i,j),A(E(i,Z),E(j,C0))),'singleton relation');return ans
     }
     function makeVal(i,j,ei,ej){return mp(conj(ei,ej),right(rel(i,j)))}
     const zVal=makeVal(Z,C0,refl(Z),refl(C0));
     const i=70,j=71,l=72,m=73;
     // Exact domain through designated zero.
     const dH=hyp(nat(i)),dh=hyp(dom(g,i));
     const domainForward=witness(dh,m,h=>orLeft(left(mp(right(h),left(rel(i,m)))),M(i,Z)));
     const rd=hyp(O(E(i,Z),M(i,Z)));
     const domainReverse=cases(rd,E(i,Z),M(i,Z),ei=>exIntro(dom(g,i),C0,conj(mc,makeVal(i,C0,ei,refl(C0)))),mi=>explode(mi,ui(ez,i),dom(g,i)));
     const bic=conj(abs(dh,domainForward),abs(rd,domainReverse));
     const domFor=move(generalize(i,abs(dH,bic)),gen(x,imp(nat(x),F(dom(g,x),O(E(x,Z),M(x,Z))))));
     const domain=exIntro(prefixDomain(g),Z,conj(mz,domFor));
     // Functionality and common base from singleton graph equivalence.
     const fh=[nat(i),nat(j),nat(l),at(g,i,j),at(g,i,l)].map(hyp);
     const e1=right(mp(fh[3],left(rel(i,j)))),e2=right(mp(fh[4],left(rel(i,l))));
     const fn=move(allP([i,j,l],fh.reduceRight((r,h)=>abs(h,r),trans(e1,symmetric(e2)))),functional(g));
     const bh=[empty(i),nat(i),nat(j),at(g,i,j)].map(hyp);
     const be=right(mp(bh[3],left(rel(i,j))));
     const bs=move(allP([i,j],bh.reduceRight((r,h)=>abs(h,r),be)),base(g));
     // No successor pair can have both inputs in the singleton zero domain.
     const sh=[nat(i),nat(m),nat(j),nat(l),succ(i,m),at(g,i,j),at(g,m,l)].map(hyp);
     const iz=left(mp(sh[5],left(rel(i,j)))),mz2=left(mp(sh[6],left(rel(m,l))));
     const sx=mp(orRight(M(i,i),refl(i)),right(ui(sh[4],i)));
     let zz=replace(sx,iz,M(99,m),99);zz=replace(zz,mz2,M(Z,99),99);
     const impossible=explode(zz,ui(ez,Z),mul(m,j,l));
     const st=move(allP([i,m,j,l],sh.reduceRight((r,h)=>abs(h,r),impossible)),step(g));
     const goodProof=nest(domain,fn,bs,st);assert(goodProof.f===good(g),'exact Good');
     // Boundedness: ordered pair belongs to the double power set;
     // every member of the singleton graph is that pair.
     const bd=inst(boundAll,Z,C0,pp,W,P,Q),[v1,rest1]=split(ns[bd.f].x),[v2,rest2]=split(rest1),[pw0,rest3]=split(rest2),[pq0,pp0]=split(rest3);
     assert(v1===mz.f&&v2===mc.f&&pp0===hp.f,'bound premises');
     const inQ=mp(nest(mz,mc,move(pw,pw0),move(pq,pq0),hp),bd);
     const hmem=hyp(M(i,g)),same=mp(hmem,left(ui(hs,i)));
     const bounded=introAt(abs(hmem,replace(inQ,symmetric(same),M(99,Q),99)),i,subset(g,Q));
     const gf=mp(conj(bounded,goodProof),right(ui(family,g)));
     // Base coverage for any empty member, by empty-set uniqueness.
     const v=20,h=hyp(A(empty(v),nat(v))),eq=emptyUnique(Z,v,ez,left(h),98),val=replace(zVal,eq,at(g,99,C0),99);
     const cv=exIntro(cover(v),g,conj(gf,exIntro(X(47,A(nat(47),at(g,v,47))),C0,conj(mc,val))));
     return generalize(v,abs(h,cv))
   }))
 });
 assert(ns[result.f].y===baseGoal,'exact base coverage');
 const out=ctx.get('bounded_prefix_family_base_coverage',result);
 return {...out,phi:k.encode(ar.ast(phi)),famSpec:k.encode(ar.ast(famSpec)),receipt:{...out.receipt,good_predicate_bytes:ns[phi].u,premises:premises.map(i=>ns[i].u),base_coverage_discharged:true,actual_rh_proof:false}};
 }
 return {prepare};
}
export const prefixBase=buildPrefixBase(pairs,kernel);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/prefix_base.mjs')){const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(prefixBase.prepare(raw).receipt,null,2));}
