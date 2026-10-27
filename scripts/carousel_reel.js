// Turns a week-series carousel page into a 9:16 motion reel. Injected by scripts/carousel_reel.py.
// Each slide is a card on warm paper; it swipes in like a real carousel, its pieces land one by one, lists reveal
// item by item, prompts type on, numbers count up, the keyword spells out. Deterministic: R.seek(t) sets every style.
(() => {
  const css = `
  html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#E7DFD1}
  #deck{position:absolute;inset:0}
  #deck .slide{position:absolute;left:0;top:0;transform-origin:0 0;border-radius:30px;box-shadow:0 50px 90px -40px rgba(40,25,5,.55);will-change:transform}
  .rv-hide{opacity:0}
  #grain{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 50% 40%,rgba(255,255,255,.35),rgba(0,0,0,.10) 75%)}`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  const g = document.createElement("div"); g.id = "grain"; document.body.prepend(g);

  const S = 0.96, X = 21.6, Y = 215;
  const slides = [...document.querySelectorAll("#deck .slide")];
  const easeOut = (x) => 1 - Math.pow(1 - x, 3);
  const back = (x) => { const c = 1.5; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const inOut = (x) => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  const cl = (x) => Math.max(0, Math.min(1, x));
  const STATIC = ["top", "dots", "handle"];
  const LISTS = [".rows", ".vs", ".in", ".chips", ".ba", ".gear"];

  // per slide: the pieces that animate, in reading order
  const plan = slides.map((sl) => {
    const parts = [];
    [...sl.children].forEach((el) => {
      if (STATIC.some((c) => el.classList.contains(c))) return;
      if (LISTS.some((q) => el.matches(q))) { parts.push({el, kind: "box", quiet: true}); [...el.children].forEach((c) => parts.push({el: c, kind: "item"})); return; }
      if (el.classList.contains("code")) { parts.push({el, kind: "code"}); return; }
      if (el.classList.contains("cta")) {
        parts.push({el, kind: "box"});
        const kw = el.querySelector(".kw");
        if (kw) { const t = kw.textContent; kw.innerHTML = [...t].map((c) => `<span>${c}</span>`).join(""); parts.push({el: kw, kind: "kw", n: t.length}); }
        return;
      }
      if (el.classList.contains("calc")) {
        parts.push({el, kind: "box"});
        const r = el.querySelector(".r");
        if (r) parts.push({el: r, kind: "count", txt: r.textContent});
        return;
      }
      if (el.classList.contains("sticker")) { parts.push({el, kind: "sticker"}); return; }
      if (el.classList.contains("face")) { parts.push({el, kind: "face"}); return; }
      if (el.classList.contains("big")) { parts.push({el, kind: "big", quiet: true}); return; }
      if (el.classList.contains("h")) { parts.push({el, kind: "head"}); return; }
      parts.push({el, kind: "fade"});
    });
    const words = (sl.innerText.match(/\S+/g) || []).length;
    return {sl, parts, words};
  });

  const DUR = {head: .5, fade: .45, item: .42, box: .4, code: 1.3, sticker: .45, face: .45, big: .6, kw: 0, count: .8};
  const GAP = {head: .2, fade: .12, item: .26, box: .1, code: .5, sticker: .2, face: .12, big: 0, kw: 0, count: .1};

  window.R = {
    measure: () => plan.map((p) => ({words: p.words, parts: p.parts.map((q) => q.kind),
                                     code: p.parts.filter((q) => q.kind === "code").map((q) => q.el.textContent.length)})),
    init(bounds, first) {
      // bounds[i] = [t0, t1] on screen (t0 = swipe-in end, t1 = swipe-out start); returns the sound events
      this.b = bounds; const ev = [];
      plan.forEach((p, i) => {
        let t = bounds[i][0] + (i === 0 ? 0 : .05);
        p.parts.forEach((q, k) => {
          if (i === 0 && k <= p.parts.findIndex((z) => z.kind === "head")) { q.t = -1; return; }  // the hook is readable on frame one
          q.t = t;
          if (q.kind === "kw") { q.t = t; q.step = .085; t += q.n * q.step + .2; q.n && [...Array(q.n)].forEach((_, j) => ev.push([t - .2 - (q.n - j) * q.step, "click", .5 + .05 * j])); return; }
          if (q.kind === "code") { q.d = Math.min(2.2, .35 + q.el.textContent.length / 260); ev.push([t, "type", q.d]); t += q.d * .6; return; }
          if (q.kind === "count") { ev.push([t, "tick", .8]); ev.push([t + DUR.count, "ding", 1]); }
          if (!q.quiet) ev.push([t, {sticker: "pop", face: "pop", item: "pop", head: "whoosh_soft"}[q.kind] || "click", {sticker: 1, face: .8, item: .9, head: .7}[q.kind] || .45]);
          t += GAP[q.kind];
        });
        if (i > 0) ev.push([bounds[i][0] - .2, "whoosh", 1]);
      });
      return ev;
    },
    seek(t) {
      plan.forEach((p, i) => {
        const [a, b] = this.b[i], sw = .42;
        let x = 0, rot = 0, sc = S;
        if (i > 0 && t < a) { const u = inOut(cl((t - (a - sw)) / sw)); x = (1 - u) * 1180; rot = (1 - u) * 4; }
        if (i < plan.length - 1 && t > b) { const u = inOut(cl((t - b) / sw)); x = -u * 1180; rot = -u * 4; }
        const vis = !(i > 0 && t < a - sw) && !(i < plan.length - 1 && t > b + sw);
        p.sl.style.display = vis ? "block" : "none";
        if (!vis) return;
        const push = 1 + .025 * cl((t - a) / Math.max(.1, b - a));  // a slow camera push while it holds
        p.sl.style.transform = `translate(${X + x}px,${Y}px) rotate(${rot}deg) scale(${sc * push})`;
        p.parts.forEach((q) => {
          const el = q.el, d = q.d || DUR[q.kind], u = q.t < 0 ? 1 : cl((t - q.t) / d);
          if (q.kind === "kw") { [...el.children].forEach((c, j) => { c.style.opacity = t >= q.t + j * q.step ? 1 : 0; }); return; }
          if (q.kind === "code") {
            el.style.opacity = cl(u * 6); el.style.clipPath = `inset(0 0 ${(1 - easeOut(u)) * 100}% 0 round 24px)`; return;
          }
          if (q.kind === "count") {
            const m = q.txt.match(/^([^\d]*)([\d,]+(?:\.\d+)?)(.*)$/);
            if (m) { const v = parseFloat(m[2].replace(/,/g, "")), dec = (m[2].split(".")[1] || "").length, cur = v * easeOut(u);
              el.textContent = m[1] + cur.toLocaleString("en-GB", {minimumFractionDigits: dec, maximumFractionDigits: dec}) + m[3]; }
            return;
          }
          const e = q.kind === "sticker" || q.kind === "face" ? back(u) : easeOut(u);
          el.style.opacity = cl(u * 2.2);
          const base = el.dataset.tf ?? (el.dataset.tf = el.style.transform || "");
          if (q.kind === "sticker" || q.kind === "face") el.style.transform = `${base} scale(${.4 + .6 * e})`;
          else if (q.kind === "big") el.style.transform = `${base} translateX(${(1 - e) * 120}px)`;
          else if (q.kind === "head") { el.style.transform = `${base} translateY(${(1 - e) * 50}px)`; el.style.filter = `blur(${(1 - u) * 10}px)`; }
          else el.style.transform = `${base} translateY(${(1 - e) * 36}px)`;
        });
      });
    },
  };
})();
