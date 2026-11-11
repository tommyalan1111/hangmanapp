# ==========================================
# Build the Reel Hangman DEVELOPMENT apk.
#
# - Uses .env.development (test ads by default), never the live units in .env.
# - Does not bump package.json / Android / iOS versions.
# - Writes to release\dev\ so it cannot be confused with a store build.
# - Production stays with build-apk.ps1 (or your Play release pipeline).
#
# Compatible with Windows PowerShell 5.1
#
#   .\build-apk-dev.ps1
#   .\build-apk-dev.ps1 -Install
# ==========================================

param(
    [switch]$Install
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$devEnv = Join-Path $root ".env.development"
if (!(Test-Path $devEnv)) {
    throw ".env.development not found. Dev builds must not fall back to the production env."
}

function Get-EnvValue([string]$name) {
    $pattern = "^\s*" + [regex]::Escape($name) + "\s*=\s*(.*)$"
    $line = Get-Content $devEnv | Where-Object { $_ -match $pattern } | Select-Object -First 1
    if (!$line) {
        return ""
    }
    return ([regex]::Match($line, $pattern)).Groups[1].Value.Trim()
}

$useTest = Get-EnvValue "VITE_ADMOB_USE_TEST"
$testDevices = Get-EnvValue "VITE_ADMOB_TESTING_DEVICES"
$devicesLabel = "none"
if ($testDevices) {
    $devicesLabel = $testDevices
}

Write-Host "==> DEV BUILD" -ForegroundColor Cyan
Write-Host "    env file     : .env.development"
Write-Host "    test ad units: $useTest"
Write-Host "    test devices : $devicesLabel"

if ($useTest -eq "false" -and !$testDevices) {
    Write-Warning "Live ad units with no registered test device. Add VITE_ADMOB_TESTING_DEVICES to .env.development, or AdMob will treat these impressions as real traffic."
}

$jdk = $env:JAVA_HOME
if (!$jdk -or !(Test-Path (Join-Path $jdk "bin\java.exe"))) {
    $jdk = "C:\Users\tommy\AppData\Local\Temp\reel-hangman-jdk21\jdk-21.0.12.1+1"
}
if (!(Test-Path (Join-Path $jdk "bin\java.exe"))) {
    throw "JDK 21 not found. Set JAVA_HOME before running this script."
}
$env:JAVA_HOME = $jdk
$env:Path = "$jdk\bin;$env:Path"

Write-Host "1. Building web app in development mode..." -ForegroundColor Cyan
npm run build:dev
if ($LASTEXITCODE -ne 0) {
    throw "Dev web build failed"
}

Write-Host "2. Syncing Capacitor Android..." -ForegroundColor Cyan
npx cap sync android
if ($LASTEXITCODE -ne 0) {
    throw "Capacitor sync failed"
}

Write-Host "3. Gradle assembleDebug..." -ForegroundColor Cyan
Push-Location (Join-Path $root "android")
.\gradlew.bat assembleDebug
$gradleExit = $LASTEXITCODE
Pop-Location
if ($gradleExit -ne 0) {
    throw "Gradle build failed"
}

Write-Host "4. Copying dev APK..." -ForegroundColor Cyan
$version = (node -p "require('./package.json').version").Trim()
$outDir = Join-Path $root "release\dev"
if (!(Test-Path $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}
$apk = Join-Path $outDir "ReelHangman-$version-dev.apk"
Copy-Item "android\app\build\outputs\apk\debug\app-debug.apk" $apk -Force

Write-Host "==> DEV BUILD SUCCESS" -ForegroundColor Green
Write-Host "    $apk" -ForegroundColor Yellow
Write-Host "    Verify in the app: Settings > Version ... dev build (test ads|live ads)" -ForegroundColor DarkGray

if ($Install) {
    Write-Host "5. Installing to a connected Android device..." -ForegroundColor Cyan
    $adb = Get-Command adb -ErrorAction SilentlyContinue
    if (!$adb) {
        Write-Warning "adb was not found. Install manually: $apk"
    } else {
        $devices = (& adb devices) -join "`n"
        if ($devices -match "\tdevice") {
            adb install -r $apk
            if ($LASTEXITCODE -eq 0) {
                Write-Host "==> Installed on device." -ForegroundColor Green
            } else {
                Write-Warning "adb install failed. A store build with a different signing key may be installed; uninstall it first, then retry."
            }
        } else {
            Write-Warning "No Android device/emulator connected. APK is ready at: $apk"
        }
    }
} else {
    Write-Host "Install with: adb install -r `"$apk`"" -ForegroundColor DarkGray
}

Write-Host "Reminder: dev web assets now sit in android/app/src/main/assets/public. A production build runs its own npm run build + cap sync before assembling." -ForegroundColor DarkYellow
