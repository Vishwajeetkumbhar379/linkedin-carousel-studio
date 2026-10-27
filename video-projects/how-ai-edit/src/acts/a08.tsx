// Line 8: "Let's *slow down* time. // At one frame a second, / a one-minute reel / takes *30 minutes* to watch."
// <slow> The film itself drops to one frame a second for three ticks, a counter reading 1, 2, 3 of
// 1,800. Then the camera runs along a wall of 1,800 photographs (the first minute of the posted
// Week 1 reel, every frame) while a clock runs to 30:00.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {cue} from '../lib';
import {C, FLOOR_Y, Label, useTextures} from '../world/kit';
import {Cart, Rail, Z} from '../world/rail';
import {Shot, Stage, faceOf, mixV, sm, v3} from './base';

// atlas: 60 x 30 frames of 24 x 43 px (1440 x 1290), ffmpeg tile of the reel's first 60 s
const COLS = 60, ROWS = 30, WALL = {x: 1.15, y0: FLOOR_Y + 0.05, z0: Z.render - 4, w: 20};

export const A08: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const tex = useTextures(['wall/atlas.jpg']);
  const t0 = cue("Let's slow down"), at = cue("At one frame"), mins = cue("30 minutes");
  // <slow>: for three ticks after "time", the picture only updates once a second
  const slowFrom = cue("down time") + 0.35, slowTo = slowFrom + 3;
  const tq = t > slowFrom && t < slowTo ? slowFrom + Math.floor(t - slowFrom) : t;
  const tick = t > slowFrom && t < slowTo ? Math.floor(t - slowFrom) + 1 : 0;
  const run = sm(Math.max(slowTo, at), mins + 0.6, tq);
  const H = (WALL.w / COLS) * ROWS * (43 / 24); // keep each frame's shape
  const start: Shot = {cam: v3(-0.3, FLOOR_Y + 1.3, WALL.z0 + 2.0), look: v3(WALL.x, FLOOR_Y + 1.6, WALL.z0 - 3)};
  const end: Shot = {cam: v3(-0.5, FLOOR_Y + 1.8, WALL.z0 - 13), look: v3(WALL.x, FLOOR_Y + 2.2, WALL.z0 - 22)};
  const shot: Shot = {cam: mixV(start.cam, end.cam, run), look: mixV(start.look, end.look, run), roll: 0.04 * Math.sin(run * Math.PI)};
  const face = faceOf(shot);
  const minutes = run * 30, clock = `${String(Math.floor(minutes)).padStart(2, '0')}:${String(Math.floor((minutes % 1) * 60)).padStart(2, '0')}`;
  const grid = useGrid();
  const wallMat = useMemo(() => tex ? new THREE.MeshBasicMaterial({map: tex[0], toneMapped: false, color: new THREE.Color(0.7, 0.7, 0.72)}) : null, [tex]);
  return (
    <Stage fr={tq * 30} shot={shot}>
      <Rail played={WALL.z0 + 3} />
      <Cart z={WALL.z0 + 3 - run * 14} face={face} scale={0.8} />
      {wallMat ? (
        <group position={[WALL.x, WALL.y0 + H / 2, WALL.z0 - WALL.w / 2]} rotation={[0, -Math.PI / 2, 0]}>
          <mesh material={wallMat}><planeGeometry args={[WALL.w, H]} /></mesh>
          {/* a hairline grid so the frames read as 1,800 separate photographs */}
          <mesh position={[0, 0, 0.002]}>
            <planeGeometry args={[WALL.w, H]} />
            <meshBasicMaterial transparent depthWrite={false} toneMapped={false} map={grid} />
          </mesh>
        </group>
      ) : null}
      <Label text={tick ? `frame ${tick} of 1,800` : `${Math.max(1, Math.round(run * 1800)).toLocaleString('en-GB')} of 1,800`} h={0.1} position={[-0.45, FLOOR_Y + 2.15, shot.look.z + 2.4]} face={face} style={{font: 'mono', weight: 500, color: '#cfd8ff', bg: 'rgba(8,10,20,0.75)', pad: 0.35}} />
      {run > 0.02 ? <Label text={clock} h={0.42} position={[-0.25, FLOOR_Y + 2.5, shot.look.z + 1.6]} face={face} style={{font: 'mono', weight: 500, color: C.amberHot}} glow={1.3} /> : null}
    </Stage>
  );
};

const useGrid = () => useMemo(() => {
  const c = document.createElement('canvas'); c.width = 1440; c.height = 1290;
  const g = c.getContext('2d')!;
  g.strokeStyle = 'rgba(6,8,15,0.95)'; g.lineWidth = 3;
  for (let i = 0; i <= COLS; i++) { g.beginPath(); g.moveTo(i * 24, 0); g.lineTo(i * 24, 1290); g.stroke(); }
  for (let j = 0; j <= ROWS; j++) { g.beginPath(); g.moveTo(0, j * 43); g.lineTo(1440, j * 43); g.stroke(); }
  const t = new THREE.CanvasTexture(c); t.anisotropy = 8; return t;
}, []);
