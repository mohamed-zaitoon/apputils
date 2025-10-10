#!/data/data/com.termux/files/usr/bin/bash
# install.sh — Install & Run Debug APK + capture only crash cause (short form)

cd "$(dirname "$0")/.."

# Detect latest built APK
APK_PATH=$(find ./app/build/outputs/apk -name "*.apk" | sort -r | head -n 1)
if [ ! -f "$APK_PATH" ]; then
  echo "❌ No APK found. Run build.sh first."
  exit 1
fi

OUTPUT_DIR="./app/build/outputs"
LOG_FILE="$OUTPUT_DIR/crash.log"
mkdir -p "$OUTPUT_DIR"
rm -f "$LOG_FILE" 2>/dev/null

echo "🚀 Installing $APK_PATH ..."
adb start-server >/dev/null
adb devices

# Install via adb
if adb install -r "$APK_PATH" >/dev/null; then
  echo "✅ Installed successfully!"
else
  echo "⚠️ adb failed or no device found."
  echo "📂 Copying APK to /sdcard/Download/ for manual installation..."
  cp "$APK_PATH" /sdcard/Download/ && echo "✅ Copied to Downloads! Open it to install manually."
  exit 0
fi

# Detect package name
PKG=$(/data/data/com.termux/files/home/android-sdk/cmdline-tools/latest/bin/apkanalyzer manifest application-id "$APK_PATH" 2>/dev/null)
if [ -z "$PKG" ]; then
  PKG=$(aapt dump badging "$APK_PATH" 2>/dev/null | grep "package: name=" | awk -F"'" '{print $2}')
fi
if [ -z "$PKG" ]; then
  echo "⚠️ Unable to detect package name automatically!"
  read -p "Enter package name manually (e.g. com.example): " PKG
fi

echo "📦 Package: $PKG"
echo "▶️ Launching app..."
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1 &

echo "🩺 Capturing crash cause for $PKG ..."
echo "Logs will be saved to: $LOG_FILE"
echo "---------------------------------------------"

# Capture only fatal lines + the next 2 lines after each crash
adb logcat -v time |
grep --line-buffered -A2 "FATAL EXCEPTION" |
grep --line-buffered -E "FATAL EXCEPTION|java\.lang\.|Exception|Error" |
tee "$LOG_FILE"