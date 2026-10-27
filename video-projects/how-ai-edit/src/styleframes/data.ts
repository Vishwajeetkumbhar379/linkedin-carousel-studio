// Beat 1 ("this video was 39 clips on my phone"): his frozen frame cracks into 39 shards that
// fly into the phone's camera roll and turn into the 39 real clips. Shared by every style frame.
import {random} from 'remotion';

// The 39 raw clips of the Week 1 reel, in folder order, with their real lengths (ffprobe, 24 Oct).
// Tiles of strangers, a stock sticker and other people's children are blurred (t*.jpg).
export const CLIP_SECONDS = [
  10.1, 0.9, 22.1, 9.1, 15.9, 22.1, 11.7, 17.3, 12.9, 14.4, 8.4, 3.5, 5.4, 5.4, 8.1, 18.2, 7.0, 14.6, 20.8, 9.8,
  24.6, 8.8, 15.1, 25.5, 16.6, 16.1, 19.6, 47.5, 38.7, 16.1, 15.6, 20.4, 45.3, 41.8, 19.3, 21.7, 7.5, 9.1, 195.1,
];
export const N = CLIP_SECONDS.length; // 39
export const tile = (i: number) => `clips/t${String(i + 1).padStart(2, '0')}.jpg`;
export const FACE = 'freeze.jpg'; // the frame he freezes on, from his real take (vo/oncam.py)
export const dur = (s: number) => { const t = Math.round(s); return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`; };

// The camera roll: 5 columns, 8 rows (7 full + 4), square tiles, like the Photos app zoomed out.
export const COLS = 5;
export const ROWS = Math.ceil(N / COLS);

type P = [number, number];
// The frame is 1 wide and A tall (9:16), y down, matching image coordinates.
export const A = 16 / 9;

// Clip the convex polygon to the half plane closer to a than to b.
const clipHalf = (poly: P[], a: P, b: P): P[] => {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, nx = b[0] - a[0], ny = b[1] - a[1];
  const side = (p: P) => (p[0] - mx) * nx + (p[1] - my) * ny; // < 0: a's side
  const out: P[] = [];
  for (let i = 0; i < poly.length; i++) {
    const p = poly[i], q = poly[(i + 1) % poly.length], sp = side(p), sq = side(q);
    if (sp <= 0) out.push(p);
    if (sp * sq < 0) { const t = sp / (sp - sq); out.push([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]); }
  }
  return out;
};
const area = (poly: P[]) => poly.reduce((s, p, i) => { const q = poly[(i + 1) % poly.length]; return s + p[0] * q[1] - q[0] * p[1]; }, 0) / 2;
const centroid = (poly: P[]): P => {
  let cx = 0, cy = 0;
  const a = area(poly);
  poly.forEach((p, i) => { const q = poly[(i + 1) % poly.length], c = p[0] * q[1] - q[0] * p[1]; cx += (p[0] + q[0]) * c; cy += (p[1] + q[1]) * c; });
  return [cx / (6 * a), cy / (6 * a)];
};
const voronoi = (seeds: P[]) => seeds.map((s, i) => seeds.reduce<P[]>((poly, o, j) => (i === j ? poly : clipHalf(poly, s, o)), [[0, 0], [1, 0], [1, A], [0, A]]));

// The crack starts at his mouth, where the word "39" is said.
export const IMPACT: P = [0.53, 0.62 * A];

export type Shard = {
  i: number; // which clip it becomes
  poly: P[]; // in frame units, 48 points resampled around the outline, clockwise from the top
  c: P; // centroid
  cell: {col: number; row: number};
  leave: number; // 0..1 progress of the beat when it leaves the frame
};

// Resample a closed polygon to n points evenly spaced along its outline, starting at its top point.
const resample = (poly: P[], n: number): P[] => {
  const top = poly.reduce((b, p, i) => (p[1] < poly[b][1] ? i : b), 0);
  const ring = [...poly.slice(top), ...poly.slice(0, top)];
  const seg = ring.map((p, i) => { const q = ring[(i + 1) % ring.length]; return Math.hypot(q[0] - p[0], q[1] - p[1]); });
  const total = seg.reduce((a, b) => a + b, 0);
  const out: P[] = [];
  let k = 0, acc = 0;
  for (let j = 0; j < n; j++) {
    const d = (j / n) * total;
    while (acc + seg[k] < d) { acc += seg[k]; k++; }
    const t = (d - acc) / seg[k], p = ring[k], q = ring[(k + 1) % ring.length];
    out.push([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]);
  }
  return out;
};
// The square the shard becomes, as the same number of points, starting top-left, same winding.
export const squarePts = (n: number, half: number): P[] => {
  const out: P[] = [];
  for (let j = 0; j < n; j++) {
    const u = (j / n) * 4, side = Math.floor(u), t = u - side;
    const c: P[] = [[-half, -half], [half, -half], [half, half], [-half, half]];
    const p = c[side], q = c[(side + 1) % 4];
    out.push([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]);
  }
  return out;
};
export const PTS = 48;

export const SHARDS: Shard[] = (() => {
  // even-ish seeds: jittered grid, a little denser around the face, then two Lloyd steps
  let seeds: P[] = [];
  for (let k = 0; k < N; k++) seeds.push([0.06 + random(`sx${k}`) * 0.88, (0.05 + random(`sy${k}`) * 0.9) * A]);
  for (let it = 0; it < 3; it++) seeds = voronoi(seeds).map(centroid);
  const polys = voronoi(seeds);
  const shards = polys.map((poly, k) => ({poly, c: centroid(poly), k}));
  // top of the frame goes to the top of the camera roll, reading order
  const byRow = [...shards].sort((a, b) => a.c[1] - b.c[1]);
  const rows: typeof shards[] = [];
  for (let r = 0; r < ROWS; r++) rows.push(byRow.slice(r * COLS, r * COLS + COLS).sort((a, b) => a.c[0] - b.c[0]));
  const out: Shard[] = [];
  rows.forEach((row, r) => row.forEach((s) => out.push({i: 0, poly: resample(s.poly, PTS), c: s.c, cell: {col: 0, row: 0}, leave: 0})));
  // the outside leaves first and his face holds until last; the roll fills in the order they land
  const far = [...out].sort((a, b) => Math.hypot(b.c[0] - IMPACT[0], b.c[1] - IMPACT[1]) - Math.hypot(a.c[0] - IMPACT[0], a.c[1] - IMPACT[1]));
  far.forEach((s, rank) => { s.leave = 0.14 + (rank / (N - 1)) * 0.54; s.i = rank; s.cell = {col: rank % COLS, row: Math.floor(rank / COLS)}; });
  return out.sort((a, b) => a.i - b.i);
})();

export const FLIGHT = 0.26; // share of the beat a shard spends in the air
export const CRACK = [0.04, 0.14]; // the cracks run out from the impact
const smooth = (t: number) => { const x = Math.min(1, Math.max(0, t)); return x * x * (3 - 2 * x); };
// 0 in the frame, 0..1 in flight, 1 landed
export const flight = (s: Shard, p: number) => smooth((p - s.leave) / FLIGHT);
export const crackReach = (p: number) => smooth((p - CRACK[0]) / (CRACK[1] - CRACK[0]));
// how far the crack has run past this shard's nearest edge (0..1): cracks open from the impact out
export const cracked = (s: Shard, p: number) => {
  const d = Math.hypot(s.c[0] - IMPACT[0], s.c[1] - IMPACT[1]) / 1.6;
  return smooth((crackReach(p) - d) * 5 + 0.4);
};
