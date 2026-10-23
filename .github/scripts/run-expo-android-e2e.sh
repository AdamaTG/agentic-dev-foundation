#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE must be set}"
APP="$ROOT/apps/expo"
EVIDENCE="$APP/ci-evidence"
mkdir -p "$EVIDENCE"
cleanup() {
  local code=$?
  adb logcat -d -t 400 > "$EVIDENCE/android-logcat-tail.txt" 2>&1 || true
  adb shell dumpsys activity activities > "$EVIDENCE/android-activities.txt" 2>&1 || true
  if [ -n "${METRO_PID:-}" ]; then kill "$METRO_PID" 2>/dev/null || true; fi
  exit "$code"
}
trap cleanup EXIT
cd "$APP"
export CI=1
export EXPO_NO_TELEMETRY=1
export MAESTRO_CLI_NO_ANALYTICS=1

echo '== Android emulator preflight =='
adb wait-for-device
for n in $(seq 1 60); do
  if [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = 1 ]; then break; fi
  sleep 2
done
[ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = 1 ] || { echo 'Emulator did not boot' >&2; exit 1; }
adb shell input keyevent 82 || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true

echo '== Build and install APK =='
npx expo prebuild --platform android --no-install
( cd android && ./gradlew --no-daemon assembleDebug )
APK="$APP/android/app/build/outputs/apk/debug/app-debug.apk"
test -s "$APK"
adb install -r "$APK"
adb shell pm path com.adf.reference | tee "$EVIDENCE/package-path.txt"
grep -q '^package:' "$EVIDENCE/package-path.txt" || { echo 'APK not installed' >&2; exit 1; }

echo '== Start Metro =='
npx expo start --localhost --port 8081 > "$APP/metro.log" 2>&1 &
METRO_PID=$!
ready=0
for n in $(seq 1 60); do
  kill -0 "$METRO_PID" 2>/dev/null || { echo 'Metro exited unexpectedly' >&2; tail -n 100 "$APP/metro.log" >&2; exit 1; }
  if curl -fsS --max-time 2 http://127.0.0.1:8081/status | grep -q 'packager-status:running'; then ready=1; break; fi
  sleep 2
done
[ "$ready" = 1 ] || { echo 'Metro never became ready' >&2; tail -n 100 "$APP/metro.log" >&2; exit 1; }
adb reverse tcp:8081 tcp:8081

echo '== Launch installed app (independent of Expo CLI) =='
adb shell am force-stop com.adf.reference || true
adb shell am start -W -n com.adf.reference/.MainActivity | tee "$EVIDENCE/activity-start.txt"

echo '== Mandatory on-device UI E2E assertion =='
cd "$ROOT"
python tools/stack_verify.py --stack expo --profile e2e || {
  echo 'E2E failed. Device logs:' >&2
  tail -n 60 "$EVIDENCE/android-logcat-tail.txt" 2>/dev/null || true
  exit 1
}
