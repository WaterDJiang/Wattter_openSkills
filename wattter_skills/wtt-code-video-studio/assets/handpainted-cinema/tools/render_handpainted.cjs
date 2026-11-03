/* Actual single-film renderer. Asset and timeline guards are the existing skill tools. */
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{execFileSync}=require('child_process');
const canvasModule=require(process.env.CANVAS_MODULE||'canvas'),{createCanvas}=canvasModule;
const root=path.resolve(process.argv[2]||'.'),full=process.argv.includes('--render');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),sha=f=>hash(fs.readFileSync(f));
function check(){return JSON.parse(execFileSync('python3',[path.join(__dirname,'asset_review.py'),'check',root],{encoding:'utf8'}));}
const receipt=check(),timeline=JSON.parse(fs.readFileSync(path.join(root,'timeline.json')));execFileSync('python3',[path.join(__dirname,'pipeline.py'),'check',root]);
const sourceFiles=['scene.js','forest.js','courier.js','film.json','tools/render_handpainted.cjs','timeline.json'],sourceSha256=Object.fromEntries(sourceFiles.map(f=>[f,sha(path.join(root,f))]));
const {width:W,height:H,totalFrames:N,fps}=timeline,canvas=createCanvas(W,H),c=canvas.getContext('2d'),movie=require(path.join(root,'scene.js')).make(canvas,createCanvas);
if(movie.width!==W||movie.height!==H||movie.totalFrames!==N||movie.fps!==fps)throw Error('Scene and locked timeline do not agree');
const raw=f=>{movie.frame(f);return Buffer.from(c.getImageData(0,0,W,H).data);};
function mad(a,b){let s=0,n=0;for(let k=0;k<a.length;k++)if(k%4!==3){s+=Math.abs(a[k]-b[k]);n++;}return s/n/255;}
const out=path.join(root,full?'preview-final':'preview-v001');if(fs.existsSync(out))throw Error('预览目录已存在；保留旧结果，另设版本');fs.mkdirSync(out);
for(const f of [0,30,60,90,120,150,180,184,185,186,210,240,270,300,330,359]){movie.frame(f);fs.writeFileSync(path.join(out,`frame-${String(f).padStart(6,'0')}.png`),canvas.toBuffer('image/png',{compressionLevel:1}));}
const determinism=[];for(const f of [0,45,147,184,185,270,359]){let a=hash(raw(f));raw((f+157)%N);let b=hash(raw(f));determinism.push({frame:f,sha256:a,repeatSha256:b,match:a===b});}
const motionMAD=mad(raw(30),raw(210));if(determinism.some(v=>!v.match)||motionMAD<.005)throw Error('乱序一致性/运动像素检查失败');
// A numeric attachment check complements (does not replace) actual pose review.
const rig=[];for(const f of [0,90,120,150,180,184]){let s=movie.state(f/fps),p=movie.birdPoint(s);let expected=[s.x+(s.wrist[0]+14)*s.scale,s.y+(s.wrist[1]-13)*s.scale];rig.push({frame:f,held:true,wrist:s.wrist,birdAnchor:p,attachmentErrorPixels:Math.hypot(...p.map((v,j)=>v-expected[j]))});}
const report={renderer:'node-canvas',node:process.version,canvas:canvasModule.version,mode:full?'render':'preview',assetReview:receipt,timelineSha256:sha(path.join(root,'timeline.json')),totalFrames:N,durationSeconds:N/fps,sourceSha256,determinism,motionMAD,rig,loop:false,visualReview:'pending-image-and-motion-inspection'};
if(full){let frames=path.join(root,'frames');if(fs.existsSync(frames))throw Error('frames目录已存在，禁止覆盖旧渲染');fs.mkdirSync(frames);let start=Date.now();for(let i=0;i<N;i++){movie.frame(i);fs.writeFileSync(path.join(frames,`frame-${String(i).padStart(4,'0')}.png`),canvas.toBuffer('image/png',{compressionLevel:1}));if(i%60===0)console.log(`render ${i}/${N}`);}
 execFileSync('ffmpeg',['-n','-v','error','-framerate',String(fps),'-i',path.join(frames,'frame-%04d.png'),'-frames:v',String(N),'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',path.join(root,'silent.mp4')]);report.renderWallSeconds=(Date.now()-start)/1000;report.videoSha256=sha(path.join(root,'silent.mp4'));}
if(JSON.stringify(check())!==JSON.stringify(receipt))throw Error('渲染期间素材变化');for(const[f,h]of Object.entries(sourceSha256))if(sha(path.join(root,f))!==h)throw Error('渲染期间源码变化');
fs.writeFileSync(path.join(root,full?'render-report.json':'preview-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({determinism:determinism.every(v=>v.match),motionMAD,full}));
