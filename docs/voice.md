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


## Round 4 (Vish: "still robotic and boring, find the best voice that's actually used")

**Best natural option we can reach from the container: Gemini 3.8 Flash TTS.** It's the voice engine behind a lot of current AI video and podcast tools. It breathes, pauses and changes pace by itself, and it takes a plain-English style prompt. It's built into `scripts/voiceover.py` as `--engine gemini`, and it switches on automatically when `GEMINI_API_KEY` is set.

Set it up (2 minutes, free tier):
1. Get a key at https://aistudio.google.com/apikey (Google account, free tier, no card).
2. In Claude Code on the web: open this environment's settings (environment menu → Edit) and add an environment variable `GEMINI_API_KEY=<your key>`. Never paste the key into chat or into the repo.
3. Start a new session (environment variables load at session start). Then: `python scripts/voiceover.py out/<post>/video.json` (defaults to voice Puck). Try `--voice Achird`, `--voice Sadachbia` or `--voice Zubenelgenubi`, and `--style "..."` to steer delivery.

Cost: the free tier covers this volume. Paid rates if it's ever needed: about $1 per 1M input text tokens and $20 per 1M audio tokens, so a 35 s voiceover costs well under one cent. Flagged anyway.

**Your own voice (best of all):** Gemini voice replication can clone from a short recording. Send a 30 to 60 s voice memo of you talking normally, plus one spoken consent line ("I, Vishwajeet Kumbhar, consent to my voice being used to generate audio for Build with Vish"). Then every video sounds like you.

Kokoro (the offline fallback) also improved this round: it now reads a whole scene in one pass, so intonation runs across the sentence instead of resetting at every phrase. Still not as alive as Gemini.

ElevenLabs remains the paid alternative (from about $5 a month, flagged, and its API is blocked from this container).
