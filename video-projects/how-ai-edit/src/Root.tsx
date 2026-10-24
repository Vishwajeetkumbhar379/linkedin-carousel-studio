import React from 'react';
import {Composition} from 'remotion';
import {Smoke} from './smoke';
export const Root: React.FC = () => (
  <>
    <Composition id="Smoke" component={Smoke} durationInFrames={60} fps={30} width={1080} height={1920} />
  </>
);
