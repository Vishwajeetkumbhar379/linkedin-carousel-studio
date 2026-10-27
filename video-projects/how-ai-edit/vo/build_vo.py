"""Build the film's voiceover from vo/plan.json: Vish's real takes, cleaned, plus his ElevenLabs clone for
the lines he did not film.

    python3 video-projects/how-ai-edit/vo/build_vo.py [--no-isolate]

1. Cut each real part from week-02-talks/raw (a hair of padding, 10 ms fades), join lines with short gaps.
2. Clean the real voice with ElevenLabs Voice Isolator (removes room echo and noise, like Adobe's Enhance).
   It costs about 1,000 credits a minute of audio; the key is CLAUDEELEVENLABS_API (the workspace with his clone).
3. Speak the missing lines with his clone (voice "Young indian male").
4. Match levels (-18 LUFS per line), a gentle high-pass, de-ess and compressor, so real and clone sit together.
Writes vo/vo_raw.wav (untouched cut, for A/B), vo/vo.wav and public/vo.wav, and vo/lines.json (where each line sits).
"""
import io
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "week-02-talks" / "raw"
SR = 48000
VOICE = "rRDZHYKovM5FXW92Zoxe"  # "Young indian male", Vish's clone
KEY = os.environ.get("CLAUDEELEVENLABS_API", "")
GAP_PART, GAP_LINE = 0.14, 0.42


def decode(args: list[str]) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", *args, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def fade(x: np.ndarray, ms: float = 10) -> np.ndarray:
    n = min(len(x) // 2, int(SR * ms / 1000))
    if n:
        r = np.linspace(0, 1, n, dtype=np.float32)
        x[:n] *= r
        x[-n:] *= r[::-1]
    return x


ISO = HERE / "iso"


def source(clip: str, iso: bool) -> np.ndarray:
    """The clip's audio; cleaned by the Voice Isolator once and cached in vo/iso/ (cutting again costs nothing)."""
    x = decode(["-i", str(RAW / f"{clip}.MOV")])
    if not iso:
        return x
    f = ISO / f"{clip}.wav"
    if not f.exists():
        ISO.mkdir(exist_ok=True)
        sf.write(f, isolate(x), SR, subtype="PCM_24")
    return sf.read(f, dtype="float32")[0]


def snap(x: np.ndarray, t: float, reach: float = 0.09) -> float:
    """Move a cut to the quietest 10 ms within `reach` of t, so it falls in the gap between words, not on one."""
    hop = int(0.01 * SR)
    a, b = max(0, int((t - reach) * SR)), min(len(x) - hop, int((t + reach) * SR))
    if b <= a:
        return t
    e = [float(np.mean(x[i:i + hop] ** 2)) for i in range(a, b, hop)]
    return (a + int(np.argmin(e)) * hop + hop // 2) / SR


CUTS: list[dict] = []  # every real part as cut: clip, its in and out points (after snapping), its length


def cut(x: np.ndarray, a: float, b: float, clip: str = "") -> np.ndarray:
    a, b = snap(x, a), snap(x, b)
    if clip:
        CUTS.append({"clip": clip, "src": [round(a, 3), round(b, 3)]})
    return fade(x[int(a * SR): int(b * SR)].copy())


def api(path: str, body: bytes, ctype: str) -> bytes:
    req = urllib.request.Request("https://api.elevenlabs.io" + path, data=body, method="POST",
                                 headers={"xi-api-key": KEY, "Content-Type": ctype, "Accept": "audio/mpeg"})
    return urllib.request.urlopen(req, timeout=300).read()


def isolate(x: np.ndarray) -> np.ndarray:
    buf = io.BytesIO(); sf.write(buf, x, SR, format="WAV", subtype="PCM_16")
    b = "----vishbound"
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"vo.wav\"\r\nContent-Type: audio/wav\r\n\r\n").encode() + buf.getvalue() + f"\r\n--{b}--\r\n".encode()
    mp3 = api("/v1/audio-isolation", body, f"multipart/form-data; boundary={b}")
    y = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], input=mp3, capture_output=True, check=True).stdout
    y = np.frombuffer(y, np.float32).copy()
    return np.pad(y, (0, max(0, len(x) - len(y))))[: len(x)]  # same timing as the input


def clone(text: str) -> np.ndarray:
    body = json.dumps({"text": text, "model_id": "eleven_multilingual_v2",
                       "voice_settings": {"stability": 0.45, "similarity_boost": 0.9, "style": 0.15, "use_speaker_boost": True}}).encode()
    mp3 = api(f"/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128", body, "application/json")
    y = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], input=mp3, capture_output=True, check=True).stdout
    y = np.frombuffer(y, np.float32).copy()
    nz = np.where(np.abs(y) > 0.01)[0]  # trim the model's leading and trailing air
    return fade(y[max(0, nz[0] - int(0.05 * SR)): nz[-1] + int(0.1 * SR)]) if len(nz) else y


def level(x: np.ndarray, target: float = -18.0) -> np.ndarray:
    m = pyln.Meter(SR)
    try:
        return pyln.normalize.loudness(x, m.integrated_loudness(x), target).astype(np.float32)
    except ValueError:
        return x


def polish(x: np.ndarray) -> np.ndarray:
    """Gentle and real: high-pass the rumble, tame the S's, even the level, nothing that changes the voice."""
    buf = io.BytesIO(); sf.write(buf, x, SR, format="WAV", subtype="FLOAT")
    af = "highpass=f=80,deesser=i=0.35,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=2,alimiter=limit=0.89"
    y = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-af", af, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], input=buf.getvalue(), capture_output=True, check=True).stdout
    return np.frombuffer(y, np.float32).copy()


if __name__ == "__main__":
    plan = json.loads((HERE / "plan.json").read_text())
    use_iso = "--no-isolate" not in sys.argv
    gap = lambda s: np.zeros(int(SR * s), np.float32)
    # real lines first, kept apart, so the isolator sees only his voice and we know where each one sits
    clips = {c for ln in plan["lines"] for c, _, _ in ln.get("parts", [])}
    src = {c: source(c, use_iso and bool(KEY)) for c in clips}
    raw_src = {c: source(c, False) for c in clips}
    real, out_real = {}, {}
    for ln in plan["lines"]:
        if "parts" in ln:
            for store, S in ((out_real, src), (real, raw_src)):
                segs = []
                for i, (c, a, b) in enumerate(ln["parts"]):
                    segs += ([gap(GAP_PART if not (ln["n"] == 1 and i == 1) else 0.3)] if i else []) + [cut(S[c], a, b, c if store is out_real else "")]
                store[ln["n"]] = np.concatenate(segs)
    vo, vo_raw, lines, t = [], [], [], 0.0
    for ln in plan["lines"]:
        n = ln["n"]
        if "parts" in ln:
            x, xr = level(out_real[n]), level(real[n])
        else:
            x = level(clone(ln["clone"])) if KEY else gap(2.0)
            xr = x
        parts = []
        if "parts" in ln:
            pt = t
            for i, _ in enumerate(ln["parts"]):
                c = CUTS.pop(0)
                if i:
                    pt += GAP_PART if not (n == 1 and i == 1) else 0.3
                parts.append({**c, "at": round(pt + 0.25, 3)})
                pt += c["src"][1] - c["src"][0]
        lines.append({"n": n, "start": round(t, 3), "end": round(t + len(x) / SR, 3), "text": ln.get("text") or ln["clone"], "voice": "clone" if "clone" in ln else "vish", "parts": parts})
        vo += [x, gap(GAP_LINE)]; vo_raw += [xr, gap(GAP_LINE)]
        t += len(x) / SR + GAP_LINE
    lead = gap(0.25)
    vo_all = polish(np.concatenate([lead] + vo))
    for i in lines: i["start"] += 0.25; i["end"] += 0.25
    sf.write(HERE / "vo.wav", vo_all, SR, subtype="PCM_24")
    sf.write(HERE / "vo_raw.wav", np.concatenate([lead] + vo_raw), SR, subtype="PCM_24")
    (HERE / "lines.json").write_text(json.dumps(lines, indent=1))
    pub = HERE.parent / "public" / "vo.wav"
    sf.write(pub, vo_all, SR, subtype="PCM_16")
    print("vo:", round(len(vo_all) / SR, 2), "s; isolated:", bool(use_iso and KEY), "; lines:", [(l["n"], l["start"], l["voice"]) for l in lines])
