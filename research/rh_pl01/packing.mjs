// RH-PL-07: bounded grammar coverage and two-model semantic packing.
import {kernel} from './kernel.mjs';
import {bounds} from './bounds.mjs';
import {spine} from './spine.mjs';
import {semantic} from './semantic.mjs';
function buildPacking(k,b,sp,sem){
 const {E,M,N,I,Q,X,A,F,encode,decode,free,axiom}=k;
 const sep=phi=>X(2,Q(0,F(M(0,2),A(M(0,1),phi))));
 function pClass(f,x=0){
   if(!free(f).has(x))return "constant";
   if(f[0]==='e'||f[0]==='m')return "atom";
   if(f[0]==='n')return pClass(f[1],x)===null?null:"boolean";
   if(f[0]==='i')return pClass(f[1],x)===null||pClass(f[2],x)===null?null:"boolean";
   const y=f[1];
   if(!free(f[2]).has(y))return pClass(f[2],x)===null?null:"vacuous";
   function simplify(g){
     switch(g[0]){
      case'e':case'm':return g;
      case'n':return N(simplify(g[1]));
      case'i':return I(simplify(g[1]),simplify(g[2]));
      case'a':return free(g[2]).has(g[1])?Q(g[1],simplify(g[2])):simplify(g[2]);
     }
   }
   const body=simplify(f[2]);
   function local(g){
     if(!free(g).has(y))return pClass(g,x)!==null;
     if(g[0]==='e'||g[0]==='m')return g.slice(1).every(v=>v===x||v===y);
     if(g[0]==='n')return local(g[1]);
     if(g[0]==='i')return local(g[1])&&local(g[2]);
     return false;
   }
   if(local(body))return "local-quantifier";
   function factor(g){
     const fv=free(g);
     if(!fv.has(y))return pClass(g,x)!==null;
     if(!fv.has(x))return true;
     if(g[0]==='n')return factor(g[1]);
     if(g[0]==='i')return factor(g[1])&&factor(g[2]);
     return false;
   }
   return factor(body)?"factor-quantifier":null;
 }
 function reduced(f){
   if(f[0]==='e'||f[0]==='m')return {atoms:1,rank:0};
   if(f[0]==='n')return reduced(f[1]);
   if(f[0]==='i'){const l=reduced(f[1]),r=reduced(f[2]);return {atoms:l.atoms+r.atoms,rank:Math.max(l.rank,r.rank)}}
   const t=reduced(f[2]);
   return {atoms:t.atoms,rank:t.atoms===1||!free(f[2]).has(f[1])?t.rank:t.rank+1};
 }
 function cClass(f,x=0){
   if(!free(f).has(x))return 'constant';
   if(reduced(f).rank<=1)return 'reduced-rank-one';
   if(f[0]==='n')return cClass(f[1],x)===null?null:'boolean';
   if(f[0]==='i')return cClass(f[1],x)===null||cClass(f[2],x)===null?null:'boolean';
   if(f[0]==='a'&&!free(f[2]).has(f[1]))return cClass(f[2],x)===null?null:'vacuous';
   return null;
 }
 function run(raw){
   const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
   const all=b.formulae(22),counts={},pClasses={},cClasses={};
   let admissible=0,pChecked=0,cChecked=0,p20Unclassified=0;
   for(const phi of all){
     if(free(phi).has(2))continue;
     const len=encode(phi).length;admissible++;counts[len]=(counts[len]||0)+1;
     const cc=cClass(phi);assert(cc!==null,'C classification failed');cClasses[cc]=(cClasses[cc]||0)+1;cChecked++;
     if(len<=20){
       const pc=pClass(phi);
       if(len<=19){assert(pc!==null,'P classification failed');pChecked++;pClasses[pc]=(pClasses[pc]||0)+1}
       else if(pc===null)p20Unclassified++;
     }
   }
   const witness=Q(1,I(M(1,3),M(0,1)));
   assert(encode(witness).length===20&&axiom(sep(witness))==='separation','P witness');
   assert(pClass(witness)===null&&cClass(witness)!==null,'witness distinguished');
   const unionBody=X(3,A(M(3,0),M(2,3)));
   const union=Q(0,X(1,Q(2,F(M(2,1),unionBody))));
   const powerBody=Q(3,I(M(3,2),M(3,0)));
   const power=Q(0,X(1,Q(2,F(M(2,1),powerBody))));
   assert(axiom(union)==='union'&&axiom(power)==='power','fixed axioms');
   const f=decode(raw.slice(0,-1));assert(encode(f)+'\n'===raw,'target');
   const rows=Object.entries(sp.encodings).map(([name,enc])=>{
     const pCost=enc.encode(power).length+1,uCost=enc.encode(union).length+1;
     const pFloor=name==='unary'?enc.encode(sep(witness)).length+1:uCost;
     const yC=pCost,yP=uCost-yC;
     assert(yC>=0&&yP>=0&&yP<=pFloor,'dual');
     let exact=0,pairs=0,optimal=0;
     for(let a=0;a<=pCost;a++)for(let v=0;v<=pFloor;v++){
       if(a+v>uCost)continue;pairs++;
       if(a+v>exact){exact=a+v;optimal=1}else if(a+v===exact)optimal++;
     }
     assert(exact===uCost&&yC+yP===exact,'dual optimum');
     return {encoding:name,power_cost:pCost,union_cost:uCost,p_witness_separation_cost:enc.encode(sep(witness)).length+1,individual_axiom_cost_floors:{C:pCost,P:pFloor},shared_false_axiom_cost_floor:uCost,certificate:{C:yC,P:yP,total:yC+yP},integer_dual_pairs:pairs,optimal_integer_pairs:optimal,...sem.semanticFloor(f,enc,exact)};
   });
   let powerTraceChecks=0,cutChecks=0;
   for(let n=1;n<=10;n++){
     const full=(1<<n)-1;
     for(let mask=0;mask<=full;mask++){
       const s=Array.from({length:n},(_,j)=>j).filter(j=>mask&(1<<j));let trace=0;
       for(let i=0;i<n;i++){
         const initial=Array.from({length:i},(_,j)=>j);
         const enumerated=initial.every(j=>s.includes(j));
         const formula=(mask&((1<<i)-1))===((1<<i)-1);
         assert(enumerated===formula,'power trace');if(formula)trace|=1<<i;powerTraceChecks++;
       }
       const firstMissing=s.length===n?n:Array.from({length:n},(_,i)=>i).find(i=>!s.includes(i));
       assert(trace===((1<<Math.min(n,firstMissing+1))-1),'initial segment trace');
     }
     for(let cut=1;cut<n;cut++){
       const family=Array.from({length:n-cut},(_,j)=>new Set([...Array.from({length:cut+j},(_,i)=>i),n]));
       const intersection=Array.from({length:n},(_,i)=>i).filter(i=>family.every(y=>y.has(i)));
       assert(intersection.length===cut&&intersection.every((x,i)=>x===i),'cut intersection');
       const uni=new Set(Array.from({length:n-cut},(_,j)=>cut+j));
       assert([...uni].every(x=>!intersection.includes(x))&&uni.size+intersection.length===n,'union cut');cutChecks+=2;
     }
   }
   return {all_formulas_through_22:all.length,admissible_separation_through_22:admissible,counts,p_admissible_through_19:pChecked,p_classes:pClasses,p_unclassified_at_20:p20Unclassified,c_admissible_through_22:cChecked,c_classes:cClasses,p_witness:encode(witness),power_trace_checks:powerTraceChecks,cut_surrogate_checks:cutChecks,bounds:rows};
 }
 return {pClass,reduced,cClass,run};
}
export const packing=buildPacking(kernel,bounds,spine,semantic);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/packing.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(packing.run(raw),null,2));
}
