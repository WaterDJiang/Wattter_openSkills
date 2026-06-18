/* =============== WebGL 网格背景（swiss 风格用） ==============
   从 template-swiss.html 内联 shader 抽出。
   特点：极简 40 格网格 + 鼠标径向晕染，比 editorial 的流体 shader 轻量 10 倍。
   主题驱动：从 CSS 变量 (--paper-rgb / --ink-rgb / --accent) 读取配色，
   换主题 → 网格底色 + 晕染色一起变。加新主题只改 theme.css，不碰本文件。

   与 fluid.js 的契约差异：
   - 单 canvas（id="bg-grid"），非双 canvas
   - mix-blend-mode:multiply（暗底 screen），opacity:.55
   - 无 domain-warp 噪声，纯几何网格 + 鼠标径向 */
(function(){
  const canvas = document.getElementById('bg-grid');
  if (!canvas) return;
  const gl = canvas.getContext('webgl', { alpha: false, antialias: true });
  if (!gl) return;

  const VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  const FS = `precision highp float;uniform vec2 u_res;uniform float u_t;uniform vec2 u_m;
uniform vec3 u_base;uniform vec3 u_ink;uniform vec3 u_accent;
float grid(vec2 uv,float d){vec2 g=mod(uv*40.,d);g=min(g,d-g);float l=min(g.x,g.y);return smoothstep(0.,.04,l);}
void main(){
  vec2 uv=gl_FragCoord.xy/u_res; vec2 p=(uv*2.-1.); p.x*=u_res.x/u_res.y;
  vec2 m=(u_m*2.-1.); m.x*=u_res.x/u_res.y;
  float md=length(p-m);
  float r=length(p);
  float g=grid(uv,1.);
  vec3 col=mix(u_base, u_ink, g*0.05);
  col+=u_accent*0.15*sin(r*8.-u_t*0.5)*0.3*exp(-md*2.);
  gl_FragColor=vec4(col, 1.);
}`;

  function mk(t, s){ const sh = gl.createShader(t); gl.shaderSource(sh, s); gl.compileShader(sh); return sh; }
  const prog = gl.createProgram();
  gl.attachShader(prog, mk(gl.VERTEX_SHADER, VS));
  gl.attachShader(prog, mk(gl.FRAGMENT_SHADER, FS));
  gl.linkProgram(prog); gl.useProgram(prog);

  const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]), gl.STATIC_DRAW);
  const a = gl.getAttribLocation(prog, 'p'); gl.enableVertexAttribArray(a); gl.vertexAttribPointer(a, 2, gl.FLOAT, false, 0, 0);

  const lR = gl.getUniformLocation(prog, 'u_res');
  const lT = gl.getUniformLocation(prog, 'u_t');
  const lM = gl.getUniformLocation(prog, 'u_m');
  const lBase = gl.getUniformLocation(prog, 'u_base');
  const lInk = gl.getUniformLocation(prog, 'u_ink');
  const lAcc = gl.getUniformLocation(prog, 'u_accent');

  const m = { x: 0.5, y: 0.5 };
  addEventListener('mousemove', e => { m.x = e.clientX / innerWidth; m.y = e.clientY / innerHeight; });

  /* ---- 读主题色：CSS 变量 → 归一化 vec3 ---- */
  function rgbVar(name, fallback){
    const raw = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    if (!raw) return fallback;
    const parts = raw.split(',').map(s => parseFloat(s));
    if (parts.length !== 3 || parts.some(isNaN)) return fallback;
    return parts.map(v => v / 255);
  }
  function hexVar(name, fallback){
    const h = (getComputedStyle(document.documentElement).getPropertyValue(name).trim() || '').replace('#', '');
    if (h.length !== 6) return fallback;
    const r = parseInt(h.slice(0,2),16), g = parseInt(h.slice(2,4),16), b = parseInt(h.slice(4,6),16);
    if ([r,g,b].some(isNaN)) return fallback;
    return [r,g,b].map(v => v / 255);
  }

  let theme = {
    base: [0.94, 0.94, 0.93],
    ink: [0.04, 0.04, 0.04],
    accent: [0.0, 0.18, 0.65]
  };
  function readThemeColors(){
    theme.base = rgbVar('--paper-rgb', theme.base);
    theme.ink = rgbVar('--ink-rgb', theme.ink);
    theme.accent = hexVar('--accent', theme.accent);
  }
  readThemeColors();
  /* T 键切主题后由 cinematic.js 调用 */
  window.__refreshThemeColors = function(){
    readThemeColors();
    setTimeout(readThemeColors, 60);
    setTimeout(readThemeColors, 200);
  };

  function resize(){
    const d = Math.min(devicePixelRatio || 1, 2);
    canvas.width = innerWidth * d; canvas.height = innerHeight * d;
    gl.viewport(0, 0, canvas.width, canvas.height);
  }
  addEventListener('resize', resize); resize();

  const t0 = Date.now();
  (function loop(){
    /* 低功耗模式跳过渲染 */
    if (document.body.classList.contains('low-power')) { requestAnimationFrame(loop); return; }
    const t = (Date.now() - t0) / 1000;
    gl.uniform2f(lR, canvas.width, canvas.height);
    gl.uniform1f(lT, t);
    gl.uniform2f(lM, m.x, 1 - m.y);
    gl.uniform3f(lBase, theme.base[0], theme.base[1], theme.base[2]);
    gl.uniform3f(lInk, theme.ink[0], theme.ink[1], theme.ink[2]);
    gl.uniform3f(lAcc, theme.accent[0], theme.accent[1], theme.accent[2]);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
    requestAnimationFrame(loop);
  })();
})();
