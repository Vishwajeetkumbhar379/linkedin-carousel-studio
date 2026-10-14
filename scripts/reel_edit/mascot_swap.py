"""Mascot version: swap Vish for his 3D mascot in the cut A-roll, keeping every gesture and lip movement.

    python scripts/reel_edit/mascot_swap.py video-projects/<slug> [--ref=brand/avatar/vish-3d-full.png] [--res=Medium Res] [--chunk=10]

Uses Wan2.2-Animate "Pose Retarget" (whole 3D mascot body, its own style; "Character Swap" only repaints the face realistically) (Apache-2.0) on the free Hugging Face Space alexnasa/Wan2.2-Animate-ZEROGPU.
Needs HF_TOKEN (a read token) in the environment: ZeroGPU only runs for signed-in users.
Free account: the Space asks for an xlarge GPU (double time), so only Low Res 2 s chunks pass the per-call cap, 2 a day; chunks already done are kept, so rerun daily
until every chunk exists. PRO ($9/month): 40 minutes a day, the whole video in one run.
Writes work-mascot/chunks/*.mp4, then work-mascot/aroll.mp4 (voice re-attached) when all chunks are in.
Then: prep.py <proj> --work=work-mascot --src=work-mascot/aroll.mp4, render.py <proj> --work=work-mascot.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

SPACE = "https://alexnasa-wan2-2-animate-zerogpu.hf.space"
GPU_S = {"Low Res": 0.5, "Medium Res": 1.0}  # app.py: seconds of GPU = table(duration) * factor


def hdr() -> dict:
    t = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    return {"Authorization": f"Bearer {t}"} if t else {}


def upload(p: Path) -> str:
    r = requests.post(f"{SPACE}/gradio_api/upload", files={"files": open(p, "rb")}, headers=hdr(), timeout=300)
    r.raise_for_status()
    return r.json()[0]


def fd(path: str) -> dict:
    return {"path": path, "meta": {"_type": "gradio.FileData"}}


def swap(video: str, ref: str, secs: int, res: str, mode: str = "Character Swap") -> str:
    cfg = requests.get(f"{SPACE}/config", headers=hdr(), timeout=60).json()
    fn = next(d.get("id", i) for i, d in enumerate(cfg["dependencies"]) if d.get("api_name") == "animate_scene")
    sh = f"vish{int(time.time())}"
    body = {"data": [fd(video), secs, fd(ref), mode, res, None], "fn_index": fn, "session_hash": sh, "event_data": None, "trigger_id": None}
    requests.post(f"{SPACE}/gradio_api/queue/join", json=body, headers=hdr(), timeout=60).raise_for_status()
    with requests.get(f"{SPACE}/gradio_api/queue/data", params={"session_hash": sh}, headers=hdr(), stream=True, timeout=1800) as r:
        for line in r.iter_lines():
            if not line.startswith(b"data:"):
                continue
            m = json.loads(line[5:])
            if m.get("msg") == "process_completed":
                if not m.get("success"):
                    raise RuntimeError(m.get("title") or m.get("output", {}).get("error") or "space error")
                out = m["output"]["data"][0]
                return (out.get("video") or out)["url"] if isinstance(out, dict) else out
    raise RuntimeError("stream ended without a result")


def main(proj: Path, ref: Path, res: str, chunk: int, limit: int = 99, mode: str = "Pose Retarget") -> None:
    w = proj / "work"
    mw = proj / "work-mascot"
    cd = mw / f"chunks-{mode.split()[0].lower()}-{chunk}s-{res.split()[0].lower()}"
    cd.mkdir(parents=True, exist_ok=True)
    dur = json.loads((w / "prep.json").read_text())["duration"]
    n = int(-(-dur // chunk))
    ref_path = upload(ref)
    new = 0
    for k in range(n):
        dst = cd / f"c{k:02d}.mp4"
        if dst.exists():
            continue
        if new >= limit:
            print(f"limit reached: {k} of {n} chunks done")
            return
        new += 1
        t0, t1 = k * chunk, min(dur, (k + 1) * chunk)
        src = cd / f"in{k:02d}.mp4"
        subprocess.run([sys.executable, str(Path(__file__).parent / "aroll.py"), str(proj), f"--from={t0}", f"--to={t1}",
                        f"--out={src.relative_to(proj)}"], check=True, capture_output=True)
        secs = int(-(-(t1 - t0) // 1))
        print(f"chunk {k + 1}/{n}: {t0:.1f}-{t1:.1f} s, {res}", flush=True)
        try:
            url = swap(upload(src), ref_path, secs, res, mode)
        except RuntimeError as e:
            print(f"stopped at chunk {k + 1}: {e}. Chunks done so far are kept; run again after the quota resets.")
            return
        with requests.get(url, headers=hdr(), timeout=600) as r:
            r.raise_for_status()
            dst.write_bytes(r.content)
    lst = cd / "list.txt"
    lst.write_text("".join(f"file 'c{k:02d}.mp4'\n" for k in range(n)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(w / "voice.wav"),
                    "-map", "0:v", "-map", "1:a", "-vf", "fps=30,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6", "-c:v", "libx264",
                    "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(mw / "aroll.mp4")], check=True)
    print("mascot A-roll:", mw / "aroll.mp4")


if __name__ == "__main__":
    a = dict(x[2:].split("=", 1) for x in sys.argv[2:] if x.startswith("--"))
    main(Path(sys.argv[1]), Path(a.get("ref", "brand/avatar/vish-3d-full.png")), a.get("res", "Medium Res"), int(a.get("chunk", 10)), int(a.get("limit", 99)), a.get("mode", "Pose Retarget"))
