"""Lock every video to the voice Vish picked (video #25, 'ai-creators-cheap-trust-isnt').

    /home/user/venvs/chatterbox/bin/python scripts/voice_clone.py out/<post>/lines.json

lines.json: {"lines": ["...", "..."], "pause": 0.45, "pause_after": {"0": 0.7}}
Each line is generated up to 4 times with Chatterbox (MIT, zero-shot clone from brand/voice-ref/vish-voice-25-full.wav).
A take wins on speaker similarity to video #25, penalised for stalls (long silences) and odd pace; it stops early when a
take is already natural. Silences inside a line are then capped at 0.24 s, so there are no mid-sentence stops.
Writes voice.wav (loudness -16 LUFS) and voice.json (per-line start/end and similarity) next to lines.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
os.environ.setdefault("TQDM_DISABLE", "1")
import librosa  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
import torchaudio as ta  # noqa: E402
from chatterbox.models.voice_encoder import VoiceEncoder  # noqa: E402
from chatterbox.tts import ChatterboxTTS  # noqa: E402
from huggingface_hub import hf_hub_download  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "brand" / "voice-ref" / "vish-voice-25-full.wav"
REF25 = ROOT / "out" / "batch-01" / "ai-creators-cheap-trust-isnt" / "voice.wav"
SEEDS, EX, CFG = (11, 23, 37, 53), 0.45, 0.5


MAX_PAUSE = 0.24  # longest silence allowed inside a line (commas, full stops); between lines the gap is set explicitly


def _frames_db(w: np.ndarray, sr: int, hop_s: float = 0.01) -> np.ndarray:
    hop = int(sr * hop_s)
    n = max(1, len(w) // hop)
    rms = np.sqrt(np.mean(w[: n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9
    return 20 * np.log10(rms / rms.max())


def trim(w: np.ndarray, sr: int) -> np.ndarray:
    """Cut leading and trailing silence, keep 40 ms / 90 ms of air."""
    db = _frames_db(w, sr)
    voiced = np.nonzero(db > -40)[0]
    if not len(voiced):
        return w
    a, b = voiced[0] * int(sr * 0.01), (voiced[-1] + 1) * int(sr * 0.01)
    return w[max(0, a - int(0.04 * sr)): min(len(w), b + int(0.09 * sr))]


def pauses(w: np.ndarray, sr: int, min_s: float = 0.12) -> list[tuple[int, float]]:
    """Internal silences (frame index, seconds) longer than min_s."""
    db = _frames_db(w, sr)
    sil, out, i = db < -38, [], 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]:
                j += 1
            if 0 < i and j < len(sil) and (j - i) * 0.01 >= min_s:
                out.append((i, (j - i) * 0.01))
            i = j
        else:
            i += 1
    return out


def cap_pauses(w: np.ndarray, sr: int, cap: float) -> np.ndarray:
    """Shorten any silence inside the line to `cap` seconds, with 10 ms crossfades so nothing clicks."""
    hop = int(sr * 0.01)
    keep, last = [], 0
    for i, g in pauses(w, sr):
        if g <= cap:
            continue
        a = i * hop + int(cap / 2 * sr)
        b = (i + int(round(g / 0.01))) * hop - int(cap / 2 * sr)
        keep.append(w[last:a])
        last = b
    keep.append(w[last:])
    if len(keep) == 1:
        return w
    x, f = keep[0], int(0.01 * sr)
    for seg in keep[1:]:
        if len(x) > f and len(seg) > f:
            ramp = np.linspace(0, 1, f, dtype=w.dtype)
            x = np.concatenate([x[:-f], x[-f:] * (1 - ramp) + seg[:f] * ramp, seg[f:]])
        else:
            x = np.concatenate([x, seg])
    return x


def main(spec: Path) -> None:
    cfg = json.loads(spec.read_text())
    lines, pause, after = cfg["lines"], cfg.get("pause", 0.45), {int(k): v for k, v in cfg.get("pause_after", {}).items()}
    tts = ChatterboxTTS.from_pretrained(device="cpu")
    ve = VoiceEncoder()
    ve.load_state_dict(torch.load(hf_hub_download("ResembleAI/chatterbox", "ve.pt"), map_location="cpu"))
    ve.eval()
    emb = lambda w: ve.embeds_from_wavs([w], sample_rate=16000, as_spk=True)  # noqa: E731
    ref = emb(librosa.load(str(REF25), sr=16000, duration=16.2)[0])
    sim = lambda w: float(np.dot(ref, e := emb(w)) / np.linalg.norm(ref) / np.linalg.norm(e))  # noqa: E731
    sr, out, meta, t = tts.sr, [], [], 0.0
    for i, line in enumerate(lines):
        cands = []
        for s in SEEDS:
            torch.manual_seed(s)
            w = tts.generate(line, audio_prompt_path=str(REF), exaggeration=EX, cfg_weight=CFG).squeeze(0).numpy()
            w = trim(w, sr)
            longest = max([g for _, g in pauses(w, sr)] or [0.0])
            words = len(line.split())
            wps = words / max(0.5, len(w) / sr - sum(g for _, g in pauses(w, sr)))
            sc = sim(librosa.resample(w, orig_sr=sr, target_sr=16000))
            score = sc - 0.06 * max(0.0, longest - 0.35) - 0.02 * max(0.0, abs(wps - 2.8) - 0.5)
            cands.append((score, sc, w, f"seed {s}", longest, wps))
            if sc >= 0.90 and longest <= 0.6 and 2.2 <= wps <= 3.5:
                break  # good enough: natural pauses, normal pace, right voice
        score, sc, wav, take, longest, wps = max(cands, key=lambda c: c[0])
        wav = cap_pauses(wav, sr, MAX_PAUSE)
        meta.append({"text": line, "start": round(t, 3), "end": round(t + len(wav) / sr, 3), "similarity": round(sc, 3), "take": take,
                     "raw_longest_pause": round(longest, 2), "wps": round(wps, 2)})
        gap = after.get(i, pause)
        out += [wav, np.zeros(int(sr * gap), dtype=wav.dtype)]
        t += len(wav) / sr + gap
        print(f"line {i + 1}/{len(lines)}: similarity {sc:.3f}, longest pause {longest:.2f}s -> capped, {wps:.1f} w/s ({take}, {len(cands)} takes)", flush=True)
    raw = spec.parent / "voice-raw.wav"
    ta.save(str(raw), torch.from_numpy(np.concatenate(out)).unsqueeze(0), sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000",
                    str(spec.parent / "voice.wav")], check=True)
    avg = sum(m["similarity"] for m in meta) / len(meta)
    (spec.parent / "voice.json").write_text(json.dumps({"reference": "video #25 ai-creators-cheap-trust-isnt", "engine": "chatterbox clone",
                                                         "avg_similarity": round(avg, 3), "duration": round(t, 3), "lines": meta}, indent=1))
    print(f"voice.wav {t:.1f}s, average similarity to #25: {avg:.3f}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
