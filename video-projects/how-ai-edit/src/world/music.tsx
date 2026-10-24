// The music lane: the first 6 s of the posted Week 1 reel's mix as a ridge, with the real true
// silence (2.57 to 2.87 s, under -50 dB) punched out as a clean hole.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import music from '../data/music.json';
import {C, FLOOR_Y, Label} from './kit';
import {Z} from './rail';

export const MUSIC = {x: 1.35, width: 1.8, perSec: 2.2, z0: Z.music};
export const mz = (tau: number) => MUSIC.z0 - tau * MUSIC.perSec;
const ENV = music.env as number[];
export const SIL = music.silence as [number, number];
const envAt = (tau: number) => { const i = tau * music.rate, a = Math.floor(i), f = i - a; return (ENV[a] ?? 0) * (1 - f) + (ENV[a + 1] ?? 0) * f; };
const hAt = (u: number, tau: number) => FLOOR_Y + 0.02 + Math.pow(envAt(tau), 1.6) * 0.75 * Math.exp(-u * u * 2) * (0.85 + 0.15 * Math.sin(u * 7 + tau * 11));

export const MusicRidge: React.FC<{face: THREE.Vector3; hole?: number}> = ({face, hole = 1}) => {
  const ribbons = useMemo(() => {
    const out: THREE.BufferGeometry[] = [];
    for (let k = 0; k < 7; k++) {
      const u = -0.85 + (k / 6) * 1.7, P: number[] = [];
      for (let j = 0; j < 600; j++) {
        const a = (j / 600) * 6, b = ((j + 1) / 600) * 6;
        if (hole > 0.5 && b > SIL[0] && a < SIL[1]) continue; // the hole
        const x = u * (MUSIC.width / 2), w = 0.008, ya = hAt(u, a), yb = hAt(u, b), za = -a * MUSIC.perSec, zb = -b * MUSIC.perSec;
        P.push(x - w, ya, za, x + w, ya, za, x - w, yb, zb, x - w, yb, zb, x + w, ya, za, x + w, yb, zb);
      }
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); out.push(g);
    }
    return out;
  }, [hole]);
  const z0 = -SIL[0] * MUSIC.perSec, z1 = -SIL[1] * MUSIC.perSec;
  const frame = useMemo(() => new THREE.EdgesGeometry(new THREE.BoxGeometry(MUSIC.width * 1.02, 1.1, z0 - z1)), [z0, z1]);
  return (
    <group position={[MUSIC.x, 0, MUSIC.z0]}>
      {ribbons.map((g, k) => <mesh key={k} geometry={g}><meshBasicMaterial color={new THREE.Color('#b8c6ff').multiplyScalar(0.8)} side={THREE.DoubleSide} toneMapped={false} /></mesh>)}
      {/* the hole: an empty box of air outlined in amber, the floor under it dark */}
      <lineSegments geometry={frame} position={[0, FLOOR_Y + 0.55, (z0 + z1) / 2]}><lineBasicMaterial color={new THREE.Color(C.amberHot).multiplyScalar(1.5 * hole)} toneMapped={false} /></lineSegments>
      <Label text="silence" h={0.16} position={[0, FLOOR_Y + 1.35, (z0 + z1) / 2]} face={face} style={{weight: 800, color: C.amberHot}} opacity={hole} />
      <Label text={`${SIL[0].toFixed(2)} to ${SIL[1].toFixed(2)} s, under -50 dB`} h={0.07} position={[0, FLOOR_Y + 1.17, (z0 + z1) / 2]} face={face} style={{font: 'mono', weight: 500, color: '#cfd8ff'}} opacity={hole} />
    </group>
  );
};
