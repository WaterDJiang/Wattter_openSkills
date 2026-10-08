/* One timeline drives preview, narration, captions and export. */
(async () => {
  const assetResponse = await fetch('assets.json');
  if (!assetResponse.ok) throw Error('缺少素材声明 assets.json');
  const assetSelection = await assetResponse.json();
  window.assetLink = id => {
    const link = assetSelection.links.find(x=>x.id===id);
    if(!link) throw Error(`未登记的导流 ID: ${id}`);
    return link.url;
  };
  const response = await fetch('timeline.json');
  if (!response.ok) throw Error('先编译 timeline.json');
  const t = await response.json();
  const canvas = document.querySelector('#stage'), ctx = canvas.getContext('2d');
  canvas.width=t.width; canvas.height=t.height;
  document.title=t.title;
  const exportMode=new URLSearchParams(location.search).has('export');
  document.body.classList.toggle('export',exportMode);
  const seek=document.querySelector('#seek'), label=document.querySelector('#time'), audio=document.querySelector('#audio');
  seek.max=t.totalFrames-1;
  // Do not request audio during frame export or before mixing.
  let hasAudio=false;
  if (!exportMode && t.locked) {
    const result=await fetch('audio/mix-master.wav',{method:'HEAD'});
    if(result.ok){audio.src='audio/mix-master.wav';hasAudio=true;}
  }
  await document.fonts.ready;
  if(window.prepareScenes) await window.prepareScenes(t);
  window.__filmMeta={width:t.width,height:t.height,fps:t.fps,totalFrames:t.totalFrames};
  window.renderFrame=async frame=>{
    if(!Number.isInteger(frame)||frame<0||frame>=t.totalFrames) throw Error(`frame 越界: ${frame}`);
    const s=t.scenes.find(x=>frame>=x.startFrame&&frame<x.endFrame);
    // Reset styles/clipping/baselines as well as pixels: captions must not leak into the next frame.
    if(ctx.reset) ctx.reset(); else canvas.width=canvas.width;
    ctx.save();
    window.drawScene(ctx,{timeline:t,scene:s,frame,localFrame:frame-s.startFrame,
      time:(frame-s.startFrame)/t.fps,progress:(frame-s.startFrame)/Math.max(1,s.durationFrames-1),width:t.width,height:t.height});
    ctx.restore();
    const cap=t.captions.find(x=>frame>=x.startFrame&&frame<x.endFrame);
    if(cap){
      const size=Math.round(Math.min(t.width/27,t.height/21));
      ctx.font=`500 ${size}px Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif`;
      ctx.textAlign='center';ctx.textBaseline='middle';
      const chars=Array.from(cap.text), lines=[''];
      for(const ch of chars){let i=lines.length-1;if(ctx.measureText(lines[i]+ch).width>t.width*.82)lines.push(ch);else lines[i]+=ch;}
      const h=lines.length*size*1.35+size*.7,y=t.height*.91-h;
      ctx.fillStyle='#17243be8';ctx.fillRect(t.width*.06,y,t.width*.88,h);
      ctx.fillStyle='#fff9ed';lines.forEach((line,i)=>ctx.fillText(line,t.width*.5,y+size*.35+size*.675+i*size*1.35));
    }
    if(!exportMode){seek.value=frame;label.textContent=`${(frame/t.fps).toFixed(1)} / ${t.durationSeconds.toFixed(1)}s`;}
  };
  let playing=false,base=0,origin=0;
  function pause(){playing=false;audio.pause();document.querySelector('#play').textContent='播放';}
  async function tick(now){
    if(!playing)return;
    const seconds=hasAudio?audio.currentTime:base+(now-origin)/1000;
    const frame=Math.min(t.totalFrames-1,Math.floor(seconds*t.fps));
    await window.renderFrame(frame);
    if(frame>=t.totalFrames-1||hasAudio&&audio.ended){pause();return;}
    requestAnimationFrame(tick);
  }
  document.querySelector('#play').onclick=async()=>{
    if(playing){pause();return;}
    if(+seek.value>=t.totalFrames-1)seek.value=0;
    base=+seek.value/t.fps;origin=performance.now();
    if(hasAudio){audio.currentTime=base;await audio.play();}
    playing=true;document.querySelector('#play').textContent='暂停';requestAnimationFrame(tick);
  };
  seek.oninput=()=>{pause();window.renderFrame(+seek.value);};
  await window.renderFrame(0);window.__ready=true;
})();
