# engine/scripts/shorts

Create short videos with voice narration and sound effects from templates.

- `scripts/shorts/render.py`: Render short video from HTML template, capture frames in parallel, mix voice/SFX, write stills, video.mp4, cover.png. (uses render3d.py, sound.py)
- `scripts/shorts/sound.py`: Generate synthetic SFX waveforms and mix them with voice and background bed, ducking and normalising audio.
- `scripts/shorts/voice.py`: Call ElevenLabs TTS API to synthesize full short narration, save voice.wav and alignment JSON, log credit usage.
- `scripts/shorts/voice_samples.py`: Generate short sample clips for several ElevenLabs narrator voices using preset text, store in output folder. (uses voice.py, samples.json)
