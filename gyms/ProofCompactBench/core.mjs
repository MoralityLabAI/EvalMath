export function library(){
  const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
  const unique=a=>new Set(a).size===a.length;
  const pop=x=>{let n=0;while(x){n++;x&=x-1}return n};
  const rng=seed=>{let x=seed>>>0||0x9e3779b9;return n=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)%n}};
  const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
  const union=xs=>[...new Set(xs.flat())].sort((a,b)=>a-b);
  const indices=n=>Array.from({length:n},(_,i)=>i);
  const isInts=(a,n)=>Array.isArray(a)&&unique(a)&&a.every(x=>Number.isInteger(x)&&x>=0&&x<n);
  const sameSet=(a,b)=>eq([...a].sort((a,b)=>a-b),[...b].sort((a,b)=>a-b));
  const parity=x=>pop(x)%2;
  function dag(n,R){
    const weights=indices(n).map(()=>1+R(9));
    const deps=indices(n).map(i=>indices(i).filter(()=>R(4)===0));
    for(let i=1;i<n;i++)if(!deps[i].length&&R(2))deps[i].push(R(i));
    return {weights,deps};
  }
  function dagCost(p,order){
    const n=p.weights.length,done=new Set();let peak=0;
    if(!isInts(order,n)||order.length!==n)return null;
    for(const v of order){
      if(!p.deps[v].every(i=>done.has(i)))return null;
      const live=[...done].filter(i=>p.deps.some((ds,j)=>!done.has(j)&&ds.includes(i)));
      peak=Math.max(peak,p.weights[v]+live.reduce((a,i)=>a+p.weights[i],0));done.add(v);
    }return peak;
  }
  function dagOpt(p){
    const n=p.weights.length,full=(1<<n)-1,dp=new Map();
    function go(s){
      if(s===full)return {peak:0,order:[]};
      if(dp.has(s))return dp.get(s);
      const live=indices(n).filter(i=>s>>i&1&&p.deps.some((ds,j)=>!(s>>j&1)&&ds.includes(i))).reduce((a,i)=>a+p.weights[i],0);
      let best={peak:Infinity,order:[]};
      for(let v=0;v<n;v++)if(!(s>>v&1)&&p.deps[v].every(i=>s>>i&1)){
        const tail=go(s|1<<v),peak=Math.max(live+p.weights[v],tail.peak);
        if(peak<best.peak)best={peak,order:[v,...tail.order]};
      }dp.set(s,best);return best;
    }return go(0);
  }
  function dagBrute(p){
    const n=p.weights.length;let best=Infinity;
    function visit(order){
      if(order.length===n){best=Math.min(best,dagCost(p,order));return}
      for(let i=0;i<n;i++)if(!order.includes(i)&&p.deps[i].every(j=>order.includes(j)))visit([...order,i]);
    }visit([]);return best;
  }
  function cacheCost(p,kept){
    if(!isInts(kept,p.intervals.length))return null;
    for(let t=0;t<p.capacity.length;t++)if(kept.filter(i=>p.intervals[i][0]<=t&&t<=p.intervals[i][1]).length>p.capacity[t])return null;
    return p.intervals.length-kept.length;
  }
  function cacheOpt(p){
    const kept=new Set(),active=new Set();
    for(let t=0;t<p.capacity.length;t++){
      for(const i of active)if(p.intervals[i][1]<t)active.delete(i);
      p.intervals.forEach(([a,b],i)=>{if(a===t){active.add(i);kept.add(i)}});
      while(active.size>p.capacity[t]){
        const i=[...active].sort((i,j)=>p.intervals[j][1]-p.intervals[i][1]||j-i)[0];active.delete(i);kept.delete(i);
      }
    }return [...kept].sort((a,b)=>a-b);
  }
  function cacheBrute(p){let best=Infinity;for(let s=0;s<1<<p.intervals.length;s++){const c=cacheCost(p,indices(p.intervals.length).filter(i=>s>>i&1));if(c!==null)best=Math.min(best,c)}return best}
  function rank(rows){const b=[];let k=0;for(let x of rows)while(x){const i=31-Math.clz32(x);if(b[i])x^=b[i];else{b[i]=x;k++;break}}return k}
  function basis(rows){const out=[];for(let i=0;i<rows.length;i++)if(rank([...out.map(j=>rows[j]),rows[i]])>out.length)out.push(i);return out}
  const kernel=(rows,d)=>indices(1<<d).filter(x=>rows.every(r=>parity(r&x)===0));
  function apply(T,x){return T.reduce((a,r,i)=>a|(parity(r&x)<<i),0)}
  function obs(rows,x){return rows.map(r=>parity(r&x)).join("")}
  function partition(p){
    const N=1<<p.dimension,states=indices(N);
    function label(xs){const m=new Map();return xs.map(s=>{if(!m.has(s))m.set(s,m.size);return m.get(s)})}
    let labels=label(states.map(x=>obs(p.observations,x)));
    for(let k=0;k<=p.dimension+N;k++){
      const next=label(states.map(x=>JSON.stringify([obs(p.observations,x),...p.actions.map(T=>labels[apply(T,x)])])));
      if(eq(next,labels))return labels;labels=next;
    }throw Error("partition did not stabilize");
  }
  function closure(p){
    let rows=p.observations.slice();rows=basis(rows).map(i=>rows[i]);
    for(let i=0;i<rows.length;i++)for(const T of p.actions){
      const x=T.reduce((a,r,j)=>a^((rows[i]>>j&1)?r:0),0);if(rank([...rows,x])>rows.length)rows.push(x);
    }return rows;
  }
  function canonicalLabels(a){const m=new Map();return a.map(x=>{if(!m.has(x))m.set(x,m.size);return m.get(x)})}
  function factorCost(p,chosen){
    if(!isInts(chosen,p.blocks.length)||chosen.length>p.max_helpers)return null;
    let root=p.fixed,closureSize=p.fixed;
    for(let i=0;i<p.blocks.length;i++){
      const b=p.blocks[i];
      // All menu items are certified equivalent in this proxy; inadmissible captures are blocked.
      if(chosen.includes(i)){
        if(!b.uniform_capture)return null;
        root+=b.uses*b.call_cost;
        closureSize+=b.uses*b.call_cost+b.body_cost+b.helper_overhead;
      }else{root+=b.uses*b.body_cost;closureSize+=b.uses*b.body_cost}
    }return root<=p.root_cap?closureSize:null;
  }
  function factorOpt(p){let best=null;for(let s=0;s<1<<p.blocks.length;s++){const chosen=indices(p.blocks.length).filter(i=>s>>i&1),cost=factorCost(p,chosen);if(cost!==null&&(!best||cost<best.cost))best={chosen,cost}}return best}
  function factorIndependent(p){
    // DP over helper count and parent size, with explicit inline/extract alternatives.
    let states=new Map([[`0,${p.fixed}`,p.fixed]]);
    for(const b of p.blocks){
      const next=new Map();
      for(const [key,cost] of states){
        const [k,r]=key.split(",").map(Number);
        for(const [kk,rr,cc] of [[k,r+b.uses*b.body_cost,cost+b.uses*b.body_cost],...(b.uniform_capture&&k<p.max_helpers?[[k+1,r+b.uses*b.call_cost,cost+b.uses*b.call_cost+b.body_cost+b.helper_overhead]]:[])]){
          if(rr>p.root_cap)continue;const id=`${kk},${rr}`;next.set(id,Math.min(next.get(id)??Infinity,cc));
        }
      }states=next;
    }return Math.min(Infinity,...states.values());
  }
  const families=["factoring","scheduling","retention","uniform","continuation","repair"];
  const descriptions={
    factoring:"Select helper indices to minimize total closure expression cost under the parent-size cap and helper limit. Only uniform_capture=true is eligible. Inline cost=uses*body_cost, extraction parent cost=uses*call_cost and total cost=parent cost+body_cost+helper_overhead. Add fixed once. Return {helpers:[indices]}.",
    scheduling:"Return {order:[node indices]} minimizing peak live weight, no recomputation. Evaluate dependencies first. Previously evaluated nodes with any unfinished consumer stay live. Allocate next node before freeing predecessors.",
    retention:"Each listed inclusive interval represents retaining a unit handle across a gap, saving one reload. Select maximum feasible number with per-time capacity. Return {keep:[interval indices]}.",
    uniform:"Each row is a bitmask over GF(2); all twist rows impose parity(row & x)=0. Return {basis:[indices in flattened twist-row list]}; basis must span the combined row space and be independent, giving the maximal uniform kernel.",
    continuation:"GF(2) state x is encoded as integer 0..2^dimension-1. Observation is parity of each observation row. Each action matrix is rows of bitmasks; next state bit i is parity(row_i & x). Return {classes:[integer labels by state]}; labels must preserve all finite future observations under any action sequence and use the minimum number of classes. Arbitrary relabeling allowed.",
    repair:"An invalid proposal is supplied. Return {order:[node indices]} repairing it into a legal topological schedule of minimum peak live weight. Same allocate-before-free, no-recompute rules as scheduling."
  };
  function generate(root,seed,split,stress=false){
    const R=rng((seed^Math.imul(root+1,0x9e3779b9))>>>0),out=[];
    function add(family,input,answer,optimum){out.push({id:`pcb-${root}-${family}`,root:`pcb-${root}`,split,family,task:descriptions[family],input,answer,optimum,claim_type:"exact_synthetic",training_eligible:split==="train",admission_status:"candidate_not_admitted"})}
    const n=(stress?7:4)+R(stress?2:3),p=dag(n,R),d=dagOpt(p);
    assert(d.peak===dagBrute(p)&&dagCost(p,d.order)===d.peak,"schedule oracle");add("scheduling",p,{order:d.order},d.peak);
    const q=dag(n,R);if(!q.deps.some(x=>x.length))q.deps[1]=[0];
    const bad=indices(n).reverse(),r=dagOpt(q);assert(dagCost(q,bad)===null&&r.peak===dagBrute(q),"repair oracle");add("repair",{...q,proposal:bad},{order:r.order},r.peak);
    const times=3+R(4),intervals=indices(6+R(stress?6:3)).map(()=>{const a=R(times);return [a,a+R(times-a)]}),cp={capacity:indices(times).map(()=>R(4)),intervals},keep=cacheOpt(cp),co=cacheCost(cp,keep);
    assert(co===cacheBrute(cp),"retention oracle");add("retention",cp,{keep},co);
    const dim=(stress?5:2)+R(3),twists=indices(2+R(4)).map(()=>indices(1+R(3)).map(()=>R(1<<dim)));
    if(root%4===0)twists.push(twists[0].slice());
    const rows=twists.flat(),b=basis(rows);assert(kernel(rows,dim).length===1<<(dim-b.length)&&eq(kernel(rows,dim),kernel(b.map(i=>rows[i]),dim)),"uniform oracle");add("uniform",{dimension:dim,twists},{basis:b},b.length);
    const cd=(stress?4:2)+R(3),actions=indices(2).map(()=>indices(cd).map(()=>R(1<<cd))),observations=[1+R((1<<cd)-1)];
    if(root%3===0){const hidden=1<<(cd-1);observations[0]&=~hidden;for(const T of actions)for(let i=0;i<cd-1;i++)T[i]&=~hidden}
    const cont={dimension:cd,actions,observations},labels=partition(cont),cr=closure(cont);
    assert(eq(labels,canonicalLabels(indices(1<<cd).map(x=>obs(cr,x))))&&new Set(labels).size===1<<cr.length,"continuation oracle");add("continuation",cont,{classes:labels},1<<cr.length);
    const blocks=indices(stress?8:5+R(3)).map(()=>({body_cost:4+R(18),uses:1+R(4),call_cost:1+R(5),helper_overhead:R(8),uniform_capture:R(5)!==0}));
    const fixed=2+R(8),max_helpers=1+R(3),root_cap=fixed+blocks.reduce((s,b)=>s+b.uses*b.body_cost,0);
    // Select an attainable, sometimes restrictive parent budget independently of the objective.
    const eligible=indices(blocks.length).filter(i=>blocks[i].uniform_capture&&blocks[i].call_cost<blocks[i].body_cost).sort((i,j)=>blocks[j].uses*(blocks[j].body_cost-blocks[j].call_cost)-blocks[i].uses*(blocks[i].body_cost-blocks[i].call_cost)).slice(0,max_helpers);
    const cap=root_cap-eligible.reduce((s,i)=>s+blocks[i].uses*(blocks[i].body_cost-blocks[i].call_cost),0);
    const fp={fixed,blocks,max_helpers,root_cap:cap+R(root_cap-cap+1)},fo=factorOpt(fp);
    assert(fo&&fo.cost===factorIndependent(fp),"factoring oracle");add("factoring",fp,{helpers:fo.chosen},fo.cost);
    return out;
  }
  function grade(r,a){
    let cost=null,valid=false;
    if(!a||typeof a!=="object"||Array.isArray(a))return {valid:false,optimal:false,score:0,cost:null};
    const p=r.input,one=k=>Object.keys(a).length===1&&Object.hasOwn(a,k);
    if((r.family==="scheduling"||r.family==="repair")&&one("order"))cost=dagCost(p,a.order);
    else if(r.family==="retention"&&one("keep"))cost=cacheCost(p,a.keep);
    else if(r.family==="factoring"&&one("helpers"))cost=factorCost(p,a.helpers);
    else if(r.family==="uniform"&&one("basis")){
      const rows=p.twists.flat(),b=a.basis;
      if(isInts(b,rows.length)&&rank(b.map(i=>rows[i]))===b.length&&eq(kernel(rows,p.dimension),kernel(b.map(i=>rows[i]),p.dimension)))cost=b.length;
    }else if(r.family==="continuation"&&one("classes")){
      const b=a.classes,N=1<<p.dimension;
      if(Array.isArray(b)&&b.length===N&&b.every(x=>Number.isSafeInteger(x)&&x>=0)){
        const groups=new Map();let good=true;
        for(let x=0;x<N;x++){
          const sig=JSON.stringify([obs(p.observations,x),...p.actions.map(T=>b[apply(T,x)])]);
          if(groups.has(b[x])&&groups.get(b[x])!==sig)good=false;groups.set(b[x],sig);
        }
        if(good)cost=groups.size;
      }
    }
    valid=cost!==null;
    if(valid)assert(cost>=r.optimum,"candidate beats frozen independent optimum");
    const optimal=valid&&cost===r.optimum;
    // A feasible but suboptimal certificate gets credit, never more than an optimum.
    return {valid,optimal,score:!valid?0:optimal?1:0.5+0.5*(r.optimum+1)/(cost+1),cost};
  }
  function packet(r){const {answer,optimum,training_eligible,admission_status,...p}=r;return p}
  function gradeAll(rows,preds){
    const m=new Map(rows.map(r=>[r.id,r])),seen=new Map();assert(m.size===rows.length,"duplicate gold");
    for(const p of preds){assert(p&&typeof p.id==="string"&&m.has(p.id)&&!seen.has(p.id)&&Object.hasOwn(p,"answer")&&Object.keys(p).length===2,"invalid or duplicate prediction");seen.set(p.id,p.answer)}
    const per={};let valid=0,optimal=0,score=0,missing=0;
    const details=rows.map(r=>{const g=grade(r,seen.get(r.id));missing+=+!seen.has(r.id);valid+=+g.valid;optimal+=+g.optimal;score+=g.score;const p=per[r.family]??={total:0,valid:0,optimal:0,score_sum:0};p.total++;p.valid+=+g.valid;p.optimal+=+g.optimal;p.score_sum+=g.score;return {id:r.id,...g}});
    return {total:rows.length,valid,optimal,missing,mean_score:score/Math.max(rows.length,1),by_family:per,details};
  }
  function selfTest(){
    let count=0,structural=0;
    const all=[];
    for(let root=0;root<96;root++){const rows=generate(root,0x50434231,root<64?"train":root<80?"calibration":"dev_test",root>=80);all.push(...rows);for(const r of rows){assert(grade(r,r.answer).optimal,"gold rejected");count++}}
    for(let root=0;root<32;root++)for(const r of generate(root,0x91bf73a5,"private",true)){assert(grade(r,r.answer).optimal,"stress");structural++}
    const seen=new Set();for(const r of all){const key=JSON.stringify([r.family,r.input]);assert(!seen.has(key),"duplicate prompt");seen.add(key)}
    const roots=new Map();for(const r of all){assert(!roots.has(r.root)||roots.get(r.root)===r.split,"split leakage");roots.set(r.root,r.split)}
    assert(all.every(r=>!Object.hasOwn(packet(r),"answer")&&!Object.hasOwn(packet(r),"optimum")),"packet leakage");
    const get=f=>all.find(r=>r.family===f),bad=[
      [get("scheduling"),{order:[]}],[get("repair"),{order:get("repair").input.proposal}],[get("retention"),{keep:[100]}],[get("uniform"),{basis:[100]}],[get("factoring"),{helpers:[100]}],[get("continuation"),{classes:[]}]];
    for(const [r,a] of bad)assert(!grade(r,a).valid,"invalid accepted");
    const c=get("continuation"),a={classes:c.answer.classes.map(x=>100+7*x)};assert(grade(c,a).optimal,"relabel");
    const singleton={classes:indices(1<<c.input.dimension)};assert(grade(c,singleton).valid,"valid singleton");
    const result=gradeAll(all,all.map(r=>({id:r.id,answer:r.answer})));assert(result.optimal===all.length&&result.mean_score===1,"full grade");
    let rejected=0;for(const p of [[{id:"unknown",answer:{}}],[{id:all[0].id,answer:{}},{id:all[0].id,answer:{}}]])try{gradeAll(all,p)}catch{rejected++}
    assert(rejected===2&&gradeAll(all,[]).missing===all.length,"fail closed");
    return {schema:"proofcompactbench-v1-receipt",public_examples:all.length,train:384,calibration:96,dev_test:96,roots:96,unique_prompts:seen.size,reference_gold_passes:count,additional_stress_passes:structural,negative_controls:9,source:"Original finite synthetic instances; native proof costs separate",training_ready:false,admitted_tokens:0};
  }
  return {families,generate,packet,grade,gradeAll,selfTest};
}
