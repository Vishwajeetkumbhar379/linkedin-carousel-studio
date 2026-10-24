// Geist from public/fonts (the renderer can't reach Google Fonts from this machine).
import {useEffect, useState} from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

const faces: [string, string, number][] = [
  ['Geist', 'geist-sans-latin-500-normal.woff2', 500], ['Geist', 'geist-sans-latin-600-normal.woff2', 600],
  ['Geist', 'geist-sans-latin-700-normal.woff2', 700], ['Geist', 'geist-sans-latin-800-normal.woff2', 800],
  ['Geist Mono', 'geist-mono-latin-500-normal.woff2', 500],
];
let loading: Promise<void> | null = null;
export const fontsLoaded = () => {
  if (!loading) loading = Promise.all(faces.map(([fam, file, w]) => new FontFace(fam, `url(${staticFile(`fonts/${file}`)})`, {weight: String(w)}).load().then((f) => { document.fonts.add(f); }))).then(() => undefined);
  return loading;
};
export const loadFonts = () => {
  if (typeof document === 'undefined') return;
  const h = delayRender('Geist');
  fontsLoaded().then(() => continueRender(h));
};
// For anything that draws text into a canvas: false until Geist is ready, holding the frame meanwhile.
export const useFonts = () => {
  const [ready, set] = useState(false);
  const [h] = useState(() => delayRender('fonts for canvas text'));
  useEffect(() => { fontsLoaded().then(() => { set(true); continueRender(h); }); }, [h]);
  return ready;
};
export const GEIST = 'Geist, system-ui, sans-serif';
export const GEIST_MONO = '"Geist Mono", ui-monospace, monospace';
