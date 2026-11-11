# Quy trình build AAB cho Google Play

Tài liệu này dùng cho app **Hangman Movie Trivia**.

- Package: `com.reelhangman.game`
- Project web: `E:\Work\Hangman app`
- Project Android: `E:\Work\Hangman app\android`
- AAB dùng để upload Google Play, **không phải APK debug**.

---

## 0. Checklist trước khi build

- [ ] Đã sửa xong code
- [ ] Nếu vừa chạy `build-apk-dev.ps1`: đã chạy lại `npm run build` + `npx cap sync android` (dev assets đang nằm trong `android/app/src/main/assets/public`)
- [ ] Đã cập nhật ngân hàng câu hỏi (nếu có)
- [ ] `npm run validate:data` chạy thành công
- [ ] `.env` đang là `VITE_ADMOB_USE_TEST=false`
- [ ] Có đúng file keystore
- [ ] Biết đúng alias
- [ ] Biết mật khẩu keystore và mật khẩu key
- [ ] `versionCode` cao hơn bản đã upload gần nhất
- [ ] Không upload file APK debug
- [ ] Không tạo keystore mới nếu chưa cần

Kiểm tra nhanh phiên bản hiện tại:

```powershell
cd "E:\Work\Hangman app"
Get-Content src\version.ts
Select-String -Path android\app\build.gradle -Pattern "versionCode|versionName"
```

---

## 1. Build web và sync sang Android

Luôn chạy trước khi build AAB:

```powershell
cd "E:\Work\Hangman app"
npm run build
npx cap sync android
```

Lệnh `npm run build` sẽ:

1. Validate dữ liệu câu hỏi
2. Typecheck TypeScript
3. Build Vite
4. Tạo service worker

Nếu bước này lỗi, **không build AAB**.

Kiểm tra nhanh dữ liệu:

```powershell
npm run validate:data
```

Kết quả mong đợi:

```text
Puzzle bank: 18593 entries
Puzzle bank is valid.
```

---

## 2. Tăng versionCode

Mỗi lần upload Play Store phải tăng `versionCode`.

Ví dụ hiện tại:

```text
versionName: 1.3.22
versionCode: 35
```

Bản tiếp theo:

```text
versionName: 1.3.23
versionCode: 36
```

Các file cần sửa:

```text
src/version.ts
package.json
android/app/build.gradle
ios/App/App.xcodeproj/project.pbxproj  (nếu build iOS)
```

Trong `android/app/build.gradle`:

```gradle
versionCode 36
versionName "1.3.23"
```

Trong `src/version.ts`:

```ts
export const APP_VERSION = "1.3.23";
```

Trong `package.json`:

```json
"version": "1.3.23"
```

> Không giảm `versionCode`.
> Nếu Play báo `versionCode already used`, tăng thêm 1 và build lại.

### Có tự tăng không?

- `.\build-apk.ps1`: **có**, tự tăng version và versionCode.
- `.\build-apk-dev.ps1`: **không** (chỉ build APK dev với test ads, không dùng cho AAB).
- Android Studio → **Generate Signed App Bundle**: **không tự tăng**.
- `npm run build`: **không tăng**.
- `npx cap sync android`: **không tăng**.

Vì vậy, nếu build AAB trực tiếp trong Android Studio, phải tự sửa `versionCode` trước. Nếu chạy `build-apk.ps1` thì script đã tăng sẵn, sau đó build AAB sẽ dùng số mới.

---

## 3. Mở đúng project Android Studio

Mở thư mục:

```text
E:\Work\Hangman app\android
```

**Không mở** `E:\Work\Hangman app`.

Nếu mở sai thư mục, mục **Generate App Bundles or APKs** sẽ bị xám.

Đợi **Gradle Sync** hoàn tất.

Nếu cần sync lại:

```text
File → Sync Project with Gradle Files
```

Kiểm tra module `app` đã được nhận.

---

## 4. Build AAB có chữ ký

Trong Android Studio:

```text
Build
→ Generate Signed App Bundle or APK...
```

Chọn:

```text
Android App Bundle
→ Module: app
→ Next
```

---

## 5. Chọn keystore

Chọn:

```text
Choose existing
```

Điền:

- Key store path: file `.jks` đúng
- Key alias: alias đúng
- Key store password
- Key password

**Không chọn Create new** trừ khi thực sự muốn tạo upload key mới.

Nếu vừa reset upload key, phải dùng keystore mới và chờ key có hiệu lực.

---

## 6. Chọn release

Ở bước cuối:

```text
Build Variants: release
```

Bấm:

```text
Next → Finish
```

Đợi build hoàn tất.

---

## 7. Lấy file AAB

File thường nằm ở:

```text
E:\Work\Hangman app\android\app\build\outputs\bundle\release\app-release.aab
```

Hoặc:

```text
E:\Work\Hangman app\android\app\release\app-release.aab
```

Kiểm tra file tồn tại:

```powershell
Get-Item "E:\Work\Hangman app\android\app\build\outputs\bundle\release\app-release.aab"
```

**Không upload file APK debug.**

---

## 8. Upload lên Closed testing

Vào Play Console:

```text
Test and release → Testing → Closed testing
→ Manage release → Create new release
```

Upload file `.aab`.

Điền release notes, ví dụ:

```text
1.3.23
- Updated question bank
- Stability improvements
- Minor bug fixes
```

Sau đó:

```text
Save → Review release → Start rollout to Closed testing
```

Không tạo track mới nếu đang trong 14 ngày closed testing.

---

## 9. Nhờ tester cập nhật

Gửi tester:

```text
Mở Play Store → Hangman Movie Trivia → Update
```

Kiểm tra trên máy tester:

```text
Settings → About
```

Phải thấy đúng version mới.

Nếu tester không thấy update:

1. Xóa cache Google Play Store
2. Mở lại Play Store
3. Vào trang app
4. Bấm Update
5. Đảm bảo đúng Gmail tester

---

## 10. Kiểm tra sau khi rollout

- [ ] App cài được từ Play
- [ ] Đúng version
- [ ] Banner ở Lobby
- [ ] Banner không che bottom tabs
- [ ] Rewarded hoạt động
- [ ] Interstitial sau khi thắng
- [ ] Remove Ads mua được
- [ ] Restore purchase hoạt động
- [ ] Offline vẫn chơi được
- [ ] Lưu tiến trình sau khi tắt app
- [ ] Màn 320px không vỡ layout

---

## 11. Lỗi thường gặp

### `Generate App Bundles or APKs` bị xám

- Đang mở sai thư mục
- Chưa Gradle sync
- Chưa nhận module `app`

Mở lại:

```text
E:\Work\Hangman app\android
```

rồi sync.

### `This release does not add or remove any app bundles`

- Chưa upload AAB
- Đang tạo release trống

Bấm **Add app bundle** hoặc promote từ Internal testing.

### `Version code already used`

- Tăng `versionCode` thêm 1
- Build AAB mới
- Upload lại

### `Upload certificate is not yet valid`

- Upload key vừa bị reset
- Chờ đến thời điểm Play Console báo
- Dùng đúng keystore mới

### `Wrong upload key`

- Chọn nhầm file `.jks`
- Sai alias
- Đang dùng key cũ sau khi reset

So sánh SHA-256:

```powershell
keytool -list -v -keystore "DUONG_DAN.jks" -alias ALIAS_THAT
```

với **Upload key certificate** trong Play Console.

### Không thấy alias

```powershell
keytool -list -v -keystore "DUONG_DAN.jks"
```

Tìm dòng:

```text
Alias name:
```

---

## 12. Bảo mật keystore

- Không đưa `.jks` vào Git
- Không ghi mật khẩu vào source
- Backup file `.jks`
- Backup alias
- Backup mật khẩu
- Lưu thêm một bản ngoài máy

Mất keystore có thể phải reset upload key và chờ Google xác nhận.

---

## 13. Quy trình ngắn gọn

```text
npm run build
npx cap sync android
→ tăng versionCode
→ mở Android Studio trong thư mục android
→ Build → Generate Signed App Bundle or APK
→ Android App Bundle → app → Next
→ chọn đúng keystore + alias
→ release → Finish
→ lấy app-release.aab
→ upload Closed testing
→ rollout
→ tester update
```
