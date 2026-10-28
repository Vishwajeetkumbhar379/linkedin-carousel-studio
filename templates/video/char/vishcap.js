// Vish in 2D, drawn fully in code (Vish, 28 Oct: "create a 2D mascot in code so you control the whole motion of the face;
// make it wear the cap, like the video where I'm in a hoodie and a cap and say let's get a haircut; my nose shouldn't look
// big, I should look handsome"). Reference: IMG_8731 (black cap, grey hoodie, white tee under it, black joggers, long dark
// hair falling from under the cap, small silver hoops, thin moustache, chin beard). Nose rule: small, slim, never the focus.
//
//   VishCap.draw(g, {x, y, s, expr, pose, talk, blink, look, turn, tilt, nod, walk, dir, t})
//     x, y   where his feet stand on the canvas (px); s = px per rig unit (he is about 1700 units tall)
//     expr   smile | laugh | thought | surprised | skeptical | focused | concerned | pleased | wink | neutral
//     pose   rest | explain | point_up | point_left | point_right | present | think | arms | thumbs | wave
//     talk   {o, w, r, f} mouth shape from the voice (open, wide, round, lower lip under the teeth) or null
//     blink  0..1, look [x, y] in -1..1, turn -1..1 (head yaw, + = towards screen right), tilt / nod in degrees
//     walk   stride phase in radians (null = standing), dir = 1 walking right, -1 walking left
(function () {
  const C = {
    skin: "#DCA57C", skinL: "#E8B993", skinS: "#C18A64", skinD: "#A06B4B", line: "#7E4F36",
    hair: "#17110E", hairH: "#3A2B22", lash: "#1A110C", brow: "#1C1410",
    cap: "#1B1C20", capH: "#34363D", capS: "#0F1013", capT: "#F2EEE6",
    hood: "#BDBCB8", hoodL: "#CDCCC8", hoodS: "#A3A29E", hoodD: "#898884", hoodLine: "#7D7C78",
    tee: "#F5F3EF", teeS: "#DEDBD4", pants: "#1F2024", pantsH: "#2E3036", pantsS: "#141518",
    shoe: "#F4F2EE", shoeS: "#D9D5CD", sole: "#C9C4BA",
    white: "#FFFCF7", iris: "#5B3A23", irisD: "#1F130B", mouthIn: "#3E1514", tongue: "#B95A55", teeth: "#FBF8F2",
    lip: "#B07560", lipD: "#7E4636", silver: "#E3E6EA", silverS: "#A9AEB5", string: "#ECEAE4"};
  const R = Math.PI / 180, cl = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v)), lerp = (a, b, k) => a + (b - a) * k;

  // ----------------------------------------------------------------------------------------------------- expressions
  // b: brow raise (L, R), bi: inner end up (L, R), e: eye open (L, R), sq: cheek squint, look, m: resting mouth, tilt
  const EX = {
    neutral: {b: [0, 0], bi: [0, 0], e: [1, 1], sq: 0, m: {o: 0, w: 0.45, s: 0.2, r: 0, a: 0}, tilt: 0},
    smile: {b: [1.5, 1.5], bi: [0, 0], e: [0.88, 0.88], sq: 0.45, m: {o: 0.3, w: 0.95, s: 1, r: 0, a: 0}, tilt: -2},
    laugh: {b: [4, 4], bi: [1, 1], e: [0.18, 0.18], happy: [1, 1], sq: 1, m: {o: 0.7, w: 1, s: 1, r: 0, a: 0}, tilt: -5},
    thought: {b: [6, -1], bi: [2, 0], e: [0.92, 0.92], sq: 0.1, look: [-0.55, -0.7], m: {o: 0, w: 0.35, s: 0.05, r: 0.25, a: -0.7}, tilt: 4},
    surprised: {b: [11, 11], bi: [2, 2], e: [1.22, 1.22], sq: 0, m: {o: 0.5, w: 0.15, s: 0, r: 1, a: 0}, tilt: 0},
    skeptical: {b: [-3, 9], bi: [-3, 1], e: [0.72, 0.96], sq: 0.15, look: [0.25, 0], m: {o: 0, w: 0.6, s: 0.45, r: 0, a: 0.9}, tilt: 3},
    focused: {b: [-3, -3], bi: [-3, -3], e: [0.78, 0.78], sq: 0.2, m: {o: 0, w: 0.45, s: 0.1, r: 0, a: 0}, tilt: 0},
    concerned: {b: [3, 3], bi: [7, 7], e: [1, 1], sq: 0, m: {o: 0, w: 0.45, s: -0.55, r: 0, a: 0}, tilt: 3},
    pleased: {b: [2, 2], bi: [1, 1], e: [0.2, 0.2], happy: [1, 1], sq: 0.9, m: {o: 0.26, w: 0.9, s: 1, r: 0, a: 0}, tilt: -5},
    wink: {b: [3, -2], bi: [0, 0], e: [1, 0.12], happy: [0, 1], sq: 0.5, m: {o: 0.22, w: 0.85, s: 1, r: 0, a: 0.5}, tilt: -4}};

  // ----------------------------------------------------------------------------------------------------- poses
  // each arm: u = upper arm angle (deg, canvas: 0 right, 90 down), ul = length scale (foreshortening), f / fl = forearm,
  // h = hand (relax | open | point | thumb | fist | palm), ha = hand angle (default: along the forearm), fl2 = mirror the hand
  const POSE = {
    rest: {L: {u: 96, f: 92, h: "relax"}, R: {u: 84, f: 88, h: "relax"}},
    explain: {L: {u: 105, ul: 0.8, f: 160, fl: 0.8, h: "open", ha: 190}, R: {u: 75, ul: 0.8, f: 20, fl: 0.8, h: "open", ha: -10}, sway: 1},
    point_up: {L: {u: 96, f: 92, h: "relax"}, R: {u: 25, ul: 0.85, f: -82, h: "point", ha: -72}, turn: 0.15, look: [0.3, -0.6]},
    point_left: {L: {u: 172, f: 178, h: "point"}, R: {u: 83, f: 87, h: "relax"}, turn: -0.35, look: [-0.8, 0]},
    point_right: {L: {u: 97, f: 93, h: "relax"}, R: {u: 8, f: 2, h: "point"}, turn: 0.35, look: [0.8, 0]},
    present: {L: {u: 97, f: 93, h: "relax"}, R: {u: 40, ul: 0.9, f: -12, h: "open", ha: -30}, turn: 0.3, look: [0.7, 0.1]},
    think: {L: {u: 70, ul: 0.8, f: 2, h: "fist"}, R: {u: 118, ul: 0.62, f: -110, fl: 0.92, h: "chin"}, expr: "thought"},
    arms: {L: {u: 80, ul: 0.72, f: -2, fl: 1.1, h: "tuck"}, R: {u: 100, ul: 0.72, f: 182, fl: 1.1, h: "fist", ha: 150}, order: ["L", "R"]},
    thumbs: {L: {u: 96, f: 92, h: "relax"}, R: {u: 100, ul: 0.7, f: -50, fl: 0.9, h: "thumb", ha: 0}},
    wave: {L: {u: 97, f: 93, h: "relax"}, R: {u: 18, ul: 0.9, f: -80, h: "palm"}, wave: 1}};

  // ----------------------------------------------------------------------------------------------------- helpers
  function P(g, d) { return new Path2D(d); }
  function fillStroke(g, path, fill, stroke, lw) { g.fillStyle = fill; g.fill(path); if (stroke) { g.strokeStyle = stroke; g.lineWidth = lw; g.stroke(path); } }
  function cap(g, pts, w, col, outline, ow) {  // a thick rounded polyline (sleeves, legs, fingers)
    g.lineCap = "round"; g.lineJoin = "round";
    const line = () => { g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); };
    if (outline) { line(); g.strokeStyle = outline; g.lineWidth = w + ow * 2; g.stroke(); }
    line(); g.strokeStyle = col; g.lineWidth = w; g.stroke();
  }
  const pt = (o, a, l) => [o[0] + Math.cos(a * R) * l, o[1] + Math.sin(a * R) * l];

  // ----------------------------------------------------------------------------------------------------- the head
  // head space: the eye line's centre is (0, 0); the face is about 190 wide; the chin is at y 140; the cap top at -188
  function head(g, o) {
    const E = o.E, tu = o.turn, jaw = o.jaw;
    // horizontal yaw: features slide towards the turn; the side facing away compresses
    const FX = (x) => x * (1 - 0.1 * Math.abs(tu)) + tu * 20;
    const OX = (x) => (x * tu > 0 ? x * (1 - 0.13 * Math.abs(tu)) : x * (1 + 0.03 * Math.abs(tu))) + tu * 5;
    const JY = (y) => y + jaw * cl((y - 50) / 90);  // the jaw drops with an open mouth

    // ---- his long hair, behind: dark waves from under the cap to the jaw, tucked behind the ears
    for (const sd of [-1, 1]) {
      const X = (x) => OX(sd * x);
      const hp = new Path2D();
      hp.moveTo(X(70), -76);
      hp.bezierCurveTo(X(100), -74, X(114), -44, X(110), -12);
      hp.bezierCurveTo(X(106), 14, X(120), 30, X(116), 56);
      hp.bezierCurveTo(X(112), 80, X(124), 92, X(114), 110);
      hp.bezierCurveTo(X(108), 120, X(98), 118, X(100), 108);
      hp.bezierCurveTo(X(94), 122, X(80), 124, X(78), 112);
      hp.bezierCurveTo(X(70), 116, X(66), 104, X(72), 96);
      hp.bezierCurveTo(X(84), 60, X(86), 20, X(82), -20);
      hp.closePath();
      g.fillStyle = C.hair; g.fill(hp);
      g.save(); g.clip(hp); g.strokeStyle = C.hairH; g.lineWidth = 2.4; g.lineCap = "round";
      g.beginPath(); g.moveTo(X(98), -46); g.bezierCurveTo(X(106), -20, X(96), 6, X(104), 30); g.bezierCurveTo(X(112), 54, X(100), 76, X(106), 100); g.stroke();
      g.beginPath(); g.moveTo(X(108), 20); g.bezierCurveTo(X(116), 44, X(106), 70, X(112), 92); g.stroke();
      g.restore();
    }
    // ---- ears (+ small silver hoops)
    for (const sd of [-1, 1]) {
      const away = sd * tu > 0 ? Math.abs(tu) : 0, ex = OX(sd * 89) - sd * away * 10;
      g.save(); g.translate(ex, 2); g.scale(sd * (1 - away * 0.6), 1);
      fillStroke(g, P(g, "M0 -20 C14 -32 25 -20 23 -3 C22 13 17 29 6 38 C2 40 -2 38 -2 34 Z"), C.skin, C.line, 2);
      g.strokeStyle = C.skinD; g.lineWidth = 2; g.beginPath(); g.moveTo(5, -16); g.bezierCurveTo(15, -19, 17, -5, 13, 8); g.stroke();
      g.restore();
      if (away < 0.5) { g.strokeStyle = C.silver; g.lineWidth = 2.4; g.beginPath(); g.arc(ex + sd * 8, 45, 5.5, -0.3 * Math.PI, 1.3 * Math.PI); g.stroke(); }
    }
    // ---- the face: high cheekbones, a tapered jaw, a defined chin
    const fo = new Path2D();
    const pts = [[-87, -86], [-90, -40, -93, -2, -91, 26], [-89, 60, -78, 90, -60, 110], [-44, 128, -26, 140, -11, 143], [11, 143], [26, 140, 44, 128, 60, 110],
      [78, 90, 89, 60, 91, 26], [93, -2, 90, -40, 87, -86]];
    fo.moveTo(OX(pts[0][0]), pts[0][1]);
    for (const p of pts.slice(1)) {
      if (p.length === 2) fo.lineTo(OX(p[0]), JY(p[1])); else fo.bezierCurveTo(OX(p[0]), JY(p[1]), OX(p[2]), JY(p[3]), OX(p[4]), JY(p[5]));
    }
    fo.closePath();
    const fg = g.createLinearGradient(OX(-96), 0, OX(96), 0);
    fg.addColorStop(0, C.skinS); fg.addColorStop(0.18, C.skin); fg.addColorStop(0.45, C.skinL); fg.addColorStop(0.75, C.skin); fg.addColorStop(1, C.skinS);
    g.fillStyle = fg; g.fill(fo);
    g.save(); g.clip(fo);
    // stubble on the jaw and around the mouth, very light
    g.fillStyle = "rgba(42,26,18,.08)";
    g.beginPath(); g.moveTo(OX(-96), JY(50)); g.bezierCurveTo(OX(-84), JY(116), OX(-34), JY(148), FX(0), JY(148)); g.bezierCurveTo(OX(34), JY(148), OX(84), JY(116), OX(96), JY(50));
    g.bezierCurveTo(OX(80), JY(96), FX(46), JY(104), FX(0), JY(100)); g.bezierCurveTo(FX(-46), JY(104), OX(-80), JY(96), OX(-96), JY(50)); g.fill();
    // the cap's shadow on the forehead and the eye sockets
    const sh = g.createLinearGradient(0, -74, 0, -6); sh.addColorStop(0, "rgba(46,24,14,.6)"); sh.addColorStop(1, "rgba(46,24,14,0)");
    g.fillStyle = sh; g.fillRect(-130, -96, 260, 92);
    g.fillStyle = "rgba(120,70,44,.06)";
    for (const sd of [-1, 1]) { g.beginPath(); g.ellipse(FX(sd * 40), -2, 30, 18, 0, 0, Math.PI * 2); g.fill(); }
    // warm cheeks and a light on the cheekbones
    for (const sd of [-1, 1]) {
      g.fillStyle = "rgba(214,118,92,.05)"; g.beginPath(); g.ellipse(FX(sd * 54), 46, 20, 10, 0, 0, Math.PI * 2); g.fill();
      g.fillStyle = "rgba(255,226,196,.12)"; g.beginPath(); g.ellipse(FX(sd * 58), 30, 14, 6, sd * -0.3, 0, Math.PI * 2); g.fill();
    }
    g.restore();
    g.strokeStyle = C.line; g.lineWidth = 2.2; g.stroke(fo);
    // temple hair in front of the ears, under the cap
    for (const sd of [-1, 1]) {
      g.fillStyle = C.hair; g.beginPath(); g.moveTo(OX(sd * 90), -82); g.bezierCurveTo(OX(sd * 94), -60, OX(sd * 93), -40, OX(sd * 90), -22);
      g.bezierCurveTo(OX(sd * 86), -40, OX(sd * 82), -62, OX(sd * 76), -82); g.closePath(); g.fill();
    }

    // ---- eyes, brows
    for (const sd of [-1, 1]) {
      const i = sd < 0 ? 0 : 1, far = sd * tu > 0 ? Math.abs(tu) : 0;
      eye(g, FX(sd * 41), 6, sd, E.e[i] * (1 - o.blink), E.sq, o.look, (E.happy && E.happy[i]) || 0, 1 - far * 0.3);
    }
    for (const sd of [-1, 1]) { const i = sd < 0 ? 0 : 1; brow(g, FX, sd, E.b[i] + o.brow, E.bi[i]); }
    // ---- nose: small and slim (the nose rule): a soft shadow down one side and a short curve under the tip
    const nx = FX(0) + tu * 8;
    g.lineCap = "round";
    g.strokeStyle = "rgba(150,96,66,.35)"; g.lineWidth = 2.2;
    g.beginPath(); g.moveTo(nx - 7, 12); g.bezierCurveTo(nx - 9, 24, nx - 10, 34, nx - 9, 41); g.stroke();
    g.strokeStyle = "rgba(122,72,48,.8)"; g.lineWidth = 2.3;
    g.beginPath(); g.moveTo(nx - 9, 44); g.bezierCurveTo(nx - 4, 49, nx + 4, 49, nx + 9, 44); g.stroke();
    g.fillStyle = "rgba(255,236,214,.4)"; g.beginPath(); g.ellipse(nx + 1, 36, 4, 5, 0, 0, Math.PI * 2); g.fill();

    // ---- mouth, moustache, chin beard
    mouth(g, FX, JY, o.m);

    // ---- the cap: crown, panels, front letters, brim
    const cx = (x) => x * (1 - 0.06 * Math.abs(tu)) + tu * 10;
    const crown = new Path2D();
    crown.moveTo(cx(-108), -66); crown.bezierCurveTo(cx(-114), -130, cx(-74), -188, cx(0), -190);
    crown.bezierCurveTo(cx(74), -188, cx(114), -130, cx(108), -66); crown.closePath();
    const cg = g.createLinearGradient(cx(-80), -180, cx(60), -60); cg.addColorStop(0, C.capH); cg.addColorStop(0.5, C.cap); cg.addColorStop(1, C.capS);
    g.fillStyle = cg; g.fill(crown);
    g.save(); g.clip(crown);
    g.strokeStyle = "rgba(255,255,255,.07)"; g.lineWidth = 2;
    for (const k of [-1, 1]) { g.beginPath(); g.moveTo(cx(k * 2), -188); g.bezierCurveTo(cx(k * 36), -152, cx(k * 52), -112, cx(k * 58), -66); g.stroke(); }
    g.restore();
    g.strokeStyle = C.capS; g.lineWidth = 2.4; g.stroke(crown);
    // a soft edge light along the top, so the black cap still reads on a dark background
    g.strokeStyle = "rgba(235,232,226,.32)"; g.lineWidth = 3; g.lineCap = "round";
    g.beginPath(); g.moveTo(cx(-106), -84); g.bezierCurveTo(cx(-110), -134, cx(-70), -184, cx(0), -186); g.bezierCurveTo(cx(44), -185, cx(80), -168, cx(96), -140); g.stroke();
    g.fillStyle = C.capS; g.beginPath(); g.ellipse(cx(0), -188, 9, 4, 0, 0, Math.PI * 2); g.fill();
    // white varsity letters, arched, like his cap (his own name instead of the brand on it)
    g.save(); g.fillStyle = C.capT; g.font = "700 27px IT, Inter Tight, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle";
    const word = "VISH", rad = 170, mid = cx(0), span = 0.4;
    for (let k = 0; k < word.length; k++) {
      const a = -span / 2 + (span * k) / (word.length - 1);
      g.save(); g.translate(mid + Math.sin(a) * rad, -118 + rad - Math.cos(a) * rad); g.rotate(a); g.scale(1 - 0.06 * Math.abs(tu), 1);
      g.lineWidth = 2.4; g.strokeStyle = C.capT; g.strokeText(word[k], 0, 0); g.fillText(word[k], 0, 0); g.restore();
    }
    g.restore();
    // the brim, seen from the front and a touch above: a wide crescent over the brows
    const brim = new Path2D();
    brim.moveTo(cx(-118), -68); brim.bezierCurveTo(cx(-84), -86, cx(84), -86, cx(118), -68);
    brim.bezierCurveTo(cx(108), -48, cx(54), -38, cx(0), -37); brim.bezierCurveTo(cx(-54), -38, cx(-108), -48, cx(-118), -68); brim.closePath();
    const bg = g.createLinearGradient(0, -86, 0, -37); bg.addColorStop(0, C.capH); bg.addColorStop(1, C.cap);
    g.fillStyle = bg; g.fill(brim); g.strokeStyle = C.capS; g.lineWidth = 2.4; g.stroke(brim);
    g.strokeStyle = "rgba(255,255,255,.12)"; g.lineWidth = 2;
    g.beginPath(); g.moveTo(cx(-104), -62); g.bezierCurveTo(cx(-60), -46, cx(60), -46, cx(104), -62); g.stroke();
  }

  function eye(g, cx, cy, sd, open, sq, look, happy, wf) {
    const hw = 23 * wf;
    const ix = cx - sd * hw, ox = cx + sd * hw;  // inner and outer corners
    if (happy > 0.5 && open < 0.4) {               // a closed, smiling eye: an arch
      g.strokeStyle = C.lash; g.lineWidth = 4.2; g.lineCap = "round";
      g.beginPath(); g.moveTo(ix, cy + 5); g.bezierCurveTo(cx - sd * 9, cy - 10, cx + sd * 9, cy - 10, ox, cy + 3); g.stroke();
      return;
    }
    if (open < 0.1) {                               // a blink: the lid line, gently down
      g.strokeStyle = C.lash; g.lineWidth = 4; g.lineCap = "round";
      g.beginPath(); g.moveTo(ix, cy + 1); g.bezierCurveTo(cx - sd * 9, cy + 8, cx + sd * 9, cy + 8, ox, cy); g.stroke();
      return;
    }
    const up = 15 * open, dn = 10 * Math.min(open, 1) * (1 - sq * 0.55);
    const al = new Path2D();
    al.moveTo(ix, cy + 1); al.bezierCurveTo(cx - sd * 10, cy - up, cx + sd * 10, cy - up - 1, ox, cy - 3);
    al.bezierCurveTo(cx + sd * 11, cy + dn, cx - sd * 10, cy + dn + 1, ix, cy + 1); al.closePath();
    g.fillStyle = C.white; g.fill(al);
    g.save(); g.clip(al);
    const px = cx + look[0] * 8, py = cy + 1 + look[1] * 4;
    const ig = g.createRadialGradient(px, py + 3, 1, px, py, 12.5); ig.addColorStop(0, "#7A5132"); ig.addColorStop(0.55, C.iris); ig.addColorStop(1, C.irisD);
    g.fillStyle = ig; g.beginPath(); g.arc(px, py, 12.5, 0, Math.PI * 2); g.fill();
    g.fillStyle = "#0B0604"; g.beginPath(); g.arc(px, py, 5.6, 0, Math.PI * 2); g.fill();
    g.fillStyle = "#fff"; g.beginPath(); g.arc(px + 4, py - 4.5, 3.4, 0, Math.PI * 2); g.fill();
    g.fillStyle = "rgba(255,255,255,.75)"; g.beginPath(); g.arc(px - 4, py + 4, 1.6, 0, Math.PI * 2); g.fill();
    g.fillStyle = "rgba(110,62,40,.3)"; g.fillRect(cx - 32, cy - up - 4, 64, 8);  // the lid's shadow on the eyeball
    g.restore();
    g.strokeStyle = C.lash; g.lineWidth = 4; g.lineCap = "round"; g.lineJoin = "round";
    g.beginPath(); g.moveTo(ix - sd * 1, cy + 2); g.bezierCurveTo(cx - sd * 10, cy - up, cx + sd * 10, cy - up - 1, ox, cy - 3); g.lineTo(ox + sd * 6, cy - 7); g.stroke();
    g.strokeStyle = "rgba(110,62,40,.6)"; g.lineWidth = 1.9;  // the crease above the lid
    g.beginPath(); g.moveTo(cx - sd * 13, cy - up - 4); g.bezierCurveTo(cx - sd * 2, cy - up - 10, cx + sd * 13, cy - up - 9, ox + sd * 2, cy - 7); g.stroke();
    g.strokeStyle = "rgba(110,62,40,.45)"; g.lineWidth = 1.7;  // the lower lid
    g.beginPath(); g.moveTo(cx - sd * 8, cy + dn + 1); g.bezierCurveTo(cx + sd * 4, cy + dn + 2, cx + sd * 14, cy + dn, ox, cy - 1); g.stroke();
  }

  function brow(g, FX, sd, raise, inner) {
    const y = -22 - raise, yi = y - inner;
    const b = new Path2D();
    b.moveTo(FX(sd * 13), yi + 5);
    b.bezierCurveTo(FX(sd * 22), yi - 9, FX(sd * 42), y - 14, FX(sd * 66), y - 8);
    b.bezierCurveTo(FX(sd * 69), y - 6, FX(sd * 68), y - 3, FX(sd * 65), y - 3);
    b.bezierCurveTo(FX(sd * 46), y - 4, FX(sd * 30), yi + 3, FX(sd * 15), yi + 11);
    b.closePath();
    g.fillStyle = C.brow; g.fill(b);
  }

  // the mouth: o open, w wide, s smile (-1 frown .. 1 smile), r round, a asymmetry (smirk), f lower lip under the teeth
  function mouth(g, FX, JY, m) {
    const y0 = 81, o = m.o, hw = 21 + 12 * m.w - 9 * m.r, sm = m.s;
    const lc = [FX(-hw), y0 - sm * 6 + m.a * 5], rc = [FX(hw), y0 - sm * 6 - m.a * 6];
    const topY = y0 - 1 - o * 4 - m.r * o * 5, botY = JY(y0 + 2 + o * 28 + Math.max(0, sm) * 3 * o);
    const cxm = FX(0) + m.a * 3;
    // smile lines beside the corners
    if (sm > 0.5) {
      g.strokeStyle = `rgba(140,84,56,${0.32 * (sm - 0.5) * 2})`; g.lineWidth = 2; g.lineCap = "round";
      for (const [c, sd] of [[lc, -1], [rc, 1]]) { g.beginPath(); g.moveTo(c[0] + sd * 3, c[1] - 20); g.quadraticCurveTo(c[0] + sd * 10, c[1] - 5, c[0] + sd * 5, c[1] + 8); g.stroke(); }
    }
    let lowerTop;
    if (o < 0.05) {
      if (m.teeth && sm > 0.6) {  // a closed smile that shows the top teeth
        const sh = new Path2D(); sh.moveTo(lc[0], lc[1]); sh.bezierCurveTo(cxm - hw * 0.5, y0 + 2, cxm + hw * 0.5, y0 + 2, rc[0], rc[1]);
        sh.bezierCurveTo(cxm + hw * 0.5, y0 + 13, cxm - hw * 0.5, y0 + 13, lc[0], lc[1]); sh.closePath();
        g.fillStyle = C.mouthIn; g.fill(sh); g.save(); g.clip(sh); g.fillStyle = C.teeth; g.fillRect(lc[0] - 4, y0 - 6, hw * 2 + 8, 13); g.restore();
        g.strokeStyle = C.lipD; g.lineWidth = 2.2; g.stroke(sh); lowerTop = y0 + 10;
      } else {
        g.strokeStyle = C.lipD; g.lineWidth = 3; g.lineCap = "round";
        g.beginPath(); g.moveTo(lc[0], lc[1]); g.bezierCurveTo(cxm - hw * 0.45, y0 + sm * 7 + 1, cxm + hw * 0.45, y0 + sm * 7 + 1, rc[0], rc[1]); g.stroke();
        lowerTop = y0 + 2 + Math.max(0, sm) * 5;
      }
    } else {
      const mp = new Path2D();
      mp.moveTo(lc[0], lc[1]);
      mp.bezierCurveTo(cxm - hw * 0.5, topY - m.r * 6, cxm + hw * 0.5, topY - m.r * 6, rc[0], rc[1]);
      mp.bezierCurveTo(cxm + hw * (0.6 - m.r * 0.15), botY + 2, cxm - hw * (0.6 - m.r * 0.15), botY + 2, lc[0], lc[1]);
      mp.closePath();
      g.fillStyle = C.mouthIn; g.fill(mp);
      g.save(); g.clip(mp);
      g.fillStyle = C.teeth; g.beginPath(); g.ellipse(cxm, topY - 2, hw * 0.92, 9.5 - m.r * 3, 0, 0, Math.PI * 2); g.fill();  // the upper teeth
      if (m.f > 0.3) { g.fillStyle = C.lip; g.beginPath(); g.ellipse(cxm, topY + 10, hw * 0.8, 7, 0, 0, Math.PI * 2); g.fill(); }
      g.fillStyle = C.tongue; g.beginPath(); g.ellipse(cxm, botY + 3, hw * 0.6, 4 + o * 10, 0, 0, Math.PI * 2); g.fill();
      g.restore();
      g.strokeStyle = C.lipD; g.lineWidth = 2.2; g.stroke(mp); lowerTop = botY + 1;
    }
    // the lower lip: a soft shape and a highlight
    g.fillStyle = "rgba(164,92,74,.42)"; g.beginPath(); g.ellipse(cxm, lowerTop + 5, hw * 0.48, 4.6, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = "rgba(255,226,206,.25)"; g.beginPath(); g.ellipse(cxm + 2, lowerTop + 4, hw * 0.2, 1.6, 0, 0, Math.PI * 2); g.fill();
    // the moustache: thin, the ends down to the mouth corners; it rides up with the upper lip
    const lift = Math.min(0, topY - (y0 - 1)) * 0.6;
    g.save(); g.translate(0, lift);
    const mu = new Path2D();
    const ey = (c) => Math.min(c[1] - 3, y0 - 6);
    mu.moveTo(lc[0] - 1, ey(lc));
    mu.bezierCurveTo(lc[0] + 2, y0 - 16, FX(-20), 61, FX(-6), 60.5);
    mu.bezierCurveTo(FX(-2), 60, FX(2), 60, FX(6), 60.5);
    mu.bezierCurveTo(FX(20), 61, rc[0] - 2, y0 - 16, rc[0] + 1, ey(rc));
    mu.bezierCurveTo(rc[0] - 4, y0 - 10, FX(18), 67, FX(6), 67);
    mu.bezierCurveTo(FX(2), 66.5, FX(-2), 66.5, FX(-6), 67);
    mu.bezierCurveTo(FX(-18), 67, lc[0] + 4, y0 - 10, lc[0] - 1, ey(lc));
    mu.closePath(); g.fillStyle = "rgba(26,18,14,.88)"; g.fill(mu);
    g.restore();
    // the chin beard: a small patch under the lip, a pointed beard on the chin
    const by = lowerTop + 16;
    g.fillStyle = "rgba(26,18,14,.7)"; g.beginPath(); g.ellipse(cxm, by, 4.5, 5.5, 0, 0, Math.PI * 2); g.fill();
    const cb = new Path2D();
    cb.moveTo(FX(-30), JY(118)); cb.bezierCurveTo(FX(-20), JY(128), FX(-10), JY(131), FX(0), JY(131)); cb.bezierCurveTo(FX(10), JY(131), FX(20), JY(128), FX(30), JY(118));
    cb.bezierCurveTo(FX(26), JY(134), FX(12), JY(147), FX(0), JY(148)); cb.bezierCurveTo(FX(-12), JY(147), FX(-26), JY(134), FX(-30), JY(118)); cb.closePath();
    g.fillStyle = "rgba(26,18,14,.72)"; g.fill(cb);
  }

  // ----------------------------------------------------------------------------------------------------- hands
  // hand space: the wrist at (0, 0), the hand points along +x; side = 1 for his left hand (screen right)
  function hand(g, kind, side) {
    const sk = C.skin, ln = C.line, lw = 2.2;
    g.lineCap = "round"; g.lineJoin = "round";
    const finger = (x0, y0, a, l, w) => { const e = pt([x0, y0], a, l); cap(g, [[x0, y0], e], w, sk, ln, 1.1); };
    const palm = (len, wid) => { const p = P(g, `M0 ${-wid} C${len * 0.6} ${-wid - 4} ${len} ${-wid + 2} ${len} 0 C${len} ${wid - 2} ${len * 0.6} ${wid + 4} 0 ${wid} Z`); fillStroke(g, p, sk, ln, lw); };
    const ts = -side;  // the thumb's side
    if (kind === "relax") {  // fingers together, gently curled; the thumb along the side
      fillStroke(g, P(g, "M0 -22 C26 -28 54 -26 72 -16 C84 -8 84 10 72 16 C54 26 26 28 0 22 Z"), sk, ln, lw);
      g.strokeStyle = ln; g.lineWidth = 1.5; g.beginPath(); g.moveTo(56, -8); g.lineTo(76, -6); g.moveTo(58, 4); g.lineTo(78, 5); g.stroke();
      finger(14, ts * 20, ts * 50, 22, 15);
    } else if (kind === "open" || kind === "palm") {
      palm(46, 25);
      for (const [y, a, l] of [[-15, -9, 32], [-5, -3, 37], [5, 3, 36], [15, 9, 29]]) finger(42, y, a, l, 16);
      finger(12, ts * 21, ts * 55, 28, 17);
    } else if (kind === "point") {  // the index finger out on the thumb's side, the thumb folded across the fist
      const f = P(g, "M0 -22 C30 -28 52 -24 54 -2 C56 20 30 26 0 22 Z"); fillStroke(g, f, sk, ln, lw);
      g.strokeStyle = ln; g.lineWidth = 1.6; g.beginPath(); g.moveTo(42, ts * -2); g.lineTo(54, ts * -2); g.moveTo(40, ts * -12); g.lineTo(51, ts * -12); g.stroke();
      finger(44, ts * 13, ts * 6, 52, 15);
      finger(18, ts * 21, ts * 38, 20, 15);
    } else if (kind === "thumb") {  // a fist side-on, curled fingers stacked, a short thick thumb up
      fillStroke(g, P(g, "M0 -22 C30 -28 52 -26 56 -4 C60 22 34 30 0 24 Z"), sk, ln, lw);
      g.strokeStyle = ln; g.lineWidth = 1.6; g.beginPath(); for (const x of [16, 28, 40]) { g.moveTo(x, -2); g.quadraticCurveTo(x + 4, 10, x, 22); } g.stroke();
      const th = P(g, `M8 ${ts * 18} C6 ${ts * 40} 12 ${ts * 54} 24 ${ts * 54} C34 ${ts * 54} 34 ${ts * 40} 30 ${ts * 18} Z`); fillStroke(g, th, sk, ln, lw);
      g.strokeStyle = "rgba(255,240,226,.6)"; g.lineWidth = 1.6; g.beginPath(); g.moveTo(16, ts * 48); g.quadraticCurveTo(22, ts * 51, 27, ts * 46); g.stroke();
    } else if (kind === "fist" || kind === "tuck") {
      const f = P(g, "M0 -24 C32 -30 54 -24 56 0 C58 24 32 30 0 24 Z"); fillStroke(g, f, sk, ln, lw);
      g.strokeStyle = ln; g.lineWidth = 1.6; g.beginPath(); for (const y of [-12, 0, 12]) { g.moveTo(40, y); g.lineTo(54, y); } g.stroke();
    } else if (kind === "chin") {  // a loose fist under the chin, index finger along the jaw
      const f = P(g, "M0 -24 C30 -30 52 -22 54 0 C56 22 30 28 0 24 Z"); fillStroke(g, f, sk, ln, lw);
      finger(46, ts * -14, ts * -25, 34, 14);
      g.strokeStyle = ln; g.lineWidth = 1.6; g.beginPath(); g.moveTo(38, 2); g.lineTo(52, 2); g.moveTo(38, 13); g.lineTo(50, 13); g.stroke();
    }
  }

  function arm(g, sh, a, side, wave) {
    const u = a.u, f = a.f + (wave || 0);
    const el = pt(sh, u, 250 * (a.ul ?? 1)), wr = pt(el, f, 228 * (a.fl ?? 1));
    // the sleeve, then the ribbed cuff
    cap(g, [sh, el, wr], 96, C.hood, C.hoodLine, 2.2);
    g.strokeStyle = "rgba(255,255,255,.18)"; g.lineWidth = 10; g.lineCap = "round";
    g.beginPath(); g.moveTo(...pt(sh, u - 90, 26)); g.lineTo(...pt(el, (u + f) / 2 - 90, 26)); g.stroke();
    const cuff0 = pt(wr, f + 180, 36);
    cap(g, [cuff0, wr], 84, C.hoodS, null, 0);
    g.strokeStyle = "rgba(0,0,0,.08)"; g.lineWidth = 2; g.beginPath(); g.moveTo(...pt(cuff0, f + 90, 36)); g.lineTo(...pt(cuff0, f - 90, 36)); g.stroke();
    // a fold at the elbow
    g.strokeStyle = C.hoodD; g.lineWidth = 2.4; g.beginPath(); g.moveTo(...pt(el, (u + f) / 2 + 90, 22)); g.quadraticCurveTo(...pt(el, (u + f) / 2 + 90, 6), ...pt(el, (u + f) / 2 + 60, -8)); g.stroke();
    const ha = a.ha ?? f;
    g.save(); g.translate(...pt(wr, f, 4)); g.rotate(ha * R); g.scale(1.42, 1.42);
    if (side > 0 && a.h !== "tuck") { g.strokeStyle = C.silver; g.lineWidth = 4.5; g.beginPath(); g.moveTo(-1, -23); g.lineTo(-1, 23); g.stroke(); }  // his bracelet
    hand(g, a.h, side);
    g.restore();
    return wr;
  }

  // ----------------------------------------------------------------------------------------------------- legs and shoes
  function leg(g, hip, th, sh, front) {
    const knee = pt(hip, th, 300), ank = pt(knee, sh, 282);
    cap(g, [hip, knee, ank], 112, C.pants, C.pantsS, 2);
    g.strokeStyle = C.pantsH; g.lineWidth = 3; g.beginPath(); g.moveTo(...pt(hip, th - 90, 32)); g.lineTo(...pt(knee, sh - 90, 30)); g.stroke();
    cap(g, [pt(ank, sh + 180, 34), pt(ank, sh + 180, 6)], 92, C.pantsS, null, 0);  // the jogger cuff
    shoe(g, ank, front);
  }
  function shoe(g, ank, front) {
    g.save(); g.translate(ank[0], ank[1] + 30); g.scale(1.25, 1.25);
    if (front === 0) {
      const s = P(g, "M-40 -22 C-44 -42 44 -42 40 -22 C52 -8 50 18 34 22 L-34 22 C-50 18 -52 -8 -40 -22 Z"); fillStroke(g, s, C.shoe, C.shoeS, 2.2);
      g.fillStyle = C.sole; g.fillRect(-38, 14, 76, 10);
    } else {
      g.scale(front, 1);
      const s = P(g, "M-46 -26 C-40 -40 0 -40 18 -26 C40 -18 70 -10 74 6 C76 16 70 22 60 22 L-46 22 C-54 16 -54 -14 -46 -26 Z"); fillStroke(g, s, C.shoe, C.shoeS, 2.2);
      g.fillStyle = C.sole; g.fillRect(-48, 14, 120, 10);
      g.strokeStyle = C.shoeS; g.lineWidth = 2; g.beginPath(); g.moveTo(-6, -30); g.lineTo(26, -18); g.stroke();
    }
    g.restore();
  }

  // ----------------------------------------------------------------------------------------------------- the whole figure
  // proportions: a big head (HS) on a hoodie body; the upper body is drawn in the old coordinates, lifted down by UP
  const HS = 1.28, UP = 180;
  window.VishCap = {
    EX, POSE, C, HS,
    // where the eye line sits above his feet, in rig units (for framing a face shot)
    EYE: 1364 - UP + 141 * HS - 8,
    draw(g, p) {
      const o = Object.assign({x: 540, y: 1900, s: 0.5, expr: "smile", pose: "rest", talk: null, blink: 0, look: null, turn: 0, tilt: 0, nod: 0, walk: null, dir: 1, t: 0, brow: 0, shadow: 1}, p);
      const pose = POSE[o.pose] || POSE.rest;
      const E = EX[o.expr] || EX[pose.expr] || EX.smile;
      const walking = o.walk !== null && o.walk !== undefined;
      const ph = walking ? o.walk : 0, bob = walking ? Math.abs(Math.sin(ph)) * 14 : 0;
      const breathe = Math.sin(o.t * 2.3) * 3;
      // the mouth: the expression's rest shape, opened and shaped by the voice
      const base = E.m, tk = o.talk;
      const m = tk ? {o: Math.max(base.o * 0.6, tk.o), w: lerp(base.w, tk.w, 0.7), s: base.s * (1 - tk.o * 0.5), r: tk.r, a: base.a * 0.5, f: tk.f, teeth: base.teeth}
                   : Object.assign({f: 0}, base);
      const turn = cl(o.turn + (pose.turn || 0) + (walking ? o.dir * 0.42 : 0), -0.7, 0.7);
      const look = o.look || pose.look || E.look || [turn * 0.6, 0];
      g.save(); g.translate(o.x, o.y); g.scale(o.s, o.s);
      if (o.shadow) { g.fillStyle = "rgba(21,19,15,.14)"; g.beginPath(); g.ellipse(0, 8, 220, 28, 0, 0, Math.PI * 2); g.fill(); }
      g.translate(0, -bob);
      // legs
      if (walking) {
        const sw = Math.sin(ph) * 28 * -o.dir, kn = (q) => Math.max(0, Math.sin(q)) * 34 * o.dir;
        leg(g, [-28, -620], 90 + sw, 90 + sw + kn(ph), o.dir);
        leg(g, [28, -620], 90 - sw, 90 - sw + kn(ph + Math.PI), o.dir);
      } else {
        leg(g, [-64, -620], 91.5, 90.5, 0); leg(g, [64, -620], 88.5, 89.5, 0);
      }
      g.translate(0, UP);
      // the body turns a little with the head (a narrower torso); walking, the far arm swings behind it
      const bx = walking ? 0.84 : 1 - Math.abs(turn) * 0.14;
      const sx = 178 * bx, shY = -1258 + breathe * 0.6;
      const sw2 = walking ? Math.sin(ph) * 24 * o.dir : 0;
      const far = o.dir > 0 ? "R" : "L";
      if (walking) arm(g, [turn * 14 + (far === "L" ? -sx : sx), shY], {u: 90 + (far === "L" ? sw2 : -sw2), f: 90 + (far === "L" ? sw2 : -sw2) * 1.3, h: "relax"}, far === "L" ? -1 : 1, 0);
      g.save(); g.translate(turn * 14, breathe * 0.4); g.scale(bx, 1);
      // the white tee below the hoodie
      fillStroke(g, P(g, "M-168 -836 L168 -836 L162 -782 C80 -774 -80 -774 -162 -782 Z"), C.tee, C.teeS, 2.2);
      g.fillStyle = C.pants; g.beginPath(); g.moveTo(-150, -800); g.lineTo(150, -800); g.lineTo(134, -690); g.lineTo(-134, -690); g.closePath(); g.fill();
      // the hood behind the neck
      fillStroke(g, P(g, "M-168 -1292 C-170 -1336 -120 -1372 -40 -1380 C-14 -1382 14 -1382 40 -1380 C120 -1372 170 -1336 168 -1292 Z"), C.hoodS, C.hoodLine, 2.2);
      // torso
      const tor = P(g, "M-70 -1322 C-112 -1318 -164 -1308 -192 -1284 C-214 -1260 -216 -1216 -214 -1170 L-204 -862 C-202 -834 -186 -820 -156 -818 L156 -818 C186 -820 202 -834 204 -862 L214 -1170 C216 -1216 214 -1260 192 -1284 C164 -1308 112 -1318 70 -1322 Z");
      const tg = g.createLinearGradient(-214, 0, 214, 0); tg.addColorStop(0, C.hoodS); tg.addColorStop(0.25, C.hoodL); tg.addColorStop(0.6, C.hood); tg.addColorStop(1, C.hoodS);
      fillStroke(g, tor, tg, C.hoodLine, 2.4);
      g.save(); g.clip(tor);
      g.fillStyle = C.hoodS; g.fillRect(-220, -866, 440, 50);  // the ribbed hem
      g.strokeStyle = "rgba(0,0,0,.07)"; g.lineWidth = 2; g.beginPath(); for (let x = -210; x < 220; x += 12) { g.moveTo(x, -862); g.lineTo(x, -818); } g.stroke();
      g.strokeStyle = C.hoodD; g.lineWidth = 2.2; g.beginPath(); g.moveTo(-214, -866); g.lineTo(214, -866); g.stroke();
      g.strokeStyle = "rgba(110,108,104,.45)"; g.lineWidth = 2.4;  // folds under the arms
      g.beginPath(); g.moveTo(-176, -1150); g.quadraticCurveTo(-146, -1120, -156, -1080); g.moveTo(176, -1150); g.quadraticCurveTo(146, -1120, 156, -1080); g.stroke();
      g.restore();
      // the kangaroo pocket
      fillStroke(g, P(g, "M-116 -1014 L116 -1014 C124 -962 138 -904 146 -872 L-146 -872 C-138 -904 -124 -962 -116 -1014 Z"), C.hood, C.hoodLine, 2.2);
      g.strokeStyle = C.hoodD; g.lineWidth = 3;
      g.beginPath(); g.moveTo(-116, -1014); g.bezierCurveTo(-128, -962, -138, -904, -146, -872); g.moveTo(116, -1014); g.bezierCurveTo(128, -962, 138, -904, 146, -872); g.stroke();
      g.restore();
      // neck
      g.save(); g.translate(turn * 14, 0);
      const ng = g.createLinearGradient(-40, 0, 40, 0); ng.addColorStop(0, C.skinD); ng.addColorStop(0.4, C.skinS); ng.addColorStop(1, C.skinD);
      fillStroke(g, P(g, "M-36 -1440 L36 -1440 L42 -1290 L-42 -1290 Z"), ng, null, 0);
      g.fillStyle = "rgba(80,46,30,.35)"; g.fillRect(-40, -1426, 80, 44);
      // the hood's front rim and the drawstrings
      g.save(); g.scale(bx, 1);
      const rim = P(g, "M-170 -1300 C-150 -1330 -110 -1338 -72 -1334 C-50 -1300 -26 -1280 0 -1278 C26 -1280 50 -1300 72 -1334 C110 -1338 150 -1330 170 -1300 C140 -1262 70 -1232 0 -1228 C-70 -1232 -140 -1262 -170 -1300 Z");
      fillStroke(g, rim, C.hoodL, C.hoodLine, 2.2);
      g.strokeStyle = C.hoodS; g.lineWidth = 3; g.beginPath(); g.moveTo(-120, -1290); g.bezierCurveTo(-80, -1262, 80, -1262, 120, -1290); g.stroke();
      const sw0 = walking ? Math.sin(ph) * 6 : Math.sin(o.t * 1.7) * 2;
      for (const sd of [-1, 1]) {
        g.strokeStyle = C.string; g.lineWidth = 8; g.lineCap = "round";
        g.beginPath(); g.moveTo(sd * 22, -1250); g.bezierCurveTo(sd * 28, -1210, sd * 26 + sw0, -1180, sd * 30 + sw0, -1146); g.stroke();
        g.strokeStyle = C.silverS; g.lineWidth = 9; g.beginPath(); g.moveTo(sd * 30 + sw0, -1146); g.lineTo(sd * 30 + sw0, -1128); g.stroke();
      }
      g.restore();
      // the head, on the neck
      const swayHead = walking ? Math.sin(ph * 2) * 1.5 : 0;
      g.translate(0, -1364 + breathe * 0.5);
      g.rotate((o.tilt + (E.tilt || 0) + swayHead) * R); g.translate(0, o.nod);
      g.translate(0, -141 * HS + 8); g.scale(HS, HS);
      head(g, {E, turn, jaw: m.o * 12, blink: o.blink, look, m, brow: o.brow});
      g.restore();
      // arms
      let A = {L: pose.L, R: pose.R};
      if (walking) {
        A = {L: {u: 90 + sw2, f: 90 + sw2 * 1.3, h: "relax"}, R: {u: 90 - sw2, f: 90 - sw2 * 1.3, h: "relax"}};
      }
      const wv = pose.wave ? Math.sin(o.t * 11) * 14 : 0, ex = pose.sway ? Math.sin(o.t * 2.2) * 6 : 0;
      for (const k of (walking ? [far === "L" ? "R" : "L"] : pose.order || ["L", "R"])) {
        const a = Object.assign({}, A[k]); if (ex) { a.f += (k === "L" ? -ex : ex); }
        arm(g, [turn * 14 + (k === "L" ? -sx : sx), shY], a, k === "L" ? -1 : 1, k === "R" ? wv : 0);
      }
      g.restore();
    }};
})();
