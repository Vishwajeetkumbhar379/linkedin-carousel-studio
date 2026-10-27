// Line 6: "Then it cut *me* out, / every single frame, / so words can sit *behind* me."
// His real frames fan out like a deck, each with its own cut-out traced in light (the RVM matte of
// that very frame, so the outline moves with him). The deck squares up and swings apart into three
// panes: the room, a title, and him in front, so the words sit behind him.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {cue} from '../lib';
import {C, FLOOR_Y, Label, useTextures} from '../world/kit';
import {Cart, Rail} from '../world/rail';
import {Shot, Stage, faceOf, mixV, sm, v3} from './base';

const N = 24;
const PATHS = [...Array.from({length: N}, (_, i) => String(i + 1).padStart(2, '0')).flatMap((k) => [`rish/f${k}.jpg`, `rish/o${k}.png`, `rish/m${k}.png`]), 'rish/bg12.jpg'];
const DECK = v3(-0.2, FLOOR_Y + 1.35, -36);
const CW = 0.62, CH = CW * (16 / 9);

export const A06: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const tex = useTextures(PATHS);
  const t0 = cue("Then it cut me"), every = cue("every single frame"), so = cue("and the caption sits"), behind = cue("behind me");
  const fan = sm(t0 + 0.2, every + 0.4, t); // the deck opens
  const square = sm(so - 0.3, so + 0.2, t); // and squares up
  const panes = sm(so + 0.1, behind + 0.1, t); // then swings apart into three panes
  const riffle = (every - t0) > 0 ? Math.floor(Math.max(0, (t - every) * 24)) : 0;
  const mats = useMemo(() => {
    if (!tex) return null;
    const room = tex[tex.length - 1], all = tex.slice(0, -1); // the room without him (inpainted behind his matte)
    const [f, o, m] = [0, 1, 2].map((k) => all.filter((_, i) => i % 3 === k));
    o.forEach((x) => { x.colorSpace = THREE.NoColorSpace; }); m.forEach((x) => { x.colorSpace = THREE.NoColorSpace; });
    return {
      frame: f.map((x) => new THREE.MeshBasicMaterial({map: x, color: new THREE.Color(0.8, 0.8, 0.8), toneMapped: false, side: THREE.DoubleSide})),
      line: o.map((x) => new THREE.MeshBasicMaterial({color: new THREE.Color(C.amberHot).multiplyScalar(1.8), alphaMap: x, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false})),
      room: new THREE.MeshBasicMaterial({map: room, toneMapped: false, color: new THREE.Color(0.75, 0.75, 0.75)}),
      cut: m.map((x, i) => new THREE.MeshBasicMaterial({map: f[i], alphaMap: x, transparent: true, toneMapped: false, color: new THREE.Color(0.92, 0.92, 0.92)})),
    };
  }, [tex]);
  const deckShot: Shot = {cam: v3(0.15, FLOOR_Y + 1.65, -31.6), look: v3(-0.2, FLOOR_Y + 1.25, -36)};
  const paneShot: Shot = {cam: v3(1.75, FLOOR_Y + 1.55, -32.6), look: v3(-0.25, FLOOR_Y + 1.3, -36.4)};
  const shot: Shot = {cam: mixV(deckShot.cam, paneShot.cam, panes), look: mixV(deckShot.look, paneShot.look, panes)};
  const face = faceOf(shot);
  const hero = 11; // the frame that becomes the three panes
  return (
    <Stage fr={fr} shot={shot}>
      <Rail played={-34} />
      <Cart z={-34} face={face} scale={0.8} />
      {mats ? (
        <group position={DECK}>
          {/* the deck: a fan of his frames, pivoting at the bottom like a hand of cards */}
          {panes < 0.02 ? Array.from({length: N}, (_, i) => {
            const u = i / (N - 1) - 0.5, a = -u * 1.9 * fan * (1 - square);
            const lift = i === (riffle % N) && fan > 0.9 && square < 0.1 ? 0.06 : 0;
            return (
              <group key={i} position={[0, -CH * 0.55, i * 0.008]} rotation={[0, 0, a]}>
                <group position={[0, CH * 0.55 + lift, 0]} rotation={[0, u * 0.25 * fan, 0]}>
                  <mesh material={mats.frame[i]}><planeGeometry args={[CW, CH]} /></mesh>
                  <mesh material={mats.line[i]} position={[0, 0, 0.002]}><planeGeometry args={[CW, CH]} /></mesh>
                  <mesh position={[0, 0, -0.003]}><planeGeometry args={[CW + 0.02, CH + 0.02]} /><meshBasicMaterial color="#0b0d14" /></mesh>
                </group>
              </group>
            );
          }) : (
            // three panes: the room at the back, the title in the middle, him in front
            <group>
              <mesh material={mats.room} position={[0, 0, -0.9 * panes]}><planeGeometry args={[CW * 1.6, CH * 1.6]} /></mesh>
              <Label text="WEEK 1" h={0.42 * (0.6 + 0.4 * panes)} position={[0, 0.55, -0.45 * panes]} style={{weight: 800, color: C.amberHot}} glow={1.2} />
              <mesh material={mats.cut[hero]} position={[0, 0, 0]}><planeGeometry args={[CW * 1.6, CH * 1.6]} /></mesh>
              <mesh material={mats.line[hero]} position={[0, 0, 0.003]}><planeGeometry args={[CW * 1.6, CH * 1.6]} /></mesh>
              {/* thin edges so each pane reads as a layer */}
              {[-0.9, 0].map((z, i) => (
                <lineSegments key={i} position={[0, 0, z * panes]} geometry={new THREE.EdgesGeometry(new THREE.PlaneGeometry(CW * 1.6, CH * 1.6))}>
                  <lineBasicMaterial color="#9fb2ff" transparent opacity={0.5} toneMapped={false} />
                </lineSegments>
              ))}
            </group>
          )}
          <pointLight position={[0, 0.4, 1.0]} color="#ffe2c4" intensity={1.5} distance={4} decay={2} />
        </group>
      ) : null}
      {mats && panes < 0.02 ? <Label text={`frame ${(riffle % N) * 3 + 1} of 72`} h={0.08} position={[DECK.x, DECK.y + CH * 0.75, DECK.z + 0.3]} face={face} style={{font: 'mono', weight: 500, color: '#cfd8ff', bg: 'rgba(8,10,20,0.7)', pad: 0.35}} opacity={fan} /> : null}
    </Stage>
  );
};
