"""Quick colour looks for Vish's iPhone footage (free, ffmpeg only).

For finished edits use film.py instead (film-print LUT, protected skin, one-lamp light falloff, lens defocus,
halation, diffusion): these quick looks lean on saturation and warmth and read as phone footage (Vish, 22 Oct).

    python scripts/reel_edit/grade.py <in.mov> <out.mp4> [--look=night|day|soft] [--preview=out.jpg --at=10,40,70]

- iPhone HDR clips (HLG or PQ, the default Camera app setting) are tone-mapped to Rec.709 SDR first, so they don't
  look washed out or neon on Instagram. SDR clips (Blackmagic Camera app, Rec.709) go straight to the look.
- Looks, measured against the reference reel @likfoon (22 Oct 2026: 78 % of pixels in shadow, near-black floor, warm
  mids, neutral highlights):
  night  talking head in the room: exposure down, true blacks, warm skin, the orange cast taken out of the
         walls and lamp, a hint of teal in the shadows, vignette, fine grain.
  day    travel and outdoor clips: richer colour, softer contrast, warm but not orange.
  soft   the paper-world middle section: lower contrast, lifted blacks, muted colour.
- --preview writes a before/after strip of a few frames instead of (or as well as) the video.
Most of the look still comes from the light: ceiling light off, one lamp beside you, a darker background.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

LOOKS = {
    "night": ("eq=brightness=-0.02:contrast=1.14:saturation=1.04:gamma=0.96,"
              "colorbalance=rs=-0.03:bs=0.04:rm=-0.01:bm=0.01:rh=-0.09:gh=-0.02:bh=0.06,"
              "curves=master='0/0 0.08/0.03 0.45/0.44 0.80/0.82 1/0.96',"
              "vibrance=intensity=0.08,vignette=angle=PI/3.6,noise=alls=5:allf=t"),
    "day": ("eq=contrast=1.06:saturation=1.10:gamma=0.97,"
            "colorbalance=rs=-0.02:bs=0.03:rh=0.02:bh=-0.02,"
            "curves=master='0/0.01 0.25/0.22 0.75/0.77 1/0.98',vibrance=intensity=0.15,noise=alls=4:allf=t"),
    "soft": ("eq=contrast=0.92:saturation=0.85:gamma=1.02,"
             "curves=master='0/0.05 0.5/0.5 1/0.94',colorbalance=rh=0.02:bh=-0.01,noise=alls=6:allf=t"),
}
HDR_TO_SDR = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
              "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def probe(src: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=color_transfer,color_primaries,width,height", "-of", "json", str(src)],
                       capture_output=True, text=True)
    return (json.loads(r.stdout or "{}").get("streams") or [{}])[0]


def chain(src: Path, look: str) -> str:
    tr = probe(src).get("color_transfer", "")
    pre = HDR_TO_SDR + "," if tr in ("arib-std-b67", "smpte2084") else ""
    return pre + LOOKS[look] + ",format=yuv420p"


def grade(src: Path, out: Path, look: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", chain(src, look),
                    "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-colorspace", "bt709",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "copy", str(out)], check=True)


def preview(src: Path, out: Path, look: str, at: list[float]) -> None:
    from PIL import Image
    tmp = out.parent / f".{out.stem}_tmp"
    tmp.mkdir(exist_ok=True)
    tiles = []
    for i, t in enumerate(at):
        for kind, vf in (("a", "format=yuv420p"), ("b", chain(src, look))):
            f = tmp / f"{i}{kind}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1",
                            "-vf", vf + ",scale=360:-2", str(f)], check=True)
            tiles.append(Image.open(f).convert("RGB"))
    w, h = tiles[0].size
    sheet = Image.new("RGB", (len(at) * (2 * w + 24), h), "white")
    for i in range(len(at)):
        sheet.paste(tiles[2 * i], (i * (2 * w + 24), 0))
        sheet.paste(tiles[2 * i + 1], (i * (2 * w + 24) + w + 4, 0))
    sheet.save(out, quality=88)
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    look = opts.get("look", "night")
    src = Path(args[0])
    if "preview" in opts:
        preview(src, Path(opts["preview"]), look, [float(x) for x in opts.get("at", "10,40,70").split(",")])
    if len(args) > 1:
        grade(src, Path(args[1]), look)
