// RH-PL-10: derive graph recurrence agreement from common base and coherent update.
import {induction} from './induction.mjs';
import {readFileSync} from 'node:fs';
function recurrenceAgreement(ind,raw){
 const p=ind.prepare(raw),ar=p.ar,ns=ar.nodes,{imp,neg,gen}=ar,{E,M,A,F,O,X,fv,sub,split,exAt,qAt,hyp,ax,mp,generalize,abs,left,right,conj,ui,exElim}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const w=1,g=8,h=5,b0=4;
 const empty=x=>gen(23,neg(M(23,x))),succ=(x,y)=>gen(23,F(M(23,y),O(M(23,x),E(23,x))));
 const at=(graph,x,y)=>p.at(graph,x,y);
 const phi=gen(33,gen(34,imp(A(M(33,w),A(M(34,w),A(at(g,0,33),at(h,0,34)))),E(33,34))));
 const induction=p.prove(phi);
 const P=x=>sub(phi,0,x);
 const quantify=(xs,f)=>xs.reduceRight((r,x)=>gen(x,r),f);
 const chain=(fs,out)=>fs.reduceRight((r,f)=>imp(f,r),out);
 const total=graph=>gen(35,imp(M(35,w),X(36,A(M(36,w),at(graph,35,36)))));
 const base=graph=>quantify([35,36],chain([empty(35),M(35,w),M(36,w),at(graph,35,36)],E(36,b0)));
 const [x,y,u,v,j,l]=[35,36,37,38,39,40];
 const coherence=quantify([x,y,u,v,j,l],chain([M(x,w),M(y,w),M(u,w),M(v,w),M(j,w),M(l,w),succ(x,y),at(g,x,u),at(h,x,v),at(g,y,j),at(h,y,l),E(u,v)],E(j,l)));
 const premises=[p.omegaW,total(g),total(h),base(g),base(h),coherence];
 const packageF=premises.reduceRight((r,f)=>A(f,r));
 const H=hyp(packageF),proofs=[];let rest=H;
 for(let i=0;i<premises.length-1;i++){proofs.push(left(rest));rest=right(rest)}proofs.push(rest);
 assert(proofs.every((q,i)=>q.f===premises[i]),'premise mismatch');
 const [omega,tg,th,bg,bh,coh]=proofs;
 const inst=(q,xs)=>xs.reduce((r,x)=>ui(r,x),q);
 const apply=(q,ps)=>ps.reduce((r,x)=>mp(x,r),q);
 function outputs(n){
   const target=ns[qAt(qAt(P(n),33),34)],Hout=hyp(target.x);
   const ma=left(Hout),q=right(Hout),mb=left(q),r=right(q),ga=left(r),hb=right(r);
   return {Hout,ma,mb,ga,hb,finish:e=>generalize(33,generalize(34,abs(Hout,e)))};
 }
 // Base: every empty core element is sent to a common initial value.
 // Equality symmetry and transitivity use two actual atomic equality
 // substitution instances and reflexivity.
 const z=20,Hb=hyp(A(empty(z),M(z,w))),ez=left(Hb),mz=right(Hb),ob=outputs(z);
 const ea=apply(inst(bg,[z,33]),[ez,mz,ob.ma,ob.ga]);
 const eb=apply(inst(bh,[z,34]),[ez,mz,ob.mb,ob.hb]);
 const refl=ax(E(34,34)),sym=mp(refl,mp(eb,ax(imp(E(34,b0),imp(E(34,34),E(b0,34))))));
 const eq=mp(ea,mp(sym,ax(imp(E(b0,34),imp(E(33,b0),E(33,34))))));
 const pb=ob.finish(eq);assert(pb.f===P(z),'base predicate');
 const baseProof=generalize(z,abs(Hb,pb));assert(baseProof.f===induction.base,'base root');
 // Step: two total graphs provide witnesses at the predecessor.
 // Agreement and common update coherence force agreement of arbitrary
 // two output witnesses at the successor.
 const xx=21,yy=22,Hs=hyp(A(M(xx,w),A(M(yy,w),A(succ(xx,yy),P(xx)))));
 const mx=left(Hs),s1=right(Hs),my=left(s1),s2=right(s1),suc=left(s2),prev=right(s2);
 const oy=outputs(yy);
 const eg=mp(mx,ui(tg,xx)),eh=mp(mx,ui(th,xx)),aa=41,bb=42;
 const Ha=hyp(exAt(eg.f,aa)),Hb2=hyp(exAt(eh.f,bb)),maa=left(Ha),ga=right(Ha),mbb=left(Hb2),hb2=right(Hb2);
 const agree=mp(conj(maa,conj(mbb,conj(ga,hb2))),inst(prev,[aa,bb]));
 const equalNext=apply(inst(coh,[xx,yy,aa,bb,33,34]),[mx,my,maa,mbb,oy.ma,oy.mb,suc,ga,hb2,oy.ga,oy.hb,agree]);
 const afterB=exElim(eh,bb,Hb2,equalNext),afterA=exElim(eg,aa,Ha,afterB);
 const py=oy.finish(afterA);assert(py.f===P(yy),'step predicate');
 const stepProof=generalize(xx,generalize(yy,abs(Hs,py)));assert(stepProof.f===induction.step,'step root');
 const goal=apply(induction.result,[omega,baseProof,stepProof]);assert(goal.f===induction.goal,'agreement goal');
 const theorem=abs(H,goal),closed=p.close(theorem),r=p.emit(closed);
 assert(fv(closed.f).size===0,'open root');
 // Individual base/step derivations still depend on the package; the
 // theorem above discharges that package and the checker replays every
 // reachable leaf and inference with no hypotheses.
 const noGraph=ar.intern(['m',0,4]);
 assert(p.prove(noGraph).result.deps.size===0,'repeat induction');
 return {theorem_ast:kencode(ar.ast(closed.f)),target_bytes:ns[closed.f].u,...r.cost,axioms:r.axioms,structural_replay:true,original_full_replay:false,base_derived:true,step_derived:true,agreement_derived:true,premises:premises.map(f=>ns[f].u),actual_rh_proof:false};
 function kencode(f){return (function go(a){const v=x=>'v'+'1'.repeat(x)+'0';switch(a[0]){case'e':case'm':return a[0]+v(a[1])+v(a[2]);case'n':return 'n'+go(a[1]);case'i':return 'i'+go(a[1])+go(a[2]);case'a':return 'a'+v(a[1])+go(a[2])}})(f)}
}
const {theorem_ast,...receipt}=recurrenceAgreement(induction,readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8'));if(process.argv.includes('--target'))process.stdout.write(theorem_ast+'\n');else console.log(JSON.stringify(receipt,null,2));
