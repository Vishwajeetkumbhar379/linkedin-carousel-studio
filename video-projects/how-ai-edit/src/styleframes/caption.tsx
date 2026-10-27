// Caption in the film's system: 2 to 4 words, white, heavy, one key word in an amber pill.
// Sits at 58 to 66% of the height (inside Instagram's safe box), drawn outside the finish pass.
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {GEIST, loadFonts} from './fonts';

loadFonts();
const fontFamily = GEIST;

export const Caption: React.FC<{words: string[]; pill: number; top?: number; shadow?: boolean; pillColor?: string}> = ({words, pill, top = 1140, shadow = true, pillColor = '#E7A15A'}) => (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 22, fontFamily, fontWeight: 800, fontSize: 92, letterSpacing: -2.5, lineHeight: 1}}>
      {words.map((w, i) => (
        <span key={i} style={i === pill
          ? {background: pillColor, color: '#14161B', padding: '10px 26px 16px', borderRadius: 22, boxShadow: '0 10px 40px rgba(231,161,90,0.35)'}
          : {color: '#F4F5F7', padding: '10px 0 16px', textShadow: shadow ? '0 4px 30px rgba(0,0,0,0.65)' : undefined}}>
          {w}
        </span>
      ))}
    </div>
  </AbsoluteFill>
);
