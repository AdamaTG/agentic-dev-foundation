#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE must be set}"
APP="$ROOT/apps/expo"
cd "$APP"

# Build and install APK on the already-running emulator.
npx expo run:android --no-bundler

# Start Metro and always leave its log available as a CI artifact.
export CI=1
npx expo start --localhost > "$APP/metro.log" 2>&1 &
metro_pid=$!
trap 'kill "$metro_pid" 2>/dev/null || true' EXIT

# Do not assume Metro is ready after a fixed sleep.
ready=0
for _ in $(seq 1 60); do
  if ! kill -0 "$metro_pid" 2>/dev/null; then
    echo "Metro exited unexpectedly; see apps/expo/metro.log" >&2
    exit 1
  fi
  if curl --fail --silent --max-time 2 http://127.0.0.1:8081/status | grep -q 'packager-status:running'; then
    ready=1
    break
  fi
  sleep 2
done
if [ "$ready" -ne 1 ]; then
  echo "Metro did not become ready within 120 seconds" >&2
  exit 1
fi

# Verify from repository root: stack_verify.py itself selects apps/expo for Maestro.
cd "$ROOT"
python tools/stack_verify.py --stack expo --profile e2e
