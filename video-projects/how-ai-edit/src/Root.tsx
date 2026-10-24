import React from 'react';
import {Composition} from 'remotion';
import {Smoke} from './smoke';
import {LuminousFrame} from './styleframes/luminous';
import {RealisticFrame} from './styleframes/realistic';
import {FlatFrame} from './styleframes/flat';
export const Root: React.FC = () => (
  <>
    <Composition id="Smoke" component={Smoke} durationInFrames={60} fps={30} width={1080} height={1920} />
    {/* style frames of beat 1: the whole beat runs over 120 frames, so any frame is a still and the run is an animatic */}
    <Composition id="SF-Luminous" component={LuminousFrame} durationInFrames={120} fps={30} width={1080} height={1920} />
    <Composition id="SF-Realistic" component={RealisticFrame} durationInFrames={120} fps={30} width={1080} height={1920} />
    <Composition id="SF-Flat" component={FlatFrame} durationInFrames={120} fps={30} width={1080} height={1920} />
  </>
);
