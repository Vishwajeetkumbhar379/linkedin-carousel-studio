// The rail: Instagram's progress bar for this video, grown into a track the camera rides down.
// The cart is the playhead (amber, the brightest thing). Stations sit beside it at fixed depths.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {C, FLOOR_Y, Label, canvasTex} from './kit';

export const RAIL_Y = FLOOR_Y + 0.14;
export const RAIL = {start: 2, end: -126}; // z of 0:00 and of the end of the bar
// Where things live along the rail (z), in the order the script walks the pipeline.
export const Z = {clips: 0, audio: -14, video: -40, render: -50, music: -84, drafts: -94, end: -126};

// played: z the bar is filled to (white behind the playhead, dim grey ahead)
export const Rail: React.FC<{played: number; glow?: number}> = ({played, glow = 1}) => {
  const len = RAIL.start - RAIL.end;
  const filled = Math.max(0, Math.min(len, RAIL.start - played));
  const groove = useMemo(() => canvasTex(4, 64, (g) => { const gr = g.createLinearGradient(0, 0, 0, 64); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.5, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 4, 64); }), []);
  return (
    <group>
      {/* the unplayed track: a dim glass bar */}
      <mesh position={[0, RAIL_Y, (RAIL.start + RAIL.end) / 2]}>
        <boxGeometry args={[0.07, 0.035, len]} />
        <meshPhysicalMaterial color="#2a2f3e" roughness={0.2} clearcoat={1} emissive="#3a4160" emissiveIntensity={0.35 * glow} />
      </mesh>
      {/* the played part: lit from inside, warm white */}
      {filled > 0.01 ? (
        <mesh position={[0, RAIL_Y + 0.004, RAIL.start - filled / 2]}>
          <boxGeometry args={[0.075, 0.04, filled]} />
          <meshBasicMaterial color={new THREE.Color('#fff1e0').multiplyScalar(1.15 * glow)} toneMapped={false} />
        </mesh>
      ) : null}
      {/* light the played bar spills on the floor */}
      {filled > 0.01 ? (
        <mesh position={[0, FLOOR_Y + 0.006, RAIL.start - filled / 2]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[0.9, filled]} />
          <meshBasicMaterial map={groove} transparent opacity={0.22 * glow} color="#ffd8b0" blending={THREE.AdditiveBlending} depthWrite={false} />
        </mesh>
      ) : null}
    </group>
  );
};

// The playhead: an amber glass puck riding the rail, with its own light and a timecode tag.
export const Cart: React.FC<{z: number; time?: string; face?: THREE.Vector3; scale?: number}> = ({z, time, face, scale = 1}) => (
  <group position={[0, RAIL_Y, z]} scale={scale}>
    <mesh position={[0, 0.02, 0]}>
      <cylinderGeometry args={[0.16, 0.18, 0.1, 40]} />
      <meshPhysicalMaterial color="#3a2614" metalness={0.3} roughness={0.25} clearcoat={1} emissive={C.amber} emissiveIntensity={0.6} />
    </mesh>
    <mesh position={[0, 0.16, 0]}>
      <sphereGeometry args={[0.1, 32, 16]} />
      <meshBasicMaterial color={new THREE.Color(C.amberHot).multiplyScalar(1.6)} toneMapped={false} />
    </mesh>
    {/* the playhead line rising from it */}
    <mesh position={[0, 0.55, 0]}>
      <boxGeometry args={[0.012, 0.8, 0.012]} />
      <meshBasicMaterial color={new THREE.Color(C.amber).multiplyScalar(1.3)} toneMapped={false} />
    </mesh>
    <pointLight position={[0, 0.3, 0]} color={C.amber} intensity={3.2} distance={4} decay={2} />
    {time ? <Label text={time} h={0.13} position={[0, 1.05, 0]} face={face} style={{font: 'mono', weight: 500, color: C.amberHot, bg: 'rgba(20,14,10,0.75)', pad: 0.35}} /> : null}
  </group>
);
