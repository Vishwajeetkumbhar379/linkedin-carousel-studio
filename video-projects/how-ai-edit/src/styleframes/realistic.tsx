// Style frame B, realistic 3D: his real desk at night, one warm lamp. The frozen frame hangs over
// the desk as a pane of glass, cracks, and its pieces drop onto the phone lying by the mug.
import React, {useMemo} from 'react';
import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {ThreeCanvas} from '../kit/three-canvas';
import {Finish} from '../kit/finish';
import {Phone3D} from '../kit/phone';
import {FLIGHT, N, SHARDS, flight} from './data';
import {paintRoll, useImgs} from './roll';
import {Pose, Shards3D, ShardLook} from './shards3d';
import {Caption} from './caption';

const LAMP = '#ffb066';

const canvasTex = (w: number, h: number, draw: (g: CanvasRenderingContext2D) => void, srgb = true) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d')!);
  const t = new THREE.CanvasTexture(c); t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace; t.anisotropy = 8; return t;
};

const Env: React.FC = () => {
  const {gl, scene} = useThree();
  useMemo(() => {
    const pm = new THREE.PMREMGenerator(gl);
    scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environmentIntensity = 0.06;
    scene.background = new THREE.Color('#0b0908');
    gl.shadowMap.type = THREE.PCFSoftShadowMap;
  }, [gl, scene]);
  return null;
};

// Walnut: long grain lines with slow waves, pores, and a roughness map from the same grain.
const useWood = () => useMemo(() => {
  const grain = (g: CanvasRenderingContext2D, rough: boolean) => {
    const W = 2048, H = 1024;
    g.fillStyle = rough ? '#7a7a7a' : '#3b2417'; g.fillRect(0, 0, W, H);
    for (let i = 0; i < 700; i++) {
      const y0 = random(`wy${i}`) * H, amp = 6 + random(`wa${i}`) * 18, fq = 0.002 + random(`wf${i}`) * 0.004, ph = random(`wp${i}`) * 6;
      const dark = random(`wd${i}`) < 0.5, a = 0.05 + random(`wo${i}`) * 0.12;
      g.strokeStyle = rough ? (dark ? `rgba(160,160,160,${a})` : `rgba(60,60,60,${a})`) : dark ? `rgba(18,9,4,${a * 1.6})` : `rgba(120,74,44,${a})`;
      g.lineWidth = 0.6 + random(`ww${i}`) * 2.4;
      g.beginPath();
      for (let x = 0; x <= W; x += 16) { const y = y0 + Math.sin(x * fq + ph) * amp + Math.sin(x * fq * 3.1 + ph) * amp * 0.25; x ? g.lineTo(x, y) : g.moveTo(x, y); }
      g.stroke();
    }
    for (let i = 0; i < 5200; i++) { g.fillStyle = rough ? 'rgba(200,200,200,0.25)' : 'rgba(15,8,4,0.25)'; g.fillRect(random(`px${i}`) * W, random(`py${i}`) * H, 2 + random(`pl${i}`) * 5, 1); }
  };
  const map = canvasTex(2048, 1024, (g) => grain(g, false));
  const rough = canvasTex(2048, 1024, (g) => grain(g, true), false);
  return {map, rough};
}, []);

const Desk: React.FC = () => {
  const wood = useWood();
  const plaster = useMemo(() => canvasTex(512, 512, (g) => {
    g.fillStyle = '#8a8a8a'; g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 9000; i++) { const v = 110 + random(`pq${i}`) * 50; g.fillStyle = `rgba(${v},${v},${v},0.35)`; g.fillRect(random(`ps${i}`) * 512, random(`pt${i}`) * 512, 2, 2); }
  }, false), []);
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[22, 14]} />
        <meshPhysicalMaterial map={wood.map} roughnessMap={wood.rough} roughness={0.62} clearcoat={0.35} clearcoatRoughness={0.4} specularIntensity={0.5} />
      </mesh>
      <mesh position={[0, 6, -4.2]} receiveShadow>
        <planeGeometry args={[30, 14]} />
        <meshStandardMaterial color="#5a4d42" roughnessMap={plaster} roughness={0.95} />
      </mesh>
    </group>
  );
};

// An anglepoise-style desk lamp: weighted base, two arms with joints, a cone shade with the bulb inside.
const Lamp: React.FC = () => {
  const metal = useMemo(() => new THREE.MeshStandardMaterial({color: '#151517', metalness: 0.75, roughness: 0.32}), []);
  const inner = useMemo(() => new THREE.MeshStandardMaterial({color: '#f1ece4', roughness: 0.5, side: THREE.BackSide, emissive: LAMP, emissiveIntensity: 0.12}), []);
  const base: [number, number, number] = [-2.05, 0, -2.6], elbow: [number, number, number] = [-1.75, 3.9, -3.2], head: [number, number, number] = [-0.75, 5.2, -2.0];
  const arm = (a: [number, number, number], b: [number, number, number]) => {
    const va = new THREE.Vector3(...a), vb = new THREE.Vector3(...b), mid = va.clone().add(vb).multiplyScalar(0.5), len = va.distanceTo(vb);
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), vb.clone().sub(va).normalize());
    return <mesh position={mid} quaternion={q} material={metal} castShadow><cylinderGeometry args={[0.07, 0.07, len, 20]} /></mesh>;
  };
  // the shade points at the desk in front of the phone
  const aim = new THREE.Vector3(0.4, 0, 1.2).sub(new THREE.Vector3(...head)).normalize();
  const shadeQ = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, -1, 0), aim);
  const bulb = new THREE.Vector3(...head).add(aim.clone().multiplyScalar(0.35));
  const target = useMemo(() => { const o = new THREE.Object3D(); o.position.set(0.4, 0, 1.2); return o; }, []);
  return (
    <group>
      <mesh position={[base[0], 0.12, base[2]]} material={metal} castShadow receiveShadow><cylinderGeometry args={[1.05, 1.15, 0.24, 48]} /></mesh>
      <mesh position={[base[0], 0.3, base[2]]} material={metal} castShadow><sphereGeometry args={[0.16, 24, 16]} /></mesh>
      {arm([base[0], 0.3, base[2]], elbow)}
      <mesh position={elbow} material={metal} castShadow><sphereGeometry args={[0.14, 24, 16]} /></mesh>
      {arm(elbow, head)}
      <group position={head} quaternion={shadeQ}>
        <mesh position={[0, -0.45, 0]} material={metal} castShadow><cylinderGeometry args={[0.28, 0.78, 0.9, 48, 1, true]} /></mesh>
        <mesh position={[0, -0.45, 0]} material={inner}><cylinderGeometry args={[0.27, 0.77, 0.89, 48, 1, true]} /></mesh>
        <mesh position={[0, 0.08, 0]} material={metal} castShadow><sphereGeometry args={[0.34, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]} /></mesh>
      </group>
      <mesh position={bulb}><sphereGeometry args={[0.24, 24, 16]} /><meshBasicMaterial color={new THREE.Color(LAMP).multiplyScalar(2.2)} toneMapped={false} /></mesh>
      <primitive object={target} />
      <spotLight position={bulb} target={target} color={LAMP} intensity={260} angle={0.78} penumbra={0.75} decay={2} distance={30} castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048} shadow-bias={-0.0004} shadow-radius={6} />
      <pointLight position={bulb.clone().add(new THREE.Vector3(0, 0.6, -0.4))} color={LAMP} intensity={9} distance={10} decay={2} />
      {/* spill on the wall behind the lamp */}
      <pointLight position={[-1.2, 4.6, -3.4]} color={LAMP} intensity={7} distance={6} decay={2} />
    </group>
  );
};

// A ceramic mug of coffee and a closed notebook with a pen: the desk he works at.
const Props: React.FC = () => {
  const mug = useMemo(() => {
    const pts = [[0, 0], [0.5, 0], [0.56, 0.04], [0.58, 0.3], [0.6, 1.25], [0.62, 1.32], [0.56, 1.32], [0.54, 0.2], [0, 0.2]].map(([x, y]) => new THREE.Vector2(x, y));
    return new THREE.LatheGeometry(pts, 64);
  }, []);
  const ceramic = useMemo(() => new THREE.MeshPhysicalMaterial({color: '#e8e1d6', roughness: 0.28, clearcoat: 0.6, clearcoatRoughness: 0.2}), []);
  return (
    <group>
      <group position={[1.35, 0, -1.5]} rotation={[0, 0.5, 0]} scale={0.82}>
        <mesh geometry={mug} material={ceramic} castShadow receiveShadow />
        <mesh position={[0.58, 0.7, 0]} rotation={[0, 0, -Math.PI / 2]} material={ceramic} castShadow><torusGeometry args={[0.32, 0.075, 16, 40, Math.PI]} /></mesh>
        <mesh position={[0, 1.12, 0]} rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[0.54, 48]} /><meshPhysicalMaterial color="#1a0d06" roughness={0.08} clearcoat={1} /></mesh>
      </group>
      <group position={[-1.75, 0, 2.3]} rotation={[0, 0.42, 0]}>
        {/* a closed notebook: two covers with the page block between them */}
        <mesh position={[0, 0.012, 0]} castShadow receiveShadow><boxGeometry args={[2.1, 0.024, 2.95]} /><meshStandardMaterial color="#10151c" roughness={0.7} /></mesh>
        <mesh position={[-0.02, 0.09, 0]} castShadow receiveShadow><boxGeometry args={[2.02, 0.13, 2.88]} /><meshStandardMaterial color="#ddd5c4" roughness={0.95} /></mesh>
        <mesh position={[0, 0.168, 0]} castShadow receiveShadow><boxGeometry args={[2.1, 0.024, 2.95]} /><meshStandardMaterial color="#10151c" roughness={0.7} /></mesh>
        <mesh position={[0.35, 0.236, -0.2]} rotation={[0, 0.5, Math.PI / 2]} castShadow><cylinderGeometry args={[0.05, 0.05, 1.9, 16]} /><meshStandardMaterial color="#b88446" metalness={0.85} roughness={0.28} /></mesh>
      </group>
    </group>
  );
};

const look: ShardLook = {
  // the frozen frame is still a screen image, so it glows a little, but it is glass and takes the lamp
  face: (t) => new THREE.MeshPhysicalMaterial({map: t, emissive: '#ffffff', emissiveMap: t, emissiveIntensity: 0.55, roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.05}),
  clip: (t) => new THREE.MeshPhysicalMaterial({map: t, emissive: '#ffffff', emissiveMap: t, emissiveIntensity: 0.5, roughness: 0.12, clearcoat: 1}),
  edge: new THREE.MeshPhysicalMaterial({color: '#4f6a63', roughness: 0.03, metalness: 0.2, clearcoat: 1, ior: 1.5, emissive: '#16211e', emissiveIntensity: 0.6}),
  thick: 0.03,
  shadows: true,
};

export const RealisticFrame: React.FC = () => {
  const fr = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const p = fr / (durationInFrames - 1);
  const imgs = useImgs();
  const pane: Pose = useMemo(() => ({pos: new THREE.Vector3(0.05, 3.25, -0.9), quat: new THREE.Quaternion().setFromEuler(new THREE.Euler(-0.14, 0.08, 0.02)), scale: 1.45}), []);
  const phone: Pose = useMemo(() => ({pos: new THREE.Vector3(0.35, 0.06, 1.55), quat: new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI / 2, 0, -0.12, 'XYZ')), scale: 1.25}), []);
  const landed = (i: number) => (flight(SHARDS[i], p) >= 0.985 ? 1 : 0);
  const flash = (i: number) => { const s = SHARDS[i], t = (p - s.leave - 0.26 * 0.985) / 0.1; return t >= 0 && t <= 1 ? 1 - t : 0; };
  const inAir = SHARDS.filter((s) => { const f = flight(s, p); return f > 0 && f < 0.985; }).length;
  const cam = new THREE.Vector3(0.15, 6.4 - p * 0.15, 9.3 - p * 0.3);
  return (
    <AbsoluteFill style={{background: '#0b0908'}}>
      <Finish fr={fr} bloom={0.45}>
        <ThreeCanvas width={1080} height={1920} shadows camera={{position: cam.toArray(), fov: 36}} gl={{toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.0}}>
          <Aim pos={cam} target={[0.15, 1.55, 0.2]} />
          <Env />
          <Desk />
          <Lamp />
          <Props />
          <hemisphereLight args={['#2a3550', '#120c08', 0.25]} />
          <pointLight position={[pane.pos.x, pane.pos.y, pane.pos.z + 0.8]} color="#ffe8d2" intensity={5 * (1 - inAir / N) * (1 - p * 0.6)} distance={6} decay={2} />
          {imgs ? (
            <>
              <Shards3D p={p} pane={pane} phone={phone} face={imgs.face} clips={imgs.clips} look={look} lightColor="#fff0e0" />
              <group position={phone.pos} quaternion={phone.quat} scale={phone.scale}>
                <Phone3D assets={null} state={{time: '9:41'}} res={3} light={1.6} glare={0.06} paint={(g) => paintRoll(g, imgs, landed, flash)} />
              </group>
            </>
          ) : null}
        </ThreeCanvas>
      </Finish>
      <Caption words={['39', 'clips']} pill={0} top={1010} />
    </AbsoluteFill>
  );
};

const Aim: React.FC<{pos: THREE.Vector3; target: [number, number, number]}> = ({pos, target}) => {
  const camera = useThree((s) => s.camera);
  camera.position.copy(pos);
  camera.lookAt(...target);
  return null;
};
