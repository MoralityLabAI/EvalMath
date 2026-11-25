// SRG-AC06 controlled K ladder. Public diagnostic, not sealed model data.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
const ck=(x,m)=>{if(!x)throw Error("AC06 ladder: "+m);};
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),sum=(a,f)=>a.reduce((s,x)=>s+f(x),0);
const pop=x=>{let n=0;for(;x;x>>>=1)n+=x&1;return n;};
const bit=(m,j)=>m&(1<<j)?-1:1;
export const LADDER={J:[1,2,4,6],K:[8,32,128],H:2,seed:0x53522621};
const feature=j=>"state.signal"+j;
const dock=s=>s===1?"dock_pos":"dock_neg";
const goal="goal";
export function fixture(J,K){
 ck(LADDER.J.includes(J)&&LADDER.K.includes(K)&&J<K,"dimensions");
 const lines=["# SWMD-SRG/2","id: AC06-J"+J+"-K"+K,'title: "Warehouse signal board"','about: "Read the signed causal signals and choose the matching dock."',"start: p0","turn-base: 0","tie: first","direct: strict"];
 for(let j=0;j<K;j++)lines.push("VAR "+feature(j)+" = 0 | public");
 const pages=[...Array.from({length:J+2},(_,i)=>"p"+i),"ready_good","ready_bad","goal","fail"];
 lines.push("SPOOL all | A:TRUE | E:"+pages.join(","));
 function enc(id,t){lines.push("ENC "+id+" turn="+t+".."+t+" | I:"+t+" | A:TRUE | Q:C(0) | N:"+JSON.stringify(id)+" | T:\"Inspect the signal board.\"");}
 function opt(id,text){lines.push("OPT "+id+" | V:TRUE | P:TRUE | T:"+JSON.stringify(text));}
 function rx(a,r,to,e,d="C(0)"){lines.push("ORX "+a+"/"+r+" -> "+to+" | E:"+e+" | D:"+d+" | G:TRUE | T:\"The board advances.\"");}
 for(let i=0;i<=J;i++){
  enc("p"+i,i);
  for(const s of [-1,1]){
   const a="set_"+i+"_"+(s===1?"pos":"neg");opt(a,"Set the next signal group to "+s);
   const writes=i<J?["SET "+feature(i)+" = C("+s+")"]:Array.from({length:K-J},(_,z)=>"SET "+feature(J+z)+" = C("+(s*(z%2?-1:1))+")");
   rx(a,"r_"+a,"p"+(i+1),writes.join("; "));
  }
 }
 enc("p"+(J+1),J+1);
 const terms=Array.from({length:J},(_,j)=>"P("+feature(j)+")"),product=J===1?terms[0]:"MUL("+terms.join(",")+")";
 for(const s of [-1,1]){
  const a=dock(s);opt(a,s===1?"Choose positive dock":"Choose negative dock");
  rx(a,"r_"+a+"_good","ready_good","NONE","MUL(C("+(.25*s)+"),"+product+")");
  rx(a,"r_"+a+"_bad","ready_bad","NONE","MUL(C("+(-.25*s)+"),"+product+")");
 }
 for(const good of [true,false]){
  const p=good?"ready_good":"ready_bad",a="finish_"+p;enc(p,J+2);opt(a,"Finish delivery");rx(a,"r_"+a,good?"goal":"fail","NONE");
 }
 enc("goal",J+3);enc("fail",J+3);
 return lines.join("\n")+"\n";
}
function walsh(values){
 const n=values.length,coefficients=[];
 for(let m=0;m<n;m++){
  let v=0;for(let i=0;i<n;i++)v+=(pop(i&m)%2?-1:1)*values[i];
  v/=n;if(v!==0)coefficients.push({mask:m,degree:pop(m),coefficient:v});
 }
 return {degree:Math.max(0,...coefficients.map(x=>x.degree)),coefficients};
}
function projected(row,mask,J){
 return JSON.stringify([row.menu,Array.from({length:J+1},(_,j)=>j).filter(j=>mask&(1<<j)).map(j=>row.values[j])]);
}
function subset(rows,J,ct){
 const n=1<<(J+1),causal=(1<<J)-1,full=rows.length,cert=[],hist=Array(n).fill(0);
 for(let a=0;a<n;a++)for(let b=0;b<a;b++)if(rows[a].label!==rows[b].label)hist[a^b]++;
 for(let mask=0;mask<n;mask++){
  const groups=new Map();
  for(const r of rows){const k=projected(r,mask,J),g=groups.get(k)??[];g.push(r);groups.set(k,g);}
  let v=0,conflicts=0;
  for(const g of groups.values()){
   const pos=sum(g,r=>Number(r.label==="dock_pos")),neg=g.length-pos;
   v+=Math.max(pos,neg);conflicts+=pos*neg;
   if((mask&causal)!==causal)ck(pos===neg,"unbalanced missing-bit cell");
   else ck(pos===0||neg===0,"full causal cell conflict");
  }
  let predicted=0;for(let m=0;m<n;m++)if(!(m&mask))predicted+=hist[m];
  ck(predicted===conflicts,"hitting-set equivalence");ct.conflict_checks++;
  ck(v===((mask&causal)===causal?full:full/2),"subset ceiling");ct.subset_checks++;
  cert.push({mask,k:pop(mask),value:v,conflicts,cells:groups.size});
 }
 for(let m=0;m<n;m++)for(let j=0;j<=J;j++)if(!(m&(1<<j))){
  ck(cert[m].value<=cert[m|(1<<j)].value,"subset monotonicity");ct.subset_edges++;
 }
 const frontier=Array.from({length:J+2},(_,k)=>({k,value:Math.max(...cert.filter(c=>c.k===k).map(c=>c.value))}));
 const min=cert.filter(c=>c.value===full&&c.k===J).map(c=>c.mask);
 ck(eq(min,[causal]),"minimum sufficient mask");
 return {subsets:cert,frontier,min_cardinality:J,minimum_mask:causal,necessary_singleton_conflicts:Array.from({length:J},(_,j)=>hist[1<<j]),full};
}
function random(seed){
 let x=seed>>>0;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};
}
export function build(api=runtime){
 const ct={fixtures:0,prefix_steps:0,root_transitions:0,finish_transitions:0,reaction_score_checks:0,subset_checks:0,subset_edges:0,conflict_checks:0,nuisance_pairs:0,causal_pairs:0},cases=[],tasks=[],gold=[],rand=random(LADDER.seed),ids=new Set(),byJ=new Map();
 for(const J of LADDER.J)for(const K of LADDER.K){
  const w=api.compileV2(fixture(J,K)),rows=[],N=1<<(J+1);ct.fixtures++;
  for(let m=0;m<N;m++){
   let s=api.initialV2(w);
   for(let j=0;j<=J;j++){const a="set_"+j+"_"+(bit(m,j)===1?"pos":"neg"),b=api.stepV2(w,s,a);s=b.next;ct.prefix_steps++;}
   const o=api.observeV2(w,s),menu=o.actions.map(a=>a.id),values=Array.from({length:K},(_,j)=>o.values[feature(j)]);
   ck(o.status==="decision"&&o.encounter==="p"+(J+1)&&eq(menu,["dock_neg","dock_pos"]),"root observation");
   ck(Object.keys(o.values).length===K,"public K");
   for(let j=0;j<K;j++)ck(values[j]===(j<J?bit(m,j):bit(m,J)*((j-J)%2?-1:1)),"signal prefix replay");
   const product=values.slice(0,J).reduce((a,b)=>a*b,1),label=dock(product),audit=api.auditV2(w,s);
   const q={},h1={};let contrast=null;
   for(const a of o.actions){
    const b=api.stepV2(w,s,a.id),aa=audit.actions.find(x=>x.id===a.id);
    ck(aa.selected===b.id&&aa.status==="ok","audit selected reaction");ct.root_transitions++;
    const sg=a.id==="dock_pos"?1:-1,scores=aa.scores;
    ck(scores.length===2&&scores.every(x=>x.eligible)&&scores[0].score===.25*sg*product&&scores[1].score===-.25*sg*product,"score contrast");ct.reaction_score_checks++;
    if(a.id==="dock_pos")contrast=scores[0].score-scores[1].score;
    const ob=api.observeV2(w,b.next);h1[a.id]=Number(ob.status==="terminal"&&ob.encounter===goal);
    ck(ob.status==="decision"&&ob.actions.length===1,"forced finish");
    const next=api.stepV2(w,b.next,ob.actions[0].id);ct.finish_transitions++;
    const end=api.observeV2(w,next.next);ck(end.status==="terminal","finish terminal");
    q[a.id]=Number(end.encounter===goal);
    ck(q[a.id]===Number(a.id===label),"utility parity");
   }
   ck(Object.values(h1).every(v=>v===0)&&Object.values(q).reduce((a,b)=>a+b,0)===1,"H1/H2 contrast");
   const row={m,menu:[o.encounter,o.turn,o.status,o.actions],values:[...values.slice(0,J),values[J]],label,q,contrast};rows.push(row);
   let id;do{id="ac06_"+rand().toString(16).padStart(8,"0")+rand().toString(16).padStart(8,"0");}while(ids.has(id));ids.add(id);
   tasks.push({id,kind:"storyworld_policy",goal:"Reach the successful delivery ending within two moves.",
    task:"The first J signed signals are causal. Multiply them; choose the positive dock if the product is +1, otherwise the negative dock. All other coordinates are nuisance signals. After choosing the dock, the only remaining action completes delivery. All listed current observations and these rules are public.",
    rules:{J,K,causal_indices:Array.from({length:J},(_,j)=>j),horizon:2,signal_encoding:"array of signed values -1 or +1"},
    observation:{encounter:"dock_choice",status:"decision",values:{signals:values},actions:o.actions},
    output_contract:"Return one legal action ID."});
   gold.push({id,J,K,answer:label,q});
  }
  ck(rows.filter(r=>r.label==="dock_pos").length===N/2,"balanced labels");
  for(let m=0;m<N;m++)for(let j=0;j<=J;j++)if(!(m&(1<<j))){
   const a=rows[m],b=rows[m|(1<<j)];ck(eq(a.menu,b.menu),"matched menu");
   if(j<J){ck(a.label!==b.label,"causal edge");ct.causal_pairs++;}
   else{ck(eq(a.q,b.q)&&a.contrast===b.contrast,"nuisance edge");ct.nuisance_pairs++;}
  }
  const a=subset(rows,J,ct),contrast=walsh(rows.map(r=>r.contrast)),utility=walsh(rows.map(r=>r.q.dock_pos));
  ck(contrast.degree===J&&utility.degree===J,"Walsh order");
  const signature=JSON.stringify([rows.map(r=>[r.values,r.label,r.q]),a.frontier,contrast,utility]);
  if(byJ.has(J))ck(byJ.get(J)===signature,"matched K invariance");else byJ.set(J,signature);
  cases.push({J,K,roots:N,positive:N/2,negative:N/2,informative:N,H1_attainable:0,H2_attainable:N,nuisance_rank:1,...a,contrast_walsh:contrast,utility_walsh:utility});
 }
 // Shuffle only task presentation; opaque IDs are assigned independent of labels.
 const shuffled=tasks.map(t=>[rand(),t]).sort((a,b)=>a[0]-b[0]).map(x=>x[1]);
 return {design:LADDER,counts:ct,cases,tasks:shuffled,gold};
}
export function score(e,submissions){
 const map=new Map(),dups=new Set(),ids=new Set(e.gold.map(g=>g.id));let malformed=0;
 for(const r of submissions){
  if(!r||typeof r.id!=="string"){malformed++;continue;}
  if(map.has(r.id))dups.add(r.id);else map.set(r.id,r);
 }
 const rows=e.cases.map(c=>({J:c.J,K:c.K,roots:c.roots,correct:0,valid:0}));
 for(const g of e.gold){
  const r=map.get(g.id),a=rows.find(x=>x.J===g.J&&x.K===g.K);
  const valid=!!r&&!dups.has(g.id)&&Object.keys(r).sort().join(",")==="action,id"&&typeof r.action==="string"&&Object.hasOwn(g.q,r.action);
  a.valid+=Number(valid);a.correct+=Number(valid&&r.action===g.answer);
 }
 return {rows,roots:e.gold.length,valid:sum(rows,r=>r.valid),correct:sum(rows,r=>r.correct),macro_accuracy:sum(rows,r=>r.correct/r.roots)/rows.length,malformed,duplicate_ids:dups.size,unknown_ids:[...map.keys()].filter(k=>!ids.has(k)).length};
}
// Equal two roots per answer label per (J,K), using the fixed shuffled
// presentation order. Full-cube verification is still mandatory.
export function pilot(e){
 const labels=new Map(e.gold.map(g=>[g.id,g])),keep=new Set();
 const cases=e.cases.map(c=>{
  for(const answer of ["dock_neg","dock_pos"]){
   const rows=e.tasks.filter(t=>{const g=labels.get(t.id);return g.J===c.J&&g.K===c.K&&g.answer===answer;}).slice(0,2);
   ck(rows.length===2,"pilot label coverage");for(const t of rows)keep.add(t.id);
  }
  return {J:c.J,K:c.K,roots:4};
 });
 return {design:e.design,counts:e.counts,cases,tasks:e.tasks.filter(t=>keep.has(t.id)),gold:e.gold.filter(g=>keep.has(g.id))};
}
export function receipt(api=runtime){
 const e=build(api),p=pilot(e),pilotOracle=score(p,p.gold.map(g=>({id:g.id,action:g.answer}))),pilotFirst=score(p,p.gold.map(g=>({id:g.id,action:"dock_neg"}))),oracle=score(e,e.gold.map(g=>({id:g.id,action:g.answer}))),first=score(e,e.gold.map(g=>({id:g.id,action:"dock_neg"}))),missing=score(e,[]),bad=score(e,[{id:e.gold[0].id,action:"dock_neg"},{id:e.gold[0].id,action:"dock_pos"},null,{id:"unknown",action:"dock_pos"},{id:e.gold[1].id,action:"invalid"},{id:e.gold[2].id,action:["dock_neg"]}]);
 ck(pilotOracle.roots===48&&pilotOracle.correct===48&&pilotFirst.correct===24&&pilotFirst.macro_accuracy===.5,"pilot scoring");
 ck(oracle.correct===e.gold.length&&oracle.valid===e.gold.length&&first.correct===e.gold.length/2&&missing.correct===0&&bad.valid===0&&bad.duplicate_ids===1&&bad.malformed===1&&bad.unknown_ids===1,"scorer controls");
 return {schema:"ac06.ladder.v1",evidence:"executed actual compiled SWMD, full legal cube and exact finite subset oracle",design:e.design,counts:e.counts,cases:e.cases,corpus:{rows:e.tasks.length,oracle,first,missing,malformed:bad,pilot:{rows:p.tasks.length,oracle:pilotOracle,first:pilotFirst}}};
}
