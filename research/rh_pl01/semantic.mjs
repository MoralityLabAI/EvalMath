// RH-PL-05: explicit infinite countermodel and proof-wide axiom-use bound.
import {kernel} from './kernel.mjs';
import {spine} from './spine.mjs';
function buildSemantic(k,sp){
  const R='r', graphNames=['plus','times','lcm','delta','num','den'];
  const z=0n,o=1n;
  const nat=x=>x===R||typeof x==='bigint'&&x>=0n;
  const succ=x=>x===R?R:x+1n;
  const lt=(x,y)=>y===R||x!==R&&x<y;
  const le=(x,y)=>x===y||lt(x,y);
  const add=(x,y)=>x===R||y===R?R:x+y;
  const mul=(x,y)=>x===0n||y===0n?0n:x===R||y===R?R:x*y;
  function gcd(a,b){while(b)[a,b]=[b,a%b];return a}
  function lcm(x){if(x===R)return R;let a=1n;for(let j=1n;j<=x;j++)a=a*j/gcd(a,j);return a}
  function delta(x){if(x===R)return R;let a=1n;for(let j=0n;j<x;j++)a*=lcm(j);return a}
  function numden(x){if(x===R)return [0n,0n];let a=0n,b=1n;for(let j=1n;j<=x;j++){a=j*a+b;b=j*b}return [a,b]}
  const num=x=>numden(x)[0], den=x=>numden(x)[1];
  function divides(x,y){
    if(x===0n)return y===0n;
    if(x===R)return y===0n||y===R;
    return y===R||y%x===0n;
  }
  const key=x=>x===R?R:typeof x==='bigint'?'n:'+x:x;
  const isNKey=s=>/^n:(0|[1-9][0-9]*)$/.test(s);
  const nValue=s=>s===R?R:BigInt(s.slice(2));
  const gKey=name=>'g:'+name;
  const isNatKey=s=>s===R||isNKey(s);
  // A countable domain: N, r, six named infinite graphs, and finite
  // sets over those objects. Finite ordinals share their canonical keys.
  function set(xs){
    const ys=[...new Set(xs)].sort();
    if(ys.every(isNKey)&&ys.every(y=>nValue(y)<BigInt(ys.length)))return key(BigInt(ys.length));
    return 's:'+JSON.stringify(ys);
  }
  function ext(s){
    if(isNKey(s)){const n=nValue(s);if(n>10000n)throw Error('sample finite extension too large');return Array.from({length:Number(n)},(_,i)=>key(BigInt(i)))}
    if(s.startsWith('s:'))return JSON.parse(s.slice(2));
    return null;
  }
  const pair=(x,y)=>set([set([x]),set([x,y])]);
  function unpair(p){
    // Finite ordinals cannot be Kuratowski pairs: pair is nonempty
    // and lacks zero. This also avoids materializing huge ordinals.
    if(!p.startsWith('s:'))return null;
    const e=ext(p);if(e.length<1||e.length>2)return null;
    for(const c of e){
      // A component equal to n:k is a singleton only at k=1.
      if(isNKey(c)&&nValue(c)!==1n)continue;
      const a=ext(c);if(!a||a.length!==1)continue;
      const x=a[0],other=e.length===1?c:e.find(t=>t!==c);
      if(isNKey(other)&&nValue(other)>2n)continue;
      const b=ext(other);if(!b||b.length<1||b.length>2||!b.includes(x))continue;
      const y=b.find(t=>t!==x)||x;
      if(pair(x,y)===p)return [x,y];
    }return null;
  }
  function member(x,y){
    if(y===R)return isNatKey(x);
    if(isNKey(y))return isNKey(x)&&nValue(x)<nValue(y);
    if(y.startsWith('s:'))return ext(y).includes(x);
    if(y.startsWith('g:')){
      const p=unpair(x);if(!p)return false;
      const [input,out]=p;if(!isNatKey(out))return false;
      const value=nValue(out),name=y.slice(2);
      if(name==='plus'||name==='times'){
        const args=unpair(input);if(!args||!args.every(isNatKey))return false;
        const [a,b]=args.map(nValue);
        return value===(name==='plus'?add(a,b):mul(a,b));
      }
      if(!isNatKey(input))return false;
      const f={lcm,delta,num,den}[name];return !!f&&value===f(nValue(input));
    }
    throw Error('unknown domain element');
  }
  function claim(n){
    const d=delta(n),a=num(d),b=den(d),n2=mul(n,n),b2=mul(b,b);
    const four=4n,twelve=12n;
    const lhs=add(mul(four,mul(a,a)),mul(mul(n2,n2),b2));
    const rhs=add(mul(mul(mul(twelve,twelve),mul(n2,n)),b2),mul(mul(mul(four,a),n2),b));
    return {n,d,a,b,lhs,rhs,holds:lt(lhs,rhs)};
  }
  function finiteCensus(max=4){
    let structures=0, candidates=0, inductiveSets=0;
    const bySize=[];
    for(let d=1;d<=max;d++){
      const count=2**(d*d), mask=(1<<d)-1;
      let yes=0;
      for(let code=0;code<count;code++){
        const e=Array.from({length:d},(_,i)=>(code>>(d*i))&mask);
        let zeros=0;
        for(let i=0;i<d;i++)if(e[i]===0)zeros|=1<<i;
        for(const w of e){
          candidates++;if(!(w&zeros))continue;
          let ok=true;
          for(let x=0;x<d;x++)if(w&(1<<x)){
            const req=e[x]|(1<<x);
            if(!e.some((y,j)=>y===req&&(w&(1<<j)))){ok=false;break}
          }
          if(ok)yes++;
        }
        structures++;
      }
      inductiveSets+=yes;bySize.push({domain:d,structures:count,inductive_candidates:count*d,inductive_sets:yes});
    }
    return {structures,candidates,inductiveSets,bySize};
  }
  function semanticFloor(f,enc,deltaCost){
    if(k.free(f).size||f[0]!=='a'||enc.encode(f).length<=1024)throw Error('requires large closed universal');
    const old=sp.cases(f,enc),d=1+2*enc.vmin;
    if(deltaCost<=d+1)throw Error('requires useful semantic floor');
    // k=1: all four counted lines are non-set-axioms. For k>=2,
    // only counted A1 can be a false nonlogical axiom. If so, its
    // line costs at least deltaCost rather than d+1.
    const cases={axiom_at_1:old.axiom_at_1+deltaCost,
      axiom_at_2:old.axiom_at_2+deltaCost-(d+1),
      axiom_at_3:old.axiom_at_3+deltaCost-(d+1),
      at_least_4:old.at_least_4+deltaCost-(d+1),
      generalization:old.generalization};
    return {previous:sp.bound(f,enc),semantic_lower:Math.min(...Object.values(cases)),cases};
  }
  function run(raw){
    const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
    const sample=[0n,1n,2n,3n,4n,5n,R];
    let arithmetic=0,pairChecks=0,graphChecks=0,leastChecks=0;
    for(const x of sample){
      assert(add(x,z)===x&&mul(x,z)===z,'zero');arithmetic+=2;
      for(const y of sample){
        assert(add(x,succ(y))===succ(add(x,y)),'addition recurrence');
        assert(mul(x,succ(y))===add(mul(x,y),x),'multiplication recurrence');arithmetic+=2;
      }
      const l=lcm(x);
      assert(l!==0n,'positive lcm');arithmetic++;
      const common=h=>h!==0n&&sample.every(j=>j===0n||!le(j,x)||divides(j,h));
      for(const j of sample)if(j!==0n&&le(j,x)){assert(divides(j,l),'lcm common');leastChecks++}
      for(const h of [...sample,l,6n,12n,60n,120n])if(common(h)){
        assert(le(l,h),'lcm least on sampled candidates');leastChecks++;
      }
      // For finite x the sample contains every positive j<=x.
      // For r a positive common multiple must be divisible by r.
      assert(delta(succ(x))===mul(delta(x),lcm(x)),'D recurrence');
      assert(num(succ(x))===add(mul(succ(x),num(x)),den(x)),'A recurrence');
      assert(den(succ(x))===mul(succ(x),den(x)),'B recurrence');arithmetic+=3;
    }
    assert(delta(z)===o&&num(z)===z&&den(z)===o,'initial sequences');
    arithmetic+=3;
    const nodes=[...sample.map(key),...graphNames.map(gKey),set([key(1n)]),set([R])];
    const seen=new Map();
    for(const a of nodes)for(const b of nodes){
      const p=pair(a,b),decoded=unpair(p);
      assert(decoded&&decoded[0]===a&&decoded[1]===b,'pair recovery');
      assert(!member(key(z),p),'pair lacks zero');
      assert(!seen.has(p)||seen.get(p)===JSON.stringify([a,b]),'pair injective');
      seen.set(p,JSON.stringify([a,b]));pairChecks++;
    }
    for(const a of sample)for(const b of sample){
      for(const [name,op] of [['plus',add],['times',mul]]){
        const p=pair(pair(key(a),key(b)),key(op(a,b)));
        assert(member(p,gKey(name)),'binary graph positive');graphChecks++;
        const bad=op(a,b)===R?key(z):key(R);
        assert(!member(pair(pair(key(a),key(b)),bad),gKey(name)),'binary graph negative');graphChecks++;
      }
    }
    for(const a of sample)for(const [name,op] of [['lcm',lcm],['delta',delta],['num',num],['den',den]]){
      const v=op(a);
      assert(member(pair(key(a),key(v)),gKey(name)),'unary graph positive');graphChecks++;
      assert(!member(pair(key(a),v===R?key(z):R),gKey(name)),'unary graph negative');graphChecks++;
    }
    for(const name of graphNames){assert(!member(key(z),gKey(name)),'graph lacks zero')}
    const graphSamples=Object.fromEntries(graphNames.map(name=>[name,
      name==='plus'||name==='times'
        ?sample.flatMap(a=>sample.map(b=>pair(pair(key(a),key(b)),key((name==='plus'?add:mul)(a,b)))))
        :sample.map(a=>pair(key(a),key({lcm,delta,num,den}[name](a))))]));
    let graphSeparation=0;
    for(let i=0;i<graphNames.length;i++)for(let j=i+1;j<graphNames.length;j++){
      const a=graphNames[i],b=graphNames[j],witness=[...graphSamples[a],...graphSamples[b]].find(p=>member(p,gKey(a))!==member(p,gKey(b)));
      assert(witness!==undefined,'graph distinction');graphSeparation++;
    }
    assert(member(R,R)&&member(R,set([R])),'foundation witness');
    assert(!member(key(z),set([R])),'singleton r');
    const falseAtR=claim(R);assert(falseAtR.lhs===0n&&falseAtR.rhs===0n&&!falseAtR.holds,'DMR fails');
    const finite=finiteCensus();assert(finite.inductiveSets===0,'finite induction');
    const target=k.decode(raw.slice(0,-1));assert(k.encode(target)+'\n'===raw,'target');
    // Pinned grammar: fixed-axiom minimum among possibly false ones is
    // foundation. Schema minima are witnessed by shortest atom e(v0,v0);
    // replacement includes two such placeholders. Documented separately.
    const rows=Object.entries(sp.encodings).map(([name,enc])=>{
      const costs=name==='unary'?{foundation:58,separation:58,replacement:125,union:94,power:86,choice:199}:{foundation:35,separation:36,replacement:70,union:46,power:38,choice:96};
      const d=Math.min(...Object.values(costs));
      return {encoding:name,formula_bytes:enc.encode(target).length,minimum_false_axiom_line:d,possibly_false_family_cost_floors:costs,...semanticFloor(target,enc,d)};
    });
    return {finite,arithmetic_controls:arithmetic,lcm_controls:leastChecks,pair_controls:pairChecks,graph_membership_controls:graphChecks,graph_distinction_witnesses:graphSeparation,false_at_r:{n:R,d:R,a:0,b:0,lhs:0,rhs:0,holds:false},bounds:rows};
  }
  return {R,succ,lt,le,add,mul,lcm,delta,numden,divides,key,set,pair,unpair,member,claim,finiteCensus,semanticFloor,run};
}
export const semantic=buildSemantic(kernel,spine);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/semantic.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(semantic.run(raw),null,2));
}
