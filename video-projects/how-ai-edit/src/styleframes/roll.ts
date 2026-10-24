// The phone's camera roll (generic Photos-style UI, no logos), painted in screen points (393 x 852).
import {useEffect, useState} from 'react';
import {delayRender, staticFile} from 'remotion';
import {settle} from '../kit/three-canvas';
import {homeBar, statusBar} from '../kit/phone';
import {CLIP_SECONDS, COLS, N, dur, tile, FACE} from './data';

export const SW = 393, SH = 852;
const GAP = 1.5, TOP = 142;
export const CELL = (SW - GAP * (COLS - 1)) / COLS;
export const cellRect = (col: number, row: number) => ({x: col * (CELL + GAP), y: TOP + row * (CELL + GAP), w: CELL, h: CELL});
const SF = 'system-ui, -apple-system, "SF Pro Text", "Helvetica Neue", sans-serif';

export type Imgs = {face: HTMLImageElement; clips: HTMLImageElement[]};
// Every image the beat needs, loaded before the frame is released.
export const useImgs = (): Imgs | null => {
  const [imgs, set] = useState<Imgs | null>(null);
  const [handle] = useState(() => delayRender('beat 1 images'));
  useEffect(() => {
    const load = (src: string) => new Promise<HTMLImageElement>((ok) => { const im = new Image(); im.onload = () => ok(im); im.src = staticFile(src); });
    Promise.all([load(FACE), ...Array.from({length: N}, (_, i) => load(tile(i)))]).then(([face, ...clips]) => { set({face, clips}); settle(handle); });
  }, [handle]);
  return imgs;
};

// Draw an image cover-cropped into a rect (crop centre biased up, where faces are).
export const cover = (g: CanvasRenderingContext2D, im: HTMLImageElement, x: number, y: number, w: number, h: number, bias = 0.4) => {
  const s = Math.max(w / im.width, h / im.height), sw = w / s, sh = h / s;
  g.drawImage(im, (im.width - sw) / 2, (im.height - sh) * bias, sw, sh, x, y, w, h);
};

// landed(i): 0..1 how far clip i has settled into its cell; flash(i): 0..1 the amber arrival ring.
export const paintRoll = (g: CanvasRenderingContext2D, imgs: Imgs, landed: (i: number) => number, flash: (i: number) => number) => {
  g.fillStyle = '#000'; g.fillRect(0, 0, SW, SH);
  // the grid: empty slots wait as dark squares
  for (let i = 0; i < N; i++) {
    const r = cellRect(i % COLS, Math.floor(i / COLS)), l = landed(i);
    g.fillStyle = '#121316'; g.fillRect(r.x, r.y, r.w, r.h);
    if (l <= 0) continue;
    g.save(); g.globalAlpha = Math.min(1, l * 1.4);
    cover(g, imgs.clips[i], r.x, r.y, r.w, r.h);
    const sh = g.createLinearGradient(0, r.y + r.h * 0.6, 0, r.y + r.h);
    sh.addColorStop(0, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(0,0,0,0.45)');
    g.fillStyle = sh; g.fillRect(r.x, r.y, r.w, r.h);
    g.fillStyle = '#fff'; g.font = `600 12px ${SF}`; g.textAlign = 'right'; g.textBaseline = 'alphabetic';
    g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 3;
    g.fillText(dur(CLIP_SECONDS[i]), r.x + r.w - 5, r.y + r.h - 5);
    g.restore();
    const fl = flash(i);
    if (fl > 0) { g.strokeStyle = `rgba(231,161,90,${fl})`; g.lineWidth = 3; g.strokeRect(r.x + 1.5, r.y + 1.5, r.w - 3, r.h - 3); }
  }
  // header over the grid
  const hd = g.createLinearGradient(0, 0, 0, TOP + 20);
  hd.addColorStop(0, 'rgba(0,0,0,0.95)'); hd.addColorStop(0.75, 'rgba(0,0,0,0.85)'); hd.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = hd; g.fillRect(0, 0, SW, TOP + 20);
  statusBar(g, '9:41');
  let n = 0; for (let i = 0; i < N; i++) if (landed(i) > 0.5) n++;
  g.fillStyle = '#fff'; g.textAlign = 'left'; g.textBaseline = 'alphabetic';
  g.font = `700 32px ${SF}`; g.fillText('Library', 16, 102);
  g.fillStyle = '#9a9aa0'; g.font = `500 15px ${SF}`; g.fillText(`${n} Video${n === 1 ? '' : 's'}`, 17, 126);
  g.fillStyle = 'rgba(120,120,128,0.36)'; g.beginPath(); g.roundRect(SW - 140, 82, 74, 32, 16); g.fill();
  g.fillStyle = '#fff'; g.font = `600 15px ${SF}`; g.textAlign = 'center'; g.fillText('Select', SW - 103, 103);
  g.fillStyle = 'rgba(120,120,128,0.36)'; g.beginPath(); g.arc(SW - 34, 98, 16, 0, 7); g.fill();
  g.strokeStyle = '#fff'; g.lineWidth = 2; g.beginPath(); g.arc(SW - 36, 96, 6, 0, 7); g.stroke();
  g.beginPath(); g.moveTo(SW - 31.5, 100.5); g.lineTo(SW - 27, 105); g.stroke();
  // the zoom control at the bottom
  const by = 772;
  g.fillStyle = 'rgba(44,44,48,0.92)'; g.beginPath(); g.roundRect(SW / 2 - 118, by, 236, 40, 20); g.fill();
  g.fillStyle = 'rgba(99,99,104,0.9)'; g.beginPath(); g.roundRect(SW / 2 + 40, by + 4, 74, 32, 16); g.fill();
  g.font = `600 14px ${SF}`; g.textAlign = 'center'; g.textBaseline = 'middle';
  [['Years', -78], ['Months', 0], ['All', 77]].forEach(([t, dx]) => { g.fillStyle = '#fff'; g.fillText(t as string, SW / 2 + (dx as number), by + 20.5); });
  homeBar(g);
};
