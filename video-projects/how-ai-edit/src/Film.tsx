// The film: one Sequence per spoken line. Acts not built yet show their line on a dark card.
import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {ACTS, ActName, FPS} from './lib';
import {A01} from './acts/a01';
import {A02} from './acts/a02';
import {A03} from './acts/a03';
import {A04} from './acts/a04';
import {A05} from './acts/a05';
import {A06} from './acts/a06';
import {A07} from './acts/a07';
import {A08} from './acts/a08';
import {A09} from './acts/a09';
import {A10} from './acts/a10';
import {A11} from './acts/a11';
import {useFonts} from './styleframes/fonts';
import {Captions} from './captions';

const BUILT: Partial<Record<ActName, React.FC<{t: number; fr: number}>>> = {l01: A01, l02: A02, l03: A03, l04: A04, l05: A05, l06: A06, l07: A07, l08: A08, l09: A09, l10: A10, l11: A11};

const Pending: React.FC<{name: string}> = ({name}) => (
  <AbsoluteFill style={{background: '#06080f', color: '#F4F5F7', fontFamily: 'Geist, sans-serif', fontSize: 64, alignItems: 'center', justifyContent: 'center'}}>{name}</AbsoluteFill>
);

const Act: React.FC<{name: ActName; from: number}> = ({name, from}) => {
  const fr = useCurrentFrame();
  const fonts = useFonts(); // labels are drawn into canvases: wait for Geist
  const C = BUILT[name];
  if (!fonts) return null;
  const t = from / FPS + fr / FPS; // absolute seconds, so every cue() works inside the act
  return C ? <C t={t} fr={from + fr} /> : <Pending name={name} />;
};

export const Film: React.FC<{vo?: boolean}> = ({vo = true}) => (
  <AbsoluteFill style={{background: '#06080f'}}>
    {(Object.keys(ACTS) as ActName[]).map((name) => {
      const [a, b] = ACTS[name], from = Math.round(a * FPS), dur = Math.round(b * FPS) - from;
      return (
        <Sequence key={name} from={from} durationInFrames={dur} name={name}>
          <Act name={name} from={from} />
        </Sequence>
      );
    })}
    <Captions />
    {vo ? <Audio src={staticFile('soundtrack.wav')} /> : null}
  </AbsoluteFill>
);
