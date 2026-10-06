// Build with Vish 3D kit: materials, hero objects and the "Dot" mascot.
// Scenes are described as JSON specs so the pipeline can render stills and video frames
// deterministically: window.setup(spec) once, then window.renderAt(t) for any time t (seconds).
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";

export const C = {
  violet: 0x7f77dd, violetLight: 0xafa9ec, violetInk: 0x4a44c4, aurora: 0x6fe0d2, auroraDeep: 0x0e8c80,
  sol: 0xf3c584, coral: 0xf5b49c, ink: 0x17141c, paper: 0xfbfaf8, lavender: 0xe9e5ec, metal: 0xc9c6d6,
  bone: 0xece7dc, teal: 0x0e4b48, signal: 0xd99a1e,
};

const hex = (v) => (typeof v === "string" ? new THREE.Color(v) : new THREE.Color(v));

export const mat = {
  clay: (color = C.violet, rough = 0.82) =>
    new THREE.MeshPhysicalMaterial({ color: hex(color), roughness: rough, metalness: 0, clearcoat: 0.12, clearcoatRoughness: 0.6, sheen: 0.25, sheenRoughness: 0.9, sheenColor: hex(color).lerp(new THREE.Color(0xffffff), 0.35) }),
  glass: (tint = 0xcfcbfa, rough = 0.08) =>
    new THREE.MeshPhysicalMaterial({ color: hex(tint), transmission: 1, roughness: rough, thickness: 1.2, ior: 1.45, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.05, attenuationColor: hex(tint), attenuationDistance: 2.5, specularIntensity: 1 }),
  frost: (tint = 0xdedbfb) =>
    new THREE.MeshPhysicalMaterial({ color: hex(tint), transmission: 0.92, roughness: 0.38, thickness: 0.9, ior: 1.4, clearcoat: 1, clearcoatRoughness: 0.2, attenuationColor: hex(tint), attenuationDistance: 1.8 }),
  metal: (color = C.metal, rough = 0.24) => new THREE.MeshStandardMaterial({ color: hex(color), metalness: 1, roughness: rough }),
  gloss: (color = C.ink, rough = 0.18) => new THREE.MeshPhysicalMaterial({ color: hex(color), roughness: rough, metalness: 0.1, clearcoat: 1, clearcoatRoughness: 0.08 }),
  glow: (color = C.aurora, intensity = 2.2) => new THREE.MeshStandardMaterial({ color: hex(color), emissive: hex(color), emissiveIntensity: intensity, roughness: 0.4 }),
};

function roundedRectShape(w, h, r) {
  const s = new THREE.Shape();
  const x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  return s;
}

function bubbleShape(w, h, r) {
  // Rounded chat bubble with a small tail bottom-left.
  const s = new THREE.Shape();
  const x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r * 0.9);
  s.lineTo(x - r * 0.55, y - r * 0.55);
  s.lineTo(x + r * 0.9, y);
  return s;
}

const extrude = (shape, depth, bevel = 0.06) =>
  new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 8, curveSegments: 32 });

// ---------- hero objects ----------
export const objects = {
  // Glass chat bubble with "text" bars and an invisible-dot watermark grid inside.
  watermarkBubble({ dots = 1 } = {}) {
    const g = new THREE.Group();
    const geo = extrude(bubbleShape(2.6, 1.7, 0.42), 0.34, 0.08);
    geo.translate(0, 0, -0.17);
    const bubble = new THREE.Mesh(geo, new THREE.MeshPhysicalMaterial({ color: 0xf4f3fb, roughness: 0.32, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.12, sheen: 0.3, sheenColor: new THREE.Color(0xd9d5fb) }));
    g.add(bubble);
    const lines = [2.0, 1.7, 1.85, 1.1];
    lines.forEach((w, i) => {
      const bar = new THREE.Mesh(new RoundedBoxGeometry(w, 0.13, 0.05, 4, 0.06), mat.clay(C.ink, 0.6));
      bar.position.set(-1.0 + w / 2, 0.5 - i * 0.32, 0.27);
      g.add(bar);
    });
    const grid = new THREE.Group();
    const dg = new THREE.SphereGeometry(0.022, 12, 12);
    const dm = new THREE.MeshStandardMaterial({ color: 0xd6d2f6, roughness: 0.6 });
    for (let ix = 0; ix < 11; ix++) for (let iy = 0; iy < 6; iy++) {
      if ((ix * 7 + iy * 3) % 4 === 0) continue;
      const d = new THREE.Mesh(dg, dm);
      d.position.set(-1.05 + ix * 0.21, -0.52 + iy * 0.2, 0.25);
      grid.add(d);
    }
    grid.name = "dots";
    grid.userData.base = dots;
    g.add(grid);
    g.userData.dots = grid;
    return g;
  },

  magnifier({ reveal = true } = {}) {
    const g = new THREE.Group();
    if (reveal) {
      // The "hidden" watermark, magnified: a violet dot lattice visible only through the lens.
      const dm = mat.glow(C.violet, 0.9), dg = new THREE.SphereGeometry(0.045, 16, 16);
      for (let ix = -4; ix <= 4; ix++) for (let iy = -4; iy <= 4; iy++) {
        const x = ix * 0.13, y = iy * 0.13;
        if (x * x + y * y > 0.27 || (ix * 3 + iy * 5) % 4 === 0) continue;
        const d = new THREE.Mesh(dg, dm); d.position.set(x, y, -0.06); g.add(d);
      }
      const disc = new THREE.Mesh(new THREE.CircleGeometry(0.6, 64), new THREE.MeshStandardMaterial({ color: 0xf7f6fd, roughness: 0.5 }));
      disc.position.z = -0.1; g.add(disc);
    }
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.62, 0.09, 32, 96), mat.metal(0xd8d5e6, 0.18));
    const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 0.06, 64), new THREE.MeshPhysicalMaterial({ color: 0xffffff, transmission: 1, roughness: 0.02, thickness: 0.05, ior: 1.2, clearcoat: 1 }));
    lens.rotation.x = Math.PI / 2;
    const handle = new THREE.Mesh(new RoundedBoxGeometry(0.2, 0.95, 0.2, 4, 0.09), mat.clay(C.ink, 0.5));
    handle.position.set(0.72, -0.72, 0); handle.rotation.z = Math.PI / 4;
    g.add(ring, lens, handle);
    return g;
  },

  // Stack of image tiles; one tile is the warm "sponsored" slot.
  imageTiles({ count = 4, sponsored = 2 } = {}) {
    const g = new THREE.Group();
    const cols = [C.violetLight, C.aurora, C.coral, C.violet, C.sol];
    for (let i = 0; i < count; i++) {
      const t = new THREE.Group();
      const isAd = i === sponsored;
      const frame = new THREE.Mesh(new RoundedBoxGeometry(1.3, 1.62, 0.08, 6, 0.1), isAd ? mat.clay(C.sol, 0.7) : mat.frost(0xe9e6fb));
      t.add(frame);
      const art = new THREE.Mesh(new RoundedBoxGeometry(1.1, 1.1, 0.05, 4, 0.08), mat.clay(cols[i % cols.length], 0.75));
      art.position.set(0, 0.17, 0.06);
      t.add(art);
      const blob = new THREE.Mesh(new THREE.SphereGeometry(0.22, 48, 48), isAd ? mat.gloss(C.ink, 0.15) : mat.clay(0xffffff, 0.6));
      blob.position.set(0.18, 0.25, 0.22); blob.scale.set(1, 1, 0.6);
      t.add(blob);
      const cap = new THREE.Mesh(new RoundedBoxGeometry(isAd ? 0.62 : 0.8, 0.1, 0.04, 3, 0.04), isAd ? mat.clay(C.ink, 0.5) : mat.clay(0xcac6dc, 0.7));
      cap.position.set(isAd ? -0.21 : -0.12, -0.6, 0.06);
      t.add(cap);
      t.position.set((i - (count - 1) / 2) * 0.62, (isAd ? 0.18 : 0) - Math.abs(i - (count - 1) / 2) * 0.08, i * 0.28);
      t.rotation.z = (i - (count - 1) / 2) * -0.09;
      t.userData.isAd = isAd;
      t.userData.i = i;
      g.add(t);
    }
    g.userData.tiles = g.children.slice();
    return g;
  },

  // Creator spheres orbiting a ring that feeds one ad tile: "discovery and paid in one place".
  creatorHub({ creators = 5 } = {}) {
    const g = new THREE.Group();
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1.35, 0.05, 24, 160), mat.metal(0xc8c4d8, 0.2));
    ring.rotation.x = Math.PI / 2.25;
    g.add(ring);
    const cols = [C.violet, C.aurora, C.coral, C.violetLight, C.sol, C.violet];
    const orbit = new THREE.Group();
    for (let i = 0; i < creators; i++) {
      const a = (i / creators) * Math.PI * 2;
      const s = new THREE.Mesh(new THREE.SphereGeometry(0.26, 48, 48), mat.clay(cols[i % cols.length], 0.8));
      s.position.set(Math.cos(a) * 1.35, Math.sin(a) * 1.35 * Math.cos(Math.PI / 2.25), Math.sin(a) * 1.35 * Math.sin(Math.PI / 2.25) * -1);
      orbit.add(s);
    }
    g.add(orbit);
    const tile = new THREE.Mesh(new RoundedBoxGeometry(0.95, 1.2, 0.16, 6, 0.12), mat.glass(0xd9d5fb, 0.06));
    tile.position.y = 0.62;
    g.add(tile);
    const play = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.32, 3), mat.clay(C.ink, 0.5));
    play.rotation.z = -Math.PI / 2; play.position.set(0.03, 0.62, 0.02);
    g.add(play);
    g.userData.orbit = orbit;
    return g;
  },

  // Soft-clay pebble cluster (abstract filler for section breaks).
  pebbles({ seed = 3 } = {}) {
    const g = new THREE.Group();
    const cols = [C.violet, C.violetLight, C.aurora, C.coral, C.sol];
    let r = seed;
    const rnd = () => ((r = (r * 9301 + 49297) % 233280) / 233280);
    for (let i = 0; i < 5; i++) {
      const m = new THREE.Mesh(new RoundedBoxGeometry(0.7, 0.7, 0.7, 6, 0.3), mat.clay(cols[i], 0.85));
      m.position.set((rnd() - 0.5) * 2.4, (rnd() - 0.5) * 1.6, (rnd() - 0.5) * 0.8);
      m.rotation.set(rnd() * 3, rnd() * 3, rnd() * 3);
      const s = 0.6 + rnd() * 0.7; m.scale.setScalar(s);
      g.add(m);
    }
    return g;
  },

  // The BwV logo mark as an object: rotated square ring with a dot.
  logoMark({ color = C.violet } = {}) {
    const g = new THREE.Group();
    const tile = new THREE.Mesh(new RoundedBoxGeometry(1.2, 1.2, 0.3, 6, 0.26), mat.clay(color, 0.7));
    g.add(tile);
    const diamond = new THREE.Mesh(new THREE.TorusGeometry(0.34, 0.06, 16, 4), mat.clay(0xffffff, 0.5));
    diamond.position.z = 0.17;
    g.add(diamond);
    const dot = new THREE.Mesh(new THREE.SphereGeometry(0.08, 32, 32), mat.clay(0xffffff, 0.4));
    dot.position.z = 0.2;
    g.add(dot);
    return g;
  },
};

// ---------- mascot: "Dot" ----------
// A small soft-clay violet sidekick. Antenna ends in the BwV diamond-and-dot.
// Expressions: neutral, happy, wink, surprised, thinking, focused.
export function mascot({ expression = "neutral", color = C.violet, pose = "idle" } = {}) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new RoundedBoxGeometry(1.0, 1.08, 0.86, 8, 0.38), mat.clay(color, 0.78));
  g.add(body);
  const visor = new THREE.Mesh(new RoundedBoxGeometry(0.74, 0.46, 0.1, 6, 0.2), mat.gloss(C.ink, 0.14));
  visor.position.set(0, 0.1, 0.42);
  g.add(visor);
  const eyeMat = mat.glow(C.aurora, 0.9);
  const eyes = new THREE.Group();
  eyes.position.set(0, 0.1, 0.48);
  const mk = (geo, x, rotZ = 0, sx = 1, sy = 1) => { const e = new THREE.Mesh(geo, eyeMat); e.position.x = x; e.rotation.z = rotZ; e.scale.set(sx, sy, 1); eyes.add(e); return e; };
  const capsule = new THREE.CapsuleGeometry(0.045, 0.1, 6, 16);
  const arc = new THREE.TorusGeometry(0.075, 0.026, 12, 24, Math.PI);
  const dotG = new THREE.SphereGeometry(0.06, 24, 24);
  const line = new THREE.CapsuleGeometry(0.024, 0.11, 6, 12);
  switch (expression) {
    case "happy": mk(arc, -0.16); mk(arc, 0.16); break;
    case "wink": mk(capsule, -0.16); mk(arc, 0.16); break;
    case "surprised": mk(dotG, -0.16, 0, 1.15, 1.15); mk(dotG, 0.16, 0, 1.15, 1.15); break;
    case "thinking": mk(capsule, -0.16); mk(line, 0.16, Math.PI / 2); eyes.position.y += 0.02; break;
    case "focused": mk(line, -0.16, Math.PI / 2 - 0.25); mk(line, 0.16, Math.PI / 2 + 0.25); break;
    default: mk(capsule, -0.16); mk(capsule, 0.16);
  }
  g.add(eyes);
  // cheeks
  const cheekM = mat.clay(C.coral, 0.9);
  [-0.3, 0.3].forEach((x) => { const c = new THREE.Mesh(new THREE.SphereGeometry(0.055, 16, 16), cheekM); c.position.set(x * 1.12, -0.24, 0.39); c.scale.set(1.1, 0.62, 0.4); g.add(c); });
  // antenna with diamond + dot
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.03, 0.26, 12), mat.clay(C.ink, 0.5));
  stem.position.set(0, 0.66, 0);
  const diamond = new THREE.Mesh(new THREE.TorusGeometry(0.11, 0.032, 12, 4), mat.clay(color === C.violet ? C.violetLight : C.violet, 0.6));
  diamond.position.set(0, 0.86, 0);
  const tip = new THREE.Mesh(new THREE.SphereGeometry(0.045, 20, 20), mat.glow(C.sol, 0.8));
  tip.position.set(0, 0.86, 0);
  g.add(stem, diamond, tip);
  // arms
  const armG = new THREE.CapsuleGeometry(0.08, 0.2, 6, 16);
  const armM = mat.clay(color, 0.78);
  const la = new THREE.Mesh(armG, armM), ra = new THREE.Mesh(armG, armM);
  la.position.set(-0.56, -0.14, 0.05); ra.position.set(0.56, -0.14, 0.05);
  la.rotation.z = 0.35; ra.rotation.z = -0.35;
  if (pose === "wave") { ra.position.set(0.62, 0.22, 0.05); ra.rotation.z = -2.5; }
  if (pose === "point") { ra.position.set(0.66, 0.0, 0.12); ra.rotation.z = -1.35; }
  if (pose === "cheer") { la.position.set(-0.62, 0.22, 0.05); la.rotation.z = 2.5; ra.position.set(0.62, 0.22, 0.05); ra.rotation.z = -2.5; }
  if (pose === "hold") { la.position.set(-0.42, -0.2, 0.42); la.rotation.set(1.2, 0, 0.6); ra.position.set(0.42, -0.2, 0.42); ra.rotation.set(1.2, 0, -0.6); }
  g.add(la, ra);
  g.userData = { body, eyes, antenna: [diamond, tip], arms: [la, ra] };
  return g;
}

// ---------- stage ----------
export function contactShadow(radius = 1.6, color = 0x2a2440, opacity = 0.32) {
  const c = document.createElement("canvas"); c.width = c.height = 256;
  const x = c.getContext("2d");
  const grad = x.createRadialGradient(128, 128, 0, 128, 128, 128);
  const col = new THREE.Color(color);
  const rgb = `${Math.round(col.r * 255)},${Math.round(col.g * 255)},${Math.round(col.b * 255)}`;
  grad.addColorStop(0, `rgba(${rgb},1)`); grad.addColorStop(0.55, `rgba(${rgb},.35)`); grad.addColorStop(1, `rgba(${rgb},0)`);
  x.fillStyle = grad; x.fillRect(0, 0, 256, 256);
  const tex = new THREE.CanvasTexture(c);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(radius * 2, radius * 2), new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity, depthWrite: false }));
  m.rotation.x = -Math.PI / 2;
  return m;
}

export function createStage(canvas, { width, height, background = null, exposure = 1.0, warm = 0.9, cool = 0.6, fov = 30 } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: background === null, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(width, height, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = exposure;
  const scene = new THREE.Scene();
  if (background !== null) scene.background = new THREE.Color(background);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.6;
  const camera = new THREE.PerspectiveCamera(fov, width / height, 0.1, 100);
  camera.position.set(0, 0, 9);
  const key = new THREE.DirectionalLight(new THREE.Color(0xfff1dc), warm * 2.2);
  key.position.set(3, 4, 5);
  const rim = new THREE.DirectionalLight(new THREE.Color(0xb9b2ff), cool * 2.4);
  rim.position.set(-4, 2, -3);
  const fill = new THREE.HemisphereLight(0xffffff, 0xd8d2e8, 0.5);
  scene.add(key, rim, fill);
  return { renderer, scene, camera, THREE };
}

// ---------- premium additions (Aurora Glass direction) ----------
function gradientGeometry(geo, top, bottom) {
  // Vertex-colour gradient along Y so one mesh reads like a glossy gradient object.
  geo.computeBoundingBox();
  const { min, max } = geo.boundingBox, pos = geo.attributes.position, cols = [];
  const a = new THREE.Color(bottom), b = new THREE.Color(top), c = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    const k = (pos.getY(i) - min.y) / (max.y - min.y || 1);
    c.copy(a).lerp(b, k); cols.push(c.r, c.g, c.b);
  }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(cols, 3));
  return geo;
}

function glyph(kind) {
  const g = new THREE.Group(), m = new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.25, clearcoat: 1 });
  if (kind === "spark") {
    for (let i = 0; i < 4; i++) { const r = new THREE.Mesh(new THREE.CapsuleGeometry(0.045, 0.36, 6, 16), m); r.rotation.z = (i * Math.PI) / 4; g.add(r); }
  } else if (kind === "bubble") {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.22, 48, 32), m); b.scale.set(1.25, 0.95, 0.4); g.add(b);
    const tail = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.16, 16), m); tail.position.set(-0.17, -0.2, 0); tail.rotation.z = 0.7; g.add(tail);
  } else if (kind === "play") {
    const p = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.32, 3), m); p.rotation.z = -Math.PI / 2; p.scale.z = 0.4; g.add(p);
  } else if (kind === "pin") {
    const s = new THREE.Mesh(new THREE.SphereGeometry(0.16, 32, 32), m); s.position.y = 0.06; g.add(s);
    const c = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.24, 32), m); c.rotation.z = Math.PI; c.position.y = -0.13; g.add(c);
  } else if (kind === "lock") {
    const body = new THREE.Mesh(new RoundedBoxGeometry(0.36, 0.28, 0.1, 4, 0.05), m); body.position.y = -0.06; g.add(body);
    const sh = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.035, 12, 32, Math.PI), m); sh.position.y = 0.08; g.add(sh);
  } else if (kind === "eye") {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.2, 48, 32), m); e.scale.set(1.5, 0.8, 0.35); g.add(e);
    const p = new THREE.Mesh(new THREE.SphereGeometry(0.09, 32, 32), new THREE.MeshPhysicalMaterial({ color: 0x17141c, roughness: 0.2, clearcoat: 1 })); p.position.z = 0.06; g.add(p);
  }
  g.position.z = 0.2;
  return g;
}

objects.glossTile = function ({ top = 0xafa9ec, bottom = 0x4a44c4, glyphKind = "spark", size = 1 } = {}) {
  const g = new THREE.Group();
  const geo = gradientGeometry(new RoundedBoxGeometry(1.1 * size, 1.1 * size, 0.32 * size, 8, 0.3 * size), top, bottom);
  const tile = new THREE.Mesh(geo, new THREE.MeshPhysicalMaterial({ vertexColors: true, roughness: 0.22, clearcoat: 1, clearcoatRoughness: 0.06, sheen: 0.3 }));
  g.add(tile);
  const gl = glyph(glyphKind); gl.scale.setScalar(size); g.add(gl);
  return g;
};

// A frosted-glass dock holding glossy gradient tiles (hero for app/tool posts).
objects.glassDock = function ({ tiles = [["spark", 0xc9c1ff, 0x5a4fd6], ["bubble", 0x9cf0e4, 0x0e8c80], ["eye", 0xffd6a8, 0xd9772e]] } = {}) {
  const g = new THREE.Group();
  const w = tiles.length * 1.3 + 0.3;
  const dock = new THREE.Mesh(new RoundedBoxGeometry(w, 1.6, 0.3, 8, 0.48), new THREE.MeshPhysicalMaterial({ color: 0xe4e0ff, transmission: 0.25, roughness: 0.55, thickness: 0.6, ior: 1.35, clearcoat: 1, clearcoatRoughness: 0.2, transparent: true, opacity: 0.55, sheen: 0.6, sheenColor: new THREE.Color(0xc9c1ff) }));
  dock.position.z = -0.25; g.add(dock);
  tiles.forEach(([k, t, b], i) => { const tl = objects.glossTile({ top: t, bottom: b, glyphKind: k }); tl.position.x = (i - (tiles.length - 1) / 2) * 1.3; g.add(tl); });
  return g;
};

// Mascot v2: premium frosted-glass Dot with a glowing violet core.
export function glassMascot({ expression = "neutral", pose = "idle" } = {}) {
  const g = mascot({ expression, pose });
  const { body } = g.userData;
  body.material = new THREE.MeshPhysicalMaterial({ color: 0xd9d4ff, transmission: 0.82, roughness: 0.42, thickness: 1.1, ior: 1.38, clearcoat: 1, clearcoatRoughness: 0.18, attenuationColor: new THREE.Color(0x6a5ff0), attenuationDistance: 0.55, sheen: 0.4, sheenColor: new THREE.Color(0xb9b2ff) });
  const core = new THREE.Mesh(new THREE.SphereGeometry(0.33, 48, 48), new THREE.MeshStandardMaterial({ color: 0x5a4fd6, emissive: 0x5a4fd6, emissiveIntensity: 0.9, roughness: 0.6 }));
  core.position.set(0, -0.12, -0.05); core.scale.set(1.15, 1, 1);
  g.add(core);
  g.children.forEach((c) => { if (c.geometry && c.geometry.type === "CapsuleGeometry" && c !== body) c.material = body.material; });
  // little legs so it stands like a designer toy
  const legG = new THREE.CapsuleGeometry(0.085, 0.22, 6, 16);
  [-0.2, 0.2].forEach((x) => { const l = new THREE.Mesh(legG, body.material); l.position.set(x, -0.6, 0); g.add(l); });
  return g;
}
