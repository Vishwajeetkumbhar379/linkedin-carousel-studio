"""Real visuals for "Nobody Tells You": maps from OpenStreetMap tiles, Wikipedia lead photos, screen captures of real sites.
    python assets.py            -> assets/*.png|jpg and assets/credits.txt (photo credits for the captions)
Maps: a handful of tiles, cached, with the OSM credit on every map card. Photos: Wikimedia Commons, credited.
"""
import io
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

A = Path(__file__).resolve().parent / "assets"
A.mkdir(exist_ok=True)
UA = {"User-Agent": "BuildWithVish-storyboard/1.0 (buildwithvvish.com)"}


def get(url, tries=4):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
        except Exception as e:  # noqa: BLE001 - rate limits come back as 429/503
            if k == tries - 1:
                raise
            time.sleep(8 * (k + 1))


def tilemap(name, z, x0, x1, y0, y1):
    if (A / f"{name}.png").exists():
        return
    im = Image.new("RGB", ((x1 - x0 + 1) * 256, (y1 - y0 + 1) * 256))
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            im.paste(Image.open(io.BytesIO(get(f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"))).convert("RGB"), ((x - x0) * 256, (y - y0) * 256))
            time.sleep(0.2)
    im.save(A / f"{name}.png")
    print(name, im.size)


def photo(name, title, width=1280):
    if (A / f"{name}.jpg").exists():
        return
    d = json.loads(get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"))
    src = d["originalimage"]["source"].split("?")[0]
    if "/thumb/" in src:  # Wikimedia only serves its standard thumbnail steps (w.wiki/GHai): 960, 1280, 1920
        src = src.rsplit("/", 1)[0] + f"/{width}px-" + src.rsplit("/", 1)[1].split("px-", 1)[-1]
    else:
        head, file = src.split("/wikipedia/commons/", 1)
        src = f"{head}/wikipedia/commons/thumb/{file}/{width}px-{file.rsplit('/', 1)[1]}"
    time.sleep(3)
    im = Image.open(io.BytesIO(get(src))).convert("RGB")
    im.thumbnail((width, width * 2))
    im.save(A / f"{name}.jpg", quality=86)
    with open(A / "credits.txt", "a") as f:
        f.write(f"{name}.jpg: Wikimedia Commons, {urllib.parse.unquote(src.rsplit('/', 1)[1])} (lead image of en.wikipedia.org/wiki/{title})\n")
    print(name, im.size)


def capture(name, url, width=760, height=5200, mobile=False):
    if (A / f"{name}.png").exists():
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1, is_mobile=mobile)
        pg.goto(url, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(2500)
        for sel in ["text=Accept all", "text=Accept", "text=Allow all", "text=I agree", "button:has-text('Accept')"]:
            try:
                pg.locator(sel).first.click(timeout=1200)
                break
            except Exception:  # noqa: BLE001
                pass
        pg.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)"); pg.wait_for_timeout(1500); pg.evaluate("window.scrollTo(0, 0)"); pg.wait_for_timeout(800)
        png = pg.screenshot(full_page=True)
        b.close()
    im = Image.open(io.BytesIO(png)).convert("RGB")
    im.crop((0, 0, im.width, min(im.height, height))).save(A / f"{name}.png", optimize=True)
    print(name, im.size)


if __name__ == "__main__":
    tilemap("map_south_asia", 5, 21, 23, 13, 15)      # India to Sri Lanka
    tilemap("map_india_europe", 4, 8, 11, 5, 7)        # India to Germany
    tilemap("map_world", 2, 0, 3, 0, 3)               # the whole world, for "different countries"
    capture("elevenlabs", "https://elevenlabs.io/")
    capture("claude_code", "https://www.anthropic.com/claude-code")
    photo("sigiriya", "Sigiriya")
    photo("ubud", "Ubud")
    photo("germany", "Neuschwanstein_Castle")
    photo("india", "Hawa_Mahal")
