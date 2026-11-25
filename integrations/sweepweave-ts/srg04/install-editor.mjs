// Preview by default. Pass --apply to install against the pinned Play tab.
// Does not modify legacy simulation logic or silently replace prior SRG files.
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
const root=process.argv[2];
if(!root)throw Error('Usage: node install-editor.mjs <sweepweave-ts checkout> [--apply]');
if(process.argv.slice(3).some(x=>x!=='--apply'))throw Error('Unknown argument');
const apply=process.argv.includes('--apply');
const packageData=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8'));
if(packageData.name!=='sweepweave-ts')throw Error('Wrong target repository');
const play=path.join(root,'src/ui/tabs/play.ts'),buf=fs.readFileSync(play);
const sha=crypto.createHash('sha1').update('blob '+buf.length+'\0').update(buf).digest('hex');
const expected='1a93817c03711281dd7d82610b12d77545945dbd';
if(sha!==expected)throw Error('Play tab differs from reviewed blob; inspect and rebase adapter manually');
const target=path.join(root,'src/srg04');
if(fs.existsSync(target))throw Error('Refusing to replace existing '+target);
const original=buf.toString('utf8');
const old='  return container;\n}';
if(original.split(old).length!==2)throw Error('Cannot locate unique panel insertion point');
const patch="import { renderSrgPanel } from '../../srg04/srgPanel';\n"+original.replace(old,'  container.appendChild(renderSrgPanel());\n'+old);
const files=['swmd-runtime.mjs','swmd-runtime.d.mts','srgPanel.ts'];
for(const name of files)fs.accessSync(new URL('./'+name,import.meta.url),fs.constants.R_OK);
console.log(JSON.stringify({apply,target,play,copy:files,reviewed_play_blob:sha},null,2));
if(apply){
  fs.mkdirSync(target);
  for(const name of files)fs.copyFileSync(new URL('./'+name,import.meta.url),path.join(target,name),fs.constants.COPYFILE_EXCL);
  // Leave the target as ordinary working-tree changes for review.
  fs.writeFileSync(play,patch,'utf8');
  console.log('Installed. Run npm test and npm run build; inspect git diff before committing.');
}
