// RH-PL-02: pure first-order Hilbert proof checker, dependency-free ES module.
// Run: node research/rh_pl01/kernel.mjs
function buildKernel(){
  const E=(x,y)=>['e',x,y], M=(x,y)=>['m',x,y], N=a=>['n',a], I=(a,b)=>['i',a,b], Q=(x,a)=>['a',x,a];
  const X=(x,a)=>N(Q(x,N(a))), A=(a,b)=>N(I(a,N(b))), O=(a,b)=>I(N(a),b), F=(a,b)=>A(I(a,b),I(b,a));
  const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
  const v=x=>{if(!Number.isSafeInteger(x)||x<0)throw Error('invalid variable');return 'v'+'1'.repeat(x)+'0'};
  function encode(f){switch(f[0]){case'e':case'm':return f[0]+v(f[1])+v(f[2]);case'n':return'n'+encode(f[1]);case'i':return'i'+encode(f[1])+encode(f[2]);case'a':return'a'+v(f[1])+encode(f[2]);default:throw Error('invalid formula')}}
  function decode(s){let p=0;function variable(){if(s[p++]!=='v')throw Error('variable');let x=0;while(s[p]==='1'){p++;x++}if(s[p++]!=='0')throw Error('terminator');return x}function formula(){switch(s[p++]){case'e':return E(variable(),variable());case'm':return M(variable(),variable());case'n':return N(formula());case'i':return I(formula(),formula());case'a':return Q(variable(),formula());default:throw Error('formula')}}const f=formula();if(p!==s.length)throw Error('trailing bytes');return f}
  function free(f){switch(f[0]){case'e':case'm':return new Set(f.slice(1));case'n':return free(f[1]);case'i':return new Set([...free(f[1]),...free(f[2])]);case'a':{const s=free(f[2]);s.delete(f[1]);return s}}throw Error('formula')}
  function subst(f,x,t){if(x===t)return f;switch(f[0]){case'e':case'm':return [f[0],...f.slice(1).map(z=>z===x?t:z)];case'n':return N(subst(f[1],x,t));case'i':return I(subst(f[1],x,t),subst(f[2],x,t));case'a':if(f[1]===x)return f;if(f[1]===t&&free(f[2]).has(x))throw Error('capture');return Q(f[1],subst(f[2],x,t))}throw Error('formula')}
  const wild=x=>['$',x];
  function match(p,f,env={}){if(Array.isArray(p)&&p[0]==='$'){if(Object.hasOwn(env,p[1]))return eq(env[p[1]],f)?env:null;env[p[1]]=f;return env}if(Array.isArray(p)){if(!Array.isArray(f)||p.length!==f.length)return null;for(let j=0;j<p.length;j++)if(!match(p[j],f[j],env))return null;return env}return p===f?env:null}
  const p=wild('p'),q=wild('q'),r=wild('r');
  const prop=[['K',I(p,I(q,p))],['S',I(I(p,I(q,r)),I(I(p,q),I(p,r)))],['classical',I(I(N(q),N(p)),I(p,q))]];
  const fixed=new Map();
  function ax(name,f){fixed.set(encode(f),name)}
  ax('extensionality',Q(0,Q(1,I(Q(2,F(M(2,0),M(2,1))),E(0,1)))));
  ax('empty',X(0,Q(1,N(M(1,0)))));
  ax('pairing',Q(0,Q(1,X(2,Q(3,F(M(3,2),O(E(3,0),E(3,1))))))));
  ax('union',Q(0,X(1,Q(2,F(M(2,1),X(3,A(M(3,0),M(2,3))))))));
  ax('power',Q(0,X(1,Q(2,F(M(2,1),Q(3,I(M(3,2),M(3,0))))))));
  ax('infinity',X(0,A(X(1,A(Q(2,N(M(2,1))),M(1,0))),Q(1,I(M(1,0),X(2,A(M(2,0),Q(3,F(M(3,2),O(M(3,1),E(3,1)))))))))));
  ax('foundation',Q(0,I(X(1,M(1,0)),X(1,A(M(1,0),N(X(2,A(M(2,1),M(2,0)))))))));
  const nonempty=Q(1,I(M(1,0),X(2,M(2,1))));
  const disjoint=Q(1,Q(2,I(A(A(M(1,0),M(2,0)),N(E(1,2))),N(X(3,A(M(3,1),M(3,2)))))));
  const selector=X(1,Q(2,I(M(2,0),X(3,A(A(M(3,2),M(3,1)),Q(4,I(A(M(4,2),M(4,1)),E(4,3))))))));
  ax('choice',Q(0,I(A(nonempty,disjoint),selector)));
  const separation=phi=>X(2,Q(0,F(M(0,2),A(M(0,1),phi))));
  const replacement=(phi,psi)=>I(Q(0,I(M(0,2),X(1,A(phi,Q(4,I(psi,E(4,1))))))),X(3,Q(1,F(M(1,3),X(0,A(M(0,2),phi))))));
  function axiom(f){
    const name=fixed.get(encode(f));if(name)return name;
    for(const [name,pat] of prop)if(match(pat,f))return name;
    if(f[0]==='e'&&f[1]===f[2])return 'equality-reflexivity';
    if(f[0]==='i'){
      const [l,h]=f.slice(1);
      if(l[0]==='a'){
        const [x,b]=l.slice(1);
        for(const t of new Set([x,...free(h)])){try{if(eq(subst(b,x,t),h))return 'forall-elimination'}catch{}}
        if(b[0]==='i'&&!free(b[1]).has(x)&&eq(h,I(b[1],Q(x,b[2]))))return 'forall-distribution';
      }
      if(l[0]==='e'&&h[0]==='i'&&['e','m'].includes(h[1][0])){
        const [x,y]=l.slice(1),g=h[1];
        for(const j of [1,2])if(g[j]===x){const t=g.slice();t[j]=y;if(eq(t,h[2]))return 'equality-substitution'}
      }
    }
    const s=match(separation(p),f);if(s&&!free(s.p).has(2))return 'separation';
    const t=match(replacement(p,q),f);
    if(t&&!free(t.p).has(3)&&!free(t.p).has(4)){try{if(eq(subst(t.p,1,4),t.q))return 'replacement'}catch{}}
    return null;
  }
  function verify(proof,target){
    try{
      if(typeof proof!=='string'||!proof.endsWith('\n')||typeof target!=='string'||free(decode(target)).size)return false;
      const lines=proof.slice(0,-1).split('\n'),seen=new Set(),incoming=new Map();
      if(lines.at(-1)!==target)return false;
      for(const line of lines){
        const f=decode(line);
        if(!axiom(f)&&!(f[0]==='a'&&seen.has(encode(f[2])))&&!(incoming.get(line)||[]).some(a=>seen.has(a)))return false;
        seen.add(line);
        if(f[0]==='i'){const k=encode(f[2]),arr=incoming.get(k)||[];arr.push(encode(f[1]));incoming.set(k,arr)}
      }return true;
    }catch{return false}
  }
  function lower(f){
    // For a nonaxiom, MP requires two distinct predecessor lines, including
    // an antecedent of at least five bytes. Generalization peels the binder.
    const l=encode(f).length, cost=l+1;
    if(axiom(f))return cost;
    return Math.min(2*l+14,f[0]==='a'?cost+lower(f[2]):Infinity);
  }
  function run(){
    const assert=(ok,m)=>{if(!ok)throw Error(m)};
    const P=M(0,0), R=E(0,0), id=I(P,P), eqsub=I(R,id);
    const proof=fs=>fs.map(encode).join('\n')+'\n';
    const rows=[];
    const fixtures=[['reflexivity',Q(0,R),[R,Q(0,R)]],['nested-reflexivity',Q(1,Q(0,R)),[R,Q(0,R),Q(1,Q(0,R))]],['membership-identity',Q(0,id),[R,eqsub,id,Q(0,id)]]];
    // verifier only accepts closed final formulas. Also check the exact
    // open identity bound separately: the same three lines are a derivation.
    assert(axiom(R)==='equality-reflexivity'&&axiom(eqsub)==='equality-substitution','identity premises');
    assert(lower(id)===36&&proof([R,eqsub,id]).length===36,'open identity exact');
    for(const [name,target,steps] of fixtures){const bytes=proof(steps);assert(verify(bytes,encode(target)),name);assert(lower(target)<=bytes.length,'bound');rows.push({name,lower:lower(target),upper:bytes.length})}
    assert(rows[0].lower===15&&rows[0].upper===15&&rows[1].lower===28&&rows[1].upper===28,'exact controls');
    const sep=separation(M(0,1)), rep=replacement(E(0,1),E(0,4));
    const capture=I(Q(0,X(1,M(0,1))),X(1,M(1,1)));
    const badDist=I(Q(0,I(P,P)),I(P,Q(0,P)));
    const bads=[['capture',capture],['free-output-separation',separation(M(0,2))],['mismatched-replacement',replacement(E(0,1),M(0,4))],['free-output-replacement',replacement(E(0,3),E(0,3))],['free-generalization-distribution',badDist]];
    for(const [name,f] of bads)assert(!axiom(f),name);
    assert(axiom(sep)==='separation'&&axiom(rep)==='replacement','schemas');
    assert(axiom(separation(Q(2,M(0,2))))==='separation','bound output name is safe');
    assert(axiom(replacement(Q(4,E(1,4)),Q(4,E(4,4))))===null,'replacement capture');
    for(const s of ['', 'ev00v0', 'ev0v0x','av0','av0ev0v0\n','ev2v0','mv0v']){let rejected=false;try{decode(s)}catch{rejected=true}assert(rejected,'malformed '+s)}
    assert(!verify(encode(Q(0,R))+'\n',encode(Q(0,R))),'missing premise');
    assert(!verify(proof([Q(0,R),R]),encode(R)),'open target');
    assert(!verify(proof([R,id,Q(0,id)]),encode(Q(0,id))),'missing MP');
    assert(!verify(proof([R,Q(0,R)]).slice(0,-1),encode(Q(0,R))),'missing LF');
    assert(!verify(proof([R,Q(0,R)])+'\n',encode(Q(0,R))),'blank line');
    function truth(f,a,mask){switch(f[0]){case'e':return a[f[1]]===a[f[2]];case'm':return !!(mask&(1<<(2*a[f[1]]+a[f[2]])));case'n':return !truth(f[1],a,mask);case'i':return !truth(f[1],a,mask)||truth(f[2],a,mask);case'a':return [0,1].every(x=>{const b=a.slice();b[f[1]]=x;return truth(f[2],b,mask)})}}
    const pool=[P,R,M(0,1),E(1,2),N(M(2,1)),Q(1,M(0,1)),X(0,E(0,2)),I(M(1,2),M(0,0))];
    const logic=new Map();
    const add=f=>logic.set(encode(f),f);
    for(const a of pool)for(const b of pool){add(I(a,I(b,a)));add(I(I(N(b),N(a)),I(a,b)));for(const c of pool)add(I(I(a,I(b,c)),I(I(a,b),I(a,c))));for(let x=0;x<3;x++)if(!free(a).has(x))add(I(Q(x,I(a,b)),I(a,Q(x,b))))}
    for(const a of pool)for(let x=0;x<3;x++)for(let y=0;y<3;y++){try{add(I(Q(x,a),subst(a,x,y)))}catch{}}
    for(let x=0;x<3;x++){add(E(x,x));for(let y=0;y<3;y++)for(let z=0;z<3;z++)for(const pred of [E,M]){add(I(E(x,y),I(pred(x,z),pred(y,z))));add(I(E(x,y),I(pred(z,x),pred(z,y))))}}
    let checks=0, badCaptureWitnesses=0,badDistWitnesses=0;
    for(const f of logic.values()){assert(eq(decode(encode(f)),f),'roundtrip');assert(axiom(f),'recognition');for(let mask=0;mask<16;mask++)for(let bits=0;bits<8;bits++){assert(truth(f,[bits&1,(bits>>1)&1,(bits>>2)&1],mask),'semantic counterexample');checks++}}
    for(let mask=0;mask<16;mask++)for(let bits=0;bits<8;bits++){const a=[bits&1,(bits>>1)&1,(bits>>2)&1];if(!truth(capture,a,mask))badCaptureWitnesses++;if(!truth(badDist,a,mask))badDistWitnesses++}
    assert(badCaptureWitnesses>0&&badDistWitnesses>0,'negative witnesses');
    for(const [s,name] of fixed){assert(eq(decode(s),decode(encode(decode(s)))),'fixed roundtrip');assert(axiom(decode(s))===name,'fixed recognition');assert(free(decode(s)).size===0,'fixed closed');assert(verify(s+'\n',s),'fixed proof')}
    return {fixed_axioms:fixed.size,logic_instances:logic.size,semantic_checks:checks,capture_countermodels:badCaptureWitnesses,distribution_countermodels:badDistWitnesses,schema_negatives:bads.length+1,parse_negatives:7,proof_negatives:5,controls:rows,open_identity_exact:36};
  }
  return {E,M,N,I,Q,X,A,O,F,encode,decode,free,subst,axiom,verify,lower,run};
}
export const kernel=buildKernel();
if (typeof process!=='undefined' && process.argv[1]?.endsWith('/kernel.mjs')) console.log(JSON.stringify(kernel.run(),null,2));
