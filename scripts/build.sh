#!/data/data/com.termux/files/usr/bin/bash
# build.sh — Build TikTokCoinApp APK in Termux (auto-install for debug)

cd "$(dirname "$0")/.."

GRADLE_PROPS="gradle.properties"
AAPT2_LINE='android.aapt2FromMavenOverride=/data/data/com.termux/files/home/android-sdk/build-tools/8.13.0/aapt2'

# 🧩 Detect if running inside Termux and add override if missing
if [ -n "$TERMUX_VERSION" ] || [ -n "$ANDROID_ROOT" ]; then
  if ! grep -q "android.aapt2FromMavenOverride" "$GRADLE_PROPS" 2>/dev/null; then
    echo "📦 Detected Termux — adding AAPT2 override..."
    echo "$AAPT2_LINE" >> "$GRADLE_PROPS"
    echo "✅ Added AAPT2 override to gradle.properties"
  else
    echo "ℹ️ AAPT2 override already exists, skipping..."
  fi
fi

# ✅ Check gradlew
if [ ! -f "./gradlew" ]; then
  echo "❌ gradlew not found in this directory."
  exit 1
fi

echo "🚀 Starting build..."
echo "---------------------------------------------"

# Clean project
bash gradlew clean

# 🏗️ Ask build type
echo ""
echo "Select build type:"
echo "1) Debug"
echo "2) Release"
read -p "Enter choice [1-2]: " choice

if [ "$choice" = "2" ]; then
  bash gradlew assembleRelease
  BUILD_TYPE="release"
else
  bash gradlew assembleDebug
  BUILD_TYPE="debug"
fi

# 🔍 Find APK output
APK_PATH=$(find ./app/build/outputs/apk/$BUILD_TYPE -name "*.apk" | head -n 1)

if [ -f "$APK_PATH" ]; then
  echo ""
  echo "✅ Build successful!"
  echo "📦 APK generated at: $APK_PATH"
else
  echo ""
  echo "❌ Build failed. Please check the Gradle output above."
  if grep -q "android.aapt2FromMavenOverride" "$GRADLE_PROPS" 2>/dev/null; then
    sed -i '/android.aapt2FromMavenOverride/d' "$GRADLE_PROPS"
    echo "🧹 Removed AAPT2 override after failed build."
  fi
  exit 1
fi

# 🧹 Cleanup after build
if grep -q "android.aapt2FromMavenOverride" "$GRADLE_PROPS" 2>/dev/null; then
  sed -i '/android.aapt2FromMavenOverride/d' "$GRADLE_PROPS"
  echo "🧹 Removed AAPT2 override after build."
fi

# 🚀 Auto-install if debug
if [ "$BUILD_TYPE" = "debug" ]; then
  echo ""
  echo "📲 Auto-installing Debug build..."
  sh ./scripts/install.sh
fi