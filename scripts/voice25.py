"""The locked voice for every video: video #25's exact recipe (Vish, 8 Oct 2026: "I only like post 25 VO").

    python scripts/voice25.py out/<post> [out/<post> ...] [--force] [--realign] [--render] [--jobs=3]

#25 is out/batch-01/ai-creators-cheap-trust-isnt: gemini-3.8-flash-lite-tts, prebuilt voice Puck, the relaxed
style in brand/tokens.json, the WHOLE script read in one request, lines aligned by transcription, then
0.32 s after each line and 0.6 s after each scene (tokens voice.voiceover.pause_s).

Template videos (video.json): writes voice.wav, voice.json and the beat timings, like scripts/voiceover.py.
Bespoke reels (lines.json): writes voice.wav and voice.json {"lines": [...]} for scripts/render_reel.py.
Every raw take is kept as voice25-take.wav; --realign re-times a post from it without a new request.
A take that drops or garbles words is re-read once.
Posts already on the recipe are skipped unless --force. --render re-renders the voiced posts afterwards
(template videos via make_batch, reels via render_reel) and writes the 9:16 export.
Free tier: 10 requests a day for this model, reset at 00:00 UTC. Exits with code 3 when the cap is
reached, after rendering what was voiced, so a queue can resume the next day.
"""
from __future__ import annotations

import difflib
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODEL, VOICE = "gemini-3.8-flash-lite-tts", "Puck"
os.environ["GEMINI_TTS_MODEL"] = MODEL  # voiceover reads it at import: never another model (another model is another voice)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import soundfile as sf  # noqa: E402
import voiceover as vo  # noqa: E402

assert vo.GEMINI_MODEL == MODEL
REFERENCE = "ai-creators-cheap-trust-isnt"
HEARD: dict = {}
REALIGN = "--realign" in sys.argv
_stt = vo._stt_words


def _recording_stt(audio):
    HEARD["words"] = _stt(audio)
    return HEARD["words"]


vo._stt_words = _recording_stt


def on_recipe(d: Path) -> bool:
    if d.name == REFERENCE:
        return True
    if (d / "lines.json").exists():
        f = d / "voice.json"
        return f.exists() and json.loads(f.read_text()).get("recipe") == "video-25"
    return (json.loads((d / "video.json").read_text()).get("voice") or {}).get("recipe") == "video-25"


def reel_narration(cfg: dict) -> list[list[str]]:
    """Lines in pairs like #25's scenes, with a scene break wherever lines.json asks for a longer pause."""
    breaks = {int(k) for k in cfg.get("pause_after", {})}
    scenes, cur = [], []
    for i, ln in enumerate(cfg["lines"]):
        cur.append(ln)
        if i in breaks or len(cur) == 2 or i == len(cfg["lines"]) - 1:
            scenes.append(cur)
            cur = []
    return scenes


def check(audio, timings: list[dict], narration: list[list[str]]) -> tuple[float, list[str]]:
    """Share of script words heard in the take, plus problems (dropped words, odd pace, broken alignment)."""
    ours = [w for sc in narration for p in sc for w in vo._norm_words(p)]
    heard = HEARD.get("words")
    problems = []
    if heard:
        sm = difflib.SequenceMatcher(a=ours, b=[w for w, _, _ in heard], autojunk=False)
        cover = sum(b.size for b in sm.get_matching_blocks()) / len(ours)
    else:
        cover = 1.0
        problems.append("no transcript: lines placed at pauses")
    if cover < 0.88:
        problems.append(f"only {cover:.0%} of the script heard")
    wps = len(ours) / (len(audio) / vo.SR)
    if not 1.8 <= wps <= 3.4:
        problems.append(f"pace {wps:.2f} words/s")
    for tm in timings:
        for p in tm["phrases"]:
            n, dur = len(vo._norm_words(p["text"])), p["end"] - p["start"]
            if dur < 0.18 * n or dur > 1.2 * n + 1.0:
                problems.append(f"line '{p['text'][:30]}' lasts {dur:.2f}s")
    return cover, problems


def from_saved(d: Path, narration: list[list[str]]):
    """synth_gemini's alignment, on the saved take (0.2 s lead, then the trimmed read)."""
    audio, _ = sf.read(str(d / "voice25-take.wav"), dtype="float32")
    lead = 0.2
    flat = [p for sc in narration for p in sc]
    bounds = vo.phrase_bounds(audio[int(lead * vo.SR):], flat)
    timings, k = [], 0
    for sc in narration:
        ph = [{"text": p, "start": round(lead + bounds[k + i][0], 3), "end": round(lead + bounds[k + i][1], 3)} for i, p in enumerate(sc)]
        k += len(sc)
        timings.append({"start": ph[0]["start"], "end": ph[-1]["end"], "phrases": ph})
    return audio, timings


def take(d: Path, narration: list[list[str]]):
    if REALIGN and (d / "voice25-take.wav").exists():
        HEARD.clear()
        audio, timings = from_saved(d, narration)
        cover, problems = check(audio, timings, narration)
        print(f"  saved take: {len(audio) / vo.SR:.1f}s, {cover:.0%} heard{'; ' + '; '.join(problems) if problems else ''}", flush=True)
        return audio, timings, cover, problems
    best = None
    for attempt in range(2):
        HEARD.clear()
        audio, timings = vo.synth_gemini(narration, VOICE, vo.GEMINI_STYLE)
        cover, problems = check(audio, timings, narration)
        print(f"  take {attempt + 1}: {len(audio) / vo.SR:.1f}s, {cover:.0%} heard{'; ' + '; '.join(problems) if problems else ''}", flush=True)
        if best is None or (len(problems), -cover) < (len(best[3]), -best[2]):
            best = (audio, timings, cover, problems)
        if not any("heard" in p or "lasts" in p for p in problems):
            break
    sf.write(d / "voice25-take.wav", best[0], vo.SR)
    return best


def voice(d: Path) -> str:
    if (d / "lines.json").exists():  # bespoke reel
        cfg = json.loads((d / "lines.json").read_text())
        narration = reel_narration(cfg)
        audio, timings, cover, problems = take(d, narration)
        work = d / ".v25"
        work.mkdir(exist_ok=True)
        spec_path = work / "video.json"
        spec = {"narration": narration}
        spec_path.write_text(json.dumps(spec))
        vo.finish(spec_path, spec, audio, timings, "gemini-oneshot", VOICE, True, False)
        shutil.move(work / "voice.wav", d / "voice.wav")
        v = json.loads((work / "voice.json").read_text())
        lines = [{"text": p["text"], "start": p["start"], "end": p["end"]} for sc in v["scenes"] for p in sc["phrases"]]
        (d / "voice.json").write_text(json.dumps({"reference": f"video #25 {REFERENCE}", "engine": MODEL, "voice": VOICE, "recipe": "video-25",
                                                  "heard": round(cover, 3), "duration": v["duration"], "lines": lines}, indent=1))
        shutil.rmtree(work)
    else:  # template video
        spec_path = d / "video.json"
        spec = json.loads(spec_path.read_text())
        audio, timings, cover, problems = take(d, spec["narration"])
        vo.finish(spec_path, spec, audio, timings, "gemini-oneshot", VOICE, True, False)
    dur = json.loads((d / "voice.json").read_text())["duration"]
    return f"{d.name}: {dur:.1f}s, {cover:.0%} heard" + (f" (check: {'; '.join(problems)})" if problems else "")


def render(d: Path) -> str:
    py = sys.executable
    if (d / "lines.json").exists():
        r = subprocess.run([py, str(ROOT / "scripts/render_reel.py"), str(d), d.name], capture_output=True, text=True)
    else:
        (d / "video.mp4").unlink(missing_ok=True)
        code = f"import sys; sys.path.insert(0,'scripts'); import make_batch as m; from pathlib import Path; s=Path({str(d / 'video.json')!r}); m.finish(s); r=m.render(s); print(r); sys.exit(0 if r.endswith(': ok') else 1)"
        r = subprocess.run([py, "-c", code], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0 or not (d / "video.mp4").exists():
        return f"{d.name}: RENDER FAILED {(r.stdout + r.stderr)[-300:]}"
    sys.path.insert(0, str(ROOT / "scripts"))
    import export_vertical
    export_vertical.vertical(d)
    return f"{d.name}: rendered + 9:16"


def main(args: list[str]) -> int:
    posts = [Path(a) for a in args if not a.startswith("--")]
    force, do_render = "--force" in args, "--render" in args
    jobs = int(next((a.split("=")[1] for a in args if a.startswith("--jobs=")), 3))
    done, code = [], 0
    for d in posts:
        if not force and not REALIGN and on_recipe(d):
            print(f"{d.name}: already the #25 voice, skipped", flush=True)
            continue
        print(f"== {d.name}", flush=True)
        try:
            print(voice(d), flush=True)
            done.append(d)
        except vo.DailyCap as e:
            print(f"DAILY CAP: {e}. Resume after 00:00 UTC.", flush=True)
            code = 3
            break
        except Exception as e:  # noqa: BLE001
            print(f"FAILED {d.name}: {e}", flush=True)
    if do_render and done:
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            for r in ex.map(render, done):
                print(r, flush=True)
    print(f"VOICED {len(done)}: {' '.join(d.name for d in done)}", flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
