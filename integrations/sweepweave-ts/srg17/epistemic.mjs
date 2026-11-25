// SRG-17B: finite nested belief with a uniform common prior on 27 worlds.
const ck=(v,m)=>{if(!v)throw Error("SRG17B: "+m);};
export const ESEED=0x53521702;
const worlds=Array.from({length:27},(_,i)=>[Math.floor(i/9),Math.floor(i/3)%3,i%3]),idx=w=>9*w[0]+3*w[1]+w[2],agents=["Ada","Ben","Cy"];
const cell=(w,i)=>[0,1,2].map(x=>{const a=[...w];a[i]=x;return idx(a);});
const maj=a=>Number(a.reduce((s,x)=>s+x,0)>=2);
export function operator(p,i){return worlds.map(w=>maj(cell(w,i).map(j=>p[j])));}
export function evaluate(p,chain){
 ck(p.length===27&&p.every(x=>x===0||x===1)&&chain.every(i=>Number.isInteger(i)&&i>=0&&i<3),"invalid formula");
 return [...chain].reverse().reduce((v,i)=>operator(v,i),p.slice());
}
function rec(p,chain,w){return !chain.length?p[idx(w)]:maj([0,1,2].map(x=>{const a=[...w];a[chain[0]]=x;return rec(p,chain.slice(1),a);}));}
function rng(seed){let x=seed>>>0||1;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};}
export function buildBelief(seed=ESEED,reps=16,allWorlds=true){
 const r=rng(seed),tasks=[],gold=[];let tests=0;
 ck(Number.isInteger(reps)&&reps>0&&reps<=64,"reps");
 for(let rep=0;rep<reps;rep++){
  const p=worlds.map(()=>r()&1),perm=[0,1,2].map(i=>[r(),i]).sort((a,b)=>a[0]-b[0]).map(x=>x[1]),selected=allWorlds?worlds:[worlds[r()%27]];
  for(let depth=0;depth<=3;depth++){
   const chain=perm.slice(0,depth),v=evaluate(p,chain),inv=evaluate(p.map(x=>1-x),chain);
   for(const w of worlds){const j=idx(w);ck(v[j]===rec(p,chain,w),"recursive mismatch");ck(v[j]+inv[j]===1,"complement");tests++;}
   for(const c of [0,1])for(const w of selected){
    const truth=c?p.map(x=>1-x):p,answer=(c?inv:v)[idx(w)],key="srg17b_"+rep+"_"+depth+"_"+c+"_"+idx(w);
    const cut=Array.from({length:depth+1},(_,k)=>evaluate(truth,chain.slice(0,k))[idx(w)]),order=(rep+depth+c+idx(w))%2?["yes","no"]:["no","yes"];
    tasks.push({id:key,kind:"storyworld_policy",root_horizon:1,action_budget:1,goal:"Determine whether the stated proposition is true in the specified world.",
     task:"There are 27 equally likely worlds (a,b,c), each coordinate in {0,1,2}. Ada observes b,c; Ben observes a,c; Cy observes a,b. Each agent believes a proposition exactly when it is true in at least two of its three indistinguishable worlds, using the uniform common prior. For nested statements evaluate the innermost proposition first in every world, then each outer agent's belief operator. The proposition truth table is in lexicographic (a,b,c) order. The actual world and truth table are public to the evaluator answering the question.",
     rules:{formula_agents_outer_to_inner:chain.map(i=>agents[i]),proposition_truth_table:truth.join(""),actual_world:w},
     observation:{encounter:"belief_query",status:"decision",actions:order.map(a=>({id:a,text:a==="yes"?"True":"False"}))},output_contract:"Return one legal action ID."});
    gold.push({id:key,depth,answer:answer?"yes":"no",cut,rep,world:idx(w),complement:c});
   }
  }
 }
 return {tasks,gold,tests};
}
export function summarize(e){
 return {recursive_checks:e.tests,complement_checks:e.tests,rows:e.tasks.length,groups:[0,1,2,3].map(depth=>{
  const rows=e.gold.filter(g=>g.depth===depth),yes=rows.filter(g=>g.answer==="yes").length;ck(yes===rows.length/2,"balance");
  return {depth,rows:rows.length,yes,truncate_accuracy:Array.from({length:depth+1},(_,k)=>rows.filter(g=>g.cut[k]===g.cut[depth]).length/rows.length)};
 })};
}
export function scoreBelief(e,sub){
 const m=new Map(),dup=new Set(),ids=new Set(e.gold.map(g=>g.id));let malformed=0;
 for(const s of sub){if(!s||typeof s.id!=="string"){malformed++;continue;}if(m.has(s.id))dup.add(s.id);else m.set(s.id,s);}
 const valid=g=>{const s=m.get(g.id);return !!s&&!dup.has(g.id)&&Object.keys(s).sort().join(",")==="action,id"&&["yes","no"].includes(s.action);};
 return {rows:e.gold.length,valid:e.gold.filter(valid).length,malformed,duplicates:dup.size,unknown:[...m.keys()].filter(id=>!ids.has(id)).length,groups:[0,1,2,3].map(depth=>{const rows=e.gold.filter(g=>g.depth===depth);return {depth,rows:rows.length,correct:rows.filter(g=>valid(g)&&m.get(g.id).action===g.answer).length};})};
}
