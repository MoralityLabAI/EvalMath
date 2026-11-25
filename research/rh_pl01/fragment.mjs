// RH-PL-06: short-schema census and rank-two graph detector controls.
import {kernel} from './kernel.mjs';
import {bounds} from './bounds.mjs';
import {spine} from './spine.mjs';
import {semantic} from './semantic.mjs';
function buildFragment(k,b,sp,sem){
  const {E,M,N,I,Q,X,A,F,encode,decode,free,axiom}=k;
  const separation=phi=>X(2,Q(0,F(M(0,2),A(M(0,1),phi))));
  function stats(f){
    switch(f[0]){
      case'e':case'm':return {atoms:1,rank:0,quantifiers:0};
      case'n':return stats(f[1]);
      case'i':{const a=stats(f[1]),b=stats(f[2]);return {atoms:a.atoms+b.atoms,rank:Math.max(a.rank,b.rank),quantifiers:a.quantifiers+b.quantifiers}}
      case'a':{const t=stats(f[2]);return {atoms:t.atoms,rank:t.rank+1,quantifiers:t.quantifiers+1}}
    }throw Error('formula');
  }
  // This class is justified by the nonstandard model's rank-one trace theorem,
  // Boolean closure and vacuous-variable elimination. Constants here mean
  // independence of the source-element variable, not computational truth.
  function classify(f,x=0){
    if(!free(f).has(x))return 'parameter-only';
    const t=stats(f);
    if(t.rank<=1)return 'rank-one';
    if(t.atoms===1)return 'single-atom';
    if(f[0]==='n')return classify(f[1],x)===null?null:'boolean';
    if(f[0]==='i')return classify(f[1],x)===null||classify(f[2],x)===null?null:'boolean';
    if(f[0]==='a'&&!free(f[2]).has(f[1]))return classify(f[2],x)===null?null:'vacuous';
    return null;
  }
  function run(raw){
    const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
    const all=b.formulae(18),byBytes={},classes={},rankCounts={};
    let admissible=0,recognized=0,highRank=0,maxRank=0;
    for(const phi of all){
      if(free(phi).has(2))continue;
      const len=encode(phi).length,s=separation(phi),t=stats(phi),cls=classify(phi);
      assert(cls!==null,'short predicate outside trace proof: '+encode(phi));
      assert(axiom(s)==='separation','schema');
      assert(encode(s).length+1===48+2*len,'unary size');
      assert(sp.compact(s).length+1===30+2*sp.compact(phi).length,'compact size');
      assert(encode(s).length+1<86,'unary threshold');
      admissible++;recognized++;if(t.rank>1)highRank++;
      maxRank=Math.max(maxRank,t.rank);
      byBytes[len]=(byBytes[len]||0)+1;
      classes[cls]=(classes[cls]||0)+1;
      rankCounts[t.rank]=(rankCounts[t.rank]||0)+1;
    }
    // A rank-two separation predicate detecting the externally modified
    // denominator graph: parameter v3 is the graph, v4 is zero.
    // v5 = pair, v6 = component; v0 = element; v2 forbidden free.
    const detect=X(5,A(M(5,3),X(6,A(M(6,5),A(M(0,6),M(4,6))))));
    assert(stats(detect).rank===2&&axiom(separation(detect))==='separation','rank-two witness');
    // Independent finite-set surrogate: emulate a marked cut on a finite
    // panel, with denominator zero above the boundary. This tests only
    // the pair detector, not nonstandard induction or the model theorem.
    let detectorChecks=0;
    const panels=[];
    for(const cut of [3,5,8,12]){
      const Nmax=cut+6;
      const ns=Array.from({length:Nmax+1},(_,i)=>sem.key(BigInt(i)));
      const zero=ns[0];
      const graph=ns.map((x,i)=>sem.pair(x,i>=cut?zero:sem.key(sem.numden(BigInt(i))[1])));
      // The pair membership representation gives its two components
      // directly; if a component is a finite ordinal, its extension
      // is queried through membership, avoiding factorial enumeration.
      const results=[];
      for(let i=0;i<=Nmax;i++){
        const x=ns[i];
        const observed=graph.some(p=>{
          const args=sem.unpair(p);
          assert(args!==null,'graph pair');
          const [a,v]=args;
          return [sem.set([a]),sem.set([a,v])].some(u=>sem.member(u,p)&&sem.member(x,u)&&sem.member(zero,u));
        });
        const expected=i===0||i===1||i>=cut;
        assert(observed===expected,'rank-two detector');
        results.push(i+':'+Number(observed));detectorChecks++;
      }
      panels.push({cut,nmax:Nmax,selected:results.filter(x=>x.endsWith(':1')).map(x=>Number(x.split(':')[0]))});
    }
    const f=decode(raw.slice(0,-1));assert(encode(f)+'\n'===raw,'target');
    // Power set fails in the model by the infinite-extension invariant:
    // its output for Omega must contain Omega and every core singleton.
    // No represented infinite extension contains the Omega object.
    // Fixed axiom recognition and costs checked below.
    const power=Q(0,X(1,Q(2,F(M(2,1),Q(3,I(M(3,2),M(3,0)))))));
    assert(axiom(power)==='power','power axiom');
    const floors={unary:encode(power).length+1,compact:sp.compact(power).length+1};
    assert(floors.unary===86&&floors.compact===38,'power cost');
    const rows=Object.entries(sp.encodings).map(([encoding,enc])=>({
      encoding,fragment_maximum_cost:floors[encoding]-1,minimum_false_axiom_line:floors[encoding],
      ...sem.semanticFloor(f,enc,floors[encoding])}));
    return {all_formulas_through_18:all.length,admissible_short_separation_predicates:admissible,recognized,high_rank:highRank,max_rank:maxRank,by_formula_bytes:byBytes,trace_classes:classes,rank_counts:rankCounts,
      detector:{predicate_unary:encode(detect),rank:2,separation_line_unary:encode(separation(detect)).length+1,separation_line_compact:sp.compact(separation(detect)).length+1,finite_surrogate_checks:detectorChecks,panels},bounds:rows};
  }
  return {stats,classify,run};
}
export const fragment=buildFragment(kernel,bounds,spine,semantic);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/fragment.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(fragment.run(raw),null,2));
}
