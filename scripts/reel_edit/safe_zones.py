"""Instagram safe zones for 9:16 Reels: find text that the app's own UI will cover, before anything is posted.

    python scripts/reel_edit/safe_zones.py check video-projects/<slug> [--step=0.2]   # every text on screen, from comp.html
    python scripts/reel_edit/safe_zones.py preview <video.mp4> [--every=3] [--out=...]  # phone preview sheet with the UI zones shaded

Zones for a 1080x1920 frame (Vish's phone, 23 Oct 2026: the top bar hid "Life is" and the week label; Meta's
ad specs say the same). Key text, titles, labels and captions stay inside the safe box; faces and backgrounds may
run under the UI.
- top 14%: status bar + the Reels/Trial reels header
- bottom 35%: caption, username, audio, progress bar (captions sit at 58 to 66% of the height)
- right 14% from 40% down: like, comment, share, save buttons
- sides 6%: tall phones crop the 9:16 frame at the edges
- his face (Vish, 23 Oct: "some of the captions were literally on my mouth"): no text, caption or sticker may be drawn
  over his face. Words that sit BEHIND him (the person matte drawn on top) are fine, and wanted: they look 3D.
  The check finds faces with YuNet (OpenCV, /home/user/models) and compares each frame with and without the text: if
  the pixels on the face change, something is drawn over it.
`check` exits 1 when any text is outside the safe box or on his face, so a render script can stop on it.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

W, H = 1080, 1920
ZONES = {  # name: (x0, y0, x1, y1) in pixels of a 1080x1920 frame
    "top bar": (0, 0, W, round(H * 0.14)),
    "caption area": (0, round(H * 0.65), W, H),
    "buttons": (round(W * 0.86), round(H * 0.40), W, H),
    "left edge": (0, 0, round(W * 0.06), H),
    "right edge": (round(W * 0.94), 0, W, H),
}

JS = """() => {
  const out = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const s = n.textContent.trim();
    if (!s) continue;
    let el = n.parentElement, op = 1, hidden = false;
    for (let e = el; e && e !== document.body; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden') { hidden = true; break; }
      op *= parseFloat(cs.opacity || '1');
    }
    if (hidden || op < 0.15) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    for (const b of r.getClientRects()) {
      if (b.width < 2 || b.height < 2) continue;
      if (b.right < 0 || b.bottom < 0 || b.left > innerWidth || b.top > innerHeight) continue;
      out.push({text: s.slice(0, 40), x0: b.left, y0: b.top, x1: b.right, y1: b.bottom});
    }
  }
  return out;
}"""


HIDE_TEXT = """() => {
  const els = new Set();
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) if (n.textContent.trim() && n.parentElement) els.add(n.parentElement);
  window.__hid = [...els].map(e => [e, e.style.visibility]);
  window.__hid.forEach(([e]) => e.style.visibility = 'hidden');
}"""
SHOW_TEXT = "() => { (window.__hid || []).forEach(([e, v]) => e.style.visibility = v); window.__hid = []; }"
YUNET = "/home/user/models/face_detection_yunet_2023mar.onnx"


def faces(img) -> list[tuple[int, int, int, int]]:
    import cv2
    h, w = img.shape[:2]
    det = cv2.FaceDetectorYN.create(YUNET, "", (w, h), 0.75)
    _, f = det.detect(img)
    out = []
    for r in (f if f is not None else []):
        x, y, fw, fh = (int(v) for v in r[:4])
        if fw < 40:  # tiny faces (photos in the background) don't count
            continue
        out.append((max(0, x - fw // 10), max(0, y - fh // 20), min(w, x + fw + fw // 10), min(h, y + fh + fh // 5)))  # incl. chin
    return out


def on_face(shot_with, shot_without) -> list[tuple[int, int, int, int]]:
    import cv2
    import numpy as np
    a = cv2.imdecode(np.frombuffer(shot_with, np.uint8), cv2.IMREAD_COLOR)
    b = cv2.imdecode(np.frombuffer(shot_without, np.uint8), cv2.IMREAD_COLOR)
    bad = []
    for x0, y0, x1, y1 in faces(b):
        d = cv2.absdiff(a[y0:y1, x0:x1], b[y0:y1, x0:x1]).max(axis=2)
        if (d > 40).mean() > 0.01:  # more than 1% of the face changed: something is drawn on it
            bad.append((x0, y0, x1, y1))
    return bad


def hits(box: dict) -> list[str]:
    return [z for z, (a, b, c, d) in ZONES.items() if box["x0"] < c and box["x1"] > a and box["y0"] < d and box["y1"] > b]


def check(project: Path, step: float = 0.2, face_step: float = 0.5) -> int:
    from playwright.sync_api import sync_playwright
    tl = json.loads((project / "work" / "timeline.json").read_text())
    found: dict[tuple[str, str], list[float]] = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--allow-file-access-from-files", "--disable-web-security"])
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(f"file://{(project / 'edit' / 'comp.html').resolve()}")
        pg.evaluate("tl => init(tl)", tl)
        pg.evaluate("document.fonts.ready.then(() => true)")
        t, next_face = 0.0, 0.0
        while t < tl["dur"]:
            pg.evaluate("t => render(t)", t)
            boxes = pg.evaluate(JS)
            for box in boxes:
                for z in hits(box):
                    found.setdefault((box["text"], z), []).append(round(t, 1))
            if boxes and t >= next_face:
                with_text = pg.screenshot(type="jpeg", quality=90)
                pg.evaluate(HIDE_TEXT)
                without = pg.screenshot(type="jpeg", quality=90)
                pg.evaluate(SHOW_TEXT)
                for fx0, fy0, fx1, fy1 in on_face(with_text, without):
                    over = [bx["text"] for bx in boxes if bx["x0"] < fx1 and bx["x1"] > fx0 and bx["y0"] < fy1 and bx["y1"] > fy0]
                    found.setdefault((" ".join(over)[:40] or "(graphic)", "ON HIS FACE"), []).append(round(t, 1))
                next_face = t + face_step
            t += step
        b.close()
    if not found:
        print("safe zones: PASS, no text under Instagram's UI or on his face")
        return 0
    nf = sum(1 for k in found if k[1] == "ON HIS FACE")
    print(f"safe zones: FAIL, {len(found) - nf} text items under Instagram's UI, {nf} on his face")
    for (txt, z), ts in sorted(found.items(), key=lambda kv: kv[1][0]):
        print(f"  {ts[0]:6.1f}s to {ts[-1]:6.1f}s  [{z}]  {txt!r}")
    return 1


def preview(video: Path, every: float = 3.0, out: Path | None = None) -> Path:
    """Contact sheet of the video with the zones shaded red, the way a phone shows it."""
    out = out or video.with_name(video.stem + "-safe-zones.jpg")
    boxes = ",".join(f"drawbox=x={a}:y={b}:w={c - a}:h={d - b}:color=red@0.28:t=fill" for a, b, c, d in ZONES.values())
    vf = f"fps=1/{every},scale={W}:{H},{boxes},scale=270:-2,tile=8x0"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                               capture_output=True, text=True).stdout or 0)
    rows = max(1, int(dur / every / 8) + 1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", vf.replace("tile=8x0", f"tile=8x{rows}"),
                    "-frames:v", "1", "-q:v", "3", str(out)], check=True)
    print("preview ->", out)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = {k.lstrip("-"): v for k, _, v in (x.partition("=") for x in a if x.startswith("--"))}
    pos = [x for x in a if not x.startswith("--")]
    if pos and pos[0] == "check":
        sys.exit(check(Path(pos[1]), float(opt.get("step", 0.2))))
    elif pos and pos[0] == "preview":
        preview(Path(pos[1]), float(opt.get("every", 3)), Path(opt["out"]) if "out" in opt else None)
    else:
        print(__doc__)
