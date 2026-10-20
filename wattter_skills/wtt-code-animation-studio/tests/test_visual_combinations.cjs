/* Real Canvas checks. Usage: PLAYWRIGHT_MODULE=... node tests/test_visual_combinations.cjs OUTPUT */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root=path.resolve(__dirname,'..'),out=path.resolve(process.argv[2]);
const sha=b=>require('node:crypto').createHash('sha256').update(b).digest('hex');
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  let browser;
  const results=[];
  try{
    browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH || (fs.existsSync('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined)});
    const page=await browser.newPage({viewport:{width:640,height:360}});
    await page.setContent('<canvas width="640" height="360"></canvas>');
    await page.addScriptTag({content:fs.readFileSync(path.join(root,'assets/starter/scenes.js'),'utf8')});
    const scene=(style,action='hop',effect='none')=>({id:'test',title:'同一个角色',visual:{subject:{id:'hero',type:'seed-character'},style,motion:{action,effect},renderer:'canvas2d'}});
    const draw=async(s,frame=25,progress=.75)=>page.evaluate(({s,frame,progress})=>{
      const canvas=document.querySelector('canvas'),c=canvas.getContext('2d');c.reset();
      const timeline={fps:20,seed:42,scenes:[s]};window.prepareScenes(timeline);
      window.drawScene(c,{scene:s,frame,progress,time:frame/20,width:640,height:360,timeline});
      return canvas.toDataURL();
    },{s,frame,progress});
    for(const style of ['flat','sand','particles'])for(const action of ['sway','hop'])for(const effect of ['none','reveal','assemble']){
      const s=scene(style,action,effect),a=await draw(s);
      await draw(scene('particles','sway','assemble'),90,.1);
      assert.equal(await draw(s),a,'乱序重画必须一致');
      assert.notEqual(await draw(s,5,.75),a,'主体动作必须随帧变化');
      if(effect!=='none')assert.notEqual(await draw(s,25,0),await draw(s,25,1),'效果必须改变画面');
      await draw(s);
      if(action==='hop'&&effect==='none')await page.locator('canvas').screenshot({path:path.join(out,`${style}.png`)});
      results.push({style,action,effect,deterministic:true,moving:true});
    }
    // Dispersal may change the actor area, never the title/footer safe zones.
    const safePixels=()=>page.evaluate(()=>{
      const source=document.querySelector('canvas');
      return [[0,79],[277,83]].map(([y,h])=>{
        const crop=document.createElement('canvas');crop.width=640;crop.height=h;
        crop.getContext('2d').drawImage(source,0,y,640,h,0,0,640,h);return crop.toDataURL();
      });
    });
    await draw(scene('particles','hop','assemble'),25,0);const safeBefore=await safePixels();
    await draw(scene('particles','hop','assemble'),25,1);assert.deepEqual((await safePixels()).map(s=>sha(Buffer.from(s))),safeBefore.map(s=>sha(Buffer.from(s))));
    const distinct=[];
    for(const style of ['flat','sand','particles'])distinct.push(sha(Buffer.from(await draw(scene(style)))));
    assert.equal(new Set(distinct).size,3,'三种画法必须不同');
    for(const bad of [Object.assign(scene('sand'),{kind:'sand'}),scene('watercolor'),{...scene('flat'),visual:{...scene('flat').visual,motion:{action:'walk',effect:'none'}}}]){
      await assert.rejects(draw(bad),/不能同时指定|未实现/);
    }
    // Compare legacy output with the frozen actual pre-change source, same browser and input.
    const oldPage=await browser.newPage({viewport:{width:640,height:360}});
    await oldPage.setContent('<canvas width="640" height="360"></canvas>');
    await oldPage.addScriptTag({content:fs.readFileSync(path.join(root,'tests/evals/versions/v002/skill/assets/starter/scenes.js'),'utf8')});
    for(const kind of ['character','sand','particles']){
      const s={id:'old',title:'旧工程',kind};
      const current=await draw(s);
      const old=await oldPage.evaluate(s=>{
        const c=document.querySelector('canvas').getContext('2d');c.reset();
        window.drawScene(c,{scene:s,frame:25,progress:.75,time:1.25,width:640,height:360,timeline:{fps:20,seed:42}});
        return c.canvas.toDataURL();
      },s);
      assert.equal(current,old,`旧 ${kind} 画面兼容`);
    }
    fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({browser:browser.version(),combinations:results,legacyExactMatches:3,negativeCases:3},null,2)+'\n');
    console.log('PASS: 18 combinations, 3 exact legacy comparisons, 3 explicit errors');
  }catch(e){fs.writeFileSync(path.join(out,'failure.txt'),String(e));throw e;}
  finally{if(browser)await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
