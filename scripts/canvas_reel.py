"""Canvas reel: a voiceover + a beat list -> a 9:16 reel on one paper canvas with a moving camera (templates/video/canvas).
    python scripts/canvas_reel.py <project dir> <key>
Needs <key>.mp3, <key>_words.json (whisper word times), scripts.json (the script, emotion tags allowed) and beats.json[key]:
{"hook": "html", "hookEnd": "phrase", "els": [{"type": card|counter|bar|list|chip|stamp|quote|tags, "at": "phrase", ...}]}.
Every "at", "out", "fill", "reveal" and row "at" is a phrase from the script ("word#2" = second time it is said), resolved to
the moment it is spoken, so a new voiceover re-times the whole reel. Captions use the script's own words. SFX follow the cards.
"""
import difflib, json, re, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SFX = ROOT / "video-projects/sfx-library"
FPS = 30
norm = lambda w: re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'"))


def align(script, words):
    toks = re.sub(r"\[[^\]]*\]", " ", script).split()
    a = [norm(t) for t in toks]; b = [norm(w["w"]) for w in words]
    T = [None] * len(toks)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            for k in range(i2 - i1): T[i1 + k] = (words[j1 + k]["s"], words[j1 + k]["e"])
        elif op == "replace":
            s0, s1 = words[j1]["s"], words[j2 - 1]["e"]; n = i2 - i1
            for k in range(n): T[i1 + k] = (s0 + (s1 - s0) * k / n, s0 + (s1 - s0) * (k + 1) / n)
    for i in range(len(T)):  # words whisper missed: borrow the neighbours' time
        if T[i] is None:
            prev = next((T[j][1] for j in range(i - 1, -1, -1) if T[j]), 0.0)
            T[i] = (prev, prev + 0.15)
    return [{"w": t, "s": round(s, 3), "e": round(e, 3)} for t, (s, e) in zip(toks, T)]


def main(proj: Path, key: str):
    script = json.loads((proj / "scripts.json").read_text())[key]
    beat = json.loads((proj / "beats.json").read_text())[key]
    W = align(script, json.loads((proj / f"{key}_words.json").read_text()))
    N = [norm(w["w"]) for w in W]

    def at(ph):
        if isinstance(ph, (int, float)): return ph
        ph, n = (ph.split("#") + ["1"])[:2]
        q = [norm(x) for x in ph.split()]; hits = [i for i in range(len(N)) if N[i:i + len(q)] == q]
        if len(hits) < int(n): sys.exit(f"{key}: phrase not in script: {ph!r}")
        return W[hits[int(n) - 1]]["s"]

    for e in beat["els"]:
        for f in ("at", "out", "fill", "reveal"):
            if f in e: e[f] = at(e[f])
        for r in e.get("rows", []): r["at"] = at(r["at"])
    end = W[-1]["e"] + 1.0
    chunks, cur = [], []
    for i, w in enumerate(W):
        cur.append(w)
        if re.search(r"[.,?!:]$", w["w"]) or len(cur) == 3 or i == len(W) - 1:
            chunks.append({"s": cur[0]["s"], "e": cur[-1]["e"] + 0.2, "t": " ".join(x["w"] for x in cur).rstrip(".,:")}); cur = []
    for c, d in zip(chunks, chunks[1:]): c["e"] = min(c["e"], d["s"])
    data = {"chunks": chunks, "hook": beat["hook"], "hookEnd": at(beat["hookEnd"]), "end": end, "els": beat["els"]}
    work = proj / "work"; work.mkdir(exist_ok=True)
    page = (ROOT / "templates/video/canvas/canvas.html").read_text().replace("__FONTS__", (ROOT / "templates/fonts-extra").as_uri()).replace("__DATA__", json.dumps(data))
    (work / f"{key}.html").write_text(page)
    pic = work / f"{key}_pic.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(pic)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto((work / f"{key}.html").as_uri()); pg.wait_for_timeout(500)
        for f in range(int(end * FPS)):
            pg.evaluate(f"seek({f / FPS})"); enc.stdin.write(pg.screenshot(type="jpeg", quality=93))
        b.close()
    enc.stdin.close(); enc.wait()
    # sound: one effect per card, quiet under the voice
    S = {"stamp": ("stamp", .8), "chip": ("pop", .5), "tags": ("pop", .45), "counter": ("tick", .4), "quote": ("hit_soft", .8)}
    cues = [(S.get(e["type"], ("whoosh_soft", .4)), e["at"]) for e in beat["els"]]
    cues += [(("whoosh", .5), e["reveal"]) for e in beat["els"] if "reveal" in e]
    ins = ["-i", str(proj / f"{key}.mp3")] + sum([["-i", str(SFX / f"{c[0]}.mp3")] for c, _ in cues], [])
    fl = [f"[{i + 2}:a]adelay={int(t * 1000)}|{int(t * 1000)},volume={c[1] * 0.3:.3f}[s{i}]" for i, (c, t) in enumerate(cues)]
    # music ships inside the file (Vish, 28 Oct), ducked under the voice so every word stays on top
    from carousel_reel import compose
    mi = len(cues) + 2
    ins += ["-i", str(compose(f"cv-{proj.name}-{key}", end + 1, beat.get("mood", "warm modern lo-fi, soft plucks, light drums, hopeful")))]
    fl += ["[1:a]asplit=2[v][vk]", f"[{mi}:a]volume=0.22,afade=t=out:st={max(0, end - 1.2):.2f}:d=1.2[mu]",
           "[mu][vk]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350:makeup=1[md]"]
    mix = "[v]" + "".join(f"[s{i}]" for i in range(len(cues))) + f"[md]amix=inputs={len(cues) + 2}:normalize=0,loudnorm=I=-14:TP=-1.5[a]"
    out = proj / f"{proj.name}-{key}-9x16.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pic), *ins, "-filter_complex", ";".join(fl + [mix]), "-map", "0:v", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-t", f"{end:.2f}", "-movflags", "+faststart", str(out)], check=True)
    print("->", out, f"{end:.1f}s")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), sys.argv[2])
