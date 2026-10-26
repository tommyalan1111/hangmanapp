# Reel Hangman

**An offline movie & TV hangman game for Android and iOS.**

Name the film, show, star, character, director, or famous screen family before the credits roll. No accounts, no ads, no signal required.

![Reel Hangman home screen](docs/screenshots/home.png)

## What is inside

- **397 hand-written puzzles** across seven categories:
  - Movies — 78
  - TV Series — 70
  - Actors — 53
  - Actresses — 59
  - Characters — 63
  - Directors — 44
  - Film Families — 30
- **A proper hangman round** with six takes, an animated gallows, large readable clues, on-screen and physical keyboards, and punctuation-friendly answers.
- **Replay on a miss** — when you run out of takes, the failed question stays on screen and **Replay this puzzle** resets the same board; the next question is never loaded automatically.
- **Clues and a "behind the scenes" fact** for every answer.
- **Daily Feature** — one date-seeded puzzle per day, worth double points.
- **One free hint per round** — reveals a useful missing letter and costs 40 points, never a take.
- **Progress that stays put** — solved puzzles, category completion, win rate, current and best streak, total points, recent history, and an in-progress round survive an app restart.
- **Accessible by design** — semantic buttons, focus rings, dialog focus trapping, a polite live region for game events, reduced-motion support, and keyboard controls.
- **Native-feeling details** — generated app icon and splash screen, status-bar styling, light haptics, synthesized sound effects, and the Android back button.
- **Truly offline** — all puzzles, artwork, audio, and code ship inside the app. The Android build has no internet permission at all.

| Game | Win screen |
| --- | --- |
| ![Game screen](docs/screenshots/game.png) | ![Win screen](docs/screenshots/result.png) |

| Stats | Settings |
| --- | --- |
| ![Stats screen](docs/screenshots/stats.png) | ![Settings screen](docs/screenshots/settings.png) |

## Play the Android build

A debug-signed, installable APK is included:

```text
release/ReelHangman-1.0.1-debug.apk
```

```bash
adb install -r release/ReelHangman-1.0.1-debug.apk
```

This is a **testing build**, not a Play Store upload. See [signing a release](#signing-for-the-stores) below.

The iOS project is complete in [`ios/`](ios/), but iOS builds require macOS and Xcode. There is no way to compile or codesign an iOS app on Windows.

## Quick start (web / PWA)

Requirements: Node.js 22+ and npm.

```bash
npm ci
npm run dev
```

Open the URL printed by Vite. For a production build:

```bash
npm run build
npm run preview
```

The production build also generates an offline service worker and precaches the app shell, so the web version can be installed as a PWA and opened offline after the first visit.

## Build Android

Requirements:

- JDK **21** (Capacitor 8 / Gradle 8.14 does not support JDK 25)
- Android SDK **platform 36** and **build tools 36**
- `ANDROID_HOME` or `ANDROID_SDK_ROOT` pointing at the SDK
- `android/local.properties` containing:
  ```properties
  sdk.dir=C:/Users/you/AppData/Local/Android/Sdk
  ```

```bash
npm run build
npx cap sync android
cd android
./gradlew assembleDebug
```

Windows:

```powershell
$env:JAVA_HOME = "C:\path\to\jdk-21"
cd android
.\gradlew.bat assembleDebug
```

The APK is written to `android/app/build/outputs/apk/debug/app-debug.apk`.

To open the native project in Android Studio:

```bash
npx cap open android
```

## Build iOS

Requirements: macOS, Xcode 16+, an Apple developer team, and a device or simulator.

```bash
npm ci
npm run build
npx cap sync ios
npx cap open ios
```

In Xcode:

1. Select the `App` target.
2. Choose your team under **Signing & Capabilities**.
3. Change the bundle identifier if `com.reelhangman.game` is already taken.
4. Select a simulator or device and run, or use **Product → Archive** for TestFlight.

Capacitor 8 uses Swift Package Manager for its iOS plugins, so CocoaPods is not required.

The iOS project is configured for iPhone, portrait orientation, iOS 15+, dark appearance, and a generated 1024×1024 app icon and launch image.

## Project layout

```text
reel-hangman/
├─ src/
│  ├─ data/              # 397 puzzles, split by category
│  ├─ core/game.ts       # pure game rules, scoring, daily seeding
│  ├─ core/storage.ts    # versioned localStorage persistence
│  ├─ core/audio.ts      # Web Audio sound synthesis (no audio files)
│  ├─ core/platform.ts   # Capacitor status bar, haptics, splash
│  ├─ ui/app.ts          # screens, rendering, input handling
│  ├─ ui/icons.ts        # inline SVG icon set
│  └─ styles.css         # cinematic mobile-first styling
├─ public/               # PWA manifest, icons, service-worker source dir
├─ resources/            # source icon and splash images
├─ scripts/              # content validation, PWA build, asset generation, browser tests
├─ android/              # Capacitor Android project
├─ ios/                  # Capacitor iOS project
├─ docs/                 # screenshots, store checklist, privacy policy
└─ release/              # installable APK
```

## Content and design

Puzzles live in `src/data/movies.ts`, `tv.ts`, `actors.ts`, `actresses.ts`, `characters.ts`, `directors.ts`, and `families.ts`.

```ts
movie(
  "THE GODFATHER",
  "Marlon Brando's don presides over a 1972 crime saga.",
  "It won Best Picture and earned Brando his second Oscar, which he refused in protest.",
  1, // 1 easy, 2 medium, 3 hard
);
```

Rules:

- Answers are uppercase letters and normal punctuation. Players only guess A–Z; spaces and punctuation are displayed automatically.
- Puzzle IDs are generated from the category and answer, so avoid duplicate answers unless you intentionally want two versions in different categories.
- Run `npm run validate:data` to check for duplicate IDs/answers, unsupported characters, short clues, and long answers.
- Keep clues useful but don't put the full answer in the clue.

The interface uses only system fonts and hand-authored CSS/SVG. There are no remote fonts, image packs, trackers, or runtime network calls.

## Testing

The repository includes two Chrome DevTools Protocol test scripts:

```bash
# With a preview server on http://127.0.0.1:4173 and headless Chrome
# started with --remote-debugging-port=9333:
node scripts/browser-check.mjs   # responsive screenshots + layout checks
node scripts/game-test.mjs       # gameplay, persistence, daily, reset, keyboard, 320px checks
```

`npm run validate:data` is also part of `npm run build`.

## Signing for the stores

### Android

Create a private keystore **outside this repository**:

```bash
keytool -genkeypair -v -keystore reel-hangman-release.jks \
  -alias reelhangman -keyalg RSA -keysize 2048 -validity 10000
```

Add a `signingConfigs.release` block to `android/app/build.gradle` using environment variables or a local `keystore.properties` file, then:

```bash
cd android
./gradlew bundleRelease
```

Upload `android/app/build/outputs/bundle/release/app-release.aab` to Google Play. Keep the keystore and passwords backed up; losing them prevents updates.

### iOS

Use Xcode **Product → Archive**, then distribute through the Organizer to TestFlight/App Store Connect. You need an App Store Connect app record and provisioning.

Before shipping, change `com.reelhangman.game` to a bundle ID you control in both `capacitor.config.ts` and the native projects, update the version, and replace the placeholder developer details in the privacy policy.

See [docs/STORE_CHECKLIST.md](docs/STORE_CHECKLIST.md) for a pre-flight list.

## Privacy

Reel Hangman collects nothing. Progress is stored only in local storage on the device. The Android manifest requests only `VIBRATE` (for haptics); it has no internet permission. See [docs/PRIVACY.md](docs/PRIVACY.md).

## License

Code is released under the MIT License. See [LICENSE](LICENSE).

Movie titles, series titles, characters, and people's names are used for trivia and identification. They remain the property of their respective owners. This is an independent fan-made game and is not affiliated with any studio, network, or streaming service.
