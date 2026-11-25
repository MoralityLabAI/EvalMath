// Pinned Reservoir Dogs source -> SWMD-SRG/2; mechanics, narrative and order.
// No inferred reward. Defaults for referenced missing beliefs follow the
// inspected reader's zero fallback, materialized explicitly at compile time.
export function migrateReservoir(d){
  const fail=m=>{throw Error("SRG-05 migration: "+m);};
  const chars=new Map(d.characters.map(c=>[c.id,c]));
  const properties=new Map(d.authored_properties.map(p=>[p.id,p]));
  const coordinates=new Map();
  const key=p=>{
    if(p.pointer_type!=="Bounded Number Pointer"||!chars.has(p.character)||!Array.isArray(p.keyring)||p.keyring.length<1||p.keyring.length>3||!properties.has(p.keyring[0])||p.keyring.slice(1).some(x=>!chars.has(x)))fail("invalid pointer");
    const k=p.character+"."+p.keyring[0]+p.keyring.slice(1).map(x=>"["+x+"]").join("");
    const raw=chars.get(p.character).bnumber_properties;
    const initial=raw[p.keyring.join("::")]??(p.keyring.length===1?(raw[p.keyring[0]]??properties.get(p.keyring[0]).default_value):0);
    if(typeof initial!=="number"||!Number.isFinite(initial)||Math.abs(initial)>1)fail("unsupported initial value "+k);
    if(!coordinates.has(k))coordinates.set(k,{initial,visibility:p.keyring.length===1?"public":"hidden",depth:p.keyring.length-1});
    return k;
  };
  const ops={"Addition":"ADD","Multiplication":"MUL","Nudge":"NUDGE","And":"AND","Or":"OR","Absolute Value":"ABS","Maximum":"MAX","Minimum":"MIN"};
  const cmp={"Greater Than or Equal To":"GE","Greater Than":"GT","Less Than or Equal To":"LE","Less Than":"LT","Equal To":"EQ","Not Equal To":"NE"};
  function expr(x){
    if(typeof x==="boolean")return x?"TRUE":"FALSE";
    if(typeof x==="number"&&Number.isFinite(x))return "C("+x+")";
    if(!x||typeof x!=="object")fail("missing script");
    if(x.pointer_type==="Boolean Constant")return x.value===true?"TRUE":x.value===false?"FALSE":fail("invalid Boolean Constant");
    if(x.pointer_type==="Bounded Number Constant"&&Number.isFinite(x.value))return "C("+x.value+")";
    if(x.pointer_type==="Bounded Number Pointer"){
      const p="P("+key(x)+")",a=x.coefficient??1;
      if(!Number.isFinite(a))fail("invalid coefficient");
      return a===1?p:"MUL("+p+",C("+a+"))";
    }
    const op=x.operator_type==="Arithmetic Comparator"?cmp[x.operator_subtype]:ops[x.operator_type];
    if(!op||!Array.isArray(x.operands))fail("unsupported operator "+x.operator_type);
    return op+"("+x.operands.map(expr).join(",")+")";
  }
  const prose=x=>{const v=typeof x==="string"?x:x?.value;if(typeof v!=="string")fail("missing narrative text");return JSON.stringify(v);};
  for(const c of d.characters)for(const prop of d.authored_properties)
    key({pointer_type:"Bounded Number Pointer",character:c.id,keyring:[prop.id]});
  const spools=[...d.spools].sort((a,b)=>a.creation_index-b.creation_index);
  const start=spools.find(s=>s.starts_active)?.encounters[0];if(!start)fail("missing initial spool");
  const body=[];
  for(const s of spools)body.push("SPOOL "+s.id+" | A:"+(s.starts_active?"TRUE":"FALSE")+" | E:"+s.encounters.join(","));
  let reactions=0,writes=0,options=0,wild=0;
  for(const p of d.encounters){
    if(p.prerequisites?.length)fail("unsupported encounter prerequisites");
    const memberIds=spools.filter(s=>s.encounters.includes(p.id)).map(s=>s.id).sort();
    if(JSON.stringify(memberIds)!==JSON.stringify([...p.connected_spools].sort()))fail("inconsistent spool membership");
    body.push("ENC "+p.id+" turn="+p.earliest_turn+".."+p.latest_turn+" | I:"+p.creation_index+" | A:"+expr(p.acceptability_script)+" | Q:"+expr(p.desirability_script)+" | N:"+prose(p.title)+" | T:"+prose(p.text_script));
    for(const o of p.options){
      if(o.prerequisites?.length)fail("unsupported option prerequisites");
      options++;body.push("OPT "+o.id+" | V:"+expr(o.visibility_script)+" | P:"+expr(o.performability_script)+" | T:"+prose(o.text_script));
      for(const r of o.reactions){
        if(r.prerequisites?.length||r.activate_spools?.length||r.deactivate_spools?.length)fail("unsupported reaction metadata");
        reactions++;wild+=Number(r.consequence_id==="wild");
        const es=r.after_effects.map(e=>{
          if(e.effect_type!=="Bounded Number Effect"||e.Set.coefficient!==1)fail("unsupported effect");
          writes++;return "SET "+key(e.Set)+" = CLAMP("+expr(e.to)+")";
        }).join("; ")||"NONE";
        body.push("ORX "+o.id+"/"+r.id+" -> "+r.consequence_id+" | E:"+es+" | D:"+expr(r.desirability_script)+" | G:TRUE | T:"+prose(r.text_script));
      }
    }
  }
  const source=["# SWMD-SRG/2","id: "+d.IFID,"title: "+prose(d.storyworld_title),"about: "+prose(d.about_text),"start: "+start,"turn-base: 1","tie: first","direct: explicit",
    ...[...coordinates].map(([k,v])=>"VAR "+k+" = "+v.initial+" | "+v.visibility),...body].join("\n")+"\n";
  const depths=[0,0,0];for(const v of coordinates.values())depths[v.depth]++;
  return {source,counts:{encounters:d.encounters.length,options,reactions,writes,wild,coordinates_by_depth:depths,spools:spools.length}};
}
