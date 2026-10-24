// The 39 shards as real slabs: his frozen frame on the front, the clip it becomes on the back,
// edges that catch the light. Rebuilt every frame from the beat's progress `p`.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {random} from 'remotion';
import {A, PTS, SHARDS, Shard, flight, cracked, squarePts} from './data';
import {CELL, SW as SCREEN_W, cellRect} from './roll';
import {PHONE, screenPoint} from '../kit/phone';

export type Pose = {pos: THREE.Vector3; quat: THREE.Quaternion; scale: number};
export type ShardLook = {
  face: (tex: THREE.Texture) => THREE.Material;
  clip: (tex: THREE.Texture) => THREE.Material;
  edge: THREE.Material;
  thick: number;
  shadows?: boolean;
};

const smooth = (t: number) => { const x = Math.min(1, Math.max(0, t)); return x * x * (3 - 2 * x); };

// Where a shard sits in the pane and where its cell is on the phone, in world space.
export const shardEnds = (s: Shard, pane: Pose, phone: Pose) => {
  const local = new THREE.Vector3((s.c[0] - 0.5) * pane.scale, -(s.c[1] - A / 2) * pane.scale, 0);
  const start = local.applyQuaternion(pane.quat).add(pane.pos);
  const r = cellRect(s.cell.col, s.cell.row);
  const [x, y] = screenPoint(r.x + r.w / 2, r.y + r.h / 2, 0);
  const end = new THREE.Vector3(x * phone.scale, y * phone.scale, 0.012 * phone.scale).applyQuaternion(phone.quat).add(phone.pos);
  return {start, end};
};
export const tileWorld = (phone: Pose) => (CELL / SCREEN_W) * PHONE.screenW * phone.scale;

const FLIP = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI);

// The pose and outline of shard s at progress p (null once it has landed: the screen shows it).
export const shardAt = (s: Shard, p: number, pane: Pose, phone: Pose) => {
  const f = flight(s, p);
  if (f >= 0.985) return null;
  const {start, end} = shardEnds(s, pane, phone);
  const k = cracked(s, p);
  // after the crack each shard sits a hair off true, so the light catches every piece differently
  const jit = new THREE.Quaternion().setFromEuler(new THREE.Euler((random(`jx${s.i}`) - 0.5) * 0.06 * k, (random(`jy${s.i}`) - 0.5) * 0.08 * k, 0));
  const q0 = pane.quat.clone().multiply(jit);
  const q1 = phone.quat.clone().multiply(FLIP);
  const quat = q0.clone().slerp(q1, smooth(f * 1.15));
  const tumble = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(random(`ax${s.i}`) - 0.5, random(`ay${s.i}`) - 0.5, 0.4).normalize(), Math.sin(Math.PI * f) * (0.5 + random(`ta${s.i}`) * 0.7));
  quat.premultiply(tumble);
  // an arc that swings toward the lens and out to the side before dropping into the cell;
  // every fifth piece swings right past the lens, big and soft, for depth
  const near = s.i % 5 === 2;
  const ctrl = start.clone().lerp(end, 0.45).add(new THREE.Vector3((random(`cx${s.i}`) - 0.5) * 1.6 + (s.c[0] - 0.5) * (near ? 3.2 : 1.4), 0.35 + random(`cy${s.i}`) * 0.6, near ? 3.6 : 1.0 + random(`cz${s.i}`) * 0.9));
  const u = smooth(f), a = (1 - u) ** 2, b = 2 * (1 - u) * u, c = u * u;
  const pos = start.clone().multiplyScalar(a).add(ctrl.clone().multiplyScalar(b)).add(end.clone().multiplyScalar(c));
  pos.add(new THREE.Vector3(0, 0, 0.015 * k)); // the cracked pane bulges toward us by a hair
  // the outline turns from shard to square on the way down
  const m = smooth((f - 0.2) / 0.75), half = tileWorld(phone) / 2, sq = squarePts(PTS, half);
  const shrink = 1 - 0.035 * k; // the crack gaps
  const pts = s.poly.map((pt, j) => {
    const x = (pt[0] - s.c[0]) * pane.scale * shrink, y = -(pt[1] - s.c[1]) * pane.scale * shrink;
    return [x + (sq[j][0] - x) * m, y + (-sq[j][1] - y) * m] as [number, number];
  });
  return {pos, quat, pts, f};
};

// One slab: a fan for the front (face image UVs), a fan for the back (clip UVs), a ribbon for the edge.
const slab = (s: Shard, outline: [number, number][], thick: number) => {
  // the outline runs clockwise with y up; walk it backwards so the front fan faces +z
  const n = outline.length, P: number[] = [], Nn: number[] = [], U: number[] = [];
  const pts = outline.map((_, j) => outline[n - 1 - j]), src = s.poly.map((_, j) => s.poly[n - 1 - j]);
  const geo = new THREE.BufferGeometry();
  const cx = pts.reduce((a, p) => a + p[0], 0) / n, cy = pts.reduce((a, p) => a + p[1], 0) / n;
  const faceUV = (j: number) => [src[j][0], 1 - src[j][1] / A];
  const fc = [s.c[0], 1 - s.c[1] / A];
  // back: square crop of the 9:16 clip, mirrored because we see it from behind
  let minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity;
  pts.forEach(([x, y]) => { minx = Math.min(minx, x); maxx = Math.max(maxx, x); miny = Math.min(miny, y); maxy = Math.max(maxy, y); });
  const v0 = (1 - 9 / 16) * 0.4;
  const backUV = (x: number, y: number) => [1 - (x - minx) / (maxx - minx), 1 - (v0 + ((maxy - y) / (maxy - miny)) * (9 / 16))];
  // front
  for (let j = 0; j < n; j++) {
    const a = pts[j], b = pts[(j + 1) % n];
    P.push(cx, cy, 0, a[0], a[1], 0, b[0], b[1], 0);
    Nn.push(0, 0, 1, 0, 0, 1, 0, 0, 1);
    U.push(...fc, ...faceUV(j), ...faceUV((j + 1) % n));
  }
  const nf = P.length / 3;
  // back (reverse winding)
  for (let j = 0; j < n; j++) {
    const a = pts[j], b = pts[(j + 1) % n];
    P.push(cx, cy, -thick, b[0], b[1], -thick, a[0], a[1], -thick);
    Nn.push(0, 0, -1, 0, 0, -1, 0, 0, -1);
    U.push(...backUV(cx, cy), ...backUV(b[0], b[1]), ...backUV(a[0], a[1]));
  }
  const nb = P.length / 3 - nf;
  // edge ribbon (now counter-clockwise, so the outward normal is (dy, -dx))
  for (let j = 0; j < n; j++) {
    const a = pts[j], b = pts[(j + 1) % n];
    let nx = b[1] - a[1], ny = -(b[0] - a[0]);
    const l = Math.hypot(nx, ny) || 1; nx /= l; ny /= l;
    P.push(a[0], a[1], 0, a[0], a[1], -thick, b[0], b[1], 0, b[0], b[1], 0, a[0], a[1], -thick, b[0], b[1], -thick);
    for (let k = 0; k < 6; k++) { Nn.push(nx, ny, 0); U.push(0, 0); }
  }
  geo.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(Nn, 3));
  geo.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2));
  geo.addGroup(0, nf, 0); geo.addGroup(nf, nb, 1); geo.addGroup(nf + nb, P.length / 3 - nf - nb, 2);
  return geo;
};

export const Shards3D: React.FC<{p: number; pane: Pose; phone: Pose; face: HTMLImageElement; clips: HTMLImageElement[]; look: ShardLook; lights?: number; lightColor?: string}> = ({p, pane, phone, face, clips, look, lights = 3, lightColor = '#ffe2c4'}) => {
  const mats = useMemo(() => {
    const tex = (im: HTMLImageElement) => { const t = new THREE.Texture(im); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.needsUpdate = true; return t; };
    const faceM = look.face(tex(face));
    return clips.map((c) => [faceM, look.clip(tex(c)), look.edge]);
  }, [face, clips, look]);
  const live = SHARDS.map((s) => ({s, st: shardAt(s, p, pane, phone)})).filter((x) => x.st);
  // the biggest pieces in the air carry a light, so they light the phone and the floor as they pass
  const flyers = live.filter((x) => x.st!.f > 0.02).sort((a, b) => Math.sin(Math.PI * b.st!.f) - Math.sin(Math.PI * a.st!.f)).slice(0, lights);
  return (
    <group>
      {live.map(({s, st}) => (
        <mesh key={s.i} geometry={slab(s, st!.pts, look.thick)} material={mats[s.i]} position={st!.pos} quaternion={st!.quat} castShadow={look.shadows} receiveShadow={look.shadows} />
      ))}
      {flyers.map(({s, st}) => <pointLight key={`l${s.i}`} position={st!.pos.clone().add(new THREE.Vector3(0, 0, 0.12))} color={lightColor} intensity={1.1 * Math.sin(Math.PI * st!.f)} distance={3} decay={2} />)}
    </group>
  );
};
