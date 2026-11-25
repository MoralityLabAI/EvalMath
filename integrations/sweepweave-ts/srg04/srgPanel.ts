// Additive SRG-04 editor panel. Intentionally independent of the legacy
// ScriptManager/Rehearsal path. The user opens a SWMD-SRG/1 source explicitly.
import { compileSWMD, initialState, playerObservation, counterfactuals, step } from './swmd-runtime.mjs';
import type { World, State, CounterfactualPacket } from './swmd-runtime.mjs';

let draft = '';
let active: {world: World; state: State} | null = null;
let history: CounterfactualPacket[] = [];

function button(text: string, action: () => void): HTMLButtonElement {
  const b=document.createElement('button'); b.textContent=text; b.type='button';
  b.addEventListener('click',action); return b;
}

export function renderSrgPanel(): HTMLElement {
  const panel=document.createElement('section'); panel.className='sw-panel';
  const title=document.createElement('h3'); title.textContent='SWMD-SRG/1 authoring audit';
  const desc=document.createElement('p'); desc.textContent='Compile a signed, direct-route SWMD profile. Player view shows only declared public values and legal options. Audit export contains private world state and forced reaction branches; keep it separate from player input.';
  const source=document.createElement('textarea'); source.rows=12; source.cols=80;
  source.style.width='100%'; source.value=draft; source.setAttribute('aria-label','SWMD execution profile source');
  const file=document.createElement('input'); file.type='file'; file.accept='.md,.swmd,.txt'; file.setAttribute('aria-label','Load SWMD execution profile');
  const status=document.createElement('pre'); status.setAttribute('role','status');
  const view=document.createElement('pre'); view.style.whiteSpace='pre-wrap';
  const choices=document.createElement('div'); choices.className='sw-row';
  const toolbar=document.createElement('div'); toolbar.className='sw-row';
  const invalidate=()=>{active=null;history=[];view.textContent='';choices.replaceChildren();};
  function show(){
    choices.replaceChildren();
    if(!active){view.textContent='';return;}
    try {
      const obs=playerObservation(active.world,active.state);
      view.textContent=JSON.stringify(obs,null,2);
      for(const action of obs.actions)choices.append(button(action.text,()=>{
        if(!active)return;
        try{
          const packet=counterfactuals(active.world,active.state);
          const result=step(active.world,active.state,action.id);
          history.push(packet);
          active={world:active.world,state:result.next};
          status.textContent='Action applied.';
          show();
        }catch(e){status.textContent=String(e);}
      }));
    }catch(e){status.textContent=String(e);}
  }
  source.addEventListener('input',()=>{draft=source.value;invalidate();status.textContent='Source changed; compile before continuing.';});
  file.addEventListener('change',async()=>{
    const f=file.files?.[0];if(!f)return;
    try{draft=await f.text();source.value=draft;invalidate();status.textContent='Source loaded; compile to play.';}
    catch(e){status.textContent=String(e);}
  });
  toolbar.append(button('Compile / reset',()=>{
    draft=source.value;invalidate();
    try{const world=compileSWMD(draft);active={world,state:initialState(world)};status.textContent='Compiled '+world.id;show();}
    catch(e){status.textContent=String(e);}
  }));
  toolbar.append(button('Export privileged audit JSON',()=>{
    if(!active){status.textContent='Compile a world first.';return;}
    const session=active;
    try{
      const packet=counterfactuals(session.world,session.state);
      // Exact source is included for reproducibility; never pass this packet to the player.
      const data={classification:'verifier-only',runtime:'SWMD-SRG/1',source:session.world.source,
        history:[...history],current:packet};
      const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
      const url=URL.createObjectURL(blob),a=document.createElement('a');
      a.href=url;a.download=session.world.id+'.srg-audit.json';
      document.body.append(a);a.click();a.remove();URL.revokeObjectURL(url);
      status.textContent='Privileged audit download requested.';
    }catch(e){status.textContent=String(e);}
  }));
  panel.append(title,desc,file,source,toolbar,status,view,choices);show();return panel;
}
