"""Turn Vish's mascot pack (brand/avatar/pack) into the locked 2D style with FLUX.1 Kontext (free Hugging Face Space).

    python scripts/char2d.py [pack-relative pngs ...]    -> brand/avatar/pack2d/<same path>.png (light background)

Same prompt and seed for every pose, so the set stays consistent. The output stays out of git (his likeness, generated).
"""
import os
import shutil
import sys
from pathlib import Path

from gradio_client import Client, handle_file
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PACK, OUT = ROOT / "brand/avatar/pack", ROOT / "brand/avatar/pack2d"
PROMPT = ("Redraw this exact man as a clean flat 2D vector illustration for an animated explainer video: bold simple shapes, "
          "soft cel shading, clean outlines, warm palette. Keep his face, pose, expression, long wavy brown hair, round tortoiseshell "
          "glasses, moustache and goatee, hoop earrings, necklace, ivory blazer, burgundy shirt and the rest of his outfit exactly the same. "
          "Plain light background.")


def run(rel: str, client: Client) -> Path:
    src, dst = PACK / rel, OUT / rel
    if dst.exists():
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (243, 238, 229, 255))
    bg.alpha_composite(im)
    tmp = dst.with_suffix(".in.png")
    bg.convert("RGB").save(tmp)
    r = client.predict(input_image=handle_file(str(tmp)), prompt=PROMPT, seed=7, randomize_seed=False, guidance_scale=2.5, steps=28,
                       api_name="/infer")
    out = r[0] if isinstance(r, (list, tuple)) else r
    Image.open(out if isinstance(out, str) else out["path"]).save(dst)
    tmp.unlink()
    return dst


if __name__ == "__main__":
    c = Client("black-forest-labs/FLUX.1-Kontext-Dev", token=os.environ.get("HF_TOKEN"))
    rels = sys.argv[1:] or [str(p.relative_to(PACK)) for p in sorted(PACK.glob("0[1-4]_*/*.png"))]
    for r in rels:
        try:
            print("->", run(r, c), flush=True)
        except Exception as e:  # free GPU quota runs out: the rest runs next time
            print("stopped at", r, str(e)[:160])
            break
