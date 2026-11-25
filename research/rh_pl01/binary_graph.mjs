// RH-PL-18: realize a natural ternary relation as a bounded binary graph.
// A carrier containing W and P(P(W)) bounds the outer Kuratowski pair.
import {pairs} from './pairs.mjs';
import {makeDenominatorPredicates} from './denominator_predicates.mjs';

function prepare(raw,sharedCtx=null,options={}){
 const ctx=sharedCtx??pairs.prepare(raw),{p,t,ar,ns,pair,pairProof,inject,bound,doubleExists,witness,pack,all,allP,and,orLeft,orRight,refl}=ctx;
 const {apply,inst,nest,move,symmetric,replace}=t,{imp,gen}=ar;
 const {E,M,A,F,X,fv,sub,split,qAt,exAt,hyp,ax,mp,generalize,abs,left,right,conj,ui,exIntro}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const W=options.W??37,T=options.T??64;
 const source=makeDenominatorPredicates(ctx,raw,{W,MUL:options.sourceGraph??8});
 const relation=options.relation??source.mul,nat=x=>M(x,W);
 const template=relation(70,71,72);
 assert(ns[template]&&![0,1,2,73,T].some(x=>fv(template).has(x)),'relation parameter collides with constructor or schema slots');
 assert(![0,1,2,70,71,72,73].includes(T)&&T!==W,'graph witness slot collision');
 // Reserve the fixed helper slots and every variable appearing in the
 // supplied relation before allocating the constructor's private variables.
 const used=new Set(Array.from({length:120},(_,i)=>i)),seen=new Set(),todo=[template];used.add(T);used.add(W);
 while(todo.length){const id=todo.pop();if(seen.has(id))continue;seen.add(id);const n=ns[id];
   if(n.tag==='e'||n.tag==='m'){used.add(n.x);used.add(n.y)}
   else if(n.tag==='n')todo.push(n.x);
   else if(n.tag==='i')todo.push(n.x,n.y);
   else{used.add(n.x);todo.push(n.y)}
 }
 let next=120;const fresh=()=>{while(used.has(next))next++;used.add(next);return next++};
 const [P,Q,D,S,PS,QS,cy,ca,cb,cp,ip,iq,wy,wa,wb,wp,np,nq,mark,out]=Array.from({length:20},fresh);
 const subset=(s,q)=>gen(3,imp(M(3,s),M(3,q)));
 const power=(s,q)=>gen(2,F(M(2,q),subset(2,s)));
 const exactTemplate=makeDenominatorPredicates(ctx,raw,{W,MUL:T}).mt;
 const total2=g=>sub(exactTemplate,T,g);
 const app=(g,x,y,z)=>{
   const q=[x,y,z,x].reduce((r,v)=>qAt(r,v),split(total2(g))[1]);
   return split(ns[ns[q].y].x)[0];
 };
 const relationSpec=g=>all([70,71,72],imp(and([nat(70),nat(71),nat(72)]),F(app(g,70,71,72),relation(70,71,72))));
 const totalRelation=all([70,71],imp(A(nat(70),nat(71)),X(72,A(nat(72),relation(70,71,72)))));
 const functionalRelation=all([70,71,72,73],imp(and([nat(70),nat(71),nat(72),nat(73)]),imp(A(relation(70,71,72),relation(70,71,73)),E(72,73))));
 const existsMany=(xs,formula)=>xs.reduceRight((f,x)=>X(x,f),formula);
 const candidate=q=>existsMany([cy,ca,cb,cp],and([nat(cy),nat(ca),nat(cb),pair(cp,cy,ca),pair(q,cp,cb),relation(cy,ca,cb)]));
 const phi=candidate(0);
 assert(fv(phi).has(0)&&!fv(phi).has(1)&&!fv(phi).has(2),'separation parameter scope');
 const sep=ax(X(2,gen(0,F(M(0,2),A(M(0,1),phi)))));
 const pow=ax(gen(0,X(1,power(0,1))));
 const union=ax(gen(0,X(1,gen(2,F(M(2,1),X(3,A(M(3,0),M(2,3))))))));
 assert(sep.detail==='separation'&&pow.detail==='power'&&union.detail==='union','bounded graph set axioms');
 const pairAll=allP([40,41],pairProof),injectAll=allP([40,41,42,43,44],inject),boundAll=allP([40,41,44,45,46,47],bound);
 function unpack(proof,count){const r=[];for(let i=1;i<count;i++){r.push(left(proof));proof=right(proof)}r.push(proof);return r}
 function pairBound(x,y,z,carrier,power1,power2,mx,my,hp1,hp2,hpair){
   const theorem=inst(boundAll,x,y,z,carrier,power1,power2),pieces=[];let rem=ns[theorem.f].x;
   for(let i=0;i<4;i++){const [first,rest]=split(rem);pieces.push(first);rem=rest}pieces.push(rem);
   return mp(nest(mx,my,move(hp1,pieces[2]),move(hp2,pieces[3]),hpair),theorem);
 }
 function candidateIntro(q,x,y,z,inner,mx,my,mz,hinner,houter,r){
   const eY=candidate(q),eA=exAt(eY,x),eB=exAt(eA,y),eP=exAt(eB,z);
   const body=nest(mx,my,mz,hinner,houter,r);
   return exIntro(eY,x,exIntro(eA,y,exIntro(eB,z,exIntro(eP,inner,body))));
 }

 const realizationGoal=X(T,relationSpec(T));
 const realization=witness(ui(pow,W),P,hP=>witness(ui(pow,P),Q,hQ=>
   witness(doubleExists(W,Q,D),D,hD=>witness(ui(union,D),S,hS=>
   witness(ui(pow,S),PS,hPS=>witness(ui(pow,PS),QS,hQS=>{
     // S is W union P(P(W)); these are the only carrier inclusions needed.
     function intoCarrier(z,which,member){
       const inD=which===W?mp(orLeft(refl(W),E(W,Q)),right(ui(hD,W))):mp(orRight(E(Q,W),refl(Q)),right(ui(hD,Q)));
       const q=ui(hS,z),target=ns[right(q).f].x;
       return mp(exIntro(target,which,conj(inD,member)),right(q));
     }
     const separated=ui(generalize(1,sep),QS);
     return witness(separated,T,hT=>{
       const [x,y,z]=[70,71,72],hNat=hyp(and([nat(x),nat(y),nat(z)])),[mx,my,mz]=unpack(hNat,3);
       const application=hyp(app(T,x,y,z));
       const forward=witness(application,ip,hp=>witness(hp,iq,hq=>{
         const [inner0,outer0,member]=unpack(hq,3),inner=move(inner0,pair(ip,x,y)),outer=move(outer0,pair(iq,ip,z));
         const selected=right(mp(member,left(ui(hT,iq))));
         return witness(selected,wy,hy=>witness(hy,wa,ha=>witness(ha,wb,hb=>witness(hb,wp,hc=>{
           const [, , ,oldInner,oldOuter,r]=unpack(hc,6);
           const outerEq=mp(conj(outer,oldOuter),inst(injectAll,ip,z,wp,wb,iq));
           const movedInner=replace(oldInner,symmetric(left(outerEq)),pair(mark,wy,wa),mark);
           const innerEq=mp(conj(inner,movedInner),inst(injectAll,x,y,wy,wa,ip));
           let value=replace(r,symmetric(left(innerEq)),relation(mark,wa,wb),mark);
           value=replace(value,symmetric(right(innerEq)),relation(x,mark,wb),mark);
           return replace(value,symmetric(right(outerEq)),relation(x,y,mark),mark);
         }))));
       }));
       const hR=hyp(relation(x,y,z));
       const reverse=witness(inst(pairAll,x,y),np,hInner=>witness(inst(pairAll,np,z),nq,hOuter=>{
         const innerInQ=pairBound(x,y,np,W,P,Q,mx,my,hP,hQ,hInner);
         const innerInS=intoCarrier(np,Q,innerInQ),valueInS=intoCarrier(z,W,mz);
         const outerInQS=pairBound(np,z,nq,S,PS,QS,innerInS,valueInS,hPS,hQS,hOuter);
         const selected=candidateIntro(nq,x,y,z,np,mx,my,mz,hInner,hOuter,hR);
         const member=mp(conj(outerInQS,selected),right(ui(hT,nq)));
         const outerExists=exAt(app(T,x,y,z),np),body=exAt(outerExists,nq);
         const result=exIntro(app(T,x,y,z),np,exIntro(outerExists,nq,move(nest(hInner,hOuter,member),body)));
         return result;
       }));
       const equivalence=conj(abs(application,forward),abs(hR,reverse));
       const spec=allP([x,y,z],abs(hNat,equivalence));
       assert(spec.f===relationSpec(T),'exact natural binary application relation');
       return exIntro(realizationGoal,T,spec);
     });
   }))))));
 assert(realization.f===realizationGoal&&realization.deps.size===0,'bounded relation realization');

 const premises=[totalRelation,functionalRelation],goal=X(T,A(total2(T),relationSpec(T)));
 const result=pack(premises,(rt,rf)=>witness(realization,T,spec=>{
   const [totalTarget,funTarget]=split(total2(T));
   const [x,y,z,v]=[70,71,72,73],hxy=hyp(A(nat(x),nat(y))),mx=left(hxy),my=right(hxy);
   const existsR=mp(hxy,inst(rt,x,y)),exactBody=qAt(qAt(totalTarget,x),y),existTarget=ns[exactBody].y;
   const totalValue=witness(existsR,out,hOut=>{
     const mz=left(hOut),r=right(hOut),equivalence=mp(nest(mx,my,mz),inst(spec,x,y,out));
     const graph=mp(r,right(equivalence));
     return exIntro(existTarget,out,move(conj(mz,graph),exAt(existTarget,out)));
   });
   const totalProof=move(allP([x,y],abs(hxy,totalValue)),totalTarget);
   const body=[x,y,z,v].reduce((f,a)=>qAt(f,a),funTarget),hAll=hyp(ns[body].x),hApps=hyp(ns[ns[body].y].x);
   const [mx2,my2,mz,mv]=unpack(hAll,4),gz=move(left(hApps),app(T,x,y,z)),gv=move(right(hApps),app(T,x,y,v));
   const rz=mp(gz,left(mp(nest(mx2,my2,mz),inst(spec,x,y,z))));
   const rv=mp(gv,left(mp(nest(mx2,my2,mv),inst(spec,x,y,v))));
   const equal=mp(conj(rz,rv),mp(hAll,inst(rf,x,y,z,v)));
   const funProof=move(allP([x,y,z,v],abs(hAll,abs(hApps,equal))),funTarget);
   return exIntro(goal,T,conj(conj(totalProof,funProof),spec));
 }));
 assert(ns[result.f].x===and(premises)&&ns[result.f].y===goal,'total binary graph construction');
 function run(cap=48000000){
   return [['bounded_natural_binary_relation_realization',realization],['total_functional_binary_relation_graph_exists',result]].map(([name,proof])=>{
     const row=ctx.get(name,proof,cap);
     Object.assign(row.receipt,{natural_domain_variable:W,graph_witness_variable:T,
       relation_formula_bytes:ns[template].u,carrier:'W union P(P(W))',outer_bound:'P(P(carrier))',
       exact_total2_from_frozen_clause_6:true,actual_rh_proof:false});
     return row;
   });
 }
 return {ctx,W,T,relation,totalRelation,functionalRelation,premises,relationSpec,total2,app,realization,realizationGoal,result,goal,run};
}
export const binaryGraph={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/binary_graph.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(binaryGraph.prepare(raw).run().map(row=>row.receipt),null,2));
}
