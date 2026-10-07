"""Lock every video to the voice Vish picked (video #25, 'ai-creators-cheap-trust-isnt').

    /home/user/venvs/chatterbox/bin/python scripts/voice_clone.py out/<post>/lines.json

lines.json: {"lines": ["...", "..."], "pause": 0.45, "pause_after": {"0": 0.7}}
Each line is generated 3 times with Chatterbox (MIT, zero-shot clone from brand/voice-ref/vish-voice-25-full.wav),
plus a voice-converted copy of each take; the take whose speaker embedding is closest to video #25 wins.
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
from chatterbox.vc import ChatterboxVC  # noqa: E402
from huggingface_hub import hf_hub_download  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "brand" / "voice-ref" / "vish-voice-25-full.wav"
REF25 = ROOT / "out" / "batch-01" / "ai-creators-cheap-trust-isnt" / "voice.wav"
SEEDS, EX, CFG = (11, 23, 37), 0.5, 0.5


def main(spec: Path) -> None:
    cfg = json.loads(spec.read_text())
    lines, pause, after = cfg["lines"], cfg.get("pause", 0.45), {int(k): v for k, v in cfg.get("pause_after", {}).items()}
    tts, vc = ChatterboxTTS.from_pretrained(device="cpu"), ChatterboxVC.from_pretrained(device="cpu")
    ve = VoiceEncoder()
    ve.load_state_dict(torch.load(hf_hub_download("ResembleAI/chatterbox", "ve.pt"), map_location="cpu"))
    ve.eval()
    emb = lambda w: ve.embeds_from_wavs([w], sample_rate=16000, as_spk=True)  # noqa: E731
    ref = emb(librosa.load(str(REF25), sr=16000, duration=16.2)[0])
    sim = lambda w: float(np.dot(ref, e := emb(w)) / np.linalg.norm(ref) / np.linalg.norm(e))  # noqa: E731
    sr, out, meta, t = tts.sr, [], [], 0.0
    tmp = spec.parent / ".takes"
    tmp.mkdir(exist_ok=True)
    for i, line in enumerate(lines):
        best = None
        for s in SEEDS:
            torch.manual_seed(s)
            w = tts.generate(line, audio_prompt_path=str(REF), exaggeration=EX, cfg_weight=CFG)
            p = tmp / f"l{i}_s{s}.wav"
            ta.save(str(p), w, sr)
            v = vc.generate(str(p), target_voice_path=str(REF))
            for kind, wav in (("tts", w), ("vc", v)):
                w16 = librosa.resample(wav.squeeze(0).numpy(), orig_sr=sr, target_sr=16000)
                sc = sim(w16)
                if not best or sc > best[0]:
                    best = (sc, wav, f"seed {s} {kind}")
        wav = best[1].squeeze(0).numpy()
        idx = np.nonzero(np.abs(wav) > 0.01)[0]  # trim leading/trailing silence
        wav = wav[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)] if len(idx) else wav
        meta.append({"text": line, "start": round(t, 3), "end": round(t + len(wav) / sr, 3), "similarity": round(best[0], 3), "take": best[2]})
        gap = after.get(i, pause)
        out += [wav, np.zeros(int(sr * gap), dtype=wav.dtype)]
        t += len(wav) / sr + gap
        print(f"line {i + 1}/{len(lines)}: similarity {best[0]:.3f} ({best[2]})", flush=True)
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
