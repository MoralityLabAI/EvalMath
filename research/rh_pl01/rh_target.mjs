// RH-PL-03: compile the integer DMR harmonic criterion to the RH-PL-02 calculus.
import {kernel} from './kernel.mjs';
import {bounds} from './bounds.mjs';
function buildCompiler(k,bounds){
  const {E,M,N,I,Q,X,A,O,F,encode,decode,free,axiom,lower}=k;
  const assert=(x,m)=>{if(!x)throw Error(m)};
  const used=new Set();
  function bind(q,n,fn,vs=[]){
    if(n===0)return fn(...vs);
    let v=0;while(used.has(v))v++;
    used.add(v);
    try{return q(v,bind(q,n-1,fn,[...vs,v]))}finally{used.delete(v)}
  }
  const all=(n,f)=>bind(Q,n,f), ex=(n,f)=>bind(X,n,f);
  const and=(...fs)=>fs.reduceRight((a,b)=>a===null?b:A(b,a),null);
  const empty=x=>all(1,u=>N(M(u,x)));
  const succ=(x,y)=>all(1,u=>F(M(u,y),O(M(u,x),E(u,x))));
  const subset=(x,y)=>all(1,u=>I(M(u,x),M(u,y)));
  const inductive=x=>and(ex(1,z=>and(empty(z),M(z,x))),all(1,u=>I(M(u,x),ex(1,v=>and(M(v,x),succ(u,v))))));
  const omega=w=>and(inductive(w),all(1,x=>I(inductive(x),subset(w,x))));
  const singleton=(s,x)=>all(1,u=>F(M(u,s),E(u,x)));
  const doubleton=(s,x,y)=>all(1,u=>F(M(u,s),O(E(u,x),E(u,y))));
  const pair=(p,x,y)=>all(1,u=>F(M(u,p),O(singleton(u,x),doubleton(u,x,y))));
  const at=(f,i,v)=>ex(1,p=>and(pair(p,i,v),M(p,f)));
  const at2=(f,x,y,v)=>ex(2,(p,q)=>and(pair(p,x,y),pair(q,p,v),M(q,f)));
  function compile(){
    assert(used.size===0,'scope reset');
    return all(9,(w,z,o,plus,times,lcm,delta,num,den)=>{
      const nat=x=>M(x,w);
      const nall=(n,f)=>all(n,(...xs)=>I(and(...xs.map(nat)),f(...xs)));
      const nex=(n,f)=>ex(n,(...xs)=>and(...xs.map(nat),f(...xs)));
      const le=(x,y)=>O(E(x,y),M(x,y));
      const pos=x=>N(E(x,z));
      const S=t=>['s',t], Add=(a,b)=>['+',a,b], Mul=(a,b)=>['*',a,b], Get=(g,i)=>['g',g,i];
      const square=x=>Mul(x,x);
      function val(t,fn){
        if(typeof t==='number')return fn(t);
        if(t[0]==='s')return val(t[1],x=>nex(1,y=>and(succ(x,y),fn(y))));
        if(t[0]==='g')return val(t[2],x=>nex(1,y=>and(at(t[1],x,y),fn(y))));
        if(t[0]==='+'||t[0]==='*')return val(t[1],x=>val(t[2],y=>nex(1,v=>and(at2(t[0]==='+'?plus:times,x,y,v),fn(v)))));
        throw Error('term');
      }
      const equal=(a,b)=>val(a,x=>val(b,y=>E(x,y)));
      const less=(a,b)=>val(a,x=>val(b,y=>M(x,y)));
      const total1=g=>and(nall(1,x=>nex(1,y=>at(g,x,y))),nall(3,(x,y,v)=>I(and(at(g,x,y),at(g,x,v)),E(y,v))));
      const total2=g=>and(nall(2,(x,y)=>nex(1,v=>at2(g,x,y,v))),nall(4,(x,y,u,v)=>I(and(at2(g,x,y,u),at2(g,x,y,v)),E(u,v))));
      const divides=(x,y)=>nex(1,j=>equal(Mul(x,j),y));
      const common=(i,l)=>and(pos(l),nall(1,j=>I(and(pos(j),le(j,i)),divides(j,l))));
      const definitions=and(
        omega(w),nat(z),empty(z),nat(o),succ(z,o),
        total2(plus),total2(times),
        nall(1,x=>equal(Add(x,z),x)),
        nall(2,(x,y)=>equal(Add(x,S(y)),S(Add(x,y)))),
        nall(1,x=>equal(Mul(x,z),z)),
        nall(2,(x,y)=>equal(Mul(x,S(y)),Add(Mul(x,y),x))),
        total1(lcm),total1(delta),total1(num),total1(den),
        nall(1,i=>val(Get(lcm,i),l=>and(common(i,l),nall(1,h=>I(common(i,h),le(l,h)))))),
        equal(Get(delta,z),o),
        nall(1,i=>equal(Get(delta,S(i)),Mul(Get(delta,i),Get(lcm,i)))),
        equal(Get(num,z),z),equal(Get(den,z),o),
        nall(1,i=>equal(Get(num,S(i)),Add(Mul(S(i),Get(num,i)),Get(den,i)))),
        nall(1,i=>equal(Get(den,S(i)),Mul(S(i),Get(den,i))))
      );
      const claim=nall(1,n=>I(pos(n),
        val(Get(delta,n),d=>val(Get(num,d),a=>val(Get(den,d),b=>
          val(square(n),n2=>val(square(b),b2=>
            val(S(o),two=>val(square(two),four=>val(Mul(S(two),four),twelve=>
              less(Add(Mul(four,square(a)),Mul(square(n2),b2)),
                   Add(Mul(Mul(square(twelve),Mul(n2,n)),b2),Mul(Mul(Mul(four,a),n2),b)))
            )))
          ))
        )))
      ));
      return I(definitions,claim);
    });
  }
  function truth(f,env,domain){
    switch(f[0]){
      case'e':return env[f[1]]===env[f[2]];
      case'm':return !!(env[f[2]]&(1<<env[f[1]]));
      case'n':return !truth(f[1],env,domain);
      case'i':return !truth(f[1],env,domain)||truth(f[2],env,domain);
      case'a':return domain.every(x=>{const e=env.slice();e[f[1]]=x;return truth(f[2],e,domain)});
    }throw Error('formula');
  }
  function testPairs(){
    const domain=Array.from({length:16},(_,i)=>i);
    used.add(0);used.add(1);used.add(2);
    const p=pair(0,1,2);
    used.clear();
    let checks=0;
    for(let x=0;x<4;x++)for(let y=0;y<4;y++)for(let t=0;t<16;t++){
      const expected=(1<<(1<<x))|(1<<((1<<x)|(1<<y)));
      assert(truth(p,[t,x,y],domain)===(t===expected),'pair semantics');
      checks++;
    }
    return checks;
  }
  const gcd=(a,b)=>{while(b)[a,b]=[b,a%b];return a};
  function arithmetic(){
    const rows=[];
    let l=1n,d=1n;
    for(let n=1n;n<=6n;n++){
      const D=d;
      let a=0n,b=1n;
      for(let j=1n;j<=D;j++){a=j*a+b;b=j*b}
      let direct=0n;
      for(let j=1n;j<=D;j++){assert(b%j===0n,'factorial divisible');direct+=b/j}
      assert(a===direct,'independent harmonic sum');
      const lhs=4n*a*a+n**4n*b*b,rhs=144n*n**3n*b*b+4n*a*n*n*b;
      const alt=(2n*a-n*n*b)**2n;
      assert(rhs-lhs===144n*n**3n*b*b-alt,'denominator clearing');
      assert(lhs<rhs,'counterexample');
      rows.push({n:Number(n),delta:Number(D),factorial_digits:b.toString().length,inequality:lhs<rhs});
      l=l*n/gcd(l,n);d*=l;
    }
    return rows;
  }
  function run(){
    const f=compile(), s=encode(f);
    assert(free(f).size===0,'closed');
    assert(encode(decode(s))===s,'roundtrip');
    assert(s===encode(compile()),'determinism');
    assert(!axiom(f),'nonaxiom target');
    const nodes={e:0,m:0,n:0,i:0,a:0};let maxVar=0,depth=0,weight=0;
    function walk(f,d){nodes[f[0]]++;depth=Math.max(depth,d);
      if(f[0]==='e'||f[0]==='m'){maxVar=Math.max(maxVar,f[1],f[2]);weight+=f[1]+f[2]}
      if(f[0]==='n')walk(f[1],d+1);
      if(f[0]==='i'){walk(f[1],d+1);walk(f[2],d+1)}
      if(f[0]==='a'){maxVar=Math.max(maxVar,f[1]);weight+=f[1];walk(f[2],d+1)}
    }walk(f,1);
    assert(bounds.minShape(f)+weight===s.length,'independent length accounting');
    return {formula_bytes:s.length,line_bytes:s.length+1,min_shape_bytes:bounds.minShape(f),variable_index_bytes:weight,max_var:maxVar,ast_depth:depth,nodes,baseline:lower(f),strengthened:bounds.strengthened(f),pair_checks:testPairs(),integer_controls:arithmetic()};
  }
  return {compile,run};
}
export const compiler=buildCompiler(kernel,bounds);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/rh_target.mjs')){
  if(process.argv.includes('--formula'))process.stdout.write(kernel.encode(compiler.compile())+'\n');
  else console.log(JSON.stringify(compiler.run(),null,2));
}
