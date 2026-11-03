/* Original small courier. World-space stance anchors and shared wrist/prop coordinates. */
(function(g){'use strict';
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v)),lerp=(a,b,t)=>a+(b-a)*t;
const smooth=(a,b,t)=>{t=clamp((t-a)/(b-a));return t*t*(3-2*t);};
function rootX(t){if(t<=2.45)return 570+t*100;let u=clamp((t-2.45)/.7);return 815+70*u-35*u*u;}
function ik(a,b,l1,l2,side=1){let dx=b[0]-a[0],dy=b[1]-a[1],d=Math.max(1,Math.hypot(dx,dy)),theta=Math.atan2(dy,dx)+side*Math.acos(clamp((d*d+l1*l1-l2*l2)/(2*d*l1),-1,1));return[a[0]+Math.cos(theta)*l1,a[1]+Math.sin(theta)*l1];}
function state(t){let raise=smooth(3.45,5.25,t),reach=smooth(5.2,6.12,t),lower=smooth(8.2,10.5,t),walk=1-smooth(2.45,3.15,t),period=1/1.55,scale=1.18,x=rootX(t),feet=[];
 for(let j=0;j<2;j++){let offset=j*period*.5,q=(t-offset)/period,k=Math.floor(q),phase=q-k,contact=offset+k*period,next=contact+period,front=22;
  let a=rootX(contact)+front*scale,b=rootX(next)+front*scale,stance=phase<.6,travel=smooth(.6,1,phase),wx=stance?a:lerp(a,b,travel),fy=stance?0:-Math.sin(Math.PI*travel)*30*walk,settle=smooth(2.5,3.15,t);
  feet.push([lerp((wx-x)/scale,j?17:-16,settle),fy]);
 }
 let wrist=[lerp(77,80,raise)+reach*52,lerp(-162,-290,raise)+reach*27];wrist=[lerp(wrist[0],64,lower),lerp(wrist[1],-165,lower)];
 let bob=-Math.abs(Math.sin(t*Math.PI*3.1))*3.5*walk+Math.sin(t*2)*.7;for(let foot of feet)foot[1]-=bob/scale;
 return{t,x,y:936+bob,scale,walk,feet,wrist,gaze:smooth(3.3,5.3,t),release:t>=6.15,step:t*2*Math.PI*1.55};
}
function birdPoint(s){return[s.x+(s.wrist[0]+14)*s.scale,s.y+(s.wrist[1]-13)*s.scale];}
function makeCourier(c){
 function p(pts,fill,stroke=null,w=1){c.beginPath();pts.forEach((v,i)=>i?c.lineTo(...v):c.moveTo(...v));c.closePath();if(fill){c.fillStyle=fill;c.fill();}if(stroke){c.strokeStyle=stroke;c.lineWidth=w;c.stroke();}}
 function ell(a,b,rx,ry,color,rot=0){c.beginPath();c.ellipse(a,b,rx,ry,rot,0,Math.PI*2);c.fillStyle=color;c.fill();}
 function stroke(pts,col,w){c.beginPath();c.moveTo(...pts[0]);pts.slice(1).forEach(v=>c.lineTo(...v));c.strokeStyle=col;c.lineWidth=w;c.lineJoin='round';c.lineCap='round';c.stroke();}
 function limb(a,b,d,fill,w){stroke([a,b,d],'#4b443c',w+1.2);stroke([a,b,d],fill,w);stroke([[a[0]-2,a[1]+2],[b[0]-2,b[1]+2],[d[0]-2,d[1]+2]],'#794e4366',w*.28);stroke([[b[0]+3,b[1]-3],[d[0]+3,d[1]-3]],'#f2be8588',1.6);}
 function boot(a,b,lift){c.save();c.translate(a,b);c.rotate(lift*.002);c.beginPath();c.moveTo(-10,-21);c.lineTo(8,-22);c.lineTo(11,-7);c.bezierCurveTo(17,-6,29,-6,28,4);c.quadraticCurveTo(6,9,-12,5);c.closePath();c.fillStyle='#50473c';c.fill();p([[-10,-20],[-3,-21],[0,-5],[-8,-2]],'#73614a');stroke([[-11,5],[26,5]],'#2d3936',2.6);stroke([[-3,-10],[9,-11]],'#b19a6c',1.2);stroke([[1,-7],[11,-8]],'#977a54',1);c.restore();}
 function draw(s){c.save();c.translate(s.x,s.y);c.scale(s.scale,s.scale);
  // Rear coat sleeve and planted legs are behind the main silhouette.
  for(let j=0;j<2;j++){let hip=[j?16:-15,-101],foot=s.feet[j],ankle=[foot[0],foot[1]-12],knee=ik(hip,ankle,44,46,-1);stroke([hip,knee,ankle],j?'#42504b':'#354b48',18);stroke([[hip[0]-3,hip[1]],[knee[0]-3,knee[1]],[ankle[0]-3,ankle[1]]],'#213c3c88',6);stroke([[knee[0]+5,knee[1]],[ankle[0]+5,ankle[1]-8]],'#70806b',1.2);boot(...foot,-foot[1]);}
  let back=[-45-Math.sin(s.step)*16*s.walk,-162+Math.cos(s.step)*7*s.walk],bs=[-28,-220],be=ik(bs,back,56,62,-1);limb(bs,be,back,'#a65d45',19);ell(back[0],back[1]+2,8,11,'#bd8c68',-.2);
  // Wind-lifted short cape, lined at the rim.
  let flutter=Math.sin(s.t*2.8)*3+Math.sin(s.step)*s.walk*4;
  c.beginPath();c.moveTo(-16,-229);c.bezierCurveTo(-38,-228,-50,-206,-55,-175);c.lineTo(-72,-122+flutter);c.quadraticCurveTo(-43,-113,-29,-125);c.lineTo(-8,-213);c.closePath();c.fillStyle='#8d4e3e';c.fill();stroke([[-63,-125+flutter],[-45,-121],[-30,-125]],'#d29c64',2);p([[-41,-210],[-42,-151],[-57,-125],[-69,-123+flutter]],'#6c483e77');
  // Coat has a narrow waist, asymmetric hem, directional light and fold shapes.
  c.beginPath();c.moveTo(-25,-226);c.quadraticCurveTo(-42,-215,-37,-175);c.lineTo(-43,-99);c.quadraticCurveTo(2,-82,43,-101);c.lineTo(32,-185);c.quadraticCurveTo(39,-218,17,-227);c.closePath();let coat=c.createLinearGradient(-42,-160,45,-160);coat.addColorStop(0,'#a85b43');coat.addColorStop(.57,'#c27a50');coat.addColorStop(1,'#e8a56b');c.fillStyle=coat;c.fill();c.strokeStyle='#6b5040';c.lineWidth=1;c.stroke();c.save();c.clip();for(let k=0;k<150;k++){let xx=-42+(k*17.171%84),yy=-226+(k*31.739%140);stroke([[xx,yy],[xx+1,yy+5+k%7]],k%2?'#f6cf9621':'#6b4c3b14',.6+k%3*.2);}c.restore();
  p([[-25,-217],[-12,-196],[-16,-133],[-8,-99],[-39,-103],[-34,-167]],'#9b5c4599');p([[20,-209],[28,-170],[17,-119],[27,-97],[39,-102],[31,-173]],'#f0b67a88');p([[5,-190],[10,-163],[3,-120],[10,-92],[16,-94],[10,-139]],'#9c614699');stroke([[-30,-109],[-8,-103],[17,-102],[33,-108]],'#efbe8188',1.2);stroke([[16,-208],[16,-121]],'#825c42',1.1);for(let j=0;j<4;j++)ell(21,-195+j*23,1.7,2,'#e2c592');
  // Sleeve-side pocket, stitching and leather satchel.
  stroke([[-27,-143],[-12,-140],[-11,-122],[-24,-126]],'#79523d',1);stroke([[-26,-142],[-14,-139]],'#e3a76c',.8);stroke([[-30,-218],[24,-133]],'#4f4b38',7);stroke([[-28,-218],[26,-133]],'#bd9b62',1.1);
  c.save();c.translate(-39,-132);c.rotate(Math.sin(s.t*3)*.02+s.walk*Math.sin(s.step)*.05);c.beginPath();c.moveTo(-16,-6);c.quadraticCurveTo(6,-11,24,-4);c.lineTo(22,27);c.quadraticCurveTo(1,35,-16,25);c.closePath();c.fillStyle='#987044';c.fill();p([[-15,-2],[21,0],[16,15],[-14,12]],'#c89a57');stroke([[-12,18],[-11,25],[16,26]],'#d3ac6d',1);ell(5,13,3,4,'#564f39');stroke([[5,12],[5,18]],'#d4bc80',1.1);c.restore();
  // A three-quarter head with a jaw, ear, planes and an actual upturn of the chin.
  c.save();c.translate(0,-275);c.rotate(-s.gaze*.12);c.translate(0,275);
  c.beginPath();c.moveTo(-28,-290);c.bezierCurveTo(-32,-315,-10,-332,15,-321);c.bezierCurveTo(37,-314,39,-295,35,-282);c.lineTo(45,-270);c.quadraticCurveTo(46,-265,36,-264);c.quadraticCurveTo(32,-239,14,-234);c.quadraticCurveTo(-11,-230,-22,-250);c.closePath();c.fillStyle='#e2ba8b';c.fill();
  p([[-24,-294],[-13,-289],[-13,-254],[4,-240],[19,-237],[9,-233],[-13,-241],[-22,-256]],'#bb886a');p([[27,-293],[33,-284],[30,-269],[39,-268],[34,-264],[30,-250],[22,-240],[18,-239],[25,-258]],'#f5d5a18a');
  ell(-20,-270,9,12,'#d0a17a',-.15);stroke([[-23,-271],[-18,-275],[-17,-264]],'#9c7457',1);ell(17,-261,8,4,'#d6927355');
  c.beginPath();c.moveTo(-29,-263);c.bezierCurveTo(-46,-291,-34,-322,-13,-328);c.quadraticCurveTo(17,-341,35,-312);c.quadraticCurveTo(22,-317,9,-300);c.lineTo(5,-311);c.quadraticCurveTo(-8,-290,-17,-284);c.lineTo(-17,-267);c.closePath();c.fillStyle='#3d4035';c.fill();
  stroke([[-30,-302],[-23,-315],[-13,-320]],'#6a6243',2);stroke([[-18,-295],[-9,-307],[1,-313]],'#796c4999',1.2);stroke([[-27,-277],[-23,-284]],'#7b6c4a',1.4);
  // Soft peaked cap, sewn brim and a restrained highlight.
  c.beginPath();c.moveTo(-36,-305);c.bezierCurveTo(-43,-328,-17,-344,6,-337);c.bezierCurveTo(25,-335,33,-322,32,-311);c.lineTo(44,-305);c.quadraticCurveTo(25,-297,-36,-305);c.closePath();c.fillStyle='#bd995a';c.fill();p([[-32,-313],[-30,-329],[-12,-338],[5,-337],[-7,-330],[-14,-314]],'#dfc484');p([[-32,-308],[16,-313],[42,-305],[26,-302]],'#796e48');stroke([[-30,-310],[-7,-314],[18,-315]],'#f1d69b',1.1);stroke([[0,-336],[7,-328],[10,-316]],'#9d834e',1);
  let blink=Math.floor(s.t*30)%139<4&&s.t>1,gx=s.gaze*1.3,gy=-s.gaze*2.5;
  stroke([[4,-283+gy],[12,-285+gy]],'#705a43',1.5);stroke([[28,-283+gy],[33,-282+gy]],'#705a43',1.2);
  if(blink){stroke([[5,-275],[12,-275]],'#534b38',1.5);stroke([[29,-275],[34,-275]],'#534b38',1.2);}else{ell(9+gx,-275+gy,2.1,3.6,'#344438');ell(30+gx,-274+gy,1.7,3.3,'#344438');ell(9.4+gx,-276+gy,.65,.95,'#fff0c5');}
  stroke([[25,-256],[29,-254],[34,-258]],'#925f4e',1.1);stroke([[16,-239],[23,-240]],'#f1d3a2',1.4);
  c.restore();
  // Neck scarf folds; tail rooted at knot, with muted underside.
  c.beginPath();c.moveTo(-24,-238);c.quadraticCurveTo(5,-229,27,-239);c.lineTo(25,-222);c.quadraticCurveTo(-2,-215,-26,-227);c.closePath();c.fillStyle='#d7ad56';c.fill();p([[-26,-229],[7,-224],[25,-230],[25,-223],[4,-217],[-25,-225]],'#ad8b42');stroke([[-20,-233],[2,-228],[22,-235]],'#f0d18b',1.5);p([[-20,-229],[-48,-225],[-91,-207+flutter],[-75,-203+flutter],[-43,-215],[-15,-220]],'#d8b263');p([[-48,-222],[-78,-209+flutter],[-65,-209+flutter],[-34,-217]],'#f2d390');
  const sh=[27,-219],wr=s.wrist,el=ik(sh,wr,68,70,1);limb(sh,el,wr,'#cd8959',20);let ang=Math.atan2(wr[1]-el[1],wr[0]-el[0]);c.save();c.translate(...wr);c.rotate(ang);
  c.beginPath();c.moveTo(-4,-9);c.lineTo(7,-9);c.quadraticCurveTo(17,-12,20,-6);c.lineTo(22,2);c.quadraticCurveTo(22,10,11,10);c.lineTo(-3,8);c.closePath();c.fillStyle='#edc695';c.fill();p([[0,4],[20,4],[16,10],[-3,8]],'#ca9c75');stroke([[-4,-10],[-4,10]],'#eed09b',4);ell(11,-8,4,6,'#f0c998',-.6);
  if(s.release){for(let j=0;j<3;j++)stroke([[14,j*3-3],[24+j*2,j*4-8]],'#f1c99a',2.4);}else{stroke([[15,-3],[21,-4]],'#c18b69',.7);stroke([[15,0],[21,0]],'#c18b69',.7);}
  c.restore();c.restore();
 }
 function bird(x,y,scale,t,flying){c.save();c.translate(x,y);c.rotate(flying?-.22+Math.sin(t*2)*.035:-.06);c.scale(scale,scale);let flap=flying?Math.sin((t-6.15)*Math.PI*4.1):-.4;
  p([[-25,3],[0,-4],[25,1],[40,-9],[27,12],[1,15]],'#e3d8ad','#6f8068',.7);p([[-8,3],[-29,-18-flap*21],[15,1]],'#fff1ca','#8d9877',.7);p([[3,7],[-2,-26-flap*23],[26,3]],'#f9e9b7','#8d9877',.7);stroke([[-2,10],[27,4],[38,-7]],'#b7b28d',.8);c.restore();}
 return{draw,bird};
}
const api={state,birdPoint,makeCourier,rootX};if(typeof module!=='undefined'&&module.exports)module.exports=api;else g.PaintedCourier=api;
})(typeof globalThis!=='undefined'?globalThis:this);
