/* Original schematic town with explicit height. Geography and named landmarks are replaced per brief. */
(function(root){'use strict';
const P=typeof module!=='undefined'?require('./presentation.js'):root.PostcardPresentation;
const {project,orderedFaces,mod,TAU}=P,N=600,H=1440;
const shade=(hex,n)=>'#'+[1,3,5].map(k=>Math.max(0,Math.min(255,parseInt(hex.slice(k,k+2),16)+n)).toString(16).padStart(2,'0')).join('');
function rng(a){return()=>{let t=a+=0x6d2b79f5;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};}
const riverCenter=x=>460+24*Math.sin(TAU*x/1080);
function make(canvas,config,pal){
 const c=canvas.getContext('2d'),r=rng(config.seed),city=config.scene==='city',ink=pal.ink,BG=pal.paper,memphis=config.palette==='memphis',frames=config.frames||N,duration=config.durationSeconds||20;
 const events=(memphis?[{id:'crosswalk-yield',frame:Math.round(frames*.335),type:'soft-step',description:'小车停在斑马线前，让行人过街'},{id:'bird-flyby',frame:Math.round(frames*.64),type:'chirp',description:'两只鸟掠过小镇上方'}]:[]).map(e=>({...e,seconds:e.frame/config.fps}));
 const dust=Array.from({length:1800},()=>({x:r()*1080,y:r()*1080,s:.3+r()*.9,a:.025+r()*.06}));
 const groundEdge=memphis?[[42,42,Math.PI],[1038,42,Math.PI*1.5],[1038,858,0],[42,858,Math.PI*.5]].flatMap(([x,z,a])=>Array.from({length:9},(_,k)=>[x+52*Math.cos(a+k*Math.PI/16),z+52*Math.sin(a+k*Math.PI/16),-1])):[[-10,-10,-1],[1090,-10,-1],[1090,910,-1],[-10,910,-1]];
 const anchors=city?[{id:'bridge',name:'河上小桥',position:[648,riverCenter(648),42],offset:[50,0]},{id:'tower',name:'钟楼广场',position:[870,182,154]},{id:'park',name:'河畔公园',position:[196,175,64]}]:[{id:'bridge',name:'河上小桥',position:[648,riverCenter(648),42],offset:[50,0]},{id:'windmill',name:'田间风车',position:[825,180,149]}];
 let faces=[];
 const f=(points,fill,stroke=ink,width=1,layer=null)=>{const face={points,fill,stroke,width:memphis&&stroke?Math.max(width,1.35):width,layer:layer??(points.every(p=>p[2]<=2)?0:1),closed:true};faces.push(face);return face;};
 const l=(points,stroke=ink,width=1,layer=null)=>faces.push({points,fill:null,stroke,width,layer:layer??(points.every(p=>p[2]<=2)?0:1),closed:false});
 const quad=(x,z,w,d,h,fill,layer=null)=>{const face=f([[x,z,h],[x+w,z,h],[x+w,z+d,h],[x,z+d,h]],fill,memphis&&fill!==pal.ground?ink:null,1.5,layer);if(memphis&&w>30&&d>30&&fill!==pal.road&&fill!==pal.mark&&fill!==BG&&fill!==pal.ground)face.pattern=['dots','stripes','zigzag'][Math.abs(Math.round(x+z))%3];return face;};
 function hardShadow(points,height){if(memphis)f(points.map(([x,z])=>[x+height*.42,z+height*.55,.7]),ink+'38',null,0,.15);}
 function box(x,z,w,d,h,color,base=0,roof=null){let top=base+h;if(base===0&&h>9)hardShadow([[x,z],[x+w,z],[x+w,z+d],[x,z+d]],h);
  f([[x,z,base],[x+w,z,base],[x+w,z,top],[x,z,top]],shade(color,-12));
  f([[x+w,z,base],[x+w,z+d,base],[x+w,z+d,top],[x+w,z,top]],shade(color,-18));
  f([[x+w,z+d,base],[x,z+d,base],[x,z+d,top],[x+w,z+d,top]],shade(color,-5));
  f([[x,z+d,base],[x,z,base],[x,z,top],[x,z+d,top]],shade(color,2));quad(x,z,w,d,top,roof||shade(color,13));
 }
 const ring=(x,z,h,rad,n=8)=>Array.from({length:n},(_,k)=>[x+Math.cos(k*TAU/n)*rad,z+Math.sin(k*TAU/n)*rad,h]);
 function drum(x,z,low,high,r0,r1,color,n=8){if(low>15)hardShadow(ring(x,z,0,Math.max(r0,r1),n),high);let a=ring(x,z,low,r0,n),b=ring(x,z,high,r1,n);for(let k=0;k<n;k++){let j=(k+1)%n;f([a[k],a[j],b[j],b[k]],shade(color,k%3*6-8));}f(b,shade(color,12));}
 function tree(x,z,k){box(x-2,z-2,4,4,23,'#B89472');let color=pal.trees[k%3];drum(x,z,22,39,12,19,color);drum(x,z,39,55,19,5,shade(color,7));}
 function person(x,z,h,k){box(x-2,z-2,4,4,8,k%2?pal.walls[0]:pal.walls[2],h);drum(x,z,h+8,h+12,2.7,2.7,'#E6C398',6);}
 function building(x,z,w,d,h,k){let color=pal.walls[k%4];box(x,z,w,d,h,color,0,pal.roofs[k%3]);
  for(let row=0;row<Math.floor((h-8)/22);row++)for(let col=0;col<Math.floor((w-8)/19);col++){let xx=x+8+col*19,hh=10+row*22;f([[xx,z+d+.2,hh],[xx+8,z+d+.2,hh],[xx+8,z+d+.2,hh+12],[xx,z+d+.2,hh+12]],'#BCE3EF',ink,.65);}
  for(let row=0;row<Math.floor((h-8)/22);row++)for(let col=0;col<Math.floor((d-8)/19);col++){let zz=z+8+col*19,hh=10+row*22;f([[x+w+.2,zz,hh],[x+w+.2,zz+8,hh],[x+w+.2,zz+8,hh+12],[x+w+.2,zz,hh+12]],'#BCE3EF',ink,.65);}
  box(x+w*.61,z+d*.2,14,14,8,'#EFF6EF',h);
 }
 function farmhouse(x,z,k){let color=pal.walls[k%4],roof=pal.roofs[k%3],w=66,d=55,h=37;box(x,z,w,d,h,color);
  const peak=[x+w/2,z,58],peakBack=[x+w/2,z+d,58];f([[x-5,z-5,h],peak,[...peakBack],[x-5,z+d+5,h]],shade(roof,-7));f([peak,[x+w+5,z-5,h],[x+w+5,z+d+5,h],peakBack],roof);
  f([[x+25,z+d+.3,0],[x+40,z+d+.3,0],[x+40,z+d+.3,23],[x+25,z+d+.3,23]],'#B18C6D');
 }
 function windmill(t){let x=825,z=180;box(x-15,z-15,30,30,73,pal.walls[3]);f([[x-22,z-22,73],[x+22,z-22,73],[x,z,100]],pal.roofs[0]);
  const center=[x,z+17,75],a=t*TAU*3;
  for(let j=0;j<4;j++){let q=a+j*TAU/4,point=(len,side)=>[center[0]+Math.cos(q)*len-Math.sin(q)*side,center[1]+.5,center[2]+Math.sin(q)*len+Math.cos(q)*side];f([point(5,-3),point(56,-5),point(56,5),point(5,3)],'#FFF4CD',ink,.9);}
  drum(x,z+18,72,78,4,4,'#B59254',6);
 }
 function clockTower(){let x=870,z=182;box(x-25,z-25,50,50,96,pal.walls[0]);box(x-32,z-32,64,64,10,pal.roofs[0],96);drum(x,z,106,133,34,4,pal.roofs[1],4);l([[x,z,133],[x,z,142]],ink,1.6);
  // Clock face is a small vertical octagon attached to the front facade.
  let pts=Array.from({length:12},(_,k)=>[x+Math.cos(k*TAU/12)*13,z+25.3,73+Math.sin(k*TAU/12)*13]);f(pts,'#FFF9DA');l([[x-8,z+25.5,73],[x,z+25.5,73],[x+4,z+25.5,81]],ink,1.1);
 }
 function bridge(t){let x=648,z=riverCenter(x)-116,d=232,span=d/3,deck=12;for(let j=0;j<3;j++)box(x-25,z+j*span,50,span,deck,pal.road,0,'#F0EDDC');for(let j=1;j<3;j++)box(x-29,z+j*span-4,58,8,20,'#91A7AC',-8);
  for(let j=0;j<3;j++)for(let side of [-1,1]){let xx=x+side*24,zz=z+j*span,arc=[];for(let k=0;k<=10;k++)arc.push([xx,zz+k*span/10,deck+5+21*Math.sin(Math.PI*k/10)]);l(arc,'#7D98A2',2);l([[xx,zz,deck+3],[xx,zz+span,deck+3]],'#8AA9AE',1.4);}
  for(let k=0;k<4;k++)person(x+(k%2?9:-9),z+25+(d-50)*(.5+.45*Math.sin(TAU*t*2+k)),deck,k);
 }
 function onMap(draw){const start=faces.length;draw();for(let k=start;k<faces.length;k++)faces[k].points=faces[k].points.map(([x,z,h])=>[Math.max(-10,Math.min(1090,x)),z,h]);}
 function boat(x,z){f([[x-24,z-8,4],[x+16,z-8,4],[x+28,z,4],[x+16,z+8,4],[x-24,z+8,4]],'#FFF2CE');box(x-10,z-5,18,10,10,pal.roofs[0],4);}
 function model(i){const t=mod(i,frames)/frames;return{t,camera:P.cameraAt(i,{frames,profile:config.viewProfile}),landmarks:anchors.map(a=>({...a,position:a.position.slice()})),windmillAngle:t*TAU*3,planeX:mod(t*2,1)*1680-300,carYield:t>=.31&&t<=.36,birdVisible:t>.55&&t<.73,events};}
 function scene(m){const t=m.t;faces=[];f(groundEdge,pal.ground,null,0,-1);
  if(city){quad(45,65,285,197,0,pal.grass);for(let j=0;j<9;j++)tree(80+j%3*95,97+Math.floor(j/3)*66,j);[[390,100,82,95,94],[505,131,84,70,120],[626,95,79,100,78],[735,123,72,80,105],[952,124,74,88,67]].forEach((b,k)=>building(...b,k));clockTower();}
  else{for(let row=0;row<3;row++)for(let col=0;col<4;col++){let x=35+col*160,z=22+row*84;quad(x,z,146,73,0,pal.fields[(row+col)%3]);for(let k=1;k<8;k++)l([[x+k*18,z+5,1],[x+k*18,z+68,1]],shade(pal.fields[(row+col)%3],12),1.1);}windmill(t);}
  quad(628,riverCenter(648)+116,40,704-riverCenter(648)-116,0,pal.road);quad(0,292,1080,45,0,pal.road);quad(0,704,1080,58,0,pal.road);quad(901,590,42,310,0,pal.road);
  for(let k=0;k<20;k++){quad(k*55,312,24,3,1,pal.mark);quad(k*55,731,24,3,1,pal.mark);}for(let k=0;k<6;k++)quad(894+k*9,698,4,30,1,pal.mark);
  const up=[],down=[];for(let x=-10;x<=1090;x+=20){let z=riverCenter(x);up.push([x,z-100,1]);down.unshift([x,z+100,1]);}f([...up,...down],pal.river,null);
  for(let k=0;k<42;k++){let x=mod(k*127+t*1080,1080),z=riverCenter(x)+(k%7-3)*24;l([[x,z,2],[Math.min(x+18+k%9,1090),z,2]],shade(pal.river,37),1);}
  for(let j=0;j<3;j++){let x=mod(t*1080*(j%2?-1:1)+j*360+90,1080);for(let copy of [-1080,0,1080])if(x+copy>-35&&x+copy<1115)onMap(()=>boat(x+copy,riverCenter(x)+(j-1)*42));}
  bridge(t);
  for(let j=0;j<15;j++){let x=35+j*73;if(Math.abs(x-648)>47)tree(x,635,j);if(Math.abs(x-648)>47&&x<1050)tree(x,272,j+1);}
  if(city)[[60,798,86,78,71],[189,785,87,93,109],[318,807,87,70,64],[448,788,91,91,126],[581,807,92,72,86],[717,785,96,93,107],[976,802,73,74,60]].forEach((b,k)=>building(...b,k));
  else{for(let j=0;j<6;j++){let x=70+j*161;if(x>890)continue;farmhouse(x,807,j);tree(x+91,842,j);}quad(790,790,85,87,0,pal.grass);}
  for(let k=0;k<6;k++){const phase=memphis&&k===0?(t<.31?t/.31*.425:t<.36?.425:.425+(t-.36)/.64*.575):t;let x=mod(phase*2160+k*179,1080);for(let copy of [-1080,0,1080])if(x+copy>-35&&x+copy<1115){let xx=x+copy,zz=713+(k%2)*29;onMap(()=>{box(xx,zz,22,12,10,pal.walls[k%4]);quad(xx+6,zz+1,10,10,11,'#C6E7EF');});}}
  for(let k=0;k<4;k++)person(919+(k%2?10:-8),memphis&&k===0?731+60*Math.sin(TAU*(t-.335)):716+Math.sin(TAU*t*2+k)*30,0,k);
  if(memphis){for(let j=0;j<2;j++){let x=mod(250+t*2160+j*360,1080),z=riverCenter(x)+30+Math.sin(TAU*t*4+j)*14;f([[x-8,z,3],[x+5,z-4,3],[x+10,z,3],[x+5,z+4,3]],pal.roofs[0],ink,1.2);l([[x-8,z,3],[x-14,z-4,3],[x-14,z+4,3],[x-8,z,3]],ink,1.2);}
   if(m.birdVisible){let u=(t-.55)/.18;for(let j=0;j<2;j++){let x=-130+1390*u-j*45,z=230+85*Math.sin(Math.PI*u)+j*30,h=177+j*8,w=13+7*Math.sin(TAU*t*30+j);l([[x-w,z+5,h+4],[x,z,h],[x+w,z+5,h+4]],ink,2.7);}}
  }
  // Planes leave the visible map before wrapping; three duplicated cloud periods avoid edge jumps.
  let px=m.planeX,pz=123+18*Math.sin(TAU*t*2),ph=167;f([[px-26,pz-3,ph],[px+27,pz-3,ph],[px+27,pz+3,ph],[px-26,pz+3,ph]],'#86B2BF');quad(px-5,pz-23,10,46,ph,'#86B2BF');
  for(let j=0;j<3;j++){let x=mod(j*350+t*1080*(1+j%2),1080),z=75+j*238;for(let copy of [-1080,0,1080])if(x+copy>-95&&x+copy<1175){let a=ring(x+copy,z,178,33,12).map(p=>[p[0],z+(p[1]-z)*.47,p[2]]);f(a,'#FFFEF1B8',null);}}
 }
 function text(s,x,y,size,color=ink,min=16){c.textAlign='center';c.textBaseline='middle';let actual=size;do{c.font=`500 ${actual}px "PingFang SC","Microsoft YaHei",sans-serif`;if(c.measureText(s).width<=940)break;actual--;}while(actual>=min);if(actual<min)throw Error('明信片文字过长，请改写文案或重新排版');c.fillStyle=color;c.fillText(s,x,y);}
 function badge(a,cam){let p=project(a.position,cam);p.x+=(a.offset||[0,0])[0];p.y+=(a.offset||[0,0])[1];let w=a.name.length*19+26;c.beginPath();c.roundRect(p.x-w/2,p.y-36,w,31,15);c.fillStyle='#FDFDF9F5';c.fill();c.strokeStyle='#DCE4DF';c.lineWidth=.8;c.stroke();text(a.name,p.x,p.y-20,18,ink,18);}
 function paintPattern(face){
  if(!memphis||!face.pattern)return;const xs=face.points.map(p=>p.x),ys=face.points.map(p=>p.y),x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);if((x1-x0)*(y1-y0)<200)return;
  c.save();c.clip();c.strokeStyle=ink+'32';c.fillStyle=ink+'44';c.lineWidth=1;
  if(face.pattern==='dots'){for(let x=Math.floor(x0/13)*13;x<x1;x+=13)for(let y=Math.floor(y0/13)*13;y<y1;y+=13){c.beginPath();c.arc(x,y,1.4,0,TAU);c.fill();}}
  else if(face.pattern==='stripes'){for(let x=x0-(y1-y0);x<x1;x+=13){c.beginPath();c.moveTo(x,y0);c.lineTo(x+y1-y0,y1);c.stroke();}}
  else{for(let y=y0;y<y1;y+=16){c.beginPath();for(let x=x0-5,k=0;x<=x1+5;x+=6,k++)k?c.lineTo(x,y+(k%2)*3):c.moveTo(x,y);c.stroke();}}c.restore();
 }
 function frame(i,{unmasked=false}={}){let m=model(i),sec=m.t*duration,scale=unmasked||config.reveal===false?1:Math.min(1,sec,sec<=duration-2?1:(duration-sec)/2);c.setTransform(1,0,0,1,0,0);c.clearRect(0,0,canvas.width,canvas.height);c.save();c.scale(canvas.width/1080,canvas.height/1080);c.fillStyle=BG;c.fillRect(0,0,1080,1080);
  c.save();c.beginPath();if(memphis)c.roundRect(540-484*scale,510-380*scale,968*scale,760*scale,Math.max(.01,42*scale));else c.rect(540-500*scale,510-390*scale,1000*scale,780*scale);c.clip();scene(m);
  for(const face of orderedFaces(faces,m.camera)){c.beginPath();face.points.forEach((p,k)=>k?c.lineTo(p.x,p.y):c.moveTo(p.x,p.y));if(face.closed)c.closePath();if(face.fill){c.fillStyle=face.fill;c.fill();}if(face.stroke){c.strokeStyle=face.stroke;c.lineWidth=face.width;c.lineJoin='round';c.lineCap='round';c.stroke();}if(face.closed)paintPattern(face);}
  if(memphis){
   // Erode the actual projected ground silhouette as well as the outer rounded aperture.
   const corners=groundEdge.map(v=>project(v,m.camera));
   const edges=corners.map((a,k)=>{let b=corners[(k+1)%corners.length];return{a,dx:b.x-a.x,dy:b.y-a.y,len:Math.hypot(b.x-a.x,b.y-a.y)||1};}),perimeter=edges.reduce((n,e)=>n+e.len,0);
   c.fillStyle=BG;for(const d of dust){let distance=d.x/1080*perimeter,k=0;while(k<edges.length-1&&distance>edges[k].len)distance-=edges[k++].len;const {a,dx,dy,len}=edges[k],u=distance/len,off=(d.y/1080-.5)*24;c.globalAlpha=.30+d.a*4;c.beginPath();c.arc(a.x+dx*u-dy/len*off,a.y+dy*u+dx/len*off,.5+d.s*1.65,0,TAU);c.fill();}c.globalAlpha=1;
  }
  if(config.labels!==false)for(const a of anchors)badge(a,m.camera);c.restore();
  if(!unmasked){
   if(memphis){
    // Stable dots erode the rounded frame edge; growing/shrinking coordinates use the same seed.
    for(let j=0;j<dust.length;j++){const d=dust[j],x=(d.x-540)/540,y=(d.y-540)/540;if(Math.max(Math.abs(x),Math.abs(y))<.90)continue;let px=540+x*484*scale,py=510+y*380*scale;c.globalAlpha=.30+d.a*5;c.fillStyle=BG;c.beginPath();c.arc(px,py,(2+d.s*5)*Math.max(.1,scale),0,TAU);c.fill();}
    if(config.reveal!==false&&(sec<1||sec>duration-2)){let q=sec<1?sec:Math.max(0,(duration-sec)/2);for(let j=0;j<100;j++){let d=dust[j],a=j*2.39996323,reach=(1-q)*(sec<1?32:80);c.globalAlpha=q*(1-q)*2.2;c.fillStyle=pal.fields[j%3];c.beginPath();c.arc(540+Math.cos(a)*reach+(d.x/1080-.5)*12,510+Math.sin(a)*reach*.7+(d.y/1080-.5)*12,.5+d.s*2,0,TAU);c.fill();}}
   }else{for(const d of dust){if(Math.min(Math.abs(d.x-40),Math.abs(d.x-1040),Math.abs(d.y-120),Math.abs(d.y-900))<20){c.globalAlpha=d.a;c.fillStyle=BG;c.beginPath();c.arc(d.x,d.y,d.s*2,0,TAU);c.fill();}}}
   c.globalAlpha=1;
   if(!memphis&&config.reveal!==false&&sec>duration-1){let q=sec-duration+1;for(let j=0;j<18;j++){let a=j*TAU/18;c.fillStyle=`rgba(85,104,92,${1-q})`;c.beginPath();c.arc(540+Math.cos(a)*q*95,510+Math.sin(a)*q*70,(1-q)*2.5,0,TAU);c.fill();}}
   text(memphis?'M E M P H I S   M I N I A T U R E   W O R L D':'S E A S O N A L   M A P   P O S T C A R D',540,60,14,memphis?ink:'#8AA29A',14);
   text(`${config.placeZh||'示例小镇'}  ${config.placeEn||'Sample Town'}`,540,958,25,ink,21);
   text(`${config.season} — ${config.moodZh||'风把日子吹得很慢'} / ${config.moodEn||'A quiet day drifts by'}`,540,999,20,ink,17);
   const geo=config.latitude==null||config.longitude==null?'示意地图 · 未标注真实坐标':`${Math.abs(config.latitude)}° ${config.latitude<0?'S':'N'}, ${Math.abs(config.longitude)}° ${config.longitude<0?'W':'E'}`;text(geo,540,1040,18,memphis?ink:'#839B94',17);
  }
  c.restore();return canvas;
 }
 return{frame,model,colors:pal,worldMode:'spatial',riverCenter,events,visualMechanisms:{roundedFrame:memphis,hardShadows:memphis,patterns:memphis?['dots','stripes','zigzag']:[],outline:ink}};
}
const api={make,riverCenter,N,H};if(typeof module!=='undefined')module.exports=api;else root.SpatialPostcard=api;
})(typeof window==='undefined'?globalThis:window);
