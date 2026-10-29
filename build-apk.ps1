# ==========================================
# Script tự động tăng Version, Build APK & Cài vào Máy ảo Android
# ==========================================

Write-Host "1. Đọc và tự động tăng version trong package.json..." -ForegroundColor Cyan
$packageJsonPath = "package.json"
$packageJsonText = Get-Content -Path $packageJsonPath -Raw

# Dùng RegEx để tìm và trích xuất version hiện tại (chuẩn Semantic Versioning X.Y.Z)
if ($packageJsonText -match '"version":\s*"(\d+)\.(\d+)\.(\d+)"') {
    $major = $Matches[1]
    $minor = $Matches[2]
    [int]$patch = $Matches[3]
    
    $oldVersion = "$major.$minor.$patch"
    # Tăng số cuối lên 1
    $patch++
    $newVersion = "$major.$minor.$patch"

    Write-Host "   Version cũ: v$oldVersion" -ForegroundColor Yellow
    Write-Host "   Version mới: v$newVersion" -ForegroundColor Green

    # Thay thế version cũ bằng version mới trong file package.json
    $updatedJsonText = $packageJsonText -replace '"version":\s*"[^"]+"', "`"version`": `"$newVersion`""
    Set-Content -Path $packageJsonPath -Value $updatedJsonText -Encoding utf8
} else {
    Write-Error "Không tìm thấy định dạng version hợp lệ trong package.json!"
    exit 1
}

Write-Host "2. Bắt đầu build ứng dụng web..." -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) { Write-Error "Build web thất bại!"; exit $LASTEXITCODE }

Write-Host "3. Đồng bộ Capacitor sang Android..." -ForegroundColor Cyan
npx cap sync android
if ($LASTEXITCODE -ne 0) { Write-Error "Capacitor sync thất bại!"; exit $LASTEXITCODE }

Write-Host "4. Cấu hình môi trường Java (JDK 21)..." -ForegroundColor Cyan
$env:JAVA_HOME = "C:\Users\tommy\AppData\Local\Temp\reel-hangman-jdk21\jdk-21.0.12.1+1"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"

Write-Host "5. Tiến hành Gradle build APK (Debug)..." -ForegroundColor Cyan
Set-Location "E:\Work\Hangman app\android"
.\gradlew.bat assembleDebug
if ($LASTEXITCODE -ne 0) { Write-Error "Gradle build thất bại!"; exit $LASTEXITCODE }

Write-Host "6. Copy file APK ra thư mục release với version mới..." -ForegroundColor Cyan
Set-Location "E:\Work\Hangman app"
if (!(Test-Path "release")) {
    New-Item -ItemType Directory -Force -Path "release" | Out-Null
}

$destFileName = "release\ReelHangman-$newVersion-debug.apk"
Copy-Item "android\app\build\outputs\apk\debug\app-debug.apk" $destFileName -Force

Write-Host "==> BUILD APK THÀNH CÔNG VỚI VERSION v$newVersion!" -ForegroundColor Green

Write-Host "7. Tự động cài đặt file APK vào máy ảo Android..." -ForegroundColor Cyan
# Kiểm tra xem có thiết bị/máy ảo nào đang kết nối không bằng adb devices
$adbDevices = adb devices
if ($adbDevices -match "device\s*$") {
    Write-Host "Đang cài đặt phiên bản v$newVersion lên máy ảo..." -ForegroundColor Yellow
    # Sử dụng cờ -r để cài đè (re-install) lên bản cũ mà không mất dữ liệu
    adb install -r $destFileName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "==> CÀI ĐẶT VÀO MÁY ẢO THÀNH CÔNG! Bạn có thể mở app lên test ngay." -ForegroundColor Green
    } else {
        Write-Warning "Cài đặt thất bại qua adb. Bạn có thể tự cài file thủ công tại: $destFileName"
    }
} else {
    Write-Warning "Không tìm thấy máy ảo hoặc thiết bị Android nào đang chạy/kết nối!"
    Write-Host "File APK đã sẵn sàng tại: $destFileName" -ForegroundColor Yellow
}