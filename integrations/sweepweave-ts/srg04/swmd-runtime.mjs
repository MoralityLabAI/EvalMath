// SWMD-SRG/1: signed BNumber, explicit direct-route deterministic runtime.
// This module is browser-safe ECMAScript; a typed TS adapter can import it.
// Independent of the legacy SweepWeave evaluator and its incomplete operators.
const KEY = /^[A-Za-z_][\w-]*\.[A-Za-z_][\w-]*(?:\[[A-Za-z_][\w-]*\]){0,2}$/;
const ID = /^[A-Za-z_][\w-]*$/;
const NUMBER = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/;
const own = (o,k) => Object.prototype.hasOwnProperty.call(o,k);
const fail = m => { throw new Error("SWMD-SRG/1: "+m); };
const finite = n => {if(typeof n!=="number"||!Number.isFinite(n))fail("nonfinite numeric value");return n;};
const bounded = n => {finite(n);if(n < -1 || n > 1)fail("BNumber outside [-1,1]");return n;};
const clamp = n => Math.max(-1,Math.min(1,finite(n)));
const map = () => Object.create(null);
const frozen = x => {if(x && typeof x==="object"&&!Object.isFrozen(x)){for(const v of Object.values(x))frozen(v);Object.freeze(x);}return x;};

const signatures = {
  ADD:["n","n",1,Infinity], MUL:["n","n",1,Infinity],
  MIN:["n","n",1,Infinity], MAX:["n","n",1,Infinity],
  SUB:["n","n",2,2], DIV:["n","n",2,2], ABS:["n","n",1,1],
  CLAMP:["n","n",1,1], NUDGE:["n","n",2,2], BLEND:["n","n",3,3],
  GE:["b","n",2,2], GT:["b","n",2,2], LE:["b","n",2,2],
  LT:["b","n",2,2], EQ:["b","n",2,2], NE:["b","n",2,2],
  AND:["b","b",1,Infinity], OR:["b","b",1,Infinity], NOT:["b","b",1,1],
};

export function parseExpression(text, coordinates, expected) {
  let i=0;
  const ws=()=>{while(/\s/.test(text[i]||"")&&i<text.length)i++;};
  const eat=c=>{ws();if(text[i]!==c)fail("expected "+c+" at "+i+" in "+text);i++;};
  function parse(depth=0){
    if(depth>64)fail("expression nesting limit");
    ws();const number=text.slice(i).match(NUMBER);
    if(number){i+=number[0].length;finite(Number(number[0]));return {op:"literal",type:"n",literal:number[0]};}
    const token=text.slice(i).match(/^[A-Z][A-Z0-9_]*/);
    if(!token)fail("expected expression at "+i+" in "+text);
    const op=token[0];i+=op.length;
    if(op==="TRUE"||op==="FALSE")return {op:"boolean",type:"b",value:op==="TRUE"};
    eat("(");
    if(op==="P"){
      const end=text.indexOf(")",i);if(end<0)fail("unclosed pointer");
      const key=text.slice(i,end).trim();i=end+1;
      if(!KEY.test(key)||!own(coordinates,key))fail("undeclared coordinate "+key);
      return {op:"pointer",type:"n",key};
    }
    const args=[parse(depth+1)];ws();
    while(text[i]===","){i++;args.push(parse(depth+1));ws();}
    eat(")");
    if(op==="C"){if(args.length!==1||args[0].op!=="literal")fail("C requires a numeric literal");return args[0];}
    if(op==="IF"){
      if(args.length!==3||args[0].type!=="b"||args[1].type!==args[2].type)fail("IF types");
      return {op,type:args[1].type,args};
    }
    const sig=own(signatures,op)?signatures[op]:null;
    if(!sig||args.length<sig[2]||args.length>sig[3]||args.some(a=>a.type!==sig[1]))fail("unsupported operator, arity or type: "+op);
    return {op,type:sig[0],args};
  }
  const result=parse();ws();if(i!==text.length)fail("trailing expression text");
  if(expected&&result.type!==expected)fail("expected "+expected+" expression");
  return frozen(result);
}

export function evaluate(node,state){
  switch(node.op){
    case "literal":return finite(Number(node.literal));
    case "boolean":return node.value;
    case "pointer":if(!own(state,node.key))fail("missing runtime pointer "+node.key);return bounded(state[node.key]);
    case "IF":return evaluate(node.args[evaluate(node.args[0],state)?1:2],state);
    case "AND":return node.args.every(x=>evaluate(x,state));
    case "OR":return node.args.some(x=>evaluate(x,state));
    case "NOT":return !evaluate(node.args[0],state);
  }
  const a=node.args.map(x=>evaluate(x,state));
  switch(node.op){
    case "ADD":return finite(a.reduce((x,y)=>x+y,0));
    case "MUL":return finite(a.reduce((x,y)=>x*y,1));
    case "MIN":return Math.min(...a);
    case "MAX":return Math.max(...a);
    case "SUB":return finite(a[0]-a[1]);
    case "DIV":if(a[1]===0)fail("division by zero");return finite(a[0]/a[1]);
    case "ABS":return Math.abs(a[0]);
    case "CLAMP":return clamp(a[0]);
    case "NUDGE":return clamp(bounded(a[0])*(1-Math.abs(bounded(a[1])))+a[1]);
    case "BLEND":{const w=(bounded(a[2])+1)/2;return clamp(bounded(a[0])*(1-w)+bounded(a[1])*w);}
    case "GE":return a[0]>=a[1];case "GT":return a[0]>a[1];
    case "LE":return a[0]<=a[1];case "LT":return a[0]<a[1];
    case "EQ":return a[0]===a[1];case "NE":return a[0]!==a[1];
    default:fail("unsupported compiled expression "+node.op);
  }
}

// A strict direct-routing subset. Existing SWMD-0-MIN is deliberately refused
// until omitted semantics are supplied. No evaluation of arbitrary source code.
export function compileSWMD(source){
  if(typeof source!=="string"||source.length>2_000_000)fail("invalid source size");
  const lines=source.replace(/^\uFEFF/,"").split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
  if(lines.shift()!=="# SWMD-SRG/1")fail("missing lossless profile header");
  const world={profile:"SWMD-SRG/1",source,coordinates:map(),pages:map()};
  const seenOptions=new Set(),seenReactions=new Set();
  let current=null;
  const header=(name,v)=>{if(current||own(world,name))fail("duplicate or late "+name);world[name]=v;};
  const expr=(s,t)=>parseExpression(s,world.coordinates,t);
  for(const line of lines){
    let m;
    if((m=line.match(/^id:\s*(\S+)$/))){if(!ID.test(m[1]))fail("invalid world id");header("id",m[1]);continue;}
    if((m=line.match(/^title:\s*(.+)$/))){header("title",m[1]);continue;}
    if((m=line.match(/^start:\s*(\S+)$/))){header("start",m[1]);continue;}
    if((m=line.match(/^tie:\s*(first|last)$/))){header("tie",m[1]);continue;}
    if((m=line.match(/^VAR\s+(\S+)\s*=\s*(\S+)\s*\|\s*(public|hidden)$/))){
      if(current||!KEY.test(m[1])||own(world.coordinates,m[1])||!NUMBER.test(m[2])||m[2].match(NUMBER)[0]!==m[2])fail("invalid variable "+m[1]);
      world.coordinates[m[1]]={initial:bounded(Number(m[2])),literal:m[2],visibility:m[3]};continue;
    }
    if((m=line.match(/^ENC\s+(\S+)\s+turn=(\d+)\.\.(\d+)\s*\|\s*A:(.+)$/))){
      const [id,lo,hi]=[m[1],Number(m[2]),Number(m[3])];
      if(!ID.test(id)||id==="wild"||own(world.pages,id)||!Number.isSafeInteger(lo)||!Number.isSafeInteger(hi)||lo>hi)fail("bad encounter "+id);
      current={id,lo,hi,gate:expr(m[4],"b"),options:map()};world.pages[id]=current;continue;
    }
    if((m=line.match(/^OPT\s+(\S+)\s*\|\s*V:(.*?)\s*\|\s*P:(.+)$/))){
      if(!current||!ID.test(m[1])||seenOptions.has(m[1]))fail("bad or duplicate option");
      seenOptions.add(m[1]);current.options[m[1]]={id:m[1],visible:expr(m[2],"b"),performable:expr(m[3],"b"),reactions:[]};continue;
    }
    if((m=line.match(/^ORX\s+(\S+)\/(\S+)\s*->\s*(\S+)\s*\|\s*O:(.*?)\s*\|\s*E:(.*?)\s*\|\s*D:(.*?)\s*\|\s*G:(.+)$/))){
      const opt=current&&current.options[m[1]];
      if(!opt||!ID.test(m[2])||seenReactions.has(m[2])||!ID.test(m[3])||m[3]==="wild")fail("bad reaction, option or direct destination");
      seenReactions.add(m[2]);
      if(own(opt,"text")&&opt.text!==m[4])fail("inconsistent option text");opt.text=m[4];
      const effects=m[5]==="NONE"?[]:m[5].split(/\s*;\s*/).map(s=>{
        const a=s.match(/^SET\s+(\S+)\s*=\s*(.+)$/);
        if(!a||!own(world.coordinates,a[1]))fail("unsupported effect or undeclared target");
        return {key:a[1],value:expr(a[2],"n")};
      });
      opt.reactions.push({id:m[2],to:m[3],effects,desirability:expr(m[6],"n"),gate:expr(m[7],"b")});continue;
    }
    fail("unrecognized line "+line.slice(0,120));
  }
  for(const k of ["id","title","start","tie"])if(!own(world,k))fail("missing "+k);
  if(!own(world.pages,world.start))fail("missing start encounter");
  for(const p of Object.values(world.pages))for(const o of Object.values(p.options)){
    if(!o.reactions.length||!o.text)fail("option without reactions/text "+o.id);
    for(const r of o.reactions)if(!own(world.pages,r.to))fail("missing destination "+r.to);
  }
  return frozen(world);
}

function pageValid(page,turn,state){return page.lo<=turn&&turn<=page.hi&&evaluate(page.gate,state);}
export function initialState(world){
  const values=map();for(const [key,v] of Object.entries(world.coordinates))values[key]=v.initial;
  if(!pageValid(world.pages[world.start],0,values))fail("initial encounter blocked");
  return {encounter:world.start,turn:0,values};
}
function assertState(world,state){
  if(!state||!own(world.pages,state.encounter)||!Number.isSafeInteger(state.turn)||state.turn<0||!state.values)fail("invalid state");
  for(const k of Object.keys(world.coordinates))if(!own(state.values,k))fail("missing coordinate "+k);else bounded(state.values[k]);
  if(Object.keys(state.values).length!==Object.keys(world.coordinates).length)fail("extraneous runtime coordinates");
  const page=world.pages[state.encounter];if(!pageValid(page,state.turn,state.values))fail("current encounter blocked");
  return page;
}
function menu(world,state){
  const p=assertState(world,state);
  return Object.values(p.options).filter(o=>evaluate(o.visible,state.values)&&evaluate(o.performable,state.values));
}
export function playerObservation(world,state){
  const opts=menu(world,state);
  const values=map();for(const [k,v] of Object.entries(world.coordinates))if(v.visibility==="public")values[k]=state.values[k];
  return {world_id:world.id,encounter:state.encounter,turn:state.turn,values,actions:opts.map(o=>({id:o.id,text:o.text})),
    status:Object.keys(world.pages[state.encounter].options).length===0?"terminal":opts.length===0?"dead_end":"decision"};
}
function applyReaction(world,state,r){
  const values=Object.assign(map(),state.values),writes=[];
  for(const e of r.effects){
    const before=values[e.key],after=bounded(evaluate(e.value,values));
    values[e.key]=after;writes.push({key:e.key,before,after});
  }
  const next={encounter:r.to,turn:state.turn+1,values};
  const valid=pageValid(world.pages[r.to],next.turn,values);
  const energy=finite(Object.keys(values).reduce((n,k)=>n+(values[k]-state.values[k])**2,0));
  return {status:valid?"ok":"blocked_destination",next,writes,squared_step_energy:energy};
}
// Privileged evaluator output. Every reaction is labelled eligible/selected;
// forced eligible alternatives are counterfactuals, not legal player actions.
export function counterfactuals(world,state){
  const opts=menu(world,state);
  const actions=opts.map(o=>{
    const scores=o.reactions.map(r=>({id:r.id,eligible:evaluate(r.gate,state.values),score:evaluate(r.desirability,state.values)}));
    const elig=scores.filter(r=>r.eligible);
    if(!elig.length)return {id:o.id,status:"no_eligible_reaction",scores,winners:[],selected:null,branches:[]};
    const max=Math.max(...elig.map(r=>r.score));
    const winners=elig.filter(r=>r.score===max).map(r=>r.id);
    const selected=world.tie==="first"?winners[0]:winners[winners.length-1];
    const branches=o.reactions.filter(r=>elig.some(x=>x.id===r.id)).map(r=>({id:r.id,...applyReaction(world,state,r)}));
    return {id:o.id,status:branches.find(b=>b.id===selected).status,scores,winners,selected,branches};
  });
  return {profile:world.profile,world_id:world.id,pre:{encounter:state.encounter,turn:state.turn,values:{...state.values}},actions};
}
export function step(world,state,actionId){
  const action=counterfactuals(world,state).actions.find(x=>x.id===actionId);
  if(!action)fail("illegal action "+actionId);
  if(action.status!=="ok")fail("selected action blocked: "+action.status);
  const branch=action.branches.find(b=>b.id===action.selected);
  return {reaction:action.selected,next:branch.next,writes:branch.writes,squared_step_energy:branch.squared_step_energy};
}
