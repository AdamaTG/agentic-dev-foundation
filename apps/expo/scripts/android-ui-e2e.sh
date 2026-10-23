#!/usr/bin/env bash
set -Eeuo pipefail
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$APP_DIR/ci-evidence"
mkdir -p "$OUT"
command -v adb >/dev/null || { echo 'adb is missing' >&2; exit 1; }
adb wait-for-device
adb shell pm path com.adf.reference | tr -d '\r' > "$OUT/package-check.txt"
grep -q '^package:' "$OUT/package-check.txt" || { echo 'App not installed' >&2; exit 1; }
# Wait for asynchronous Metro bundle and React Native UI render.
# UIAutomator reads the actual accessibility hierarchy on the Android device.
seen=0
: > "$OUT/uiautomator-attempts.log"
for n in $(seq 1 36); do
  adb shell uiautomator dump /sdcard/adf-ui.xml >> "$OUT/uiautomator-attempts.log" 2>&1 || true
  adb exec-out cat /sdcard/adf-ui.xml > "$OUT/ui-hierarchy.xml" 2>/dev/null || true
  if grep -Fq 'ADF Mobile Reference' "$OUT/ui-hierarchy.xml"; then seen=1; break; fi
  echo "UI text not visible yet (attempt $n/36)" >> "$OUT/uiautomator-attempts.log"
  sleep 5
done
adb exec-out screencap -p > "$OUT/android-screen.png" || true
if [ "$seen" -ne 1 ]; then
  echo 'E2E FAIL: expected text not found in Android UI hierarchy' >&2
  sed -n '1,15p' "$OUT/uiautomator-attempts.log" >&2 || true
  head -c 1600 "$OUT/ui-hierarchy.xml" >&2 || true
  echo >&2
  exit 1
fi
printf 'E2E PASS: actual Android UI contains expected reference text.\n'
