// Side elevation. The bright half-ring follows the outbound and reflected paths.
export function draw(ctx, {width, height, progress}) {
  ctx.scale(width / 640, height / 360);
  ctx.fillStyle = '#f5ead2';
  ctx.fillRect(0, 0, 640, 360);
  ctx.fillStyle = '#213f4a';
  ctx.fillRect(502, 53, 34, 245);
  ctx.fillRect(74, 156, 19, 44);
  ctx.beginPath();
  ctx.moveTo(93, 156); ctx.lineTo(120, 136); ctx.lineTo(120, 220);
  ctx.lineTo(93, 200); ctx.closePath(); ctx.fill();
  const returning = progress >= 0.5;
  const travel = returning ? (1 - progress) * 2 : progress * 2;
  const center = 140 + travel * 337;
  ctx.strokeStyle = '#c14d36';
  ctx.lineWidth = 7;
  for (let i = 0; i < 3; i++) {
    const angle = returning ? Math.PI : 0;
    ctx.beginPath();
    ctx.arc(center, 178, 13 + 11 * i, angle - 0.72, angle + 0.72); ctx.stroke();
  }
  ctx.fillStyle = '#213f4a';
  ctx.font = '18px sans-serif';
  ctx.fillText(returning ? '反射' : '发出', 64, 302);
}
