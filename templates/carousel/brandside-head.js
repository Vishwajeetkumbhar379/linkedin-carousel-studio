// Shared chrome for the "From the brand side" and "Sound human" carousels (week-series.css system).
window.deck = (series, slides) => {
  const N = slides.length;
  const top_ = (i) => `<div class="top"><span>Build with Vish · ${series}</span><span>${String(i).padStart(2, "0")} / ${N}</span></div>`;
  const dots = (i) => `<div class="dots">${Array.from({length: N}, (_, k) => `<i class="${k + 1 === i ? "on" : ""}"></i>`).join("")}</div><div class="handle">@buildwith.vish</div>`;
  document.getElementById("deck").innerHTML = slides.map((f, k) => {
    const [cls, html] = f(k + 1);
    return `<section class="slide ${cls}">${top_(k + 1)}${html}${dots(k + 1)}</section>`;
  }).join("");
  Promise.all([...document.images].map((im) => im.decode().catch(() => {}))).then(() => document.fonts.ready).then(() => { window.READY = true; });
};
