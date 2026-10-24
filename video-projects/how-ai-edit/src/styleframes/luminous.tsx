// Style frame A, luminous 3D: the reel's own timeline as a dark world. His frozen frame hangs over
// it and cracks; the shards are lit screens that fly down into the phone's camera roll.
import React, {useMemo} from 'react';
import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {ThreeCanvas} from '../kit/three-canvas';
import {Finish} from '../kit/finish';
import {Phone3D} from '../kit/phone';
import {A, FLIGHT, N, SHARDS, cracked, crackReach, flight} from './data';
import {paintRoll, useImgs} from './roll';
import {Pose, Shards3D, ShardLook} from './shards3d';
import {Caption} from './caption';

const NIGHT = '#06080f', HORIZON = '#1c1519';

const canvasTex = (w: number, h: number, draw: (g: CanvasRenderingContext2D) => void) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d')!);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
};

// Reflections come from a small dark room with one amber strip (the lamp) and a cool strip opposite.
const World: React.FC = () => {
  const {gl, scene} = useThree();
  useMemo(() => {
    const room = new THREE.Scene();
    room.add(new THREE.Mesh(new THREE.SphereGeometry(10, 32, 16), new THREE.MeshBasicMaterial({color: '#05060a', side: THREE.BackSide})));
    const strip = (color: string, x: number, y: number, z: number, w: number, h: number, i: number) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({color: new THREE.Color(color).multiplyScalar(i), side: THREE.DoubleSide}));
      m.position.set(x, y, z); m.lookAt(0, 0, 0); room.add(m);
    };
    strip('#E7A15A', -6, 2, -3, 2.5, 7, 3.2);
    strip('#5f78ff', 6, 3, 2, 1.5, 6, 1.1);
    strip('#ffffff', 0, 8, 4, 6, 1, 0.6);
    const pm = new THREE.PMREMGenerator(gl);
    scene.environment = pm.fromScene(room, 0.03).texture;
    // the sky: night overhead, a low ember of dusk where the timeline meets the horizon (~40% down)
    scene.background = canvasTex(8, 1024, (g) => {
      const gr = g.createLinearGradient(0, 0, 0, 1024);
      gr.addColorStop(0, '#03050a'); gr.addColorStop(0.28, '#070a14'); gr.addColorStop(0.37, '#1a1420'); gr.addColorStop(0.4, '#3a2522'); gr.addColorStop(0.43, HORIZON); gr.addColorStop(1, HORIZON);
      g.fillStyle = gr; g.fillRect(0, 0, 8, 1024);
    });
    scene.fog = new THREE.FogExp2(HORIZON, 0.05);
  }, [gl, scene]);
  return null;
};

// The floor is the timeline: dark glass lanes running to the horizon, timecode ticks across them.
// Far down the lanes lie clips, as on an editor's timeline: the world the next line flies into.
const Blocks: React.FC = () => {
  const mesh = useMemo(() => {
    const geo = new THREE.BoxGeometry(1, 0.06, 1);
    const mat = new THREE.MeshBasicMaterial({color: '#ffffff'}); // a dim glow per clip, taken by the fog with distance
    const n = 90, im = new THREE.InstancedMesh(geo, mat, n), o = new THREE.Object3D(), c = new THREE.Color();
    for (let i = 0; i < n; i++) {
      const lane = Math.floor(random(`bl${i}`) * 8), z = -9 - random(`bz${i}`) * 70, len = 0.6 + random(`bw${i}`) * 2.4;
      o.position.set(-3.92 + lane * 1.12 + 0.56, -2.52, z); o.scale.set(0.86, 1, len); o.updateMatrix(); im.setMatrixAt(i, o.matrix);
      const warm = random(`bc${i}`) < 0.35;
      im.setColorAt(i, c.set(warm ? '#5a3418' : '#1c2448'));
    }
    return im;
  }, []);
  return <primitive object={mesh} />;
};

const Timeline: React.FC = () => {
  const {lanes, ticks, fade} = useMemo(() => ({
    fade: (() => { const t = canvasTex(4, 256, (g) => { const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, '#000'); gr.addColorStop(0.86, '#1a1a1a'); gr.addColorStop(0.97, '#fff'); gr.addColorStop(1, '#fff'); g.fillStyle = gr; g.fillRect(0, 0, 4, 256); }); t.colorSpace = THREE.NoColorSpace; return t; })(),
    lanes: canvasTex(1024, 1024, (g) => {
      g.fillStyle = '#000'; g.fillRect(0, 0, 1024, 1024);
      for (let i = 0; i <= 8; i++) { const x = 64 + i * 112; g.fillStyle = i % 4 === 0 ? 'rgba(120,140,220,0.55)' : 'rgba(80,100,180,0.28)'; g.fillRect(x - 1.5, 0, 3, 1024); }
    }),
    ticks: canvasTex(64, 1024, (g) => {
      g.fillStyle = '#000'; g.fillRect(0, 0, 64, 1024);
      for (let y = 0; y < 1024; y += 64) { g.fillStyle = 'rgba(140,160,230,0.5)'; g.fillRect(0, y, 64, 2); }
    }),
  }), []);
  lanes.wrapS = lanes.wrapT = THREE.RepeatWrapping; lanes.repeat.set(1, 24);
  ticks.wrapS = ticks.wrapT = THREE.RepeatWrapping; ticks.repeat.set(46, 48);
  return (
    <group position={[0, -2.55, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, -150]}>
        <planeGeometry args={[600, 320]} />
        <meshPhysicalMaterial color="#0a0c15" roughness={0.3} metalness={0.0} clearcoat={0.5} clearcoatRoughness={0.3} />
      </mesh>
      {/* additive lines can't take fog (it would add the fog colour), so they fade out by their own alpha */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.002, -110]}>
        <planeGeometry args={[16, 240]} />
        <meshBasicMaterial map={lanes} alphaMap={fade} transparent opacity={0.6} blending={THREE.AdditiveBlending} depthWrite={false} fog={false} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.004, -110]}>
        <planeGeometry args={[16, 240]} />
        <meshBasicMaterial map={ticks} alphaMap={fade} transparent opacity={0.35} blending={THREE.AdditiveBlending} depthWrite={false} fog={false} />
      </mesh>
    </group>
  );
};

// Dust in the air and soft out-of-focus motes right at the lens.
const Air: React.FC<{fr: number}> = ({fr}) => {
  const {dust, disc} = useMemo(() => {
    const n = 700, pos = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { pos[i * 3] = (random(`dx${i}`) - 0.5) * 9; pos[i * 3 + 1] = (random(`dy${i}`) - 0.5) * 7; pos[i * 3 + 2] = (random(`dz${i}`) - 0.5) * 9; }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const disc = canvasTex(128, 128, (c) => { const gr = c.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.55, 'rgba(255,255,255,0.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = gr; c.fillRect(0, 0, 128, 128); });
    return {dust: g, disc};
  }, []);
  return (
    <group>
      <points geometry={dust} rotation={[0, fr * 0.0015, 0]}>
        <pointsMaterial map={disc} size={0.03} color="#ffd9b0" transparent opacity={0.45} depthWrite={false} blending={THREE.AdditiveBlending} />
      </points>
      {[[-1.05, 1.9, 4.6, 0.55, '#E7A15A', 0.16], [1.0, -1.5, 4.8, 0.7, '#7b8cff', 0.1], [0.9, 2.3, 4.3, 0.35, '#ffd2a0', 0.14], [-0.95, -2.05, 4.5, 0.45, '#E7A15A', 0.1]].map(([x, y, z, s, c, o], i) => (
        <sprite key={i} position={[x as number, (y as number) + Math.sin(fr * 0.02 + i) * 0.03, z as number]} scale={[s as number, s as number, 1]}>
          <spriteMaterial map={disc} color={c as string} transparent opacity={o as number} depthWrite={false} blending={THREE.AdditiveBlending} fog={false} />
        </sprite>
      ))}
    </group>
  );
};

// Amber light leaking through the cracks, from the impact outwards; holes go dark.
export const Cracks: React.FC<{p: number; pane: Pose}> = ({p, pane}) => {
  const {canvas, tex} = useMemo(() => {
    const canvas = document.createElement('canvas'); canvas.width = 540; canvas.height = 960;
    const tex = new THREE.CanvasTexture(canvas); tex.colorSpace = THREE.SRGBColorSpace;
    return {canvas, tex};
  }, []);
  const g = canvas.getContext('2d')!, S = 540;
  g.clearRect(0, 0, 540, 960);
  g.lineJoin = 'round';
  SHARDS.forEach((s) => {
    const k = cracked(s, p) * (1 - Math.min(1, flight(s, p) * 6)); // a piece that has left takes its crack with it
    if (k <= 0.01) return;
    g.beginPath(); s.poly.forEach(([x, y], j) => (j ? g.lineTo(x * S, y * S) : g.moveTo(x * S, y * S))); g.closePath();
    g.strokeStyle = `rgba(255,190,120,${0.9 * k})`; g.lineWidth = 3; g.shadowColor = 'rgba(231,161,90,1)'; g.shadowBlur = 14; g.stroke();
  });
  tex.needsUpdate = true;
  return (
    <mesh position={pane.pos.clone().add(new THREE.Vector3(0, 0, -0.012).applyQuaternion(pane.quat))} quaternion={pane.quat}>
      <planeGeometry args={[pane.scale, pane.scale * A]} />
      <meshBasicMaterial map={tex} transparent opacity={crackReach(p)} blending={THREE.AdditiveBlending} depthWrite={false} toneMapped={false} />
    </mesh>
  );
};

// The frozen frame is a screen in the dark: a soft spill of its light around it.
export const Halo: React.FC<{pane: Pose; k: number}> = ({pane, k}) => {
  const tex = useMemo(() => canvasTex(256, 256, (g) => { const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, 'rgba(255,214,170,0.55)'); gr.addColorStop(0.4, 'rgba(231,161,90,0.18)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); }), []);
  return (
    <mesh position={pane.pos.clone().add(new THREE.Vector3(0, 0, -0.25).applyQuaternion(pane.quat))} quaternion={pane.quat}>
      <planeGeometry args={[pane.scale * 3.2, pane.scale * A * 2.2]} />
      <meshBasicMaterial map={tex} transparent opacity={0.7 * k} blending={THREE.AdditiveBlending} depthWrite={false} toneMapped={false} />
    </mesh>
  );
};

export const look: ShardLook = {
  // the shards are pieces of a screen: they give light rather than take it
  face: (t) => new THREE.MeshBasicMaterial({map: t, color: new THREE.Color(0.86, 0.84, 0.82), toneMapped: false}),
  clip: (t) => new THREE.MeshBasicMaterial({map: t, color: new THREE.Color(0.9, 0.9, 0.9), toneMapped: false}),
  edge: new THREE.MeshPhysicalMaterial({color: '#8d95a8', metalness: 0.1, roughness: 0.08, clearcoat: 1, emissive: '#5a3a20', emissiveIntensity: 0.5}),
  thick: 0.016,
};

export const LuminousFrame: React.FC = () => {
  const fr = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const p = fr / (durationInFrames - 1);
  const imgs = useImgs();
  const pane: Pose = useMemo(() => ({pos: new THREE.Vector3(-0.08, 1.12, -0.7), quat: new THREE.Quaternion().setFromEuler(new THREE.Euler(0.02, 0.16, -0.03)), scale: 1.16}), []);
  const phone: Pose = useMemo(() => ({pos: new THREE.Vector3(0.1, -1.36, 0.55), quat: new THREE.Quaternion().setFromEuler(new THREE.Euler(-1.05, 0.0, 0.1, 'XYZ')), scale: 1.4}), []);
  const landed = (i: number) => (flight(SHARDS[i], p) >= 0.985 ? 1 : 0);
  const flash = (i: number) => { const s = SHARDS[i], t = (p - s.leave - 0.2 * 0.985) / 0.1; return t >= 0 && t <= 1 ? 1 - t : 0; };
  const cam = new THREE.Vector3(0.05 - p * 0.15, 0.42 - p * 0.1, 6.5 - p * 0.35);
  const inAir = SHARDS.filter((s) => { const f = flight(s, p); return f > 0 && f < 0.985; }).length;
  return (
    <AbsoluteFill style={{background: NIGHT}}>
      <Finish fr={fr} bloom={0.85}>
        <ThreeCanvas width={1080} height={1920} camera={{position: cam.toArray(), fov: 38}} gl={{toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.05}} onCreated={({camera}) => camera.lookAt(0, -0.05, 0)}>
          <CamAim target={[0, -0.05 - p * 0.05, 0]} pos={cam} />
          <World />
          <Timeline />
          <Blocks />
          <Air fr={fr} />
          <ambientLight intensity={0.06} />
          <directionalLight position={[-3, 4, -4]} color="#E7A15A" intensity={2.6} />
          <directionalLight position={[4, 1, 3]} color="#7088ff" intensity={0.35} />
          {/* the frozen frame lights what is in front of it, less as it empties */}
          <pointLight position={[pane.pos.x, pane.pos.y, pane.pos.z + 0.9]} color="#ffe7cf" intensity={2.2 * (1 - inAir / N) * (1 - p * 0.6)} distance={6} decay={2} />
          {imgs ? (
            <>
              <Cracks p={p} pane={pane} />
              <Halo pane={pane} k={(1 - inAir / N) * (1 - p * 0.5)} />
              <Shards3D p={p} pane={pane} phone={phone} face={imgs.face} clips={imgs.clips} look={look} />
              <group position={phone.pos} quaternion={phone.quat} scale={phone.scale}>
                <Phone3D assets={null} state={{time: '9:41'}} res={3} light={1.3} glare={0.05} paint={(g) => paintRoll(g, imgs, landed, flash)} />
              </group>
            </>
          ) : null}
        </ThreeCanvas>
      </Finish>
      <Caption words={['39', 'clips']} pill={0} top={1010} />
    </AbsoluteFill>
  );
};

const CamAim: React.FC<{target: [number, number, number]; pos: THREE.Vector3}> = ({target, pos}) => {
  const camera = useThree((s) => s.camera);
  camera.position.copy(pos);
  camera.lookAt(...target);
  return null;
};
