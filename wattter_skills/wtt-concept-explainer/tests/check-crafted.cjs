const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const html=fs.readFileSync(`${__dirname}/../assets/cache-apparatus.html`,"utf8");
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const nodes={};
function register(markup){for(const [,id] of markup.matchAll(/\bid="([^"]+)"/g))if(!nodes[id])nodes[id]={
 textContent:"",style:{},attrs:{},classList:{toggle(name,value){this[name]=value;}},
 set innerHTML(value){register(value);},setAttribute(k,v){this.attrs[k]=v;},addEventListener(k,v){this[k]=v;}
};}
register(html);
let animation,nextTimer=0;const timers=new Map();
const context=vm.createContext({document:{getElementById:id=>{assert.ok(nodes[id],`缺少 ${id}`);return nodes[id];},addEventListener(){}},
 matchMedia:()=>({matches:false}),cancelAnimationFrame:()=>{animation=null;},requestAnimationFrame:fn=>{animation=fn;return 1;},
 performance:{now:()=>0},setTimeout:(fn,ms)=>{const id=++nextTimer;timers.set(id,{fn,ms});return id;},clearTimeout:id=>timers.delete(id)});
vm.runInContext(script,context);
const click=id=>nodes[id].click(),read=expr=>vm.runInContext(expr,context);
assert.equal(nodes.cartridge.style.transform,"translate(0,-17px)");
click("request");
assert.equal(read("state.version"),1);
assert.equal(nodes.cartridge.style.transform,"translate(0,0)");
assert.equal(nodes["source-path"].attrs.class,"route active");
assert.equal(nodes["time-arc"].attrs["stroke-dashoffset"],0);
animation(500);
assert.equal(nodes.packet.style.opacity,1);
assert.ok(Number.isFinite(nodes.packet.attrs.cx));
click("advance");
assert.equal(nodes.needle.style.transform,"rotate(180deg)");
assert.equal(nodes.packet.style.opacity,0);
click("request");
assert.equal(read("state.written"),0);
assert.equal(read("state.version"),1);
assert.equal(nodes["source-path"].attrs.class,"route dim");
click("advance");
assert.equal(nodes["fresh-strip"].style.opacity,".12");
assert.equal(nodes["time-arc"].attrs["stroke-dashoffset"],264);
assert.equal(nodes.status.textContent,"缓存已到期");
click("request");
assert.equal(read("state.version"),2);
assert.equal(read("state.written"),60);
assert.equal(nodes["fresh-strip"].style.opacity,"1");
click("reset");
assert.equal(read("state.now"),0);
assert.equal(nodes.cartridge.style.transform,"translate(0,-17px)");
click("tour");
assert.equal(nodes.tour.textContent,"停止演示");
for(const [,job] of [...timers].sort((a,b)=>a[1].ms-b[1].ms))job.fn();
assert.equal(read("state.now"),60);
assert.equal(read("state.version"),2);
assert.equal(nodes.tour.textContent,"演示一轮");
click("tour");click("tour");
assert.equal(timers.size,0,"停止演示应取消后续操作");
console.log("PASS: 缓存边界、存储匣开合、表盘、有效标记、命中/回源路径、路径回放、重置、自动演示与停止");
