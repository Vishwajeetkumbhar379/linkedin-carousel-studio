"""Disney-style avatar of Vish from his best selfie (free FLUX Kontext Space). Nose rule in the prompt (CONTENT-OS).

    python scripts/avatar_try.py <face.jpg> <out_dir> [seeds...]   -> <out_dir>/d<seed>.jpg + cmp.jpg (selfie + results)
"""
import os
import sys
from pathlib import Path

from gradio_client import Client, handle_file
from PIL import Image

P = ("Redraw this man as the handsome hero of a modern 2D Disney animated film, the most flattering version of him. "
     "Small, slim, refined nose. Big bright expressive eyes with lively highlights and a warm confident look, never sleepy. "
     "Light warm skin tone as in the photo, smooth and clear with no wrinkles. Keep his long dark hair swept back from the forehead, "
     "his thin moustache, neat goatee and light stubble on the cheeks, and the small hoop earrings, so he is clearly the same person. "
     "Friendly confident smile, grey hoodie. Clean outlines, soft cel shading, plain light background.")

face, out = Path(sys.argv[1]), Path(sys.argv[2])
seeds = [int(s) for s in sys.argv[3:]] or [3, 19, 51]
out.mkdir(parents=True, exist_ok=True)
c = Client("black-forest-labs/FLUX.1-Kontext-Dev", token=os.environ.get("HF_TOKEN"))
done = []
for s in seeds:
    try:
        r = c.predict(input_image=handle_file(str(face)), prompt=P, seed=s, randomize_seed=False, guidance_scale=2.8, steps=30, api_name="/infer")
        o = r[0] if isinstance(r, (list, tuple)) else r
        Image.open(o if isinstance(o, str) else o["path"]).convert("RGB").save(out / f"d{s}.jpg", quality=92)
        done.append(s)
        print("ok", s, flush=True)
    except Exception as e:
        print("stop", str(e)[:140])
        break
if done:
    ims = [Image.open(face)] + [Image.open(out / f"d{s}.jpg") for s in done]
    for i in ims:
        i.thumbnail((360, 360))
    b = Image.new("RGB", (sum(i.width for i in ims) + 10 * len(ims), 360), "white")
    x = 0
    for i in ims:
        b.paste(i, (x, 0))
        x += i.width + 10
    b.save(out / "cmp.jpg", quality=82)
