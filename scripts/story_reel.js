// Motion-graphics story engine (CONTENT-OS: motion-graphics stories). Scenes = section.f, one per spoken line.
// R.init(bounds, chunks) -> sound events; R.seek(t) sets every style (deterministic, frame by frame).
(() => {
  const S = [...document.querySelectorAll("section.f")];
  const cc = document.getElementById("cc");
  const cl = (x) => Math.max(0, Math.min(1, x)), eo = (x) => 1 - Math.pow(1 - x, 3);
  const back = (x) => { const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const num = /^\s*(€?)([\d,]+)(\D*)$/;
  const plan = S.map((s) => {
    const parts = [];
    [...s.children].forEach((el) => {
      if (el.classList.contains("mat") || el.classList.contains("cap")) return;
      const kind = el.classList.contains("stamp") ? "slam" : el.classList.contains("badge") ? "pop" : "rise";
      parts.push({el, kind});
      el.querySelectorAll("div").forEach((d) => { if (!d.children.length && num.test(d.textContent) && parseInt(d.textContent.replace(/\D/g, "")) >= 100) parts.push({el: d, kind: "count", txt: d.textContent}); });
      if (el.matches("div") && !el.children.length && num.test(el.textContent) && parseInt(el.textContent.replace(/\D/g, "")) >= 100) parts[parts.length - 1] = {el, kind: "count", txt: el.textContent};
    });
    return {s, parts, paper: s.classList.contains("paper")};
  });
  window.R = {
    init(bounds, chunks) {
      this.b = bounds; this.c = chunks; const ev = [];
      plan.forEach((p, i) => {
        let t = bounds[i][0] + (i === 0 ? 0 : 0.12);
        if (i > 0) ev.push([bounds[i][0], "whoosh", 1]);
        p.parts.forEach((q, k) => {
          q.t = i === 0 && k < 2 ? -1 : t;
          if (q.kind === "slam") ev.push([t + 0.12, "impact", 1]);
          else if (q.kind === "count") { ev.push([t, "tick", 1]); ev.push([t + 0.9, "ding", 0.8]); }
          else if (q.kind === "pop") ev.push([t, "pop", 0.8]);
          else if (k > 0) ev.push([t, "pop", 0.35]);
          t += q.kind === "count" ? 0.2 : 0.16;
        });
      });
      return ev;
    },
    seek(t) {
      plan.forEach((p, i) => {
        const [a, b] = this.b[i], tr = 0.28;
        const vis = t >= a - 0.001 && t < (i + 1 < plan.length ? this.b[i + 1][0] : 1e9);
        p.s.style.display = vis ? "block" : "none";
        if (!vis) return;
        const u = i === 0 ? 1 : eo(cl((t - a) / tr));
        const push = 1 + 0.045 * cl((t - a) / Math.max(0.5, b - a));
        p.s.style.transform = `scale(${(1.14 - 0.14 * u) * push})`;
        p.s.style.filter = u < 1 ? `blur(${(1 - u) * 14}px)` : "none";
        p.s.style.opacity = i === 0 ? 1 : cl(u * 1.6);
        p.parts.forEach((q) => {
          const el = q.el, v = q.t < 0 ? 1 : cl((t - q.t) / (q.kind === "count" ? 0.9 : 0.45));
          const base = el.dataset.tf ?? (el.dataset.tf = el.style.transform || "");
          if (q.kind === "count") { const m = q.txt.match(num), n = parseInt(m[2].replace(/,/g, "")); el.textContent = m[1] + Math.round(n * eo(v)).toLocaleString("en-GB") + m[3]; return; }
          el.style.opacity = cl(v * 2.5);
          if (q.kind === "slam") el.style.transform = `${base} scale(${2.2 - 1.2 * eo(v)})`;
          else if (q.kind === "pop") el.style.transform = `${base} scale(${0.3 + 0.7 * back(v)})`;
          else el.style.transform = `${base} translateY(${(1 - eo(v)) * 46}px)`;
        });
        document.body.classList.toggle("paperon", p.paper);
      });
      const c = this.c.find((x) => t >= x.t0 && t < x.t1);
      if (c) { if (cc.dataset.k !== String(c.t0)) { cc.innerHTML = c.html; cc.dataset.k = String(c.t0); } const v = cl((t - c.t0) / 0.12); cc.style.transform = `scale(${0.88 + 0.12 * back(v)})`; cc.style.opacity = 1; }
      else cc.style.opacity = 0;
    },
  };
})();
