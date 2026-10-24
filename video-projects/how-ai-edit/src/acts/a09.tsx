// Line 9: "And the sound? / *Silence*, / exactly where it hurts."
// The music lane as a ridge, with a clean hole where the Week 1 mix really goes silent. When the
// playhead crosses the hole, the sound cuts dead and everything moving freezes for a full beat,
// then sound and motion come back together.
import React from 'react';
import {cue} from '../lib';
import {Caption} from '../styleframes/caption';
import {FLOOR_Y} from '../world/kit';
import {Cart, Rail} from '../world/rail';
import {MUSIC, MusicRidge, SIL, mz} from '../world/music';
import {Shot, Stage, faceOf, sm, v3} from './base';

export const A09: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const t0 = cue("And the sound"), sil = cue("Silence"), hurts = cue("where it hurts");
  // <freeze>: from "Silence" for one beat, time stops (camera, cart, dust and grain hold)
  const fz0 = sil, fz1 = sil + 0.9;
  const tf = t > fz0 && t < fz1 ? fz0 : t > fz1 ? t - (fz1 - fz0) : t;
  const travel = sm(t0, sil, tf);
  const cartZ = mz(0.8) - (mz(SIL[0]) - mz(0.8)) * -travel;
  const mid = (SIL[0] + SIL[1]) / 2;
  const shot: Shot = {cam: v3(MUSIC.x - 2.6 + travel * 0.4, FLOOR_Y + 1.35, mz(mid) + 1.6 - travel * 0.6), look: v3(MUSIC.x + 0.1, FLOOR_Y + 0.5, mz(mid) - 0.3)};
  const face = faceOf(shot);
  const frz = tf !== t ? Math.round(fz0 * 30) : fr;
  const caption = t < sil - 0.1 ? {w: ['and', 'the', 'sound?'], p: -1} : t < hurts - 0.1 ? {w: ['Silence'], p: 0} : {w: ['where', 'it', 'hurts'], p: 2};
  return (
    <Stage fr={frz} shot={shot} overlay={<Caption words={caption.w} pill={caption.p} top={1060} />}>
      <Rail played={cartZ} />
      <MusicRidge face={face} />
      <Cart z={cartZ} face={face} scale={0.8} />
    </Stage>
  );
};
