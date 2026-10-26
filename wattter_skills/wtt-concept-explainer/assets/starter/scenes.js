/* 可替换的帧接口示例；正式主体按已确认分镜制作。无外部 JS 依赖。 */
window.drawScene=(ctx,{scene,width:w,height:h,progress})=>{
 const drawText=(value,x,y,available)=>{const txt=String(value);if(ctx.measureText(txt).width>available)throw Error('模板文字溢出：重排主体/标题/标签，不要横向挤压：'+txt);ctx.fillText(txt,x,y);};
 const data=scene.director, labels=data?.labels;
 if(!Array.isArray(labels)||labels.length<2||labels.length>6||!Number.isInteger(data.focus)||data.focus<0||data.focus>=labels.length)throw Error('模板需要 director.labels（2–6项）与有效 focus；自定义主体请改写 scenes.js');
 const gap=w*.7/(labels.length-1),x=i=>w*.15+i*gap,y=h*.52,r=Math.min(gap*.30,h*.12);
 ctx.fillStyle='#F3F6FB';ctx.fillRect(0,0,w,h);
 ctx.textBaseline='middle';ctx.textAlign='left';ctx.fillStyle='#4B627F';ctx.font=`${h*.022}px sans-serif`;ctx.fillText('概念讲解 · 舞台模板',w*.075,h*.09);
 ctx.fillStyle='#142746';ctx.font=`600 ${Math.min(w*.055,h*.071)}px sans-serif`;drawText(scene.title||'',w*.075,h*.18,w*.85);
 ctx.strokeStyle='#91A9C6';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(x(0),y);ctx.lineTo(x(labels.length-1),y);ctx.stroke();
 labels.forEach((label,i)=>{const focused=i===data.focus;ctx.fillStyle=focused?'#002FA7':'#E6EDFA';ctx.beginPath();ctx.arc(x(i),y,r,0,2*Math.PI);ctx.fill();ctx.fillStyle=focused?'#fff':'#142746';ctx.textAlign='center';ctx.font=`${Math.min(w*.04,h*.061)}px sans-serif`;drawText(label,x(i),y,r*1.7)});
 ctx.fillStyle='#4B627F';ctx.font=`${h*.022}px sans-serif`;ctx.textAlign='left';drawText('舞台示例 · 请按分镜重做主体',w*.075,h*.74,w*.85);
 ctx.fillStyle='#002FA7';ctx.fillRect(0,h-4,w*progress,4);
};
