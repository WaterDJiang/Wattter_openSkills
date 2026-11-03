/* Original seasonal schematic map; same frame function for browser and node-canvas. */
(function(root){
'use strict';
const P=typeof module!=='undefined'?require('./presentation.js'):root.PostcardPresentation;
const N=600,H=1440,W=1080,TAU=Math.PI*2,BG='#FDFDF9';
const mod=(n,m)=>(n%m+m)%m;
function mulberry32(a){return()=>{let t=a+=0x6D2B79F5;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};}
const river=y=>760+62*Math.sin(TAU*y/H)+24*Math.sin(2*TAU*y/H);
const road=y=>365+36*Math.sin(TAU*y/H);
function model(i){const t=mod(i,N)/N;return {t,camY:t*H,windmillAngle:t*TAU*3,cloudY:t*H*.55,planeX:mod(t*2,1)*1440-180};}
function make(canvas,config={}){
 const c=canvas.getContext('2d'),rng=mulberry32(config.seed??20261103),autumn=config.season==='秋',city=config.scene==='city';
 const colors=P.seasonPalette(config.season||'春',{palette:config.palette||'vivid',overrides:config.paletteOverrides||{}}),p=colors.fields,BG=colors.paper;
 if(!p)throw Error('季节须为春/夏/秋/冬');if(!['village','city'].includes(config.scene||'village'))throw Error('scene须为village/city');
 for(const [key,max] of [['latitude',90],['longitude',180]])if(config[key]!=null&&(!Number.isFinite(config[key])||Math.abs(config[key])>max))throw Error('无效坐标 '+key);
 const trees=Array.from({length:75},()=>({x:45+rng()*990,y:rng()*H,r:10+rng()*10,k:Math.floor(rng()*3)}));
 const specks=Array.from({length:2200},()=>({x:rng()*W,y:rng()*W,r:.5+rng()*2.7,a:.15+rng()*.65}));
 const clouds=Array.from({length:7},()=>({x:rng()*W,y:rng()*H*.55,r:22+rng()*22,cycles:1+Math.floor(rng()*2)}));
 const buildings=Array.from({length:city?42:15},(_,n)=>({x:city?65+(n%6)*155:65+(n%3)*120,y:95+Math.floor(n/(city?6:3))*(city?205:275),w:city?75:49,h:city?88:56,k:n%3}));
 function rect(x,y,w,h,color){c.fillStyle=color;c.fillRect(x,y,w,h);}
 function disk(x,y,r,color){c.fillStyle=color;c.beginPath();c.arc(x,y,r,0,TAU);c.fill();}
 function label(s,x,y,size){c.font=`${size}px "PingFang SC","Microsoft YaHei",sans-serif`;c.textAlign='center';c.fillStyle='#374f48';c.fillText(s,x,y);}
 function repeated(y,draw,height=H){for(let k=-2;k<=2;k++){const sy=y+k*height;if(sy>-220&&sy<W+220)draw(sy);}}
 function world(m){
  rect(0,0,W,W,BG);
  if(!city){for(let row=0;row<8;row++)for(let col=0;col<3;col++){
   let wy=row*180;repeated(wy-m.camY,sy=>{rect(38+col*101,sy+22,89,140,p[(row+col+30)%3]);c.strokeStyle='#FDFDF9';c.lineWidth=2;for(let k=1;k<8;k++){c.beginPath();c.moveTo(38+col*101+k*11,sy+22);c.lineTo(38+col*101+k*11,sy+162);c.stroke();}});
  }}
  // Sample periodic centre lines at absolute world coordinates, including the visible wrap.
  function curve(fn,color,width){c.strokeStyle=color;c.lineWidth=width;c.beginPath();for(let y=-30;y<=W+30;y+=3){const x=fn(y+m.camY);y===-30?c.moveTo(x,y):c.lineTo(x,y);}c.stroke();}
  curve(river,colors.river,110);curve(y=>river(y)+14,'#d8e9e6',4);curve(road,colors.road,68);
  c.strokeStyle='#fffef8';c.lineWidth=3;c.setLineDash([12,12]);c.lineDashOffset=mod(m.camY,24);c.beginPath();for(let y=-30;y<W+30;y+=3){const x=road(y+m.camY);y===-30?c.moveTo(x,y):c.lineTo(x,y);}c.stroke();c.setLineDash([]);
  for(let q=0;q<4;q++)repeated(q*360-m.camY,sy=>{
   rect(0,sy-22,700,44,colors.road);
   for(let z=0;z<6;z++)rect(road(q*360)-25+z*9,sy-28,5,56,BG);
   rect(691,sy-30,138,60,'#e1cdb0');
   const px=road(q*360)+Math.sin(TAU*m.t*2+q)*72;disk(px,sy+40,4,'#526f75');
  });
  for(const b of buildings){if(city){const mid=b.y+b.h/2,overlaps=x=>b.x-8<x+76&&b.x+b.w+8>x-76;if(overlaps(road(mid))||overlaps(river(mid))||Math.abs(mod(mid+180,360)-180)<b.h/2+28)continue;}repeated(b.y-m.camY,sy=>{
   rect(b.x,sy,b.w,b.h,colors.walls[b.k]);c.strokeStyle=colors.ink;c.lineWidth=1.2;c.strokeRect(b.x,sy,b.w,b.h);
   if(city){rect(b.x+9,sy+10,b.w-18,b.h-20,'#f3eee4');rect(b.x+19,sy+23,b.w-38,b.h-46,p[b.k]);}
   else {rect(b.x-4,sy+15,b.w+8,26,'#caa087');c.strokeRect(b.x-4,sy+15,b.w+8,26);}
  });
  }
  if(city)repeated(1180-m.camY,sy=>{rect(65,sy,230,130,'#d6e4bc');for(let j=0;j<8;j++)disk(90+j%4*57,sy+35+Math.floor(j/4)*65,18,p[1]);rect(490,sy+15,90,95,'#d8c5ac');rect(526,sy-20,18,140,'#d8c5ac');});
  for(const tree of trees){if(Math.abs(tree.x-river(tree.y))<80||Math.abs(tree.x-road(tree.y))<58)continue;repeated(tree.y-m.camY,sy=>{rect(tree.x-2,sy,4,15,'#b9aa8b');disk(tree.x,sy-3,tree.r,colors.trees[tree.k]);disk(tree.x-6,sy-8,tree.r*.6,colors.trees[(tree.k+1)%3]);});}
  // Windmill has exactly three rotations over 600 frames.
  repeated(1225-m.camY,sy=>{rect(591,sy,21,38,'#d7c5a9');c.save();c.translate(602,sy);c.rotate(m.windmillAngle);for(let k=0;k<4;k++){c.rotate(TAU/4);rect(0,-3,45,6,'#f2eddc');c.strokeStyle='#65766b';c.lineWidth=.8;c.strokeRect(0,-3,45,6);}c.restore();disk(602,sy,4,'#8d9a86');});
  for(let n=0;n<8;n++){const wy=mod(n*180+m.t*H*(n%2?2:-1),H);repeated(wy-m.camY,sy=>{const x=road(wy)+(n%2?16:-16);rect(x-7,sy-12,14,24,p[n%3]);rect(x-5,sy-5,10,8,BG);});}
  for(let n=0;n<3;n++){const wy=mod(n*H/3-m.t*H,H);repeated(wy-m.camY,sy=>{const x=river(wy);c.fillStyle='#f0e7d2';c.beginPath();c.ellipse(x,sy,11,26,0,0,TAU);c.fill();rect(x-5,sy-10,10,16,'#c9ab91');});}
  for(const cloud of clouds){const x=mod(cloud.x+m.t*W*cloud.cycles,W);repeated(cloud.y-m.cloudY,sy=>{for(let k=-1;k<=1;k++){disk(x+k*W,sy,cloud.r,'#fffef6cc');disk(x+k*W+cloud.r*.9,sy+8,cloud.r*.8,'#fffef6cc');}},H*.55);}
  c.save();c.translate(m.planeX,165+18*Math.sin(TAU*m.t*2));rect(-27,-3,54,6,'#839eab');rect(-6,-23,12,46,'#839eab');rect(-22,-12,6,24,'#839eab');c.restore();
 }
 function frame(i,{unmasked=false}={}){
  if(!Number.isInteger(i))throw Error('frame index must be integer');const m=model(i);c.setTransform(1,0,0,1,0,0);c.clearRect(0,0,canvas.width,canvas.height);c.save();c.scale(canvas.width/W,canvas.height/W);rect(0,0,W,W,BG);
  const sec=m.t*20,open=Math.min(1,sec),close=sec<=18?1:Math.max(0,(20-sec)/2),scale=unmasked||config.reveal===false?1:Math.min(open,close);
  c.save();c.beginPath();c.rect(540-450*scale,490-450*scale,900*scale,900*scale);c.clip();world(m);c.restore();
  if(!unmasked){
   // Fixed paper-grain brush around border, never a fresh random mask each frame.
   for(const s of specks){if(Math.min(Math.abs(s.x-90),Math.abs(s.x-990),Math.abs(s.y-40),Math.abs(s.y-940))<25){c.globalAlpha=s.a;disk(s.x,s.y,s.r,BG);}}c.globalAlpha=1;
   if(config.reveal!==false&&sec>19){const q=(sec-19),a=1-q;for(let k=0;k<18;k++){const ang=k*TAU/18;disk(540+Math.cos(ang)*q*95,490+Math.sin(ang)*q*70,a*2.5,`rgba(85,104,92,${a})`);}}
   rect(0,941,W,139,BG);const geo=config.latitude==null||config.longitude==null?'示意地图 · 未标注真实坐标':`${Math.abs(config.latitude)}° ${config.latitude<0?'S':'N'}, ${Math.abs(config.longitude)}° ${config.longitude<0?'W':'E'}`;
   label(`${config.placeZh||'示例小镇'}  ${config.placeEn||'Sample Town'}`,540,975,25);
   label(`${config.season||'春'} — ${config.moodZh||'风把日子吹得很慢'} / ${config.moodEn||'A quiet day drifts by'}`,540,1011,20);label(geo,540,1045,18);
  }
  c.restore();return canvas;
 }
 return {frame,model,river,road,colors,worldMode:'scroll'};
}
const api={make,model,river,road,mod,N,H};if(typeof module!=='undefined')module.exports=api;else root.LegacyScrollPostcard=api;
})(typeof window==='undefined'?globalThis:window);
