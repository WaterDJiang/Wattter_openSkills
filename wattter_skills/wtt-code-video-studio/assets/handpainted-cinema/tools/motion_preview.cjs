/* Silent action window for art review, not a finalized movie or an automatic approval. */
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{execFileSync}=require('child_process');
const {createCanvas}=require(process.env.CANVAS_MODULE||'canvas'),root=path.resolve(__dirname,'..'),start=Number(process.argv[2]),count=Number(process.argv[3]),name=process.argv[4];
if(!Number.isInteger(start)||start<0||!Number.isInteger(count)||count<2||!name||!/^[a-zA-Z0-9][a-zA-Z0-9_-]*$/.test(name))throw Error('use motion_preview.cjs START_FRAME FRAME_COUNT NEW_DIR_NAME');
const out=path.join(root,name);if(fs.existsSync(out))throw Error('动作预览目录已存在，不覆盖');
const guard=()=>JSON.parse(execFileSync('python3',['-c','import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import asset_review;print(json.dumps(asset_review.guard_if_locked(Path(sys.argv[2]))))',__dirname,root],{encoding:'utf8'}));
const receipt=guard(),sha=b=>crypto.createHash('sha256').update(b).digest('hex'),sources=['scene.js','forest.js','courier.js','tools/motion_preview.cjs'],sourceSha256=Object.fromEntries(sources.map(f=>[f,sha(fs.readFileSync(path.join(root,f)))]));
const canvas=createCanvas(1920,1080),movie=require('../scene.js').make(canvas,createCanvas);if(start+count>movie.totalFrames)throw Error('动作窗口超过画面帧数；按本片事件重选');
const width=640,height=360,small=createCanvas(width,height),c=small.getContext('2d');fs.mkdirSync(out);
for(let i=0;i<count;i++){movie.frame(start+i);c.drawImage(canvas,0,0,width,height);fs.writeFileSync(path.join(out,`frame-${String(i).padStart(4,'0')}.png`),small.toBuffer('image/png',{compressionLevel:1}));}
execFileSync('ffmpeg',['-n','-v','error','-framerate',String(movie.fps),'-i',path.join(out,'frame-%04d.png'),'-frames:v',String(count),'-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,'action.mp4')]);
if(JSON.stringify(guard())!==JSON.stringify(receipt))throw Error('动作预览期间素材变化');for(const f of sources)if(sourceSha256[f]!==sha(fs.readFileSync(path.join(root,f))))throw Error('动作预览期间源码变化：'+f);
const media=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-of','json',path.join(out,'action.mp4')],{encoding:'utf8'})),v=media.streams.find(s=>s.codec_type==='video');if(Number(v.nb_frames)!==count||v.width!==width||v.height!==height||Math.abs(Number(v.duration)-count/movie.fps)>.05)throw Error('实际动作片段参数不符');
execFileSync('ffmpeg',['-v','error','-i',path.join(out,'action.mp4'),'-f','null','-'],{stdio:'pipe'});
fs.writeFileSync(path.join(out,'motion-preview.json'),JSON.stringify({mode:'silent-motion-preview',startFrame:start,endFrame:start+count,totalFrames:count,fps:movie.fps,width,height,assetReview:receipt,sourceSha256,videoSha256:sha(fs.readFileSync(path.join(out,'action.mp4'))),visualReview:'pending; 不是正式成片验收',node:process.version,canvas:require(process.env.CANVAS_MODULE||'canvas').version},null,2)+'\n');console.log(out);
