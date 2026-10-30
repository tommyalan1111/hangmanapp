#!/bin/bash

# Exit immediately if any command fails
set -e

echo "1. Reading and auto-incrementing version in package.json..."
PACKAGE_JSON="package.json"

# Read current version (Semantic Versioning X.Y.Z) using Node.js
CURRENT_VERSION=$(node -p "require('./$PACKAGE_JSON').version")
echo "   Old version: v$CURRENT_VERSION"

# Split Major, Minor, Patch
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "   New version: v$NEW_VERSION"

# Update new version in package.json using a compact Node.js script
node -e "
const fs = require('fs');
const file = './$PACKAGE_JSON';
const json = JSON.parse(fs.readFileSync(file, 'utf8'));
json.version = '$NEW_VERSION';
fs.writeFileSync(file, JSON.stringify(json, null, 2) + '\n');
"

echo "2. Starting web application build..."
npm run build

echo "3. Syncing Capacitor to Android..."
npx cap sync android

echo "4. Configuring Java environment (JDK 21) for macOS..."
export JAVA_HOME="/Library/Java/JavaVirtualMachines/openjdk-21.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"

echo "5. Building Android APK (Debug via Gradle)..."
cd android
./gradlew assembleDebug
cd ..

echo "6. Copying APK file to release directory with the new version..."
mkdir -p release
DEST_FILE="release/ReelHangman-$NEW_VERSION-debug.apk"
cp "android/app/build/outputs/apk/debug/app-debug.apk" "$DEST_FILE"

echo "==> APK BUILD SUCCESSFUL WITH VERSION v$NEW_VERSION! Saved at: $DEST_FILE"

echo "7. Automatically installing APK file to Android emulator/device..."
# Check if any device/emulator is connected
if adb devices | grep -qw "device"; then
    echo "Installing version v$NEW_VERSION onto the device..."
    adb install -r "$DEST_FILE"
    echo "==> INSTALLATION ON DEVICE SUCCESSFUL! You can open the app to test right away."
else
    echo "⚠️ No running/connected Android emulator or device found!"
    echo "APK file is ready at: $DEST_FILE"
fi