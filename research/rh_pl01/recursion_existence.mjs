// RH-PL-13: derive total functional denominator recurrence from compatible approximations.
import {gluing} from './gluing.mjs';
import {kernel} from './kernel.mjs';
function buildRecursiveExistence(gl,k){
 function prepare(raw){
 const ctx=gl.prepare(raw),{t,p,ar,ns,cover,total,functional,compat,memberFamily,base,step,unionRel}=ctx,{apply,inst,nest,replace,empty,succ}=t,{imp,gen,intern}=ar,{E,M,A,X,sub,split,qAt,exAt,hyp,mp,generalize,abs,left,right,conj,ui,exIntro,exElim}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)},all=(xs,f)=>xs.reduceRight((r,x)=>gen(x,r),f),allP=(xs,pf)=>xs.reduceRight((r,x)=>generalize(x,r),pf),chain=(fs,f)=>fs.reduceRight((r,s)=>imp(s,r),f),and=fs=>fs.reduceRight((r,s)=>A(s,r)),nat=n=>M(n,1),inFam=s=>M(s,4),at=(s,n,v)=>p.at(s,n,v);
 function unpack(h,count){const out=[];for(let i=0;i<count-1;i++){out.push(left(h));h=right(h)}out.push(h);return out}
 function witness(q,v,fn){const h=hyp(exAt(q.f,v));return exElim(q,v,h,fn(h))}
 function pack(fs,fn){const h=hyp(and(fs));return abs(h,fn(...unpack(h,fs.length)))}
 let f=intern(k.decode(raw.slice(0,-1)));while(ns[f].tag==='a')f=ns[f].y;let rem=ns[f].x;const clauses=[];for(let j=0;j<21;j++){const [x,y]=split(rem);clauses.push(x);rem=y}clauses.push(rem);
 const mt=sub(sub(clauses[6],4,8),0,1);
 function mul(x,y,z){const q=[x,y,z,x].reduce((r,v)=>qAt(r,v),split(mt)[1]);return split(ns[ns[q].y].x)[0]}
 const x=40,y=49,a=42,b=43,s=44,U=5,mark=99;
 const bLocal=all([s,x,a],chain([inFam(s),empty(x),nat(x),nat(a),at(s,x,a)],E(a,6)));
 const localWitness=(x,y)=>X(46,A(inFam(46),X(47,A(nat(47),X(48,A(nat(48),A(at(46,x,47),A(at(46,y,48),mul(y,47,48)))))))));
 const ext=all([x,y],chain([nat(x),nat(y),succ(x,y),cover(x)],localWitness(x,y)));
 const baseOut=g=>all([x,a],chain([empty(x),nat(x),nat(a),at(g,x,a)],E(a,6)));
 const updateOut=g=>all([x,y,a,b],chain([nat(x),nat(y),nat(a),nat(b),succ(x,y),at(g,x,a),at(g,y,b)],mul(y,a,b)));
 const goal=X(U,A(total(U),A(functional(U),A(baseOut(U),updateOut(U)))));
 const premises=[p.omegaW,base,compat,bLocal,ext];
 const withRel=ctx.glue(true);
 const result=pack(premises,(omega,b0,coh,bl,ex)=>{
   const xx=21,yy=22,H=hyp(A(nat(xx),A(nat(yy),A(succ(xx,yy),cover(xx))))),[mx,my,sy,cov]=unpack(H,4);
   const loc=apply(inst(ex,xx,yy),mx,my,sy,cov);
   const covY=witness(loc,50,hf=>witness(right(hf),51,ha=>witness(right(ha),52,hb=>{
      const [mb,ax,ay,m]=unpack(hb,4);
      return exIntro(cover(yy),50,conj(left(hf),exIntro(X(47,A(nat(47),at(50,yy,47))),52,conj(mb,ay))))
   })));
   const stepProof=allP([xx,yy],abs(H,covY));assert(stepProof.f===step,'coverage step');
   const graphEx=mp(nest(omega,b0,stepProof,coh),withRel);
   return witness(graphEx,U,hg=>{
     const [rel,tot,fun]=unpack(hg,3);
     assert(rel.f===unionRel(U)&&tot.f===total(U)&&fun.f===functional(U),'graph witness');
     const outBase=(()=>{
       const hs=[empty(x),nat(x),nat(a),at(U,x,a)].map(hyp),[em,mx,ma,ua]=hs;
       const f=mp(ua,left(inst(rel,x,a)));
       const eq=witness(f,50,hf=>apply(inst(bl,50,x,a),left(hf),em,mx,ma,right(hf)));
       return allP([x,a],hs.reduceRight((r,h)=>abs(h,r),eq))
     })();
     const outStep=(()=>{
       const hs=[nat(x),nat(y),nat(a),nat(b),succ(x,y),at(U,x,a),at(U,y,b)].map(hyp),[mx,my,ma,mb,sy,ua,ub]=hs;
       const v=mp(ua,left(inst(rel,x,a)));
       const cv=witness(v,50,hf=>exIntro(cover(x),50,conj(left(hf),exIntro(X(47,A(nat(47),at(50,x,47))),a,conj(ma,right(hf))))));
       const loc=apply(inst(ex,x,y),mx,my,sy,cv);
       const eq=witness(loc,50,hf=>witness(right(hf),51,ha=>witness(right(ha),52,hb=>{
         const [m2,ax,ay,prod]=unpack(hb,4),m1=left(ha),mf=left(hf);
         const u1=mp(exIntro(memberFamily(x,51),50,conj(mf,ax)),right(inst(rel,x,51)));
         const u2=mp(exIntro(memberFamily(y,52),50,conj(mf,ay)),right(inst(rel,y,52)));
         const e1=apply(inst(fun,x,51,a),mx,m1,ma,u1,ua),e2=apply(inst(fun,y,52,b),my,m2,mb,u2,ub);
         let q=replace(prod,e1,mul(y,mark,52),mark);
         q=replace(q,e2,mul(y,a,mark),mark);
         assert(q.f===mul(y,a,b),'update target');return q
       })));
       return allP([x,y,a,b],hs.reduceRight((r,h)=>abs(h,r),eq))
     })();
     assert(outBase.f===baseOut(U)&&outStep.f===updateOut(U),'normalized recurrence');
     return exIntro(goal,U,nest(tot,fun,outBase,outStep))
   })
 });
 const root=p.close(result),r=p.emit(root);
 return {raw:{nodes:ar.nodes,ids:r.ids,root:root.f,target:k.encode(ar.ast(root.f)),cost:r.cost},receipt:{name:'denominator_recursion_existence_from_compatible_family',target_bytes:ns[root.f].u,...r.cost,axioms:r.axioms,premise_formula_bytes:premises.map(i=>ns[i].u),structural_replay:true,original_full_replay:false,coverage_step_derived:true,normalized_base_and_recurrence_derived:true,actual_rh_proof:false}};
 }
 return {prepare};
}
export const recursionExistence=buildRecursiveExistence(gluing,kernel);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/recursion_existence.mjs')){const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(recursionExistence.prepare(raw).receipt,null,2));}
