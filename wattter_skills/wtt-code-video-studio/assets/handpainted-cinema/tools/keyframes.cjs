/* Art-only preview before sound selection. Locked projects still use the shared asset guard. */
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{execFileSync}=require('child_process');
const {createCanvas}=require(process.env.CANVAS_MODULE||'canvas'),root=path.resolve(__dirname,'..'),name=process.argv[2]||'art-v001';
if(!/^[a-zA-Z0-9][a-zA-Z0-9_-]*$/.test(name))throw Error('预览名须为项目内的新目录名');const out=path.join(root,name);if(fs.existsSync(out))throw Error('预览目录已存在，不覆盖');
const guard=()=>JSON.parse(execFileSync('python3',['-c','import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import asset_review;print(json.dumps(asset_review.guard_if_locked(Path(sys.argv[2]))))',__dirname,root],{encoding:'utf8'}));
const receipt=guard(),sha=b=>crypto.createHash('sha256').update(b).digest('hex'),names=['scene.js','forest.js','courier.js','tools/keyframes.cjs'],sourceSha256=Object.fromEntries(names.map(f=>[f,sha(fs.readFileSync(path.join(root,f)))]));
const cv=createCanvas(1920,1080),c=cv.getContext('2d'),movie=require('../scene.js').make(cv,createCanvas);fs.mkdirSync(out);const frames=[];
for(const i of [0,45,147,184,185,270,359]){movie.frame(i);const file=`frame-${String(i).padStart(4,'0')}.png`;frames.push({frame:i,file,pixelSha256:sha(Buffer.from(c.getImageData(0,0,1920,1080).data))});fs.writeFileSync(path.join(out,file),cv.toBuffer('image/png',{compressionLevel:1}));}
if(JSON.stringify(guard())!==JSON.stringify(receipt))throw Error('绘制期间素材变化');for(const f of names)if(sourceSha256[f]!==sha(fs.readFileSync(path.join(root,f))))throw Error('绘制期间源码变化：'+f);
fs.writeFileSync(path.join(out,'art-preview.json'),JSON.stringify({mode:'art-preview',assetReview:receipt,sourceSha256,frames,visualReview:'pending; 静帧不是动作或艺术评分',node:process.version,canvas:require(process.env.CANVAS_MODULE||'canvas').version},null,2)+'\n');console.log(out);
