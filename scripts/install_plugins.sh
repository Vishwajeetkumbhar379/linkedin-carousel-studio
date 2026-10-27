#!/bin/bash
# Fetch the two large third-party skills that stay out of git (see .claude/skills/THIRD_PARTY.md).
set -e; cd "$(dirname "$0")/.."; t=$(mktemp -d)
fetch() { [ -f ".claude/skills/$2/SKILL.md" ] && return; git clone -q --depth 1 "https://github.com/$1" "$t/$2"; rm -rf "$t/$2/.git"; mkdir -p ".claude/skills/$2"; cp -r "$t/$2/$3"/. ".claude/skills/$2/"; echo "installed $2"; }
fetch hugohe3/ppt-master ppt-master skills/ppt-master
fetch tt-a1i/archify archify archify
rm -rf "$t"
# Remotion's skills repo has no licence, so they are fetched here rather than committed
t=$(mktemp -d); if [ ! -f .claude/skills/remotion-best-practices/SKILL.md ]; then
  git clone -q --depth 1 https://github.com/remotion-dev/skills "$t/r" && for d in "$t"/r/skills/*/; do n=$(basename "$d"); [ -e ".claude/skills/$n" ] || cp -r "$d" ".claude/skills/$n"; done && echo "installed remotion skills"
fi; rm -rf "$t"
