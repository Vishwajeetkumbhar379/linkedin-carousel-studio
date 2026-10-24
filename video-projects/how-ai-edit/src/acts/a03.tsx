// Line 3: "First, AI listened. // Every word I said got a start time and an end time."
// The cart rolls to the audio lane: the real "Hey, I'm Rish" clip as a waveform terrain. Each word
// drops onto it as a glass box stamped with its real Whisper start and end times.
import React from 'react';
import {cue} from '../lib';
import {Caption} from '../styleframes/caption';
import {useTextures} from '../world/kit';
import {Cart, RAIL, RAIL_Y, Rail, Z} from '../world/rail';
import {ClipLane} from '../world/props';
import {tile} from '../styleframes/data';
import {AUDIO, AudioTerrain, WORDS, WordBox, zAt} from '../world/audio';
import {FLOOR_Y} from '../world/kit';
import {Shot, Stage, faceOf, mixV, sm, v3} from './base';

const CLIP_PATHS = Array.from({length: 39}, (_, i) => tile(i));

export const A03: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const clips = useTextures(CLIP_PATHS);
  const t0 = cue("First AI listened"), every = cue("Every word"), endT = cue("end time");
  const roll = sm(t0, t0 + 1.4, t); // the cart rolls from 0:00 to the start of the clip
  const cartZ = RAIL.start + (zAt(0) + 0.4 - RAIL.start) * roll;
  // camera rides behind the cart, then turns to the lane
  const A: Shot = {cam: v3(0.42, RAIL_Y + 0.62, RAIL.start + 2.3), look: v3(-0.15, RAIL_Y + 0.05, RAIL.start - 10)};
  const B: Shot = {cam: v3(0.3, FLOOR_Y + 2.1, Z.audio + 4.4), look: v3(AUDIO.x - 0.05, FLOOR_Y + 0.3, Z.audio - 3.4)};
  const k = sm(t0, every, t);
  const drift = sm(every, endT + 0.6, t);
  const shot: Shot = {cam: mixV(A.cam, B.cam, k).add(v3(0.05 * drift, -0.1 * drift, -0.5 * drift)), look: mixV(A.look, B.look, k)};
  // words stamp one after another while he says "Every word I said got a start time and an end time"
  const stampAt = (i: number) => every + (i / WORDS.length) * (endT - every + 0.3);
  const caption = t < every - 0.1 ? {w: ['AI', 'listened'], p: 1} : t < endT - 0.2 ? {w: ['every', 'word'], p: 1} : {w: ['an', 'end', 'time'], p: 1};
  const face = faceOf(shot);
  return (
    <Stage fr={fr} shot={shot} overlay={<Caption words={caption.w} pill={caption.p} top={1060} />}>
      <Rail played={cartZ} />
      {clips ? <ClipLane tex={clips} /> : null}
      <AudioTerrain hot={null} />
      {WORDS.map((w, i) => (
        <WordBox key={i} w={w} face={face} stamp={sm(stampAt(i), stampAt(i) + 0.25, t)} flags={i < 5} label={i < 5} tier={i === 2 ? 1 : 0} />
      ))}
      <Cart z={cartZ} face={face} />
    </Stage>
  );
};
