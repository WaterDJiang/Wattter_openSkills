const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const html=fs.readFileSync(`${__dirname}/../assets/four-stroke-engine.html`,"utf8");
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script); // Parse the complete delivered script, not a rewritten model.
const context=vm.createContext({});
vm.runInContext(script.slice(0,script.indexOf("const P=")),context);
const model=vm.runInContext("model",context),L=155,R=48;
let maxError=0,minClearance=Infinity;
for(let angle=0;angle<=720;angle+=.5){
 const s=model(angle);
 const length=Math.hypot(s.crankX,s.pinZ-s.crankZ);
 maxError=Math.max(maxError,Math.abs(length-L));
 assert.ok(s.travel>=-1e-12&&s.travel<=1+1e-12);
 assert.ok(s.intake>=0&&s.exhaust>=0);
 assert.ok(!(s.intake>.001&&s.exhaust>.001),"理想相位无重叠");
 assert.ok(s.phase===0||s.intake===0);
 assert.ok(s.phase===3||s.exhaust===0);
 minClearance=Math.min(minClearance,254-Math.max(s.intake,s.exhaust)-s.crown);
 assert.ok(254-Math.max(s.intake,s.exhaust)>s.crown,"气门不得穿过活塞顶");
}
assert.ok(maxError<1e-10,"固定连杆长度");
for(const angle of [0,360,720])assert.equal(model(angle).pinZ,L+R);
for(const angle of [180,540])assert.equal(model(angle).pinZ,L-R);
assert.deepEqual([90,270,450,630].map(a=>model(a).phase),[0,1,2,3]);
assert.ok(model(90).intake>12.9&&model(630).exhaust>12.9);
assert.ok(model(360).ignition&&!model(350).ignition&&!model(400).ignition);
assert.equal(model(720).angle,0);
assert.ok(Math.abs(model(719.999).pinZ-model(.001).pinZ)<1e-8);
assert.equal(model(-90).phase,3);
// Finite rod length produces a non-sinusoidal midstroke position.
assert.ok(Math.abs(model(90).pinZ-L)>1);
console.log(`PASS: 1441 个相位；杆长最大误差 ${maxError.toExponential(2)}；气门/活塞最小净空 ${minClearance.toFixed(2)} 绘图单位；上下止点、气门相位、点火窗口与循环连续`);
