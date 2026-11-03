/* Original WTT examples, 2026-11-03. No external assets, clocks, or mutable particle simulation. */
(()=>{
'use strict';
const clamp=x=>Math.max(0,Math.min(1,x)), ease=x=>{x=clamp(x);return x*x*(3-2*x);}, lerp=(a,b,t)=>a+(b-a)*t;
const rand=n=>{let x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x);};
function text(c,s,x,y,size=28,color='#183c46',align='left',weight=500){c.font=`${weight} ${size}px "PingFang SC",sans-serif`;c.fillStyle=color;c.textAlign=align;c.textBaseline='middle';c.fillText(s,x,y);}
function rect(c,x,y,w,h,r,color){c.fillStyle=color;c.beginPath();c.roundRect(x,y,w,h,r);c.fill();}
function line(c,points,color,width=2){c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';c.lineJoin='round';c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.stroke();}
function circle(c,x,y,r,color){c.fillStyle=color;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fill();}
function header(c,k,title,dark=false){text(c,k,52,39,15,dark?'#90b7b8':'#5a7e7b','left',700);text(c,title,50,94,42,dark?'#f5f2e5':'#173a42','left',650);}
function footer(c,s,dark=false){text(c,s,50,505,24,dark?'#c2cfd0':'#4c6972');}
function grid(c,col){for(let x=0;x<960;x+=40)line(c,[[x,0],[x,540]],col,.6);for(let y=0;y<540;y+=40)line(c,[[0,y],[960,y]],col,.6);}
function queueAt(t){const arrivals=Math.max(0,Math.floor((t-1)*3+1e-8)),departures=Math.max(0,Math.floor(t-2+1e-8));return {arrivals,departures,queue:Math.max(0,arrivals-departures)};}
function dataAt(t){const p=ease((t-1)/3.7),base=[40,60,20],target=[65,75,40],vals=base.map((v,i)=>Math.round(lerp(v,target[i],p))),total=vals.reduce((a,b)=>a+b,0);return {base,vals,total,growth:Math.round((total/120-1)*100)};}
window.sampleModels={queueAt,dataAt};
function knowledge(c,t){
 c.fillStyle='#edf3ef';c.fillRect(0,0,960,540);grid(c,'#dce6e0');header(c,'01 / 知识与原理','慢的一环，决定流速');
 const {arrivals,departures,queue}=queueAt(t);
 rect(c,55,191,215,221,22,'#d6e6df');rect(c,690,191,215,221,22,'#d6e6df');
 line(c,[[95,300],[865,300]],'#b9d1c9',92);line(c,[[95,300],[865,300]],'#f9fcf7',64);
 rect(c,408,178,142,247,20,'#234d50');rect(c,434,258,90,84,12,'#7bb0a0');
 line(c,[[456,273],[456,327]],'#e9f1dc',7);line(c,[[480,273],[480,327]],'#e9f1dc',7);line(c,[[504,273],[504,327]],'#e9f1dc',7);
 for(let i=0;i<24;i++){let begin=1+(i+1)/3,end=3+i; if(t<begin)continue;
   let x=t<end?Math.min(386-(Math.max(0,i-departures))*13,lerp(80,386,ease((t-begin)/.6))):lerp(550,870,ease((t-end)/.7));
   if(t>end+.8)continue;circle(c,x,300,8,t<end?'#e3a044':'#2d9d87');}
 text(c,'输入 3 个/秒',64,157,29);text(c,'处理 1 个/秒',480,155,29,'#173a42','center');text(c,'输出 1 个/秒',688,157,29);
 text(c,'等待',102,391,23);text(c,String(queue),214,389,37,'#173a42','center',700);
 text(c,'限流口',480,389,28,'#eef4df','center');text(c,`${departures} 个`,789,389,37,'#173a42','center',700);
 footer(c,t<3?'单位时间的处理能力，决定通过速度。':'输入快于处理，等待便会累积。');
}
function lamp(c,x,y,lit,tilt=0){c.save();c.translate(x,y);c.rotate(tilt);line(c,[[-16,45],[-26,63]],'#182e43',8);line(c,[[16,45],[26,63]],'#182e43',8);rect(c,-32,-32,64,84,18,'#d8b883');rect(c,-25,-24,50,56,12,lit?'#ffdb82':'#687d86');line(c,[[-19,-33],[-19,-47],[19,-47],[19,-33]],'#d8b883',6);circle(c,-9,0,3,'#243b48');circle(c,9,0,3,'#243b48');line(c,[[-4,13],[4,13]],'#243b48',3);c.restore();}
function story(c,t){
 c.fillStyle='#183348';c.fillRect(0,0,960,540);for(let i=0;i<36;i++)circle(c,rand(i)*960,125+rand(i+80)*220,1.2,'#789198');
 header(c,'02 / 故事与观点','把光，递给下一个人',true);
 const p=ease((t-1.5)/3.6),x=lerp(255,704,p),y=318-Math.sin(p*Math.PI)*103;
 const glow=c.createRadialGradient(x,y,1,x,y,210);glow.addColorStop(0,'#fbc77966');glow.addColorStop(1,'#fbc77900');c.fillStyle=glow;c.fillRect(0,0,960,540);
 c.fillStyle='#2f5a64';c.beginPath();c.moveTo(0,390);c.bezierCurveTo(180,310,300,480,500,365);c.bezierCurveTo(660,270,760,385,960,322);c.lineTo(960,540);c.lineTo(0,540);c.fill();
 c.fillStyle='#173e4c';c.beginPath();c.moveTo(0,457);c.bezierCurveTo(310,369,550,488,960,407);c.lineTo(960,540);c.lineTo(0,540);c.fill();
 line(c,[[280,365],[370,395],[570,395],[682,365]],'#8ca49b',4);
 for(let i=0;i<22;i++){const a=i/21;circle(c,lerp(280,682,a),365+Math.sin(a*Math.PI)*30,2,'#d8c28a');}
 lamp(c,235,350,true,-.05*Math.sin(t));lamp(c,722,350,p>.88,.04*Math.sin(t));
 line(c,[[260,360],[300,330]],'#d8b883',7);line(c,[[700,360],[668,330]],'#d8b883',7);
 circle(c,x,y,15,'#fff0b0');circle(c,x-3,y-4,5,'#fffdf0');
 if(t>5.2){let q=ease((t-5.2)/1.1);for(let i=0;i<5;i++){let bx=540+i*41;line(c,[[bx,445],[bx,445-38*q]],'#9ab99a',3);circle(c,bx,445-38*q,5*q,'#f0c475');}}
 footer(c,t<5?'一盏灯，把自己的光送了出去。':'远处亮起来，它也看见了路。',true);
}
function product(c,t){
 c.fillStyle='#f4f1eb';c.fillRect(0,0,960,540);header(c,'03 / 产品与教程 · 虚构产品演示','把杂乱，收进一个动作');
 rect(c,48,155,864,308,22,'#ffffff');rect(c,48,155,864,54,22,'#dfe9e4');rect(c,48,185,864,24,0,'#dfe9e4');text(c,'拾刻',76,182,26,'#24594d','left',700);
 text(c,'收集',384,244,24,'#55736d');text(c,'今天',704,244,24,'#55736d');
 rect(c,72,230,211,208,14,'#f1f4f0');text(c,'把注意力',91,269,25);text(c,'留给重要的事',91,310,25);text(c,'任务  →  行动',91,393,19,'#6d7e77');
 for(let i=0;i<3;i++){rect(c,320,276+i*52,245,40,10,'#edf1ed');if(i!==1)text(c,['整理资料','写开场','录一次演示'][i],342,297+i*52,23);}
 rect(c,608,276,272,146,12,'#f1f5f1');const p=ease((t-1.4)/2.3),x=lerp(320,620,p),y=lerp(328,290,p);
 rect(c,x+3,y+5,245,44,10,'#143e3520');rect(c,x,y,245,44,10,'#25765f');text(c,'写开场',x+22,y+22,25,'#fff');
 c.save();c.translate(x+196,y+28);c.fillStyle='#152d33';c.strokeStyle='#fff';c.lineWidth=2;c.beginPath();c.moveTo(0,0);c.lineTo(0,26);c.lineTo(8,18);c.lineTo(16,32);c.lineTo(23,28);c.lineTo(14,14);c.lineTo(26,14);c.closePath();c.fill();c.stroke();c.restore();
 if(t>4.1){let q=ease((t-4.1)/.6);circle(c,643,376,15*q,'#2b8c70');line(c,[[636,376],[641,382],[651,371]],'#fff',3);text(c,'已安排到今天',674,377,24);}
 footer(c,t<3.5?'拖动一张任务卡，确定下一步。':'一次归位，开始行动。此处为示例功能。');
}
function documentary(c,t){
 c.fillStyle='#112f34';c.fillRect(0,0,960,540);grid(c,'#204248');header(c,'04 / 资讯与纪实 · 虚构事件示意','六分钟，一条时间线',true);
 const roads=[[[55,220],[342,220],[477,358],[880,358]],[[110,430],[110,180],[600,180],[600,430]],[[70,300],[700,300],[856,190]],[[310,150],[310,444]],[[770,154],[770,430]]];roads.forEach(p=>line(c,p,'#355a5c',12));roads.forEach(p=>line(c,p,'#5d7774',1));
 const points=[[167,220],[469,300],[770,358]], active=Math.min(2,Math.floor(Math.max(0,t-.9)/2));
 points.forEach(([x,y],i)=>{circle(c,x,y,22,i<=active?'#dcae67':'#3c5857');circle(c,x,y,12,'#15373a');text(c,'ABC'[i],x,y,17,'#f3deba','center',700);if(i===active){c.strokeStyle='#dcae6790';c.lineWidth=2;c.beginPath();c.arc(x,y,28+((t*.7)%1)*18,0,Math.PI*2);c.stroke();}});
 const labels=['09:12  A处记录','09:15  B处记录','09:18  C处记录'];
 rect(c,467,150,439,94,12,'#e4decc');text(c,labels[active],491,180,28,'#253d3b','left',700);text(c,['示例：发现路灯熄灭','示例：巡查人员到达','示例：恢复供电'][active],491,218,23,'#4a5b51');
 line(c,[[84,443],[870,443]],'#496e6d',3);for(let i=0;i<3;i++){let x=100+i*375;circle(c,x,443,8,i<=active?'#e3b96e':'#63807a');text(c,['09:12','09:15','09:18'][i],x,474,23,'#d2ddcf','center');}
 footer(c,'虚构演示 · 包装记录，不推定未被材料证明的因果。',true);
}
function data(c,t){
 c.fillStyle='#f4f0e6';c.fillRect(0,0,960,540);header(c,'05 / 数据与汇报 · 示例数据','总量增长，来源不同');
 const {base,vals,total,growth}=dataAt(t);
 rect(c,96,147,16,16,3,'#cbd3c7');text(c,'前期',122,155,20,'#708077');rect(c,209,147,16,16,3,'#287268');text(c,'本期',235,155,20,'#708077');
 for(let v=0;v<=80;v+=20){const y=430-v*2.9;line(c,[[76,y],[618,y]],'#d8d9cb',1);text(c,String(v),57,y,18,'#708077','right');}
 const colors=['#287268','#819e63','#dcaa58'];
 vals.forEach((v,i)=>{let x=120+i*170;rect(c,x-24,430-base[i]*2.9,56,base[i]*2.9,6,'#cbd3c7');rect(c,x+15,430-v*2.9,68,v*2.9,6,colors[i]);text(c,String(Math.round(v)),x+49,409-v*2.9,27,colors[i],'center',700);text(c,['新客','复购','推荐'][i],x+18,465,25,'#304b48','center');});
 line(c,[[667,170],[667,463]],'#c8d2c3',2);text(c,'合计',716,197,26);text(c,String(total),716,267,72,'#1c6158','left',700);text(c,`+${growth}%`,716,342,43,'#287268');text(c,'前期 → 本期',716,413,23,'#708077');
 footer(c,'同一比例尺、同一份数据，数值与柱高同步。');
}
function creative(c,t){
 c.fillStyle='#e7c998';c.fillRect(0,0,960,540);
 for(let i=0;i<8500;i++){const x=rand(i)*960,y=rand(i+12000)*540;circle(c,x,y,.35+rand(i+9000)*.65,i%2?'#b1844420':'#fff3c72b');}
 header(c,'06 / 视觉与创意','风把山，写进沙里');
 const p=ease((t-.7)/4.8);
 for(let i=0;i<11000;i++){
  let tx=65+rand(i+20000)*830, height=130*Math.exp(-(((tx-345)/135)**2))+165*Math.exp(-(((tx-618)/130)**2))+30;
  let ty=435-rand(i+31000)*height;
  let sx=rand(i+40000)*960,sy=lerp(490,155,rand(i+51000));
  let q=ease(clamp(p*1.6-rand(i+60000)*.6)), x=lerp(sx,tx,q),y=lerp(sy,ty,q)+Math.sin(q*Math.PI)*35*Math.sin(i);
  circle(c,x,y,.55+rand(i+70000)*1.2,rand(i+81000)>.35?'#553b20b3':'#98682fa8');
 }
 const sunY=lerp(350,214,ease((t-3.8)/2.1));circle(c,730,sunY,27,'#f9e5b0');
 for(let i=0;i<1800;i++){const a=rand(i+92000)*Math.PI*2,r=Math.sqrt(rand(i+94000))*28;circle(c,730+Math.cos(a)*r,sunY+Math.sin(a)*r,.65,'#efd08c77');}
 footer(c,'固定粒子身份，让形体浮现，而不是噪声闪烁。');
}
const draw={knowledge,story,product,documentary,data,creative};
window.drawScene=(c,{scene,time,width,height})=>{c.save();c.scale(width/960,height/540);draw[scene.id](c,time);c.restore();};
})();
