#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="${GITHUB_WORKSPACE:?}"
EVIDENCE="$ROOT/apps/expo/ci-evidence"
mkdir -p "$EVIDENCE"
trap 'rc=$?; adb devices -l > "$EVIDENCE/adb-final.txt" 2>&1 || true; adb logcat -d -t 5000 > "$EVIDENCE/logcat-final.txt" 2>&1 || true; echo "Diagnostic exit code: $rc"; exit "$rc"' EXIT
{
  echo "=== versions ==="
  date -u
  uname -a
  java -version 2>&1
  maestro --version 2>&1
  adb version
  echo "=== devices ==="
  adb devices -l
  echo "=== boot state ==="
  adb shell getprop sys.boot_completed
  adb shell getprop ro.build.version.sdk
  adb shell getprop ro.product.cpu.abi
  echo "=== memory ==="
  free -h
  df -h "$ROOT"
  adb shell dumpsys meminfo | head -n 45
  echo "=== package availability ==="
  adb shell pm list packages com.android.settings
} 2>&1 | tee "$EVIDENCE/environment.txt"

cat > "$EVIDENCE/maestro-settings-smoke.yaml" <<'FLOW'
appId: com.android.settings
---
- launchApp
FLOW

# The control tests the Maestro driver with Android Settings, not the Expo app.
# Any nonzero result is a real failure; the full CLI output is retained.
set +e
timeout --signal=TERM --kill-after=15s 240s maestro test "$EVIDENCE/maestro-settings-smoke.yaml" --format junit --output "$EVIDENCE/maestro-settings.xml" > "$EVIDENCE/maestro-settings.log" 2>&1
rc=$?
set -e
cat "$EVIDENCE/maestro-settings.log"
if [ "$rc" -ne 0 ]; then
  echo "::error::Maestro minimal Android Settings test failed (exit $rc). See evidence-expo-diagnostic artifact."
  exit "$rc"
fi

echo 'Minimal Maestro driver test PASSED; now run the app-specific E2E pipeline.'
