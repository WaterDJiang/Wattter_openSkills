/* Preview first. A full export consumes the exact approved snapshot, never a rebuilt approval. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{execFileSync}=require('node:child_process');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const value=(flag,fallback)=>{const at=process.argv.indexOf(flag);if(at<0)return fallback;const v=process.argv[at+1];if(!v||v.startsWith('--'))throw Error(flag+'须指定值');return v;};
const out=path.resolve(value('--out',''));if(!process.argv.includes('--out'))throw Error('use --out NEW_DIRECTORY [--config FILE] [--check-only | --render-approved]');
const render=process.argv.includes('--render-approved'),checkOnly=process.argv.includes('--check-only');if(render&&checkOnly)throw Error('--render-approved与--check-only互斥');
const helperIn=process.env.PREVIEW_REVIEW_TOOL||[path.join(__dirname,'preview_review.py'),path.resolve(__dirname,'../../scripts/preview_review.py')].find(p=>fs.existsSync(p));
if(!helperIn)throw Error('缺少共用preview_review.py；从完整Skill运行，或设置PREVIEW_REVIEW_TOOL后复制到新工程');
const names=['map.js','world.js','legacy-scroll.js','presentation.js','export.cjs','index.html'];
let saved;
if(render){
 if(!fs.existsSync(out))throw Error('先生成四张样帧拼图并取得用户确认，再--render-approved');
 saved=JSON.parse(fs.readFileSync(path.join(out,'seam-check.json')));
 if(fs.existsSync(path.join(out,'frames')))throw Error('完整帧目录已存在，不能覆盖；使用原样复用或新的候选版本');
 // If called from the template, current requested code/config must still be the approved snapshot.
 for(const name of names)if(sha(fs.readFileSync(path.join(__dirname,name)))!==saved.sourceFilesSha256[name])throw Error('源码已变化，四帧批准失效：'+name+'；创建新的候选预览目录');
 const configArg=value('--config',null);if(configArg&&sha(fs.readFileSync(path.resolve(configArg)))!==saved.sourceFilesSha256['config.json'])throw Error('配置已变化，四帧批准失效；先生成新候选拼图');
}else{
 if(fs.existsSync(out))throw Error('输出必须是新目录；已锁项目只能向候选目录导出，不覆盖作品');
 const configFile=path.resolve(value('--config',path.join(__dirname,'config.json')));
 // Resolve before creating an output: malformed config must not create a seemingly usable project.
 require('./map.js').resolve(JSON.parse(fs.readFileSync(configFile)));
 fs.mkdirSync(out,{recursive:true});for(const name of names)fs.copyFileSync(path.join(__dirname,name),path.join(out,name));fs.copyFileSync(configFile,path.join(out,'config.json'));fs.copyFileSync(helperIn,path.join(out,'preview_review.py'));
}
const helper=path.join(out,'preview_review.py');
const approval=render?JSON.parse(execFileSync(process.env.PYTHON||'python3',[helper,'check',out,'--kind','map'],{encoding:'utf8'})):null;
const Canvas=require(process.env.CANVAS_MODULE||'canvas'),{createCanvas}=Canvas,{make,river,road,H}=require(path.join(out,'map.js'));
const config=JSON.parse(fs.readFileSync(path.join(out,'config.json'))),canvas=createCanvas(1080,1080),map=make(canvas,config),ctx=canvas.getContext('2d'),N=map.config.frames,fps=map.config.fps;
const sourceNames=[...names,'config.json','preview_review.py'],sourceFilesSha256=Object.fromEntries(sourceNames.map(f=>[f,sha(fs.readFileSync(path.join(out,f)))]));
if(saved)for(const name of sourceNames)if(sourceFilesSha256[name]!==saved.sourceFilesSha256[name])throw Error('批准后快照已变化：'+name);
const pixels=(f,opt)=>{map.frame(f,opt);return Buffer.from(ctx.getImageData(0,0,1080,1080).data);};
const mad=(a,b)=>{let sum=0,n=0;for(let i=0;i<a.length;i++)if(i%4!==3){sum+=Math.abs(a[i]-b[i]);n++;}return sum/n/255;};
const a=pixels(0),end=pixels(N-1),middle=pixels(Math.round(N*.45)),other=pixels(Math.round(N*.225)),rawA=pixels(0,{unmasked:true}),rawEnd=pixels(N-1,{unmasked:true}),rawCycle=pixels(N,{unmasked:true});
const determinism=[];for(const f of [0,.10,.25,.40,.55,.77,1].map(x=>Math.round(x*(N-1)))){let a=sha(pixels(f));pixels((f+Math.round(N*.328))%N);let b=sha(pixels(f));determinism.push({frame:f,sha256:a,repeatSha256:b,match:a===b});}
const e=.001,lines=map.worldMode==='scroll'?[river,road]:[map.riverCenter],period=map.worldMode==='scroll'?H:1080;
let topology=true;for(const fn of lines){topology&&=Math.abs(fn(0)-fn(period))<1e-8;topology&&=Math.abs((fn(e)-fn(-e))/(2*e)-(fn(period+e)-fn(period-e))/(2*e))<1e-6;}
const bg=map.colors.paper.slice(1).match(/../g).map(v=>parseInt(v,16));let count=0;for(let i=0;i<rawA.length;i+=4)if(Math.max(...bg.map((v,j)=>Math.abs(rawA[i+j]-v)))>20)count++;
const cameraLoop=map.worldMode==='scroll'||JSON.stringify(map.model(0).camera)===JSON.stringify(map.model(N).camera);
const report={sourceSha256:sourceFilesSha256['map.js'],sourceFilesSha256,node:process.version,canvas:Canvas.version,resolvedConfig:map.config,worldMode:map.worldMode,colors:map.colors,visualMechanisms:map.visualMechanisms||{},events:map.events||[],cameraSamples:map.worldMode==='spatial'?[0,.40,.77,1].map(x=>{const frame=Math.round(x*N);return{frame,camera:map.model(frame).camera};}):[],cameraLoop,width:1080,height:1080,fps,frames:N,durationSeconds:N/fps,threshold:12/255,seamMAD:mad(a,end),unmaskedSeamMAD:mad(rawA,rawEnd),cycleMAD:mad(rawA,rawCycle),deterministic:determinism.every(v=>v.match),determinism,topology,foregroundRatio:count/(rawA.length/4),motionMAD:mad(middle,other),cloudLayerHeight:map.worldMode==='scroll'?H*.55:null,mode:render?'render':checkOnly?'check-only':'preview',exportedFrames:0,fullRenderAllowed:false,previewReview:saved?.previewReview||null};
const save=()=>fs.writeFileSync(path.join(out,'seam-check.json'),JSON.stringify(report,null,2)+'\n');
report.passed=report.seamMAD<report.threshold&&report.unmaskedSeamMAD<report.threshold&&report.cycleMAD===0&&report.deterministic&&topology&&cameraLoop&&report.foregroundRatio>.1&&report.motionMAD>.005;
if(!report.passed){save();throw Error('接缝/相机/确定性/非空检查失败，见seam-check.json；禁止标记无缝通过');}
try{
 if(render){
  if(!Array.isArray(approval.frameIndices)||approval.frameIndices.length!==4)throw Error('批准回执缺少四个帧号；禁止完整渲染');
  const verifyDir=fs.mkdtempSync(path.join(out,'.preview-review','map-verification-'));
  const verified=approval.frameIndices.map(frame=>{map.frame(frame);const file=path.relative(out,path.join(verifyDir,`frame-${String(frame).padStart(6,'0')}.png`));fs.writeFileSync(path.join(out,file),canvas.toBuffer('image/png',{compressionLevel:1}));return{frame,file};});
  const requestFile=path.join(verifyDir,'request.json');fs.writeFileSync(requestFile,JSON.stringify({frames:verified},null,2)+'\n');
  report.fullRenderVerification=JSON.parse(execFileSync(process.env.PYTHON||'python3',[helper,'check',out,'--kind','map','--request',requestFile],{encoding:'utf8'}));
  report.fullRenderAllowed=true;
  const start=Date.now(),dir=path.join(out,'frames');fs.mkdirSync(dir);for(let i=0;i<N;i++){map.frame(i);fs.writeFileSync(path.join(dir,`frame-${String(i).padStart(4,'0')}.png`),canvas.toBuffer('image/png',{compressionLevel:1}));report.exportedFrames++;if(i%(fps*2)===0)console.log('frame',i+'/'+N);}report.renderWallSeconds=(Date.now()-start)/1000;
 }
 else{
  const chosen=value('--review-frames',null),frames=chosen?chosen.split(',').map(Number):[.15,.38,.64,.86].map(x=>Math.round(x*N));if(frames.length!==4||new Set(frames).size!==4||frames.some(i=>!Number.isInteger(i)||i<0||i>=N))throw Error('--review-frames须为片内4个不同整数帧');
  const images=frames.map(frame=>{map.frame(frame);const file=`preview-${String(frame).padStart(6,'0')}.png`;fs.writeFileSync(path.join(out,file),canvas.toBuffer('image/png',{compressionLevel:1}));return{frame,file};});
  map.frame(0,{unmasked:true});fs.writeFileSync(path.join(out,'preview-unmasked-0.png'),canvas.toBuffer('image/png',{compressionLevel:1}));
  const request={kind:'map',fps,totalFrames:N,width:1080,height:1080,sourceSha256:sourceFilesSha256,frames:images};fs.writeFileSync(path.join(out,'preview-request.json'),JSON.stringify(request,null,2)+'\n');
  const receipt=JSON.parse(execFileSync(process.env.PYTHON||'python3',[helper,'prepare',out,'--request',path.join(out,'preview-request.json')],{encoding:'utf8'}));report.previewReview=receipt;
  fs.writeFileSync(path.join(out,'sound-events.json'),JSON.stringify({schema:'postcard-sound-events/v1',fps,durationSeconds:N/fps,events:map.events||[],basis:'由同一个model/绝对帧事件表产生；原创合成音效，非当地实录'},null,2)+'\n');
 }
 for(const file of sourceNames)if(sha(fs.readFileSync(path.join(out,file)))!==sourceFilesSha256[file])throw Error('导出期间绘图依赖/配置变化：'+file);
 save();
}catch(error){report.passed=false;report.fullRenderAllowed=false;report.error=error.message;save();throw error;}
console.log(JSON.stringify(report));
