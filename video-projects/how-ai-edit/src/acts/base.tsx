// What every 3D act shares: the finish, one canvas, the sky, the floor, the air and the camera.
import React from 'react';
import {AbsoluteFill} from 'remotion';
import * as THREE from 'three';
import {ThreeCanvas} from '../kit/three-canvas';
import {Finish} from '../kit/finish';
import {Air, Aim, C, Floor, Sky} from '../world/kit';

export type Shot = {cam: THREE.Vector3; look: THREE.Vector3; fov?: number; roll?: number};
export const v3 = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
// the direction labels face: back toward the lens, so they read square to the screen
export const faceOf = (s: Shot) => s.cam.clone().sub(s.look).normalize();

export const Stage: React.FC<{fr: number; shot: Shot; fog?: number; bloom?: number; lanes?: boolean; exposure?: number; overlay?: React.ReactNode; children: React.ReactNode}> = ({fr, shot, fog, bloom = 0.85, lanes = true, exposure = 1.05, overlay, children}) => (
  <AbsoluteFill style={{background: C.night}}>
    <Finish fr={fr} bloom={bloom}>
      <ThreeCanvas width={1080} height={1920} camera={{position: shot.cam.toArray(), fov: shot.fov ?? 38, far: 1200}} gl={{toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: exposure}}>
        <Aim pos={shot.cam} look={shot.look} fov={shot.fov ?? 38} roll={shot.roll} />
        <Sky fog={fog} />
        <Floor lanes={lanes} />
        <Air fr={fr} at={[shot.look.x, shot.look.y, shot.look.z]} cam={shot.cam} look={shot.look} />
        <ambientLight intensity={0.06} />
        <directionalLight position={[-3, 4, -4]} color={C.amber} intensity={2.4} />
        <directionalLight position={[4, 1, 3]} color="#7088ff" intensity={0.35} />
        {children}
      </ThreeCanvas>
    </Finish>
    {overlay}
  </AbsoluteFill>
);

// smoothstep and helpers in act-local seconds
export const sm = (a: number, b: number, t: number) => { const x = Math.min(1, Math.max(0, (t - a) / (b - a))); return x * x * (3 - 2 * x); };
export const mixV = (a: THREE.Vector3, b: THREE.Vector3, k: number) => a.clone().lerp(b, k);
