// Vish as a 2D character drawn in code, modelled on his mascot (brand/avatar/pack): long wavy brown hair, round
// tortoiseshell glasses, moustache + goatee, small hoop earrings, ivory blazer, burgundy shirt, necklace with a grey stone.
// Rigged for animation: expr (smile|laugh|surprised|worried|skeptical|neutral), blink 0..1, look -1..1, mouth (auto|o|a|flat),
// arm (none|point|chin|wave), tilt in degrees. Returns an <svg> string, viewBox 0 0 600 800.
(function () {
  const C = {skin: "#B87A50", skinD: "#9A6040", skinL: "#CF9468", hair: "#4A2A1A", hairL: "#7A4A2C", beard: "#2A1A12",
    blazer: "#EDE4D3", blazerD: "#CFC3AE", shirt: "#6A1F2B", shirtD: "#4E1520", chain: "#D2D2D2", stone: "#5C6670"};
  const brows = {smile: [-2, 0], laugh: [-6, 0], surprised: [-14, 0], worried: [-6, 10], skeptical: [-12, -4], neutral: [0, 0]};
  function mouth(e, m) {
    if (m === "o" || (m === "auto" && e === "surprised")) return `<ellipse cx="300" cy="370" rx="10" ry="13" fill="#4A1C1C"/>`;
    if (m === "a" || (m === "auto" && e === "laugh")) return `<path d="M274 360 Q300 398 326 360 Z" fill="#4A1C1C"/><path d="M279 361 Q300 368 321 361 L319 366 Q300 371 281 366 Z" fill="#F4EEE6"/>`;
    if (e === "worried") return `<path d="M282 370 Q300 360 318 370" stroke="#4A1C1C" stroke-width="5" fill="none" stroke-linecap="round"/>`;
    if (e === "skeptical") return `<path d="M282 366 Q302 372 320 360" stroke="#4A1C1C" stroke-width="5" fill="none" stroke-linecap="round"/>`;
    if (m === "flat" || e === "neutral") return `<path d="M284 366 L316 366" stroke="#4A1C1C" stroke-width="5" stroke-linecap="round"/>`;
    return `<path d="M278 362 Q300 378 322 362" stroke="#4A1C1C" stroke-width="5" fill="none" stroke-linecap="round"/>`;
  }
  function eye(cx, look, blink, e) {
    const ry = e === "surprised" ? 11 : e === "laugh" ? 3 : 9;
    if (blink > 0.6 || e === "laugh") return `<path d="M${cx - 13} 274 Q${cx} ${e === "laugh" ? 264 : 278} ${cx + 13} 274" stroke="#2A1A12" stroke-width="4.5" fill="none" stroke-linecap="round"/>`;
    const h = ry * (1 - blink);
    return `<ellipse cx="${cx}" cy="274" rx="13" ry="${h}" fill="#FBF7F1"/><circle cx="${cx + look * 5}" cy="275" r="${Math.min(7.5, h)}" fill="#3A2416"/>
      <circle cx="${cx + look * 5}" cy="275" r="${Math.min(3.6, h)}" fill="#120A06"/><circle cx="${cx + look * 5 + 2.5}" cy="272" r="2" fill="#fff"/>`;
  }
  function arm(a) {
    if (a === "point") return `<g><path d="M470 600 C500 560 520 520 540 500" stroke="${C.blazer}" stroke-width="66" stroke-linecap="round" fill="none"/>
      <g transform="translate(560,488) rotate(-20)"><rect x="-26" y="-22" width="44" height="44" rx="16" fill="${C.skin}"/><rect x="10" y="-20" width="46" height="13" rx="6.5" fill="${C.skin}"/><rect x="-14" y="-34" width="16" height="22" rx="8" fill="${C.skinD}"/></g></g>`;
    if (a === "present") return `<g><path d="M470 620 C506 590 526 560 540 540" stroke="${C.blazer}" stroke-width="66" stroke-linecap="round" fill="none"/>
      <g transform="translate(556,520) rotate(-30)"><ellipse cx="0" cy="0" rx="30" ry="24" fill="${C.skin}"/>${[-14, -4, 6, 16].map(y => `<rect x="14" y="${y - 5}" width="30" height="10" rx="5" fill="${C.skin}"/>`).join("")}</g></g>`;
    if (a === "chin") return `<g><path d="M440 640 C420 560 380 500 340 450" stroke="${C.blazer}" stroke-width="62" stroke-linecap="round" fill="none"/>
      <ellipse cx="322" cy="428" rx="30" ry="24" fill="${C.skin}"/><rect x="300" y="404" width="40" height="14" rx="7" fill="${C.skinD}"/></g>`;
    if (a === "wave") return `<g><path d="M150 570 C120 520 110 470 125 410" stroke="${C.blazer}" stroke-width="64" stroke-linecap="round" fill="none"/>
      <g transform="translate(128,370) rotate(-12)"><rect x="-28" y="-46" width="56" height="70" rx="22" fill="${C.skin}"/>${[-18, -6, 6, 18].map(x => `<rect x="${x - 5}" y="-70" width="10" height="34" rx="5" fill="${C.skin}"/>`).join("")}</g></g>`;
    return "";
  }
  window.vishChar = function ({expr = "smile", blink = 0, look = 0, mouth: m = "auto", arm: a = "none", tilt = 0} = {}) {
    const [by, bt] = brows[expr];
    return `<svg viewBox="0 0 600 800" xmlns="http://www.w3.org/2000/svg">
<defs>
 <radialGradient id="vf" cx=".45" cy=".4" r=".7"><stop offset="0" stop-color="${C.skinL}"/><stop offset=".7" stop-color="${C.skin}"/><stop offset="1" stop-color="${C.skinD}"/></radialGradient>
 <linearGradient id="vh" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${C.hairL}"/><stop offset=".5" stop-color="${C.hair}"/><stop offset="1" stop-color="#2E190F"/></linearGradient>
 <linearGradient id="vt" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3B1D10"/><stop offset=".3" stop-color="#8A4A22"/><stop offset=".55" stop-color="#4A2412"/><stop offset=".8" stop-color="#9A5A2A"/><stop offset="1" stop-color="#3B1D10"/></linearGradient>
 <linearGradient id="vb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6EFE3"/><stop offset="1" stop-color="${C.blazerD}"/></linearGradient>
</defs>
<g>
 <path d="M76 800 C80 604 118 506 248 462 L300 566 L352 462 C482 506 520 604 524 800 Z" fill="url(#vb)"/>
 <path d="M252 460 L300 566 L348 460 C330 450 270 450 252 460 Z" fill="${C.shirt}"/>
 <path d="M252 460 L232 516 L286 506 Z M348 460 L368 516 L314 506 Z" fill="${C.shirtD}"/>
 <path d="M248 462 L200 522 L240 548 L216 660 L300 566 Z M352 462 L400 522 L360 548 L384 660 L300 566 Z" fill="${C.blazerD}" opacity=".6"/>
 <path d="M248 462 L200 522 L240 548 L216 660 M352 462 L400 522 L360 548 L384 660" stroke="#BDB09A" stroke-width="2.5" fill="none"/>
 <circle cx="300" cy="690" r="8" fill="#B9AC94"/>
</g>
<g transform="rotate(${tilt} 300 440)">
 <path d="M300 76 C174 68 126 160 148 252 C138 304 150 348 178 376 C198 360 206 332 208 300 L212 252 L388 252 L392 300 C394 332 402 360 422 376 C450 348 462 304 452 252 C474 160 426 68 300 76 Z" fill="url(#vh)"/>
 <path d="M178 376 C164 384 150 380 146 368 M422 376 C436 384 450 380 454 368" stroke="${C.hair}" stroke-width="12" fill="none" stroke-linecap="round"/>
 <rect x="266" y="396" width="68" height="74" rx="22" fill="${C.skinD}"/>
 <path d="M272 462 Q300 520 328 462" stroke="${C.chain}" stroke-width="2.5" fill="none"/><ellipse cx="300" cy="520" rx="7.5" ry="10.5" fill="${C.stone}"/>
 <ellipse cx="208" cy="282" rx="15" ry="25" fill="${C.skinD}"/><ellipse cx="392" cy="282" rx="15" ry="25" fill="${C.skinD}"/>
 <circle cx="204" cy="310" r="7" stroke="#D6D6D6" stroke-width="2.5" fill="none"/><circle cx="396" cy="310" r="7" stroke="#D6D6D6" stroke-width="2.5" fill="none"/>
 <path d="M208 240 C206 302 214 352 238 386 C256 410 280 424 300 426 C320 424 344 410 362 386 C386 352 394 302 392 240 C390 166 210 166 208 240 Z" fill="url(#vf)"/>
 <path d="M228 360 C246 404 276 424 300 426 C324 424 354 404 372 360" stroke="${C.beard}" stroke-width="14" fill="none" opacity=".12"/>
 <path d="M298 290 C294 316 288 328 294 336 C300 341 310 339 313 332" stroke="${C.skinD}" stroke-width="4" fill="none" stroke-linecap="round"/>
 ${eye(260, look, blink, expr)}${eye(340, look, blink, expr)}
 <path d="M230 ${244 + by} Q258 ${228 + by + bt} 291 ${238 + by}" stroke="${C.beard}" stroke-width="10" fill="none" stroke-linecap="round"/>
 <path d="M370 ${244 + by + (expr === "skeptical" ? 8 : 0)} Q342 ${228 + by + bt + (expr === "skeptical" ? 10 : 0)} 309 ${238 + by}" stroke="${C.beard}" stroke-width="10" fill="none" stroke-linecap="round"/>
 <g stroke="url(#vt)" stroke-width="7" fill="rgba(255,255,255,.06)"><rect x="224" y="250" width="70" height="58" rx="28"/><rect x="306" y="250" width="70" height="58" rx="28"/></g>
 <path d="M294 268 Q300 261 306 268 M224 266 L210 262 M376 266 L390 262" stroke="url(#vt)" stroke-width="6" fill="none"/>
 <path d="M262 356 C280 342 320 342 338 356 C332 366 322 366 314 360 C308 355 292 355 286 360 C278 366 268 366 262 356 Z" fill="${C.beard}"/>
 ${mouth(expr, m)}
 <path d="M276 390 C288 382 312 382 324 390 C328 414 316 436 300 442 C284 436 272 414 276 390 Z" fill="${C.beard}"/>
 <path d="M206 250 C190 160 240 98 312 96 C384 96 420 150 404 238 C396 200 380 176 352 164 C362 186 360 204 352 214 C330 176 286 160 252 180 C230 194 214 220 206 250 Z" fill="url(#vh)"/>
 <path d="M246 132 C278 114 326 114 360 132 M226 176 C250 150 288 142 318 150 M336 168 C364 178 384 202 394 230" stroke="${C.hairL}" stroke-width="6" fill="none" stroke-linecap="round" opacity=".75"/>
 <path d="M166 262 C160 306 170 344 192 370 M434 262 C440 306 430 344 408 370" stroke="${C.hairL}" stroke-width="6" fill="none" stroke-linecap="round" opacity=".5"/>
</g>
${arm(a)}
</svg>`;
  };
})();
