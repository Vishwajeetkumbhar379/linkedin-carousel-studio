# Build with Vish content engine. Run `make help`.
PY ?= python3
TODAY := $(shell date +%F)
POST ?= $(lastword $(sort $(wildcard out/20*)))

help:            ## list commands
	@grep -E '^[a-z-]+:.*## ' Makefile | sed 's/:.*## /\t/'

setup:           ## install Python + Node deps (Playwright pinned to the preinstalled Chromium)
	pip install -e ".[dev]" "playwright==1.56.0"
	cd templates && npm ci

research:        ## pull fresh items from all feeds into research/daily/
	$(PY) scripts/research/fetch.py $(TODAY)

mascot:          ## re-render the mascot poses and sheet
	$(PY) scripts/render3d.py --batch brand/mascot/specs brand/mascot/poses

heroes:          ## re-render 3D hero objects for the samples
	$(PY) scripts/render3d.py --batch out/_samples/specs out/_samples/3d

build:           ## render POST=out/<folder> (deck.json -> slides + PDF; video.json -> MP4)
	@if [ -f $(POST)/deck.json ]; then $(PY) scripts/build_post.py $(POST); fi
	@if [ -f $(POST)/video.json ]; then $(PY) scripts/render_video.py $(POST)/video.json; fi

qa:              ## run the quality gate on POST
	$(PY) scripts/qa.py $(POST)

post: build qa   ## research is manual for now: draft deck.json in out/<date-slug>/, then `make post POST=...`
	@echo "Review pack ready: $(POST)"

samples:         ## rebuild and QA the three test-gate samples
	$(PY) scripts/build_post.py out/2026-10-06-eu-ai-text-watermark out/2026-10-06-meta-creator-hub
	$(PY) scripts/render_video.py out/2026-10-06-chatgpt-image-ads/video.json
	QA_TODAY=2026-10-06 $(PY) scripts/qa.py out/2026-10-06-eu-ai-text-watermark out/2026-10-06-meta-creator-hub out/2026-10-06-chatgpt-image-ads --no-net

week:            ## after the go-ahead: research -> top 5-7 topics -> drafts -> build -> QA (drafting step lands after Vish picks a direction)
	@echo "Locked until Vish approves a direction at the test-first gate."

test:            ## unit tests
	pytest -q

.PHONY: help setup research mascot heroes build qa post samples week test
