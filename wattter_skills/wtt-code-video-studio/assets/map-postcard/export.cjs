/* New-directory-only node-canvas export and direct pixel seam validation. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {createCanvas}=require(process.env.CANVAS_MODULE||'canvas');
const {make,river,road,H}=require('./map.js');
const at=process.argv.indexOf('--out');if(at<0)throw Error('use --out NEW_DIRECTORY [--check-only]');const out=path.resolve(process.argv[at+1]);
if(fs.existsSync(out))throw Error('输出必须是新目录；已锁项目只能向候选目录导出，不覆盖作品');
const configAt=process.argv.indexOf('--config'),config=JSON.parse(fs.readFileSync(configAt<0?path.join(__dirname,'config.json'):process.argv[configAt+1]));
const canvas=createCanvas(1080,1080),map=make(canvas,config),ctx=canvas.getContext('2d');fs.mkdirSync(out,{recursive:true});fs.copyFileSync(path.join(__dirname,'map.js'),path.join(out,'map.js'));fs.copyFileSync(__filename,path.join(out,'export.cjs'));
const pixels=(f,opt)=>{map.frame(f,opt);return Buffer.from(ctx.getImageData(0,0,1080,1080).data);};
const mad=(a,b)=>{let sum=0,n=0;for(let i=0;i<a.length;i++)if(i%4!==3){sum+=Math.abs(a[i]-b[i]);n++;}return sum/n/255;};
const sha=a=>crypto.createHash('sha256').update(a).digest('hex');
const a=pixels(0),end=pixels(599),middle=pixels(270),other=pixels(135);pixels(500);const again=pixels(270);
const rawA=pixels(0,{unmasked:true}),rawEnd=pixels(599,{unmasked:true}),rawCycle=pixels(600,{unmasked:true});
const e=.001;let topology=true;for(const fn of [river,road]){topology&&=Math.abs(fn(0)-fn(H))<1e-8;topology&&=Math.abs((fn(e)-fn(-e))/(2*e)-(fn(H+e)-fn(H-e))/(2*e))<1e-6;}
const foreground=Array.from({length:rawA.length/4},(_,i)=>Math.max(Math.abs(rawA[i*4]-253),Math.abs(rawA[i*4+1]-253),Math.abs(rawA[i*4+2]-249))>20).filter(Boolean).length/(rawA.length/4);
const report={sourceSha256:sha(fs.readFileSync(path.join(__dirname,'map.js'))),node:process.version,canvas:require(path.join(path.dirname(require.resolve(process.env.CANVAS_MODULE||'canvas')),'package.json')).version,width:1080,height:1080,fps:30,frames:600,threshold:12/255,seamMAD:mad(a,end),unmaskedSeamMAD:mad(rawA,rawEnd),cycleMAD:mad(rawA,rawCycle),deterministic:sha(middle)===sha(again),topology,foregroundRatio:foreground,motionMAD:mad(middle,other),cloudLayerHeight:H*.55};
report.passed=report.seamMAD<report.threshold&&report.unmaskedSeamMAD<report.threshold&&report.cycleMAD===0&&report.deterministic&&topology&&foreground>.1&&report.motionMAD>.005;
fs.writeFileSync(path.join(out,'seam-check.json'),JSON.stringify(report,null,2));
for(const f of [0,150,300,450,599]){map.frame(f);fs.writeFileSync(path.join(out,`preview-${f}.png`),canvas.toBuffer('image/png'));}
if(!report.passed)throw Error('接缝/确定性/非空检查失败，见seam-check.json；禁止标记无缝通过');
if(!process.argv.includes('--check-only')){const dir=path.join(out,'frames');fs.mkdirSync(dir);for(let i=0;i<600;i++){map.frame(i);fs.writeFileSync(path.join(dir,`frame-${String(i).padStart(4,'0')}.png`),canvas.toBuffer('image/png'));if(i%100===0)console.log('frame',i);}}
fs.copyFileSync(configAt<0?path.join(__dirname,'config.json'):process.argv[configAt+1],path.join(out,'config.json'));
console.log(JSON.stringify(report));
