#!/bin/bash
# Nobody Tells You: render the 7 episodes on three lanes (4 cores), posting order first. Log per episode in work/render_<key>.log
cd "$(dirname "$0")"
lane() { for k in "$@"; do python3 ../../scripts/canvas_reel.py . $k > work/render_$k.log 2>&1; echo "$k $(tail -1 work/render_$k.log)"; done; }
lane e1 e4 e7 & lane e2 e5 & lane e3 e6 & wait; echo ALL RENDERED
