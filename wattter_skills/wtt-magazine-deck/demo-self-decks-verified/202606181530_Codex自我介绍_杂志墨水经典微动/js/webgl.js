/* =============== WebGL 双背景 ==============
   深色页：Holographic Dispersion（全息色散 · 钛金暗流）—— 彩虹微扰、鼠标径向涟漪
   浅色页：Spiral Vortex（旋转涡流 · 银色珍珠）—— domain-warp 流动、无中心

   主题驱动：shader 颜色不再硬编码，启动时 + T 键切换主题时从 CSS 变量
   (--ink-rgb / --paper-rgb / --accent / --accent-2) 读取并写入 uniform。
   换主题 → 文字色 + 流体背景色一起变。加新主题只改 theme.css，不碰本文件。 */
(function(){
  const VS = 'attribute vec2 position;void main(){gl_Position=vec4(position,0.0,1.0);}';

  /* 暗页 shader：主色 a / 暗底 base / 色散强调 accent 全部走 uniform */
  const FS_DARK = `precision highp float;
uniform vec2 u_resolution;uniform float u_time;uniform vec2 u_mouse;
uniform vec3 u_darkA;uniform vec3 u_darkBase;uniform vec3 u_darkAccent;
vec3 palette(float t,vec3 a,vec3 b,vec3 c,vec3 d){return a+b*cos(6.28318*(c*t+d));}
void main(){
  vec2 uv=gl_FragCoord.xy/u_resolution.xy;
  vec2 p=uv*2.0-1.0;p.x*=u_resolution.x/u_resolution.y;
  vec2 m=u_mouse*2.0-1.0;m.x*=u_resolution.x/u_resolution.y;
  float md=length(p-m);
  float mr=sin(md*15.0-u_time*4.0)*exp(-md*3.0);p+=mr*0.08;
  vec2 p0=p;
  for(float i=1.0;i<4.0;i++){
    p.x+=0.1/i*sin(i*3.0*p.y+u_time*0.4)+0.05;
    p.y+=0.1/i*cos(i*2.0*p.x+u_time*0.3)-0.05;
  }
  float r=length(p);float ang=atan(p.y,p.x);
  vec3 b=u_darkA*0.25;
  vec3 c=vec3(1.0,1.0,1.0);
  vec3 d=mix(u_darkAccent,vec3(0.1,0.2,0.4),0.5);
  vec3 col=palette(r*1.5+p0.x*0.5+u_time*0.1,u_darkA,b,c,d);
  float disp=sin(r*25.0-u_time*1.5+ang*2.0)*0.5+0.5;
  col+=u_darkAccent*disp*0.04;
  float hi=pow(sin(p.x*4.0+p.y*3.0+u_time)*0.5+0.5,8.0);
  col+=hi*0.08;
  col=mix(u_darkBase,col,0.85);
  gl_FragColor=vec4(col,1.0);
}`;

  /* 亮页 shader：纸色 paper / 暗部 silverDark / 珍珠高光 accent 走 uniform */
  const FS_LIGHT = `precision highp float;
uniform vec2 u_resolution;uniform float u_time;uniform vec2 u_mouse;
uniform vec3 u_lightDark;uniform vec3 u_lightPaper;uniform vec3 u_lightAccent;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){
  vec2 i=floor(p),f=fract(p);
  float a=hash(i),b=hash(i+vec2(1,0));
  float c=hash(i+vec2(0,1)),d=hash(i+vec2(1,1));
  vec2 u=f*f*(3.0-2.0*f);
  return mix(a,b,u.x)+(c-a)*u.y*(1.0-u.x)+(d-b)*u.x*u.y;
}
float fbm(vec2 p){
  float v=0.0,a=0.5;
  mat2 m=mat2(0.80,0.60,-0.60,0.80);
  for(int i=0;i<5;i++){v+=a*noise(p);p=m*p*2.02;a*=0.5;}
  return v;
}
void main(){
  vec2 uv=gl_FragCoord.xy/u_resolution.xy;
  vec2 p=uv;p.x*=u_resolution.x/u_resolution.y;
  vec2 m=u_mouse;m.x*=u_resolution.x/u_resolution.y;
  vec2 md=p-m;float dl=length(md);
  p+=normalize(md+vec2(0.0001))*exp(-dl*5.0)*0.03;
  vec2 q=vec2(fbm(p*1.8+u_time*0.07),fbm(p*1.8+vec2(5.2,1.3)+u_time*0.06));
  vec2 r=vec2(fbm(p*2.0+q*1.3+vec2(1.7,9.2)+u_time*0.05),
              fbm(p*2.0+q*1.3+vec2(8.3,2.8)+u_time*0.04));
  float f=fbm(p*2.2+r*1.5);
  vec3 col=mix(u_lightDark,u_lightPaper,f);
  float ph=r.x*2.2+u_time*0.35;
  col+=u_lightAccent*sin(ph)*0.055;
  col+=u_lightAccent*sin(ph*0.8+2.0)*0.05;
  float hl=smoothstep(0.48,0.92,f);
  col+=hl*0.06;
  gl_FragColor=vec4(col,1.0);
}`;

  const mouse = { x: 0.5, y: 0.5 };
  addEventListener('mousemove', e => { mouse.x = e.clientX / innerWidth; mouse.y = e.clientY / innerHeight; });

  /* ---- 读主题色：CSS 变量 → 归一化 vec3 ---- */
  function rgbVar(name){
    /* --xxx-rgb 已是 "r,g,b" 字符串 */
    const raw = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    if(!raw) return null;
    const parts = raw.split(',').map(s => parseFloat(s));
    if(parts.length !== 3 || parts.some(isNaN)) return null;
    return parts.map(v => v/255);
  }
  function hexToRgb01(hex){
    const h = (hex||'').trim().replace('#','');
    if(h.length !== 6) return null;
    const r = parseInt(h.slice(0,2),16), g = parseInt(h.slice(2,4),16), b = parseInt(h.slice(4,6),16);
    if([r,g,b].some(isNaN)) return null;
    return [r,g,b].map(v => v/255);
  }
  function hexVar(name){
    return hexToRgb01(getComputedStyle(document.documentElement).getPropertyValue(name).trim());
  }
  /* 把一个 rgb01 加深/提亮，避免 shader 里出现纯黑/纯白导致流体看不见 */
  function clamp01(v){ return Math.max(0, Math.min(1, v)); }
  function shade(rgb01, factor){
    /* factor<1 加深，>1 提亮（按通道乘） */
    return rgb01.map(v => clamp01(v*factor));
  }

  /* 当前主题色缓存（归一化），readThemeColors 填充 */
  let theme = {
    darkA: [0.12,0.12,0.13], darkBase: [0.05,0.05,0.06], darkAccent: [0.1,0.2,0.4],
    lightDark: [0.86,0.85,0.84], lightPaper: [0.955,0.945,0.925], lightAccent: [0.78,0.62,0.92]
  };

  function readThemeColors(){
    const ink = rgbVar('--ink-rgb') || theme.darkA;
    const paper = rgbVar('--paper-rgb') || theme.lightPaper;
    const accent = hexVar('--accent') || hexVar('--accent-2') || theme.darkAccent;
    const accent2 = hexVar('--accent-2') || accent;
    theme.darkA = ink.map(v => clamp01(v*1.15 + 0.03));          /* 比 ink 略亮一点，保证流体可见 */
    theme.darkBase = shade(ink, 0.45);                            /* 暗底，比 ink 更深 */
    theme.darkAccent = accent;
    theme.lightDark = shade(paper, 0.86).map((v,i) => clamp01(v*0.7 + ink[i]*0.15)); /* 纸色压暗带一点 ink 偏色 */
    theme.lightPaper = paper.map(v => clamp01(v*1.0));
    theme.lightAccent = accent2;
  }

  function bootGL(canvasId, fsSrc) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return () => false;
    const gl = canvas.getContext('webgl', { alpha: false, antialias: true });
    if (!gl) return () => false;
    const mk = (t, s) => { const sh = gl.createShader(t); gl.shaderSource(sh, s); gl.compileShader(sh); return sh; };
    const prog = gl.createProgram();
    gl.attachShader(prog, mk(gl.VERTEX_SHADER, VS));
    gl.attachShader(prog, mk(gl.FRAGMENT_SHADER, fsSrc));
    gl.linkProgram(prog); gl.useProgram(prog);
    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]), gl.STATIC_DRAW);
    const pos = gl.getAttribLocation(prog, 'position');
    gl.enableVertexAttribArray(pos); gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);
    const lRes = gl.getUniformLocation(prog, 'u_resolution');
    const lT = gl.getUniformLocation(prog, 'u_time');
    const lM = gl.getUniformLocation(prog, 'u_mouse');
    /* 主题 uniform location（暗页/亮页各 3 个，名字一致） */
    const lA = gl.getUniformLocation(prog, 'u_darkA') || gl.getUniformLocation(prog, 'u_lightDark');
    const lBase = gl.getUniformLocation(prog, 'u_darkBase') || gl.getUniformLocation(prog, 'u_lightPaper');
    const lAcc = gl.getUniformLocation(prog, 'u_darkAccent') || gl.getUniformLocation(prog, 'u_lightAccent');
    const isDark = !!gl.getUniformLocation(prog, 'u_darkA');
    const resize = () => {
      const d = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = innerWidth * d; canvas.height = innerHeight * d;
      gl.viewport(0, 0, canvas.width, canvas.height);
    };
    addEventListener('resize', resize); resize();
    return (tSec) => {
      gl.uniform2f(lRes, canvas.width, canvas.height);
      gl.uniform1f(lT, tSec);
      gl.uniform2f(lM, mouse.x, 1 - mouse.y);
      /* 每帧更新主题 uniform（仅 6 条 gl.uniform3f，开销可忽略；免时序 bug） */
      if (lA && lBase && lAcc) {
        if (isDark) {
          gl.uniform3f(lA, theme.darkA[0], theme.darkA[1], theme.darkA[2]);
          gl.uniform3f(lBase, theme.darkBase[0], theme.darkBase[1], theme.darkBase[2]);
          gl.uniform3f(lAcc, theme.darkAccent[0], theme.darkAccent[1], theme.darkAccent[2]);
        } else {
          gl.uniform3f(lA, theme.lightDark[0], theme.lightDark[1], theme.lightDark[2]);
          gl.uniform3f(lBase, theme.lightPaper[0], theme.lightPaper[1], theme.lightPaper[2]);
          gl.uniform3f(lAcc, theme.lightAccent[0], theme.lightAccent[1], theme.lightAccent[2]);
        }
      }
      gl.drawArrays(gl.TRIANGLES, 0, 6);
      return true;
    };
  }

  const drawDark = bootGL('bg-dark', FS_DARK);
  const drawLight = bootGL('bg-light', FS_LIGHT);
  /* 启动时读一次主题色 */
  readThemeColors();
  const t0 = Date.now();

  /* T 键切主题后由 cinematic.js 调用：css 可能异步加载，延时重读几次确保拿到新值 */
  window.__refreshThemeColors = function(){
    readThemeColors();
    setTimeout(readThemeColors, 60);
    setTimeout(readThemeColors, 200);
  };

  (function loop() {
    const t = (Date.now() - t0) / 1000;
    drawDark(t); drawLight(t);
    requestAnimationFrame(loop);
  })();
})();
