# Voiceover

## Today: open voice (no cost)
`python scripts/voiceover.py out/<post>/video.json --voice af_heart`
- Engine: Kokoro-82M (Apache-2.0) via kokoro-onnx, runs on CPU in ~20 s for a 1-minute script.
- Natural pacing: the script is voiced phrase by phrase; pauses follow punctuation (comma 0.16 s, full stop 0.38 s, question 0.42 s, scene change 0.5 s), speed varies ±2.5% between phrases, a soft inhale sits between scenes, and a warm pad at -31 dB sits under the voice. Final mix is loudness-normalised to -15 LUFS.
- The video follows the voice: scene timings and subtitle chunks are written back into `video.json`, so captions always match the audio.
- Voices included in the review: `af_heart` (default, the model's highest-rated voice) and `am_michael` (male alternative, `voice-alt-male.wav`).

## Next: your own voice
Send a clean 30 to 60 second recording (phone voice memo is fine, quiet room, normal speaking pace, no music). Read anything, ideally a past post.
- Engine: Chatterbox (Resemble AI, MIT licence) clones a voice from one reference clip and adds natural expressiveness (`exaggeration` setting).
- It needs Hugging Face, which this cloud container blocks. Two ways to run it: (a) allow `huggingface.co` in the environment's network settings, or (b) run it in GitHub Actions. I'll add the Chatterbox mode to `scripts/voiceover.py` for whichever you pick.
- Consent: only your own voice, only for your own posts. The recording stays out of the public repo (`brand/voice/` is git-ignored).
