// Line 1: "Before you saw my face, / this video was *39* clips / on my phone."
// He talks to camera (until he films it: the stand-in still, full frame). On "39" the frame freezes,
// the camera pulls back to show it hanging over the timeline, and it cracks from his mouth into 39
// shards that fly into the phone's camera roll, each one landing as the real clip it came from.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {cue, ACTS} from '../lib';
import {Caption} from '../styleframes/caption';
import {Phone3D} from '../kit/phone';
import {FLIGHT, N, SHARDS, flight, A as ASPECT} from '../styleframes/data';
import {paintRoll, useImgs} from '../styleframes/roll';
import {Pose, Shards3D} from '../styleframes/shards3d';
import {Cracks, Halo, look} from '../styleframes/luminous';
import {Rail} from '../world/rail';
import {RAIL} from '../world/rail';
import {Shot, Stage, mixV, sm, v3} from './base';

export const PANE: Pose = {pos: v3(-0.08, 1.12, -0.7), quat: new THREE.Quaternion().setFromEuler(new THREE.Euler(0.02, 0.16, -0.03)), scale: 1.16};
export const PHONE1: Pose = {pos: v3(0.1, -1.36, 0.55), quat: new THREE.Quaternion().setFromEuler(new THREE.Euler(-1.05, 0, 0.1)), scale: 1.4};

export const A01: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const imgs = useImgs();
  const freeze = cue("39") - 0.06;
  const p = Math.min(1, Math.max(0, (t - freeze) / (ACTS.l01[1] - freeze - 0.05)));
  // full frame on his face until the freeze, then pull back to the world
  const near = useMemo(() => {
    const n = new THREE.Vector3(0, 0, 1).applyQuaternion(PANE.quat), d = (PANE.scale * ASPECT) / (2 * Math.tan((38 / 2) * Math.PI / 180));
    return {cam: PANE.pos.clone().add(n.multiplyScalar(d * 0.995)), look: PANE.pos.clone()};
  }, []);
  const wide: Shot = {cam: v3(0.05 - p * 0.15, 0.42 - p * 0.1, 6.5 - p * 0.35), look: v3(0, -0.05 - p * 0.05, 0)};
  const k = sm(freeze, freeze + 0.9, t);
  const shot: Shot = {cam: mixV(near.cam, wide.cam, k), look: mixV(near.look, wide.look, k)};
  const landed = (i: number) => (flight(SHARDS[i], p) >= 0.985 ? 1 : 0);
  const flash = (i: number) => { const s = SHARDS[i], u = (p - s.leave - FLIGHT * 0.985) / 0.1; return u >= 0 && u <= 1 ? 1 - u : 0; };
  const inAir = SHARDS.filter((s) => { const f = flight(s, p); return f > 0 && f < 0.985; }).length;
  const words = t < cue("this video") - 0.1 ? {w: ['Before', 'you', 'saw', 'me'], p: -1} : t < freeze ? {w: ['this', 'video', 'was'], p: -1} : {w: ['39', 'clips'], p: 0};
  return (
    <Stage fr={fr} shot={shot} overlay={<Caption words={words.w} pill={words.p} top={k < 0.5 ? 1140 : 1010} />}>
      <Rail played={RAIL.start} glow={0.6} />
      <pointLight position={[PANE.pos.x, PANE.pos.y, PANE.pos.z + 0.9]} color="#ffe7cf" intensity={2.2 * (1 - inAir / N) * (1 - p * 0.6)} distance={6} decay={2} />
      {imgs ? (
        <>
          <Cracks p={p} pane={PANE} />
          <Halo pane={PANE} k={k * (1 - inAir / N) * (1 - p * 0.5)} />
          <Shards3D p={p} pane={PANE} phone={PHONE1} face={imgs.face} clips={imgs.clips} look={look} />
          <group position={PHONE1.pos} quaternion={PHONE1.quat} scale={PHONE1.scale}>
            <Phone3D assets={null} state={{time: '9:41'}} res={3} light={1.3} glare={0.05} paint={(g) => paintRoll(g, imgs, landed, flash)} />
          </group>
        </>
      ) : null}
    </Stage>
  );
};
