#!/usr/bin/env bash
# The video editing tool stack (Vish, 22 Oct 2026). Idempotent: installs only what is missing, so it is cheap to run
# at every session start (.claude/settings.json runs it in the background).
#
#   FFmpeg          every cut, crop, mix, mute and render         github.com/FFmpeg/FFmpeg
#   faster-whisper  word-level transcription (every cut)          github.com/SYSTRAN/faster-whisper
#   Whisper         OpenAI's speech model (faster-whisper's base) github.com/openai/whisper
#   yt-dlp          downloading YouTube / Instagram sources       github.com/yt-dlp/yt-dlp
#   OpenCV contrib  tracking the speaker (CSRT), mattes, crops    github.com/opencv/opencv(_contrib)
#   Puppeteer       headless Chrome for HTML titles and captures  github.com/puppeteer/puppeteer
#   HyperFrames     agent-built motion graphics from HTML         github.com/heygen-com/hyperframes
set -u
log() { echo "[setup_tools] $*"; }
pipi() { pip install -q --break-system-packages "$@" 2>&1 | grep -v "Running pip as the 'root'" || true; }

command -v ffmpeg >/dev/null || { log "ffmpeg"; (apt-get update -qq && apt-get install -y -qq ffmpeg) >/dev/null 2>&1; }
python3 -c "import faster_whisper" 2>/dev/null || { log "faster-whisper"; pipi faster-whisper; }
python3 -c "import torch" 2>/dev/null || { log "torch (cpu)"; pipi torch --index-url https://download.pytorch.org/whl/cpu; }
python3 -c "import whisper" 2>/dev/null || { log "openai-whisper"; pipi openai-whisper; }
command -v yt-dlp >/dev/null || { log "yt-dlp"; pipi yt-dlp; }
python3 -c "import cv2; cv2.TrackerCSRT_create" 2>/dev/null || { log "opencv-contrib"; pipi opencv-contrib-python; }
npm ls -g puppeteer >/dev/null 2>&1 || { log "puppeteer"; PUPPETEER_SKIP_DOWNLOAD=1 npm install -g -s puppeteer >/dev/null 2>&1; }
npm ls -g hyperframes >/dev/null 2>&1 || { log "hyperframes"; npm install -g -s hyperframes >/dev/null 2>&1; }
# Puppeteer uses the browser that is already on the machine instead of downloading its own
[ -e /opt/pw-browsers/chromium ] && log "puppeteer browser: /opt/pw-browsers/chromium (launch with executablePath)"
log "ready"
