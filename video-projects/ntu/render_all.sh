#!/bin/bash
# Nobody Tells You v3: render the 7 episodes, two at a time, in posting order. Log per episode in work/render_<key>.log
cd "$(dirname "$0")"
( for k in e1 e3 e5 e7; do python3 ../../scripts/canvas_reel.py . $k > work/render_$k.log 2>&1; echo "$k $(tail -1 work/render_$k.log)"; done ) &
( for k in e2 e4 e6; do python3 ../../scripts/canvas_reel.py . $k > work/render_$k.log 2>&1; echo "$k $(tail -1 work/render_$k.log)"; done ) &
wait; echo ALL RENDERED
