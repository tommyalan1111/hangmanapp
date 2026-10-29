# ==========================================
# Build Reel Hangman APK, bump versions, install
# Compatible with Windows PowerShell 5.1
# ==========================================

$ErrorActionPreference = "Stop"
$root = "E:\Work\Hangman app"
Set-Location $root

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Write-TextNoBom([string]$path, [string]$text) {
    [System.IO.File]::WriteAllText((Resolve-Path $path).Path, $text, $utf8NoBom)
}

Write-Host "1. Bumping patch version..." -ForegroundColor Cyan

$oldVersion = (node -p "require('./package.json').version").Trim()

npm version patch --no-git-tag-version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "npm version failed"
}

$newVersion = (node -p "require('./package.json').version").Trim()
Write-Host "   $oldVersion -> $newVersion" -ForegroundColor Green

# Keep the visible app version in sync with package.json.
$versionTs = Join-Path $root "src\version.ts"
$versionText = [System.IO.File]::ReadAllText($versionTs)
$versionText = [regex]::Replace($versionText, 'APP_VERSION = "[^"]+"', "APP_VERSION = `"$newVersion`"")
Write-TextNoBom $versionTs $versionText

# Keep Android versionCode/versionName in sync.
$gradlePath = Join-Path $root "android\app\build.gradle"
$gradleText = [System.IO.File]::ReadAllText($gradlePath)
$codeMatch = [regex]::Match($gradleText, 'versionCode\s+(\d+)')
if (-not $codeMatch.Success) {
    throw "versionCode not found in android/app/build.gradle"
}
$newCode = [int]$codeMatch.Groups[1].Value + 1
$gradleText = [regex]::Replace($gradleText, 'versionCode\s+\d+', "versionCode $newCode")
$gradleText = [regex]::Replace($gradleText, 'versionName\s+"[^"]+"', "versionName `"$newVersion`"")
Write-TextNoBom $gradlePath $gradleText

# Keep the iOS project in sync too.
$pbxPath = Join-Path $root "ios\App\App.xcodeproj\project.pbxproj"
$pbxText = [System.IO.File]::ReadAllText($pbxPath)
$pbxText = [regex]::Replace($pbxText, 'CURRENT_PROJECT_VERSION = \d+;', "CURRENT_PROJECT_VERSION = $newCode;")
$pbxText = [regex]::Replace($pbxText, 'MARKETING_VERSION = [^;]+;', "MARKETING_VERSION = $newVersion;")
Write-TextNoBom $pbxPath $pbxText

Write-Host "2. Building web app..." -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) {
    throw "Web build failed"
}

Write-Host "3. Syncing Capacitor Android..." -ForegroundColor Cyan
npx cap sync android
if ($LASTEXITCODE -ne 0) {
    throw "Capacitor sync failed"
}

Write-Host "4. Configuring JDK 21..." -ForegroundColor Cyan
$env:JAVA_HOME = "C:\Users\tommy\AppData\Local\Temp\reel-hangman-jdk21\jdk-21.0.12.1+1"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"

Write-Host "5. Gradle assembleDebug..." -ForegroundColor Cyan
Push-Location (Join-Path $root "android")
.\gradlew.bat assembleDebug
$gradleExit = $LASTEXITCODE
Pop-Location
if ($gradleExit -ne 0) {
    throw "Gradle build failed"
}

Write-Host "6. Copying APK to release..." -ForegroundColor Cyan
$releaseDir = Join-Path $root "release"
if (!(Test-Path $releaseDir)) {
    New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
}
$destFileName = Join-Path $releaseDir "ReelHangman-$newVersion-debug.apk"
Copy-Item "android\app\build\outputs\apk\debug\app-debug.apk" $destFileName -Force

Write-Host "==> BUILD SUCCESS: v$newVersion" -ForegroundColor Green
Write-Host "    $destFileName" -ForegroundColor Yellow

Write-Host "7. Installing to a connected Android device..." -ForegroundColor Cyan
$adb = Get-Command adb -ErrorAction SilentlyContinue
if ($adb) {
    $devices = (& adb devices) -join "`n"
    if ($devices -match "\tdevice") {
        adb install -r $destFileName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "==> Installed successfully." -ForegroundColor Green
        } else {
            Write-Warning "adb install failed. Install manually: $destFileName"
        }
    } else {
        Write-Warning "No Android device/emulator connected."
        Write-Host "APK is ready at: $destFileName" -ForegroundColor Yellow
    }
} else {
    Write-Warning "adb was not found. Install manually: $destFileName"
}
