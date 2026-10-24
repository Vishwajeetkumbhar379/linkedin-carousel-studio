// Objects that appear in more than one act: the 39 clips on their lane, the sealed editing app.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {random} from 'remotion';
import {CLIP_SECONDS} from '../styleframes/data';
import {C, FLOOR_Y, canvasTex} from './kit';
import {RAIL} from './rail';

export const CLIP_LANE = {x: -0.78, width: 0.62, perSec: 0.05, gap: 0.05};
// z range of each clip on the video lane, end to end from 0:00
export const CLIP_SPANS = (() => {
  let z = RAIL.start - 0.3;
  return CLIP_SECONDS.map((s) => { const len = 0.25 + s * CLIP_LANE.perSec, a = z; z -= len + CLIP_LANE.gap; return [a, a - len] as [number, number]; });
})();

// The 39 raw clips lying end to end on the video lane, each a filmstrip of its own first frame.
export const ClipLane: React.FC<{tex: THREE.Texture[]; reveal?: number; glow?: number}> = ({tex, reveal = 1, glow = 1}) => {
  const mats = useMemo(() => tex.map((t, i) => {
    const m = t.clone(); m.needsUpdate = true; m.wrapS = m.wrapT = THREE.RepeatWrapping;
    const [a, b] = CLIP_SPANS[i], frames = Math.max(1, Math.round((a - b) / (CLIP_LANE.width * 0.5625)));
    m.repeat.set(1, frames); // portrait frames laid flat, one after another along the clip
    m.center.set(0.5, 0.5);
    return new THREE.MeshBasicMaterial({map: m, color: new THREE.Color(0.62, 0.6, 0.6).multiplyScalar(glow), toneMapped: false});
  }), [tex, glow]);
  const side = useMemo(() => new THREE.MeshPhysicalMaterial({color: '#1b2030', roughness: 0.25, clearcoat: 1, emissive: C.laneDim, emissiveIntensity: 0.6}), []);
  return (
    <group>
      {CLIP_SPANS.map(([a, b], i) => {
        const len = a - b, on = Math.min(1, Math.max(0, reveal * 40 - i)); // they land one after another
        if (on <= 0) return null;
        return (
          <group key={i} position={[CLIP_LANE.x, FLOOR_Y + 0.04 + (1 - on) * 0.6, (a + b) / 2]}>
            <mesh material={side}><boxGeometry args={[CLIP_LANE.width, 0.05, len]} /></mesh>
            <mesh position={[0, 0.026, 0]} rotation={[-Math.PI / 2, 0, 0]} material={mats[i]}><planeGeometry args={[CLIP_LANE.width * 0.94, len * 0.97]} /></mesh>
          </group>
        );
      })}
    </group>
  );
};

const squircle = (s: number, r: number) => {
  const sh = new THREE.Shape(), h = s / 2;
  sh.moveTo(-h + r, -h); sh.lineTo(h - r, -h); sh.quadraticCurveTo(h, -h, h, -h + r); sh.lineTo(h, h - r); sh.quadraticCurveTo(h, h, h - r, h);
  sh.lineTo(-h + r, h); sh.quadraticCurveTo(-h, h, -h, h - r); sh.lineTo(-h, -h + r); sh.quadraticCurveTo(-h, -h, -h + r, -h);
  return sh;
};

// A generic video-editing app icon (no real logo), still sealed in shrink-wrap with its tear strip.
export const SealedApp: React.FC = () => {
  const {body, face, wrap, crinkle, faceGeo, strip, gloss} = useMemo(() => {
    const body = new THREE.ExtrudeGeometry(squircle(1, 0.24), {depth: 0.14, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 5, curveSegments: 24});
    body.translate(0, 0, -0.14);
    const faceGeo = new THREE.ShapeGeometry(squircle(0.995, 0.235), 24);
    const uv = faceGeo.attributes.uv, p = faceGeo.attributes.position;
    for (let i = 0; i < p.count; i++) uv.setXY(i, p.getX(i) + 0.5, p.getY(i) + 0.5);
    // the icon: a dark gradient tile, a film frame and a play triangle, a timeline bar
    const face = canvasTex(512, 512, (g) => {
      const gr = g.createLinearGradient(0, 0, 512, 512); gr.addColorStop(0, '#2b3350'); gr.addColorStop(1, '#0d1020');
      g.fillStyle = gr; g.fillRect(0, 0, 512, 512);
      g.strokeStyle = '#e9edf8'; g.lineWidth = 22; g.lineJoin = 'round';
      g.beginPath(); g.roundRect(120, 132, 272, 196, 26); g.stroke();
      for (let i = 0; i < 5; i++) { g.fillStyle = '#e9edf8'; g.fillRect(146 + i * 52, 106, 26, 18); g.fillRect(146 + i * 52, 336, 26, 18); }
      g.fillStyle = '#e9edf8'; g.beginPath(); g.moveTo(228, 186); g.lineTo(306, 230); g.lineTo(228, 274); g.closePath(); g.fill();
      g.fillStyle = 'rgba(233,237,248,0.35)'; g.beginPath(); g.roundRect(120, 392, 272, 16, 8); g.fill();
      g.fillStyle = '#9fb2ff'; g.beginPath(); g.roundRect(120, 392, 110, 16, 8); g.fill();
    });
    // crinkled plastic: random folds as a bump texture
    const crinkle = canvasTex(512, 512, (g) => {
      g.fillStyle = '#808080'; g.fillRect(0, 0, 512, 512);
      for (let i = 0; i < 140; i++) {
        const x = random(`kx${i}`) * 512, y = random(`ky${i}`) * 512, a = random(`ka${i}`) * Math.PI, l = 30 + random(`kl${i}`) * 140;
        g.strokeStyle = random(`kc${i}`) < 0.5 ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.45)'; g.lineWidth = 1 + random(`kw${i}`) * 3;
        g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
      }
    }, false);
    const wrap = new THREE.ExtrudeGeometry(squircle(1.1, 0.3), {depth: 0.24, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.04, bevelSegments: 4, curveSegments: 20});
    wrap.translate(0, 0, -0.17);
    const strip = new THREE.BoxGeometry(1.16, 0.022, 0.008);
    // gloss: the bright creases light catches on stretched plastic
    const gloss = canvasTex(512, 512, (g) => {
      g.clearRect(0, 0, 512, 512);
      const streak = (x0: number, y0: number, x1: number, y1: number, w: number, a: number) => {
        const gr = g.createLinearGradient(x0, y0, x1, y1); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.5, `rgba(255,255,255,${a})`); gr.addColorStop(1, 'rgba(255,255,255,0)');
        g.strokeStyle = gr; g.lineWidth = w; g.lineCap = 'round'; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke();
      };
      streak(40, 300, 300, 40, 26, 0.55); streak(120, 470, 470, 120, 10, 0.35); streak(330, 500, 500, 330, 18, 0.25);
      for (let i = 0; i < 40; i++) { const x = random(`gx${i}`) * 512, y = random(`gy${i}`) * 512, a = random(`ga${i}`) * Math.PI, l = 20 + random(`gl${i}`) * 70; streak(x, y, x + Math.cos(a) * l, y + Math.sin(a) * l, 2, 0.5); }
    });
    return {body, face, wrap, crinkle, faceGeo, strip, gloss};
  }, []);
  return (
    <group>
      <mesh geometry={body}><meshPhysicalMaterial color="#1a1f33" roughness={0.3} metalness={0.2} clearcoat={1} /></mesh>
      <mesh geometry={faceGeo} position={[0, 0, 0.031]}><meshPhysicalMaterial map={face} roughness={0.25} clearcoat={1} emissive="#ffffff" emissiveMap={face} emissiveIntensity={0.35} /></mesh>
      <mesh geometry={wrap} renderOrder={2}>
        <meshPhysicalMaterial color="#e8eef8" transparent opacity={0.16} roughness={0.12} metalness={0} clearcoat={1} clearcoatRoughness={0.05} bumpMap={crinkle} bumpScale={4} depthWrite={false} specularIntensity={1} />
      </mesh>
      <mesh geometry={faceGeo} position={[0, 0, 0.125]} scale={1.08} renderOrder={4}><meshBasicMaterial map={gloss} transparent opacity={0.85} blending={THREE.AdditiveBlending} depthWrite={false} toneMapped={false} /></mesh>
      {/* the tear strip across the front, with its tab */}
      <mesh geometry={strip} position={[0, 0.4, 0.13]} renderOrder={3}><meshPhysicalMaterial color="#f2f0ea" roughness={0.4} clearcoat={0.5} /></mesh>
      <mesh position={[0.6, 0.43, 0.135]} rotation={[0, 0, 0.5]} renderOrder={3}><boxGeometry args={[0.09, 0.04, 0.006]} /><meshPhysicalMaterial color="#f2f0ea" roughness={0.4} /></mesh>
    </group>
  );
};
