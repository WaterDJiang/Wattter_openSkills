/* Shared deterministic Node/browser director, no bitmap or generative-media inputs. */
(function(g){'use strict';
const F=typeof module!=='undefined'&&module.exports?require('./forest.js'):g.PaintedForest;
const C=typeof module!=='undefined'&&module.exports?require('./courier.js'):g.PaintedCourier;
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const smooth=(a,b,t)=>{t=clamp((t-a)/(b-a));return t*t*(3-2*t);};
function make(canvas,createCanvas){createCanvas=createCanvas||((w,h)=>{let el=document.createElement('canvas');el.width=w;el.height=h;return el;});let c=canvas.getContext('2d'),forest=F.makeForest(createCanvas),hero=C.makeCourier(c);
 function frame(i){let t=clamp(i,0,359)/30,s=C.state(t),zoom=1+.045*smooth(0,12,t),cam=16*smooth(0,12,t);if(c.reset)c.reset();else{c.setTransform(1,0,0,1,0,0);c.globalAlpha=1;c.globalCompositeOperation='source-over';}c.clearRect(0,0,1920,1080);c.save();c.translate(960,540);c.scale(zoom,zoom);c.translate(-960-cam*.2,-540);forest.drawBase(c,t,cam);
  c.save();c.translate(s.x,s.y+4);c.scale(s.scale,1);let shadow=c.createRadialGradient(0,0,1,0,0,70);shadow.addColorStop(0,'#233c3549');shadow.addColorStop(1,'#233c3500');c.scale(1,.18);c.fillStyle=shadow;c.fillRect(-80,-80,160,160);c.restore();hero.draw(s);
  if(!s.release){let p=C.birdPoint(s);hero.bird(...p,1.10,t,false);}else{let p=C.birdPoint(C.state(6.15)),u=t-6.15;hero.bird(p[0]+u*54,p[1]-u*38-Math.sin(u*.7)*40,1.1-u*.04,t,true);}
  // Pollen stays sparse in the lit opening, with frame-indexed analytic paths.
  for(let j=0;j<23;j++){let xx=700+(j*63+t*(3+j%5))%850,yy=120+(j*89)%650+Math.sin(t*.9+j)*8;c.fillStyle=j%3?'#f7e9ad66':'#d0b46a99';c.beginPath();c.ellipse(xx,yy,j%3?1.2:3.4,j%3?1.2:1.2,t*.4+j,0,Math.PI*2);c.fill();}
  forest.drawFront(c,t,cam);c.restore();
  // Small cinematic title in naturally dark foreground, away from the bird path.
  let a=smooth(9.1,10.2,t);if(a){c.save();c.globalAlpha=a;c.textBaseline='alphabetic';c.textAlign='left';c.fillStyle='#f5e4b4';c.font='500 56px "Songti SC", "STSong", serif';c.fillText('晚风来信',200,943);c.fillStyle='#d2c99b';c.font='15px Georgia, serif';c.fillText('A LETTER ON THE EVENING WIND',202,978);c.restore();}
 }
 return{frame,state:C.state,birdPoint:C.birdPoint,width:1920,height:1080,totalFrames:360,fps:30,paintStats:forest.stats};
}
if(typeof module!=='undefined'&&module.exports)module.exports={make};else g.Handpainted={make};
})(typeof globalThis!=='undefined'?globalThis:this);
