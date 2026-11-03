/* Content-specific starter, not a universal renderer. Replace geometry and actions for each film.
   Legacy kind scenes retain their old behavior; new scenes combine independent visual fields. */
(() => {
  const hash=n=>{const v=Math.sin(n*127.1+37.7)*43758.5453;return v-Math.floor(v);};
  const ease=x=>x*x*(3-2*x);
  function plant(c,x,y,r,grow,bloom){
    c.strokeStyle='#477c65';c.lineWidth=r*.12;c.lineCap='round';
    c.beginPath();c.moveTo(x,y);c.quadraticCurveTo(x-r*.24,y-r*grow,x,y-r*2*grow);c.stroke();
    for(const d of [-1,1]){c.fillStyle='#719570';c.beginPath();c.ellipse(x+d*r*.38*grow,y-r*grow,r*.46*grow,r*.16*grow,d*.5,0,Math.PI*2);c.fill();}
    if(bloom>0){for(let i=0;i<7;i++){const a=i*Math.PI*2/7;c.fillStyle='#ed9760';c.beginPath();c.ellipse(x+Math.cos(a)*r*.42*bloom,y-r*2*grow+Math.sin(a)*r*.42*bloom,r*.3*bloom,r*.3*bloom,0,0,Math.PI*2);c.fill();}c.fillStyle='#f1ca6e';c.beginPath();c.arc(x,y-r*2*grow,r*.23*bloom,0,Math.PI*2);c.fill();}
  }
  const drawLegacyScene=(c,{scene:s,progress:p,time,width:w,height:h,timeline:t})=>{
    const dark=s.kind==='particles',ink=dark?'#fbf3df':'#28394c';
    c.fillStyle=dark?'#19263d':'#f4eddd';c.fillRect(0,0,w,h);
    c.fillStyle=ink;c.textAlign='center';c.font=`700 ${Math.min(w*.048,h*.07)}px Arial, 'PingFang SC',sans-serif`;
    c.fillText(s.title,w*.5,h*.17,w*.86);
    const r=Math.min(w*.12,h*.16), x=w*.5,y=h*.7;
    if(s.kind==='character'){
      const bounce=Math.sin(Math.min(p*2,1)*Math.PI)*h*.12;
      c.fillStyle='#27395120';c.beginPath();c.ellipse(x,y,r*.8,r*.12,0,0,Math.PI*2);c.fill();
      c.save();c.translate(x,y-r-bounce);c.rotate(Math.sin(time*2)*.08);
      c.fillStyle='#ad7547';c.strokeStyle=ink;c.lineWidth=3;c.beginPath();c.ellipse(0,0,r*.7,r,0,0,Math.PI*2);c.fill();c.stroke();
      c.fillStyle='#172d40';for(const d of [-1,1]){c.beginPath();c.arc(d*r*.24,-r*.08,r*.06,0,Math.PI*2);c.fill();}
      c.beginPath();c.arc(0,r*.13,r*.2,0,Math.PI);c.stroke();c.restore();
    }else if(s.kind==='sand'){
      c.fillStyle='#ceb58d';c.fillRect(0,y,w,h-y);plant(c,x,y,r,ease(p),0);
      for(let i=0;i<1800;i++){const px=hash(i+t.seed)*w,py=y+hash(i+770)*h*.3;
        c.fillStyle=i%2?'#a38b654d':'#f5e6c355';c.fillRect(px,py,1.8,1.8);}
      for(let i=0;i<55;i++){const px=hash(i+80)*w,py=((hash(i+560)+time*.27)%1)*h*.63;c.strokeStyle='#7398a270';c.lineWidth=2;c.beginPath();c.moveTo(px,py);c.lineTo(px-3,py+12);c.stroke();}
    }else if(s.kind==='particles'){
      const bloom=ease(Math.min(1,p*2));plant(c,x,y,r,1,bloom);
      for(let i=0;i<440;i++){
        const a=hash(i+100)*Math.PI*2+time*.17,dist=(.2+hash(i+230)*.8)*Math.min(w*.4,h*.36);
        const px=x+Math.cos(a)*dist,py=h*.48+Math.sin(a)*dist*.65;
        c.globalAlpha=(.25+hash(i+99)*.65)*Math.min(1,p*4);c.fillStyle=i%3?'#f6d488':'#ed9760';c.beginPath();c.arc(px,py,1+hash(i)*2,0,Math.PI*2);c.fill();
      }c.globalAlpha=1;
    }else throw Error(`未实现的场景 kind: ${s.kind}`);
  };

  const subjects = new Map();
  function visualOf(s) {
    if(s.visual !== undefined && s.kind !== undefined) throw Error(`${s.id}: visual 与 kind 不能同时指定`);
    if(s.visual === undefined) {
      if(!['character','sand','particles'].includes(s.kind)) throw Error(`${s.id}: 未实现的旧 kind: ${s.kind}`);
      return null;
    }
    const v=s.visual;
    if(!v || typeof v !== 'object' || typeof v.subject?.id !== 'string' || !v.subject.id.trim()) throw Error(`${s.id}: 缺少主体身份`);
    const choices={type:['seed-character'],style:['flat','sand','particles'],action:['sway','hop'],effect:['none','reveal','assemble'],renderer:['canvas2d']};
    const values={type:v.subject.type,style:v.style,action:v.motion?.action,effect:v.motion?.effect,renderer:v.renderer};
    for(const [key,list] of Object.entries(choices)) if(!list.includes(values[key])) throw Error(`${s.id}: 未实现的 ${key}: ${values[key]}；请按分镜补实现`);
    return v;
  }

  // One local silhouette supplies the flat body, sand mask and particle targets.
  function silhouette(c) {
    c.lineWidth=12;c.lineCap='round';
    c.beginPath();c.moveTo(86,146);c.lineTo(64,162);c.moveTo(170,146);c.lineTo(192,162);
    c.moveTo(108,189);c.lineTo(102,213);c.moveTo(148,189);c.lineTo(154,213);c.stroke();
    c.beginPath();c.ellipse(128,126,51,76,-.13,0,Math.PI*2);c.fill();
    c.beginPath();c.ellipse(145,47,22,9,-.65,0,Math.PI*2);c.fill();
  }
  function face(c, light=false) {
    c.fillStyle=light?'#fff3bc':'#26384a';
    for(const x of [111,146]){c.beginPath();c.arc(x,118,5,0,Math.PI*2);c.fill();}
    c.strokeStyle=c.fillStyle;c.lineWidth=4;c.lineCap='round';
    c.beginPath();c.arc(128,136,12,.12,Math.PI-.12);c.stroke();
  }
  function subjectSeed(id,seed) {
    let n=Number(seed)||0;
    for(const ch of id)n=(n*31+ch.codePointAt(0))%1000003;
    return n;
  }
  window.prepareScenes=t=>{
    subjects.clear();
    for(const s of t.scenes){
      const v=visualOf(s);if(!v)continue;
      const old=subjects.get(v.subject.id);
      if(old){if(old.type!==v.subject.type)throw Error(`${s.id}: 同一主体 ID 的 type 不一致`);continue;}
      const layer=document.createElement('canvas');layer.width=layer.height=256;
      const lc=layer.getContext('2d',{willReadFrequently:true});
      lc.fillStyle=lc.strokeStyle='#c0884a';silhouette(lc);
      const pixels=lc.getImageData(0,0,256,256).data, points=[];
      const seed=subjectSeed(v.subject.id,t.seed);
      for(let y=24;y<224;y+=3)for(let x=48;x<208;x+=3){
        if(pixels[(y*256+x)*4+3]<128)continue;
        const i=points.length;
        const jx=x+(hash(i+seed+301)-.5)*2.7,jy=y+(hash(i+seed+701)-.5)*2.7;
        if(pixels[(Math.round(jy)*256+Math.round(jx))*4+3]<128)continue;
        points.push({x:jx,y:jy,n:hash(i+seed),dx:(hash(i+seed+30)-.5)*430,dy:(hash(i+seed+80)-.5)*350});
      }
      subjects.set(v.subject.id,{type:v.subject.type,layer,points});
    }
  };
  window.drawScene=(c,args)=>{
    const {scene:s,progress:p,frame,width:w,height:h,timeline:t}=args;
    const v=visualOf(s);if(!v)return drawLegacyScene(c,args);
    const subject=subjects.get(v.subject.id);
    if(!subject)throw Error(`${s.id}: 主体尚未准备`);
    const dark=v.style==='particles';
    c.fillStyle=dark?'#15243a':'#f5eddd';c.fillRect(0,0,w,h);
    c.fillStyle=dark?'#fae5b4':'#354758';c.textAlign='center';
    c.font=`700 ${Math.min(w*.043,h*.062)}px Arial, 'PingFang SC',sans-serif`;
    c.fillText(s.title,w*.5,h*.15,w*.88);
    const scale=Math.min(w*.48,h*.64)/256;
    // Global-frame pose preserves the action phase across a change of style.
    const seconds=frame/t.fps,phase=seconds*Math.PI*1.4;
    const lift=v.motion.action==='hop'?Math.abs(Math.sin(phase))*h*.055:0;
    c.fillStyle=dark?'#d3af6d25':'#73583c20';c.beginPath();
    c.ellipse(w*.5,h*.73,scale*(51-lift/h*200),h*.013,0,0,Math.PI*2);c.fill();
    // Keep dispersed grains out of title and subtitle areas.
    c.save();c.beginPath();c.rect(w*.06,h*.23,w*.88,h*.53);c.clip();
    c.translate(w*.5,h*.72-lift);c.scale(scale,scale);
    c.rotate(Math.sin(phase)*(v.motion.action==='sway'?.09:.035));c.translate(-128,-216);
    if(v.motion.effect==='reveal'){
      c.beginPath();c.rect(0,0,256,256*ease(Math.min(1,p/.7)));c.clip();
    }
    const assembled=v.motion.effect==='assemble'?ease(Math.min(1,p/.65)):1;
    if(v.style==='flat'&&assembled===1){
      c.drawImage(subject.layer,0,0);face(c);
    }else{
      if(v.style==='sand' && assembled===1){c.globalAlpha=.18;c.drawImage(subject.layer,0,0);c.globalAlpha=1;}
      for(let i=0;i<subject.points.length;i++){
        const q=subject.points[i];
        // Sparse particles and dense sand share the exact same underlying target positions.
        if(v.style==='particles'&&i%2)continue;
        const x=q.x+q.dx*(1-assembled),y=q.y+q.dy*(1-assembled);
        c.fillStyle=v.style==='sand'?['#765332','#b08148','#d5b47d'][Math.floor(q.n*3)]:['#f6d590','#d29958','#fff0bb'][Math.floor(q.n*3)];
        c.globalAlpha=v.style==='sand'?1:.65+.35*Math.sin(seconds*1.5+q.n*6)**2;
        const radius=v.style==='sand'?.75+q.n*.85:1.05+q.n*.65;
        c.beginPath();c.arc(x,y,radius,0,Math.PI*2);c.fill();
      }
      c.globalAlpha=Math.max(0,(assembled-.8)/.2);face(c,dark);
    }
    c.restore();
  };
})();
