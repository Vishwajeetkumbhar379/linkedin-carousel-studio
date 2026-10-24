// A caption as what it really is: a small web page in a browser window, drawn at a moment of its
// pop-in animation. Generic browser chrome, no logos.
import * as THREE from 'three';
import {C, canvasTex} from './kit';

const pop = (k: number) => { const x = Math.min(1, Math.max(0, k)); return 1 - Math.pow(1 - x, 3) * Math.cos(x * 4.2); };

// the page at progress k (0..1 of one second of animation)
export const pageTex = (k: number, chrome = true) => canvasTex(540, 960, (g) => {
  const W = 540, H = 960;
  g.fillStyle = '#0b0d14'; g.fillRect(0, 0, W, H);
  g.strokeStyle = 'rgba(159,178,255,0.55)'; g.lineWidth = 6; g.strokeRect(3, 3, W - 6, H - 6);
  g.fillStyle = 'rgba(255,255,255,0.05)';
  for (let y = 12; y < H; y += 24) for (let x = 12; x < W; x += 24) g.fillRect(x - 1, y - 1, 2, 2);
  if (chrome) {
    g.fillStyle = '#1c1f29'; g.fillRect(0, 0, W, 74);
    ['#ff6159', '#ffbd2e', '#28c941'].forEach((c, i) => { g.fillStyle = c; g.beginPath(); g.arc(26 + i * 22, 24, 7, 0, 7); g.fill(); });
    g.fillStyle = '#2a2e3b'; g.beginPath(); g.roundRect(18, 40, W - 36, 26, 13); g.fill();
    g.fillStyle = '#aab3cc'; g.font = '500 15px "Geist Mono", monospace'; g.textBaseline = 'middle'; g.fillText('localhost:3000  /  caption.html', 34, 54);
  }
  // the caption: "39" in an amber pill, "clips" in white, scaled by its pop-in
  const s = pop(k);
  g.save(); g.translate(W / 2, H * 0.5); g.scale(s * 1.25, s * 1.25);
  g.font = '800 64px Geist, sans-serif'; g.textBaseline = 'middle';
  const a = g.measureText('39').width, b = g.measureText('clips').width, pad = 18, gap = 16, total = a + pad * 2 + gap + b;
  g.fillStyle = C.amber; g.beginPath(); g.roundRect(-total / 2, -40, a + pad * 2, 80, 16); g.fill();
  g.fillStyle = '#14161B'; g.fillText('39', -total / 2 + pad, 3);
  g.fillStyle = C.white; g.fillText('clips', -total / 2 + a + pad * 2 + gap, 3);
  g.restore();
  // a small readout of which photograph this is
  g.fillStyle = 'rgba(207,216,255,0.7)'; g.font = '500 18px "Geist Mono", monospace'; g.textBaseline = 'alphabetic';
  g.fillText(`frame ${String(Math.round(k * 29) + 1).padStart(2, '0')} / 30`, 22, H - 24);
});
export const PAGE = {w: 0.9, h: 1.6};
export const pageMat = (k: number, chrome = true, dim = 1) => new THREE.MeshBasicMaterial({map: pageTex(k, chrome), toneMapped: false, color: new THREE.Color(dim, dim, dim), side: THREE.DoubleSide});
