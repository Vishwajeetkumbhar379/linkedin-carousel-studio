"""Lighten skin in a stylised avatar without touching hair, clothes or background.

    python scripts/skin_tone.py in.png out.png [--lift 0.16] [--desat 0.8]

Skin pixels are picked by colour (warm hue, mid saturation, mid value), feathered, and then lifted in
value and slightly desaturated toward the reference photo's tone. Boots sit in the same colour range, so the
lower part of the canvas (below --floor, fraction of height) is excluded.
"""
from __future__ import annotations

import sys

import numpy as np
from PIL import Image, ImageFilter


def lighten(src: str, dst: str, lift: float = 0.16, desat: float = 0.8, floor: float = 0.86) -> None:
    im = Image.open(src).convert("RGB")
    hsv = np.asarray(im.convert("HSV")).astype(float) / 255.0
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    m = ((h > 6) & (h < 34) & (s > 0.32) & (s < 0.9) & (v > 0.22) & (v < 0.92)).astype(np.float32)
    H = m.shape[0]
    m[int(H * floor):, :] = 0
    mask = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(2.5))
    k = np.asarray(mask).astype(float) / 255.0
    v2 = np.clip(v + lift * (1 - v) * 1.6 * k + lift * 0.35 * v * k, 0, 1)
    s2 = s * (1 - (1 - desat) * k)
    h2 = (hsv[..., 0] * 360 + 2.5 * k) / 360  # a touch less orange, a touch more rose-beige
    out = np.stack([h2, s2, v2], -1)
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "HSV").convert("RGB").save(dst)


if __name__ == "__main__":
    a = sys.argv[1:]
    lift = float(a[a.index("--lift") + 1]) if "--lift" in a else 0.16
    desat = float(a[a.index("--desat") + 1]) if "--desat" in a else 0.8
    lighten(a[0], a[1], lift, desat)
