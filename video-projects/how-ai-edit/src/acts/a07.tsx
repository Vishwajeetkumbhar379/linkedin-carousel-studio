// Line 7: "Every caption, / every sticker / is a tiny web page, / photographed / 30 times a second."
// Push into this film's own caption until browser chrome appears around it: it is a page. Then
// thirty shutter clicks stack thirty photographs of it behind, one per frame of its pop-in:
// one second of video.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {cue} from '../lib';
import {C, FLOOR_Y, Label} from '../world/kit';
import {Cart, Rail, Z} from '../world/rail';
import {PAGE, pageMat} from '../world/browser';
import {Shot, Stage, faceOf, mixV, sm, v3} from './base';

const AT = v3(-0.3, FLOOR_Y + 1.9, Z.render);

export const A07: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const t0 = cue("Every caption"), page = cue("tiny webpage"), photo = cue("photographed"), sec = cue("30 times a second") + 0.6;
  const mats = useMemo(() => Array.from({length: 30}, (_, i) => pageMat(i / 29, true, 0.7 + 0.3 * (i / 29))), []);
  const front = useMemo(() => pageMat(1, true), []);
  const chrome = sm(page - 0.3, page + 0.2, t); // the browser appears around the caption
  const shots = Math.floor(30 * sm(photo, sec + 0.4, t)); // shutter clicks: how many photographs exist
  const flash = shots > 0 && shots < 30 ? 1 - ((30 * sm(photo, sec + 0.4, t)) % 1) : 0;
  // close enough that the caption fills the frame without spilling off it, then back until the whole
  // page and its browser bar are in frame as the voice says "web page", then wide for the stack
  const close: Shot = {cam: AT.clone().add(v3(0.03, 0.06, 1.9)), look: AT.clone().add(v3(0, 0.03, 0))};
  const page2: Shot = {cam: AT.clone().add(v3(0, 0.02, 2.8)), look: AT.clone()};
  const wide: Shot = {cam: AT.clone().add(v3(-1.7, -0.1, 3.1)), look: AT.clone().add(v3(0.55, -0.5, -1.2))};
  const back = sm(t0 + 0.3, page + 0.4, t), k = sm(photo - 0.2, sec, t);
  const mid = {cam: mixV(close.cam, page2.cam, back), look: mixV(close.look, page2.look, back)};
  const shot: Shot = {cam: mixV(mid.cam, wide.cam, k), look: mixV(mid.look, wide.look, k)};
  const face = faceOf(shot);
  return (
    <Stage fr={fr} shot={shot}>
      <Rail played={Z.render + 2} />
      <Cart z={Z.render + 2} face={face} scale={0.8} />
      <group position={AT} rotation={[0, -0.12, 0]}>
        {/* the photographs, stacking back from the page, oldest furthest */}
        {Array.from({length: shots}, (_, i) => (
          <mesh key={i} material={mats[i]} position={[0.045 * (29 - i), 0.012 * (29 - i), -0.06 - (29 - i) * 0.09]}>
            <planeGeometry args={[PAGE.w, PAGE.h]} />
          </mesh>
        ))}
        {/* the page itself, in front; its chrome fades in when we learn it's a web page */}
        <mesh material={front} position={[0, 0, 0.02]} scale={[1, 1, 1]}>
          <planeGeometry args={[PAGE.w, PAGE.h]} />
        </mesh>
        <mesh position={[0, 0, 0.018]}><planeGeometry args={[PAGE.w + 0.02, PAGE.h + 0.02]} /><meshBasicMaterial color={new THREE.Color('#9fb2ff')} transparent opacity={0.35 * chrome} toneMapped={false} /></mesh>
        {flash > 0 ? <pointLight position={[0.3, 0.3, 0.8]} color="#ffffff" intensity={6 * flash} distance={3} decay={2} /> : null}
        {k > 0.3 ? <Label text="30 photographs = 1 second" h={0.1} position={[0.05, PAGE.h / 2 + 0.16, 0.1]} face={face} style={{font: 'mono', weight: 500, color: C.amberHot, bg: 'rgba(20,12,6,0.8)', pad: 0.35}} opacity={sm(0.3, 0.7, k)} /> : null}
      </group>
    </Stage>
  );
};
