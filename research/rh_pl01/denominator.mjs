// RH-PL-11: normalize exact frozen denominator recurrence and derive uniqueness.
import {transport} from './transport.mjs';
import {kernel} from './kernel.mjs';
function denominator(tr,k,raw,mode='all'){
 const t=tr.prepare(raw),{p,ar,ns,apply,inst,nest,move,symmetric,trans,replace,emptyUnique,succUnique,empty,succ}=t,{imp,neg,gen,intern}=ar,{E,M,A,fv,sub,split,exAt,qAt,hyp,mp,generalize,abs,left,right,conj,ui,exElim}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 let f=intern(k.decode(raw.slice(0,-1)));while(ns[f].tag==='a')f=ns[f].y;const D=ns[f].x;
 const clauses=[];let rem=D;for(let j=0;j<21;j++){const [x,y]=split(rem);clauses.push(x);rem=y}clauses.push(rem);
 const G=8,H=43,mark=99,Z=1,ONE=2,nat=x=>M(x,0),and=fs=>fs.reduceRight((r,q)=>A(q,r)),qform=(f,...xs)=>xs.reduce((r,x)=>qAt(r,x),f);
 const zNat=clauses[1],zEmpty=clauses[2],mulTotal=clauses[6],denTotal=g=>sub(clauses[14],G,g),denInit=g=>sub(clauses[19],G,g),denRec=g=>sub(clauses[21],G,g);
 function graph1(g,x,u){const f=qform(split(denTotal(g))[1],x,u,x);return split(ns[ns[f].y].x)[0]}
 function graph2(x,y,u){const f=qform(split(mulTotal)[1],x,y,u,x);return split(ns[ns[f].y].x)[0]}
 function unpack(h,count){const out=[];for(let i=0;i<count-1;i++){out.push(left(h));h=right(h)}out.push(h);return out}
 function pack(fs,fn){const H=hyp(and(fs));return abs(H,fn(...unpack(H,fs.length)))}
 function withNat(q,x,fn){const h=hyp(exAt(q.f,x));return exElim(q,x,h,fn(left(h),right(h)))}
 function fun1(total,x,u,v,mx,mu,mv,gu,gv){const q=mp(nest(mx,mu,mv),inst(right(total),x,u,v)),[l,r]=split(ns[q.f].x);return mp(conj(move(gu,l),move(gv,r)),q)}
 function fun2(total,x,y,u,v,mx,my,mu,mv,gu,gv){const q=mp(nest(mx,my,mu,mv),inst(right(total),x,y,u,v)),[l,r]=split(ns[q.f].x);return mp(conj(move(gu,l),move(gv,r)),q)}
 const quantified=(pf,xs)=>xs.reduceRight((r,x)=>generalize(x,r),pf);
 const [x,y,u,j]=[50,51,52,53];
 const base=pack([zNat,zEmpty,denTotal(G),denInit(G),empty(x),nat(x),nat(y),graph1(G,x,y)],(mz,ez,total,initial,ex,mx,mv,gv)=>{
   const exz=emptyUnique(x,Z,ex,ez,98),gz=replace(gv,exz,graph1(G,mark,y),mark);
   return withNat(initial,60,(m,s)=>trans(fun1(total,Z,y,60,mz,mv,m,gz,left(s)),right(s)))
 });
 const baseQ=quantified(base,[G,x,y]);assert(ns[base.f].y===E(y,ONE),'base conclusion');
 const update=pack([denTotal(G),denRec(G),nat(x),nat(y),nat(u),nat(j),succ(x,y),graph1(G,x,u),graph1(G,y,j)],(total,rec,mx,my,mu,mj,sy,gxu,gyj)=>{
   return withNat(mp(mx,ui(rec,x)),60,(mk,kbody)=>withNat(right(kbody),61,(ma,abody)=>withNat(right(abody),62,(ml,lbody)=>withNat(right(lbody),63,(mb,bbody)=>withNat(right(bbody),64,(mc,cbody)=>{
     const sk=left(kbody),gka=left(abody),sl=left(lbody),gxb=left(bbody),prod=left(cbody),eqac=right(cbody);
     assert(eqac.f===E(61,64),'recurrence final equality');
     const ky=succUnique(x,60,y,sk,sy,98),ly=succUnique(x,62,y,sl,sy,98);
     const gya=replace(move(gka,graph1(G,60,61)),ky,graph1(G,mark,61),mark);
     const aj=fun1(total,y,61,j,my,ma,mj,gya,gyj),bu=fun1(total,x,63,u,mx,mb,mu,gxb,gxu),cj=trans(symmetric(eqac),aj);
     let z=move(prod,graph2(62,63,64));z=replace(z,ly,graph2(mark,63,64),mark);z=replace(z,bu,graph2(y,mark,64),mark);z=replace(z,cj,graph2(y,u,mark),mark);
     assert(z.f===graph2(y,u,j),'normalized update');return z
   })))))
 });
 const updateQ=quantified(update,[G,x,y,u,j]);
 const row=(name,pf,cap=0)=>{const closed=p.close(pf),r=cap?p.replay(closed,cap):p.emit(closed);return {name,root_bytes:ns[closed.f].u,...r.cost,axioms:r.axioms,structural_replay:true,original_full_replay:!!r.original}};
 const rows=[row('exact_denominator_base',baseQ,16000000),row('exact_denominator_successor_normalization',updateQ,16000000)];
 const premiseIds=[0,1,2,6,14,19,21],premiseFormulas=[...premiseIds.map(i=>clauses[i]),denTotal(H),denInit(H),denRec(H)];
 if(mode==='local')return {rows,source_clauses:premiseIds,formula_nodes:ns.length-1,actual_rh_proof:false};
 const phi=gen(33,gen(34,imp(A(M(33,1),A(M(34,1),A(p.at(G,0,33),p.at(H,0,34)))),E(33,34))));
 const ir=p.prove(phi).source0,B=ns[ns[ir.f].y].x,STEP=ns[ns[ns[ir.f].y].y].x,goal=ns[ns[ns[ir.f].y].y].y;
 assert(ns[ir.f].x===clauses[0],'omega');
 const P=n=>sub(sub(phi,0,n),1,0);
 function outputs(n){const q=ns[qform(P(n),33,34)],h=hyp(q.x),[ma,mb,ga,hb]=unpack(h,4);return {ma,mb,ga,hb,end:r=>generalize(33,generalize(34,abs(h,r)))}}
 const result=pack(premiseFormulas,(omega,mz,ez,mt,gT,gI,gR,hT,hI,hR)=>{
   const z=20,baseHyp=hyp(A(empty(z),nat(z))),bz=left(baseHyp),bm=right(baseHyp),ob=outputs(z);
   const b1=mp(nest(mz,ez,gT,gI,bz,bm,ob.ma,move(ob.ga,graph1(G,z,33))),inst(baseQ,G,z,33));
   const b2=mp(nest(mz,ez,hT,hI,bz,bm,ob.mb,move(ob.hb,graph1(H,z,34))),inst(baseQ,H,z,34));
   const bp=generalize(z,abs(baseHyp,ob.end(trans(b1,symmetric(b2)))));assert(bp.f===B,'base');
   const xx=21,yy=22,stepHyp=hyp(A(nat(xx),A(nat(yy),A(succ(xx,yy),P(xx))))),[mx,my,sy,prev]=unpack(stepHyp,4),oy=outputs(yy);
   const eg=mp(mx,ui(left(gT),xx)),eh=mp(mx,ui(left(hT),xx));
   const next=withNat(eg,55,(ma,ga)=>withNat(eh,56,(mb,hb)=>{
     const ag=mp(nest(ma,mb,move(ga,p.at(G,xx,55)),move(hb,p.at(H,xx,56))),inst(prev,55,56));
     const mg=mp(nest(gT,gR,mx,my,ma,oy.ma,sy,move(ga,graph1(G,xx,55)),move(oy.ga,graph1(G,yy,33))),inst(updateQ,G,xx,yy,55,33));
     const mh=mp(nest(hT,hR,mx,my,mb,oy.mb,sy,move(hb,graph1(H,xx,56)),move(oy.hb,graph1(H,yy,34))),inst(updateQ,H,xx,yy,56,34));
     const mh2=replace(mh,symmetric(ag),graph2(yy,mark,34),mark);
     return fun2(mt,yy,55,33,34,my,ma,oy.ma,oy.mb,mg,mh2)
   }));
   const stepProof=generalize(xx,generalize(yy,abs(stepHyp,oy.end(next))));assert(stepProof.f===STEP,'step');
   const out=apply(ir,omega,bp,stepProof);assert(out.f===goal,'agreement');return out
 });
 rows.push(row('denominator_agreement_from_exact_clauses',result));
 return {rows,source_clauses:premiseIds,comparison_graph_slot:H,source_formula_bytes:premiseIds.map(i=>({index:i,bytes:ns[clauses[i]].u})),base_discharged:true,step_discharged:true,formula_nodes:ns.length-1,actual_rh_proof:false};
}
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/denominator.mjs')){const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(denominator(transport,kernel,raw,process.argv.includes('--local')?'local':'all'),null,2));}
