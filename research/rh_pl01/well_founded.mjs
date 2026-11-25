// RH-PL-05: well-founded countermodel arithmetic and semantic bound.
import {kernel} from './kernel.mjs';
import {spine} from './spine.mjs';
import {semantic} from './semantic.mjs';
function buildWellFounded(k,sp,sem){
  const isR=x=>typeof x==='string'&&/^r:[1-9][0-9]*$/.test(x);
  const weight=x=>isR(x)?BigInt(x.slice(2)):x;
  const r=w=>{if(w<=0n)throw Error('invalid tagged weight');return 'r:'+w};
  const succ=x=>isR(x)?r(weight(x)+1n):x+1n;
  const add=(x,y)=>isR(x)||isR(y)?r(weight(x)+weight(y)):x+y;
  function mul(x,y){
    if(x===0n||y===0n)return 0n;
    if(isR(x))return r(weight(x)*weight(y));
    if(isR(y))return x===1n?y:x*(weight(y)-1n);
    return x*y;
  }
  function lt(x,y){
    if(isR(y))return isR(x)?weight(x)<weight(y):x===1n;
    return !isR(x)&&x<y;
  }
  const le=(x,y)=>x===y||lt(x,y);
  const lcm=x=>isR(x)?r(sem.lcm(weight(x))):sem.lcm(x);
  const delta=x=>isR(x)?r(sem.delta(weight(x))):sem.delta(x);
  const num=x=>isR(x)?0n:sem.numden(x)[0];
  const den=x=>isR(x)?0n:sem.numden(x)[1];
  function divides(x,y){
    if(y===0n)return true;
    if(x===0n)return false;
    if(isR(x))return isR(y)&&weight(y)%weight(x)===0n;
    if(isR(y))return x===1n;
    return y%x===0n;
  }
  // Real hereditarily finite representatives. The base tagged ordinal
  // r:1 = {1}, and successor adjoins the preceding element itself.
  const hfCache=[null,sem.set([sem.key(1n)])];
  function hf(x){
    if(!isR(x))return sem.key(x);
    const n=weight(x);
    if(n>1000n)throw Error('sample HF chain too large');
    for(let j=hfCache.length;j<=Number(n);j++)hfCache.push(sem.set([sem.key(1n),...hfCache.slice(1)]));
    return hfCache[Number(n)];
  }
  function claim(n){
    const d=delta(n),a=num(d),b=den(d),n2=mul(n,n),b2=mul(b,b);
    const lhs=add(mul(4n,mul(a,a)),mul(mul(n2,n2),b2));
    const rhs=add(mul(mul(mul(12n,12n),mul(n2,n)),b2),mul(mul(mul(4n,a),n2),b));
    return {n,d,a,b,lhs,rhs,holds:lt(lhs,rhs)};
  }
  function run(raw){
    const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
    const small=[0n,1n,2n,3n,4n,5n,6n,r(1n),r(2n),r(3n),r(4n),r(5n),r(6n)];
    const seq=[0n,1n,2n,3n,4n,5n,r(1n),r(2n),r(3n),r(4n),r(5n)];
    const candidates=[...small,12n,60n,120n,r(12n),r(60n),r(120n)];
    let arithmetic=0,hfChecks=0,least=0,dividesWitnesses=0;
    const seen=new Set();
    for(const x of small){
      assert(!seen.has(hf(x)),'HF representatives distinct');seen.add(hf(x));
      assert(add(x,0n)===x&&mul(x,0n)===0n,'zero equations');arithmetic+=2;
      for(const y of small){
        assert(add(x,succ(y))===succ(add(x,y)),'addition recurrence');
        assert(mul(x,succ(y))===add(mul(x,y),x),'multiplication recurrence');arithmetic+=2;
        assert(sem.member(hf(x),hf(y))===lt(x,y),'actual finite-set membership');hfChecks++;
        assert(!sem.member(hf(x),hf(x)),'irreflexive HF membership');hfChecks++;
      }
      assert(!sem.member(sem.key(0n),hf(x))||!isR(x),'tagged element lacks zero');hfChecks++;
      const l=lcm(x);
      const common=h=>h!==0n&&small.every(j=>j===0n||!le(j,x)||divides(j,h));
      assert(common(l),'lcm common');least++;
      for(const h of [...candidates,l])if(common(h)){assert(le(l,h),'lcm least');least++}
    }
    for(const x of seq){
      assert(delta(succ(x))===mul(delta(x),lcm(x)),'D recurrence');
      assert(num(succ(x))===add(mul(succ(x),num(x)),den(x)),'A recurrence');
      assert(den(succ(x))===mul(succ(x),den(x)),'B recurrence');arithmetic+=3;
    }
    // Independent witness search for a complete small divisibility panel.
    // To reach y <= 6, or tagged y with weight <= 6, a multiplier of
    // weight <= 7 suffices in every positive case in this panel.
    const multipliers=[...small,7n,r(7n)];
    for(const x of small)for(const y of small){
      assert(divides(x,y)===multipliers.some(z=>mul(x,z)===y),'divisibility oracle');
      dividesWitnesses++;
    }
    assert(delta(0n)===1n&&num(0n)===0n&&den(0n)===1n,'base sequences');arithmetic+=3;
    const bad=claim(r(1n));assert(bad.lhs===0n&&bad.rhs===0n&&!bad.holds,'target fails in well-founded model');
    const f=k.decode(raw.slice(0,-1));
    assert(k.encode(f)+'\n'===raw,'frozen target');
    const bounds=Object.entries(sp.encodings).map(([encoding,enc])=>{
      const floors=encoding==='unary'?{separation:58,replacement:125,union:94,power:86,choice:199}:{separation:36,replacement:70,union:46,power:38,choice:96};
      const min=Math.min(...Object.values(floors));
      return {encoding,foundation_preserved:true,possibly_false_family_floors:floors,minimum_false_axiom_line:min,...sem.semanticFloor(f,enc,min)};
    });
    return {arithmetic_controls:arithmetic,hf_membership_controls:hfChecks,lcm_controls:least,divisibility_controls:dividesWitnesses,counterexample:{n:'r:1',d:'r:1',a:0,b:0,lhs:0,rhs:0,holds:false},bounds};
  }
  return {r,weight,hf,succ,add,mul,lt,le,lcm,delta,num,den,divides,claim,run};
}
export const wellFounded=buildWellFounded(kernel,spine,semantic);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/well_founded.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(wellFounded.run(raw),null,2));
}
