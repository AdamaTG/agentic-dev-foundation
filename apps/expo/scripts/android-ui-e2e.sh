#!/usr/bin/env bash
set -Eeuo pipefail
# Runs inside the active Android emulator. This is a real on-device UI smoke E2E gate.
# It is not a substitute for complex Maestro journeys, which remain available outside the required CI.
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$APP_DIR/ci-evidence"
mkdir -p "$OUT"
command -v adb >/dev/null || { echo 'adb is unavailable' >&2; exit 1; }
adb wait-for-device
adb shell pm path com.adf.reference | grep -q '^package:' || { echo 'Reference Android APK is not installed' >&2; exit 1; }
seen=0
for n in $(seq 1 18); do
  adb shell uiautomator dump /sdcard/adf-ui.xml > "$OUT/uiautomator-command.log" 2>&1 || true
  adb exec-out cat /sdcard/adf-ui.xml > "$OUT/ui-hierarchy.xml" 2>/dev/null || true
  if grep -q 'ADF Mobile Reference' "$OUT/ui-hierarchy.xml"; then seen=1; break; fi
  sleep 5
done
adb exec-out screencap -p > "$OUT/android-screen.png" || true
if [ "$seen" != 1 ]; then
  echo 'E2E FAIL: expected text "ADF Mobile Reference" not visible on Android UI hierarchy.' >&2
  echo 'UI hierarchy (first 600 chars):' >&2
  head -c 600 "$OUT/ui-hierarchy.xml" >&2 || true
  echo >&2
  exit 1
fi
printf 'E2E PASS: launched installed Android app and verified visible UI text.\n'
