/* New-directory-only export: snapshots the entire renderer, checks the world and camera, then exports. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const Canvas=require(process.env.CANVAS_MODULE||'canvas'),{createCanvas}=Canvas;
const {make,river,road,H}=require('./map.js');
const at=process.argv.indexOf('--out');if(at<0||!process.argv[at+1]||process.argv[at+1].startsWith('--'))throw Error('use --out NEW_DIRECTORY [--config FILE] [--check-only]');
const out=path.resolve(process.argv[at+1]);if(fs.existsSync(out))throw Error('输出必须是新目录；已锁项目只能向候选目录导出，不覆盖作品');
const configAt=process.argv.indexOf('--config');if(configAt>=0&&(!process.argv[configAt+1]||process.argv[configAt+1].startsWith('--')))throw Error('--config须指定文件');
const configFile=configAt<0?path.join(__dirname,'config.json'):path.resolve(process.argv[configAt+1]),config=JSON.parse(fs.readFileSync(configFile));
const canvas=createCanvas(1080,1080),map=make(canvas,config),ctx=canvas.getContext('2d'),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const names=['map.js','world.js','legacy-scroll.js','presentation.js','export.cjs','index.html'],sources=Object.fromEntries(names.map(f=>[f,path.join(__dirname,f)]));sources['config.json']=configFile;
const sourceFilesSha256=Object.fromEntries(Object.entries(sources).map(([f,p])=>[f,sha(fs.readFileSync(p))]));
fs.mkdirSync(out,{recursive:true});for(const [name,file]of Object.entries(sources))fs.copyFileSync(file,path.join(out,name));
const pixels=(f,opt)=>{map.frame(f,opt);return Buffer.from(ctx.getImageData(0,0,1080,1080).data);};
const mad=(a,b)=>{let sum=0,n=0;for(let i=0;i<a.length;i++)if(i%4!==3){sum+=Math.abs(a[i]-b[i]);n++;}return sum/n/255;};
const a=pixels(0),end=pixels(599),middle=pixels(270),other=pixels(135),rawA=pixels(0,{unmasked:true}),rawEnd=pixels(599,{unmasked:true}),rawCycle=pixels(600,{unmasked:true});
const determinism=[];for(const f of [0,60,150,240,330,460,599]){let a=sha(pixels(f));pixels((f+197)%600);let b=sha(pixels(f));determinism.push({frame:f,sha256:a,repeatSha256:b,match:a===b});}
const e=.001,lines=map.worldMode==='scroll'?[river,road]:[map.riverCenter],period=map.worldMode==='scroll'?H:1080;
let topology=true;for(const fn of lines){topology&&=Math.abs(fn(0)-fn(period))<1e-8;topology&&=Math.abs((fn(e)-fn(-e))/(2*e)-(fn(period+e)-fn(period-e))/(2*e))<1e-6;}
const bg=map.colors.paper.slice(1).match(/../g).map(v=>parseInt(v,16));let count=0;for(let i=0;i<rawA.length;i+=4)if(Math.max(...bg.map((v,j)=>Math.abs(rawA[i+j]-v)))>20)count++;
const cameraLoop=map.worldMode==='scroll'||JSON.stringify(map.model(0).camera)===JSON.stringify(map.model(600).camera),checkOnly=process.argv.includes('--check-only');
const report={sourceSha256:sourceFilesSha256['map.js'],sourceFilesSha256,node:process.version,canvas:Canvas.version,resolvedConfig:map.config,worldMode:map.worldMode,colors:map.colors,cameraSamples:map.worldMode==='spatial'?[0,240,460,600].map(frame=>({frame,camera:map.model(frame).camera})):[],cameraLoop,width:1080,height:1080,fps:30,frames:600,threshold:12/255,seamMAD:mad(a,end),unmaskedSeamMAD:mad(rawA,rawEnd),cycleMAD:mad(rawA,rawCycle),deterministic:determinism.every(v=>v.match),determinism,topology,foregroundRatio:count/(rawA.length/4),motionMAD:mad(middle,other),cloudLayerHeight:map.worldMode==='scroll'?H*.55:null,mode:checkOnly?'check-only':'render',exportedFrames:0};
const save=()=>fs.writeFileSync(path.join(out,'seam-check.json'),JSON.stringify(report,null,2)+'\n');
report.passed=report.seamMAD<report.threshold&&report.unmaskedSeamMAD<report.threshold&&report.cycleMAD===0&&report.deterministic&&topology&&cameraLoop&&report.foregroundRatio>.1&&report.motionMAD>.005;
if(!report.passed){save();throw Error('接缝/相机/确定性/非空检查失败，见seam-check.json；禁止标记无缝通过');}
try{
 for(const f of [0,60,150,240,330,432,504,599]){map.frame(f);fs.writeFileSync(path.join(out,`preview-${f}.png`),canvas.toBuffer('image/png',{compressionLevel:1}));}
 map.frame(0,{unmasked:true});fs.writeFileSync(path.join(out,'preview-unmasked-0.png'),canvas.toBuffer('image/png',{compressionLevel:1}));
 if(!checkOnly){const start=Date.now(),dir=path.join(out,'frames');fs.mkdirSync(dir);for(let i=0;i<600;i++){map.frame(i);fs.writeFileSync(path.join(dir,`frame-${String(i).padStart(4,'0')}.png`),canvas.toBuffer('image/png',{compressionLevel:1}));report.exportedFrames++;if(i%100===0)console.log('frame',i);}report.renderWallSeconds=(Date.now()-start)/1000;}
 for(const [file,src]of Object.entries(sources))if(sha(fs.readFileSync(src))!==sourceFilesSha256[file])throw Error('导出期间绘图依赖/配置变化：'+file);
 save();
}catch(error){report.passed=false;report.error=error.message;save();throw error;}
console.log(JSON.stringify(report));
