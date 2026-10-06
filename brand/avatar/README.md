# Vish avatar (stylised 3D)

Made on 6 Oct 2026 in Canva's image generator from Vish's own public portrait (`buildwithvish/src/vish.jpg`), at his request.

| Version | Canva media | Notes |
|---|---|---|
| v1 | https://www.canva.com/M/MAHXQUwQ-oI | Too photo-real. Not used |
| v2 | https://www.canva.com/M/MAHXQSEoDQQ | Stylised 3D head-and-shoulders, violet gradient background |
| v3 sheet | https://www.canva.com/M/MAHXQiVWMLk | Full body + 3 expression heads. Wrong trousers (skinny) per Vish, round 4 |
| v4 sheet | https://www.canva.com/M/MAHXQ4Mf8bM | Round 4: bootcut denim and chelsea boots (Canva) |
| **v5 sheet** | `vish-3d-sheet.png` | Round 5: Vish's own ChatGPT-made sheet (`vish-3d-sheet-original.jpg`), skin lifted toward his real photo with `scripts/skin_tone.py --lift 0.12 --desat 0.85`. Stronger option: `vish-3d-sheet-lighter.png` (`--lift 0.2 --desat 0.78`). Crops: `vish-3d-full.png`, `vish-3d-laugh.png`, `vish-3d-smirk.png`, `vish-3d-surprised.png`. **Current** |

The full-size file can't be downloaded inside the cloud container (Canva's download hosts are blocked by its network policy). To use it in the pipeline:
1. Open the v4 sheet link, download the PNG. Or: connect Google Drive in Zapier once (link in the review page) and the pipeline fetches Canva exports itself.
2. Save it as `brand/avatar/vish-3d.png` (or send it in chat).
3. Any slide can then use `"mascot": "vish-3d"` or `"hero": "vish-3d"`.

Where it goes: CTA slides ("Follow Vish for…"), build-in-public posts, career posts. Dot (the glass mascot) stays the default sidekick on explainer slides. Never on posts about other people's products as if endorsing them.
