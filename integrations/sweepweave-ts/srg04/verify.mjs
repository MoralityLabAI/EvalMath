// Executable SRG-04 conformance and pinned TSUN migration/replay.
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import * as api from './swmd-runtime.mjs';
const pinnedBlob="9067b02e536c9407cd90c466fed0f4ea2c3edc2e";
const sourcePath="storyworlds/tsun01b_last_train_home/tsun01b.sweepweave.json";
function runSuite(api,gold){
  const {compileSWMD,initialState,playerObservation,counterfactuals,step,parseExpression,evaluate}=api;
  const checks={},check=(name,fn)=>{if(!fn())throw Error("FAIL "+name);checks[name]=true;};
  const rejects=fn=>{try{fn();return false;}catch(e){return /SWMD-SRG\/1:/.test(String(e));}};
  const close=(x,y)=>Math.abs(x-y)<1e-12;
  const fixture=`# SWMD-SRG/1
id: srg04
title: The Council Ledger
start: opening
tie: last
VAR council.Trust = 0.8 | public
VAR council.Support = 0 | public
VAR council.Trust[other] = -0.4 | hidden
VAR council.Trust[other][third] = 0.35 | hidden
ENC opening turn=0..0 | A:TRUE
OPT negotiate | V:TRUE | P:TRUE
ORX negotiate/r_first -> accepted | O:Negotiate a commitment. | E:SET council.Trust = NUDGE(P(council.Trust),C(-0.2)); SET council.Support = P(council.Trust); SET council.Trust[other][third] = C(-0.5) | D:ADD(P(council.Trust[other]),C(0.4)) | G:TRUE
ORX negotiate/r_last -> accepted | O:Negotiate a commitment. | E:SET council.Support = P(council.Trust); SET council.Trust = NUDGE(P(council.Trust),C(-0.2)); SET council.Trust = NUDGE(P(council.Trust),C(0.1)) | D:C(0) | G:TRUE
ORX negotiate/r_hidden -> accepted | O:Negotiate a commitment. | E:NONE | D:C(3) | G:LT(P(council.Trust[other][third]),C(0))
OPT refuse | V:GE(P(council.Trust),C(0.8)) | P:TRUE
ORX refuse/r_refuse -> refused | O:Refuse. | E:SET council.Support = C(-0.2) | D:C(1) | G:TRUE
OPT impossible | V:TRUE | P:LT(P(council.Trust),C(0))
ORX impossible/r_impossible -> refused | O:Impossible. | E:NONE | D:C(1) | G:TRUE
ENC accepted turn=1..1 | A:GE(P(council.Support),C(0.3))
ENC refused turn=1..1 | A:TRUE`;
  const w=compileSWMD(fixture),s=initialState(w),obs=playerObservation(w,s),cf=counterfactuals(w,s),a=cf.actions[0],b=a.branches[0],last=a.branches[1],end=step(w,s,"negotiate");
  check("legacy_projection_rejected",()=>rejects(()=>compileSWMD(fixture.replace("# SWMD-SRG/1","# SWMD-0-MIN"))));
  check("legal_menu_both_guards",()=>obs.actions.map(x=>x.id).join(",")==="negotiate,refuse");
  check("hidden_keyrings_not_in_player_observation",()=>Object.keys(obs.values).join(",")==="council.Trust,council.Support"&&!JSON.stringify(obs).includes("r_hidden"));
  check("full_keyring_isolation",()=>close(b.next.values["council.Trust[other]"],-.4)&&close(b.next.values["council.Trust[other][third]"],-.5)&&close(b.next.values["council.Trust"],.44));
  check("exact_equal_ties_last",()=>a.winners.join(",")==="r_first,r_last"&&a.selected==="r_last");
  check("explicit_first_tie",()=>counterfactuals(compileSWMD(fixture.replace("tie: last","tie: first")),s).actions[0].selected==="r_first");
  check("ineligible_high_score",()=>a.scores.find(r=>r.id==="r_hidden").score===3&&!a.scores.find(r=>r.id==="r_hidden").eligible&&a.branches.length===2);
  check("ordered_dependent_writes",()=>close(b.next.values["council.Support"],.44)&&close(last.next.values["council.Support"],.8));
  check("duplicate_writes_preserved",()=>last.writes.map(x=>x.key).join(",")==="council.Support,council.Trust,council.Trust"&&close(last.next.values["council.Trust"],.496));
  check("step_matches_selected_branch",()=>JSON.stringify(end.next)===JSON.stringify(last.next)&&end.reaction===a.selected);
  check("counterfactual_no_mutation",()=>s.values["council.Trust"]===.8&&s.values["council.Support"]===0&&s.turn===0);
  check("state_energy",()=>close(last.squared_step_energy,(.496-.8)**2+.8**2));
  check("blocked_destination",()=>counterfactuals(compileSWMD(fixture.replace("A:GE(P(council.Support),C(0.3))","A:GE(P(council.Support),C(0.9))")),s).actions[0].status==="blocked_destination");
  check("blocked_step_rejected",()=>rejects(()=>step(compileSWMD(fixture.replace("A:GE(P(council.Support),C(0.3))","A:GE(P(council.Support),C(0.9))")),s,"negotiate")));
  check("illegal_action_rejected",()=>rejects(()=>step(w,s,"impossible")));
  check("unknown_pointer_rejected",()=>rejects(()=>compileSWMD(fixture.replace("P(council.Trust[other])","P(council.Unknown)"))));
  check("unknown_operator_rejected",()=>rejects(()=>compileSWMD(fixture.replace("D:C(0)","D:UNKNOWN(C(0))"))));
  check("boolean_numeric_mismatch_rejected",()=>rejects(()=>compileSWMD(fixture.replace("D:C(0)","D:TRUE"))));
  check("unresolved_wild_rejected",()=>rejects(()=>compileSWMD(fixture.replace("-> accepted","-> wild"))));
  check("missing_destination_rejected",()=>rejects(()=>compileSWMD(fixture.replace("-> accepted","-> missing"))));
  check("out_of_range_initial_rejected",()=>rejects(()=>compileSWMD(fixture.replace("Trust = 0.8","Trust = 1.1"))));
  check("bounded_assignment_fail_closed",()=>rejects(()=>counterfactuals(compileSWMD(fixture.replace("SET council.Support = P(council.Trust)","SET council.Support = C(1.5)")),s)));
  check("comparator_direction",()=>evaluate(parseExpression("GE(C(0.65),C(0.65))",{}),{})&&!evaluate(parseExpression("GT(C(0.65),C(0.65))",{}),{})&&evaluate(parseExpression("LE(C(0.2),C(0.65))",{}),{})&&!evaluate(parseExpression("GE(C(0.2),C(0.65))",{}),{}));
  check("blend_signed_weight",()=>close(evaluate(parseExpression("BLEND(C(-0.8),C(0.6),C(0))",{}),{}),-.1));
  check("lazy_if",()=>evaluate(parseExpression("IF(TRUE,C(0.1),DIV(C(1),C(0)))",{}),{})===.1);
  check("terminal_observation",()=>playerObservation(w,end.next).status==="terminal"&&playerObservation(w,end.next).actions.length===0);
  // Restricted migration of the pinned TSUN native source. Preserve effect
  // order and explicit gold outcomes; do not use the legacy SWMD score labels.
  const ptr=x=>x.character+"."+x.keyring[0]+x.keyring.slice(1).map(k=>"["+k+"]").join("");
  function expr(x){
    if(typeof x==="boolean")return x?"TRUE":"FALSE";
    if(typeof x==="number")return "C("+x+")";
    if(x.pointer_type==="Boolean Constant")return x.value?"TRUE":"FALSE";
    if(x.pointer_type==="Bounded Number Constant")return "C("+x.value+")";
    if(x.pointer_type==="Bounded Number Pointer")return (x.coefficient===1||x.coefficient===undefined)?"P("+ptr(x)+")":"MUL(P("+ptr(x)+"),C("+x.coefficient+"))";
    const names={"Addition":"ADD","Multiplication":"MUL","Nudge":"NUDGE","And":"AND","Or":"OR","Absolute Value":"ABS"};
    const cmp={"Greater Than or Equal To":"GE","Greater Than":"GT","Less Than or Equal To":"LE","Less Than":"LT","Equal To":"EQ","Not Equal To":"NE"};
    const op=x.operator_type==="Arithmetic Comparator"?cmp[x.operator_subtype]:names[x.operator_type];
    if(!op)throw Error("unsupported source operator "+x.operator_type);
    return op+"("+x.operands.map(expr).join(",")+")";
  }
  const lines=["# SWMD-SRG/1","id: SW-TSUN-01B-20261029","title: TSUN-01B: The Last Train Home","start: page_notebook","tie: last"];
  for(const c of gold.characters)for(const [k,v] of Object.entries(c.bnumber_properties)){
    if(typeof v!=="number")throw Error("TSUN migration supports scalar initials only");
    lines.push("VAR "+c.id+"."+k+" = "+v+" | public");
  }
  for(const e of gold.encounters){
    lines.push("ENC "+e.id+" turn="+e.earliest_turn+".."+e.latest_turn+" | A:"+expr(e.acceptability_script));
    for(const o of e.options){
      lines.push("OPT "+o.id+" | V:"+expr(o.visibility_script)+" | P:"+expr(o.performability_script));
      for(const r of o.reactions){
        if(r.after_effects.some(e=>e.effect_type!=="Bounded Number Effect"||e.Set.coefficient!==1))throw Error("unsupported effect");
        const effects=r.after_effects.map(e=>"SET "+ptr(e.Set)+" = "+expr(e.to)).join("; ")||"NONE";
        if(o.text_script.value.includes("|")||/[\r\n]/.test(o.text_script.value))throw Error("unescaped text");
        lines.push("ORX "+o.id+"/"+r.id+" -> "+r.consequence_id+" | O:"+o.text_script.value+" | E:"+effects+" | D:"+expr(r.desirability_script)+" | G:TRUE");
      }
    }
  }
  const migrated=lines.join("\n")+"\n",tw=compileSWMD(migrated),root=initialState(tw);
  const terminals=Object.fromEntries(gold.encounters.filter(e=>!e.options.length).map(e=>[e.id,e.outcome]));
  const ts={nodes:0,leaves:0,actions:0,forced_eligible_branches:0,blocked:0,terminal_counts:{},uniform_legal_probability_numerator_over_81:{},protected_numerator:0,protected_without_privacy_numerator:0,max_energy_share:0};
  function walk(s,energies=[]){
    const o=playerObservation(tw,s);
    if(o.status==="terminal"){
      ts.leaves++;ts.terminal_counts[s.encounter]=(ts.terminal_counts[s.encounter]||0)+1;
      const weight=3**(4-s.turn);ts.uniform_legal_probability_numerator_over_81[s.encounter]=(ts.uniform_legal_probability_numerator_over_81[s.encounter]||0)+weight;
      const t=terminals[s.encounter];if(t.protected){ts.protected_numerator+=weight;if(!t.privacy_breach&&s.values["char_reina.Privacy_Breach"]===0)ts.protected_without_privacy_numerator+=weight;}
      ts.max_energy_share=Math.max(ts.max_energy_share,Math.max(...energies)/energies.reduce((a,b)=>a+b,0));return;
    }
    if(o.status!=="decision"||s.turn>=4)throw Error("unexpected TSUN path");
    ts.nodes++;
    const cf=counterfactuals(tw,s);for(const a of cf.actions){
      ts.actions++;ts.forced_eligible_branches+=a.branches.length;
      if(a.status!=="ok"){ts.blocked++;continue;}
      const branch=a.branches.find(b=>b.id===a.selected),other=a.branches.find(b=>b.id!==a.selected);
      if(JSON.stringify(branch.next)!==JSON.stringify(other.next))throw Error("tone equivalence lost");
      walk(branch.next,[...energies,branch.squared_step_energy]);
    }
  }
  walk(root);
  check("tsun_all_terminal_routes",()=>ts.leaves===45&&ts.nodes===22&&ts.actions===66&&ts.blocked===0);
  check("tsun_route_counts_match_srg02",()=>JSON.stringify(ts.terminal_counts)===JSON.stringify({"page_end_success_protected":2,"page_end_privacy_cost":2,"page_end_failure_silence":18,"page_end_failure_delay":9,"page_end_failure_unverified":7,"page_end_failure_privacy_unverified":7}));
  check("tsun_explicit_gold_utility",()=>ts.protected_numerator===4&&ts.protected_without_privacy_numerator===1);
  return {checks,fixture,migrated,ts,counts:{checks_passed:Object.keys(checks).length,fixture_actions:cf.actions.length,fixture_forced_branches:cf.actions.reduce((n,a)=>n+a.branches.length,0)}};
}
const checkout=process.argv[2];if(!checkout)throw Error("Usage: node verify.mjs <pinned GPTStoryworld checkout> [receipt.json]");
const buf=fs.readFileSync(path.join(checkout,sourcePath));
const actual=crypto.createHash('sha1').update('blob '+buf.length+'\0').update(buf).digest('hex');
if(actual!==pinnedBlob)throw Error("TSUN source hash mismatch");
const {fixture,migrated,...results}=runSuite(api,JSON.parse(buf.toString('utf8')));
const out={source_repo:'MoralityLabAI/GPTStoryworld',source_revision:'ee1c6918db77d1e0924877f59eca819bae3f1c8c',source_blob:pinnedBlob,runtime_blob:crypto.createHash('sha1').update('blob '+fs.statSync(new URL('./swmd-runtime.mjs',import.meta.url)).size+'\0').update(fs.readFileSync(new URL('./swmd-runtime.mjs',import.meta.url))).digest('hex'),...results};
const receipt=JSON.stringify(out,null,2)+'\n';
if(process.argv[3])fs.writeFileSync(process.argv[3],receipt);else process.stdout.write(receipt);
