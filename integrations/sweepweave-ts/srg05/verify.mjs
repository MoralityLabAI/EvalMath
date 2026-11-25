import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import * as api from './swmd-runtime-v2.mjs';
import {migrateReservoir} from './migrate-reservoir.mjs';
function run(api,migrate,d,readerText){
 const {compileV2,initialV2,observeV2,auditV2,stepV2,applyLinePatch}=api;
 const checks={},check=(n,p)=>{if(!p)throw Error("FAIL "+n);checks[n]=true;},rejects=f=>{try{f();return false;}catch{return true;}};
 const fixture=`# SWMD-SRG/2
id: council
title: "Council | public account"
about: "A compact test."
start: opening
turn-base: 0
tie: first
direct: strict
VAR a.trust = 0 | public
VAR a.trust[b] = 0.3 | hidden
SPOOL act1 | A:TRUE | E:opening
SPOOL act2 | A:FALSE | E:preferred,alternate,closed
ENC opening turn=0..0 | I:0 | A:TRUE | Q:C(0) | N:"Opening" | T:"The council meets."
OPT verify | V:TRUE | P:NOT(SEEN(verify)) | T:"Verify the record."
ORX verify/r1 -> wild | E:SET a.trust = C(0.5); SPOOL act2 = TRUE; SPOOL act1 = FALSE | D:C(1) | G:TRUE | T:"The second chamber opens."
OPT ignore | V:TRUE | P:TRUE | T:"Ignore the record."
ORX ignore/r2 -> wild | E:NONE | D:C(1) | G:TRUE | T:"Nothing changes."
ENC preferred turn=1..1 | I:1 | A:AND(ACTIVE(act2),SEEN(r1),GE(P(a.trust),C(0.5))) | Q:C(0.8) | N:"Preferred" | T:"Verified."
ENC alternate turn=1..1 | I:2 | A:TRUE | Q:C(0.8) | N:"Alternate" | T:"An alternative."
ENC closed turn=2..2 | I:3 | A:TRUE | Q:C(1) | N:"Closed" | T:"Too early."
`;
 const w=compileV2(fixture),s=initialV2(w),a=auditV2(w,s),b=stepV2(w,s,"verify");
 check("wild_filters_and_ties",b.next.encounter==="preferred"&&b.routing.candidates.map(c=>c.id).join(",")==="preferred,alternate");
 check("spool_activation_and_order",b.next.spools.act2&&!b.next.spools.act1&&b.writes.map(x=>x.kind).join(",")==="number,spool,spool");
 check("event_prerequisites",b.next.seen.join(",")==="opening,verify,r1,preferred");
 check("no_wild_destination_flagged",a.actions[1].status==="no_wild_destination"&&rejects(()=>stepV2(w,s,"ignore")));
 check("no_state_mutation",s.values["a.trust"]===0&&s.spools.act1&&!s.spools.act2&&s.seen.length===1);
 check("public_observation_omits_hidden_and_history",!JSON.stringify(observeV2(w,s)).includes("trust[b]")&&!Object.hasOwn(observeV2(w,s),"seen"));
 check("narrative_roundtrip",w.title==="Council | public account"&&b.text==="The second chamber opens."&&observeV2(w,b.next).text==="Verified.");
 check("step_audit_equivalence",JSON.stringify(b)===JSON.stringify(a.actions[0].branches[0]));
 check("unknown_event_rejected",rejects(()=>compileV2(fixture.replace("SEEN(r1)","SEEN(r999)"))));
 check("unknown_spool_rejected",rejects(()=>compileV2(fixture.replace("ACTIVE(act2)","ACTIVE(unknown)"))));
 check("strict_direct_checks_guard",auditV2(compileV2(fixture.replace("verify/r1 -> wild","verify/r1 -> closed")),s).actions[0].status==="blocked_destination");
 const explicit=compileV2(fixture.replace("direct: strict","direct: explicit").replace("verify/r1 -> wild","verify/r1 -> closed"));
 check("explicit_direct_bypass_logged",!stepV2(explicit,s,"verify").guard_admitted&&stepV2(explicit,s,"verify").next.encounter==="closed");
 const rows=fixture.split("\n"),i=rows.findIndex(x=>x.includes("verify/r1")),patch={line:i+1,before:rows[i],after:rows[i].replace("C(0.5)","C(0.6)")};
 check("patch_stale_guard",applyLinePatch(fixture,patch).includes("C(0.6)")&&rejects(()=>applyLinePatch(applyLinePatch(fixture,patch),patch)));
 const migrated=migrate(d),world=compileV2(migrated.source),strict=compileV2(migrated.source.replace("direct: explicit","direct: strict"));
 check("source_counts",migrated.counts.encounters===20&&migrated.counts.options===46&&migrated.counts.reactions===138&&migrated.counts.writes===690);
 const originalRx=d.encounters.flatMap(e=>e.options.flatMap(o=>o.reactions));
 const rById=new Map(originalRx.map(r=>[r.id,r]));
 check("all_reaction_text_preserved",Object.values(world.pages).every(p=>Object.values(p.options).every(o=>o.reactions.every(r=>r.text===rById.get(r.id).text_script.value))));
 check("all_effect_orders_preserved",Object.values(world.pages).every(p=>Object.values(p.options).every(o=>o.reactions.every(r=>r.effects.every((e,j)=>{const q=rById.get(r.id).after_effects[j].Set;return e.key===q.character+"."+q.keyring[0]+q.keyring.slice(1).map(k=>"["+k+"]").join("");})))));
 check("all_encounter_text_preserved",d.encounters.every(p=>world.pages[p.id].text===p.text_script.value));
 const begin=readerText.indexOf("class StoryworldEngine"),end=readerText.indexOf("// ========== UI CONTROLLER",begin);
 if(begin<0||end<0)throw Error("pinned reader class not found");
 const Reader=new Function(readerText.slice(begin,end)+"\nreturn StoryworldEngine;")();
 const count=(o,k)=>o[k]=(o[k]||0)+1;
 const keyring=k=>{const [owner,rest]=k.split(".");return [owner,[rest.split("[")[0],...Array.from(rest.matchAll(/\[([^\]]+)\]/g),m=>m[1])]];};
 const coords=Object.keys(world.coordinates), keys=coords.map(keyring);
 const freshReader=()=>new Reader().load(d);
 function readerAt(s){
   const e=freshReader();e.state.turn=s.turn;e.state.currentEncounterId=s.encounter;
   e.state.activeSpools=new Set(Object.entries(s.spools).filter(([,a])=>a).map(([k])=>k));e.state.visitedEncounters=new Set(s.visited);
   for(let j=0;j<coords.length;j++)e.setBNumber(keys[j][0],keys[j][1],s.values[coords[j]]);
   return e;
 }
 function readerAction(e,id){const r=e.selectReaction(e.getCurrentEncounter().options.find(o=>o.id===id));if(!r)throw Error("missing reader reaction");e.selectOption(id);const before=e.state.turn;e.continueToNext();return {id:r.id,to:e.state.turn===before?null:e.state.currentEncounterId,values:coords.map((_,j)=>e.getBNumber(keys[j][0],keys[j][1]))};}
 const n=64, auditN=16;let rng=0x53524705;
 const random=()=>{rng=(Math.imul(rng,1664525)+1013904223)>>>0;return rng;};
 const metrics={sampled_policy_sequences:n,same_state_audit_sequences:auditN,signed_endings:{},reader_endings:{},strict_endings:{},signed_terminations:0,reader_terminations:0,strict_terminations:0,paired_ending_disagreements:0,matched_state_actions:0,matched_reaction_disagreements:0,matched_route_disagreements:0,matched_numeric_disagreements:0,menu_disagreements:0,explicit_guard_bypasses:0,forced_eligible_branches:0,blocked_forced_branches:0,wild_selected_steps:0,wild_candidate_total:0,max_coordinate_difference:0,first_difference:null};
 function rollout(mode,seq,trial){
   let s=initialV2(mode==="strict"?strict:world),e=mode==="reader"?freshReader():null;
   for(let t=0;t<seq.length;t++){
     if(e){
       const p=e.getCurrentEncounter();if(!p||!p.options.length)return p?.id??"dead_end";
       const opts=e.getVisibleOptions(p);if(!opts.length)return "dead_end";const action=opts[seq[t]%opts.length].id;
       if(!readerAction(e,action).to)return "no_wild_destination";continue;
     }
     const active=mode==="strict"?strict:world,obs=observeV2(active,s);if(obs.status!=="decision")return obs.status==="terminal"?s.encounter:obs.status;
     if(mode==="signed"&&trial<auditN){
       const packet=auditV2(world,s),ro=readerAt(s).getVisibleOptions(readerAt(s).getCurrentEncounter()).map(o=>o.id);
       metrics.menu_disagreements+=Number(ro.join(",")!==obs.actions.map(o=>o.id).join(","));
       for(const a of packet.actions){
         metrics.forced_eligible_branches+=a.branches.length;
         metrics.blocked_forced_branches+=a.branches.filter(x=>x.status!=="ok").length;
         const b=a.branches.find(b=>b.id===a.selected);if(!b)continue;
         const old=readerAction(readerAt(s),a.id);metrics.matched_state_actions++;
         metrics.matched_reaction_disagreements+=Number(a.selected!==old.id);
         metrics.matched_route_disagreements+=Number((b.next?.encounter??null)!==old.to);
         if(b.next){
           const delta=Math.max(...coords.map((k,j)=>Math.abs(b.next.values[k]-old.values[j])));
           metrics.matched_numeric_disagreements+=Number(delta>1e-12);metrics.max_coordinate_difference=Math.max(metrics.max_coordinate_difference,delta);
           if(!metrics.first_difference&&delta>1e-12)metrics.first_difference={trial,turn:s.turn,encounter:s.encounter,action:a.id,reaction:a.selected,reader_reaction:old.id,max_delta:delta};
         }
       }
     }
     try{
       const b=stepV2(active,s,obs.actions[seq[t]%obs.actions.length].id);
       if(mode==="signed"){metrics.explicit_guard_bypasses+=Number(!b.guard_admitted);if(b.routing.candidates.length){metrics.wild_selected_steps++;metrics.wild_candidate_total+=b.routing.candidates.length;}}
       s=b.next;
     }catch(err){
       if(/SWMD-SRG\/2: (blocked_destination|no_wild_destination|no eligible reaction)/.test(String(err)))return String(err).split(": ").at(-1);
       throw err;
     }
   }
   return "timeout";
 }
 const terminalIds=new Set(d.encounters.filter(p=>!p.options.length).map(p=>p.id));
 for(let trial=0;trial<n;trial++){
   const seq=Array.from({length:24},random),a=rollout("signed",seq,trial),b=rollout("reader",seq,trial),c=rollout("strict",seq,trial);
   count(metrics.signed_endings,a);count(metrics.reader_endings,b);count(metrics.strict_endings,c);
   metrics.signed_terminations+=Number(terminalIds.has(a));metrics.reader_terminations+=Number(terminalIds.has(b));metrics.strict_terminations+=Number(terminalIds.has(c));
   metrics.paired_ending_disagreements+=Number(a!==b);
 }
 check("paired_accounting",Object.values(metrics.signed_endings).reduce((a,b)=>a+b,0)===n&&Object.values(metrics.reader_endings).reduce((a,b)=>a+b,0)===n);
 return {checks,fixture,migrated,metrics};
}
const root=process.argv[2];if(!root)throw Error('Usage: node verify.mjs <pinned GPTStoryworld checkout> [receipt]');
const files={"storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_bonsai27.json":"f735f6198f2c7c1810d3feef13459632867cf1d9","storyworld_reader.html":"d43d9ab729206f1594ea7cee98918bc9ec92f267"};
const contents=Object.entries(files).map(([p,sha])=>{const b=fs.readFileSync(path.join(root,p));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('blob mismatch '+p);return b.toString('utf8');});
const r=run(api,migrateReservoir,JSON.parse(contents[0]),contents[1]);
const receipt={source_revision:'ee1c6918db77d1e0924877f59eca819bae3f1c8c',source_blobs:files,checks:r.checks,migration:r.migrated.counts,metrics:r.metrics};
const out=JSON.stringify(receipt,null,2)+'\n';if(process.argv[3])fs.writeFileSync(process.argv[3],out);else process.stdout.write(out);
