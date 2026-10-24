// Line 5: "Then it cut. / Not between sentences: / between *words*."
// Down in the valley of the waveform. The blade snaps to the gap between two words like a magnet and
// the real cuts of the Week 1 edit lift out: a 0.05 s sliver between "Rish" and "I'm", and
// everything after 2.40 s. The ridges close up without a seam.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {cue} from '../lib';
import {Caption} from '../styleframes/caption';
import {C, FLOOR_Y, Label, canvasTex} from '../world/kit';
import {Cart, Rail} from '../world/rail';
import {AUDIO, AudioTerrain, WORDS, WordBox, zAt} from '../world/audio';
import {Shot, Stage, faceOf, sm, v3} from './base';

// a sheet of light standing across the lane: the blade
const Blade: React.FC<{tau: number; on: number; label?: string; face: THREE.Vector3}> = ({tau, on, label, face}) => {
  const tex = useMemo(() => canvasTex(4, 256, (g) => { const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.7, 'rgba(255,255,255,0.35)'); gr.addColorStop(1, 'rgba(255,255,255,1)'); g.fillStyle = gr; g.fillRect(0, 0, 4, 256); }), []);
  if (on <= 0) return null;
  return (
    <group position={[AUDIO.x, FLOOR_Y, zAt(tau)]}>
      <mesh position={[0, 0.85, 0]}>
        <planeGeometry args={[AUDIO.width * 1.05, 1.7]} />
        <meshBasicMaterial map={tex} color={new THREE.Color(C.amberHot).multiplyScalar(1.4)} transparent opacity={0.75 * on} blending={THREE.AdditiveBlending} depthWrite={false} side={THREE.DoubleSide} toneMapped={false} />
      </mesh>
      <mesh position={[0, 0.02, 0]}><boxGeometry args={[AUDIO.width * 1.05, 0.012, 0.02]} /><meshBasicMaterial color={new THREE.Color(C.amberHot).multiplyScalar(2)} toneMapped={false} /></mesh>
      <pointLight position={[0, 0.5, 0.3]} color={C.amber} intensity={2.5 * on} distance={3} decay={2} />
      {label ? <Label text={label} h={0.1} position={[-AUDIO.width * 0.55, 1.78, 0]} face={face} style={{font: 'mono', weight: 500, color: C.amberHot, bg: 'rgba(20,12,6,0.8)', pad: 0.35}} opacity={on} anchor="right" /> : null}
    </group>
  );
};

export const A05: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const t0 = cue("Then it cut not"), notB = cue("Not between"), betw = cue("between words");
  const snap1 = sm(t0 + 0.15, t0 + 0.45, t), snap2 = sm(notB + 0.3, notB + 0.6, t);
  const out1 = sm(t0 + 0.5, t0 + 1.0, t), out2 = sm(notB + 0.6, betw, t);
  const lift = (tau: number) => (tau > 1.3 && tau < 1.35 ? out1 : tau > 2.4 ? out2 : 0);
  const shot: Shot = {cam: v3(0.05, FLOOR_Y + 2.5, zAt(0.9) + 3.3), look: v3(AUDIO.x + 0.1, FLOOR_Y + 0.3, zAt(2.3))};
  const face = faceOf(shot);
  const caption = t < notB - 0.1 ? {w: ['Then', 'it', 'cut'], p: 2} : t < betw - 0.1 ? {w: ['not', 'between', 'sentences'], p: -1} : {w: ['between', 'words'], p: 1};
  return (
    <Stage fr={fr} shot={shot} overlay={<Caption words={caption.w} pill={caption.p} top={1060} />}>
      <Rail played={zAt(1.3)} />
      <AudioTerrain lift={lift} gapShift={-0.05 * out1} />
      {WORDS.slice(0, 5).map((w, i) => <WordBox key={i} w={i === 2 ? {...w, w: 'Vish,'} : w} face={face} flags={false} label={i !== 1} />)}
      {/* the words after the cut lift out with their stretch of audio */}
      {WORDS.slice(5).map((w, i) => (
        <group key={i} position={[0, out2 * 0.9, 0]}><WordBox w={w} face={face} flags={false} label={false} stamp={1 - out2 * 0.85} /></group>
      ))}
      <Blade tau={1.3} on={snap1 * (1 - out2 * 0.7)} face={face} />
      <Blade tau={2.4} on={snap2} label="cut 2.40" face={face} />
      <Cart z={zAt(1.3)} face={face} scale={0.8} />
    </Stage>
  );
};
