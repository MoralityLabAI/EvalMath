// RH-PL-13: checked graph-union and recursive gluing theorems.
import {transport} from './transport.mjs';
import {kernel} from './kernel.mjs';
function buildGluing(tr,k){
 function prepare(raw){
 const t=tr.prepare(raw),{p,ar,ns,apply,inst,nest,move,empty,succ}=t,{imp,gen,neg}=ar,{E,M,A,F,X,fv,sub,split,qAt,exAt,hyp,ax,mp,generalize,abs,left,right,conj,ui,exIntro,exElim}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const all=(xs,f)=>xs.reduceRight((r,x)=>gen(x,r),f);
 const allProof=(xs,pf)=>xs.reduceRight((r,x)=>generalize(x,r),pf);
 const chain=(fs,f)=>fs.reduceRight((r,s)=>imp(s,r),f);
 const and=fs=>fs.reduceRight((r,s)=>A(s,r));
 function unpack(h,count){const out=[];for(let i=0;i<count-1;i++){out.push(left(h));h=right(h)}out.push(h);return out}
 function witness(pf,v,fn){const h=hyp(exAt(pf.f,v));return exElim(pf,v,h,fn(h))}
 const [W,K,U]=[1,4,5],x=40,y=41,aa=42,bb=43,g=44,h=45;
 const nat=n=>M(n,W),at=(s,n,v)=>p.at(s,n,v);
 const union=ax(gen(0,X(1,gen(2,F(M(2,1),X(3,A(M(3,0),M(2,3))))))));
 assert(union.detail==='union','wrong axiom');
 const existsUnion=ui(union,K);
 const memberFamily=(n,v)=>X(46,A(M(46,K),at(46,n,v)));
 const unionRel=(s)=>all([x,y],F(at(s,x,y),memberFamily(x,y)));
 function proveUnion(){
   return witness(existsUnion,U,hu=>{
     function forward(){
       const ha=hyp(at(U,x,y)),r=witness(ha,50,hp=>{
         const pair=left(hp),mem=right(hp),hit=mp(mem,left(ui(hu,50)));
         return witness(hit,51,hg=>{
           const inFam=left(hg),inGraph=right(hg);
           const a=exIntro(at(51,x,y),50,conj(pair,inGraph));
           return exIntro(memberFamily(x,y),51,conj(inFam,a))
         })
       });
       return abs(ha,r)
     }
     function reverse(){
       const hf=hyp(memberFamily(x,y)),r=witness(hf,51,hg=>{
         const inFam=left(hg),val=right(hg);
         return witness(val,50,hp=>{
           const pair=left(hp),inGraph=right(hp),u=ui(hu,50);
           const rhs=ns[right(u).f].x;
           const hit=exIntro(rhs,51,conj(inFam,inGraph)),mem=mp(hit,right(u));
           return exIntro(at(U,x,y),50,conj(pair,mem))
         })
       });
       return abs(hf,r)
     }
     const rel=generalize(x,generalize(y,conj(forward(),reverse())));
     assert(rel.f===unionRel(U),'union relation');
     return exIntro(X(U,unionRel(U)),U,rel)
   })
 }
 const unionProof=proveUnion();
 const cover=n=>X(46,A(M(46,K),X(47,A(nat(47),at(46,n,47)))));
 const phi=cover(0),ind=p.prove(phi);
 const base=ind.base,step=ind.step;
 const compat=all([g,h,x,aa,bb],chain([M(g,K),M(h,K),nat(x),nat(aa),nat(bb),at(g,x,aa),at(h,x,bb)],E(aa,bb)));
 const total=s=>gen(x,imp(nat(x),X(47,A(nat(47),at(s,x,47)))));
 const functional=s=>all([x,aa,bb],chain([nat(x),nat(aa),nat(bb),at(s,x,aa),at(s,x,bb)],E(aa,bb)));
 const goal=X(U,A(total(U),functional(U)));
 function glue(){
   const premises=[p.omegaW,base,step,compat],H=hyp(and(premises)),[omega,b,st,coh]=unpack(H,4);
   const covered=apply(ind.result,omega,b,st);
   assert(covered.f===ind.goal,'cover induction');
   const r=witness(unionProof,U,rel=>{
     const hx=hyp(nat(x)),cov=mp(hx,ui(covered,x));
     const val=witness(cov,51,hg=>{
       const inFam=left(hg);
       return witness(right(hg),52,hv=>{
         const m=left(hv),a=right(hv),relAt=inst(rel,x,52);
         const inAny=exIntro(memberFamily(x,52),51,conj(inFam,a)),inU=mp(inAny,right(relAt));
         const target=X(47,A(nat(47),at(U,x,47)));
         return exIntro(target,52,conj(m,inU))
       })
     });
     const tf=generalize(x,abs(hx,val));assert(tf.f===total(U),'total');
     const hs=[nat(x),nat(aa),nat(bb),at(U,x,aa),at(U,x,bb)].map(hyp);
     const [mx,ma,mb,au,bu]=hs;
     const ag=mp(au,left(inst(rel,x,aa))),bg=mp(bu,left(inst(rel,x,bb)));
     const eq=witness(ag,51,ha=>witness(bg,52,hb=>apply(inst(coh,51,52,x,aa,bb),left(ha),left(hb),mx,ma,mb,right(ha),right(hb))));
     const ff=allProof([x,aa,bb],hs.reduceRight((r,h)=>abs(h,r),eq));
     assert(ff.f===functional(U),'functional');
     return exIntro(goal,U,conj(tf,ff))
   });
   assert(r.f===goal,'gluing goal');return abs(H,r)
 }
 const glued=glue();
 function row(name,pr,cap=0){const root=p.close(pr),r=cap?p.replay(root,cap):p.emit(root);return {name,target:k.encode(ar.ast(root.f)),target_bytes:ns[root.f].u,...r.cost,axioms:r.axioms,structural_replay:true,original_full_replay:!!r.original}}
 function run(){
   const rows=[row('union_graph_application_equivalence',unionProof,24000000),row('recursive_graph_gluing_existence',glued)];
   const result=rows.map(({target,...r})=>r);
   return {rows:result,premise_formula_bytes:[p.omegaW,base,step,compat].map(i=>ns[i].u),formula_nodes:ns.length-1,actual_rh_proof:false}
 }
 function cert(which='glue'){const root=p.close(which==='union'?unionProof:glued),r=p.emit(root);return {nodes:ar.nodes,ids:r.ids,root:root.f,target:k.encode(ar.ast(root.f)),cost:r.cost}}
 return {run,cert,unionProof,glued,t,p,ar,ns,cover,total,functional,compat,memberFamily,base,step};
 }
 return {prepare};
}
export const gluing=buildGluing(transport,kernel);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/gluing.mjs')){const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(gluing.prepare(raw).run(),null,2));}
