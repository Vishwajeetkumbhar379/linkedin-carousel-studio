# engine/scripts/research

Collect, parse, and analyze external content feeds, social media posts, and video data for research.

- `scripts/research/fetch.py`: Fetches RSS and Hacker News feeds, parses items, stores daily JSON per date. (uses sources.json)
- `scripts/research/ig_fetch.py`: Fetches Instagram posts/reels via headless Chromium, extracts caption, author, media, carousel images, screenshots, saves to output folder.
- `scripts/research/reel_teardown.py`: Analyzes video cuts, transcripts, sound onsets, generates shot metadata, thumbnails, and frame strips using ffmpeg and faster-whisper. (uses transcript.json)
- `scripts/research/sources.json`: JSON: _note, feeds, keywords_boost, keywords_drop
