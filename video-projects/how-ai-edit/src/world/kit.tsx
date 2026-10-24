// The film's world, shared by every act: a dusk sky, the timeline floor, air, labels and loaders.
// Look (approved 24 Oct, style frame A): a dark low-saturation ground, amber for what to follow,
// cool lane blue for structure, white for his words and real numbers.
import React, {useEffect, useMemo, useState} from 'react';
import {delayRender, random, staticFile} from 'remotion';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {settle} from '../kit/three-canvas';

export const C = {
  night: '#06080f', horizon: '#1c1519', amber: '#E7A15A', amberHot: '#ffc68a', lane: '#6f86ff',
  laneDim: '#26304f', white: '#F4F5F7', red: '#ff5a4e', floor: '#0a0c15',
};
export const FLOOR_Y = -2.55;

export const canvasTex = (w: number, h: number, draw: (g: CanvasRenderingContext2D) => void, srgb = true) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d')!);
  const t = new THREE.CanvasTexture(c); t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace; t.anisotropy = 8;
  return t;
};

// Load images from public/ as textures; the frame waits until all are decoded.
export const useTextures = (paths: string[]): THREE.Texture[] | null => {
  const key = paths.join('|');
  const [tex, set] = useState<THREE.Texture[] | null>(null);
  const [handle] = useState(() => delayRender(`textures ${key.slice(0, 60)}`));
  useEffect(() => {
    Promise.all(paths.map((p) => new Promise<THREE.Texture>((ok) => {
      const im = new Image();
      im.onload = () => { const t = new THREE.Texture(im); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.needsUpdate = true; ok(t); };
      im.src = staticFile(p);
    }))).then((t) => { set(t); settle(handle); });
  }, [key]); // eslint-disable-line react-hooks/exhaustive-deps
  return tex;
};

// Sky dome (night overhead, an ember of dusk at the horizon), fog the colour of the horizon, and a
// dim environment with one amber strip and one cool strip for reflections.
export const Sky: React.FC<{fog?: number}> = ({fog = 0.05}) => {
  const {gl, scene} = useThree();
  useMemo(() => {
    const room = new THREE.Scene();
    room.add(new THREE.Mesh(new THREE.SphereGeometry(10, 32, 16), new THREE.MeshBasicMaterial({color: '#05060a', side: THREE.BackSide})));
    const strip = (color: string, x: number, y: number, z: number, w: number, h: number, i: number) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({color: new THREE.Color(color).multiplyScalar(i), side: THREE.DoubleSide}));
      m.position.set(x, y, z); m.lookAt(0, 0, 0); room.add(m);
    };
    strip(C.amber, -6, 2, -3, 2.5, 7, 3.2);
    strip('#5f78ff', 6, 3, 2, 1.5, 6, 1.1);
    strip('#ffffff', 0, 8, 4, 6, 1, 0.6);
    scene.environment = new THREE.PMREMGenerator(gl).fromScene(room, 0.03).texture;
    scene.background = new THREE.Color(C.night);
    scene.fog = new THREE.FogExp2(C.horizon, fog);
  }, [gl, scene, fog]);
  const dome = useMemo(() => canvasTex(8, 1024, (g) => {
    const gr = g.createLinearGradient(0, 0, 0, 1024); // v=1 (top of the canvas) is the zenith
    gr.addColorStop(0, '#03050a'); gr.addColorStop(0.3, '#070a14'); gr.addColorStop(0.44, '#1a1420'); gr.addColorStop(0.49, '#3a2522');
    gr.addColorStop(0.5, C.horizon); gr.addColorStop(1, '#0a080b');
    g.fillStyle = gr; g.fillRect(0, 0, 8, 1024);
  }), []);
  return (
    <mesh renderOrder={-10}>
      <sphereGeometry args={[400, 32, 32]} />
      <meshBasicMaterial map={dome} side={THREE.BackSide} fog={false} depthWrite={false} toneMapped={false} />
    </mesh>
  );
};

// The floor: dark glass; lane lines and timecode ticks run down the middle toward the horizon.
export const Floor: React.FC<{lanes?: boolean}> = ({lanes = true}) => {
  const {lane, ticks, fade} = useMemo(() => {
    const lane = canvasTex(1024, 1024, (g) => {
      g.fillStyle = '#000'; g.fillRect(0, 0, 1024, 1024);
      for (let i = 0; i <= 8; i++) { const x = 64 + i * 112; g.fillStyle = i % 4 === 0 ? 'rgba(120,140,220,0.55)' : 'rgba(80,100,180,0.28)'; g.fillRect(x - 1.5, 0, 3, 1024); }
    });
    const ticks = canvasTex(64, 1024, (g) => { g.fillStyle = '#000'; g.fillRect(0, 0, 64, 1024); for (let y = 0; y < 1024; y += 64) { g.fillStyle = 'rgba(140,160,230,0.5)'; g.fillRect(0, y, 64, 2); } });
    const fade = canvasTex(4, 256, (g) => { const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, '#000'); gr.addColorStop(0.86, '#1a1a1a'); gr.addColorStop(0.97, '#fff'); gr.addColorStop(1, '#fff'); g.fillStyle = gr; g.fillRect(0, 0, 4, 256); }, false);
    lane.wrapS = lane.wrapT = THREE.RepeatWrapping; lane.repeat.set(1, 24);
    ticks.wrapS = ticks.wrapT = THREE.RepeatWrapping; ticks.repeat.set(46, 48);
    return {lane, ticks, fade};
  }, []);
  return (
    <group position={[0, FLOOR_Y, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, -150]} receiveShadow>
        <planeGeometry args={[600, 340]} />
        <meshPhysicalMaterial color={C.floor} roughness={0.3} clearcoat={0.5} clearcoatRoughness={0.3} />
      </mesh>
      {lanes ? (
        <>
          {/* additive lines can't take fog (it would add the fog colour), so they fade by their own alpha */}
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.002, -110]}>
            <planeGeometry args={[16, 240]} />
            <meshBasicMaterial map={lane} alphaMap={fade} transparent opacity={0.6} blending={THREE.AdditiveBlending} depthWrite={false} fog={false} />
          </mesh>
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.004, -110]}>
            <planeGeometry args={[16, 240]} />
            <meshBasicMaterial map={ticks} alphaMap={fade} transparent opacity={0.35} blending={THREE.AdditiveBlending} depthWrite={false} fog={false} />
          </mesh>
        </>
      ) : null}
    </group>
  );
};

export const disc = () => canvasTex(128, 128, (c) => { const gr = c.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.55, 'rgba(255,255,255,0.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = gr; c.fillRect(0, 0, 128, 128); });

// Dust in the air around `at`, and soft out-of-focus motes at the lens (relative to the camera).
export const Air: React.FC<{fr: number; at?: [number, number, number]; cam: THREE.Vector3; look: THREE.Vector3}> = ({fr, at = [0, 0, 0], cam, look}) => {
  const {dust, d} = useMemo(() => {
    const n = 900, pos = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { pos[i * 3] = (random(`dx${i}`) - 0.5) * 10; pos[i * 3 + 1] = (random(`dy${i}`) - 0.5) * 7; pos[i * 3 + 2] = (random(`dz${i}`) - 0.5) * 14; }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    return {dust: g, d: disc()};
  }, []);
  // motes sit on a plane 1.2 units in front of the lens
  const fwd = look.clone().sub(cam).normalize(), right = new THREE.Vector3().crossVectors(fwd, new THREE.Vector3(0, 1, 0)).normalize(), up = new THREE.Vector3().crossVectors(right, fwd);
  const mote = (x: number, y: number) => cam.clone().add(fwd.clone().multiplyScalar(1.2)).add(right.clone().multiplyScalar(x)).add(up.clone().multiplyScalar(y));
  return (
    <group>
      <points geometry={dust} position={at} rotation={[0, fr * 0.0015, 0]}>
        <pointsMaterial map={d} size={0.03} color="#ffd9b0" transparent opacity={0.45} depthWrite={false} blending={THREE.AdditiveBlending} />
      </points>
      {([[-0.28, 0.42, 0.13, C.amber, 0.14], [0.27, -0.35, 0.17, '#7b8cff', 0.09], [0.22, 0.55, 0.08, '#ffd2a0', 0.12], [-0.24, -0.5, 0.11, C.amber, 0.09]] as [number, number, number, string, number][]).map(([x, y, s, c, o], i) => (
        <sprite key={i} position={mote(x, y + Math.sin(fr * 0.02 + i) * 0.006)} scale={[s, s, 1]}>
          <spriteMaterial map={d} color={c} transparent opacity={o} depthWrite={false} blending={THREE.AdditiveBlending} fog={false} />
        </sprite>
      ))}
    </group>
  );
};

// A text label drawn on a canvas, as a plane `h` units tall. Mono for numbers, Geist for words.
export type LabelStyle = {font?: 'sans' | 'mono'; weight?: number; color?: string; bg?: string; pad?: number; radius?: number; stroke?: string};
const FONT = {sans: 'Geist, system-ui, sans-serif', mono: '"Geist Mono", ui-monospace, monospace'};
export const labelTex = (text: string, s: LabelStyle = {}) => {
  const px = 96, pad = (s.pad ?? 0.25) * px;
  const m = document.createElement('canvas').getContext('2d')!;
  const font = `${s.weight ?? 700} ${px}px ${FONT[s.font ?? 'sans']}`;
  m.font = font;
  const w = Math.ceil(m.measureText(text).width + pad * 2), h = Math.ceil(px * 1.3 + pad * 2);
  const t = canvasTex(w, h, (g) => {
    if (s.bg) { g.fillStyle = s.bg; g.beginPath(); g.roundRect(0, 0, w, h, (s.radius ?? 0.3) * h); g.fill(); }
    if (s.stroke) { g.strokeStyle = s.stroke; g.lineWidth = 6; g.beginPath(); g.roundRect(3, 3, w - 6, h - 6, (s.radius ?? 0.3) * h); g.stroke(); }
    g.font = font; g.fillStyle = s.color ?? C.white; g.textBaseline = 'middle'; g.fillText(text, pad, h / 2 + px * 0.04);
  });
  return {t, aspect: w / h};
};
export const Label: React.FC<{text: string; h: number; position: [number, number, number] | THREE.Vector3; face?: THREE.Vector3; rotation?: [number, number, number]; style?: LabelStyle; opacity?: number; glow?: number; anchor?: 'left' | 'center' | 'right'}> = ({text, h, position, face, rotation, style, opacity = 1, glow = 1, anchor = 'center'}) => {
  const {t, aspect} = useMemo(() => labelTex(text, style), [text, JSON.stringify(style)]); // eslint-disable-line react-hooks/exhaustive-deps
  const ref = React.useRef<THREE.Mesh>(null);
  const pos = position instanceof THREE.Vector3 ? position : new THREE.Vector3(...position);
  // `face`: the direction the label looks along (toward the camera), so parents may be translated
  const quat = useMemo(() => {
    if (!face) return undefined;
    const o = new THREE.Object3D(); o.lookAt(face); return o.quaternion.clone();
  }, [face?.x, face?.y, face?.z]); // eslint-disable-line react-hooks/exhaustive-deps
  const off = anchor === 'left' ? (h * aspect) / 2 : anchor === 'right' ? -(h * aspect) / 2 : 0;
  return (
    <group position={pos} quaternion={quat} rotation={quat ? undefined : rotation}>
      <mesh ref={ref} position={[off, 0, 0]}>
        <planeGeometry args={[h * aspect, h]} />
        <meshBasicMaterial map={t} transparent opacity={opacity} depthWrite={false} toneMapped={false} color={new THREE.Color(glow, glow, glow)} />
      </mesh>
    </group>
  );
};

// Point the camera every frame (the canvas camera is set once at mount).
export const Aim: React.FC<{pos: THREE.Vector3; look: THREE.Vector3; fov?: number; roll?: number}> = ({pos, look, fov, roll = 0}) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  camera.position.copy(pos);
  camera.up.set(Math.sin(roll), Math.cos(roll), 0);
  camera.lookAt(look);
  if (fov && camera.fov !== fov) { camera.fov = fov; camera.updateProjectionMatrix(); }
  return null;
};
