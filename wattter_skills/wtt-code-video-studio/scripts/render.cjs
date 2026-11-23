#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const {createRequire} = require('node:module');
const {spawn, execFileSync} = require('node:child_process');
const {once} = require('node:events');
const root = path.resolve(process.argv[2] || '.');
const sampleFlag = process.argv.indexOf('--sample-frames');
const mode = process.argv.includes('--render') ? 'render' : sampleFlag >= 0 ? 'sample' : 'preview';
const formatFlag = process.argv.indexOf('--frame-format');
const frameFormat = formatFlag < 0 ? 'png' : process.argv[formatFlag + 1];
const reviewFlag = process.argv.indexOf('--review-frames');
let previewApproval;
function reviewTool(command, extra=[]) {
  return JSON.parse(execFileSync(process.env.PYTHON || 'python3', [path.join(__dirname,'preview_review.py'),command,root,...extra], {encoding:'utf8'}));
}
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const fileHash = p => hash(fs.readFileSync(p));
const errors = [], sourceSha256 = {};
let browser, encoder, server;

function materialCheck() {
  return JSON.parse(execFileSync(process.env.PYTHON || 'python3', [path.join(__dirname, 'asset_review.py'), 'check', root], {encoding:'utf8'}));
}

function sampleRange(timeline) {
  const match = /^(\d+):(\d+)$/.exec(process.argv[sampleFlag + 1] || '');
  if (!match) throw Error('--sample-frames 需要起帧:止帧，例如 240:432，止帧不含');
  const [start, end] = match.slice(1).map(Number);
  if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start >= end || end > timeline.totalFrames) {
    throw Error('试剪帧区间为空或超出锁定时间轴');
  }
  if (start === 0 && end === timeline.totalFrames) throw Error('全片须走 --render 和四帧审批');
  return {start, end};
}

function checkedMix(assetReview, timelineSha256) {
  const mixFile = path.join(root, 'audio/mix-master.wav');
  const receipt = JSON.parse(fs.readFileSync(path.join(root, 'audio/mix-report.json')));
  if (receipt.assetReview?.manifestSha256 !== assetReview.manifestSha256
      || receipt.assetReview?.version !== assetReview.version
      || receipt.timelineSha256 !== timelineSha256 || receipt.mixSha256 !== fileHash(mixFile)) {
    throw Error('试剪混音已过期，请先运行 pipeline.py mix');
  }
  return receipt.mixSha256;
}

async function encodeFrames(grab, timeline, start, end, target, logFile, audioArgs = []) {
  const log = fs.openSync(logFile, 'w');
  try {
    encoder = spawn('ffmpeg', [
      '-y','-hide_banner','-loglevel','warning','-f','image2pipe','-vcodec',
      frameFormat==='jpeg'?'mjpeg':'png','-framerate',String(timeline.fps),'-i','pipe:0',
      ...(audioArgs.length ? audioArgs : ['-an']),
      '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',target
    ], {stdio:['pipe','ignore',log]});
    let encoderError;
    const done = new Promise((resolve,reject)=>{
      encoder.on('error',reject);
      encoder.on('close',code=>code===0?resolve():reject(Error(`FFmpeg exit ${code}，见 ${logFile}`)));
      encoder.stdin.on('error',reject);
    });
    done.catch(e=>{encoderError=e;});
    const begun = Date.now();
    for (let f=start; f<end; f++) {
      if (encoderError) throw encoderError;
      const data=await grab(f,frameFormat);
      if (!encoder.stdin.write(data)) await Promise.race([once(encoder.stdin,'drain'),done.then(()=>{throw Error('编码器提前退出');})]);
      if ((f-start) % (timeline.fps*2) === 0) console.log(`${mode} ${f-start}/${end-start} · ${((Date.now()-begun)/1000).toFixed(1)}s`);
      if (errors.length) throw Error(errors.join('\n'));
    }
    encoder.stdin.end(); await done;
    return (Date.now()-begun)/1000;
  } finally { fs.closeSync(log); }
}

async function exportSample(grab, t, range, assetReview, timelineSha256, mixSha256) {
  const {start, end} = range;
  const samples = path.join(root, 'preview', 'samples');
  fs.mkdirSync(samples, {recursive:true});
  const folder = fs.mkdtempSync(path.join(samples, `frames-${start}-${end}-`));
  const partial = path.join(folder, 'sample.partial.mp4');
  const mixFile = path.join(root, 'audio/mix-master.wav');
  // The mixer writes one fixed 48 kHz PCM timeline. Slice it at the same frame boundaries.
  const firstSample = Math.round(start * 48000 / t.fps);
  const endSample = Math.round(end * 48000 / t.fps);
  const audioArgs = ['-i',mixFile,'-map','0:v:0','-map','1:a:0',
    '-af',`atrim=start_sample=${firstSample}:end_sample=${endSample},asetpts=PTS-STARTPTS`,
    '-c:a','aac','-b:a','160k'];
  await encodeFrames(grab, t, start, end, partial, path.join(folder,'ffmpeg.log'), audioArgs);
  const info=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-of','json',partial],{encoding:'utf8'}));
  const video=info.streams.find(s=>s.codec_type==='video');
  const audio=info.streams.find(s=>s.codec_type==='audio');
  const duration=(end-start)/t.fps;
  if (Number(video?.nb_frames)!==end-start || video.width!==t.width || video.height!==t.height
      || audio?.codec_name!=='aac' || !(Math.abs(Number(audio.duration)-duration)<=1/t.fps)) {
    throw Error('试剪音画时长或帧数不符');
  }
  if (materialCheck().manifestSha256 !== assetReview.manifestSha256
      || fileHash(path.join(root,'timeline.json')) !== timelineSha256
      || fileHash(path.join(root,'film.json')) !== t.filmSha256
      || checkedMix(assetReview, timelineSha256) !== mixSha256
      || Object.entries(sourceSha256).some(([file, sha]) => fileHash(path.join(root,file)) !== sha)) {
    throw Error('试剪期间输入发生变化，请重新试剪');
  }
  const report = {mode:'sample', startFrame:start, endFrameExclusive:end, fps:t.fps, totalFrames:end-start,
    durationSeconds:duration, assetReview, timelineSha256, mixSha256, sourceSha256, videoSha256:fileHash(partial)};
  fs.writeFileSync(path.join(folder,'sample-report.json'),JSON.stringify(report,null,2)+'\n');
  const output=path.join(folder,'sample.mp4');
  fs.renameSync(partial,output);
  console.log(`有声试剪：${output}`);
}

async function main() {
  if(!['png','jpeg'].includes(frameFormat)) throw Error('--frame-format 必须为 png 或 jpeg');
  if (sampleFlag >= 0 && (mode !== 'sample' || reviewFlag >= 0 || process.argv.includes('--preview'))) {
    throw Error('--sample-frames 单独运行；四帧预览和完整渲染请另用对应命令');
  }
  const assetReview = materialCheck();
  const film = JSON.parse(fs.readFileSync(path.join(root,'film.json')));
  if (film.footageManifest) execFileSync(process.env.PYTHON || 'python3', [path.join(__dirname,'footage.py'),'check',root], {stdio:'inherit'});
  const assetSelection = JSON.parse(fs.readFileSync(path.join(root,'assets.json')));
  const view = JSON.parse(execFileSync(process.env.PYTHON || 'python3', [path.join(__dirname,'asset_review.py'),'view',root], {encoding:'utf8'}));
  const approved = new Map(view.selection.assets.map(a=>[a.path,a.sha256]));
  const approvedLinks = new Set([...assetSelection.links.map(a=>a.url), ...assetSelection.assets.map(a=>a.landingUrl).filter(Boolean)].map(u=>new URL(u).href));
  const t = JSON.parse(fs.readFileSync(path.join(root, 'timeline.json')));
  const range = mode === 'sample' ? sampleRange(t) : null;
  const timelineSha256 = range ? fileHash(path.join(root, 'timeline.json')) : null;
  const mixSha256 = range ? checkedMix(assetReview, timelineSha256) : null;
  if (range) execFileSync(process.env.PYTHON || 'python3', [path.join(__dirname, 'pipeline.py'),'check',root], {stdio:'inherit'});
  if (mode === 'render') {
    execFileSync(process.env.PYTHON || 'python3', [path.join(__dirname, 'pipeline.py'), 'check', root], {stdio: 'inherit'});
    previewApproval=reviewTool('check',['--kind','pipeline']);
  }
  if (t.assetReview?.version!==assetReview.version || t.assetReview?.manifestSha256!==assetReview.manifestSha256) throw Error('时间轴未绑定当前素材锁；重新编译时间轴');
  if (t.filmSha256 !== fileHash(path.join(root, 'film.json'))) throw Error('film.json 已变化；重新编译时间轴');
  let playwright;
  try { playwright = createRequire(path.join(root, 'package.json'))('playwright'); }
  catch (e) {
    if (!process.env.PLAYWRIGHT_MODULE) throw Error('缺少 Playwright；在项目中安装 playwright 或设置 PLAYWRIGHT_MODULE');
    playwright = require(process.env.PLAYWRIGHT_MODULE);
  }
  const mime = {'.html':'text/html', '.css':'text/css', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.webp':'image/webp', '.js':'application/javascript', '.json':'application/json', '.wav':'audio/wav', '.mp3':'audio/mpeg', '.svg':'image/svg+xml', '.png':'image/png', '.woff2':'font/woff2'};
  server = http.createServer((req, res) => {
    try {
      const name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      const file = path.resolve(root, '.' + (name === '/' ? '/index.html' : name));
      if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile() || !fs.realpathSync(file).startsWith(fs.realpathSync(root) + path.sep)) { res.writeHead(404).end(); return; }
      const relative=path.relative(root,file).split(path.sep).join('/');
      if (relative.startsWith('.asset-review/') || relative.startsWith('.voice-local/')) {res.writeHead(403).end();return;}
      const isCode = !relative.includes('/') && ['.html','.js','.css'].includes(path.extname(relative)) || relative.startsWith('code/') && ['.js','.css','.html'].includes(path.extname(relative));
      const isControl = ['timeline.json','assets.json'].includes(relative);
      const isMix = relative==='audio/mix-master.wav';
      if (!approved.has(relative) && !isCode && !isControl && !isMix) {errors.push(`未登记的素材请求：${relative}`);res.writeHead(403).end();return;}
      const data = fs.readFileSync(file);
      if (approved.has(relative) && hash(data)!==approved.get(relative)) {errors.push(`素材在渲染中变化：${relative}`);res.writeHead(409).end();return;}
      if (isMix) {
        const mix=JSON.parse(fs.readFileSync(path.join(root,'audio/mix-report.json')));
        if(mix.assetReview?.manifestSha256!==assetReview.manifestSha256 || mix.mixSha256!==hash(data)) {errors.push('混音版本/哈希不符');res.writeHead(409).end();return;}
      }
      const digest = hash(data);
      if (range && sourceSha256[relative] && sourceSha256[relative] !== digest) {
        errors.push(`试剪期间源文件变化：${relative}`);res.writeHead(409).end();return;
      }
      sourceSha256[relative] = digest;
      res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
      res.end(data);
    } catch { res.writeHead(400).end(); }
  });
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  const mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  const executablePath = process.env.CHROME_PATH || (fs.existsSync(mac) ? mac : undefined);
  browser = await playwright.chromium.launch({executablePath, headless:true});
  const page = await browser.newPage({viewport:{width:t.width, height:t.height}, deviceScaleFactor:1});
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', e => { if(e.type() === 'error') errors.push(e.text()); });
  page.on('requestfailed', r => errors.push(`${r.url()} ${r.failure()?.errorText}`));
  page.on('response', r => { if(r.status() >= 400) errors.push(`HTTP ${r.status()} ${r.url()}`); });
  const origin=`http://127.0.0.1:${server.address().port}`;
  await page.route('**/*', route=>{
    if(new URL(route.request().url()).origin!==origin){errors.push(`禁止未锁定远程资源：${route.request().url()}`);return route.abort();}
    const relative=decodeURIComponent(new URL(route.request().url()).pathname.slice(1));
    if(['image','font','media'].includes(route.request().resourceType()) && !approved.has(relative) && relative!=='audio/mix-master.wav'){errors.push(`媒体未登记：${relative}`);return route.abort();}
    return route.continue();
  });
  const checkLinks = async()=>{
    const links=await page.evaluate(()=>[...document.querySelectorAll('a[href],area[href],form[action]')].map(e=>e.href||e.action));
    for(const link of links){if(new URL(link).origin!==origin && !approvedLinks.has(new URL(link).href)){
      execFileSync(process.env.PYTHON || 'python3',[path.join(__dirname,'asset_review.py'),'observe',root,'--url',link],{stdio:'inherit'});
      throw Error(`网页导流未在锁定清单中：${link}`);
    }}
  };
  await page.goto(`${origin}/?export=1`, {waitUntil:'load'});
  await page.waitForFunction(() => window.__ready === true, null, {timeout:30000});
  await page.evaluate(() => document.fonts.ready);
  const meta = await page.evaluate(() => window.__filmMeta);
  if (!meta || ['width','height','fps','totalFrames'].some(k => meta[k] !== t[k])) throw Error('页面 __filmMeta 与时间轴不符');
  const stage = page.locator('#stage');
  const bounds=await stage.boundingBox();
  if(!bounds || Math.abs(bounds.width-t.width)>.1 || Math.abs(bounds.height-t.height)>.1) throw Error('#stage 实际尺寸与时间轴不符；检查样式加载与缩放');
  let grabbedFrames=0;
  const previewStarted=Date.now();
  const grab = async (frame, format='png') => {
    grabbedFrames++;
    await page.evaluate(async f => { await window.renderFrame(f); }, frame);
    await checkLinks();
    return stage.screenshot({type:format, ...(format==='jpeg'?{quality:95}:{}), animations:'allow'});
  };
  if (range) return exportSample(grab, t, range, assetReview, timelineSha256, mixSha256);
  let preview = path.join(root, 'preview');
  if(mode==='render'){
    const candidates=path.join(root,'.preview-review','candidates');fs.mkdirSync(candidates,{recursive:true});
    const ids=fs.readdirSync(candidates).filter(x=>/^render-\d+$/.test(x)).map(x=>Number(x.slice(7)));
    preview=path.join(candidates,`render-${String(Math.max(0,...ids)+1).padStart(4,'0')}`);
  }
  fs.mkdirSync(preview, {recursive:true});
  // Boundaries plus each scene midpoint: review cuts, captions and representative poses.
  const quadFrames=reviewFlag<0?(previewApproval?.frameIndices||[.08,.35,.65,.92].map(x=>Math.min(t.totalFrames-1,Math.floor(x*t.totalFrames)))):String(process.argv[reviewFlag+1]||'').split(',').map(v=>Number(v));
  if(t.totalFrames<4 || quadFrames.length!==4 || new Set(quadFrames).size!==4 || quadFrames.some(f=>!Number.isInteger(f)||f<0||f>=t.totalFrames)) throw Error('--review-frames须为四个不同且未越界的整数帧号，如20,90,170,260');
  const samples = new Set([0, t.totalFrames - 1,...quadFrames]);
  for (const s of t.scenes) for (const f of [s.startFrame, s.startFrame + Math.floor(s.durationFrames / 2), s.endFrame - 1]) samples.add(f);
  for (const c of t.captions) samples.add(Math.floor((c.startFrame + c.endFrame - 1) / 2));
  // Beat grid is sampled for long clips; every declared action gets before/on/after evidence.
  const beatFrames=(t.rhythm?.beats||[]).map(b=>b.frame);
  const beatSamples=[...new Set(beatFrames.length<=64?beatFrames:Array.from({length:64},(_,i)=>beatFrames[Math.round(i*(beatFrames.length-1)/63)]))];
  for(const f of beatSamples)samples.add(f);
  for(const e of t.rhythm?.events||[])for(const f of [e.frame-1,e.frame,e.frame+1])if(f>=0&&f<t.totalFrames)samples.add(f);
  const loopFrames=t.loop?[...new Set([0,1,2,t.totalFrames-3,t.totalFrames-2,t.totalFrames-1].filter(f=>f>=0&&f<t.totalFrames))]:[];
  for(const f of loopFrames)samples.add(f);
  for (const f of [...samples].sort((a,b)=>a-b)) fs.writeFileSync(path.join(preview, `frame-${String(f).padStart(6,'0')}.png`), await grab(f));
  const determinism = [];
  const tests = [...new Set([0, .19, .47, .79, 1].map(x=>Math.round(x*(t.totalFrames-1))))];
  for (const f of tests) {
    const a = hash(await grab(f)); await grab((f + Math.floor(t.totalFrames * .37) + 1) % t.totalFrames);
    const b = hash(await grab(f)); determinism.push({frame:f, sha256:a, repeatSha256:b, match:a===b});
  }
  if (errors.length || determinism.some(c=>!c.match)) throw Error(JSON.stringify({errors,determinism}));
  const previewWallSeconds=(Date.now()-previewStarted)/1000;
  const sampleFrames=[...samples].sort((a,b)=>a-b);
  const previewCoverage={sampleFrames,beatCount:beatFrames.length,beatSampleCount:beatSamples.length,
    eventCount:(t.rhythm?.events||[]).length,loopFrames,
    loopStatus:t.loop?'sampled-needs-motion-and-audio-review':'not-requested'};
  const previewPerformance={wallSeconds:previewWallSeconds,screenshotCalls:grabbedFrames,
    estimatedRenderSeconds:previewWallSeconds/Math.max(1,grabbedFrames)*t.totalFrames,
    estimateScope:'画面截图粗估；不含浏览器启动、完整编码与混音，不是完成时间承诺'};
  fs.writeFileSync(path.join(preview,'index.html'),'<!doctype html><meta charset="utf-8"><title>逐帧审阅</title><style>body{background:#eee;font:14px system-ui}main{display:flex;flex-wrap:wrap;gap:12px}figure{margin:0;background:white;padding:8px}img{max-width:320px;height:auto}</style><h1>逐帧审阅</h1><p>抽样证据不等于观感通过；检查事件前后、文字和循环接缝。</p><main>'+sampleFrames.map(f=>`<figure><img loading="lazy" src="frame-${String(f).padStart(6,'0')}.png"><figcaption>帧 ${f} · ${(f/t.fps).toFixed(3)}s</figcaption></figure>`).join('')+'</main>');
  const report = {mode, frameEncoding:{format:frameFormat,quality:frameFormat==='jpeg'?95:null,preview:'png'}, assetReview, previewCoverage, previewPerformance, timelineSha256:fileHash(path.join(root,'timeline.json')), browser:browser.version(),
    totalFrames:t.totalFrames, durationSeconds:t.durationSeconds, determinism, browserErrors:errors, sourceSha256, ...(previewApproval?{previewReview:previewApproval}:{})};
  if (mode === 'render') {
    const requestFile=path.join(preview,'review-request.json');
    fs.writeFileSync(requestFile,JSON.stringify({frames:quadFrames.map(frame=>({frame,file:path.relative(root,path.join(preview,`frame-${String(frame).padStart(6,'0')}.png`))}))},null,2)+'\n');
    const resampled=reviewTool('check',['--kind','pipeline','--request',requestFile]);
    if(JSON.stringify(resampled)!==JSON.stringify(previewApproval))throw Error('整片导出前四帧批准变化；停止渲染');
    report.renderWallSeconds=await encodeFrames(grab,t,0,t.totalFrames,path.join(root,'silent.mp4'),path.join(root,'render-ffmpeg.log'));
    report.videoSha256=fileHash(path.join(root,'silent.mp4'));
  }
  if(mode==='render'){
    const finalApproval=reviewTool('check',['--kind','pipeline']);
    if(JSON.stringify(finalApproval)!==JSON.stringify(previewApproval)) throw Error('渲染期间四帧批准变化；不能验收');
  }
  const finalAssets=materialCheck();
  if(finalAssets.manifestSha256!==assetReview.manifestSha256) throw Error('渲染期间素材版本变化；不能验收');
  if(errors.length) throw Error(errors.join('\n'));
  fs.writeFileSync(path.join(root, mode==='render'?'render-report.json':'preview-report.json'), JSON.stringify(report,null,2)+'\n');
  if(mode==='preview'){
    const bound={...sourceSha256};
    const add=file=>{if(fs.existsSync(file)&&fs.statSync(file).isFile())bound[path.relative(root,file).split(path.sep).join('/')]=fileHash(file);};
    for(const name of ['film.json','timeline.json','assets.json'])add(path.join(root,name));
    for(const name of fs.readdirSync(root))if(/\.(js|html|css)$/.test(name))add(path.join(root,name));
    const scan=folder=>{if(!fs.existsSync(folder))return;for(const name of fs.readdirSync(folder)){const file=path.join(folder,name);if(fs.statSync(file).isDirectory())scan(file);else if(/\.(js|html|css)$/.test(name))add(file);}};scan(path.join(root,'code'));
    for(const name of ['pipeline.py','render.cjs','preview_review.py','asset_review.py','speech.py'])add(path.join(root,'tools',name));
    const request={kind:'pipeline',fps:t.fps,totalFrames:t.totalFrames,width:t.width,height:t.height,assetReview,sourceSha256:bound,frames:quadFrames.map(frame=>({frame,file:`preview/frame-${String(frame).padStart(6,'0')}.png`}))};
    const requestFile=path.join(preview,'review-request.json');fs.writeFileSync(requestFile,JSON.stringify(request,null,2)+'\n');
    report.previewReview=reviewTool('prepare',['--request',requestFile]);
    fs.writeFileSync(path.join(root,'preview-report.json'),JSON.stringify(report,null,2)+'\n');
    console.log(`四帧拼图待用户确认：${report.previewReview.contactSheet} (${report.previewReview.version})`);
  }
  console.log(`${mode} complete: ${root}`);
}
main().catch(e=>{
  console.error(e);
  if(sampleFlag<0 && fs.existsSync(root)) fs.writeFileSync(path.join(root,'render-failure.json'),JSON.stringify({error:String(e),browserErrors:errors},null,2));
  process.exitCode=1;
}).finally(async()=>{
  if (encoder && encoder.exitCode === null) encoder.kill();
  if (browser) await browser.close();
  if (server) server.close();
});
