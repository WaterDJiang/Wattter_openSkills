/* Original small helpers for code-drawn postcard scenes. No rendering engine or geographic data. */
(function(root){'use strict';
const TAU=Math.PI*2,mod=(x,n)=>(x%n+n)%n,smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
const PALETTES={
 vivid:{paper:'#FDFDF9',ink:'#4D6170',river:'#65BDE4',grass:'#80C9A0',trees:['#FFC94A','#50B792','#F59A66'],walls:['#F2ABC7','#B8AAE5','#91CEE5','#96D3B5'],roofs:['#F8D774','#D0C2F1','#B3DDE7'],road:'#CDD1DF',mark:'#FFFDF0'},
 soft:{paper:'#FDFDF9',ink:'#6C796E',river:'#B6D6DC',grass:'#D6E4BC',trees:['#D8C183','#ADC5A2','#DCA69D'],walls:['#D6C1C8','#C6C2D4','#B6CFD2','#BFCDB6'],roofs:['#E4D5AA','#D7CDD9','#C6D6D2'],road:'#E5E3D7',mark:'#FFFDF0'}
};
function palette(name='vivid',overrides={}){if(!Object.hasOwn(PALETTES,name))throw Error('palette须为vivid/soft');return Object.assign({},PALETTES[name],overrides);}
function cameraAt(frame,{frames=600,profile='multi-angle'}={}){
 if(!Number.isInteger(frame)||!Number.isInteger(frames)||frames<2)throw Error('frame/frames须为有效整数');if(!['top-down','isometric','multi-angle'].includes(profile))throw Error('未知view profile');
 const t=mod(frame,frames)/frames;
 if(profile==='top-down')return {elevation:90,yaw:0,scale:.73};
 if(profile==='isometric')return {elevation:35.26438968,yaw:-45,scale:.70};
 // Periodic itinerary: map -> left axonometric -> right axonometric -> map.
 const keys=[[0,90,0,.73],[.19,90,0,.73],[.34,35.26438968,-25,.70],[.56,35.26438968,-17,.70],[.72,40,23,.70],[.84,40,23,.70],[1,90,0,.73]];
 let a=keys[0],b=keys[1];for(let k=1;k<keys.length;k++){if(t<=keys[k][0]){a=keys[k-1];b=keys[k];break;}}
 const u=smooth((t-a[0])/(b[0]-a[0]));return {elevation:a[1]+(b[1]-a[1])*u,yaw:a[2]+(b[2]-a[2])*u,scale:a[3]+(b[3]-a[3])*u};
}
function project(point,camera,{centerX=540,centerZ=450,screenX=540,screenY=548}={}){
 if(!Array.isArray(point)||point.length!==3||!point.every(Number.isFinite))throw Error('point须为有限[x,z,height]');
 if(!camera||!['elevation','yaw','scale'].every(k=>Number.isFinite(camera[k]))||camera.scale<=0)throw Error('camera无效');
 const [px,pz,h]=point,el=camera.elevation*Math.PI/180,yaw=camera.yaw*Math.PI/180,x=px-centerX,z=pz-centerZ;
 const q=x*Math.cos(yaw)-z*Math.sin(yaw),depth=x*Math.sin(yaw)+z*Math.cos(yaw);
 return {x:screenX+camera.scale*q,y:screenY+camera.scale*(depth*Math.sin(el)-h*Math.cos(el)),depth:depth*Math.cos(el)+h*Math.sin(el)};
}
function orderedFaces(faces,camera,options){return faces.map((f,i)=>{const points=f.points.map(p=>project(p,camera,options));return {...f,points,depth:points.reduce((s,p)=>s+p.depth,0)/points.length,_order:i};}).sort((a,b)=>(a.layer??1)-(b.layer??1)||a.depth-b.depth||a._order-b._order);}
const api={palette,cameraAt,project,orderedFaces,mod,smooth,TAU};if(typeof module!=='undefined')module.exports=api;else root.PostcardPresentation=api;
})(typeof window==='undefined'?globalThis:window);
