// SRG-03: SWMD authoring audit and exact integer sequential oracle.
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
const inputs=["storyworlds/tsun01b_last_train_home/tsun01b.swmd.min.md","storyworlds/tsun01b_last_train_home/tsun01b.sweepweave.json","storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_bonsai27.swmd.min.md","codex-skills/storyworld-building/scripts/json_to_swmd.py","codex-skills/storyworld-building/scripts/swmd_patch_json.py"];
const blobs={"storyworlds/tsun01b_last_train_home/tsun01b.swmd.min.md":"80cabc0245d194c92372f139965a42f0ef12921c","storyworlds/tsun01b_last_train_home/tsun01b.sweepweave.json":"9067b02e536c9407cd90c466fed0f4ea2c3edc2e","storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_bonsai27.swmd.min.md":"1c36aeda9bed766c8f993119d43bc8affdb77d66","codex-skills/storyworld-building/scripts/json_to_swmd.py":"04c601b3ea4fd2611e7bff9299a622de54e453bd","codex-skills/storyworld-building/scripts/swmd_patch_json.py":"6afc7ca7f7e0a9ffdce588acdb7a5894dbfa12cf"};
const ref="ee1c6918db77d1e0924877f59eca819bae3f1c8c";
function auditSWMD(doc,gold=null){
  const body=doc.split(/^# SWMD-0-MIN\s*$/m);
  if(body.length!==2)throw Error("expected minified body");
  const front=body[0],pages=new Map(),flat=new Map();
  const ptr=/P\(([A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_.-]+\])*)\)/g;
  const reads=s=>new Set(Array.from(s.matchAll(ptr),m=>m[1]));
  const depth=k=>Math.min(3,(k.match(/\[/g)||[]).length);
  const effects=s=>s.split(/\s*;\s*/).map(t=>{
    const m=t.match(/^SET\s+(\S+)\s+(\+=|=)\s+(.+)$/);
    if(!m)throw Error("invalid effect "+t);
    return {key:m[1],op:m[2],expr:m[3],reads:reads(m[3])};
  }).filter(e=>e.key!=="none");
  let cur=null;
  for(const raw of body[1].split(/\r?\n/)){
    const s=raw.trim();
    if(!s||s.startsWith("id:")||s.startsWith("title:"))continue;
    if(s.startsWith("ENC ")){
      const m=s.match(/^ENC (\S+) turn=(\S+)\.\.(\S+)$/);
      if(!m||pages.has(m[1]))throw Error("invalid encounter "+s);
      cur=new Map();pages.set(m[1],cur);continue;
    }
    const m=s.match(/^ORX (\S+)\/(\S+) -> (\S+) \| O:(.*?) \| E:(.*?) \| D:(.*)$/);
    if(!cur||!m||flat.has(m[2]))throw Error("invalid ORX "+s.slice(0,150));
    if(!cur.has(m[1]))cur.set(m[1],[]);
    const r={id:m[2],dest:m[3],effects:effects(m[5]),formula:m[6],refs:reads(m[6])};
    cur.get(m[1]).push(r);flat.set(r.id,r);
  }
  const z={encounters:pages.size,options:0,reactions:0,terminal_encounters:0,unique_formula_keys_by_belief_depth:[0,0,0,0],unique_effect_targets_by_belief_depth:[0,0,0,0],formula_reference_occurrences_by_belief_depth:[0,0,0,0],effect_dependency_reactions:0,effect_dependency_pairs:0,duplicate_write_reactions:0,structurally_identical_mechanics_menus:0,unknown_destinations:[],frontmatter_ambiguous_comparators:0,frontmatter_ending_labels:{}};
  const refs=new Set(),writes=new Set(),mechanics=r=>JSON.stringify([r.dest,r.effects.map(e=>[e.key,e.op,e.expr])]);
  for(const opts of pages.values()){
    if(!opts.size)z.terminal_encounters++;
    for(const rs of opts.values()){
      z.options++;if(rs.length>1&&rs.every(r=>mechanics(r)===mechanics(rs[0])))z.structurally_identical_mechanics_menus++;
      for(const r of rs){
        z.reactions++;
        if(!pages.has(r.dest)&&!z.unknown_destinations.includes(r.dest))z.unknown_destinations.push(r.dest);
        for(const k of r.refs)refs.add(k);
        for(const m of r.formula.matchAll(ptr))z.formula_reference_occurrences_by_belief_depth[depth(m[1])]++;
        let deps=0;const w=new Set();
        for(let i=0;i<r.effects.length;i++){
          const e=r.effects[i];writes.add(e.key);w.add(e.key);
          for(let j=0;j<r.effects.length;j++)if(i!==j&&r.effects[j].reads.has(e.key))deps++;
        }
        if(w.size<r.effects.length)z.duplicate_write_reactions++;
        if(deps){z.effect_dependency_reactions++;z.effect_dependency_pairs+=deps;}
      }
    }
  }
  for(const k of refs)z.unique_formula_keys_by_belief_depth[depth(k)]++;
  for(const k of writes)z.unique_effect_targets_by_belief_depth[depth(k)]++;
  z.frontmatter_ambiguous_comparators=(front.match(/ARITHMETIC COMPARATOR\(/g)||[]).length;
  for(const m of front.matchAll(/^\s+- id: "([^"]+)"\s*\n\s+type: "([^"]+)"/gm))z.frontmatter_ending_labels[m[1]]=m[2];
  if(gold){
    const key=p=>p.character+"."+p.keyring[0]+p.keyring.slice(1).map(k=>"["+k+"]").join("");
    const astReads=(a,out=new Set())=>{if(a&&typeof a==="object"){if(a.pointer_type==="Bounded Number Pointer")out.add(key(a));for(const o of a.operands||[])astReads(o,out);}return out;};
    z.gold={reaction_order_changes:0,effect_order_changed_reactions:0,changed_order_dependency_pairs:0,route_mismatches:0,ending_label_protection_conflicts:[],initial_numeric_coordinates:0,nontrivial_visibility_or_performability_options:0};
    for(const c of gold.characters)for(const v of Object.values(c.bnumber_properties))if(typeof v==="number")z.gold.initial_numeric_coordinates++;
    const trivial=a=>a===true||(a&&a.pointer_type==="Boolean Constant"&&a.value===true);
    for(const p of gold.encounters){
      if(p.outcome&&!p.outcome.protected&&z.frontmatter_ending_labels[p.id]==="success")z.gold.ending_label_protection_conflicts.push(p.id);
      for(const o of p.options){
        if(!trivial(o.visibility_script)||!trivial(o.performability_script))z.gold.nontrivial_visibility_or_performability_options++;
        const rows=pages.get(p.id)?.get(o.id);if(!rows||rows.length!==o.reactions.length)throw Error("gold menu mismatch");
        if(rows.some((r,i)=>r.id!==o.reactions[i].id))z.gold.reaction_order_changes++;
        for(const r of o.reactions){
          const row=flat.get(r.id);if(!row)throw Error("missing reaction");
          if(row.dest!==r.consequence_id)z.gold.route_mismatches++;
          const before=r.after_effects.map(e=>key(e.Set)),after=row.effects.map(e=>e.key);
          if(before.join("|")!==after.join("|"))z.gold.effect_order_changed_reactions++;
          if(new Set(before).size!==before.length)throw Error("duplicate writes in gold fixture");
          for(let i=0;i<before.length;i++)for(let j=i+1;j<before.length;j++)
            if(after.indexOf(before[i])>after.indexOf(before[j])&&(astReads(r.after_effects[j].to).has(before[i])||astReads(r.after_effects[i].to).has(before[j])))z.gold.changed_order_dependency_pairs++;
        }
      }
    }
  }
  return z;
}
function sequential(){
  // Unit mass initial worlds, deterministic transition and observation.
  // Keep all multiplicities. Rewards are exact integers; no probability rounding.
  function oracle(worlds,obs,actions,step,h){
    let nodes=0;
    function split(ss){const m=new Map();for(const s of ss){const k=obs(s);if(!m.has(k))m.set(k,[]);m.get(k).push(s);}return [...m.values()];}
    function rec(ss,t){
      nodes++;
      if(t===0||ss.every(s=>s.done))return ss.reduce((n,s)=>n+(s.done?s.reward:0),0);
      if(ss.some(s=>s.done))throw Error("terminal observation must be distinct");
      const menu=actions(ss[0]);if(ss.some(s=>JSON.stringify(actions(s))!==JSON.stringify(menu)))throw Error("hidden-dependent menu");
      return Math.max(...menu.map(a=>split(ss.map(s=>step(s,a))).reduce((n,c)=>n+rec(c,t-1),0)));
    }
    return {numerator:split(worlds).reduce((n,c)=>n+rec(c,h),0),denominator:worlds.length,nodes};
  }
  function fixture(k,hidden=false,padding=0){
    const worlds=Array.from({length:2**(k+padding)},(_,i)=>({bits:Array.from({length:k+padding},(_,j)=>(i>>j)&1),t:0,last:-1,done:false}));
    const obs=s=>s.done?"terminal":`${s.t}:${s.last}`;
    const acts=s=>s.t<k?["read"]:["even","odd"];
    const step=(s,a)=>s.t<k?{...s,t:s.t+1,last:hidden&&s.t===k-1?-1:s.bits[s.t]}:
      {...s,done:true,reward:Number((a==="odd"?1:0)===s.bits.slice(0,k).reduce((v,b)=>v^b,0))};
    return {worlds,obs,acts,step};
  }
  const run=(f,h)=>oracle(f.worlds,f.obs,f.acts,f.step,h);
  const results={parity:[],hidden:[],precision:[],rounding_counterexample:[],planning:{},repair:{}};
  for(const k of [1,2,4,8]){
    const f=fixture(k),bad=fixture(k,true),v=run(f,k+1),b=run(bad,k+1);
    let memoryless=0;
    for(const mask of [0,1,2,3]){
      let n=0;for(let s of f.worlds){for(let t=0;t<k;t++)s=f.step(s,"read");n+=f.step(s,((mask>>s.last)&1)?"odd":"even").reward;}memoryless=Math.max(memoryless,n);
    }
    let compressed=0;
    for(let s of f.worlds){let m=0;for(let t=0;t<k;t++){s=f.step(s,"read");m^=s.last;}compressed+=f.step(s,m?"odd":"even").reward;}
    if(v.numerator!==f.worlds.length||b.numerator*2!==bad.worlds.length||compressed!==v.numerator||memoryless!==(k===1?v.numerator:v.numerator/2))throw Error("parity mismatch");
    results.parity.push({k,full_history:v,memoryless_numerator:memoryless,one_bit_memory_numerator:compressed});
    results.hidden.push({k,oracle:b,repair:v});
  }
  const padded=run(fixture(4,false,4),5);
  if(padded.numerator!==padded.denominator)throw Error("padding mismatch");
  results.padded_k4_ambient8=padded;
  function precision(x,y,threshold,digits){
    const scale=10**(3-digits),worlds=[{x,done:false},{x:y,done:false}];
    return {digits,...oracle(worlds,s=>s.done?"terminal":Math.floor((2*s.x+scale)/(2*scale)),()=>["below","above"],(s,a)=>({...s,done:true,reward:Number((s.x>=threshold)===(a==="above"))}),1)};
  }
  for(const d of [0,1,2,3]){
    const v=precision(646,648,647,d),w=precision(649,651,650,d);
    if(v.numerator!==(d===3?2:1)||w.numerator!==([1,2,1,2][d]))throw Error("precision mismatch");
    results.precision.push(v);results.rounding_counterexample.push(w);
  }
  const worlds=[{t:0,done:false}],obs=s=>s.done?"terminal":s.t;
  const actions=s=>s.t===0?["take","prepare"]:["finish"];
  const step=(s,a)=>a==="take"?{...s,done:true,reward:1}:a==="prepare"?{t:1,done:false}:{...s,done:true,reward:2};
  results.planning={h1:oracle(worlds,obs,actions,step,1),h2:oracle(worlds,obs,actions,step,2)};
  function gate(amount,late,wrong){
    let x=0;const path=[];for(let t=0;t<4;t++){const a=t===3?late:amount;x+=a;path.push(a*a);}
    return {final:x,eligible:wrong?x<=80:x>=80,max_energy_share:[Math.max(...path),path.reduce((a,b)=>a+b,0)]};
  }
  results.repair={clean:gate(25,25,false),weak:gate(10,10,false),windfall:gate(0,100,false),wrong_sign:gate(25,25,true),repaired:gate(25,25,false)};
  if(!results.repair.clean.eligible||results.repair.weak.eligible||results.repair.wrong_sign.eligible||!results.repair.windfall.eligible||results.planning.h1.numerator!==1||results.planning.h2.numerator!==2)throw Error("repair mismatch");
  return results;
}
function runAll(contents){return {evidence:"source-pinned SWMD static audit; exact integer finite synthetic sequential oracle",tsun:auditSWMD(contents[0],JSON.parse(contents[1])),reservoir_dogs:auditSWMD(contents[2]),sequential:sequential()};}
const root=process.argv[2];
if(!root)throw Error("Usage: node scripts/verify_storyworld_srg03.mjs <pinned GPTStoryworld checkout> [output]");
const contents=inputs.map(p=>{const b=fs.readFileSync(path.join(root,p));const sha=crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');if(sha!==blobs[p])throw Error('source blob mismatch '+p);return b.toString('utf8');});
const receipt=JSON.stringify({source_repository:'MoralityLabAI/GPTStoryworld',source_revision:ref,source_git_blobs:blobs,...runAll(contents)},null,2)+'\n';
if(process.argv[3])fs.writeFileSync(process.argv[3],receipt);else process.stdout.write(receipt);
