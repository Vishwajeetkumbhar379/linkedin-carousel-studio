// Geist from public/fonts (the renderer can't reach Google Fonts from this machine).
import {continueRender, delayRender, staticFile} from 'remotion';

const faces: [string, string, number][] = [
  ['Geist', 'geist-sans-latin-500-normal.woff2', 500], ['Geist', 'geist-sans-latin-600-normal.woff2', 600],
  ['Geist', 'geist-sans-latin-700-normal.woff2', 700], ['Geist', 'geist-sans-latin-800-normal.woff2', 800],
  ['Geist Mono', 'geist-mono-latin-500-normal.woff2', 500],
];
let loaded = false;
export const loadFonts = () => {
  if (loaded || typeof document === 'undefined') return;
  loaded = true;
  const h = delayRender('Geist');
  Promise.all(faces.map(([fam, file, w]) => new FontFace(fam, `url(${staticFile(`fonts/${file}`)})`, {weight: String(w)}).load().then((f) => document.fonts.add(f))))
    .then(() => continueRender(h));
};
export const GEIST = 'Geist, system-ui, sans-serif';
export const GEIST_MONO = '"Geist Mono", ui-monospace, monospace';
