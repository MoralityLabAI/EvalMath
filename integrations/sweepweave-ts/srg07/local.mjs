// SRG-07 local task materializer/scorer. No network or model calls.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {makeSuite,evaluatePatch} from './curriculum.mjs';

const fail=m=>{throw Error("SRG07 local: "+m);};
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const publicSeeds={train_public:0x53520701,calibration_public:0x53520702};
const smokeSeed=0x53520703;
const add=(o,k)=>o[k]=(o[k]??0)+1;
const jsonl=xs=>xs.map(x=>JSON.stringify(x)).join("\n")+(xs.length?"\n":"");
const readRows=p=>fs.readFileSync(p,"utf8").split(/\r?\n/).filter(Boolean).map(s=>JSON.parse(s));
function stateAt(api,w,c,m){
  const s=api.initialV2(w);
  c.keys.forEach((key,j)=>s.values[key]=(m>>>j)&1?c.amplitude:-c.amplitude);
  return s;
}
function prepare(api,w,c,m){
  let s=stateAt(api,w,c,m);
  for(let t=1;t<c.h;t++){
    const a=api.observeV2(w,s).actions.find(a=>a.text==="Prepare the next scheduled contribution.");
    if(!a)fail("missing preparation action");
    s=api.stepV2(w,s,a.id).next;
  }
  return s;
}
function V(api,w,c,s,h){
  if(own(c.payoff,s.encounter))return c.payoff[s.encounter];
  if(h===0)return 0;
  return Math.max(...api.observeV2(w,s).actions.map(a=>V(api,w,c,api.stepV2(w,s,a.id).next,h-1)));
}
export function expandedPlayer(suite,api){
  const player=[],playerGold=[],planning=[],planningGold=[];
  for(const c of suite.cases){
    const tab=suite.tables.get(c.family+"/"+c.k);
    for(const shown of [0,c.k/2,c.k]){
      const w=api.compileV2(c.render({shown}));
      for(let i=0;i<c.probes.length;i++){
        const m=c.probes[i],s=prepare(api,w,c,m),ob=api.observeV2(w,s);
        const id=c.id+"_o"+shown+"_p"+i;
        player.push({id,world_id:c.id,split:suite.split,observation:ob,goal:"Obtain utility 2. Choose the correct report given the available cues.",output_contract:"Return one legal action ID."});
        playerGold.push({id,action:tab.labels[m]?c.trueAction:c.falseAction,family:c.family,k_relevant:c.k,horizon:c.h,shown});
      }
    }
    if(c.h>1){
      const w=api.compileV2(c.render());
      for(let i=0;i<2;i++)for(const budget of [1,c.h]){
        const s=stateAt(api,w,c,c.probes[i]),ob=api.observeV2(w,s);
        const vals=Object.fromEntries(ob.actions.map(a=>[a.id,V(api,w,c,api.stepV2(w,s,a.id).next,budget-1)]));
        const optimum=Math.max(...Object.values(vals)),winners=Object.keys(vals).filter(a=>vals[a]===optimum);
        if(optimum!==(budget===1?1:2)||winners.length!==1)fail("planning control failed");
        const id=c.id+"_h"+budget+"_p"+i;
        planning.push({id,world_id:c.id,split:suite.split,observation:ob,action_budget:budget,required_contributions:c.h,goal:"Maximize terminal utility within the action budget. An immediate settlement yields 1; a correct completed report after all required contributions yields 2; an incorrect or unfinished report yields 0.",output_contract:"Return one legal first action ID."});
        planningGold.push({id,actions:winners,optimum,values:vals,family:c.family,k_relevant:c.k,horizon:c.h,action_budget:budget});
      }
    }
  }
  return {player,playerGold,planning,planningGold};
}
function rowIndex(rows){
  const map=new Map(),duplicates=new Set();
  for(const r of rows){
    if(!r||typeof r.id!=="string")fail("each submission requires string id");
    if(map.has(r.id))duplicates.add(r.id);
    else map.set(r.id,r);
  }
  return {map,duplicates};
}
export function scoreAuthor(suite,rows,api){
  const {map,duplicates}=rowIndex(rows),expected=new Set(suite.cases.map(c=>c.id)),results=[],counts={};
  let n=0,d=0;
  for(const c of suite.cases){
    const table=suite.tables.get(c.family+"/"+c.k),masks=[...new Set([...c.probes,...table.witness.flat()])],r=map.get(c.id);
    let status="missing",passed=0;
    if(duplicates.has(c.id))status="duplicate";
    else if(r){
      try{
        if(Object.keys(r).sort().join(",")!=="after,before,id,line")fail("invalid submission fields");
        const x=evaluatePatch(api,c,table,{line:r.line,before:r.before,after:r.after},masks);
        passed=x.passed;status=passed===masks.length?"pass":"fail";
      }catch(e){status="rejected";}
    }
    add(counts,status);n+=passed;d+=masks.length;
    results.push({id:c.id,family:c.family,k:c.k,horizon:c.h,status,passed,total:masks.length});
  }
  return {kind:"author",counts,passed_probes:n,total_probes:d,unknown_ids:[...map.keys()].filter(id=>!expected.has(id)),results};
}
export function scoreActions(tasks,gold,rows){
  const {map,duplicates}=rowIndex(rows),expected=new Set(tasks.map(t=>t.id)),g=new Map(gold.map(r=>[r.id,r])),counts={},groups={},results=[];
  if(g.size!==tasks.length||expected.size!==tasks.length)fail("invalid task/gold IDs");
  for(const t of tasks){
    const z=g.get(t.id),r=map.get(t.id);if(!z)fail("missing gold");
    let status="missing",success=false;
    if(duplicates.has(t.id))status="duplicate";
    else if(r){
      if(Object.keys(r).sort().join(",")!=="action,id"||typeof r.action!=="string"||!t.observation.actions.some(a=>a.id===r.action))status="rejected";
      else{success=z.actions?z.actions.includes(r.action):z.action===r.action;status=success?"pass":"fail";}
    }
    add(counts,status);
    const key=[z.family,"K"+z.k_relevant,"H"+z.horizon,z.shown!==undefined?"observed"+z.shown:"budget"+z.action_budget].join("/");
    const group=groups[key]??={correct:0,total:0};group.correct+=Number(success);group.total++;
    results.push({id:t.id,status,correct:success});
  }
  return {kind:"action",counts,correct:counts.pass??0,total:tasks.length,unknown_ids:[...map.keys()].filter(id=>!expected.has(id)),groups,results};
}
function write(p,data){fs.writeFileSync(p,data,{mode:0o600,flag:"wx"});}
function repoRoot(){return fs.realpathSync(fileURLToPath(new URL("../../../",import.meta.url)));}
function outsideRepo(p){
  const parent=fs.realpathSync(path.dirname(path.resolve(p))),resolved=path.join(parent,path.basename(path.resolve(p)));
  const rel=path.relative(repoRoot(),resolved);
  return rel===".."||rel.startsWith(".."+path.sep)||path.isAbsolute(rel);
}
function generate(split,out,replicates){
  if(!out||!split)fail("generate requires split and output directory");
  if(split==="evaluation_private"&&!outsideRepo(out))fail("private evaluation must be generated outside the repository");
  let seed=publicSeeds[split];
  if(split==="evaluation_private"){
    do{seed=crypto.randomBytes(4).readUInt32LE(0);}while(!seed||seed===smokeSeed||Object.values(publicSeeds).includes(seed));
  }
  if(!seed)fail("unknown split");
  const suite=makeSuite({split,seed,replicates,verify:true,api});
  const extra=expandedPlayer(suite,api);
  fs.mkdirSync(out,{mode:0o700});
  fs.mkdirSync(path.join(out,"model_input"),{mode:0o700});
  fs.mkdirSync(path.join(out,"verifier"),{mode:0o700});
  const input=path.join(out,"model_input"),priv=path.join(out,"verifier");
  for(const [name,rows] of [["author",suite.author],["player",extra.player],["planning",extra.planning]])write(path.join(input,name+".jsonl"),jsonl(rows));
  for(const [name,rows] of [["author",suite.gold],["player",extra.playerGold],["planning",extra.planningGold]])write(path.join(priv,name+"_gold.jsonl"),jsonl(rows));
  write(path.join(priv,"manifest.json"),JSON.stringify({schema:"SRG07/local/1",split,seed,replicates},null,2)+"\n");
  write(path.join(priv,"receipt.json"),JSON.stringify(suite.receipt,null,2)+"\n");
  console.log(JSON.stringify({split,author:suite.author.length,player:extra.player.length,planning:extra.planning.length,output:path.resolve(out)},null,2));
}
function score(kind,out,submissions){
  if(!["author","player","planning"].includes(kind)||!out||!submissions)fail("score requires kind, generated directory and submission file");
  const m=JSON.parse(fs.readFileSync(path.join(out,"verifier","manifest.json"),"utf8"));
  if(m.schema!=="SRG07/local/1")fail("invalid manifest");
  const s=makeSuite({split:m.split,seed:m.seed,replicates:m.replicates,verify:false,api});
  const rows=readRows(submissions);
  if(kind==="author")return scoreAuthor(s,rows,api);
  const e=expandedPlayer(s,api);
  return kind==="player"?scoreActions(e.player,e.playerGold,rows):scoreActions(e.planning,e.planningGold,rows);
}
const main=process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(main){
  const [cmd,a,b,c]=process.argv.slice(2);
  if(cmd==="generate")generate(a,b,c===undefined?1:Number(c));
  else if(cmd==="score")console.log(JSON.stringify(score(a,b,c),null,2));
  else fail("usage: node local.mjs generate <split> <new-output-dir> [replicates] | score <author|player|planning> <generated-dir> <submissions.jsonl>");
}
