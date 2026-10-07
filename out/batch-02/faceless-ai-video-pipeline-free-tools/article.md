# How to automate a faceless AI content pipeline, step by step, with free tools

## The pipeline in one line

Script → voice → B-roll → motion → sound → captions → schedule. Each step has a free option, and none of them needs your face on camera. Here is the stack I'd use, with the catch for each step.

## 01 · Script with free models

Write the script with an LLM routed through FreeLLMAPI or OmniRoute. Both are open-source projects that put many free tiers behind one OpenAI-compatible endpoint, so a rate limit on one provider doesn't stop your run. A prompt to start with:

> Write a 70-word voiceover for a 35-second video. One idea per line. Plain British English. Every number needs a source link I can check.

Then read every claim yourself. Free models make confident mistakes.

## 02 · Voice with an open model

Kokoro-82M is an open-weight text-to-speech model with 82 million parameters and Apache-licensed weights. On Hugging Face's new Open TTS Leaderboard, published on 30 September, it's one of three models leading on English word error rate, alongside `Supertone/supertonic-3` and `fishaudio/s2-pro`. The leaderboard measures intelligibility, speed and speaker similarity, not how natural a voice sounds, so use its Listen tab before you pick. Write lines you can say in one breath.

## 03 · B-roll from real screens

Record the actual thing you're talking about: the GitHub repo, the docs page, the changelog. OBS Studio is free, open-source software for recording and streaming on Windows, Mac and Linux. A real screen is more believable than a stock clip of someone typing, and it shows you did the homework.

## 04 · Motion graphics in code

Remotion lets you build videos with React. Its licence, as shipped with version 4.0.533 on 5 October, is free, commercial use included, for individuals, for-profit companies with up to 3 employees, and non-profits. Bigger companies need a company licence. Keep one idea per screen and let text move only when the line changes.

## 05 · Sound design

Freesound hosts sounds under Creative Commons licences. CC0 sounds can be used almost any way you like. Attribution sounds need a credit. Noncommercial sounds can't be used commercially, which rules out ads. A soft whoosh on scene changes and a quiet music bed go a long way.

## 06 · Captions

Transcribe your own voiceover so the captions match word for word. Hugging Face describes Qwen3 ASR as the top-ranking open-source model on its Open ASR Leaderboard. Whatever you use, fix names, brands and numbers by hand.

## 07 · Scheduling

Buffer's free plan connects up to 3 channels with 10 scheduled posts per channel. Schedule the post, then turn up in the comments yourself. Automation can publish. It can't have the conversation.

## What I'd do

Start with steps 01, 02 and 06 this week, because they save the most time. Add screen recordings next, because they make the video believable. Leave motion graphics until the script and voice feel right. And keep a human check on every fact before anything goes live.

## Sources

- FreeLLMAPI README: https://github.com/tashfeenahmed/freellmapi
- OmniRoute README: https://github.com/diegosouzapw/OmniRoute
- Kokoro-82M model card: https://huggingface.co/hexgrad/Kokoro-82M
- Hugging Face, Open TTS Leaderboard (30 Sep 2026): https://huggingface.co/blog/open-tts-leaderboard
- OBS Studio: https://obsproject.com/
- Remotion licence, v4.0.533: https://unpkg.com/remotion@4.0.533/LICENSE.md
- Freesound FAQ (licences): https://freesound.org/help/faq/
- Buffer pricing: https://buffer.com/pricing
