// The caption lane as a split-flap board: one tile per letter, each with a top and a bottom half.
// A flip drops the top flap: its front carries the old letter's top half, its back the new letter's
// bottom half, so a letter changes the way a station board does.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {C} from './kit';

const TW = 0.2, TH = 0.3, GAP = 0.012;
const halfTex = new Map<string, THREE.CanvasTexture>();
// top or bottom half of a letter, light on a dark tile; `tone` colours the letter
const half = (ch: string, top: boolean, tone: string) => {
  const key = `${ch}|${top}|${tone}`;
  let t = halfTex.get(key);
  if (!t) {
    const c = document.createElement('canvas'); c.width = 128; c.height = 96;
    const g = c.getContext('2d')!;
    const gr = g.createLinearGradient(0, 0, 0, 96); gr.addColorStop(0, top ? '#22252e' : '#1a1c23'); gr.addColorStop(1, top ? '#1b1d24' : '#121318');
    g.fillStyle = gr; g.fillRect(0, 0, 128, 96);
    g.fillStyle = tone; g.font = `800 150px Geist, system-ui, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
    if (ch !== ' ') g.fillText(ch, 64, top ? 100 : -4); // the letter's centre sits on the split line
    t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    halfTex.set(key, t);
  }
  return t;
};
const mat = (ch: string, top: boolean, tone: string, glow: number) => new THREE.MeshPhysicalMaterial({map: half(ch, top, tone), roughness: 0.35, clearcoat: 0.6, emissive: '#ffffff', emissiveMap: half(ch, top, tone), emissiveIntensity: glow, side: THREE.DoubleSide});

// One tile. `flip` 0..1 turns `from` into `to`.
export const Flap: React.FC<{from: string; to?: string; flip?: number; tone?: string; toTone?: string; glow?: number}> = ({from, to = from, flip = 0, tone = C.white, toTone = tone, glow = 0.35}) => {
  const a = Math.min(1, Math.max(0, flip)) * Math.PI;
  const m = useMemo(() => ({
    newTop: mat(to, true, toTone, glow), oldBottom: mat(from, false, tone, glow), oldTop: mat(from, true, tone, glow), newBottom: mat(to, false, toTone, glow),
  }), [from, to, tone, toTone, glow]);
  const hh = (TH - GAP) / 2;
  return (
    <group>
      <mesh position={[0, -0.002, -0.004]}><boxGeometry args={[TW + 0.02, TH + 0.02, 0.006]} /><meshStandardMaterial color="#08090c" roughness={0.6} /></mesh>
      {/* behind the falling flap: the new top, the old bottom (until the flap lands on it) */}
      <mesh position={[0, GAP / 2 + hh / 2, 0]} material={m.newTop}><planeGeometry args={[TW, hh]} /></mesh>
      <mesh position={[0, -GAP / 2 - hh / 2, 0]} material={a < Math.PI / 2 ? m.oldBottom : m.newBottom}><planeGeometry args={[TW, hh]} /></mesh>
      {/* the falling flap, hinged on the split */}
      {flip > 0 && flip < 1 ? (
        <group rotation={[-a, 0, 0]} position={[0, 0, 0.004]}>
          <mesh position={[0, GAP / 2 + hh / 2, 0]} material={a < Math.PI / 2 ? m.oldTop : m.newBottom} rotation={[a < Math.PI / 2 ? 0 : Math.PI, 0, 0]}><planeGeometry args={[TW, hh]} /></mesh>
        </group>
      ) : null}
      {/* the hinge line */}
      <mesh position={[0, 0, 0.002]}><boxGeometry args={[TW, GAP * 0.6, 0.004]} /><meshBasicMaterial color="#050506" /></mesh>
    </group>
  );
};

// A word of tiles laid left to right along +x of its group.
export const FlapWord: React.FC<{text: string; to?: string; flips?: number[]; tone?: string; toTone?: string; glow?: number}> = ({text, to, flips = [], tone, toTone, glow}) => (
  <group>
    {[...text].map((ch, i) => (
      <group key={i} position={[i * (TW + 0.03), 0, 0]}>
        <Flap from={ch} to={to?.[i] ?? ch} flip={flips[i] ?? 0} tone={tone} toTone={toTone} glow={glow} />
      </group>
    ))}
  </group>
);
export const FLAP_W = TW + 0.03;
