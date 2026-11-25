// RH-PL-09: exact AST-DAG proof sharing and cost-sensitive template selection.
import {kernel} from './kernel.mjs';
import {spine} from './spine.mjs';
import {assembler} from './assembler.mjs';
import {interfaces} from './interfaces.mjs';
function buildCompression(k,sp,a,old){
 const {M,N,I,encode,decode}=k,P=M(0,0),R=M(1,1);
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 function compose(p,q,r){const ab=I(p,q),bc=I(q,r),abc=I(p,bc),ac=I(p,r);return [I(bc,abc),abc,I(abc,I(ab,ac)),I(ab,ac),ac]}
 function identity(p){const pp=I(p,p),x=I(p,I(pp,p)),y=I(p,pp);return [x,y,I(x,I(y,pp)),I(y,pp),pp]}
 function exp(p,q){const h=N(p),c=I(N(q),h),pq=I(p,q);return [I(h,c),I(c,pq),...compose(h,c,pq)]}
 function dne(p){const h=N(N(p)),g=N(p),v=N(h),imp=I(g,v),pq=I(h,p),pp=I(h,h),ppq=I(h,pq);return [...exp(g,v),I(imp,pq),...compose(h,imp,pq),...identity(h),I(ppq,I(pp,pq)),I(pp,pq),pq]}
 function dni(p){const d=I(N(N(N(p))),N(p)),goal=I(p,N(N(p)));return [...dne(N(p)),I(d,goal),goal]}
 function alt(p,q,left,direct){
   const r=I(p,N(q)),h=N(r),goal=left?p:q,neg=N(goal);
   return [...(left?(direct?exp(p,N(q)):old.explosion(p,N(q)).lines):[I(neg,r)]),...(direct?dni(r):old.dni(r).lines),...compose(neg,r,N(h)),I(I(neg,N(h)),I(h,goal)),I(h,goal)];
 }
 function arena(){
   const nodes=[null],index=new Map(),memo=new WeakMap();
   const w=x=>x<36?1:2+x.toString(36).length;
   function make(tag,x,y){
     const key=tag+':'+x+':'+(y??'');if(index.has(key))return index.get(key);
     let u,c;
     if(tag==='e'||tag==='m'){u=5+x+y;c=1+w(x)+w(y)}
     else if(tag==='n'){u=1+nodes[x].u;c=1+nodes[x].c}
     else if(tag==='i'){u=1+nodes[x].u+nodes[y].u;c=1+nodes[x].c+nodes[y].c}
     else if(tag==='a'){u=3+x+nodes[y].u;c=1+w(x)+nodes[y].c}
     else throw Error('tag');
     const id=nodes.length;nodes.push({tag,x,y,u,c});index.set(key,id);return id;
   }
   function intern(f){
     if(memo.has(f))return memo.get(f);let id;
     if(f[0]==='e'||f[0]==='m')id=make(f[0],f[1],f[2]);
     else if(f[0]==='n')id=make('n',intern(f[1]));
     else if(f[0]==='i')id=make('i',intern(f[1]),intern(f[2]));
     else if(f[0]==='a')id=make('a',f[1],intern(f[2]));
     else throw Error('AST');
     memo.set(f,id);return id;
   }
   const imp=(x,y)=>make('i',x,y),neg=x=>make('n',x),gen=(x,y)=>make('a',x,y);
   function ast(id,cache=new Map()){
     if(cache.has(id))return cache.get(id);
     const {tag,x,y}=nodes[id];let f;
     if(tag==='e'||tag==='m')f=[tag,x,y];else if(tag==='n')f=[tag,ast(x,cache)];
     else if(tag==='i')f=[tag,ast(x,cache),ast(y,cache)];else f=[tag,x,ast(y,cache)];
     cache.set(id,f);return f;
   }
   function prop(id){
     const n=nodes[id];if(n.tag!=='i')return false;
     const l=nodes[n.x],r=nodes[n.y];
     if(r.tag==='i'&&r.y===n.x)return true;
     if(l.tag==='i'&&r.tag==='i'){
       const ll=nodes[l.y],ra=nodes[r.x],rb=nodes[r.y];
       if(ll.tag==='i'&&ra.tag==='i'&&rb.tag==='i'&&ra.x===l.x&&rb.x===l.x&&ra.y===ll.x&&rb.y===ll.y)return true;
       const nl=nodes[l.x],nr=nodes[l.y];
       if(nl.tag==='n'&&nr.tag==='n'&&r.x===nr.x&&r.y===nl.x)return true;
     }return false;
   }
   function cost(ids){return ids.reduce((r,id)=>({lines:r.lines+1,unary:r.unary+nodes[id].u+1,compact:r.compact+nodes[id].c+1}),{lines:0,unary:0,compact:0})}
   function book(){
     const seen=new Map(),incoming=new Map(),order=[];
     function add(id){
       if(seen.has(id))return id;const f=nodes[id];let parents;
       if(prop(id))parents=[];else if(f.tag==='a'&&seen.has(f.y))parents=[f.y];
       else{const h=(incoming.get(id)||[]).find(t=>seen.has(nodes[t].x));assert(h!==undefined,'rule failure '+id);parents=[nodes[h].x,h]}
       seen.set(id,parents);order.push(id);
       if(f.tag==='i'){const xs=incoming.get(f.y)||[];xs.push(id);incoming.set(f.y,xs)}
       return id;
     }
     const addAll=ids=>{for(const id of ids)add(id)};
     function slice(roots){const need=new Set(),stack=roots.slice();while(stack.length){const id=stack.pop();if(need.has(id))continue;assert(seen.has(id),'missing root');need.add(id);stack.push(...seen.get(id))}return order.filter(id=>need.has(id))}
     return {add,addAll,slice,order,seen};
   }
   return {nodes,intern,ast,imp,neg,gen,prop,book,cost};
 }
 function prepare(raw){
   const frozen=decode(raw.slice(0,-1));assert(encode(frozen)+'\n'===raw,'frozen target');
   const {vars,hypothesis:D}=a.stripPrefix(frozen),ar=arena(),d=ar.intern(D),p=ar.intern(P),q=ar.intern(R);
   const templates={left:[],right:[]};let axiomCrosschecks=0,templateChecks=0;
   for(const side of ['left','right']){
     const left=side==='left',base=old.elim(P,R,left);
     const candidates=[['baseline',base.lines],['composed',alt(P,R,left,false)],['direct',alt(P,R,left,true)]];
     for(const [name,lines] of candidates){
       const target=lines.at(-1);assert(encode(target)===encode(base.target),'template root');
       assert(a.verifyOpen(lines,target),'original kernel template');templateChecks++;
       const b=ar.book(),rawIds=lines.map(ar.intern);b.addAll(rawIds);
       for(let j=0;j<rawIds.length;j++)if(ar.prop(rawIds[j])){assert(['K','S','classical'].includes(k.axiom(lines[j])),'axiom agreement');axiomCrosschecks++}
       const ids=b.slice([ar.intern(target)]);templates[side].push({name,ids,raw:ar.cost(rawIds),sliced:ar.cost(ids)});
     }
   }
   function subst(id,x,y,cache){
     if(id===p)return x;if(id===q)return y;if(cache.has(id))return cache.get(id);
     const f=ar.nodes[id];let z;
     if(f.tag==='i')z=ar.imp(subst(f.x,x,y,cache),subst(f.y,x,y,cache));else if(f.tag==='n')z=ar.neg(subst(f.x,x,y,cache));else throw Error('schematic atom');
     cache.set(id,z);return z;
   }
   const tails=[d],clauses=[];
   for(let j=0;j<21;j++){const [x,y]=old.split(ar.ast(tails.at(-1)));clauses.push(ar.intern(x));tails.push(ar.intern(y))}
   clauses.push(tails.at(-1));assert(clauses.length===22,'22 clauses');
   const blocks=Array.from({length:21},(_,j)=>Object.fromEntries(['left','right'].map(side=>[side,templates[side].map(t=>{const m=new Map();return {name:t.name,ids:t.ids.map(id=>subst(id,clauses[j],tails[j+1],m))}})])));
   function join(b,root,mid,last){
     const ab=ar.imp(root,mid),bc=ar.imp(mid,last),abc=ar.imp(root,bc),ac=ar.imp(root,last);
     b.addAll([ar.imp(bc,abc),abc,ar.imp(abc,ar.imp(ab,ac)),ar.imp(ab,ac),ac]);return ac;
   }
   function closure(b,id){for(const x of vars.slice().reverse()){id=ar.gen(x,id);b.add(id)}return id}
   function build(mode,indices,closed=true){
     const b=ar.book(),roots=[],choices=[],want=new Set(indices),max=Math.max(...indices);let cur=null;
     for(let j=0;j<=Math.min(max,20);j++){
       const l=want.has(j),r=j<max;if(!l&&!r)continue;
       const left=l?blocks[j].left:[{name:'none',ids:[]}],right=r?blocks[j].right:[{name:'none',ids:[]}];
       let best;
       for(const L of (mode==='baseline'?left.slice(0,1):left))for(const R of (mode==='baseline'?right.slice(0,1):right)){
         const ids=[...new Set([...L.ids,...R.ids])].filter(x=>!b.seen.has(x)),c=ar.cost(ids);
         const score=mode==='compact'?c.compact:c.unary;
         if(!best||score<best.score)best={L,R,score};
       }
       b.addAll(best.L.ids);b.addAll(best.R.ids);choices.push({suffix:j,left:best.L.name,right:best.R.name});
       if(l){const local=ar.imp(tails[j],clauses[j]),id=j===0?local:join(b,d,tails[j],clauses[j]);roots.push(closed?closure(b,id):id)}
       if(r){const local=ar.imp(tails[j],tails[j+1]);cur=j===0?local:join(b,d,tails[j],tails[j+1])}
     }
     if(want.has(21)){assert(cur===ar.imp(d,clauses[21]),'last clause');roots.push(closed?closure(b,cur):cur)}
     const ids=b.slice(roots),check=ar.book();check.addAll(ids);assert(roots.every(id=>check.seen.has(id)),'sliced roots');
     return {ids,roots,cost:ar.cost(ids),choices};
   }
   return {ar,templates,templateChecks,axiomCrosschecks,clauses,build,frozen};
 }
 function run(raw){
   const {ar,templates,templateChecks,axiomCrosschecks,clauses,build,frozen}=prepare(raw);
   const indices=clauses.map((_,j)=>j),results={};
   let fullChecks=0;
   for(const mode of ['baseline','unary','compact']){
     const individual=indices.map(j=>build(mode,[j]).cost),shared=build(mode,indices),open=build(mode,indices,false);
     const sum=individual.reduce((r,c)=>({lines:r.lines+c.lines,unary:r.unary+c.unary,compact:r.compact+c.compact}),{lines:0,unary:0,compact:0});
     const firstTwo=[];
     for(const j of [0,1]){
       const one=build(mode,[j]),asts=one.ids.map(id=>ar.ast(id)),target=ar.ast(one.roots[0]);
       assert(encode(asts.at(-1))===encode(target),'root last');
       assert(k.verify(asts.map(encode).join('\n')+'\n',encode(target)),'original kernel full payload');
       const c=a.cost(asts);assert(c.unary===one.cost.unary&&c.compact===one.cost.compact,'expanded cost');
       fullChecks++;firstTwo.push(c);
     }
     results[mode]={first_two_original_kernel:firstTwo,all_independent:sum,all_shared_closed:shared.cost,all_shared_open:open.cost,individual,choices:shared.choices,root_count:shared.roots.length};
   }
   assert(results.unary.all_shared_closed.unary<=results.baseline.all_shared_closed.unary,'unary regression');
   assert(results.compact.all_shared_closed.compact<=results.baseline.all_shared_closed.compact,'compact regression');
   assert(results.baseline.all_shared_closed.unary<results.baseline.all_independent.unary,'sharing ineffective');
   let reject=false;try{ar.book().add(ar.intern(M(2,2)))}catch{reject=true}assert(reject,'missing premise accepted');
   return {target_formula_bytes:encode(frozen).length,definition_clauses:clauses.length,templates:Object.fromEntries(Object.entries(templates).map(([s,ls])=>[s,ls.map(({name,raw,sliced})=>({name,raw,sliced}))])),results,dag_nodes:ar.nodes.length-1,original_kernel_template_checks:templateChecks,original_kernel_full_payload_checks:fullChecks,axiom_crosschecks:axiomCrosschecks,negative_rejected:reject,actual_rh_proof:false};
 }
 return {prepare,run};
}
export const compression=buildCompression(kernel,spine,assembler,interfaces);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/compression.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 if(process.argv.includes('--emit')){const i=Number(process.argv[process.argv.indexOf('--emit')+1]);const p=compression.prepare(raw);if(!Number.isInteger(i)||i<0||i>=p.clauses.length)throw Error('clause index');const r=p.build(process.argv.includes('--compact')?'compact':'unary',[i]);for(const id of r.ids)process.stdout.write((process.argv.includes('--compact')?spine.compact:kernel.encode)(p.ar.ast(id))+'\n');}
 else console.log(JSON.stringify(compression.run(raw),null,2));
}
