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
const mode = process.argv.includes('--render') ? 'render' : 'preview';
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const fileHash = p => hash(fs.readFileSync(p));
const errors = [], sourceSha256 = {};
let browser, encoder, server;

async function main() {
  const t = JSON.parse(fs.readFileSync(path.join(root, 'timeline.json')));
  if (mode === 'render') execFileSync(process.env.PYTHON || 'python3', [path.join(__dirname, 'pipeline.py'), 'check', root], {stdio: 'inherit'});
  if (t.filmSha256 !== fileHash(path.join(root, 'film.json'))) throw Error('film.json 已变化；重新编译时间轴');
  let playwright;
  try { playwright = createRequire(path.join(root, 'package.json'))('playwright'); }
  catch (e) {
    if (!process.env.PLAYWRIGHT_MODULE) throw Error('缺少 Playwright；在项目中安装 playwright 或设置 PLAYWRIGHT_MODULE');
    playwright = require(process.env.PLAYWRIGHT_MODULE);
  }
  const mime = {'.html':'text/html', '.js':'application/javascript', '.json':'application/json', '.wav':'audio/wav', '.mp3':'audio/mpeg', '.svg':'image/svg+xml', '.png':'image/png', '.woff2':'font/woff2'};
  server = http.createServer((req, res) => {
    try {
      const name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      const file = path.resolve(root, '.' + (name === '/' ? '/index.html' : name));
      if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile() || !fs.realpathSync(file).startsWith(fs.realpathSync(root) + path.sep)) { res.writeHead(404).end(); return; }
      const data = fs.readFileSync(file);
      sourceSha256[path.relative(root, file)] = hash(data);
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
  await page.goto(`http://127.0.0.1:${server.address().port}/?export=1`, {waitUntil:'load'});
  await page.waitForFunction(() => window.__ready === true, null, {timeout:30000});
  await page.evaluate(() => document.fonts.ready);
  const meta = await page.evaluate(() => window.__filmMeta);
  if (!meta || ['width','height','fps','totalFrames'].some(k => meta[k] !== t[k])) throw Error('页面 __filmMeta 与时间轴不符');
  const stage = page.locator('#stage');
  const grab = async frame => {
    await page.evaluate(async f => { await window.renderFrame(f); }, frame);
    return stage.screenshot({type:'png', animations:'allow'});
  };
  const preview = path.join(root, 'preview'); fs.mkdirSync(preview, {recursive:true});
  // Boundaries plus each scene midpoint: review cuts, captions and representative poses.
  const samples = new Set([0, t.totalFrames - 1]);
  for (const s of t.scenes) for (const f of [s.startFrame, s.startFrame + Math.floor(s.durationFrames / 2), s.endFrame - 1]) samples.add(f);
  for (const c of t.captions) samples.add(Math.floor((c.startFrame + c.endFrame - 1) / 2));
  for (const f of [...samples].sort((a,b)=>a-b)) fs.writeFileSync(path.join(preview, `frame-${String(f).padStart(6,'0')}.png`), await grab(f));
  const determinism = [];
  const tests = [...new Set([0, .19, .47, .79, 1].map(x=>Math.round(x*(t.totalFrames-1))))];
  for (const f of tests) {
    const a = hash(await grab(f)); await grab((f + Math.floor(t.totalFrames * .37) + 1) % t.totalFrames);
    const b = hash(await grab(f)); determinism.push({frame:f, sha256:a, repeatSha256:b, match:a===b});
  }
  if (errors.length || determinism.some(c=>!c.match)) throw Error(JSON.stringify({errors,determinism}));
  const report = {mode, timelineSha256:fileHash(path.join(root,'timeline.json')), browser:browser.version(),
    totalFrames:t.totalFrames, durationSeconds:t.durationSeconds, determinism, browserErrors:errors, sourceSha256};
  if (mode === 'render') {
    const log = fs.openSync(path.join(root, 'render-ffmpeg.log'), 'w');
    try {
      encoder = spawn('ffmpeg', ['-y','-hide_banner','-loglevel','warning','-f','image2pipe','-vcodec','png','-framerate',String(t.fps),'-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',path.join(root,'silent.mp4')], {stdio:['pipe','ignore',log]});
      let encoderError;
      const done = new Promise((resolve,reject)=>{
        encoder.on('error',reject); encoder.on('close',code=>code===0?resolve():reject(Error(`FFmpeg exit ${code}，见 render-ffmpeg.log`)));
        encoder.stdin.on('error',reject);
      });
      done.catch(e=>{encoderError=e;});
      const begun = Date.now();
      for (let f=0; f<t.totalFrames; f++) {
        if (encoderError) throw encoderError;
        const data=await grab(f);
        if (!encoder.stdin.write(data)) await Promise.race([once(encoder.stdin,'drain'),done.then(()=>{throw Error('编码器提前退出');})]);
        if (f % Math.max(1,t.fps*2) === 0) console.log(`render ${f}/${t.totalFrames} · ${((Date.now()-begun)/1000).toFixed(1)}s`);
        if (errors.length) throw Error(errors.join('\n'));
      }
      encoder.stdin.end(); await done;
      report.renderWallSeconds=(Date.now()-begun)/1000;
      report.videoSha256=fileHash(path.join(root,'silent.mp4'));
    } finally { fs.closeSync(log); }
  }
  fs.writeFileSync(path.join(root, mode==='render'?'render-report.json':'preview-report.json'), JSON.stringify(report,null,2)+'\n');
  console.log(`${mode} complete: ${root}`);
}
main().catch(e=>{
  console.error(e);
  if(fs.existsSync(root)) fs.writeFileSync(path.join(root,'render-failure.json'),JSON.stringify({error:String(e),browserErrors:errors},null,2));
  process.exitCode=1;
}).finally(async()=>{
  if (encoder && encoder.exitCode === null) encoder.kill();
  if (browser) await browser.close();
  if (server) server.close();
});
