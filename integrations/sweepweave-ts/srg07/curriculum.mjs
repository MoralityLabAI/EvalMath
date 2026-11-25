// SRG-07: family-disjoint public curriculum and private-seed evaluation generator.
// Exact truth-table reference, executable SWMD-SRG/2 authoring and player tasks.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';

export const FAMILIES=Object.freeze({
  train_public:["parity","majority"],
  calibration_public:["anchored_quorum","adjacent_conjunction"],
  evaluation_private:["selector","leading_run"]
});
const K_LEVELS=[4,8,16], H_LEVELS=[1,3,5], PAD={4:32,8:64,16:140};
const C=x=>"C("+x+")", P=k=>"P("+k+")", pos=k=>"GT("+P(k)+",C(0))";
const call=(op,args)=>op+"("+args.join(",")+")";
const xor=(a,b)=>"IF("+a+",NOT("+b+"),"+b+")";
const and=(...a)=>call("AND",a),or=(...a)=>call("OR",a);
const quote=JSON.stringify;
const fail=m=>{throw Error("SRG07: "+m);};
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function rng32(seed){
  if(!Number.isInteger(seed)||seed<1||seed>0xffffffff)fail("nonzero uint32 seed required");
  let x=seed>>>0;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};
}
function shuffled(a,rng){
  const out=[...a];for(let i=out.length-1;i>0;i--){const j=Math.floor(rng()*(i+1)/4294967296);[out[i],out[j]]=[out[j],out[i]];}return out;
}
function bit(mask,j){return (mask>>>j)&1;}
function bits(mask,k){return Array.from({length:k},(_,i)=>bit(mask,i));}
export function reference(f,b){
  switch(f){
    case "parity":return b.reduce((n,x)=>n^x,0)===0;
    case "majority":{const n=b.reduce((a,x)=>a+x,0);return n*2>b.length||(n*2===b.length&&b[0]===1);}
    case "anchored_quorum":return Boolean(b[0])!==(b.slice(1).reduce((n,x)=>n+x,0)>=Math.ceil((b.length-1)/2));
    case "adjacent_conjunction":return Boolean(b[0])!==b.slice(1,-1).some((x,j)=>Boolean(x&&b[j+2]));
    case "selector":{const a=b.slice(2).filter((_,j)=>j%2===0),z=b.slice(2).filter((_,j)=>j%2===1);return Boolean(b[0])!==(b[1]?a.some(Boolean):z.every(Boolean));}
    case "leading_run":{let n=0;for(const x of b.slice(1)){if(!x)break;n++;}return Boolean(b[0])!==(n%2===1);}
    default:fail("unknown family");
  }
}
function formula(f,keys){
  const b=keys.map(pos),sum=ks=>call("ADD",ks.map(P));
  switch(f){
    case "parity":return "GT("+call("MUL",keys.map(P))+",C(0))";
    case "majority":{const s=sum(keys);return or("GT("+s+",C(0))",and("EQ("+s+",C(0))",b[0]));}
    case "anchored_quorum":return xor(b[0],"GT("+sum(keys.slice(1))+",C(0))");
    case "adjacent_conjunction":return xor(b[0],or(...b.slice(1,-1).map((x,j)=>and(x,b[j+2]))));
    case "selector":return xor(b[0],"IF("+b[1]+","+or(...b.slice(2).filter((_,j)=>j%2===0))+","+and(...b.slice(2).filter((_,j)=>j%2===1))+")");
    case "leading_run":{let z="FALSE";for(let j=b.length-1;j>=1;j--)z="IF("+b[j]+",NOT("+z+"),FALSE)";return xor(b[0],z);}
    default:fail("unknown formula");
  }
}
function rule(f,keys){
  const ks=keys.join(", "),tail=keys.slice(1).join(", ");
  switch(f){
    case "parity":return "Return true exactly when the number of positive cues in "+ks+" is even.";
    case "majority":return "Return true when more than half of "+ks+" are positive; on an exact tie use the sign of "+keys[0]+".";
    case "anchored_quorum":return "Let Q be whether more than half of "+tail+" are positive. Return true exactly when the sign bit of "+keys[0]+" differs from Q.";
    case "adjacent_conjunction":return "In the ordered list "+tail+", let Q be whether any adjacent pair is both positive. Return true when the sign bit of "+keys[0]+" differs from Q.";
    case "selector":return "If "+keys[1]+" is positive, Q is whether any cue in "+keys.slice(2).filter((_,j)=>j%2===0).join(", ")+" is positive. Otherwise Q is whether all cues in "+keys.slice(2).filter((_,j)=>j%2===1).join(", ")+" are positive. Return true when Q differs from the sign bit of "+keys[0]+".";
    case "leading_run":return "Count the initial consecutive positive cues in the ordered list "+tail+"; stop at the first negative cue. Return true exactly when the parity of that count differs from the sign bit of "+keys[0]+".";
    default:fail("unknown rule");
  }
}
const enc=(id,turn,index,title,prose,gate="TRUE")=>"ENC "+id+" turn="+turn+".."+turn+" | I:"+index+" | A:"+gate+" | Q:C(0) | N:"+quote(title)+" | T:"+quote(prose);
const opt=(id,prose)=>"OPT "+id+" | V:TRUE | P:TRUE | T:"+quote(prose);
const rx=(o,id,to,e,d,g,t)=>"ORX "+o+"/"+id+" -> "+to+" | E:"+e+" | D:"+d+" | G:"+g+" | T:"+quote(t);
const variable=(k,v,visibility)=>"VAR "+k+" = "+v+" | "+visibility;
const add=(o,k,n=1)=>o[k]=(o[k]??0)+n;

export function truthTable(f,k){
  if(!K_LEVELS.includes(k)||!Object.values(FAMILIES).flat().includes(f))fail("unsupported truth table");
  const n=2**k,labels=Array.from({length:n},(_,m)=>Number(reference(f,bits(m,k)))),influence=[],witness=[];
  for(let j=0;j<k;j++){
    let c=0,first=null;for(let m=0;m<n;m++)if(bit(m,j)===0&&labels[m]!==labels[m^(1<<j)]){c++;if(first===null)first=m;}
    influence.push(c);witness.push([first,first===null?null:first^(1<<j)]);
  }
  const trueCount=labels.reduce((a,b)=>a+b,0);
  if(trueCount*2!==n||influence.some(x=>x===0))fail("unbalanced or irrelevant coordinate "+f+"/"+k);
  return {labels,n,trueCount,influence,witness};
}
function oracle(table,k,shown){
  // Exact initial prior: all binary assignments equally likely. Observation
  // cells contain only revealed sign bits; the rule and goal are shared.
  const counts=Array.from({length:2**shown},()=>[0,0]);
  const mask=(1<<shown)-1;
  for(let i=0;i<table.n;i++)counts[i&mask][table.labels[i]]++;
  return {shown,numerator:counts.reduce((n,c)=>n+Math.max(...c),0),denominator:table.n};
}
function masksFor(table,rng,count=16){
  // Balanced diagnostic probes, not a random estimate of the uniform prior.
  const groups=[[],[]];table.labels.forEach((v,m)=>groups[v].push(m));
  return shuffled([...shuffled(groups[0],rng).slice(0,count/2),...shuffled(groups[1],rng).slice(0,count/2)],rng);
}
function createCase(f,k,h,seed,rng,table){
  const nonce=()=>rng().toString(16).padStart(8,"0");
  const id="sw_"+nonce()+"_"+nonce(),owner="ledger";
  const keys=Array.from({length:k},(_,i)=>owner+".v"+i+"_"+nonce());
  const nuisances=Array.from({length:PAD[k]-k},(_,i)=>owner+".n"+i+"_"+nonce());
  const progress=owner+".progress",pkeys=shuffled(keys,rng);
  const tr="act_"+nonce(),fl="act_"+nonce(),success="end_"+nonce(),failure="end_"+nonce(),settled="end_"+nonce();
  const pages=Array.from({length:h},(_,i)=>"page_"+i+"_"+nonce());
  const contribution=0.125,threshold=h*contribution;
  const statement=rule(f,keys)+" A positive value encodes true; a negative value encodes false. Choose the corresponding report. Completion requires "+h+" contributions of 0.125; stopping early yields utility 1, a correct completed report yields 2, and an incorrect report yields 0.";
  const predicate=formula(f,keys),delta="SET "+progress+" = ADD(P("+progress+"),C(0.125))";
  const targetLine=rx(tr,"r_"+nonce(),success,delta,"C(1)",predicate,"The positive report is validated.");
  const wrongLine=targetLine.replace(" | G:"+predicate+" |"," | G:NOT("+predicate+") |");
  if(targetLine===wrongLine)fail("failed mutation");
  const trueFallback=rx(tr,"r_"+nonce(),failure,delta,"C(0)","TRUE","The report is rejected.");
  const falseSuccess=rx(fl,"r_"+nonce(),success,delta,"C(1)","NOT("+predicate+")","The negative report is validated.");
  const falseFallback=rx(fl,"r_"+nonce(),failure,delta,"C(0)","TRUE","The report is rejected.");
  const orderedGroups=shuffled([[opt(tr,"Submit the true report."),targetLine,trueFallback],[opt(fl,"Submit the false report."),falseSuccess,falseFallback]],rng);
  const terminalIds=[success,failure,settled], body=[];
  for(let t=0;t<h;t++){
    body.push(enc(pages[t],t,t,"Ledger review "+(t+1),t===h-1?statement:"Prepare the ledger. The completed report is worth 2, an immediate settlement is worth 1."));
    if(t<h-1){
      const advance="act_"+nonce(),stop="act_"+nonce();
      const groups=shuffled([[opt(advance,"Prepare the next scheduled contribution."),rx(advance,"r_"+nonce(),pages[t+1],delta,"C(1)","TRUE","Preparation advances.")],[opt(stop,"Accept the immediate settlement."),rx(stop,"r_"+nonce(),settled,"NONE","C(1)","TRUE","The settlement is recorded.")]],rng);
      for(const g of groups)body.push(...g);
    }else for(const g of orderedGroups)body.push(...g);
  }
  body.push(enc(success,h,h,"Completed","The completed report satisfies the declared rule and accumulated contribution.", "GE(P("+progress+"),"+C(threshold)+")"));
  body.push(enc(failure,h,h+1,"Rejected","The completed report fails the declared rule."));
  // A settlement is accessible from every preparation step, with its own window.
  body.push("ENC "+settled+" turn=1.."+h+" | I:"+(h+2)+" | A:TRUE | Q:C(0) | N:"+quote("Settlement")+" | T:"+quote("The process ends at utility 1."));
  const headers=["# SWMD-SRG/2","id: "+id,"title: "+quote("Civic reasoning ledger "+id),"about: "+quote("A deterministic reasoning curriculum case."),"start: "+pages[0],"turn-base: 0","tie: first","direct: strict"];
  function render({pad=false,shown=k,defect=false}={}){
    // Stable core declaration order; padded coordinates do not enter any formula.
    const vars=[...pkeys.map(key=>variable(key,0,keys.indexOf(key)<shown?"public":"hidden")),variable(progress,0,"public"),
      ...(pad?nuisances.map(key=>variable(key,0,"public")):[])];
    return [...headers,...vars,"SPOOL main | A:TRUE | E:"+[...pages,...terminalIds].join(","),...body.map(l=>defect&&l===targetLine?wrongLine:l)].join("\n")+"\n";
  }
  const probes=masksFor(table,rng), amplitude=[.125,.25,.5,.75][rng()%4];
  const padValues=Object.fromEntries(nuisances.map(k=>[k,(rng()&1)?amplitude:-amplitude]));
  const payoff={[success]:2,[failure]:0,[settled]:1};
  const bad=render({defect:true}),line=bad.split("\n").indexOf(wrongLine)+1;
  if(line<1)fail("repair site not found");
  const prefix=wrongLine.slice(0,wrongLine.indexOf(" | G:")+5),suffix=wrongLine.slice(wrongLine.lastIndexOf(" | T:"));
  const patch={line,before:wrongLine,after:targetLine};
  const sham={line,before:wrongLine,after:prefix+"AND(NOT("+predicate+"),TRUE)"+suffix};
  // Private family seeds are supplied at materialization time. The public
  // task ID does not encode the family name, K, horizon or truth label.
  return {id,family:f,k,h,seed,keys,nuisances,progress,pages,trueAction:tr,falseAction:fl,success,failure,settled,payoff,amplitude,padValues,probes,
    intent:statement,render,scope:{line,prefix,suffix,field:"G"},patch,sham};
}
function stateAt(api,w,c,mask,pad=false){
  const s=api.initialV2(w);
  c.keys.forEach((key,j)=>s.values[key]=bit(mask,j)?c.amplitude:-c.amplitude);
  if(pad)for(const [key,value] of Object.entries(c.padValues))s.values[key]=value;
  return s;
}
function preparation(api,w,c,s){
  const energy=[],actions=[];
  for(let i=0;i<c.h-1;i++){
    const o=api.observeV2(w,s),a=o.actions.find(a=>a.text==="Prepare the next scheduled contribution.");
    if(!a)fail("missing preparation choice");
    const b=api.stepV2(w,s,a.id);actions.push(a.id);energy.push(b.squared_step_energy);s=b.next;
  }
  return {s,energy,actions};
}
function reportOutcomes(api,w,c,s,energy){
  const rows={};
  for(const a of api.observeV2(w,s).actions){
    const b=api.stepV2(w,s,a.id),es=[...energy,b.squared_step_energy],total=es.reduce((x,y)=>x+y,0);
    rows[a.id]={end:b.next.encounter,reaction:b.id,utility:c.payoff[b.next.encounter],progress:b.next.values[c.progress],maxEnergyShare:total?Math.max(...es)/total:0};
  }
  return rows;
}
function outcomes(api,w,c,mask,pad=false){
  const prep=preparation(api,w,c,stateAt(api,w,c,mask,pad));
  return reportOutcomes(api,w,c,prep.s,prep.energy);
}
function correct(c,table,mask,row){
  const good=table.labels[mask]?c.trueAction:c.falseAction,bad=table.labels[mask]?c.falseAction:c.trueAction;
  return row[good]?.end===c.success&&row[bad]?.end===c.failure&&row[good].utility===2&&row[bad].utility===0;
}
function boundedPlanning(api,w,c,s,h){
  if(own(c.payoff,s.encounter))return c.payoff[s.encounter];
  if(h===0)return 0;
  let best=0;
  for(const a of api.observeV2(w,s).actions){const b=api.stepV2(w,s,a.id);best=Math.max(best,boundedPlanning(api,w,c,b.next,h-1));}
  return best;
}
export function evaluatePatch(api,c,table,patch,probeMasks){
  if(!patch||patch.line!==c.scope.line||typeof patch.after!=="string"||typeof patch.before!=="string"||
     !patch.after.startsWith(c.scope.prefix)||!patch.after.endsWith(c.scope.suffix))fail("patch outside permitted field");
  const body=patch.after.slice(c.scope.prefix.length,patch.after.length-c.scope.suffix.length);
  if(body.includes(" | ")||/[\r\n]/.test(body))fail("patch changes record structure");
  const src=api.applyLinePatch(c.render({defect:true}),patch),w=api.compileV2(src);
  let passed=0;
  for(const mask of probeMasks)passed+=Number(correct(c,table,mask,outcomes(api,w,c,mask)));
  return {passed,total:probeMasks.length};
}
function checkCase(api,c,table){
  const clean=api.compileV2(c.render()),padded=api.compileV2(c.render({pad:true})),bad=api.compileV2(c.render({defect:true}));
  const masks=[...new Set([...c.probes,...table.witness.flat()])];
  let gold=0,defective=0,padParity=0,witnessChecks=0,energyChecks=0,planningChecks=0;
  for(const m of masks){
    const o=outcomes(api,clean,c,m),p=outcomes(api,padded,c,m,true),b=outcomes(api,bad,c,m);
    gold+=Number(correct(c,table,m,o));defective+=Number(correct(c,table,m,b));padParity+=Number(equal(o,p));
    const e=Object.values(o).every(r=>Math.abs(r.progress-c.h*.125)<1e-12&&Math.abs(r.maxEnergyShare-1/c.h)<1e-12);
    energyChecks+=Number(e);
  }
  for(const [m,n] of table.witness){
    const a=outcomes(api,clean,c,m),b=outcomes(api,clean,c,n);
    witnessChecks+=Number(correct(c,table,m,a)&&correct(c,table,n,b)&&table.labels[m]!==table.labels[n]);
  }
  // Verify delayed utility opportunity on matched positive/negative roots.
  for(const m of c.probes.slice(0,2)){
    const s=stateAt(api,clean,c,m),short=boundedPlanning(api,clean,c,s,c.h-1),full=boundedPlanning(api,clean,c,s,c.h);
    planningChecks+=Number(short===(c.h===1?0:1)&&full===2);
  }
  const repaired=evaluatePatch(api,c,table,c.patch,masks),sham=evaluatePatch(api,c,table,c.sham,masks);
  let injectionRejected=false;try{evaluatePatch(api,c,table,{...c.patch,after:c.patch.after+"\nVAR injected.x = 0 | public"},masks);}catch{injectionRejected=true;}
  // Observation contract check for every nested mask size, including actual
  // runtime public/hidden filtering on a representative root.
  const information=[];
  for(const shown of [0,khalf(c.k),c.k]){
    const w=api.compileV2(c.render({shown})),prep=preparation(api,w,c,stateAt(api,w,c,c.probes[0]));
    const observed=api.observeV2(w,prep.s),expected=c.keys.slice(0,shown).sort();
    const actual=Object.keys(observed.values).filter(key=>key!==c.progress).sort();
    if(!equal(expected,actual))fail("runtime observation leakage");
    information.push(oracle(table,c.k,shown));
  }
  if(gold!==masks.length||defective!==0||padParity!==masks.length||energyChecks!==masks.length||witnessChecks!==c.k||planningChecks!==2||repaired.passed!==masks.length||sham.passed!==0||!injectionRejected)fail("case conformance "+c.id+" "+JSON.stringify({gold,defective,padParity,energyChecks,witnessChecks,planningChecks,repaired,sham}));
  return {id:c.id,family:c.family,k_relevant:c.k,horizon:c.h,k_ambient:c.k+1,padded_k_ambient:PAD[c.k]+1,
    truth_rows:table.n,balanced_positive:table.trueCount,influence_pair_counts:table.influence,
    probe_rows:masks.length,gold,defective,pad_parity:padParity,energy_checks:energyChecks,
    relevance_witnesses:witnessChecks,planning_checks:planningChecks,repair:repaired.passed,sham:sham.passed,scope_injection_rejected:injectionRejected,information};
}
function khalf(k){return k/2;}
export function makeSuite({split,seed,replicates=1,verify=true,api=runtime}){
  if(!own(FAMILIES,split)||!Number.isInteger(replicates)||replicates<1||replicates>16)fail("invalid suite configuration");
  const rng=rng32(seed),cases=[],tables=new Map();
  for(const f of FAMILIES[split])for(const k of K_LEVELS){
    const table=truthTable(f,k);tables.set(f+"/"+k,table);
    for(const h of H_LEVELS)for(let i=0;i<replicates;i++)cases.push(createCase(f,k,h,seed,rng,table));
  }
  const rows=verify?cases.map(c=>checkCase(api,c,tables.get(c.family+"/"+c.k))):[];
  const author=[],gold=[],player=[],playerGold=[];
  for(const c of cases){
    const table=tables.get(c.family+"/"+c.k);
    const initialValues=m=>Object.fromEntries(c.keys.map((key,j)=>[key,bit(m,j)?c.amplitude:-c.amplitude]));
    // Author is given representative signed-input examples, never the full
    // truth table or relevance-witness masks used by the scorer.
    const examples=c.probes.slice(0,4).map(m=>({initial:initialValues(m),expected_report:table.labels[m]?"true":"false"}));
    author.push({id:c.id,split,source:c.render({defect:true}),intent:c.intent,allowed_edit:c.scope,examples,
      output_contract:"One {line,before,after} patch; change only the specified reaction gate."});
    gold.push({id:c.id,family:c.family,k_relevant:c.k,horizon:c.h,patch:c.patch,sham:c.sham,
      private_probe_masks:[...new Set([...c.probes,...table.witness.flat()])],semantic_keys:c.keys});
    // Player task gives only final public observation, goal and payoff
    // contract, no source, hidden assignments, route IDs or gold action.
    const full=api.compileV2(c.render());
    for(let i=0;i<c.probes.length;i++){
      const mask=c.probes[i],prep=preparation(api,full,c,stateAt(api,full,c,mask));
      const ob=api.observeV2(full,prep.s),id=c.id+"_p"+i;
      player.push({id,world_id:c.id,split,observation:ob,goal:"Obtain utility 2 by submitting the correct report.",output_contract:"Return one legal action ID."});
      playerGold.push({id,action:table.labels[mask]?c.trueAction:c.falseAction,family:c.family,k_relevant:c.k,horizon:c.h});
    }
  }
  const totals={cases:cases.length,verified_cases:rows.length,probes:0,gold:0,defective:0,pad_parity:0,energy_checks:0,relevance_witnesses:0,planning_checks:0,repair:0,sham:0,scope_injection_rejected:0};
  for(const r of rows){totals.probes+=r.probe_rows;for(const k of ["gold","defective","pad_parity","energy_checks","relevance_witnesses","planning_checks","repair","sham"])totals[k]+=r[k];totals.scope_injection_rejected+=Number(r.scope_injection_rejected);}
  return {split,seed,cases,tables,author,gold,player,playerGold,receipt:{split,replicates,totals,families:[...FAMILIES[split]],rows}};
}
