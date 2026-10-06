# Vish avatar (stylised 3D)

Made on 6 Oct 2026 in Canva's image generator from Vish's own public portrait (`buildwithvish/src/vish.jpg`), at his request.

| Version | Canva media | Notes |
|---|---|---|
| v1 | https://www.canva.com/M/MAHXQUwQ-oI | Too photo-real. Not used |
| v2 | https://www.canva.com/M/MAHXQSEoDQQ | Stylised 3D head-and-shoulders, violet gradient background |
| **v3 sheet** | https://www.canva.com/M/MAHXQiVWMLk | Full body (arms crossed, blazer, sneakers) + 3 expression heads (laughing, smirk, surprised), light background. **Recommended**, matches the reference Vish sent |

The full-size file can't be downloaded inside the cloud container (Canva's download hosts are blocked by its network policy). To use it in the pipeline:
1. Open the v3 sheet link, download the PNG. Or: connect Google Drive in Zapier once (link in the review page) and the pipeline fetches Canva exports itself.
2. Save it as `brand/avatar/vish-3d.png` (or send it in chat).
3. Any slide can then use `"mascot": "vish-3d"` or `"hero": "vish-3d"`.

Where it goes: CTA slides ("Follow Vish for…"), build-in-public posts, career posts. Dot (the glass mascot) stays the default sidekick on explainer slides. Never on posts about other people's products as if endorsing them.
