// RH-PL-15: shared formulas for the exact RH-PL-13 bounded-prefix predicate.
import {kernel} from './kernel.mjs';

export function makePrefixPredicates(ctx,raw,{W=37,C0=6,MUL=8}={}){
 const {p,t,ar,ns,all,chain,and}=ctx,{imp,gen,intern}=ar;
 const {E,M,A,F,O,X,sub,split,qAt}=p.logic,{empty,succ}=t;
 let f=intern(kernel.decode(raw.slice(0,-1)));
 while(ns[f].tag==='a')f=ns[f].y;
 let rem=ns[f].x;const clauses=[];
 for(let j=0;j<21;j++){const [x,y]=split(rem);clauses.push(x);rem=y}
 clauses.push(rem);
 const mt=sub(sub(clauses[6],4,MUL),0,W);
 const nat=x=>M(x,W),at=(g,x,y)=>p.at(g,x,y);
 function mul(x,y,z){const q=[x,y,z,x].reduce((r,v)=>qAt(r,v),split(mt)[1]);return split(ns[ns[q].y].x)[0]}
 const subset=(s,q)=>gen(3,imp(M(3,s),M(3,q)));
 const power=(s,q)=>gen(2,F(M(2,q),subset(2,s)));
 const dom=(s,x)=>X(45,A(nat(45),at(s,x,45)));
 const domain=(s,n)=>gen(41,imp(nat(41),F(dom(s,41),O(E(41,n),M(41,n)))));
 const prefixDomain=s=>X(40,A(nat(40),domain(s,40)));
 const functional=s=>all([41,43,44],chain([nat(41),nat(43),nat(44),at(s,41,43),at(s,41,44)],E(43,44)));
 const base=s=>all([41,43],chain([empty(41),nat(41),nat(43),at(s,41,43)],E(43,C0)));
 const step=s=>all([41,42,43,44],chain([nat(41),nat(42),nat(43),nat(44),succ(41,42),at(s,41,43),at(s,42,44)],mul(42,43,44)));
 const good=s=>and([prefixDomain(s),functional(s),base(s),step(s)]);
 const famSpec=(q,g)=>gen(0,F(M(0,g),A(subset(0,q),good(0))));
 return {W,C0,MUL,clauses,mt,nat,at,mul,subset,power,powerDef:power,dom,domain,prefixDomain,functional,base,step,good,famSpec,omega:sub(p.omega0,0,W)};
}
export const prefixPredicates=makePrefixPredicates;
