// SRG-02: audited, pinned source files only. The engine is deliberately evaluated from a verified Git blob, never from arbitrary user-supplied JS.
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
const inputs=["storyworlds/tsun01b_last_train_home/tsun01b.sweepweave.json","storyworlds/tsun01b_last_train_home/tsun01b_env.py","storyworlds/balance_of_reason/source_cards.json","storyworlds/balance_of_reason/engine.mjs"];
const blobs={"storyworlds/tsun01b_last_train_home/tsun01b.sweepweave.json":"9067b02e536c9407cd90c466fed0f4ea2c3edc2e","storyworlds/tsun01b_last_train_home/tsun01b_env.py":"72f43fccf9dd617e42a5fe01d0b378b0d6178d5a","storyworlds/balance_of_reason/source_cards.json":"2503e811ebdd6e0f8e5c1a61dc178c2448acc666","storyworlds/balance_of_reason/engine.mjs":"34f56047948f699a07b18edc07aebf19b4e530ca"};
const revision="ee1c6918db77d1e0924877f59eca819bae3f1c8c";
function audit(world, source, engine) {
  const clamp=x=>Math.max(-1,Math.min(1,x));
  const signed=(x,a)=>clamp(x*(1-Math.abs(a))+a);
  const round=x=>Number(x.toFixed(8));
  const count=(obj,key)=>obj[key]=(obj[key]||0)+1;
  const byId=Object.fromEntries(world.encounters.map(e=>[e.id,e]));
  const ts={pages:world.encounters.length,options:0,reactions:0,
    mechanical_equivalence_menus:0,common_mode_coordinates:{},relative_coordinates:{},
    reachable_prefixes:0,leaves:0,terminal_path_counts:{},terminal_probability_numerator_over_81:{},
    protected_numerator_over_81:0,protected_private_numerator_over_81:0,
    gate_failures_signed:0,gate_failures_additive:0,
    winner_sets_on_reachable_prefixes:{},effect_scripts:0,zero_nudges:0};
  const linear=ast=>{
    const coeff={};let bias=0;
    if(ast.operator_type!=="Addition")throw Error("Unsupported TSUN score");
    for(const node of ast.operands){
      if(node.pointer_type==="Bounded Number Constant")bias+=node.value;
      else if(node.pointer_type==="Bounded Number Pointer"&&node.character==="char_reina"&&node.keyring.length===1)
        coeff[node.keyring[0]]=(coeff[node.keyring[0]]||0)+node.coefficient;
      else throw Error("Unsupported TSUN score operand");
    }
    return {coeff,bias};
  };
  const evalLinear=(f,state)=>f.bias+Object.entries(f.coeff).reduce((s,[k,a])=>s+state[k]*a,0);
  for(const page of world.encounters)for(const opt of page.options){
    ts.options++;ts.reactions+=opt.reactions.length;
    if(opt.reactions.length!==2)throw Error("Expected paired tone reactions");
    const [a,b]=opt.reactions;
    if(a.consequence_id===b.consequence_id&&JSON.stringify(a.after_effects)===JSON.stringify(b.after_effects))ts.mechanical_equivalence_menus++;
    else throw Error("TSUN tone equivalence broken");
    const [f,g]=[a,b].map(r=>linear(r.desirability_script));
    for(const k of new Set([...Object.keys(f.coeff),...Object.keys(g.coeff)])){
      const p=f.coeff[k]||0,q=g.coeff[k]||0;
      count(p===q?ts.common_mode_coordinates:ts.relative_coordinates,k);
    }
    for(const r of opt.reactions)for(const effect of r.after_effects){
      ts.effect_scripts++;
      if(effect.to.operator_type==="Nudge"&&effect.to.operands[1].value===0)ts.zero_nudges++;
    }
  }
  function walk(id,traits,flags,path,addClock) {
    const page=byId[id];
    if(!page)throw Error("Missing destination");
    if(!page.options.length){
      ts.leaves++;count(ts.terminal_path_counts,id);
      const weight=3**(4-path.length);
      ts.terminal_probability_numerator_over_81[id]=(ts.terminal_probability_numerator_over_81[id]||0)+weight;
      if(page.outcome.protected){
        ts.protected_numerator_over_81+=weight;
        if(!flags.privacy_breach&&!page.outcome.privacy_breach){
          ts.protected_private_numerator_over_81+=weight;
          ts.example_private_protected_path=path;
        }
      }
      const gate=page.acceptability_script;
      if(gate.operator_type!=="Arithmetic Comparator"||gate.operator_subtype!=="Greater Than or Equal To"||
          gate.operands[0].keyring[0]!=="Phase_Clock")throw Error("Unexpected terminal gate");
      const threshold=gate.operands[1].value;
      if(traits.Phase_Clock<threshold)ts.gate_failures_signed++;
      if(addClock<threshold)ts.gate_failures_additive++;
      return;
    }
    ts.reachable_prefixes++;
    if(page.options.length!==3)throw Error("Expected three choices");
    for(const opt of page.options){
      const scores=opt.reactions.map(r=>evalLinear(linear(r.desirability_script),traits));
      const max=Math.max(...scores);
      const winners=scores.map((s,i)=>Math.abs(s-max)<1e-10?i:null).filter(i=>i!==null).join(",");
      if(!ts.winner_sets_on_reachable_prefixes[opt.id])ts.winner_sets_on_reachable_prefixes[opt.id]={};
      count(ts.winner_sets_on_reachable_prefixes[opt.id],winners);
      const next={...traits};
      for(const [k,a] of Object.entries(opt.trait_deltas))next[k]=Number(signed(next[k],a).toFixed(4));
      walk(opt.reactions[0].consequence_id,next,{...flags,...opt.state_updates},[...path,opt.action_id],clamp(addClock+opt.trait_deltas.Phase_Clock));
    }
  }
  walk("page_notebook",{...world.characters[0].bnumber_properties},{},[],0);
  const winnerRecords=Object.values(ts.winner_sets_on_reachable_prefixes);
  ts.menus_with_multiple_observed_winner_sets=winnerRecords.filter(x=>Object.keys(x).length>1).length;
  ts.reachable_menu_evaluations=winnerRecords.reduce((n,o)=>n+Object.values(o).reduce((a,b)=>a+b,0),0);
  delete ts.winner_sets_on_reachable_prefixes;
  if(Object.values(ts.terminal_probability_numerator_over_81).reduce((a,b)=>a+b,0)!==81)throw Error("Probability conservation");
  function load(code){
    const body=code.replace(/^export\s+/gm,"");
    return new Function(body+"\nreturn {initial,current,choose,scoreEndings};")();
  }
  let replacements=0;
  let mutant=engine.replace(/clamp\(state\.stats(\[key\]|\.[A-Z])([+-])([^\n;]+)\);/g,(_,access,sign,expr)=>{
    replacements++;return `signed(state.stats${access},${sign}(${expr}));`;
  }).replace(/clamp\(\(state\.factions\[shift\.id\]\?\?0\)\+shift\.amount\)/g,()=>{
    replacements++;return "signed((state.factions[shift.id]??0),shift.amount)";
  });
  if(replacements!==16)throw Error("Unexpected update replacement count: "+replacements);
  mutant="function signed(x,a){return Math.max(-1,Math.min(1,x*(1-Math.abs(a))+a));}\n"+mutant;
  const orig=load(engine),alt=load(mutant);
  const cp=s=>({...s,stats:{...s.stats},factions:{...s.factions},history:[]});
  const coordinates=s=>[...Object.values(s.stats),...Object.values(s.factions)];
  const delta=(a,b)=>{const x=coordinates(a),y=coordinates(b);return x.map((v,i)=>y[i]-v)};
  const key=s=>[s.yearIndex,s.sceneIndex,s.phase,s.result].join("|");
  const bor={policy_sequences:128,paired_final_ending_disagreements:0,paired_final_turn_disagreements:0,
    original_endings:{},signed_mutant_endings:{},paired_same_state_action_checks:0,successor_route_disagreements:0,
    any_coordinate_differences:0,max_abs_coordinate_difference:0,
    original_total_squared_step_energy:0,signed_mutant_total_squared_step_energy:0,
    first_route_disagreement:null,update_sites_replaced:replacements,always_same_index:[]};
  function run(api,actions) {
    let s=api.initial(source);
    for(let i=0;i<actions.length&&s.phase!=="end";i++)api.choose(source,s,actions[i]%api.current(source,s).choices.length);
    if(s.phase!=="end")throw Error("Policy sequence too short");
    return s;
  }
  for(let i=0;i<3;i++){
    const seq=Array(95).fill(i),a=run(orig,seq),b=run(alt,seq);
    bor.always_same_index.push({index:i,original:a.result,mutant:b.result,original_turns:a.turns,mutant_turns:b.turns});
  }
  let rng=0x53524702;
  const random=()=>{rng=(Math.imul(rng,1664525)+1013904223)>>>0;return rng%3};
  for(let trial=0;trial<bor.policy_sequences;trial++){
    const seq=Array.from({length:95},random);
    let state=orig.initial(source);
    for(let t=0;t<seq.length&&state.phase!=="end";t++){
      const n=orig.current(source,state).choices.length;
      for(let a=0;a<n;a++){
        const s=orig.choose(source,cp(state),a),v=alt.choose(source,cp(state),a);
        bor.paired_same_state_action_checks++;
        if(key(s)!==key(v)){
          bor.successor_route_disagreements++;
          if(!bor.first_route_disagreement)bor.first_route_disagreement={trial,turn:t+1,phase:state.phase,action:a,original:key(s),mutant:key(v)};
        }
        const diff=Math.max(...delta(s,v).map(Math.abs));
        if(diff>1e-12)bor.any_coordinate_differences++;
        bor.max_abs_coordinate_difference=Math.max(bor.max_abs_coordinate_difference,diff);
        bor.original_total_squared_step_energy+=delta(state,s).reduce((a,d)=>a+d*d,0);
        bor.signed_mutant_total_squared_step_energy+=delta(state,v).reduce((a,d)=>a+d*d,0);
      }
      orig.choose(source,state,seq[t]%n);
    }
    const v=run(alt,seq);
    if(state.phase!=="end")throw Error("Incomplete original");
    count(bor.original_endings,state.result);count(bor.signed_mutant_endings,v.result);
    bor.paired_final_ending_disagreements+=Number(state.result!==v.result);
    bor.paired_final_turn_disagreements+=Number(state.turns!==v.turns);
  }
  for(const k of ["max_abs_coordinate_difference","original_total_squared_step_energy","signed_mutant_total_squared_step_energy"])bor[k]=round(bor[k]);
  return {evidence:"source-pinned authored-world audit; binary64 replay, exhaustive TSUN route tree, sampled paired Balance of Reason policies",tsun01b:ts,balance_of_reason:bor};
}
const root=process.argv[2];
if(!root)throw Error("Usage: node scripts/verify_storyworld_srg02.mjs <GPTStoryworld checkout at pinned revision> [output]");
const files=inputs.map(p=>{const b=fs.readFileSync(path.join(root,p));const sha=crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');if(sha!==blobs[p])throw Error('source blob mismatch '+p);return b.toString('utf8');});
const result={source_repository:'MoralityLabAI/GPTStoryworld',source_revision:revision,source_git_blobs:blobs,...audit(JSON.parse(files[0]),JSON.parse(files[2]),files[3])};
const receipt=JSON.stringify(result,null,2)+'\n';
if(process.argv[3])fs.writeFileSync(process.argv[3],receipt);else process.stdout.write(receipt);
