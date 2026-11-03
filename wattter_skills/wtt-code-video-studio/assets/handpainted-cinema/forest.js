/* Original procedural painting. Pigment marks belong to individual forms, not the whole screen. */
(function(g){'use strict';
function rng(s){return()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const mix=(a,b,t)=>a.map((v,i)=>Math.round(v+(b[i]-v)*clamp(t)));
const css=(a,alpha=1)=>`rgba(${a[0]},${a[1]},${a[2]},${alpha})`;
function poly(x,pts,fill){x.beginPath();pts.forEach((p,i)=>i?x.lineTo(...p):x.moveTo(...p));x.closePath();x.fillStyle=fill;x.fill();}
function line(x,pts,color,width){x.beginPath();x.moveTo(...pts[0]);for(let i=1;i<pts.length;i++)x.lineTo(...pts[i]);x.strokeStyle=color;x.lineWidth=width;x.lineCap='round';x.lineJoin='round';x.stroke();}
function dab(x,r,a,b,size,color,angle=0,stretch=1){let pts=[];let ca=Math.cos(angle),sa=Math.sin(angle);for(let k=0;k<7;k++){let t=k/7*Math.PI*2,rr=.63+r()*.58,xx=Math.cos(t)*size*rr,yy=Math.sin(t)*size*.5*rr*stretch;pts.push([a+ca*xx-sa*yy,b+sa*xx+ca*yy]);}poly(x,pts,color);}
function makeForest(createCanvas,W=1920,H=1080){
 let count=0;
 function layer(f){let cv=createCanvas(W,H),x=cv.getContext('2d');f(x);return cv;}
 function crown(x,r,a,b,rx,ry,depth=1,countMarks=1200){
  // The leaf mass has a shadow core, broken silhouette and a directed sunward cap.
  const dark=depth>.8?[21,60,54]:[90,130,105],mid=depth>.8?[57,100,68]:[137,161,112],light=depth>.8?[156,178,84]:[196,199,132];
  let pts=[];for(let j=0;j<26;j++){let q=j/26*6.283,rr=.82+r()*.25;pts.push([a+Math.cos(q)*rx*rr,b+Math.sin(q)*ry*rr]);}poly(x,pts,css(dark));
  for(let i=0;i<countMarks;i++){
   let u=r()*2-1,v=r()*2-1;if(u*u+v*v>1)continue;
   let z=Math.sqrt(Math.max(0,1-u*u-v*v)),lit=clamp(.18+.25*u-.5*v+.48*z+(r()-.5)*.43),col=lit<.58?mix(dark,mid,lit/.58):mix(mid,light,(lit-.58)/.42);
   let size=3+r()*8,px=a+u*rx*(.98+(r()-.5)*.04),py=b+v*ry;
   dab(x,r,px,py,size,css(col,.76+r()*.24),-.6+u*.65+(r()-.5)*1.6,.5+r()*.7);count++;
   if(lit>.78&&r()<.18)line(x,[[px,py],[px+size*.5,py-size*.5]],css(mix(col,[232,213,133],.32),.65),.8);
  }
 }
 function tree(x,r,a,base,top,width,depth=1){
  let bend=(r()-.5)*55,pts=[[a-width*.64,base],[a-width*.43,base-180],[a-width*.45+bend*.5,top+140],[a-width*.25+bend,top],[a+width*.2+bend,top],[a+width*.36+bend*.5,top+140],[a+width*.45,base-180],[a+width*.72,base]];
  x.save();x.beginPath();pts.forEach((p,i)=>i?x.lineTo(...p):x.moveTo(...p));x.closePath();x.clip();
  let col=depth>.8?[[17,48,46],[67,83,58],[137,138,89]]:[[91,130,111],[132,155,122],[187,187,139]],grad=x.createLinearGradient(a-width,0,a+width*.7,0);grad.addColorStop(0,css(col[0]));grad.addColorStop(.55,css(col[1]));grad.addColorStop(1,css(col[2]));x.fillStyle=grad;x.fillRect(a-width*2,top-10,width*4,base-top+20);
  for(let j=0;j<1200*depth;j++){let yy=top+r()*(base-top),xx=a+(r()-.5)*width*1.6+bend*(1-(yy-top)/(base-top));let highlight=r()>.6;dab(x,r,xx,yy,1+r()*3,css(highlight?mix(col[1],col[2],r()):col[0],.1+r()*.27),Math.PI/2,2+r()*4);}
  for(let j=0;j<22;j++){let xx=a+(r()-.5)*width,yy=top+r()*(base-top);line(x,[[xx,yy],[xx+(r()-.5)*10,yy+30+r()*85]],css(col[0],.1+r()*.25),1+r()*2);}
  for(let j=0;j<360;j++){let xx=a-width*.4+r()*width*.4,yy=base-r()*(base-top)*.8;dab(x,r,xx,yy,2+r()*5,css([76,112,62],.25+r()*.55),-.6,1.1);}
  x.restore();
  if(depth>.8){
   x.beginPath();x.moveTo(a,top+240);x.bezierCurveTo(a-70,top+175,a-125,top+150,a-165,top+75);x.strokeStyle=css(col[1]);x.lineWidth=width*.25;x.lineCap='round';x.stroke();
   poly(x,[[a-width*.44,base-45],[a-width*.9,base+7],[a-width*.15,base-4],[a+width*.9,base+10],[a+width*.4,base-40]],css(col[1]));
   for(let k=0;k<36;k++){let xx=a+(r()-.5)*width*2,yy=base+r()*13;line(x,[[xx,yy],[xx+(r()-.5)*12,yy-5-r()*12]],'#4d6d43',.6+r());}
  }
 }
 const sky=layer(x=>{let grad=x.createLinearGradient(0,0,0,H);grad.addColorStop(0,'#a5bcb0');grad.addColorStop(.45,'#f5e9bd');grad.addColorStop(.76,'#e7d7a0');grad.addColorStop(1,'#698d7a');x.fillStyle=grad;x.fillRect(0,0,W,H);let sun=x.createRadialGradient(1190,400,20,1190,400,660);sun.addColorStop(0,'#fff2bdcc');sun.addColorStop(1,'#fff2bd00');x.fillStyle=sun;x.fillRect(0,0,W,H);
  let r=rng(44);for(let i=0;i<14000;i++){let yy=r()*H,xx=r()*W;dab(x,r,xx,yy,1+r()*7,i%2?'#fff3ce08':'#638d7d05',0,.2);}});
 const far=layer(x=>{let r=rng(15);for(let i=0;i<34;i++){let a=i*66-70,yy=940+r()*70;tree(x,r,a,yy,100+r()*200,8+r()*19,.4);for(let j=0;j<3;j++)crown(x,r,a+(r()-.5)*110,210+j*100+r()*70,75+r()*80,40+r()*50,.45,460);}
  x.globalCompositeOperation='destination-in';let fade=x.createLinearGradient(0,550,0,845);fade.addColorStop(0,'#ffffffff');fade.addColorStop(1,'#ffffff00');x.fillStyle=fade;x.fillRect(0,0,W,H);x.globalCompositeOperation='source-over';
  let mist=x.createLinearGradient(0,150,0,900);mist.addColorStop(0,'#efdfaf00');mist.addColorStop(.68,'#f8e8bba6');mist.addColorStop(1,'#d9d8a8ee');x.fillStyle=mist;x.fillRect(0,0,W,H);
 });
 const middle=layer(x=>{let r=rng(477);
  // Long trunks create open vertical intervals instead of a wall of texture.
  for(let i=0;i<12;i++){let a=[-40,110,236,380,500,625,1460,1550,1680,1800,1940,2030][i],base=810+r()*100;tree(x,r,a,base,-120,26+r()*36,.75);}
  for(let j=0;j<40;j++){let trunk=(j<22?[-40,110,236,380,500,625]:[1460,1550,1680,1800,1940,2030])[(r()*6)|0],a=trunk+(r()-.5)*150,b=180+r()*450;let rx=45+r()*100;x.beginPath();x.moveTo(trunk,b+75);x.quadraticCurveTo(trunk+(a-trunk)*.4,b+20,a,b+7);x.strokeStyle='#41694e';x.lineWidth=3+r()*5;x.lineCap='round';x.stroke();crown(x,r,a,b,rx,rx*.58,.9,680);}
  // Grounded understory follows the forest edge; the central light pocket stays open.
  for(let j=0;j<26;j++){let a=j<15?r()*760:1430+r()*500,b=740+r()*70;crown(x,r,a,b,65+r()*75,28+r()*30,.7,450);}
 });
 const ground=layer(x=>{let r=rng(887);let grad=x.createLinearGradient(0,730,0,H);grad.addColorStop(0,'#b9b883');grad.addColorStop(.4,'#7d9567');grad.addColorStop(1,'#294d40');poly(x,[[0,780],[450,767],[850,798],[1190,761],[1550,780],[1920,746],[1920,1080],[0,1080]],grad);
  // Sunlit bank/path, with a curved shore.
  x.beginPath();x.moveTo(500,1080);x.bezierCurveTo(480,930,760,920,780,861);x.bezierCurveTo(800,815,1050,810,1150,796);x.bezierCurveTo(930,870,1190,901,1050,974);x.lineTo(1080,1080);x.closePath();x.fillStyle='#b6b284';x.fill();
  for(let j=0;j<17000;j++){let xx=r()*W,yy=770+r()*310,depth=(yy-770)/310;let bright=xx>500&&xx<1100;let color=bright?(r()>.48?'#e2cc8d26':'#667c572f'):(r()>.5?'#a7b57639':'#254d3c3f');dab(x,r,xx,yy,1+r()*(2+depth*8),color,-.1,1.2);}
  // Pond with reflected forest silhouettes, all clipped to its own form.
  x.save();x.beginPath();x.moveTo(1030,1080);x.bezierCurveTo(1285,976,1000,864,1280,806);x.bezierCurveTo(1450,767,1630,843,1920,802);x.lineTo(1920,1080);x.closePath();x.clip();let water=x.createLinearGradient(0,800,0,1080);water.addColorStop(0,'#8eaf91');water.addColorStop(.45,'#708f7a');water.addColorStop(1,'#244e4e');x.fillStyle=water;x.fillRect(950,760,970,320);
  for(let i=0;i<9000;i++){let xx=1000+r()*920,yy=800+r()*280,shine=Math.abs(xx-1390)<150,cc=shine?'#e6dcaa18':'#234e5020';dab(x,r,xx,yy,2+r()*20,cc,0,.12);}
  for(let i=0;i<9;i++){let xx=1490+i*63;poly(x,[[xx,790],[xx+13,790],[xx-10,1080],[xx-32,1080]],'#183f4423');}
  x.restore();
  // Individual grasses are rooted in soil, scaled by depth, not laid over the pond.
  for(let i=0;i<2600;i++){let xx=r()*W,yy=810+r()*270;if(xx>1100&&yy>830)continue;let depth=(yy-770)/310,h=(5+r()*20)*depth,wind=(r()-.5)*15,col=xx>600&&xx<1100?['#657a4d','#8e9a5d','#b8bc75','#d9c98a'][i%4]:['#294f40','#42684a','#8da16a'][i%3];x.beginPath();x.moveTo(xx,yy);x.quadraticCurveTo(xx+wind*.4,yy-h,xx+wind,yy-h*1.2);x.strokeStyle=col;x.lineWidth=.6+depth*.9;x.stroke();}
  for(let i=0;i<100;i++){let xx=400+r()*700,yy=800+r()*180;line(x,[[xx,yy],[xx+2,yy-9]],'#81925b',.7);dab(x,r,xx+2,yy-11,1.5,'#f4e1aa',0);}
 });
 const frameTrees=layer(x=>{let r=rng(2026);poly(x,[[1630,1080],[1710,990],[1745,905],[1830,850],[1920,833],[1920,1080]],'#325b44');
  for(let k=0;k<2300;k++){let xx=1720+r()*200,yy=860+r()*220;dab(x,r,xx,yy,1+r()*5,k%2?'#6c855149':'#163f3940',-.4,1.8);}
 tree(x,r,110,1040,-100,126,1.2);tree(x,r,1850,1080,-200,153,1.2);tree(x,r,371,870,-100,45,.95);tree(x,r,1612,806,-100,53,.95);
  // Canopy arches around the light opening and does not fill it.
  for(let j=0;j<31;j++){let a=j<16?-70+r()*880:1380+r()*650,b=-45+r()*210;let rx=95+r()*140;crown(x,r,a,b,rx,60+r()*90,1.15,1700);}
  for(let j=0;j<9;j++){let a=r()*510,b=290+r()*280;crown(x,r,a,b,55+r()*100,35+r()*55,1.2,1050);}
  for(let j=0;j<7;j++){let a=1660+r()*310,b=250+r()*320;crown(x,r,a,b,40+r()*95,30+r()*45,1.2,1000);}
  // Hanging stems and lancet leaves, attached to a shared curved centerline.
  for(let j=0;j<15;j++){let a=450+j*66+(r()-.5)*35,len=80+r()*210;let pts=[];for(let q=0;q<12;q++)pts.push([a+Math.sin(q*.4+j)*9,q/11*len]);line(x,pts,'#274e3c',1.5);for(let k=1;k<15;k++){let yy=k/15*len,xx=a+Math.sin(k*.3+j)*8,side=k%2?1:-1;poly(x,[[xx,yy],[xx+side*14,yy+8],[xx+side*20,yy+23],[xx+side*5,yy+16]],k%3?'#315e42':'#547a4b');}}
 });
 const foreground=layer(x=>{let r=rng(33);
  for(let j=0;j<1600;j++){let xx=r()*W,yy=1080+r()*60,h=35+r()*115;let central=xx>560&&xx<1350;if(central)h*=.42;x.beginPath();x.moveTo(xx,yy);x.quadraticCurveTo(xx+(r()-.5)*70,yy-h*.8,xx+(r()-.5)*90,yy-h);x.strokeStyle=['#173d3b','#214c40','#345d45','#55784c'][j%4];x.lineWidth=.8+r()*2.2;x.stroke();}
  function fern(a,b,scale,tilt){x.save();x.translate(a,b);x.rotate(tilt);x.scale(scale,scale);line(x,[[0,0],[5,-50],[14,-100],[21,-148]],'#527348',2);for(let k=1;k<13;k++){let yy=-k*11,xx=k*k*.12,wide=Math.sin(k/14*Math.PI)*44;for(let side of [-1,1]){x.beginPath();x.moveTo(xx,yy);x.bezierCurveTo(xx+side*wide*.4,yy-18,xx+side*wide,yy-21,xx+side*wide,yy-28);x.quadraticCurveTo(xx+side*wide*.8,yy-3,xx,yy);x.fillStyle=k%3?'#2d6248':'#477449';x.fill();line(x,[[xx,yy],[xx+side*wide*.8,yy-20]],'#71905b88',.7);}}x.restore();}
  for(let i=0;i<17;i++)fern(i<9?r()*500:1500+r()*450,1040+r()*130,.7+r()*.8,(r()-.5)*1.2);
  for(let j=0;j<180;j++){let xx=r()<.5?r()*490:1530+r()*390,yy=960+r()*120;dab(x,r,xx,yy,3+r()*10,['#284d3f','#496641','#729052'][j%3],-.6,1.3);}
 });
 const grain=layer(x=>{let r=rng(111);for(let j=0;j<70000;j++){x.fillStyle=j%2?'#fff3c806':'#132e3406';x.fillRect(r()*W,r()*H,.5+r()*1.2,.5+r()*.7);}});
 function drawBase(c,t,cam=0){c.drawImage(sky,0,0);c.drawImage(far,-cam*.16,0);c.drawImage(middle,-cam*.38,0);c.drawImage(ground,0,0);
  // Restrained translucent rays, without hard polygon edges.
  c.save();c.globalCompositeOperation='screen';let shaft=c.createLinearGradient(1300,90,920,970);shaft.addColorStop(0,'#ffe4a416');shaft.addColorStop(1,'#ffe4a400');poly(c,[[1280,-80],[1390,-80],[1100,1010],[740,1010]],shaft);c.restore();
  for(let k=0;k<28;k++){let a=1240+Math.sin(k*2.5)*200,b=844+k*7,shift=Math.sin(t*.6+k)*6;line(c,[[a+shift,b],[a+26+k%4*19+shift,b]],k%4?'#c5ce9e20':'#f1dca543',.7+k/50);}
 }
 function drawFront(c,t,cam=0){c.drawImage(frameTrees,-cam*.7,0);c.drawImage(foreground,-cam,0);c.drawImage(grain,0,0);}
 return{drawBase,drawFront,stats:{leafMarks:count,layers:7,seed:20261103}};
}
if(typeof module!=='undefined'&&module.exports)module.exports={makeForest,rng,poly,line,css,mix};else g.PaintedForest={makeForest,rng,poly,line,css,mix};
})(typeof globalThis!=='undefined'?globalThis:this);
