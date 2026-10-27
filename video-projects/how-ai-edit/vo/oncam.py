"""The on-camera moments, cut from the same takes as the voiceover so the picture stays lip-synced.

    python3 video-projects/how-ai-edit/vo/oncam.py

His takes are landscape 1920x1080 with him centred, so each is cropped to a 9:16 strip, upscaled to
1080x1920 (lanczos), lightly denoised and sharpened, and graded with the film's "soft" look (natural skin,
no extra saturation). Video only: the sound comes from vo.wav.
- public/oncam/l01.mp4: line 1 up to the freeze, the 0.3 s gap held on the last frame of "Hold on."
- public/oncam/l10.mp4: "Hi, I'm Vish." (line 10's second part)
- public/freeze.jpg: the frame he freezes on (the word "39"); the shards are cut from it.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "reel_edit"))
from film import write_lut  # noqa: E402

RAW = HERE.parents[1] / "week-02-talks" / "raw"
OUT = HERE.parent / "public" / "oncam"
OUT.mkdir(parents=True, exist_ok=True)
LUT = write_lut("soft", HERE / "film-soft.cube")
VF = f"crop=608:1080:656:0,scale=1080:1920:flags=lanczos,hqdn3d=1.5:1.5:4:4,unsharp=5:5:0.45:5:5:0,lut3d=file='{LUT}':interp=tetrahedral,format=yuv420p"


def seg(clip: str, a: float, b: float, out: Path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(RAW / f"{clip}.MOV"), "-an",
                    "-vf", VF, "-r", "30", "-c:v", "libx264", "-crf", "14", "-preset", "medium", str(out)], check=True)


if __name__ == "__main__":
    lines = {l["n"]: l for l in json.loads((HERE / "lines.json").read_text())}
    words = json.loads((HERE.parent / "src" / "words.json").read_text())
    tmp = OUT / "_tmp"; tmp.mkdir(exist_ok=True)
    # line 1: part A, hold its last frame through the gap, then part B
    a, b = lines[1]["parts"]
    seg(a["clip"], *a["src"], tmp / "a.mp4")
    seg(b["clip"], *b["src"], tmp / "b.mp4")
    gap = b["at"] - (a["at"] + a["src"][1] - a["src"][0])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "a.mp4"), "-vf", f"tpad=stop_mode=clone:stop_duration={gap:.3f}", "-c:v", "libx264", "-crf", "14", str(tmp / "a2.mp4")], check=True)
    (tmp / "list.txt").write_text(f"file '{tmp / 'a2.mp4'}'\nfile '{tmp / 'b.mp4'}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-c", "copy", str(OUT / "l01.mp4")], check=True)
    # the freeze frame: the word "39" in the voiceover, mapped back into the take
    t39 = next(w["s"] for w in words if w["w"].strip(",.") == "39")
    src_t = b["src"][0] + (t39 - b["at"]) + 0.06
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{src_t:.3f}", "-i", str(RAW / f"{b['clip']}.MOV"), "-frames:v", "1", "-vf", VF.replace(",format=yuv420p", ""), "-q:v", "2", str(HERE.parent / "public" / "freeze.jpg")], check=True)
    # line 10: "Hi, I'm Vish."
    hi = lines[10]["parts"][1]
    seg(hi["clip"], *hi["src"], OUT / "l10.mp4")
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    print("l01 starts", a["at"], "freeze at", round(t39, 3), "(take", round(src_t, 3), "s); l10 starts", hi["at"])
