"""Motion-graphics story reel: scenes in templates/video/stories/<name>.html (section.f, one per line), narration with word
timings (video-projects/<proj>/vo.mp3, vo_words.json, vo_lines_t.json), composed brand music ducked under the voice,
studio sound effects, captions that appear as the words are spoken. -14 LUFS.

    python scripts/story_reel.py mg-story-01 video-projects/mg-story-01 --mood="emotional, hopeful, building"
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from carousel_reel import SFX, SR, beats, compose, load  # noqa: E402
from render3d import serve  # noqa: E402

FPS = 30
KEY = re.compile(r"^(\d|robot|robots|debt|AI|A,|B,|job|salary|anywhere|euros|rejections|automatic|vote)", re.I)


def chunks(words):
    out, cur = [], []
    for k, w in enumerate(words):
        cur.append(w)
        end = w["w"][-1] in ".,?!:" or len(cur) == 3
        if end or k == len(words) - 1:
            html = " ".join(f"<b>{x['w'].strip('.,?!:')}</b>" if KEY.match(x["w"]) else x["w"].strip(".,?!:") for x in cur)
            out.append({"t0": cur[0]["s"], "t1": cur[-1]["e"] + (0.25 if end else 0.05), "html": html})
            cur = []
    for a, b in zip(out, out[1:]):
        a["t1"] = min(a["t1"], b["t0"])
    return out


def main(name, proj, mood):
    from playwright.sync_api import sync_playwright
    proj = Path(proj).resolve()
    words = json.loads((proj / "vo_words.json").read_text())
    lines = json.loads((proj / "vo_lines_t.json").read_text())
    vo = load(proj / "vo.mp3")
    end = len(vo) / SR + 1.4
    starts = [max(0.0, ln["t0"] - 0.15) for ln in lines]
    bounds = [[starts[i], starts[i + 1] if i + 1 < len(starts) else end] for i in range(len(starts))]
    js = (Path(__file__).parent / "story_reel.js").read_text()
    out = proj / f"{name}-9x16.mp4"
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(f"{base}/video/stories/{name}.html")
        pg.wait_for_function("window.READY === true")
        pg.add_script_tag(content=js)
        ev = pg.evaluate(f"R.init({json.dumps(bounds)}, {json.dumps(chunks(words))})")
        n = int(end * FPS)
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                                "-crf", "17", "-pix_fmt", "yuv420p", str(out.with_suffix(".video.mp4"))], stdin=subprocess.PIPE)
        for f in range(n):
            pg.evaluate(f"R.seek({f / FPS})")
            enc.stdin.write(pg.screenshot(type="jpeg", quality=92))
        enc.stdin.close()
        enc.wait()
        b.close()
    L = int(end * SR)
    voice = np.zeros((L, 2), np.float32)
    v = vo / (np.sqrt((vo ** 2).mean()) + 1e-9) * 0.1
    voice[:len(v)] = v[:L]
    music = load(compose(name, end + 1.0, mood))[:L]
    music = np.pad(music, ((0, max(0, L - len(music))), (0, 0)))
    env = np.convolve(np.abs(voice.mean(1)), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    duck = 1.0 - 0.72 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
    mus = music / (np.sqrt((music ** 2).mean()) + 1e-9) * 0.06 * duck[:, None]
    k = int(1.4 * SR)
    mus[-k:] *= np.linspace(1, 0, k)[:, None]
    mix = voice + mus
    cache = {}
    for t, s, g in ev:
        if s not in cache:
            cache[s] = load(SFX / f"{s}.mp3")
        x = cache[s]
        if s == "whoosh":
            t -= np.argmax(np.abs(x).mean(1)) / SR
        i0 = int(max(0, t) * SR)
        seg = x[:max(0, L - i0)] / (np.abs(x).max() + 1e-9) * {"whoosh": .16, "pop": .1, "impact": .22, "tick": .08, "ding": .12}.get(s, .1) * g
        mix[i0:i0 + len(seg)] += seg
    import soundfile as sf
    wav = out.with_suffix(".wav")
    sf.write(str(wav), np.clip(mix, -1, 1), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out.with_suffix(".video.mp4")), "-i", str(wav), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    out.with_suffix(".video.mp4").unlink()
    wav.unlink()
    print("->", out, f"{end:.1f} s")


if __name__ == "__main__":
    opt = dict(a[2:].split("=", 1) for a in sys.argv[3:] if a.startswith("--"))
    main(sys.argv[1], sys.argv[2], opt.get("mood", "emotional, hopeful"))
