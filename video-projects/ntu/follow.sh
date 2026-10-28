#!/bin/bash
# After the first batch: re-render the episodes that started before the syllable mouth fix.
cd "$(dirname "$0")"
until grep -q "ALL RENDERED" work/render_all.log; do sleep 20; done
( for k in e3 e1; do python3 ../../scripts/canvas_reel.py . $k > work/render_$k.log 2>&1; echo "$k $(tail -1 work/render_$k.log)"; done ) &
( for k in e2; do python3 ../../scripts/canvas_reel.py . $k > work/render_$k.log 2>&1; echo "$k $(tail -1 work/render_$k.log)"; done ) &
wait; echo FOLLOW DONE
