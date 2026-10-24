// Toolchain check: a lit, physical object in fog with an environment map, through the template's canvas and finish.
import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {ThreeCanvas} from './kit/three-canvas';
import {Finish} from './kit/finish';

const Env: React.FC = () => {
  const {gl, scene} = useThree();
  useMemo(() => { const pm = new THREE.PMREMGenerator(gl); scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; scene.fog = new THREE.Fog(0x0b0d16, 4, 14); scene.background = new THREE.Color(0x0b0d16); }, [gl, scene]);
  return null;
};
export const Smoke: React.FC = () => {
  const fr = useCurrentFrame();
  return (
    <Finish fr={fr}>
      <AbsoluteFill style={{background: '#0b0d16'}}>
        <ThreeCanvas width={1080} height={1920} camera={{position: [0, 0.6, 4], fov: 40}} gl={{toneMapping: THREE.ACESFilmicToneMapping}}>
          <Env />
          <mesh rotation={[0.3, fr * 0.03, 0]}><boxGeometry args={[1.2, 2.2, 0.12]} /><meshPhysicalMaterial color="#1c1f2a" metalness={0.6} roughness={0.25} clearcoat={1} /></mesh>
          <mesh position={[0, -1.4, 0]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[20, 20]} /><meshStandardMaterial color="#0e1018" roughness={0.6} metalness={0.2} /></mesh>
          <pointLight position={[1.5, 1, 1.5]} color="#E7A15A" intensity={8} distance={6} />
          <mesh position={[1.5, 1, 1.5]}><sphereGeometry args={[0.05]} /><meshBasicMaterial color="#ffd4a0" toneMapped={false} /></mesh>
        </ThreeCanvas>
      </AbsoluteFill>
    </Finish>
  );
};
