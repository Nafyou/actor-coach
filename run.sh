#!/bin/bash
# Launch Actor Coach. Usage: ./run.sh [camera-index | --list]
#
# Why this wrapper exists: Homebrew's current python@3.13 ships a pyexpat
# linked against a libexpat that is missing XML_SetAllocTrackerActivationThreshold
# on this machine, so `import mediapipe` dies on `import matplotlib -> plistlib`.
# If the venv's interpreter is broken, repoint the venv at any Cellar python3.13
# whose pyexpat actually loads.
set -euo pipefail
cd "$(dirname "$0")"

VENV_PY=.venv/bin/python

if [ ! -x "$VENV_PY" ]; then
  echo "No .venv found. Create it first:" >&2
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

if ! "$VENV_PY" -c "import pyexpat" >/dev/null 2>&1; then
  echo "venv interpreter has a broken pyexpat; looking for a working python3.13..." >&2
  for cand in /opt/homebrew/Cellar/python@3.13/*/Frameworks/Python.framework/Versions/3.13/bin/python3.13; do
    [ -x "$cand" ] || continue
    if "$cand" -c "import pyexpat" >/dev/null 2>&1; then
      ln -sfn "$cand" .venv/bin/python3.13
      sed -i '' "s|^home = .*|home = $(dirname "$cand")|" .venv/pyvenv.cfg
      echo "repointed .venv at $cand" >&2
      break
    fi
  done
  "$VENV_PY" -c "import pyexpat" >/dev/null 2>&1 || {
    echo "Still broken. Try: brew reinstall python@3.13  (or rebuild the venv on python3.11)" >&2
    exit 1
  }
fi

exec "$VENV_PY" actor_coach.py "$@"
