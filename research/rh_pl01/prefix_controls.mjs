// RH-PL-13: exact finite recursion and harmonic-identity controls.
export function finitePrefixAudit(max=128){
 const assert=(q,m)=>{if(!q)throw Error(m)};
 const gcd=(a,b)=>{while(b)[a,b]=[b,a%b];return a};
 let A=0n,B=1n,rf=0n,rd=1n;
 const vals=[],prefixes=[],check={factorial:0,numerator:0,positive:0,reduced_harmonic:0,extensions:0,compatible_overlap_values:0,union_values:0,mutations_rejected:0};
 for(let i=0;i<=max;i++){
   const n=BigInt(i);
   if(i){A=n*A+B;B=n*B;rf=rf*n+rd;rd*=n;const g=gcd(rf,rd);rf/=g;rd/=g}
   let fac=1n;for(let j=1n;j<=n;j++)fac*=j;
   assert(B===fac,"factorial");check.factorial++;
   let s=0n;for(let j=1n;j<=n;j++){assert(fac%j===0n,"divides");s+=fac/j}
   assert(A===s,"numerator");check.numerator++;
   assert(B>0n,"positive");check.positive++;
   assert(A*rd===B*rf,"harmonic");check.reduced_harmonic++;
   vals.push([A,B]);prefixes.push(vals.map(v=>v.slice()));
 }
 for(let i=1;i<prefixes.length;i++){
   const p=prefixes[i-1],q=prefixes[i],n=BigInt(i);
   assert(q.length===p.length+1&&q.at(-1)[0]===n*p.at(-1)[0]+p.at(-1)[1]&&q.at(-1)[1]===n*p.at(-1)[1],"extension");check.extensions++;
 }
 for(let i=0;i<prefixes.length;i++)for(let j=i;j<prefixes.length;j++)for(let z=0;z<=i;z++){assert(prefixes[i][z].every((v,k)=>v===prefixes[j][z][k]),"overlap");check.compatible_overlap_values++}
 const union=new Map();
 for(const prefix of prefixes)for(let i=0;i<prefix.length;i++){const value=prefix[i];if(union.has(i))assert(value.every((v,k)=>v===union.get(i)[k]),"union conflict");union.set(i,value)}
 for(let i=0;i<=max;i++){assert(union.has(i)&&union.get(i).every((v,k)=>v===vals[i][k]),"union total");check.union_values++}
 const valid=prefix=>{
   if(prefix.length<1||prefix[0][0]!==0n||prefix[0][1]!==1n)return false;
   for(let i=1;i<prefix.length;i++){const n=BigInt(i);if(prefix[i][0]!==n*prefix[i-1][0]+prefix[i-1][1]||prefix[i][1]!==n*prefix[i-1][1])return false}
   return true;
 };
 for(let i=0;i<=max;i++)for(let j=0;j<2;j++){const v=prefixes[i].map(x=>x.slice());v[i][j]++;assert(!valid(v),"accepted mutation");check.mutations_rejected++}
 assert(prefixes.every(valid),"valid prefix rejected");
 return {max,controls:check,total:Object.values(check).reduce((x,y)=>x+y,0),scope:"finite exact standard-natural arithmetic only"};
}
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/prefix_controls.mjs'))console.log(JSON.stringify(finitePrefixAudit(),null,2));
