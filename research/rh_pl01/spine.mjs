// RH-PL-04: implication-spine lower bound and compact encoding sensitivity.
import {kernel} from './kernel.mjs';
import {bounds} from './bounds.mjs';
function buildSpine(k){
  const {E,M,N,I,Q,encode,decode,axiom,subst,free}=k;
  const digits='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const compactVar=x=>{
    if(!Number.isSafeInteger(x)||x<0)throw Error('variable');
    return x<36?digits[x]:'~'+x.toString(36).toUpperCase()+';';
  };
  function compact(f){
    switch(f[0]){
      case'e':case'm':return f[0]+compactVar(f[1])+compactVar(f[2]);
      case'n':return'n'+compact(f[1]);
      case'i':return'i'+compact(f[1])+compact(f[2]);
      case'a':return'a'+compactVar(f[1])+compact(f[2]);
      default:throw Error('formula');
    }
  }
  function parseCompact(s){
    let p=0;
    function v(){
      const c=s[p++];if(c===undefined)throw Error('variable');
      if(c!=='~'){const n=digits.indexOf(c);if(n<0)throw Error('variable');return n}
      const start=p;while(p<s.length&&digits.includes(s[p]))p++;
      const raw=s.slice(start,p);
      if(s[p++]!==';'||!raw||raw[0]==='0')throw Error('noncanonical variable');
      const n=parseInt(raw,36);
      if(n<36||!Number.isSafeInteger(n)||compactVar(n)!=='~'+raw+';')throw Error('noncanonical variable');
      return n;
    }
    function f(){switch(s[p++]){case'e':return E(v(),v());case'm':return M(v(),v());case'n':return N(f());case'i':return I(f(),f());case'a':return Q(v(),f());default:throw Error('formula')}}
    const out=f();if(p!==s.length)throw Error('trailing bytes');return out;
  }
  const encodings={
    unary:{encode,w:x=>x+2,vmin:2},
    compact:{encode:compact,w:x=>compactVar(x).length,vmin:1}
  };
  // Every fixed axiom is < 1024 bytes in unary; compact never costs more.
  // The pinned kernel's fixed-axiom inventory is checked independently.
  const fixedCap=1024;
  function freeCounts(f){
    const result=new Map(),scope=new Map();
    const add=x=>{if(!scope.get(x))result.set(x,(result.get(x)||0)+1)};
    function visit(g){switch(g[0]){
      case'e':case'm':add(g[1]);add(g[2]);break;
      case'n':visit(g[1]);break;
      case'i':visit(g[1]);visit(g[2]);break;
      case'a':scope.set(g[1],(scope.get(g[1])||0)+1);visit(g[2]);scope.set(g[1],scope.get(g[1])-1);break;
    }}visit(f);return result;
  }
  function shape(f,v){
    switch(f[0]){
      case'e':case'm':return 1+2*v;
      case'n':return 1+shape(f[1],v);
      case'i':return 1+shape(f[1],v)+shape(f[2],v);
      case'a':return 1+v+shape(f[2],v);
      default:throw Error('formula');
    }
  }
  function m(f,enc){
    let save=0;
    for(const [x,c] of freeCounts(f))save=Math.max(save,(enc.w(x)-enc.vmin)*c);
    return Math.max(shape(f,enc.vmin),enc.encode(f).length-save);
  }
  function old(f,enc){
    const n=enc.encode(f).length,d=1+2*enc.vmin,q=1+enc.vmin;
    if(axiom(f))return n+1;
    if(f[0]!=='a')return 2*n+2*d+4;
    return Math.min(2*n+2*m(f,enc)+2*q+4,3*n+4*d+7,n+1+old(f[2],enc));
  }
  function cases(f,enc){
    const n=enc.encode(f).length,d=1+2*enc.vmin,q=1+enc.vmin;
    if(axiom(f))return {axiom:n+1};
    if(f[0]!=='a')return {mp:2*n+2*d+4};
    const t=m(f,enc);
    const k1=t+q>fixedCap
      ? 2*n+3*t+(freeCounts(f).size===0?3*q+d+6:2*q+5)
      : 2*n+2*t+2*q+4;
    return {
      axiom_at_1:k1,
      axiom_at_2:Math.min(5*n+5*d+14,5*n+5*d+10,3*n+2*t+5*d+2*q+10),
      axiom_at_3:4*n+t+8*d+13,
      at_least_4:5*n+11*d+16,
      generalization:n+1+bound(f[2],enc)
    };
  }
  function bound(f,enc){return Math.min(...Object.values(cases(f,enc)))}
  function verifyCompact(proof,target){
    try{
      if(!proof.endsWith('\n'))return false;
      const lines=proof.slice(0,-1).split('\n').map(s=>encode(parseCompact(s)));
      return k.verify(lines.join('\n')+'\n',encode(parseCompact(target)));
    }catch{return false}
  }
  function run(raw,formulae){
    const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
    const f=decode(raw.slice(0,-1));
    assert(encode(f)+'\n'===raw&&free(f).size===0,'frozen target');
    const c=compact(f);
    assert(encode(parseCompact(c))+'\n'===raw,'compact roundtrip');
    const rows=Object.entries(encodings).map(([name,enc])=>({encoding:name,formula_bytes:enc.encode(f).length,min_shape:shape(f,enc.vmin),previous:old(f,enc),spine:bound(f,enc),cases:cases(f,enc)}));
    const pool=formulae.filter(g=>encode(g).length<=8);
    let proofChecks=0, formulaChecks=0, substitutionChecks=0, terminalChecks=0, compactRejects=0;
    function checkProof(fs){
      const seen=new Set(), implications=[];
      const cumulative={unary:0,compact:0};
      for(const g of fs){
        const s=encode(g);
        const ok=axiom(g)||(g[0]==='a'&&seen.has(encode(g[2])))||implications.some(([a,h])=>h===s&&seen.has(a));
        assert(ok,'control proof invalid');
        for(const [name,enc] of Object.entries(encodings)){
          cumulative[name]+=enc.encode(g).length+1;
          assert(bound(g,enc)<=cumulative[name],'bound exceeds proof');
          assert(bound(g,enc)>=old(g,enc),'regressed bound');
          proofChecks++;
        }
        seen.add(s);if(g[0]==='i')implications.push([encode(g[1]),encode(g[2])]);
      }
      const g=fs.at(-1);
      if(!free(g).size)assert(verifyCompact(fs.map(compact).join('\n')+'\n',compact(g)),'compact proof invalid');
    }
    for(const g of formulae){
      assert(encode(parseCompact(compact(g)))===encode(g),'small compact roundtrip');
      formulaChecks++;
      for(const x of [0,1,2,35,36,1296])for(const y of [0,1,2,35,36,1296]){
        let h;try{h=subst(g,x,y)}catch{continue}
        for(const enc of Object.values(encodings)){assert(enc.encode(g).length>=m(h,enc),'substitution floor');substitutionChecks++}
      }
    }
    for(const a of pool)for(const p of pool){
      const K=I(a,I(p,a));
      checkProof([K,Q(0,K),Q(1,Q(0,K)),I(Q(1,Q(0,K)),Q(0,K)),Q(0,K)]);
      const r=E(0,0), id=I(p,p);
      if(axiom(I(r,id)))checkProof([r,I(r,id),id,Q(0,id),Q(1,Q(0,id)),Q(2,Q(1,Q(0,id)))]);
      for(const g of [Q(0,p),Q(1,Q(0,p))]){
        const H1=I(a,g);
        const cases2=[I(I(N(g),N(a)),H1),I(Q(0,I(a,p)),H1),I(Q(2,H1),H1)];
        for(const h of cases2){
          if(!axiom(h))continue;
          // K can be excluded by chronological collision; for the
          // remaining cases count the actual distinct mandatory lines.
          const a2=h[1], set=new Map([g,a,H1,a2,h].map(x=>[encode(x),x]));
          if(set.size<5)continue;
          for(const enc of Object.values(encodings)){
            const n=enc.encode(g).length,d=1+2*enc.vmin,q=1+enc.vmin,t=m(g,enc);
            const floor=Math.min(5*n+5*d+14,5*n+5*d+10,3*n+2*t+5*d+2*q+10);
            const total=[...set.values()].reduce((s,x)=>s+enc.encode(x).length+1,0);
            assert(total>=floor,'depth2 floor');terminalChecks++;
          }
        }
        const H2=I(I(a,p),H1), S=I(I(a,I(p,g)),H2);
        for(const h of [S,I(I(N(H1),N(a)),I(a,H1)),I(Q(2,H2),H2)]){
          if(!axiom(h))continue;
          const h2=h[2],h1=h2[2],f0=h1[2];
          if(encode(f0)!==encode(g))continue;
          const set=new Map([g,h1,h2,h,a].map(x=>[encode(x),x]));
          if(set.size<5)continue;
          for(const enc of Object.values(encodings)){
            const n=enc.encode(g).length,d=1+2*enc.vmin,t=m(g,enc);
            const total=[...set.values()].reduce((s,x)=>s+enc.encode(x).length+1,0);
            assert(total>=4*n+t+8*d+13,'depth3 floor');terminalChecks++;
          }
        }
      }
    }
    for(const s of ['e~0;0','e~Z;0','e~010;0','e~10','e~10;0x','e0','a~;e00','e-0']){
      let rejected=false;try{parseCompact(s)}catch{rejected=true}
      assert(rejected,'malformed compact accepted');compactRejects++;
    }
    for(const x of [0,35,36,1295,1296,Number.MAX_SAFE_INTEGER]){
      const g=Q(x,E(x,x));assert(JSON.stringify(parseCompact(compact(g)))===JSON.stringify(g),'extended compact roundtrip');
    }
    return {target_closed:true,encodings:rows,formula_roundtrips:formulaChecks,proof_prefix_encoding_checks:proofChecks,substitution_encoding_checks:substitutionChecks,terminal_axiom_encoding_checks:terminalChecks,compact_parse_negatives:compactRejects};
  }
  return {compact,parseCompact,encodings,m,old,cases,bound,verifyCompact,run};
}
export const spine=buildSpine(kernel);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/spine.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 if(process.argv.includes('--compact'))process.stdout.write(spine.compact(kernel.decode(raw.slice(0,-1)))+'\n');
 else console.log(JSON.stringify(spine.run(raw,bounds.formulae(11)),null,2));
}
