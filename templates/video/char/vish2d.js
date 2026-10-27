// Vish, 2D Disney-style lead drawn fully in code (CONTENT-OS "nose rule": small refined nose, fair warm skin, bright eyes,
// smooth skin; facial hair = cheek stubble + neat moustache + goatee, never a full beard). Every part is a parameter:
//   vish2d({expr, mouth, blink, lookX, lookY, browL, browR, tilt, nod, outfit})
//   expr: smile | laugh | surprised | skeptical | worried | neutral   mouth: auto | rest | A | E | O | M (visemes for lip-sync)
//   blink 0..1, lookX/lookY -1..1, browL/browR extra raise in px, tilt degrees, nod px, outfit: tee | blazer
(function () {
  const K = {skin: "#EBC29C", skinL: "#F6D6B6", skinS: "#D4A27E", line: "#9A6448", hair: "#231812", hairM: "#3A281D", hairH: "#6A4A36",
    lip: "#B9705C", mouthIn: "#5A2420", teeth: "#FBF6EF", iris1: "#7A4E2E", iris2: "#2E1A0E", lid: "#22150E"};
  const EX = {
    smile: {bl: 0, br: 0, eh: 1, mouth: "smile"}, laugh: {bl: -4, br: -4, eh: 0.35, mouth: "A"},
    surprised: {bl: -12, br: -12, eh: 1.18, mouth: "O"}, skeptical: {bl: 4, br: -12, eh: 0.9, mouth: "smirk"},
    worried: {bl: -6, br: -6, eh: 1, mouth: "worried", tilt: 1}, neutral: {bl: 0, br: 0, eh: 1, mouth: "rest"}};
  const P = (pts) => pts; // readability

  function eye(cx, cy, side, o) {
    const s = side; // -1 left eye (outer corner on the left), 1 right eye
    const h = Math.max(0.02, o.eh * (1 - o.blink));
    const up = 17 * h, dn = 11 * h;
    const almond = `M${cx - 24 * s} ${cy + 1} C${cx - 13 * s} ${cy - up} ${cx + 13 * s} ${cy - up} ${cx + 24 * s} ${cy - 3} C${cx + 14 * s} ${cy + dn} ${cx - 14 * s} ${cy + dn} ${cx - 24 * s} ${cy + 1} Z`;
    const id = `e${side < 0 ? "l" : "r"}${Math.round(Math.random() * 1e6)}`;
    const ix = cx + o.lookX * 7, iy = cy + o.lookY * 4 - 1;
    const lidPath = `M${cx - 27 * s} ${cy + 2} C${cx - 14 * s} ${cy - up - 3} ${cx + 14 * s} ${cy - up - 3} ${cx + 27 * s} ${cy - 4}`;
    if (h < 0.15) return `<path d="M${cx - 25 * s} ${cy} C${cx - 10 * s} ${cy + 6} ${cx + 10 * s} ${cy + 6} ${cx + 25 * s} ${cy - 2}" stroke="${K.lid}" stroke-width="4.5" fill="none" stroke-linecap="round"/>`;
    return `<clipPath id="${id}"><path d="${almond}"/></clipPath>
      <path d="${almond}" fill="#FFFDF9"/>
      <g clip-path="url(#${id})"><circle cx="${ix}" cy="${iy}" r="11.5" fill="url(#iris)"/><circle cx="${ix}" cy="${iy}" r="5.2" fill="#120A06"/>
        <circle cx="${ix + 3.5}" cy="${iy - 4}" r="3.4" fill="#fff"/><circle cx="${ix - 3.5}" cy="${iy + 3.5}" r="1.5" fill="#fff" opacity=".8"/>
        <path d="M${cx - 30} ${cy - up - 2} L${cx + 30} ${cy - up - 2} L${cx + 30} ${cy - up + 5} L${cx - 30} ${cy - up + 5} Z" fill="${K.skinS}" opacity=".25"/></g>
      <path d="${lidPath}" stroke="${K.lid}" stroke-width="4.8" fill="none" stroke-linecap="round"/>
      <path d="M${cx + 24 * s} ${cy - 4} l${6 * s} -4" stroke="${K.lid}" stroke-width="3.2" stroke-linecap="round"/>
      <path d="M${cx - 16 * s} ${cy + dn + 1} C${cx - 5 * s} ${cy + dn + 4} ${cx + 8 * s} ${cy + dn + 3} ${cx + 18 * s} ${cy + dn - 1}" stroke="${K.skinS}" stroke-width="1.6" fill="none" opacity=".7"/>`;
  }

  function brow(side, raise) {
    const y = 252 - raise, s = side, x0 = 300 + 74 * s;
    return `<path d="M${x0} ${y + 16} C${x0 - 12 * s} ${y - 2} ${x0 - 42 * s} ${y - 8} ${x0 - 60 * s} ${y + 1} C${x0 - 62 * s} ${y + 6} ${x0 - 60 * s} ${y + 9} ${x0 - 55 * s} ${y + 9}
      C${x0 - 40 * s} ${y + 5} ${x0 - 18 * s} ${y + 8} ${x0 - 4 * s} ${y + 20} Z" fill="${K.hair}"/>`;
  }

  function mouth(kind) {
    const y = 372;
    switch (kind) {
      case "A": return `<path d="M272 ${y - 2} C286 ${y + 30} 314 ${y + 30} 328 ${y - 2} C314 ${y + 4} 286 ${y + 4} 272 ${y - 2} Z" fill="${K.mouthIn}"/>
        <path d="M276 ${y} C288 ${y + 5} 312 ${y + 5} 324 ${y} L322 ${y + 7} C310 ${y + 11} 290 ${y + 11} 278 ${y + 7} Z" fill="${K.teeth}"/>
        <path d="M288 ${y + 19} C296 ${y + 23} 304 ${y + 23} 312 ${y + 19}" stroke="#C0606A" stroke-width="5" stroke-linecap="round" opacity=".7"/>`;
      case "E": return `<path d="M274 ${y} C288 ${y + 14} 312 ${y + 14} 326 ${y} C312 ${y + 4} 288 ${y + 4} 274 ${y} Z" fill="${K.mouthIn}"/>
        <path d="M278 ${y + 1} C290 ${y + 5} 310 ${y + 5} 322 ${y + 1} L320 ${y + 5} C308 ${y + 8} 292 ${y + 8} 280 ${y + 5} Z" fill="${K.teeth}"/>`;
      case "O": return `<ellipse cx="300" cy="${y + 6}" rx="10" ry="13" fill="${K.mouthIn}"/><path d="M292 ${y + 15} C297 ${y + 19} 303 ${y + 19} 308 ${y + 15}" stroke="#C0606A" stroke-width="3" opacity=".6"/>`;
      case "M": return `<path d="M282 ${y + 2} C292 ${y + 4} 308 ${y + 4} 318 ${y + 2}" stroke="${K.lip}" stroke-width="3.5" stroke-linecap="round" fill="none"/>`;
      case "smirk": return `<path d="M282 ${y + 3} C294 ${y + 8} 310 ${y + 6} 324 ${y - 4}" stroke="${K.lip}" stroke-width="3.5" stroke-linecap="round" fill="none"/>`;
      case "worried": return `<path d="M282 ${y + 6} C292 ${y} 308 ${y} 318 ${y + 6}" stroke="${K.lip}" stroke-width="3.5" stroke-linecap="round" fill="none"/>`;
      case "rest": return `<path d="M282 ${y + 2} C294 ${y + 6} 306 ${y + 6} 318 ${y + 2}" stroke="${K.lip}" stroke-width="3.5" stroke-linecap="round" fill="none"/>`;
      default: return `<path d="M274 ${y - 2} C288 ${y + 14} 312 ${y + 14} 326 ${y - 2}" stroke="${K.lip}" stroke-width="3.8" stroke-linecap="round" fill="none"/>
        <path d="M290 ${y + 14} C296 ${y + 17} 304 ${y + 17} 310 ${y + 14}" stroke="${K.skinS}" stroke-width="2.2" stroke-linecap="round" fill="none"/>`;
    }
  }

  window.vish2d = function (opt = {}) {
    const o = Object.assign({expr: "smile", mouth: "auto", blink: 0, lookX: 0, lookY: 0, browL: 0, browR: 0, tilt: 0, nod: 0, outfit: "tee"}, opt);
    const e = EX[o.expr] || EX.smile;
    o.eh = e.eh;
    const m = o.mouth === "auto" ? e.mouth : o.mouth;
    const tilt = o.tilt + (e.tilt || 0);
    const body = o.outfit === "blazer"
      ? `<path d="M96 800 C100 640 140 540 262 492 L300 560 L338 492 C460 540 500 640 504 800 Z" fill="#EFE7D9"/>
         <path d="M262 492 L300 560 L338 492 C322 484 278 484 262 492 Z" fill="#6A1F2B"/>
         <path d="M262 492 L214 548 L252 572 L232 690 L300 562 Z M338 492 L386 548 L348 572 L368 690 L300 562 Z" fill="#D9CDB8"/>`
      : `<path d="M110 800 L116 650 C120 600 150 572 214 556 C244 548 260 530 268 508 C286 520 314 520 332 508 C340 530 356 548 386 556 C450 572 480 600 484 650 L490 800 Z" fill="#1E1E24"/>
         <path d="M258 494 C278 520 322 520 342 494" stroke="#3A3A44" stroke-width="5" fill="none"/>
         <path d="M170 720 C172 670 178 630 190 606 M430 720 C428 670 422 630 410 606" stroke="#2C2C34" stroke-width="4" fill="none"/>`;
    return `<svg viewBox="0 0 600 800" xmlns="http://www.w3.org/2000/svg">
<defs>
 <radialGradient id="face" cx=".46" cy=".42" r=".66"><stop offset="0" stop-color="${K.skinL}"/><stop offset=".62" stop-color="${K.skin}"/><stop offset="1" stop-color="${K.skinS}"/></radialGradient>
 <radialGradient id="iris" cx=".45" cy=".4" r=".6"><stop offset="0" stop-color="${K.iris1}"/><stop offset="1" stop-color="${K.iris2}"/></radialGradient>
 <linearGradient id="hair" x1="0" y1="0" x2=".3" y2="1"><stop offset="0" stop-color="${K.hairM}"/><stop offset="1" stop-color="${K.hair}"/></linearGradient>
 <pattern id="stub" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.3" r=".8" fill="#2B1D16"/><circle cx="3.6" cy="3.4" r=".7" fill="#2B1D16"/></pattern>
 <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
 <radialGradient id="jawshade" cx=".5" cy=".2" r=".8"><stop offset="0" stop-color="#3A2A22" stop-opacity="0"/><stop offset="1" stop-color="#3A2A22" stop-opacity=".22"/></radialGradient>
</defs>
${body}
<path d="M300 556 C280 556 272 536 270 514" stroke="#D8D8D8" stroke-width="2.6" fill="none" stroke-dasharray="5 2"/>
<path d="M300 556 C320 556 328 536 330 514" stroke="#D8D8D8" stroke-width="2.6" fill="none" stroke-dasharray="5 2"/>
<g transform="translate(0 ${o.nod}) rotate(${tilt} 300 470) translate(300 500) scale(1.26) translate(-300 -470)">
 <path d="M300 92 C262 86 226 98 204 124 C180 132 170 160 174 186 C160 206 162 236 172 254 C164 280 170 312 186 330 C184 350 196 366 212 370 L218 300 L382 300 L388 370 C404 366 416 350 414 330 C430 312 436 280 428 254 C438 236 440 206 426 186 C430 160 420 132 396 124 C374 98 338 86 300 92 Z" fill="url(#hair)"/>
 <path d="M268 400 L268 488 C286 502 314 502 332 488 L332 400 Z" fill="${K.skinS}"/>
 <path d="M264 432 C284 452 316 452 336 432 L336 410 L264 410 Z" fill="#B78466" opacity=".45"/>
 <path d="M206 282 C188 270 180 300 188 318 C194 332 206 332 210 322 Z" fill="${K.skin}" stroke="${K.line}" stroke-width="2"/>
 <path d="M394 282 C412 270 420 300 412 318 C406 332 394 332 390 322 Z" fill="${K.skin}" stroke="${K.line}" stroke-width="2"/>
 <circle cx="192" cy="332" r="6" stroke="#E2E2E2" stroke-width="2.4" fill="none"/><circle cx="408" cy="332" r="6" stroke="#E2E2E2" stroke-width="2.4" fill="none"/>
 <path d="M300 168 C360 168 398 210 400 270 C402 318 392 352 374 380 C356 406 330 428 300 432 C270 428 244 406 226 380 C208 352 198 318 200 270 C202 210 240 168 300 168 Z" fill="url(#face)" stroke="${K.line}" stroke-width="2.5"/>
 <path d="M206 318 C214 368 248 412 300 432 C352 412 386 368 394 318 C378 352 352 366 326 362 L274 362 C248 366 222 352 206 318 Z" fill="url(#stub)" opacity=".34"/>
 <path d="M300 168 C360 168 398 210 400 270 C402 318 392 352 374 380 C356 406 330 428 300 432 C270 428 244 406 226 380 C208 352 198 318 200 270 C202 210 240 168 300 168 Z" fill="url(#jawshade)"/>
 <ellipse cx="236" cy="338" rx="22" ry="11" fill="#F0A090" opacity=".14" filter="url(#soft)"/><ellipse cx="364" cy="338" rx="22" ry="11" fill="#F0A090" opacity=".14" filter="url(#soft)"/>
 ${eye(254, 296, -1, o)}${eye(346, 296, 1, o)}
 ${brow(-1, e.bl + o.browL)}${brow(1, e.br + o.browR)}
 <path d="M302 304 C300 320 296 332 297 338 C299 343 305 344 309 340" stroke="${K.skinS}" stroke-width="3" fill="none" stroke-linecap="round"/>
 <ellipse cx="296" cy="318" rx="3" ry="9" fill="#FFF3E6" opacity=".45"/>
 <path d="M266 368 C278 350 294 350 300 356 C306 350 322 350 334 368 C324 364 312 362 300 366 C288 362 276 364 266 368 Z" fill="${K.hair}"/>
 ${mouth(m)}
 <path d="M296 389 L304 389 L302 398 L298 398 Z" fill="${K.hair}" opacity=".85"/>
 <path d="M282 402 C292 397 308 397 318 402 C320 416 311 428 300 432 C289 428 280 416 282 402 Z" fill="${K.hair}" opacity=".9"/>
 <path d="M298 104 C250 100 208 128 198 184 C192 216 196 246 206 270 C212 248 222 230 236 218 C250 200 266 186 280 180 C290 176 296 168 298 156 Z" fill="url(#hair)"/>
 <path d="M302 104 C350 100 392 128 402 184 C408 216 404 246 394 270 C388 248 378 230 364 218 C350 200 334 186 320 180 C310 176 304 168 302 156 Z" fill="url(#hair)"/>

 <path d="M204 232 C186 262 184 300 194 336 C186 344 182 354 186 362 C196 352 206 336 210 316 C212 300 214 290 216 282 Z M396 232 C414 262 416 300 406 336 C414 344 418 354 414 362 C404 352 394 336 390 316 C388 300 386 290 384 282 Z" fill="${K.hair}"/>
 <path d="M292 112 C258 116 226 146 214 198 M296 118 C278 136 262 160 246 196 M306 112 C340 116 372 146 386 198 M304 118 C322 136 338 160 354 196 M228 230 C220 244 218 258 220 270 M372 230 C380 244 382 258 380 270 M232 112 C214 128 200 150 194 176 M368 112 C386 128 400 150 406 176" stroke="${K.hairH}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".75"/>
</g>
</svg>`;
  };
})();
