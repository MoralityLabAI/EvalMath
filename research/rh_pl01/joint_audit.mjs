// RH-PL-12: independent certificate replay. No producer parent pointers.
import {kernel} from './kernel.mjs';
import {transport} from './transport.mjs';
import {denominator} from './denominator.mjs';
import {numerator} from './numerator.mjs';
export function certificate(raw){
 const need=new Set(),todo=raw.ids.slice();
 while(todo.length){const i=todo.pop();if(need.has(i))continue;need.add(i);const n=raw.nodes[i];if(!n)throw Error('missing node');if(n.tag==='n')todo.push(n.x);if(n.tag==='i')todo.push(n.x,n.y);if(n.tag==='a')todo.push(n.y)}
 const nodes=[null],map=new Map();
 for(const id of [...need].sort((a,b)=>a-b)){
   const n=raw.nodes[id];let row;
   if(n.tag==='e'||n.tag==='m')row=[n.tag,n.x,n.y];
   else if(n.tag==='n')row=[n.tag,map.get(n.x)];
   else if(n.tag==='i')row=[n.tag,map.get(n.x),map.get(n.y)];
   else if(n.tag==='a')row=[n.tag,n.x,map.get(n.y)];
   else throw Error('node tag');
   map.set(id,nodes.length);nodes.push(row);
 }
 return {version:1,nodes,lines:raw.ids.map(i=>map.get(i)),root:map.get(raw.root),target:raw.target,claimed:{lines:raw.cost.lines,unary:String(raw.cost.unary),compact:String(raw.cost.compact)}};
}
export function verifyCertificate(k,cert){
 const fail=m=>{throw Error(m)},ok=(x,m)=>{if(!x)fail(m)};
 ok(cert.version===1&&Array.isArray(cert.nodes)&&cert.nodes[0]===null&&Array.isArray(cert.lines),'header');
 const nodes=cert.nodes,seenSyntax=new Set(),u=[0n],c=[0n],free=[null];
 const variable=x=>Number.isSafeInteger(x)&&x>=0,child=(x,i)=>Number.isInteger(x)&&x>0&&x<i;
 const cc=x=>BigInt(x<36?1:2+x.toString(36).length);
 for(let i=1;i<nodes.length;i++){
   const n=nodes[i];ok(Array.isArray(n),'node');const [tag,x,y]=n;
   const key=JSON.stringify(n);ok(!seenSyntax.has(key),'noncanonical duplicate node');seenSyntax.add(key);
   if(tag==='e'||tag==='m'){ok(n.length===3&&variable(x)&&variable(y),'atom');u.push(5n+BigInt(x)+BigInt(y));c.push(1n+cc(x)+cc(y));free.push(new Set([x,y]))}
   else if(tag==='n'){ok(n.length===2&&child(x,i),'negation child');u.push(1n+u[x]);c.push(1n+c[x]);free.push(free[x])}
   else if(tag==='i'){ok(n.length===3&&child(x,i)&&child(y,i),'implication child');u.push(1n+u[x]+u[y]);c.push(1n+c[x]+c[y]);free.push(new Set([...free[x],...free[y]]))}
   else if(tag==='a'){ok(n.length===3&&variable(x)&&child(y,i),'quantifier child');u.push(3n+BigInt(x)+u[y]);c.push(1n+cc(x)+c[y]);const s=new Set(free[y]);s.delete(x);free.push(s)}
   else fail('tag');
 }
 const roots=cert.lines;ok(roots.length>0&&roots.at(-1)===cert.root&&child(cert.root,nodes.length)&&free[cert.root].size===0,'root');
 const astMemo=new Map();
 function ast(i){if(astMemo.has(i))return astMemo.get(i);const [t,x,y]=nodes[i];let r;if(t==='n')r=[t,ast(x)];else if(t==='i')r=[t,ast(x),ast(y)];else if(t==='a')r=[t,x,ast(y)];else r=[t,x,y];astMemo.set(i,r);return r}
 ok(k.encode(ast(cert.root))===cert.target,'target mismatch');
 // Pattern matcher uses an independently written declarative schema table,
 // with variables represented by strings and bound by exact DAG node ID.
 const schemas=[
   ['K',['i','P',['i','Q','P']]],
   ['S',['i',['i','P',['i','Q','R']],['i',['i','P','Q'],['i','P','R']]]],
   ['classical',['i',['i',['n','Q'],['n','P']],['i','P','Q']]]
 ];
 function match(p,i,env){if(typeof p==='string'){if(env.has(p))return env.get(p)===i;env.set(p,i);return true}const n=nodes[i];if(n[0]!==p[0]||n.length!==p.length)return false;for(let j=1;j<p.length;j++)if(!match(p[j],n[j],env))return false;return true}
 const seen=new Set(),byConsequent=new Map(),rules={K:0,S:0,classical:0,mp:0,gen:0},axioms={};let unary=0n,compact=0n;
 for(let i=0;i<roots.length;i++){
   const id=roots[i];ok(child(id,nodes.length)&&!seen.has(id),'invalid or duplicate line');const n=nodes[id];let rule=null;
   if(n[0]==='a'&&seen.has(n[2]))rule='gen';
   if(!rule){const prev=byConsequent.get(id)||[];if(prev.some(a=>seen.has(a)))rule='mp'}
   if(!rule){for(const [name,p] of schemas)if(match(p,id,new Map())){rule=name;break}}
   if(rule)rules[rule]++;
   else{const name=k.axiom(ast(id));ok(name,'unjustified line '+i);axioms[name]=(axioms[name]||0)+1}
   seen.add(id);
   if(n[0]==='i'){let a=byConsequent.get(n[2]);if(!a){a=[];byConsequent.set(n[2],a)}a.push(n[1])}
   unary+=u[id]+1n;compact+=c[id]+1n;
 }
 ok(cert.claimed.lines===roots.length&&String(unary)===cert.claimed.unary&&String(compact)===cert.claimed.compact,'cost mismatch');
 return {lines:roots.length,unary:String(unary),compact:String(compact),nodes:nodes.length-1,target_bytes:String(u[cert.root]),rules,nonpropositional_axioms:axioms};
}
export function mutationAudit(k,cert){
 const rejects={};
 function reject(name,obj){let error;try{verifyCertificate(k,obj)}catch(e){error=String(e)}if(!error)throw Error('accepted mutant '+name);rejects[name]=error}
 reject('incorrect_cost',{...cert,claimed:{...cert.claimed,unary:String(BigInt(cert.claimed.unary)+1n)}});
 reject('incorrect_root',{...cert,root:cert.lines[0]});
 const badNodes=cert.nodes.slice();badNodes[1]=['n',1];reject('cyclic_formula',{...cert,nodes:badNodes});
 function ast(i){const [t,x,y]=cert.nodes[i];return t==='n'?[t,ast(x)]:t==='i'?[t,ast(x),ast(y)]:t==='a'?[t,x,ast(y)]:[t,x,y]}
 const sepId=cert.lines.find(i=>{const n=cert.nodes[i];if(n[0]!=='n')return false;const a=cert.nodes[n[1]];return a[0]==='a'&&a[1]===2&&k.axiom(ast(i))==='separation'});
 if(!sepId)throw Error('no separation');
 const without=cert.lines.filter(i=>i!==sepId);
 reject('missing_separation',{...cert,lines:without,claimed:{...cert.claimed,lines:without.length}});
 return rejects;
}
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/joint_audit.mjs')){
 const {readFileSync}=await import('node:fs');
 const inputIndex=process.argv.indexOf('--verify');
 let cert;
 if(inputIndex>=0)cert=JSON.parse(readFileSync(process.argv[inputIndex+1],'utf8'));
 else{const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');cert=certificate(numerator(transport,kernel,denominator,raw,'certificate'));}
 if(process.argv.includes('--emit'))process.stdout.write(JSON.stringify(cert)+'\n');
 else if(process.argv.includes('--target'))process.stdout.write(cert.target+'\n');
 else{const r=verifyCertificate(kernel,cert);if(process.argv.includes('--mutations'))r.negative_controls=mutationAudit(kernel,cert);console.log(JSON.stringify(r,null,2));}
}
