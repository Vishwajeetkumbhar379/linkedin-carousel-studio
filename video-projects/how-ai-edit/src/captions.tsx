// The film's captions: hand-cut sense units over Vish's real words (src/words.json), 2 to 4 words, one key
// word in an amber pill (red for the misheard "Rish"). On his face they would cover it, so while he is
// on camera they sit above his head; over the 3D world they sit at 55% (inside Instagram's safe box).
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {WORDS, chunk} from './lib';
import {Caption} from './styleframes/caption';
import LINES from '../vo/lines.json';

// [sense unit exactly as transcribed, index of the pill word or -1, optional pill colour]
const UNITS: [string, number, string?][] = [
  ['Hold on,', -1], ['this video was', -1], ['39 clips', 0], ['on my phone.', 2],
  ['No editing app', 0], ['touched this', -1], ["but let's rewind.", 2], ['See what touched it.', -1],
  ['First AI listened', 1], ['very carefully', -1], ['to every word I said.', 2], ['It got the start time,', 3], ['it got the end time.', 3],
  ['It even got', -1], ['my name wrong.', 2], ['Instead of Vish,', 2], ['it got Rish', 2, '#ff5a4e'], ['but one line', 1], ['fixed it.', -1],
  ['Then it cut everything', 2], ['not in between', -1], ['the sentences', -1], ['but in between', -1], ['the words.', 1],
  ['Then it cut me out.', 3], ['Every single frame', 0], ['and the caption', 2], ['sits behind me.', 1],
  ['Every caption,', 1], ['every sticker', 1], ['is a tiny webpage', 3], ['photographed', -1], ['30 times a second.', 0],
  ["Let's slow down time.", 1], ['At one frame a second', 1], ['a one -minute reel', -1], ['takes 30 minutes', 1], ['to watch', -1],
  ['and the sound', -1], ['silence', 0], ['exactly where it hurts.', 3],
  ["And it didn't take one,", 4], ["it didn't take five,", 3], ['it took 12 rounds', 2], ['of feedback from me', 2], ['to get the perfect', -1], ['video I want.', -1],
  ["Hi, I'm Vish.", 2], ["And if you're", -1], ['still here,', -1], ['the edit', -1], ['did its job.', 2],
  ['Comment EDIT', 1], ['and I will send you', -1], ['the prompts.', 1],
];
const CHUNKS = chunk(WORDS, UNITS.map((u) => u[0]));
const clean = (w: string) => w.replace(/^-/, '').replace(/[,.]$/, '');
// while he is on camera (line 1 before the freeze, "Hi, I'm Vish") captions go above his head
const ON_CAM: [number, number][] = [[0, WORDS.find((w) => w.w === '39')!.s - 0.06], [LINES[9].parts[1].at, LINES[10].start]];

export const Captions: React.FC = () => {
  const t = useCurrentFrame() / 30;
  const i = CHUNKS.findIndex((c) => t >= c.s && t < c.e);
  if (i < 0) return null;
  const [, pill, color] = UNITS[i];
  const top = ON_CAM.some(([a, b]) => t >= a && t < b) ? 300 : 1060;
  return <Caption words={CHUNKS[i].words.map((w) => clean(w.w))} pill={pill} top={top} pillColor={color} />;
};
