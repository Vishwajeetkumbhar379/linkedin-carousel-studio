// Line 11: "And if you're still here, / the edit / did its *job*. // Comment *EDIT* / for the five prompts."
// The progress bar runs out at the end of the rail: one glowing dot left, labelled "you". Then the
// comment box: E, D, I, T go down as heavy keys and the five prompts of the free guide fan out.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {cue} from '../lib';
import {Caption} from '../styleframes/caption';
import {C, FLOOR_Y, Label, canvasTex} from '../world/kit';
import {RAIL, RAIL_Y, Rail} from '../world/rail';
import {GEIST} from '../styleframes/fonts';
import {Shot, Stage, faceOf, mixV, sm, v3} from './base';

// the five prompt templates in /resources/ai-edit-stack (section 4)
const PROMPTS = ['Transcribe', 'Cut plan', 'Storyboard', 'Build and sound', 'Export'];
const END = v3(0, RAIL_Y, RAIL.end);

const Key: React.FC<{ch: string; down: number; x: number}> = ({ch, down, x}) => {
  const legend = useMemo(() => canvasTex(256, 256, (g) => {
    const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, '#2a2e3b'); gr.addColorStop(1, '#171a22');
    g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
    g.fillStyle = C.amberHot; g.font = `800 150px ${GEIST}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(ch, 128, 136);
  }), [ch]);
  return (
    <group position={[x, -0.06 * down, 0]}>
      <mesh position={[0, -0.06, 0]}><boxGeometry args={[0.36, 0.12, 0.36]} /><meshPhysicalMaterial color="#141720" roughness={0.35} clearcoat={0.8} /></mesh>
      <mesh position={[0, 0.001, 0]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[0.32, 0.32]} /><meshPhysicalMaterial map={legend} emissive="#ffffff" emissiveMap={legend} emissiveIntensity={0.5 + down * 0.6} roughness={0.3} clearcoat={1} /></mesh>
    </group>
  );
};

const cardTex = (n: number, title: string) => canvasTex(360, 480, (g) => {
  g.fillStyle = '#12141c'; g.beginPath(); g.roundRect(0, 0, 360, 480, 26); g.fill();
  g.strokeStyle = 'rgba(159,178,255,0.45)'; g.lineWidth = 3; g.stroke();
  g.fillStyle = C.amber; g.font = `500 30px "Geist Mono", monospace`; g.fillText(`0${n}`, 28, 56);
  g.fillStyle = C.white; g.font = `800 40px ${GEIST}`;
  title.split(' ').reduce<string[]>((ls, w) => { const l = ls[ls.length - 1]; if (l && (l + ' ' + w).length <= 11) ls[ls.length - 1] = `${l} ${w}`; else ls.push(w); return ls; }, []).forEach((l, i) => g.fillText(l, 28, 120 + i * 46));
  g.fillStyle = 'rgba(207,216,255,0.35)'; for (let i = 0; i < 6; i++) g.fillRect(28, 260 + i * 30, 300 - (i % 3) * 60, 10);
});

export const A11: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const t0 = cue("And if you're"), job = cue("did its job"), comment = cue("Comment EDIT"), five = cue("five prompts");
  const run = sm(t0, job, t);
  const played = RAIL.start + (RAIL.end + 0.35 - RAIL.start) * (0.9 + 0.1 * run);
  const toBox = sm(comment - 0.5, comment, t);
  const keys = [0, 1, 2, 3].map((i) => sm(comment + 0.12 * i, comment + 0.12 * i + 0.1, t) * (1 - sm(comment + 0.12 * i + 0.12, comment + 0.12 * i + 0.3, t) * 0.6));
  const fan = sm(five - 0.3, five + 0.4, t);
  const cards = useMemo(() => PROMPTS.map((p, i) => cardTex(i + 1, p)), []);
  const A: Shot = {cam: v3(0.55, RAIL_Y + 0.65, RAIL.end + 3.0), look: v3(0, RAIL_Y + 0.1, RAIL.end - 0.6)};
  const BOX = v3(0, RAIL_Y + 1.6, RAIL.end - 2);
  const B: Shot = {cam: BOX.clone().add(v3(0, 1.05, 4.3)), look: BOX.clone().add(v3(0, 0.55, 0))};
  const shot: Shot = {cam: mixV(A.cam, B.cam, toBox), look: mixV(A.look, B.look, toBox)};
  const face = faceOf(shot);
  const caption = t < job - 0.2 ? {w: ["if", "you're", 'still', 'here'], p: -1} : t < comment - 0.1 ? {w: ['the', 'edit', 'did', 'its job'], p: 3} : {w: ['Comment', 'EDIT'], p: 1};
  return (
    <Stage fr={fr} shot={shot} overlay={<Caption words={caption.w} pill={caption.p} top={1060} />}>
      <Rail played={played} />
      {/* the end of the bar, and the one dot left: you */}
      <mesh position={[0, RAIL_Y, RAIL.end - 0.02]}><sphereGeometry args={[0.07, 24, 16]} /><meshBasicMaterial color={new THREE.Color(C.amberHot).multiplyScalar(1.8)} toneMapped={false} /></mesh>
      <pointLight position={[0, RAIL_Y + 0.25, RAIL.end]} color={C.amber} intensity={2.5} distance={3} decay={2} />
      <Label text="you" h={0.16} position={[0, RAIL_Y + 0.3, RAIL.end]} face={face} style={{weight: 800, color: C.amberHot}} opacity={1 - toBox} />
      {toBox > 0 ? (
        <group position={BOX}>
          {/* the comment field */}
          <mesh position={[0, 0.45, -0.25]} rotation={[-0.35, 0, 0]}><planeGeometry args={[2.0, 0.34]} /><meshPhysicalMaterial color="#0f121a" roughness={0.2} clearcoat={1} transparent opacity={0.9} /></mesh>
          <Label text={`${'EDIT'.slice(0, keys.filter((k) => k > 0.3).length)}${keys[3] > 0.3 ? '' : '|'}`} h={0.18} position={[-0.85, 0.47, -0.2]} rotation={[-0.35, 0, 0]} style={{font: 'mono', weight: 500, color: C.white}} anchor="left" />
          {['E', 'D', 'I', 'T'].map((ch, i) => <Key key={ch} ch={ch} down={keys[i]} x={(i - 1.5) * 0.42} />)}
          {/* the five prompts, fanning up out of the box */}
          {cards.map((tx, i) => {
            const u = i - 2, a = -u * 0.32 * fan;
            return (
              <group key={i} position={[0, 0.9 * fan, -0.6]} rotation={[0, 0, a]}>
                <mesh position={[u * 0.06 * fan, 0.62 * fan, u * 0.01]} scale={fan}><planeGeometry args={[0.6, 0.8]} /><meshBasicMaterial map={tx} transparent toneMapped={false} /></mesh>
              </group>
            );
          })}
        </group>
      ) : null}
    </Stage>
  );
};
