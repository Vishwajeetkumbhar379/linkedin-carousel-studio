// The audio lane: the real "Hey, I'm Rish" clip from Week 1 as a waveform terrain beside the rail,
// with each word stamped as a glass box carrying its real Whisper start and end times.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import rish from '../data/rish.json';
import {C, FLOOR_Y, Label} from './kit';
import {Z} from './rail';

export const AUDIO = {x: 1.45, width: 2.0, perSec: 3.0, z0: Z.audio};
export const zAt = (tau: number) => AUDIO.z0 - tau * AUDIO.perSec;
export const WORDS = rish.words as {w: string; s: number; e: number}[];
const ENV = rish.env as number[];
const envAt = (tau: number) => { const i = tau * rish.rate, a = Math.floor(i), f = i - a; return (ENV[a] ?? 0) * (1 - f) + (ENV[a + 1] ?? 0) * f; };
// height of the terrain at lane offset u (-1..1 across the lane) and clip time tau
export const heightAt = (u: number, tau: number, swell = 1) => {
  const e = Math.pow(envAt(tau), 1.6);
  return FLOOR_Y + 0.02 + e * 1.25 * swell * Math.exp(-u * u * 2.2) * (0.85 + 0.15 * Math.sin(u * 9 + tau * 13));
};
const DUR = 4.7;

// `lift(tau)`: 0..1 how far a stretch is lifted out (the cut), `gapShift`: how far later audio has
// slid back toward earlier audio (seconds), `hot`: [s, e] stretch drawn amber.
export const AudioTerrain: React.FC<{lift?: (tau: number) => number; gapShift?: number; hot?: [number, number] | null; swell?: number}> = ({lift, gapShift = 0, hot = null, swell = 1}) => {
  const {surface, ridges} = useMemo(() => {
    const nx = 36, nz = 560;
    const surface = new THREE.PlaneGeometry(AUDIO.width, DUR * AUDIO.perSec, nx, nz);
    surface.rotateX(-Math.PI / 2);
    const p = surface.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const u = p.getX(i) / (AUDIO.width / 2), tau = (-(p.getZ(i)) + (DUR * AUDIO.perSec) / 2) / AUDIO.perSec;
      p.setY(i, heightAt(u, tau, swell) - 0.01);
    }
    surface.translate(0, 0, -(DUR * AUDIO.perSec) / 2); // tau = 0 at the near end (z = 0), like the ridges
    surface.computeVertexNormals();
    // ridgelines along the lane: thin ribbons that follow the terrain
    const ridges: {u: number; pts: THREE.Vector3[]}[] = [];
    for (let k = 0; k < 11; k++) {
      const u = -0.9 + (k / 10) * 1.8, pts: THREE.Vector3[] = [];
      for (let j = 0; j <= 470; j++) { const tau = (j / 470) * DUR; pts.push(new THREE.Vector3(u * (AUDIO.width / 2), heightAt(u, tau, swell), -tau * AUDIO.perSec)); }
      ridges.push({u, pts});
    }
    return {surface, ridges};
  }, [swell]);
  const ribbon = (pts: THREE.Vector3[], hotRange: [number, number] | null, want: 'hot' | 'cool') => {
    const P: number[] = [];
    for (let j = 0; j < pts.length - 1; j++) {
      const tau = (j / (pts.length - 1)) * DUR, isHot = !!hotRange && tau >= hotRange[0] && tau <= hotRange[1];
      if ((want === 'hot') !== isHot) continue;
      const a = pts[j], b = pts[j + 1], w = 0.007;
      const la = (lift?.(tau) ?? 0), lb = (lift?.(tau + DUR / 470) ?? 0);
      const sh = (t: number) => (t > 2.0 ? gapShift * AUDIO.perSec : 0);
      const ya = a.y + la * 0.9, yb = b.y + lb * 0.9, za = a.z + sh(tau), zb = b.z + sh(tau);
      P.push(a.x - w, ya, za, a.x + w, ya, za, b.x - w, yb, zb, b.x - w, yb, zb, a.x + w, ya, za, b.x + w, yb, zb);
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
    return g;
  };
  return (
    <group position={[AUDIO.x, 0, AUDIO.z0]}>
      <mesh geometry={surface}>
        <meshPhysicalMaterial color="#0c1020" roughness={0.35} metalness={0.2} clearcoat={0.8} emissive="#141a33" emissiveIntensity={0.4} transparent opacity={0.92} />
      </mesh>
      {ridges.map(({u, pts}, k) => (
        <group key={k}>
          <mesh geometry={ribbon(pts, hot, 'cool')}><meshBasicMaterial color={new THREE.Color('#b8c6ff').multiplyScalar(0.75 + 0.25 * Math.cos(u * 1.6))} side={THREE.DoubleSide} toneMapped={false} /></mesh>
          {hot ? <mesh geometry={ribbon(pts, hot, 'hot')}><meshBasicMaterial color={new THREE.Color(C.amberHot).multiplyScalar(1.4)} side={THREE.DoubleSide} toneMapped={false} /></mesh> : null}
        </group>
      ))}
    </group>
  );
};

// One stamped word: a glass plate floating over its stretch of terrain like a clip on a timeline,
// the word on top, its real start and end times on tags at the plate's two ends.
export const WordBox: React.FC<{w: {w: string; s: number; e: number}; face: THREE.Vector3; stamp?: number; hot?: boolean; flags?: boolean; label?: boolean; tier?: number}> = ({w, face, stamp = 1, hot = false, flags = true, label = true, tier = 0}) => {
  const z0 = zAt(w.s), z1 = zAt(w.e), len = Math.max(0.12, z0 - z1);
  let peak = 0; for (let t = w.s; t <= w.e; t += 0.01) peak = Math.max(peak, heightAt(0, t) - FLOOR_Y);
  const y = peak + 0.1 + (1 - stamp) * 1.4, col = hot ? C.amber : '#9fb2ff';
  const edges = useMemo(() => new THREE.EdgesGeometry(new THREE.BoxGeometry(AUDIO.width * 0.7, 0.05, len)), [len]);
  const tag = {font: 'mono' as const, weight: 500, color: hot ? C.amberHot : '#cfd8ff', bg: 'rgba(8,10,20,0.78)', pad: 0.3};
  return (
    <group position={[AUDIO.x, FLOOR_Y + y, (z0 + z1) / 2]}>
      <mesh>
        <boxGeometry args={[AUDIO.width * 0.7, 0.05, len]} />
        <meshPhysicalMaterial color={hot ? '#3a2410' : '#1a2340'} transparent opacity={0.55 * stamp} roughness={0.1} clearcoat={1} depthWrite={false} emissive={col} emissiveIntensity={hot ? 0.5 : 0.25} />
      </mesh>
      <lineSegments geometry={edges}><lineBasicMaterial color={new THREE.Color(col).multiplyScalar(hot ? 1.6 : 1.1)} transparent opacity={stamp} toneMapped={false} /></lineSegments>
      {label ? <Label text={w.w.replace(/[,.]$/, '')} h={0.24} position={[0, 0.2 + tier * 0.3, 0]} face={face} style={{weight: 800, color: hot ? C.amberHot : C.white}} opacity={stamp} /> : null}
      {flags ? (
        <>
          <Label text={w.s.toFixed(2)} h={0.085} position={[-AUDIO.width * 0.35, 0.08, len / 2]} face={face} style={tag} opacity={stamp} anchor="right" />
          <Label text={w.e.toFixed(2)} h={0.085} position={[AUDIO.width * 0.35, 0.08, -len / 2]} face={face} style={tag} opacity={stamp} anchor="left" />
        </>
      ) : null}
    </group>
  );
};
