// RH-PL-13: bounded candidate-family comprehension via power and separation.
import {transport} from './transport.mjs';
import {kernel} from './kernel.mjs';
function buildPrefixFamily(tr,k){
 function prepare(raw){
 const t=tr.prepare(raw),{p,ar,ns,apply,inst,nest,empty,succ}=t,{imp,gen,intern}=ar,{E,M,A,F,O,X,sub,split,qAt,exAt,hyp,ax,mp,generalize,abs,left,right,conj,ui,exIntro,exElim}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)},all=(xs,f)=>xs.reduceRight((r,x)=>gen(x,r),f),chain=(fs,f)=>fs.reduceRight((r,s)=>imp(s,r),f),and=fs=>fs.reduceRight((r,s)=>A(s,r));
 function witness(q,v,fn){const h=hyp(exAt(q.f,v));return exElim(q,v,h,fn(h))}
 let f=intern(k.decode(raw.slice(0,-1)));while(ns[f].tag==='a')f=ns[f].y;let rem=ns[f].x;const clauses=[];for(let j=0;j<21;j++){const [x,y]=split(rem);clauses.push(x);rem=y}clauses.push(rem);
 const W=37,C0=6,MUL=8,S=0,n=40,x=41,y=42,a=43,b=44,P=50,Q=51,R=52,K=53,nat=x=>M(x,W),at=(s,x,a)=>p.at(s,x,a);
 const mt=sub(sub(clauses[6],4,MUL),0,W);
 function mul(x,y,z){const q=[x,y,z,x].reduce((r,v)=>qAt(r,v),split(mt)[1]);return split(ns[ns[q].y].x)[0]}
 const subset=(s,q)=>gen(3,imp(M(3,s),M(3,q)));
 const powerDef=(s,q)=>gen(2,F(M(2,q),subset(2,s)));
 const pow=ax(gen(0,X(1,powerDef(0,1))));
 assert(pow.detail==='power','power axiom');
 const dom=(s,x)=>X(45,A(nat(45),at(s,x,45)));
 const prefixDomain=s=>X(n,A(nat(n),gen(x,imp(nat(x),F(dom(s,x),O(E(x,n),M(x,n)))))));
 const functional=s=>all([x,a,b],chain([nat(x),nat(a),nat(b),at(s,x,a),at(s,x,b)],E(a,b)));
 const base=s=>all([x,a],chain([empty(x),nat(x),nat(a),at(s,x,a)],E(a,C0)));
 const step=s=>all([x,y,a,b],chain([nat(x),nat(y),nat(a),nat(b),succ(x,y),at(s,x,a),at(s,y,b)],mul(y,a,b)));
 const good=s=>and([prefixDomain(s),functional(s),base(s),step(s)]);
 const phi=good(S);
 assert(p.logic.fv(phi).has(S)&&!p.logic.fv(phi).has(1)&&!p.logic.fv(phi).has(2),'separation parameter scope');
 const sep=ax(X(2,gen(0,F(M(0,2),A(M(0,1),phi)))));
 assert(sep.detail==='separation','separation axiom');
 const famSpec=(q,g)=>gen(0,F(M(0,g),A(subset(0,q),phi)));
 const resultBody=and([powerDef(W,P),powerDef(P,Q),famSpec(Q,K)]);
 const goal=X(P,X(Q,X(K,resultBody)));
 const pr=witness(ui(pow,W),P,hp=>{
   const eq=witness(ui(pow,P),Q,hq=>{
     const famExists=ui(generalize(1,sep),R);
     const existsK=witness(ui(pow,Q),R,hr=>witness(famExists,K,hk=>{
       const sepAt=ui(hk,S),powAt=ui(hr,S);
       const h1=hyp(M(S,K)),sp1=mp(h1,left(sepAt));
       const forward=abs(h1,conj(mp(left(sp1),left(powAt)),right(sp1)));
       const h2=hyp(A(subset(S,Q),phi)),mr=mp(left(h2),right(powAt));
       const reverse=abs(h2,mp(conj(mr,right(h2)),right(sepAt)));
       const spec=generalize(S,conj(forward,reverse));assert(spec.f===famSpec(Q,K),'family characterization');
       return exIntro(X(K,resultBody),K,nest(hp,hq,spec))
     }));
     return exIntro(X(Q,X(K,resultBody)),Q,existsK);
   });
   return exIntro(goal,P,eq);
 });
 // The preceding proof returns exists Q exists K ..., with P free
 // inside the witness derivation, so introduce P before eliminating it.
 // (The wrapper below is the exact nesting expected by the checker.)
 assert(pr.f===goal,'family existence target');
 const root=p.close(pr),r=p.emit(root);
 return {raw:{nodes:ar.nodes,ids:r.ids,root:root.f,target:k.encode(ar.ast(root.f)),cost:r.cost},receipt:{name:'bounded_prefix_candidate_family_exists',target_bytes:ns[root.f].u,predicate_bytes:ns[phi].u,...r.cost,axioms:r.axioms,structural_replay:true,original_full_replay:false,actual_rh_proof:false}};
 }
 return {prepare}
}
export const prefixFamily=buildPrefixFamily(transport,kernel);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/prefix_family.mjs')){const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(prefixFamily.prepare(raw).receipt,null,2));}
