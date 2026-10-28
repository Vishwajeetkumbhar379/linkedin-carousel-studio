#!/bin/bash
# Inside AI: render EP 3 to 9 on three lanes (4 cores), posting order first. Log per episode in work/render_<key>.log
cd "$(dirname "$0")"
lane() { for k in "$@"; do python3 ../../scripts/canvas_reel.py . $k > work/render_$k.log 2>&1; echo "$k $(tail -1 work/render_$k.log)"; done; }
lane a3 a6 a9 & lane a4 a7 & lane a5 a8 & wait; echo ALL RENDERED
