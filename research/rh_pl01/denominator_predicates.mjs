// RH-PL-16: literal frozen denominator clauses and the PL-15 normalized form.
import {kernel} from './kernel.mjs';

export function makeDenominatorPredicates(ctx,raw,{W=37,Z=60,C0=6,MUL=8,G=61}={}){
 const {p,t,ar,ns,all,chain,and}=ctx,{imp,gen,intern}=ar;
 const {E,M,A,X,sub,split,qAt,fv}=p.logic,{empty,succ}=t;
 let f=intern(kernel.decode(raw.slice(0,-1)));
 while(ns[f].tag==='a')f=ns[f].y;
 let rem=ns[f].x;const sourceClauses=[];
 for(let j=0;j<21;j++){const [x,y]=split(rem);sourceClauses.push(x);rem=y}
 sourceClauses.push(rem);
 const slots={0:W,1:Z,2:C0,4:MUL,8:G};
 // The original denominator slot is 8, which is also the new multiplication
 // slot. Temporary variables keep each original parameter independent.
 function simultaneous(formula,mapping){
   const used=new Set(Object.values(mapping)),seen=new Set(),todo=[formula];
   while(todo.length){
     const id=todo.pop();if(seen.has(id))continue;seen.add(id);const n=ns[id];
     if(n.tag==='e'||n.tag==='m'){used.add(n.x);used.add(n.y)}
     else if(n.tag==='n')todo.push(n.x);
     else if(n.tag==='i')todo.push(n.x,n.y);
     else{used.add(n.x);todo.push(n.y)}
   }
   const active=Object.entries(mapping).map(([x,y])=>[Number(x),y]).filter(([x])=>fv(formula).has(x));
   let fresh=100;const swaps=[];
   for(const [from,to] of active){while(used.has(fresh))fresh++;used.add(fresh);swaps.push([from,fresh++,to])}
   for(const [from,temp] of swaps)formula=sub(formula,from,temp);
   for(const [,temp,to] of swaps)formula=sub(formula,temp,to);
   return formula;
 }
 const clause=(index,graph=G)=>simultaneous(sourceClauses[index],{...slots,8:graph});
 const clauses=sourceClauses.map((_,i)=>clause(i));
 const nat=x=>M(x,W),at=(g,x,y)=>p.at(g,x,y),mt=clause(6);
 const qform=(f,...xs)=>xs.reduce((r,x)=>qAt(r,x),f);
 const graph1=(g,x,u)=>{
   const q=qform(split(clause(14,g))[1],x,u,x);
   return split(ns[ns[q].y].x)[0];
 };
 const mul=(x,y,u)=>{
   const q=qform(split(mt)[1],x,y,u,x);
   return split(ns[ns[q].y].x)[0];
 };
 const total=g=>gen(40,imp(nat(40),X(47,A(nat(47),at(g,40,47)))));
 const functional=g=>all([40,42,43],chain([nat(40),nat(42),nat(43),at(g,40,42),at(g,40,43)],E(42,43)));
 const base=g=>all([40,42],chain([empty(40),nat(40),nat(42),at(g,40,42)],E(42,C0)));
 const update=g=>all([40,49,42,43],chain([nat(40),nat(49),nat(42),nat(43),succ(40,49),at(g,40,42),at(g,49,43)],mul(49,42,43)));
 const normalized=g=>and([total(g),functional(g),base(g),update(g)]);
 const exact=g=>and([clause(14,g),clause(19,g),clause(21,g)]);
 return {W,Z,C0,MUL,G,slots,sourceClauses,clauses,clause,simultaneous,nat,at,mul,graph1,total,functional,base,update,normalized,exact,omega:clause(0),mt,qform};
}
