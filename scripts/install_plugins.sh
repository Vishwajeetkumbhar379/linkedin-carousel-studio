#!/bin/bash
# Fetch the two large third-party skills that stay out of git (see .claude/skills/THIRD_PARTY.md).
set -e; cd "$(dirname "$0")/.."; t=$(mktemp -d)
fetch() { [ -f ".claude/skills/$2/SKILL.md" ] && return; git clone -q --depth 1 "https://github.com/$1" "$t/$2"; rm -rf "$t/$2/.git"; mkdir -p ".claude/skills/$2"; cp -r "$t/$2/$3"/. ".claude/skills/$2/"; echo "installed $2"; }
fetch hugohe3/ppt-master ppt-master skills/ppt-master
fetch tt-a1i/archify archify archify
rm -rf "$t"
