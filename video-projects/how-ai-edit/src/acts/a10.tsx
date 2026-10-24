// Line 10: "It took 12 drafts / of plain English feedback / from me. // Hi, / I'm *Vish*."
// Twelve framed drafts of the Week 1 reel stand along the rail, each showing the same moment of that
// version. Sticky notes carry his real feedback, in his words. v12 is lit: "I loved everything".
// The camera flies into v12, which becomes his room: "Hi, I'm Vish", and a name tag slaps onto the
// frame beside him, RISH struck out, VISH written over it.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {cue} from '../lib';
import {Caption} from '../styleframes/caption';
import {C, FLOOR_Y, Label, canvasTex, useTextures} from '../world/kit';
import {Cart, Rail, Z} from '../world/rail';
import {GEIST} from '../styleframes/fonts';
import {Shot, Stage, faceOf, mixV, sm, v3} from './base';

// his feedback in the chat, matched to the draft he was watching (by the time he sent it)
const NOTES: Record<number, string> = {3: 'Speed it up a bit. Not too fast.', 4: 'Do proper sound design.', 6: 'Not this sad music.', 7: "That doesn't make any sense.", 12: 'I loved everything.'};
const CARD = {w: 0.56, h: 0.996};
const pos = (v: number) => v3(v % 2 ? -0.62 : 0.62, FLOOR_Y + 0.75, Z.drafts - (v - 1) * 1.7);

const noteTex = (text: string, hot: boolean) => canvasTex(360, 300, (g) => {
  g.fillStyle = hot ? '#ffd9a8' : '#f3ecd6'; g.fillRect(0, 0, 360, 300);
  g.fillStyle = 'rgba(0,0,0,0.06)'; g.fillRect(0, 0, 360, 34);
  g.fillStyle = '#1b1a17'; g.font = `700 40px ${GEIST}`; g.textBaseline = 'top';
  const words = text.split(' '), lines: string[] = []; let cur = '';
  words.forEach((w) => { const s = cur ? `${cur} ${w}` : w; if (g.measureText(s).width > 310) { lines.push(cur); cur = w; } else cur = s; });
  lines.push(cur);
  lines.forEach((l, i) => g.fillText(l, 24, 56 + i * 50));
  g.fillStyle = '#6b665a'; g.font = `500 22px "Geist Mono", monospace`; g.fillText('Vish', 24, 300 - 40);
});

export const A10: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const tex = useTextures(Array.from({length: 12}, (_, i) => `drafts/v${i + 1}.jpg`));
  const t0 = cue("It took 12"), plain = cue("plain English"), hi = cue("Hi I'm Vish"), vish = cue("Vish");
  const notes = useMemo(() => Object.fromEntries(Object.entries(NOTES).map(([v, s]) => [v, noteTex(s, v === '12')])), []);
  const run = sm(t0, hi - 0.4, t), into = sm(hi - 0.6, hi + 0.05, t);
  const A: Shot = {cam: v3(0.1, FLOOR_Y + 1.15, Z.drafts + 2.6), look: v3(0, FLOOR_Y + 0.75, Z.drafts - 8)};
  const B: Shot = {cam: v3(0.15, FLOOR_Y + 1.05, pos(12).z + 3.6), look: v3(pos(12).x * 0.9, FLOOR_Y + 0.8, pos(12).z)};
  const C12: Shot = {cam: pos(12).clone().add(v3(-0.05, 0, 0.62)), look: pos(12)};
  const shot: Shot = into > 0 ? {cam: mixV(B.cam, C12.cam, into), look: mixV(B.look, C12.look, into)} : {cam: mixV(A.cam, B.cam, run), look: mixV(A.look, B.look, run)};
  const face = faceOf(shot);
  const onCam = t >= hi; // "Hi, I'm Vish": his own footage, full frame
  const slap = sm(vish - 0.05, vish + 0.12, t);
  const caption = t < plain - 0.1 ? {w: ['12', 'drafts'], p: 0} : t < hi - 0.1 ? {w: ['plain English', 'feedback'], p: 0} : {w: ['Hi,', "I'm", 'Vish'], p: 2};
  if (onCam) {
    return (
      <AbsoluteFill style={{background: '#000'}}>
        <Img src={staticFile('vish_still.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        {/* the name tag, slapped onto the frame beside his face, never on it */}
        <div style={{position: 'absolute', left: 60, top: 420, width: 330, transform: `rotate(-8deg) scale(${0.6 + 0.4 * slap})`, opacity: slap, transformOrigin: 'center', boxShadow: '0 18px 40px rgba(0,0,0,0.45)', borderRadius: 18, overflow: 'hidden', fontFamily: GEIST}}>
          <div style={{background: C.amber, color: '#14161B', textAlign: 'center', padding: '12px 0 8px', fontWeight: 800, fontSize: 40, lineHeight: 1}}>HELLO<div style={{fontSize: 20, fontWeight: 700, marginTop: 4}}>my name is</div></div>
          <div style={{background: '#f6f3ec', height: 150, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
            <span style={{fontSize: 64, fontWeight: 800, color: '#9a958a', position: 'absolute', top: 18, left: 62}}>RISH<span style={{position: 'absolute', left: -8, right: -8, top: 34, height: 7, background: C.red, transform: 'rotate(-6deg)'}} /></span>
            <span style={{fontSize: 76, fontWeight: 800, color: '#14161B', position: 'absolute', top: 58, left: 120, transform: 'rotate(-4deg)', fontStyle: 'italic'}}>VISH</span>
          </div>
        </div>
        <Caption words={caption.w} pill={caption.p} top={300} />
      </AbsoluteFill>
    );
  }
  return (
    <Stage fr={fr} shot={shot} overlay={<Caption words={caption.w} pill={caption.p} top={1060} />}>
      <Rail played={shot.cam.z - 1} />
      <Cart z={shot.cam.z - 1.4} face={face} scale={0.7} />
      {tex ? Array.from({length: 12}, (_, i) => {
        const v = i + 1, p = pos(v), hot = v === 12, note = notes[v];
        return (
          <group key={v} position={p} rotation={[0, v % 2 ? 0.35 : -0.35, 0]}>
            <mesh position={[0, 0, -0.012]}><boxGeometry args={[CARD.w + 0.06, CARD.h + 0.06, 0.02]} /><meshPhysicalMaterial color={hot ? '#3a2410' : '#151821'} roughness={0.3} clearcoat={1} emissive={hot ? C.amber : '#000000'} emissiveIntensity={hot ? 0.9 : 0} /></mesh>
            <mesh><planeGeometry args={[CARD.w, CARD.h]} /><meshBasicMaterial map={tex[i]} toneMapped={false} color={new THREE.Color(hot ? 1 : 0.72, hot ? 1 : 0.72, hot ? 1 : 0.72)} /></mesh>
            <Label text={`v${v}`} h={0.09} position={[0, -CARD.h / 2 - 0.11, 0.01]} style={{font: 'mono', weight: 500, color: hot ? C.amberHot : '#cfd8ff'}} />
            {note ? (
              <mesh position={[CARD.w * 0.28, CARD.h * 0.3, 0.02]} rotation={[0, 0, v % 2 ? 0.08 : -0.07]}>
                <planeGeometry args={[0.42, 0.35]} />
                <meshStandardMaterial map={note} roughness={0.8} emissive="#ffffff" emissiveMap={note} emissiveIntensity={0.55} />
              </mesh>
            ) : null}
            {hot ? <pointLight position={[0, 0, 0.6]} color={C.amber} intensity={2.5} distance={3} decay={2} /> : null}
          </group>
        );
      }) : null}
      <Label text="12 drafts" h={0.14} position={[0, FLOOR_Y + 1.75, Z.drafts - 3]} face={face} style={{font: 'mono', weight: 500, color: '#cfd8ff'}} opacity={1 - run} />
    </Stage>
  );
};
