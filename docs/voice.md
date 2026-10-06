# Voiceover

## Today: open voice (no cost)
`python scripts/voiceover.py out/<post>/video.json --voice af_heart`
- Engine: Kokoro-82M (Apache-2.0) via kokoro-onnx, runs on CPU in ~20 s for a 1-minute script.
- Natural pacing: the script is voiced phrase by phrase; pauses follow punctuation (comma 0.16 s, full stop 0.38 s, question 0.42 s, scene change 0.5 s), speed varies ±2.5% between phrases, a soft inhale sits between scenes, and a warm pad at -31 dB sits under the voice. Final mix is loudness-normalised to -15 LUFS.
- The video follows the voice: scene timings and subtitle chunks are written back into `video.json`, so captions always match the audio.
- Voices included in the review: `af_heart` (default, the model's highest-rated voice) and `am_michael` (male alternative, `voice-alt-male.wav`).

## Round 3 changes (Vish: "too robotic", wants a younger, captivating male voice)
- The narration is now its own conversational script (`narration` in video.json). It summarises; it does not read the screen. 35 s instead of 55 s.
- Voice: a blend of Kokoro's two best-rated male voices, `am_puck:0.6,am_fenrir:0.4`, at 1.07x speed with tighter pauses. Alternative in the review: `am_michael:0.5,am_puck:0.5`.
- Honest limit: Kokoro is the best open voice that runs inside this locked-down container, and its male voices are its weaker ones. A truly "ChatGPT-voice" level of breathing and emotion needs a bigger model.

## The real fix, ranked
1. **Your own voice, cloned (best, free):** send a 30 to 60 s voice memo. Chatterbox (Resemble AI, MIT) clones it and has an expressiveness dial. It runs on Hugging Face. Fastest switch-on: in your Hugging Face MCP settings, enable Spaces/Gradio tools (the connector currently has them off, "gradio=none"), then I can call the `ResembleAI/Chatterbox` Space directly. Or allow `huggingface.co` in this environment's network settings and it runs locally.
2. **ElevenLabs (paid, flagged):** the most natural stock and cloned voices; costs money per month, so only with your OK.
3. **Kokoro blend (today, free):** what the current video uses.

Send a clean 30 to 60 second recording (phone voice memo is fine, quiet room, normal speaking pace, no music). Read anything, ideally a past post.
- Engine: Chatterbox (Resemble AI, MIT licence) clones a voice from one reference clip and adds natural expressiveness (`exaggeration` setting).
- It needs Hugging Face, which this cloud container blocks. Two ways to run it: (a) allow `huggingface.co` in the environment's network settings, or (b) run it in GitHub Actions. I'll add the Chatterbox mode to `scripts/voiceover.py` for whichever you pick.
- Consent: only your own voice, only for your own posts. The recording stays out of the public repo (`brand/voice/` is git-ignored).
