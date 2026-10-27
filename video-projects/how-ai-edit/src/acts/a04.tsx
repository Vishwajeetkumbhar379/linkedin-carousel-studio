// Line 4: "It even heard my name wrong. // *Rish*. // One line fixed it."
// Across the rail from the waveform, the caption lane is a split-flap board spelling what Whisper
// heard. RISH glows red. The real fix types itself above the board, {"Rish,": "Vish,"} from
// week1.py, and with one clack the R falls to a V.
import React from 'react';
import {cue} from '../lib';
import {C, FLOOR_Y, Label} from '../world/kit';
import {Cart, Rail, Z} from '../world/rail';
import {AudioTerrain, WORDS, zAt} from '../world/audio';
import {FLAP_W, FlapWord} from '../world/flaps';
import {Shot, Stage, faceOf, sm, v3} from './base';

const BOARD = {x: -1.2, y: FLOOR_Y + 1.05, s: 0.62};
// each caption word stands at its own spot along the lane, in speaking order
const zw = (i: number) => Z.audio - 0.4 - i * 1.3;
const ROWS = ["HEY I'M", 'RISH,', "I'M 27,"]; // what Whisper heard, in caption lines
const FIX = '{"Rish,": "Vish,"}';

export const A04: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const heard = cue("It even got"), rish = cue("Rish"), one = cue("One line fixed it"), fixed = cue("fixed it");
  const typed = sm(one - 0.2, fixed, t); // the fix types itself while he says "One line fixed it"
  const flip = sm(fixed + 0.05, fixed + 0.4, t);
  const redGlow = sm(rish - 0.2, rish + 0.1, t);
  const zR = zw(2), push = sm(heard, fixed, t);
  const shot: Shot = {cam: v3(0.8 - push * 0.15, BOARD.y + 0.05, zR + 3.3 - push * 0.4), look: v3(BOARD.x + 0.15, BOARD.y - 0.18, zR)};
  const face = faceOf(shot);
  const shown = FIX.slice(0, Math.round(typed * FIX.length));
  return (
    <Stage fr={fr} shot={shot}>
      <Rail played={zAt(0.9)} />
      <AudioTerrain />
      <Cart z={zAt(0.9)} face={face} scale={0.8} />
      {/* the board: three rows of tiles like a station departures board, on the left of the rail */}
      <group position={[BOARD.x, BOARD.y, zR]} rotation={[0, 0.62, 0]} scale={BOARD.s}>
        <mesh position={[0, 0, -0.03]}><boxGeometry args={[7 * FLAP_W + 0.2, 3 * 0.42 + 0.16, 0.04]} /><meshPhysicalMaterial color="#0c0e14" roughness={0.4} clearcoat={0.6} /></mesh>
        {ROWS.map((row, r) => (
          <group key={r} position={[-3 * FLAP_W, (1 - r) * 0.42, 0]}>
            <FlapWord text={row.padEnd(7, ' ')} to={r === 1 ? 'VISH,  ' : undefined} flips={r === 1 ? [flip] : []} tone={r === 1 && redGlow > 0.5 && flip < 0.5 ? C.red : C.white} toTone={r === 1 ? C.amberHot : C.white} glow={r === 1 ? 0.35 + redGlow * 0.6 : 0.3} />
          </group>
        ))}
        <pointLight position={[0, 0, 0.6]} color={flip > 0.5 ? C.amber : C.red} intensity={1.4 * redGlow} distance={2.5} decay={2} />
      </group>
      {/* the fix, typed in a code strip over the board */}
      {typed > 0 ? (
        <group position={[BOARD.x + 0.2, BOARD.y + 0.58, zR + 0.15]}>
          <Label text={shown + (typed < 1 ? '|' : '')} h={0.11} position={[0, 0, 0]} face={face} style={{font: 'mono', weight: 500, color: C.amberHot, bg: 'rgba(10,9,14,0.86)', pad: 0.45, radius: 0.18}} />
          <Label text="week1.py, line 46" h={0.05} position={[0, 0.12, 0]} face={face} style={{font: 'mono', weight: 500, color: '#8e97b8'}} />
        </group>
      ) : null}
    </Stage>
  );
};
