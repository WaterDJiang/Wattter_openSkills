// Small-angle classroom illustration. One geometry, camera and oscillation clock.
export function sampleWorld(frame, fps) {
  const seconds = frame / fps;
  const angle = 0.57 * Math.cos(2 * Math.PI * seconds / 2.64);
  return {angle, pivotX: 320, pivotY: 78, length: 152,
    cameraX: 10 * Math.sin(seconds * 0.45), seconds};
}

function ink(ctx, points, color, weight) {
  ctx.strokeStyle = color; ctx.lineWidth = weight; ctx.beginPath();
  for (const [i, [x, y]] of points.entries()) {
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();
}

export function paint(ctx, {world: w, width, height}, mix) {
  ctx.save(); ctx.scale(width / 640, height / 360);
  const rgb = (a,b) => 'rgb(' + a.map((v,i) => Math.round(v+(b[i]-v)*mix)).join(',') + ')';
  const paper = rgb([249,241,219],[239,245,241]);
  const dark = rgb([91,70,61],[34,67,74]);
  ctx.fillStyle = paper; ctx.fillRect(0,0,640,360);
  ctx.translate(w.cameraX,0);
  // The scale is fixed to the support. Neither it nor the bob restarts at a cut.
  for(let i=-6;i<=6;i++) {
    const a=i*0.1, r=196, tip=r+(i%3===0?9:4);
    ink(ctx,[[320+r*Math.sin(a),78+r*Math.cos(a)],[320+tip*Math.sin(a),78+tip*Math.cos(a)]],dark,1);
  }
  ink(ctx,[[252,65],[388,65]],dark,2);
  ink(ctx,[[304,65],[320,78],[336,65]],dark,2);
  ctx.save(); ctx.translate(w.pivotX,w.pivotY); ctx.rotate(-w.angle);
  ink(ctx,[[0,0],[0,w.length]],dark,2);
  ctx.translate(0,w.length);
  // Pigment drains into unpainted paper while the same curved silhouette gains hatch lines.
  ctx.fillStyle=rgb([201,111,75],[239,245,241]);
  ctx.beginPath(); ctx.arc(0,0,22,0,2*Math.PI); ctx.fill(); ctx.strokeStyle=dark; ctx.lineWidth=2; ctx.stroke();
  ctx.save(); ctx.clip(); ctx.rotate(-0.55);
  for(let i=-23;i<=23;i+=3) {
    const rough=1-mix, ripple=Math.sin(i*7)*rough*1.4;
    ink(ctx,[[i,-23],[i+ripple,0],[i,23]],rgb([165,86,64],[40,83,84]),0.6+mix*0.5);
  }
  ctx.restore(); ctx.restore();
  ctx.beginPath(); ctx.arc(320,78,3,0,Math.PI*2); ctx.fillStyle=dark; ctx.fill();
  ctx.restore();
}
