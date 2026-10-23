// Shared Shorts captions: up to 3 words a group, each word flips up in 3D as it's said, an amber box with
// corner handles slides to the spoken word. Deterministic from t. Needs #capline inside #cap (shorts.css).
window.Captions = (() => {
  let CAPS = [], shown = -1, box = null;
  function build(spec) {
    CAPS = [];
    spec.lines.forEach((ln, li) => {
      let g = [];
      ln.words.forEach((w, wi) => {
        g.push(w);
        const end = /[.,?!:]$/.test(w.w) || g.length === 3 || wi === ln.words.length - 1;
        if (end) { CAPS.push({li, words: g, start: g[0].start - (CAPS.length ? 0.06 : 0.25), end: g[g.length - 1].end}); g = []; }
      });
    });
    CAPS.forEach((c, i) => { c.until = i + 1 < CAPS.length ? Math.min(CAPS[i + 1].start, c.end + 0.6) : c.end + 0.6; });
  }
  function draw(t) {
    const line = document.getElementById('capline');
    const ci = CAPS.findIndex(c => t >= c.start && t < c.until);
    if (ci !== shown) {
      line.innerHTML = '';
      if (ci >= 0) {
        box = document.createElement('div'); box.id = 'wbox';
        box.innerHTML = '<i style="left:-7px;top:-7px"></i><i style="right:-7px;top:-7px"></i><i style="left:-7px;bottom:-7px"></i><i style="right:-7px;bottom:-7px"></i>';
        line.appendChild(box);
        CAPS[ci].words.forEach(w => { const s = document.createElement('span'); s.textContent = w.w.replace(/[.,!:]$/, ''); line.appendChild(s); });
      }
      shown = ci;
    }
    if (ci < 0) return;
    const c = CAPS[ci], spans = [...line.querySelectorAll('span')];
    let act = 0;
    c.words.forEach((w, i) => {
      const p = Math.min(1, Math.max(0, (t - w.start + 0.1) / 0.2)), e = 1 - Math.pow(1 - p, 3);
      spans[i].style.transform = `rotateX(${(1 - e) * -95}deg) translateY(${(1 - e) * 30}px)`;
      spans[i].style.opacity = e;
      if (t >= w.start - 0.02) act = i;
    });
    spans.forEach((s, i) => s.classList.toggle('on', i === act));
    const lr = line.getBoundingClientRect(), r = spans[act].getBoundingClientRect();
    const pr = act > 0 ? spans[act - 1].getBoundingClientRect() : r;
    const k = Math.min(1, Math.max(0, (t - c.words[act].start) / 0.12)), e = 1 - Math.pow(1 - k, 3);
    const L = pr.left + (r.left - pr.left) * e, W = pr.width + (r.width - pr.width) * e;
    Object.assign(box.style, {left: (L - lr.left - 14) + 'px', top: (r.top - lr.top - 4) + 'px', width: (W + 28) + 'px', height: (r.height + 8) + 'px',
      opacity: Math.min(1, Math.max(0, (t - c.words[0].start + 0.05) / 0.12))});
  }
  return {build, draw};
})();
