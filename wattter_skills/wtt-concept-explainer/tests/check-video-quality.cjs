/* 浏览器行为回归：不同画幅字幕的可见字号、换行、安全区和超限拒绝。 */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE);
const root=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);fs.mkdirSync(out,{recursive:true});
(async()=>{
 const server=http.createServer((req,res)=>{const name=new URL(req.url,'http://localhost').pathname;const file=path.resolve(root,'.'+(name==='/'?'/index.html':name));if(!file.startsWith(root+'/')||!fs.existsSync(file)||!fs.statSync(file).isFile())return res.writeHead(404).end();res.setHeader('Content-Type',({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json'})[path.extname(file)]||'application/octet-stream');res.end(fs.readFileSync(file));});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const result=[];
 try{
  for(const [w,h] of [[1920,1080],[1280,720],[1080,1920]]){
   const page=await browser.newPage({viewport:{width:w,height:h}});const t=JSON.parse(fs.readFileSync(path.join(root,'timeline.json')));t.width=w;t.height=h;
   const caption='甲'.repeat(w>=h?32:24);t.captions=[{text:caption,startFrame:1,endFrame:90}];
   await page.route('**/timeline.json',r=>r.fulfill({contentType:'application/json',body:JSON.stringify(t)}));
   await page.goto(`http://127.0.0.1:${server.address().port}/?export=1`);await page.waitForFunction(()=>window.__ready);
   const runs=await page.evaluate(async()=>{const c=document.querySelector('#stage').getContext('2d'),native=c.fillText,log=[];c.fillText=function(txt,x,y,...args){if(/^甲+$/.test(txt))log.push({text:txt,font:this.font,x,y,width:this.measureText(txt).width});return native.call(this,txt,x,y,...args)};try{await renderFrame(2);return log}finally{c.fillText=native}});
   assert.equal(runs.length,2);assert.equal(runs.map(r=>r.text).join(''),caption);
   for(const run of runs){const size=Number(run.font.match(/([\d.]+)px/)[1]);assert(size*(w>=h?640:360)/w>=20);assert(run.width<=w*.88);assert(run.y+size/2<h);assert(run.y-size/2>h*.7);}
   await page.locator('#stage').screenshot({path:path.join(out,`caption-${w}x${h}.png`)});
   t.captions[0].text='甲'.repeat(100);await page.reload();await page.waitForFunction(()=>window.__ready);
   const failure=await page.evaluate(async()=>{try{await renderFrame(2);return null}catch(e){return String(e)}});assert.match(failure,/字幕溢出/);
   await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'../assets/starter/scenes.js'),'utf8')});
   const template=await page.evaluate(({w,h})=>{const ctx=document.querySelector('#stage').getContext('2d'),base={scene:{title:'先看整体',director:{labels:['输入','变化','结果'],focus:0}},width:w,height:h,progress:.5};drawScene(ctx,base);const errors=[];for(const which of ['title','label']){const value=structuredClone(base);if(which==='title')value.scene.title='甲'.repeat(100);else value.scene.director.labels[0]='甲'.repeat(30);try{drawScene(ctx,value);errors.push(null)}catch(e){errors.push(String(e))}}return errors},{w,h});
   assert(template.every(e=>e&&e.includes('模板文字溢出')));
   result.push({width:w,height:h,lines:runs,overflowRejected:true,templateOverflowRejected:true});await page.close();
  }
  fs.writeFileSync(path.join(out,'caption-check.json'),JSON.stringify({passed:true,cases:result},null,2));console.log('3画幅换行/安全区通过；3个超长字幕反例均被拒绝。');
 }finally{await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exit(1)});
