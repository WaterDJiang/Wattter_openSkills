// Illustrative microphone trace; amplitudes and time units are schematic.
export function draw(ctx, {width, height, progress}) {
  ctx.scale(width / 640, height / 360);
  ctx.fillStyle = '#102f35'; ctx.fillRect(0, 0, 640, 360);
  ctx.strokeStyle = '#285055'; ctx.lineWidth = 1;
  ctx.beginPath();
  for (let x = 60; x <= 580; x += 26) { ctx.moveTo(x, 76); ctx.lineTo(x, 268); }
  for (let y = 76; y <= 268; y += 24) { ctx.moveTo(60, y); ctx.lineTo(580, y); }
  ctx.stroke();
  const packet = (x, center, amplitude) =>
    amplitude * Math.exp(-((x - center) ** 2) / 125) * Math.sin((x - center) * 0.55);
  ctx.beginPath(); ctx.strokeStyle = '#a5e4b3'; ctx.lineWidth = 3;
  const end = 60 + Math.min(1, progress / 0.8) * 520;
  for (let x = 60; x <= end; x++) {
    const y = 172 - packet(x, 174, 75) - packet(x, 405, 39);
    if (x === 60) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.fillStyle = '#ffe3a8'; ctx.font = '17px sans-serif';
  if (end >= 190) ctx.fillText('原声', 155, 284);
  if (end >= 421) ctx.fillText('回声', 386, 284);
}
