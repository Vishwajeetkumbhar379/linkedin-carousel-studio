// Style frame C, motion graphics: flat and exact. The frame is a card on a night canvas; the cracks
// are hairlines, the shards slide and flip on clean curves into a flat phone's camera roll.
import React, {useLayoutEffect, useRef} from 'react';
import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {A, FLIGHT, IMPACT, PTS, SHARDS, cracked, crackReach, flight, squarePts} from './data';
import {CELL, Imgs, cellRect, cover, paintRoll, useImgs} from './roll';
import {Caption} from './caption';
import {GEIST_MONO, loadFonts} from './fonts';

loadFonts();
const W = 1080, H = 1920;
const CARD = {x: 355, y: 205, w: 370}; // the frozen frame, 9:16
const PHONE = {x: 290, y: 1060, s: 1.27, r: 70}; // flat phone: screen origin and scale (points to px)
const smooth = (t: number) => { const x = Math.min(1, Math.max(0, t)); return x * x * (3 - 2 * x); };

const draw = (g: CanvasRenderingContext2D, imgs: Imgs, p: number) => {
  // the canvas: night, a faint dot grid, a warm pool behind the card
  g.fillStyle = '#121318'; g.fillRect(0, 0, W, H);
  g.fillStyle = 'rgba(255,255,255,0.055)';
  for (let y = 20; y < H; y += 40) for (let x = 20; x < W; x += 40) g.fillRect(x - 1.5, y - 1.5, 3, 3);
  const pool = g.createRadialGradient(540, 560, 0, 540, 560, 620);
  pool.addColorStop(0, 'rgba(231,161,90,0.16)'); pool.addColorStop(1, 'rgba(231,161,90,0)');
  g.fillStyle = pool; g.fillRect(0, 0, W, H);

  // the flat phone, screen first so the shards land on top of it
  const sw = 393 * PHONE.s, sh = 852 * PHONE.s;
  g.save();
  g.fillStyle = '#23252c'; g.beginPath(); g.roundRect(PHONE.x - 16, PHONE.y - 16, sw + 32, sh + 32, PHONE.r + 14); g.fill();
  g.strokeStyle = 'rgba(255,255,255,0.14)'; g.lineWidth = 2; g.stroke();
  g.beginPath(); g.roundRect(PHONE.x, PHONE.y, sw, sh, PHONE.r); g.clip();
  g.translate(PHONE.x, PHONE.y); g.scale(PHONE.s, PHONE.s);
  const landed = (i: number) => (flight(SHARDS[i], p) >= 0.985 ? 1 : 0);
  const flash = (i: number) => { const t = (p - SHARDS[i].leave - FLIGHT * 0.985) / 0.1; return t >= 0 && t <= 1 ? 1 - t : 0; };
  paintRoll(g, imgs, landed, flash);
  g.restore();

  // the frozen frame's empty slot (where pieces have left), then its card shadow
  const cw = CARD.w, ch = CARD.w * A;
  g.save();
  g.strokeStyle = 'rgba(255,255,255,0.16)'; g.setLineDash([10, 10]); g.lineWidth = 2;
  g.beginPath(); g.roundRect(CARD.x, CARD.y, cw, ch, 26); g.stroke();
  g.restore();

  // shards: in the card, or in the air
  const half = (CELL * PHONE.s) / 2;
  SHARDS.forEach((s) => {
    const f = flight(s, p);
    if (f >= 0.985) return;
    const k = cracked(s, p);
    const start = {x: CARD.x + s.c[0] * cw, y: CARD.y + s.c[1] * cw};
    const r = cellRect(s.cell.col, s.cell.row);
    const end = {x: PHONE.x + (r.x + r.w / 2) * PHONE.s, y: PHONE.y + (r.y + r.h / 2) * PHONE.s};
    const side = s.c[0] < 0.5 ? -1 : 1;
    const ctrl = {x: (start.x + end.x) / 2 + side * (180 + random(`fx${s.i}`) * 160), y: (start.y + end.y) / 2 - 60 - random(`fy${s.i}`) * 120};
    const u = smooth(f), a = (1 - u) ** 2, b = 2 * (1 - u) * u, c = u * u;
    const x = start.x * a + ctrl.x * b + end.x * c, y = start.y * a + ctrl.y * b + end.y * c;
    // a crack pushes each piece a few pixels away from the impact
    const ix = CARD.x + IMPACT[0] * cw, iy = CARD.y + IMPACT[1] * cw, d = Math.hypot(start.x - ix, start.y - iy) || 1;
    const push = 5 * k * (1 - u);
    const rot = Math.sin(Math.PI * f) * (random(`fr${s.i}`) - 0.5) * 1.6;
    const flip = Math.cos(Math.PI * smooth((f - 0.1) / 0.6)); // 1 face, -1 clip
    const m = smooth((f - 0.2) / 0.75), sq = squarePts(PTS, half);
    const pts = s.poly.map((pt, j) => { const px = (pt[0] - s.c[0]) * cw * (1 - 0.03 * k), py = (pt[1] - s.c[1]) * cw * (1 - 0.03 * k); return [px + (sq[j][0] - px) * m, py + (sq[j][1] - py) * m]; });
    const lift = Math.sin(Math.PI * f);
    g.save();
    g.translate(x + ((start.x - ix) / d) * push, y + ((start.y - iy) / d) * push);
    g.rotate(rot);
    g.scale(Math.max(0.03, Math.abs(flip)) * (1 + lift * 0.25), 1 + lift * 0.25);
    const path = () => { g.beginPath(); pts.forEach(([px, py], j) => (j ? g.lineTo(px, py) : g.moveTo(px, py))); g.closePath(); };
    if (lift > 0.02) { g.save(); g.shadowColor = 'rgba(0,0,0,0.55)'; g.shadowBlur = 30 * lift; g.shadowOffsetY = 18 * lift; path(); g.fillStyle = '#000'; g.fill(); g.restore(); }
    g.save(); path(); g.clip();
    if (flip >= 0) g.drawImage(imgs.face, -s.c[0] * cw, -s.c[1] * cw, cw, cw * A);
    else {
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      pts.forEach(([px, py]) => { x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py); });
      g.scale(-1, 1); // seen from the back
      cover(g, imgs.clips[s.i], -x1, y0, x1 - x0, y1 - y0);
    }
    g.restore();
    path(); g.lineWidth = 1.5 / Math.max(0.2, Math.abs(flip)); g.strokeStyle = f > 0 ? 'rgba(255,255,255,0.7)' : `rgba(255,255,255,${0.85 * k})`; g.stroke();
    g.restore();
  });

  // the impact point: a small amber burst where the word lands
  const burst = crackReach(p) * (1 - smooth((p - 0.3) / 0.2));
  if (burst > 0) {
    const ix = CARD.x + IMPACT[0] * cw, iy = CARD.y + IMPACT[1] * cw;
    g.strokeStyle = `rgba(231,161,90,${burst})`; g.lineWidth = 4;
    g.beginPath(); g.arc(ix, iy, 18 + 70 * crackReach(p), 0, 7); g.stroke();
  }

  // a live counter above the roll, in mono, like an editor's readout
  let n = 0; SHARDS.forEach((s) => { if (flight(s, p) >= 0.985) n++; });
  g.font = `500 30px ${GEIST_MONO}`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillStyle = 'rgba(244,245,247,0.55)'; g.fillText(`${String(n).padStart(2, '0')} / 39 CLIPS`, 540, 1015);
};

export const FlatFrame: React.FC = () => {
  const fr = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const p = fr / (durationInFrames - 1);
  const imgs = useImgs();
  const ref = useRef<HTMLCanvasElement>(null);
  useLayoutEffect(() => { if (imgs && ref.current) draw(ref.current.getContext('2d')!, imgs, p); }, [imgs, p]);
  return (
    <AbsoluteFill style={{background: '#121318'}}>
      <canvas ref={ref} width={W} height={H} style={{width: W, height: H}} />
      <Caption words={['39', 'clips']} pill={0} top={862} shadow={false} />
    </AbsoluteFill>
  );
};
