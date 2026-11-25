// RH-PL-12: exact numerator normalization and joint harmonic graph agreement.
import {transport} from './transport.mjs';
import {kernel} from './kernel.mjs';
import {denominator} from './denominator.mjs';
export function numerator(tr,k,den,raw,mode='all'){
 const t=tr.prepare(raw),{p,ar,ns,apply,inst,nest,move,symmetric,trans,replace,emptyUnique,succUnique,empty,succ}=t,{imp,gen,intern}=ar,{E,M,A,X,fv,sub,split,exAt,qAt,hyp,mp,generalize,abs,left,right,conj,ui,exIntro,exElim}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 let f=intern(k.decode(raw.slice(0,-1)));while(ns[f].tag==='a')f=ns[f].y;const D=ns[f].x;
 const clauses=[];let rem=D;for(let j=0;j<21;j++){const [x,y]=split(rem);clauses.push(x);rem=y}clauses.push(rem);
 const G=7,H=44,B=8,C=43,mark=99,Z=1,ADD=3,MUL=4,nat=x=>M(x,0),and=fs=>fs.reduceRight((r,q)=>A(q,r)),qform=(f,...xs)=>xs.reduce((r,x)=>qAt(r,x),f);
 const zNat=clauses[1],zEmpty=clauses[2],addTotal=clauses[5],mulTotal=clauses[6],numTotal=g=>sub(clauses[13],G,g),denTotal=b=>sub(clauses[14],B,b),numInit=g=>sub(clauses[18],G,g),numRec=(g,b)=>sub(sub(clauses[20],G,g),B,b);
 function graph1(total,x,u){const f=qform(split(total)[1],x,u,x);return split(ns[ns[f].y].x)[0]}
 function graph2(total,x,y,u){const f=qform(split(total)[1],x,y,u,x);return split(ns[ns[f].y].x)[0]}
 const gn=(g,x,u)=>graph1(numTotal(g),x,u),gb=(b,x,u)=>graph1(denTotal(b),x,u),gm=(x,y,u)=>graph2(mulTotal,x,y,u),ga=(x,y,u)=>graph2(addTotal,x,y,u);
 function unpack(h,count){const out=[];for(let i=0;i<count-1;i++){out.push(left(h));h=right(h)}out.push(h);return out}
 function pack(fs,fn){const H=hyp(and(fs));return abs(H,fn(...unpack(H,fs.length)))}
 function withNat(q,x,fn){const h=hyp(exAt(q.f,x));return exElim(q,x,h,fn(left(h),right(h)))}
 function fun1(total,x,u,v,mx,mu,mv,gu,gv){const q=mp(nest(mx,mu,mv),inst(right(total),x,u,v)),[l,r]=split(ns[q.f].x);return mp(conj(move(gu,l),move(gv,r)),q)}
 function fun2(total,x,y,u,v,mx,my,mu,mv,gu,gv){const q=mp(nest(mx,my,mu,mv),inst(right(total),x,y,u,v)),[l,r]=split(ns[q.f].x);return mp(conj(move(gu,l),move(gv,r)),q)}
 const quantified=(pf,xs)=>xs.reduceRight((r,x)=>generalize(x,r),pf);
 const [x,y,u,j,b]=[50,51,52,53,54];
 const base=pack([zNat,zEmpty,numTotal(G),numInit(G),empty(x),nat(x),nat(y),gn(G,x,y)],(mz,ez,total,initial,ex,mx,mv,gv)=>{
   const exz=emptyUnique(x,Z,ex,ez,98),gz=replace(gv,exz,gn(G,mark,y),mark);
   return withNat(initial,60,(m,s)=>trans(fun1(total,Z,y,60,mz,mv,m,gz,left(s)),right(s)))
 });
 const baseQ=quantified(base,[G,x,y]);assert(ns[base.f].y===E(y,Z),'base conclusion');
 const updateGoal=(y,u,b,j)=>X(70,A(nat(70),A(gm(y,u,70),ga(70,b,j))));
 // Exact numerator clause: seven successive natural witnesses
 // k,a,l,b0,c0,d0,e0; the final equality is a=e0.
 const update=pack([numTotal(G),denTotal(B),numRec(G,B),nat(x),nat(y),nat(u),nat(j),nat(b),succ(x,y),gn(G,x,u),gn(G,y,j),gb(B,x,b)],(nt,dt,rec,mx,my,mu,mj,mb,sy,gxu,gyj,bxb)=>{
   return withNat(mp(mx,ui(rec,x)),60,(mk,kbody)=>withNat(right(kbody),61,(ma,abody)=>withNat(right(abody),62,(ml,lbody)=>withNat(right(lbody),63,(mnb,nbbody)=>withNat(right(nbbody),64,(mc,cbody)=>withNat(right(cbody),65,(md,dbody)=>withNat(right(dbody),66,(me,ebody)=>{
     const sk=left(kbody),gka=left(abody),sl=left(lbody),gxb=left(nbbody),prod=left(cbody),denx=left(dbody),sum=left(ebody),eqae=right(ebody);
     assert(eqae.f===E(61,66),'recurrence final equality');
     const ky=succUnique(x,60,y,sk,sy,98),ly=succUnique(x,62,y,sl,sy,98);
     const gya=replace(move(gka,gn(G,60,61)),ky,gn(G,mark,61),mark);
     const aj=fun1(nt,y,61,j,my,ma,mj,gya,gyj),bu=fun1(nt,x,63,u,mx,mnb,mu,gxb,gxu),db=fun1(dt,x,65,b,mx,md,mb,denx,bxb),ej=trans(symmetric(eqae),aj);
     let mul=move(prod,gm(62,63,64));mul=replace(mul,ly,gm(mark,63,64),mark);mul=replace(mul,bu,gm(y,mark,64),mark);
     let add=move(sum,ga(64,65,66));add=replace(add,db,ga(64,mark,66),mark);add=replace(add,ej,ga(64,b,mark),mark);
     assert(mul.f===gm(y,u,64)&&add.f===ga(64,b,j),'normalized update');
     const out=exIntro(updateGoal(y,u,b,j),64,nest(mc,mul,add));assert(out.f===updateGoal(y,u,b,j),'existential normalized');return out
   })))))))
 });
 const updateQ=quantified(update,[G,B,x,y,u,j,b]);
 const row=(name,pf,cap=0)=>{const closed=p.close(pf),r=cap?p.replay(closed,cap):p.emit(closed);return {name,root_bytes:ns[closed.f].u,...r.cost,axioms:r.axioms,structural_replay:true,original_full_replay:!!r.original}};
 const rows=mode==='certificate'?[]:[row('exact_numerator_base',baseQ,24000000),row('exact_numerator_successor_normalization',updateQ)];
 if(mode==='local')return {rows,formula_nodes:ns.length-1,actual_rh_proof:false};
 // Instantiate the prior exact denominator theorem in the same proof
 // arena, without assuming the resulting agreement.
 const denProof=den(tr,k,raw,'proof',t);
 const phi=gen(33,gen(34,imp(A(M(33,1),A(M(34,1),A(p.at(G,0,33),p.at(H,0,34)))),E(33,34))));
 const ir=p.prove(phi).source0,BP=ns[ns[ir.f].y].x,STEP=ns[ns[ns[ir.f].y].y].x,goal=ns[ns[ns[ir.f].y].y].y;
 assert(ns[ir.f].x===clauses[0],'omega');
 const P=n=>sub(sub(phi,0,n),1,0);
 function outputs(n){const q=ns[qform(P(n),33,34)],h=hyp(q.x),[ma,mb,ga,hb]=unpack(h,4);return {ma,mb,ga,hb,end:r=>generalize(33,generalize(34,abs(h,r)))}}
 const sourceIds=[0,1,2,5,6,13,14,18,19,20,21],basePremises=sourceIds.map(i=>clauses[i]);
 const comparison=[numTotal(H),numInit(H),numRec(H,C),denTotal(C),sub(clauses[19],B,C),sub(clauses[21],B,C)];
 const premises=[...basePremises,...comparison];
 const localPremises=[clauses[0],zNat,zEmpty,addTotal,mulTotal,numTotal(G),numInit(G),numRec(G,B),numTotal(H),numInit(H),numRec(H,C),denTotal(B),denTotal(C),denProof.goal];
 const numeratorProof=pack(localPremises,(omega,mz,ez,atot,mt,gT,gI,gR,hT,hI,hR,bT,cT,denAgree)=>{
   const z=20,baseHyp=hyp(A(empty(z),nat(z))),bz=left(baseHyp),bm=right(baseHyp),ob=outputs(z);
   const b1=mp(nest(mz,ez,gT,gI,bz,bm,ob.ma,move(ob.ga,gn(G,z,33))),inst(baseQ,G,z,33));
   const b2=mp(nest(mz,ez,hT,hI,bz,bm,ob.mb,move(ob.hb,gn(H,z,34))),inst(baseQ,H,z,34));
   const bp=generalize(z,abs(baseHyp,ob.end(trans(b1,symmetric(b2)))));assert(bp.f===BP,'base');
   const xx=21,yy=22,stepHyp=hyp(A(nat(xx),A(nat(yy),A(succ(xx,yy),P(xx))))),[mx,my,sy,prev]=unpack(stepHyp,4),oy=outputs(yy);
   const eg=mp(mx,ui(left(gT),xx)),eh=mp(mx,ui(left(hT),xx)),eb=mp(mx,ui(left(bT),xx)),ec=mp(mx,ui(left(cT),xx));
   const next=withNat(eg,55,(ma,gx)=>withNat(eh,56,(mb,hx)=>withNat(eb,57,(md,bx)=>withNat(ec,58,(me,cx)=>{
     const ag=mp(nest(ma,mb,move(gx,p.at(G,xx,55)),move(hx,p.at(H,xx,56))),inst(prev,55,56));
     const dp=mp(mx,ui(denAgree,xx));
     const bd=mp(nest(md,me,move(bx,p.at(B,xx,57)),move(cx,p.at(C,xx,58))),inst(dp,57,58));
     const mg=mp(nest(gT,bT,gR,mx,my,ma,oy.ma,md,sy,move(gx,gn(G,xx,55)),move(oy.ga,gn(G,yy,33)),move(bx,gb(B,xx,57))),inst(updateQ,G,B,xx,yy,55,33,57));
     const mh=mp(nest(hT,cT,hR,mx,my,mb,oy.mb,me,sy,move(hx,gn(H,xx,56)),move(oy.hb,gn(H,yy,34)),move(cx,gb(C,xx,58))),inst(updateQ,H,C,xx,yy,56,34,58));
     return withNat(mg,67,(mp1,rb1)=>withNat(mh,68,(mp2,rb2)=>{
       const m1=left(rb1),a1=right(rb1);
       const m2=replace(left(rb2),symmetric(ag),gm(yy,mark,68),mark);
       const eq=fun2(mt,yy,55,67,68,my,ma,mp1,mp2,m1,m2);
       let a2=replace(right(rb2),symmetric(eq),ga(mark,58,34),mark);
       a2=replace(a2,symmetric(bd),ga(67,mark,34),mark);
       return fun2(atot,67,57,33,34,mp1,md,oy.ma,oy.mb,a1,a2)
     }))
   }))));
   const stepProof=generalize(xx,generalize(yy,abs(stepHyp,oy.end(next))));assert(stepProof.f===STEP,'step');
   const out=apply(ir,omega,bp,stepProof);assert(out.f===goal,'agreement');return out
 });
 if(mode!=='certificate')rows.push(row('numerator_agreement_given_denominator_agreement',numeratorProof));
 // Discharge the denominator agreement premise using the already derived
 // denominator theorem. All premise lookup uses literal formula IDs.
 const combined=pack(premises,(...ps)=>{
   const by=new Map(ps.map(q=>[q.f,q]));
   const pick=f=>{assert(by.has(f),'missing premise '+f);return by.get(f)};
   const denom=mp(nest(...denProof.premiseFormulas.map(pick)),denProof.result);
   assert(denom.f===denProof.goal,'denominator conclusion');
   const num=mp(nest(...localPremises.map(f=>f===denProof.goal?denom:pick(f))),numeratorProof);
   assert(num.f===goal,'numerator conclusion');
   return conj(denom,num)
 });
 if(mode==='certificate'){const root=p.close(combined),r=p.emit(root);return {nodes:ar.nodes,ids:r.ids,root:root.f,target:k.encode(ar.ast(root.f)),cost:r.cost};}
 rows.push(row('joint_harmonic_graph_agreement_from_exact_clauses',combined));
 return {rows,source_clauses:sourceIds,comparison_graph_slots:{numerator:H,denominator:C},source_formula_bytes:sourceIds.map(i=>({index:i,bytes:ns[clauses[i]].u})),base_discharged:true,step_discharged:true,denominator_premise_discharged:true,formula_nodes:ns.length-1,actual_rh_proof:false};
}
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/numerator.mjs')){const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(numerator(transport,kernel,denominator,raw,process.argv.includes('--local')?'local':'all'),null,2));}
