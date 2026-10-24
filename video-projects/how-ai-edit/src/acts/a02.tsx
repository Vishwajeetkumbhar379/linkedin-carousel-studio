// Line 2: "No editing app touched it. // So let's rewind and see what did."
// The editing app rises out of the phone still sealed in its wrap; on "rewind" the camera drops onto
// the progress bar, which runs back to 0:00 and becomes the rail, the 39 clips lying beside it.
import React from 'react';
import * as THREE from 'three';
import {cue} from '../lib';
import {Caption} from '../styleframes/caption';
import {Phone3D} from '../kit/phone';
import {paintRoll, useImgs} from '../styleframes/roll';
import {tile} from '../styleframes/data';
import {Label, useTextures} from '../world/kit';
import {Cart, RAIL, RAIL_Y, Rail} from '../world/rail';
import {ClipLane, SealedApp} from '../world/props';
import {AudioTerrain} from '../world/audio';
import {Shot, Stage, faceOf, mixV, sm, v3} from './base';

const PHONE = {pos: v3(0.1, -1.36, 0.55), quat: new THREE.Quaternion().setFromEuler(new THREE.Euler(-1.05, 0, 0.1)), scale: 1.4};
const CLIP_PATHS = Array.from({length: 39}, (_, i) => tile(i));

export const A02: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const imgs = useImgs();
  const clips = useTextures(CLIP_PATHS);
  const rw = cue("rewind"), see = cue("see what did");
  const up = sm(cue("No editing app"), cue("No editing app") + 1.0, t); // the app rises
  const dive = sm(rw - 0.1, see + 0.2, t); // the camera drops to the rail
  const back = sm(rw, see + 0.6, t); // the playhead runs back to 0:00
  const A: Shot = {cam: v3(0.05, 0.35, 6.4), look: v3(0, -0.15, 0)};
  const B: Shot = {cam: v3(0.3, RAIL_Y + 1.35, RAIL.start + 3.6), look: v3(0.1, RAIL_Y + 0.1, RAIL.start - 9)};
  const k = dive * dive * (3 - 2 * dive);
  const shot: Shot = {cam: mixV(A.cam, B.cam, k), look: mixV(A.look, B.look, k), roll: Math.sin(Math.PI * k) * -0.12};
  const cartZ = RAIL.start - (1 - back) * 26;
  const secs = Math.max(0, (RAIL.start - cartZ) / 26 * 11.1);
  const words = t < rw - 0.15 ? {w: ['No', 'editing', 'app'], pill: 0} : {w: ["let's", 'rewind'], pill: 1};
  return (
    <Stage fr={fr} shot={shot} overlay={<Caption words={words.w} pill={words.pill} top={t < rw - 0.15 ? 900 : 1060} />}>
      <Rail played={cartZ} />
      {clips ? <ClipLane tex={clips} /> : null}
      <AudioTerrain />
      <Cart z={cartZ} time={`0:${secs.toFixed(1).padStart(4, '0')}`} face={faceOf(shot)} scale={0.65} />
      {imgs ? (
        <group position={PHONE.pos.clone().add(v3(0, k * 4.5, -k * 2))} quaternion={PHONE.quat} scale={PHONE.scale * (1 - 0.4 * k)}>
          <Phone3D assets={null} state={{time: '9:41'}} res={3} light={1.3} glare={0.05} paint={(g) => paintRoll(g, imgs, () => 1, () => 0)} />
        </group>
      ) : null}
      {/* the sealed app, rising from the phone and turning slowly; it leaves frame as we dive */}
      <group position={[0.0, -0.9 + up * 1.55 + k * 4, 1.2 + up * 0.3]} rotation={[0.12 - up * 0.08, -0.62 + up * 0.4 + (t - rw) * 0.05, 0.04]} scale={0.62 * up + 0.001}>
        <SealedApp />
        <pointLight position={[0.6, 0.8, 1.4]} color="#ffe6cc" intensity={2.2} distance={4} decay={2} />
      </group>
      {k > 0.6 ? <Label text="0:00" h={0.09} position={[0.32, RAIL_Y + 0.02, RAIL.start + 0.05]} rotation={[-Math.PI / 2, 0, 0]} style={{font: 'mono', weight: 500, color: '#cfd8ff'}} opacity={sm(0.6, 1, k) * 0.9} /> : null}
    </Stage>
  );
};
