// RH-PL-17: exact numerator clauses and the existential normalized update
// used by RH-PL-12, with the arithmetic and graph parameters kept separate.
import {makeDenominatorPredicates} from './denominator_predicates.mjs';

export function makeNumeratorPredicates(ctx,raw,{W=37,Z=60,C0=6,ADD=7,MUL=8,G=62,B=61}={}){
 const {p,t,ar,ns,all,chain,and}=ctx,{imp,gen}=ar;
 const {E,M,A,X,split,qAt}=p.logic,{empty,succ}=t;
 const original=makeDenominatorPredicates(ctx,raw),{sourceClauses,simultaneous}=original;
 const slots={0:W,1:Z,2:C0,3:ADD,4:MUL,7:G,8:B};
 const clause=(index,graph=G,denominator=B)=>simultaneous(sourceClauses[index],{...slots,7:graph,8:denominator});
 const clauses=sourceClauses.map((_,i)=>clause(i));
 const nat=x=>M(x,W),at=(g,x,y)=>p.at(g,x,y),mt=clause(6),addTotal=clause(5);
 const qform=(f,...xs)=>xs.reduce((r,x)=>qAt(r,x),f);
 const graph1=(formula,x,u)=>{
   const q=qform(split(formula)[1],x,u,x);
   return split(ns[ns[q].y].x)[0];
 };
 const graph2=(formula,x,y,u)=>{
   const q=qform(split(formula)[1],x,y,u,x);
   return split(ns[ns[q].y].x)[0];
 };
 const gn=(g,x,u)=>graph1(clause(13,g),x,u);
 const gb=(b,x,u)=>graph1(clause(14,G,b),x,u);
 const mul=(x,y,u)=>graph2(mt,x,y,u),add=(x,y,u)=>graph2(addTotal,x,y,u);
 const total=g=>gen(40,imp(nat(40),X(47,A(nat(47),at(g,40,47)))));
 const functional=g=>all([40,42,43],chain([nat(40),nat(42),nat(43),at(g,40,42),at(g,40,43)],E(42,43)));
 const base=g=>all([40,42],chain([empty(40),nat(40),nat(42),at(g,40,42)],E(42,Z)));
 const updateGoal=(y,a,d,b)=>X(70,A(nat(70),A(mul(y,a,70),add(70,d,b))));
 const update=(g,b=B)=>all([40,49,42,43,44],chain([nat(40),nat(49),nat(42),nat(43),nat(44),succ(40,49),at(g,40,42),at(g,49,43),at(b,40,44)],updateGoal(49,42,44,43)));
 const normalized=(g,b=B)=>and([total(g),functional(g),base(g),update(g,b)]);
 const exact=(g,b=B)=>and([clause(13,g,b),clause(18,g,b),clause(20,g,b)]);
 const denExact=(b=B)=>and([clause(14,G,b),clause(19,G,b),clause(21,G,b)]);
 return {W,Z,C0,ADD,MUL,G,B,slots,sourceClauses,clauses,clause,simultaneous,nat,at,gn,gb,mul,add,total,functional,base,updateGoal,update,normalized,exact,denExact,omega:clause(0),mt,addTotal,qform};
}
