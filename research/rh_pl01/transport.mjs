// RH-PL-11: derived alpha conversion, equality transport, and extensional uniqueness.
import {induction} from './induction.mjs';
import {kernel} from './kernel.mjs';
function buildTransport(ind,k){
 function prepare(raw){
 const p=ind.prepare(raw),ar=p.ar,ns=ar.nodes,{imp,neg,gen}=ar,{E,M,A,F,O,X,fv,sub,split,hyp,ax,mp,generalize,abs,comp,left,right,conj,ui,introAt,identity,lift,contra}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const apply=(q,...args)=>args.reduce((r,h)=>mp(h,r),q);
 const inst=(q,...xs)=>xs.reduce((r,x)=>ui(r,x),q);
 const nest=(...ps)=>ps.reduceRight((r,q)=>conj(q,r));
 const freshCache=new Map();
 function variables(f){if(freshCache.has(f))return freshCache.get(f);const n=ns[f];let s;
   if(n.tag==='e'||n.tag==='m')s=new Set([n.x,n.y]);else if(n.tag==='n')s=variables(n.x);else if(n.tag==='i')s=new Set([...variables(n.x),...variables(n.y)]);else s=new Set([n.x,...variables(n.y)]);freshCache.set(f,s);return s}
 function fresh(...fs){const used=new Set(fs.flatMap(f=>[...variables(f)]));let t=0;while(used.has(t))t++;return t}
 const alphaCache=new Map(),transportCache=new Map();
 function alpha(s,t){
   const key=s+':'+t;if(alphaCache.has(key))return alphaCache.get(key);
   let r;const a=ns[s],b=ns[t];
   if(s===t)r=identity(s);
   else{
     assert(a.tag===b.tag,'alpha tags differ');
     if(a.tag==='n')r=contra(alpha(b.x,a.x));
     else if(a.tag==='i'){
       const H=hyp(s),J=hyp(b.x);
       const ans=apply(alpha(a.y,b.y),mp(apply(alpha(b.x,a.x),J),H));
       r=abs(H,abs(J,ans));
     }else if(a.tag==='a'){
       const z=fresh(s,t),H=hyp(s);
       const ans=apply(alpha(p.logic.qAt(s,z),p.logic.qAt(t,z)),ui(H,z));
       r=abs(H,introAt(ans,z,t));
     }else throw Error('alpha atoms differ');
   }
   assert(r.f===imp(s,t)&&r.deps.size===0,'alpha result');alphaCache.set(key,r);return r
 }
 const move=(q,t)=>q.f===t?q:apply(alpha(q.f,t),q);
 function symmetric(e){
   const {x,y}=ns[e.f];assert(ns[e.f].tag==='e','not equality');
   return apply(ax(imp(e.f,imp(E(x,x),E(y,x)))),e,ax(E(x,x)));
 }
 function trans(e,f){
   const a=ns[e.f],b=ns[f.f];assert(a.tag==='e'&&b.tag==='e'&&a.y===b.x,'equality chain');
   return apply(ax(imp(f.f,imp(e.f,E(a.x,b.y)))),f,e)
 }
 // Derive equality substitution for an arbitrary formula with a free
 // placeholder. Reversed transport uses the SAME template, not the
 // substituted formula, so unrelated occurrences of y are preserved.
 function transport(t,v,x,y){
   const key=[t,v,x,y].join(':');if(transportCache.has(key))return transportCache.get(key);
   const a=sub(t,v,x),b=sub(t,v,y),eq=E(x,y),n=ns[t];
   let r;
   if(a===b)r=lift(eq,identity(a));
   else{
     const H=hyp(eq),J=hyp(a);let out;
     const forward=(s,q)=>apply(transport(s,v,x,y),H,q);
     const backward=(s,q)=>apply(transport(s,v,y,x),symmetric(H),q);
     if(n.tag==='e'||n.tag==='m'){
       let cur=J,uv=[ns[a].x,ns[a].y];const atom=n.tag==='e'?E:M;
       for(let i=0;i<2;i++)if([n.x,n.y][i]===v){uv[i]=y;const next=atom(...uv);if(next!==cur.f)cur=apply(ax(imp(eq,imp(cur.f,next))),H,cur)}
       out=cur;
     }else if(n.tag==='n'){
       const h=hyp(sub(n.x,v,y));
       out=apply(contra(abs(h,backward(n.x,h))),J);
     }else if(n.tag==='i'){
       const h=hyp(sub(n.x,v,y));out=abs(h,forward(n.y,mp(backward(n.x,h),J)));
     }else{
       assert(n.x!==x&&n.x!==y&&n.x!==v,'active binder collision');
       out=generalize(n.x,forward(n.y,ui(J,n.x)));
     }
     assert(out.f===b,'transport conclusion');r=abs(H,abs(J,out));
   }
   assert(r.f===imp(eq,imp(a,b))&&r.deps.size===0,'transport root');transportCache.set(key,r);return r;
 }
 function replace(q,e,t,v){const n=ns[e.f];assert(n.tag==='e'&&sub(t,v,n.x)===q.f,'transport input');return apply(transport(t,v,n.x,n.y),e,q)}
 const ext=ax(gen(0,gen(1,imp(gen(2,F(M(2,0),M(2,1))),E(0,1)))));
 assert(ext.detail==='extensionality','extensionality axiom');
 const empty=x=>gen(23,neg(M(23,x))),succ=(x,y)=>gen(23,F(M(23,y),O(M(23,x),E(23,x))));
 function eqFromExt(s,t,point){
   const e=inst(ext,s,t),target=ns[e.f].x,z=fresh(target,E(s,t)),pointProof=point(z);
   return mp(introAt(pointProof,z,target),e)
 }
 function emptyUnique(x,y,ex,ey){
   ex=move(ex,empty(x));ey=move(ey,empty(y));
   return eqFromExt(x,y,z=>{
     const a=ui(ex,z),b=ui(ey,z),u=M(z,x),v=M(z,y);
     function explosion(p,q,n){const c=mp(n,ax(imp(n.f,imp(neg(q),n.f))));return mp(c,ax(imp(c.f,imp(p,q))))}
     return conj(explosion(u,v,a),explosion(v,u,b))
   })
 }
 function succUnique(x,y,z,s,t){
   s=move(s,succ(x,y));t=move(t,succ(x,z));
   return eqFromExt(y,z,u=>{const a=ui(s,u),b=ui(t,u);return conj(comp(left(a),right(b)),comp(left(b),right(a)))})
 }
 function controls(){
   const cases=[
    ['atomic_double',E(0,0),0,4,5],
    ['unchanged_occurrence',M(0,5),0,4,5],
    ['negative',neg(M(0,5)),0,4,5],
    ['implication',imp(M(0,5),E(0,5)),0,4,5],
    ['quantifier',gen(6,imp(M(6,0),M(0,5))),0,4,5],
    ['graph',p.at(8,0,4),0,50,51]
   ];
   const rows=[];
   for(const [name,f,v,x,y] of cases){const root=p.close(transport(f,v,x,y)),r=p.replay(root,16000000);rows.push({name,...r.cost,original:r.original})}
   const s=gen(6,imp(M(6,4),X(7,E(7,6)))),t=gen(9,imp(M(9,4),X(10,E(10,9))));
   const root=p.close(alpha(s,t)),r=p.replay(root,16000000);rows.push({name:'alpha_nested',...r.cost,original:r.original});
   const e=hyp(empty(50)),f=hyp(empty(51)),u=p.close(abs(e,abs(f,emptyUnique(50,51,e,f)))),er=p.replay(u,16000000);rows.push({name:'empty_unique',...er.cost,original:er.original});
   const l=hyp(succ(50,51)),h=hyp(succ(50,52)),v=p.close(abs(l,abs(h,succUnique(50,51,52,l,h)))),sr=p.replay(v,16000000);rows.push({name:'successor_unique',...sr.cost,original:sr.original});
   const bads=[()=>alpha(M(0,4),M(0,5)),()=>transport(gen(5,M(0,5)),0,4,5),()=>replace(hyp(M(4,6)),hyp(E(4,5)),M(0,7),0)];
   let rejects=0;for(const fn of bads){let failed=false;try{fn()}catch{failed=true}assert(failed,'bad transport accepted');rejects++}
   return {rows,negative_rejected:rejects,alpha_cache:alphaCache.size,transport_cache:transportCache.size}
 }
 return {p,ar,ns,apply,inst,nest,alpha,move,symmetric,trans,transport,replace,emptyUnique,succUnique,empty,succ,controls};
 }
 return {prepare}
}
export const transport=buildTransport(induction,kernel);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/transport.mjs')){const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(transport.prepare(raw).controls(),null,2));}
