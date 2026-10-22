"""Film grade for Vish's phone footage: make it read like a cinema camera with a colourist, not a filter.

    python scripts/reel_edit/film.py <clip> --look=night|day|soft --at=2,6 --preview=out.jpg [--matte]

What it does, and why (phone footage gives itself away through each of these):
- Tone: a film-print curve. Dense but not crushed blacks, mids left alone, a long shoulder so lamps, windows and
  skies roll off instead of clipping to flat white (phones clip hard and tone-map everything to the same brightness).
- Colour: overall saturation down (phones push it), skin protected and kept natural, greens toward olive, blues
  toward teal, highlights desaturated like film, a little subtractive density so strong colours get richer, not neon.
  Split-tone is a whisper: cool shadows, warm highlights.
- Light: the room behind the speaker falls off darker, slightly cooler and less saturated, so he is the lit subject
  (one-lamp look), with a gentle lens defocus on the background (large-sensor depth instead of phone everything-sharp).
- Optics: red-biased halation around bright sources, a 1/8-strength diffusion (Pro-Mist style) glow, and the phone's
  edge sharpening softened. Grain is added in the compositor (mid-tone weighted overlay).
The global part is baked into a 3D LUT (applied by ffmpeg's lut3d), the spatial part runs per frame in finish().
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

HDR_TO_SDR = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
              "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")

LOOKS = {
    # talking head in the room at night: the lamp is the key light, the room falls away
    "night": dict(exposure=-0.12, wb=(1.0, 1.0, 1.02), sat=0.88, skin_sat=1.0, hi_desat=0.55,
                  curve=[(0, .012), (.05, .030), (.15, .108), (.30, .252), (.50, .478), (.70, .700), (.86, .848), (1, .940)],
                  shadow_tint=(-.010, .002, .014), hi_tint=(.014, .005, -.010), density=.10, green=-10, blue=-8,
                  bg=dict(gain=.50, sat=.90, cool=(.96, 1.0, 1.04), defocus=10), halation=.10, mist=.05),
    # travel and outdoor: natural, rich, skies kept
    "day": dict(exposure=-0.08, wb=(1.0, 1.0, 1.0), sat=0.88, skin_sat=1.0, hi_desat=0.55,
                curve=[(0, .018), (.06, .045), (.20, .175), (.50, .488), (.75, .745), (.90, .872), (1, .945)],
                shadow_tint=(-.010, .004, .012), hi_tint=(.012, .006, -.008), density=.12, green=-12, blue=-10,
                bg=None, halation=.09, mist=.05),
    # the paper-world middle: memory, softer and cooler
    "soft": dict(exposure=-0.05, wb=(.99, 1.0, 1.02), sat=0.76, skin_sat=0.92, hi_desat=0.6,
                 curve=[(0, .040), (.15, .150), (.50, .490), (.80, .780), (1, .925)],
                 shadow_tint=(-.006, .004, .012), hi_tint=(.010, .004, -.004), density=.06, green=-10, blue=-6,
                 bg=dict(gain=.80, sat=.85, cool=(.98, 1.0, 1.02), defocus=8), halation=.07, mist=.08),
}


def _to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def _to_disp(x):
    x = np.maximum(x, 0)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def _smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _luma(x):
    return x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722


def transform(rgb: np.ndarray, look: str) -> np.ndarray:
    """The global film transform on display-referred RGB in [0, 1] (shape (..., 3))."""
    from scipy.interpolate import PchipInterpolator
    p = LOOKS[look]
    x = _to_disp(np.minimum(_to_lin(rgb) * 2 ** p["exposure"] * np.array(p["wb"]), 1.0))
    # hue moves in HSV (greens to olive, blues to teal), measured on the source colour
    hsv = cv2.cvtColor(x.reshape(-1, 1, 3).astype(np.float32), cv2.COLOR_RGB2HSV).reshape(x.shape)
    h, s = hsv[..., 0], hsv[..., 1]
    dh = p["green"] * np.exp(-((h - 115) / 40) ** 2) + p["blue"] * np.exp(-((h - 215) / 30) ** 2)
    hsv[..., 0] = np.mod(h + dh * _smooth(.05, .25, s), 360)
    x = cv2.cvtColor(hsv.reshape(-1, 1, 3), cv2.COLOR_HSV2RGB).reshape(x.shape)
    # saturation around luma: calmer overall, skin protected, film-like loss in highlights and deep shadows
    Y = _luma(x)[..., None]
    skin = (np.exp(-((h - 24) / 15) ** 2) * _smooth(.08, .22, s) * (1 - _smooth(.62, .85, s)))[..., None]
    f = p["sat"] * (1 - skin) + p["skin_sat"] * skin
    f = f * (1 - p["hi_desat"] * _smooth(.70, 1.0, Y)) * (1 - .25 * (1 - _smooth(.02, .12, Y)))
    x = Y + (x - Y) * f
    # print curve per channel
    xs, ys = zip(*p["curve"])
    cur = PchipInterpolator(xs, ys)
    x = cur(np.clip(x, 0, 1))
    # whisper split-tone, then subtractive density
    Y2 = _luma(x)[..., None]
    x = x + np.array(p["shadow_tint"]) * (1 - Y2) ** 2.5 + np.array(p["hi_tint"]) * Y2 ** 2.5
    chroma = (x.max(-1) - x.min(-1))[..., None]
    x = x * (1 - p["density"] * chroma)
    return np.clip(x, 0, 1)


def write_lut(look: str, path: Path, n: int = 33) -> Path:
    if path.exists():
        return path
    g = np.linspace(0, 1, n)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")  # red varies fastest in the file
    rgb = np.stack([r, gg, b], -1).reshape(-1, 3)
    out = transform(rgb, look)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        fh.write(f'TITLE "vish film {look}"\nLUT_3D_SIZE {n}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        fh.write("\n".join(f"{a:.6f} {c:.6f} {d:.6f}" for a, c, d in out))
        fh.write("\n")
    return path


def is_hdr(src: Path) -> bool:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                        "-of", "csv=p=0", str(src)], capture_output=True, text=True)
    return r.stdout.strip() in ("arib-std-b67", "smpte2084")


def chain(src: Path, look: str, lut_dir: Path) -> str:
    """ffmpeg filters: HDR to SDR when needed, the film LUT, and the phone's edge sharpening softened."""
    lut = write_lut(look, lut_dir / f"film-{look}.cube")
    pre = HDR_TO_SDR + "," if is_hdr(src) else ""
    return f"{pre}lut3d=file='{lut}':interp=tetrahedral,gblur=sigma=0.55"


_DISK = {}


def _disk(r: int) -> np.ndarray:
    if r not in _DISK:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)).astype(np.float32)
        _DISK[r] = k / k.sum()
    return _DISK[r]


def pool_center(alpha: np.ndarray) -> tuple[float, float, float]:
    """Where the key light falls: centre (x, y as 0..1 of the frame) and size (0..1), from the speaker's matte."""
    m = alpha > 0.5
    if m.sum() < 50:
        return .5, .45, .35
    ys, xs = np.nonzero(m)
    h, w = alpha.shape
    top = np.percentile(ys, 2)
    return float(xs.mean() / w), float((top + 0.6 * (ys.mean() - top)) / h), float(np.clip(np.sqrt(m.mean()), .2, .6))


def finish(bgr: np.ndarray, look: str, alpha: np.ndarray | None = None, center: tuple | None = None) -> np.ndarray:
    """The spatial part, per frame (BGR uint8 in and out). alpha: the speaker's matte (any size, 0..1) or None;
    center: (x, y, size) of the light pool, smoothed over the shot by the caller (pool_center per frame)."""
    p = LOOKS[look]
    f = bgr.astype(np.float32) / 255
    h, w = f.shape[:2]
    if alpha is not None and p["bg"]:
        b = p["bg"]
        a = cv2.resize(np.clip(alpha * 1.1, 0, 1).astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
        a = cv2.GaussianBlur(a, (0, 0), 1.6)
        # lens defocus on the background only (normalised so the speaker never bleeds into it)
        hs, ws = h // 2, w // 2
        fs = cv2.resize(f, (ws, hs), interpolation=cv2.INTER_AREA)
        inv = 1 - cv2.resize(a, (ws, hs), interpolation=cv2.INTER_AREA)
        k = _disk(max(1, b["defocus"] // 2))
        num = cv2.filter2D(fs * inv[..., None], -1, k)
        den = cv2.filter2D(inv, -1, k)[..., None]
        blur = cv2.resize(num / np.maximum(den, 1e-3), (w, h), interpolation=cv2.INTER_LINEAR)
        f = f * a[..., None] + blur * (1 - a[..., None])
        # light falls off away from him like a pool from one lamp: a broad ellipse, never his outline
        cx, cy, sz = center or pool_center(cv2.resize(alpha.astype(np.float32), (w // 4, h // 4)))
        yy, xx = np.mgrid[0:h // 8, 0:w // 8].astype(np.float32)
        rx, ry = (0.30 + 0.5 * sz) * w / 8, (0.42 + 0.5 * sz) * h / 8
        pool = np.exp(-(((xx - cx * w / 8) / rx) ** 2 + ((yy - cy * h / 8) / ry) ** 2) * 1.6)
        pool = cv2.resize(pool, (w, h), interpolation=cv2.INTER_LINEAR)
        m = np.maximum(pool, a)[..., None]
        Y = _luma(f[..., ::-1])[..., None]
        f = Y + (f - Y) * (b["sat"] + (1 - b["sat"]) * m)
        cool = np.array(b["cool"][::-1], np.float32)  # BGR
        f = f * (b["gain"] + (1 - b["gain"]) * m) * (cool + (1 - cool) * m)
    # halation: red-biased glow from the brightest areas
    Y = _luma(f[..., ::-1])
    hl = np.clip((Y - .70) / .30, 0, 1) ** 1.6
    q = cv2.resize(hl, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    q = cv2.resize(cv2.GaussianBlur(q, (0, 0), 5), (w, h), interpolation=cv2.INTER_LINEAR)
    f = f + p["halation"] * q[..., None] * np.array([.18, .42, 1.0], np.float32)
    # diffusion: a soft glow that lifts only what is darker than its surroundings (Pro-Mist 1/8)
    g = cv2.resize(f, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    g = cv2.resize(cv2.GaussianBlur(g, (0, 0), 9), (w, h), interpolation=cv2.INTER_LINEAR)
    f = f + p["mist"] * np.maximum(g - f, 0)
    return (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)


class Matte:
    """Robust Video Matting (MIT) on CPU: one recurrent state per shot."""

    def __init__(self, model: str = "/home/user/models/rvm_mobilenetv3_fp32.onnx", threads: int = 2):
        import onnxruntime as ort
        o = ort.SessionOptions()
        o.intra_op_num_threads = threads
        self.sess = ort.InferenceSession(model, o, providers=["CPUExecutionProvider"])
        self.reset()

    def reset(self):
        self.rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4

    def __call__(self, bgr: np.ndarray, ratio: float = 0.4) -> np.ndarray:
        h, w = bgr.shape[:2]
        small = cv2.resize(bgr, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
        x = (small[:, :, ::-1].transpose(2, 0, 1)[None] / 255).astype(np.float32)
        _, pha, *self.rec = self.sess.run(None, {"src": x, "r1i": self.rec[0], "r2i": self.rec[1], "r3i": self.rec[2],
                                                 "r4i": self.rec[3], "downsample_ratio": np.array([ratio], np.float32)})
        return pha[0, 0]


def preview(src: Path, out: Path, look: str, at: list[float], matte: bool) -> None:
    """Before / after strip: the phone original next to the film grade."""
    tmp = out.parent / f".{out.stem}_tmp"
    tmp.mkdir(exist_ok=True)
    tiles = []
    mt = Matte() if matte else None
    for i, t in enumerate(at):
        a = tmp / f"{i}a.png"
        b = tmp / f"{i}b.png"
        pre = HDR_TO_SDR + "," if is_hdr(src) else ""
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", "-vf", pre + "format=rgb24", str(a)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1",
                        "-vf", chain(src, look, tmp) + ",format=rgb24", str(b)], check=True)
        orig, g = cv2.imread(str(a)), cv2.imread(str(b))
        al = None
        if mt:
            mt.reset()
            for _ in range(3):
                al = mt(orig)
        fin = finish(g, look, al)
        hh = 640
        tiles += [cv2.resize(orig, (int(orig.shape[1] * hh / orig.shape[0]), hh)), cv2.resize(fin, (int(fin.shape[1] * hh / fin.shape[0]), hh))]
    row = np.concatenate([np.pad(t, ((0, 0), (0, 12), (0, 0)), constant_values=255) for t in tiles], 1)
    cv2.imwrite(str(out), row, [cv2.IMWRITE_JPEG_QUALITY, 88])
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict((a[2:].split("=", 1) + [""])[:2] for a in sys.argv[1:] if a.startswith("--"))
    preview(Path(args[0]), Path(opts.get("preview", "film-preview.jpg")), opts.get("look", "night"),
            [float(x) for x in opts.get("at", "2").split(",")], "matte" in opts)
    print(opts.get("preview", "film-preview.jpg"))
