// Public pilot scorer. One JSONL row: {"id":"...","patch":{"line":1,"before":"...","after":"..."}}.
// Gold is regenerated inside the verifier; never give the gold file to the model.
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import * as api from './swmd-runtime-v2.mjs';
import {buildGym} from './build-authoring-gym.mjs';

export function parseRows(text){
  return text.split(/\r?\n/).filter(x=>x.trim()).map((line,i)=>{
    try{return JSON.parse(line);}catch{throw Error('invalid JSONL row '+(i+1));}
  });
}
export function scoreRows(gym,rows,split='all'){
  if(!['all','train_public','calibration_public'].includes(split))throw Error('invalid split');
  const tasks=gym.publicRows.filter(t=>split==='all'||t.split===split);
  const byId=new Map(tasks.map(t=>[t.id,t])),entries=new Map(),unknown=[];
  for(const row of rows){
    if(!row||typeof row.id!=='string'||!byId.has(row.id)){unknown.push(row?.id??null);continue;}
    const group=entries.get(row.id)??[];group.push(row);entries.set(row.id,group);
  }
  const detail=[];
  for(const t of tasks){
    const group=entries.get(t.id)??[],total=t.author_visible_probes.length;
    if(group.length!==1){
      detail.push({id:t.id,status:group.length?'duplicate':'missing',passed:0,total});continue;
    }
    const p=group[0].patch;
    try{
      if(!p||!Number.isSafeInteger(p.line)||typeof p.before!=='string'||typeof p.after!=='string')throw Error('invalid patch shape');
      const s=gym.scoreSubmission(t.id,p);
      if(s.total!==total)throw Error('probe accounting mismatch');
      detail.push({id:t.id,status:s.passed===s.total?'repaired':'failed',passed:s.passed,total});
    }catch(e){detail.push({id:t.id,status:'rejected',passed:0,total,error:String(e).slice(0,500)});}
  }
  const status={};for(const d of detail)status[d.status]=(status[d.status]??0)+1;
  return {split,tasks:tasks.length,submitted:rows.length,unknown,status,
    fully_repaired:detail.filter(d=>d.status==='repaired').length,
    probes_passed:detail.reduce((n,d)=>n+d.passed,0),
    probes_total:detail.reduce((n,d)=>n+d.total,0),detail};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
  const [input,output,split='all']=process.argv.slice(2);
  if(!input)throw Error('Usage: node score-author-patches.mjs submissions.jsonl [receipt.json] [all|train_public|calibration_public]');
  const g=buildGym(api),result=scoreRows(g,parseRows(fs.readFileSync(input,'utf8')),split);
  const text=JSON.stringify(result,null,2)+'\n';
  if(output)fs.writeFileSync(output,text);else process.stdout.write(text);
}
