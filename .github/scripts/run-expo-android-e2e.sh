#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE must be set}"
APP="$ROOT/apps/expo"
EVIDENCE="$APP/ci-evidence"
mkdir -p "$EVIDENCE"
METRO_PID=''
cleanup() {
  local code=$?
  set +e
  adb devices -l > "$EVIDENCE/adb-devices-final.txt" 2>&1
  adb logcat -d -t 2000 > "$EVIDENCE/android-logcat-tail.txt" 2>&1
  adb shell dumpsys activity activities > "$EVIDENCE/android-activities.txt" 2>&1
  adb shell dumpsys meminfo com.adf.reference > "$EVIDENCE/android-app-meminfo.txt" 2>&1
  if [ -n "$METRO_PID" ]; then kill "$METRO_PID" 2>/dev/null; fi
  if [ "$code" -ne 0 ]; then
    echo '=== Android E2E failed; final diagnostics ===' >&2
    tail -n 80 "$APP/metro.log" 2>/dev/null >&2
    tail -n 100 "$EVIDENCE/android-logcat-tail.txt" 2>/dev/null >&2
  fi
  exit "$code"
}
trap cleanup EXIT
export CI=1 EXPO_NO_TELEMETRY=1
cd "$APP"
echo '== Android emulator readiness =='
adb wait-for-device
booted=0
for n in $(seq 1 90); do
  if [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = '1' ]; then booted=1; break; fi
  sleep 2
done
[ "$booted" -eq 1 ] || { echo 'Emulator did not boot' >&2; exit 1; }
adb shell input keyevent 82 || true
for setting in window_animation_scale transition_animation_scale animator_duration_scale; do
  adb shell settings put global "$setting" 0 || true
done

echo '== Build Android debug APK =='
npx expo prebuild --platform android --no-install
( cd android && ./gradlew --no-daemon assembleDebug )
APK="$APP/android/app/build/outputs/apk/debug/app-debug.apk"
test -s "$APK"
echo '== Install Android debug APK =='
adb install -r "$APK"
adb shell pm path com.adf.reference | tr -d '\r' | tee "$EVIDENCE/package-path.txt"
grep -q '^package:' "$EVIDENCE/package-path.txt" || { echo 'APK package not installed' >&2; exit 1; }

echo '== Start Metro =='
npx expo start --localhost --port 8081 > "$APP/metro.log" 2>&1 &
METRO_PID=$!
ready=0
for n in $(seq 1 90); do
  kill -0 "$METRO_PID" 2>/dev/null || { echo 'Metro stopped prematurely' >&2; exit 1; }
  if curl -fsS --max-time 2 http://127.0.0.1:8081/status 2>/dev/null | grep -q 'packager-status:running'; then ready=1; break; fi
  sleep 2
done
[ "$ready" -eq 1 ] || { echo 'Metro not ready' >&2; exit 1; }
adb reverse tcp:8081 tcp:8081

echo '== Launch app and validate activity =='
adb shell am force-stop com.adf.reference || true
adb shell am start -W -n com.adf.reference/.MainActivity | tee "$EVIDENCE/activity-start.txt"
if grep -qiE 'Error:|does not exist|Exception|unable to resolve' "$EVIDENCE/activity-start.txt"; then
  echo 'Android activity launch failed' >&2; exit 1
fi

echo '== Run mandatory on-device UI E2E =='
cd "$ROOT"
python tools/stack_verify.py --stack expo --profile e2e
