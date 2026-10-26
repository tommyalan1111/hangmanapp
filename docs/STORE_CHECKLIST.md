# Store pre-flight checklist

## Identity

- [ ] Replace `com.reelhangman.game` with a bundle ID you control.
  - `capacitor.config.ts`
  - `android/app/build.gradle` (`applicationId`, `namespace`)
  - `android/app/src/main/java/com/reelhangman/game/MainActivity.java`
  - `ios/App/App.xcodeproj/project.pbxproj` (`PRODUCT_BUNDLE_IDENTIFIER`)
- [ ] Replace the placeholder support email in `docs/PRIVACY.md`.
- [ ] Set the developer/studio name in the store listing and copyright fields.
- [ ] Review the app name for trademark conflicts in your target countries.

## Android

- [ ] JDK 21 is installed and `JAVA_HOME` points to it.
- [ ] `android/local.properties` points at Android SDK 36.
- [ ] `npm run build && npx cap sync android`.
- [ ] Create a private release keystore outside the repo.
- [ ] Configure `signingConfigs.release` with secrets from environment variables or an ignored properties file.
- [ ] `./gradlew bundleRelease`.
- [ ] Test the signed release build on a physical device.
- [ ] Google Play target API requirement is met (currently target SDK 36).
- [ ] Upload an AAB, screenshots, feature graphic, short/full description, and privacy policy URL.
- [ ] Complete the Data safety form: no data collected, no data shared.
- [ ] Complete the content rating questionnaire. The game contains no violence, despite the hangman drawing.
- [ ] Verify the app installs and opens with airplane mode enabled.

## iOS

- [ ] Build on macOS with Xcode 16+.
- [ ] Set the development team and provisioning profile.
- [ ] Confirm the bundle ID matches App Store Connect.
- [ ] Test on a physical iPhone and at least one small-screen simulator.
- [ ] Confirm portrait-only behavior and safe areas on a notched device.
- [ ] Archive and upload to TestFlight.
- [ ] Provide the privacy policy URL and App Privacy answers ("Data Not Collected").
- [ ] Supply 6.7-inch and 6.1-inch screenshots. The files in `docs/screenshots/` are 780×1688 (390×844 logical), so render store-sized captures from a device or simulator.
- [ ] Add the support URL and marketing URL.
- [ ] Confirm `ITSAppUsesNonExemptEncryption` is false (no custom encryption).

## Content

- [ ] Run `npm run validate:data`; it must report zero errors.
- [ ] Spot-check new clues for accuracy and spoilers.
- [ ] Confirm no answer duplicates across categories unless intentional.
- [ ] Review the "behind the scenes" facts for the release date; they are written to be evergreen.
- [ ] Confirm the disclaimer in Settings and the README is acceptable for your listing.

## Accessibility and quality

- [ ] Test with TalkBack and VoiceOver.
- [ ] Test at 320×568 logical pixels and at a large system font size.
- [ ] Test with Reduced Motion enabled.
- [ ] Confirm sound and haptics toggles persist after restart.
- [ ] Confirm the Android hardware back button behaves correctly on home, game, result, and modal screens.
- [ ] Confirm the iOS swipe-back gesture does not break the single-page navigation.

## Release metadata

- Version: `1.0.0` (build `1`)
- Android minimum SDK: 24
- Android target/compile SDK: 36
- iOS deployment target: 15.0
- Orientation: portrait
- Category: Games / Word
- Offline: yes
