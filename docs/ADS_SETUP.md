# Ads and Remove Ads setup

Reel Hangman uses three monetization pieces:

1. **Rewarded video** — optional free hint in the game screen.
2. **Capped interstitial** — only after a win, at most once every 3 completed rounds and 90 seconds.
3. **Remove Ads** — one-time non-consumable purchase that disables both ad formats.

Everything is wired through:

- `@capacitor-community/admob` for AdMob, UMP consent, and ATT.
- `@capgo/native-purchases` for Google Play Billing / StoreKit 2.
- `src/config/ads.ts` for IDs and caps.
- `src/core/ads.ts` for consent, ad loading, frequency caps, purchase/restore, and offline fallback.

Android's AdMob app ID and both ad unit IDs are configured. The debug build keeps `VITE_ADMOB_USE_TEST=true`, so it requests test ads and earns nothing. Set it to `false` only for a store release build. iOS still uses Google test IDs.

## 1. Create the AdMob apps and units

Android is already configured:

- App ID: `ca-app-pub-1345063149639557~8575837391`
- Rewarded: `Android_Rewarded_FreeHint`
- Interstitial: `Android_Interstitial_AfterWin`

For iOS, create one AdMob app and the two corresponding ad units, then replace the test IDs in three places:

### Android app ID

`android/app/src/main/res/values/strings.xml`

```xml
<string name="admob_app_id" translatable="false">ca-app-pub-1345063149639557~8575837391</string>
```

The manifest already reads it through `@string/admob_app_id`.

### iOS app ID

`ios/App/App/Info.plist`

```xml
<key>GADApplicationIdentifier</key>
<string>ca-app-pub-XXXXXXXX~YYYYYYYY</string>
```

### Ad unit IDs

Put production IDs in `.env` (or edit the fallbacks in `src/config/ads.ts`):

```bash
VITE_ADS_ENABLED=true
VITE_ADMOB_USE_TEST=false

VITE_ADMOB_ANDROID_REWARDED=ca-app-pub-XXXXXXXX/1111111111
VITE_ADMOB_ANDROID_INTERSTITIAL=ca-app-pub-XXXXXXXX/2222222222
VITE_ADMOB_IOS_REWARDED=ca-app-pub-XXXXXXXX/3333333333
VITE_ADMOB_IOS_INTERSTITIAL=ca-app-pub-XXXXXXXX/4444444444

VITE_REMOVE_ADS_PRODUCT_ID=com.reelhangman.game.removeads
```

`VITE_ADMOB_USE_TEST=false` also stops AdMob from being initialized in test mode.

## 2. Consent and privacy

### UMP

In AdMob → **Privacy & messaging**, create the messages for the regions you serve, including:

- GDPR message for the EEA/UK/Switzerland
- US states privacy message
- IDFA/ATT message for iOS where applicable

The app calls `requestConsentInfo()` and shows the consent form when required. If the player declines, `canRequestAds` is false and no ads load.

Where UMP reports that privacy options are required, **Settings → Ad privacy options** opens the Google privacy options form.

### iOS App Tracking Transparency

The app requests ATT after UMP consent on iOS. The usage description is in `Info.plist`. If permission is denied, requests are made with `npa: true` (non-personalized ads).

Add the SKAdNetwork identifiers recommended by AdMob for your campaigns. The project includes Google's `cstr6suwn9.skadnetwork`; add the rest from AdMob's iOS integration page if you run install campaigns.

## 3. Create the Remove Ads product

Use this product ID on both stores:

```text
com.reelhangman.game.removeads
```

### Google Play Console

1. Upload an AAB to a testing track first. Sideloaded debug APKs cannot query Play Billing products reliably.
2. Go to **Monetize → Products → In-app products**.
3. Create a **one-time product** with ID `com.reelhangman.game.removeads`.
4. Set the price and activate it.
5. Add test accounts under **License testing**.

### App Store Connect

1. Create the app record.
2. Go to **Monetization → In-App Purchases**.
3. Create a **Non-Consumable** product with ID `com.reelhangman.game.removeads`.
4. Add a localized display name, description, and price.
5. Submit it with a build for review.

### Xcode

The App target has the **In-App Purchase** capability marked in the project. If Xcode does not show it after opening, add it under **Signing & Capabilities → + Capability → In-App Purchase**.

### How the app handles purchases

- Product title and localized price are loaded from the store and shown before purchase.
- A successful purchase is stored locally and ads stop immediately.
- **Restore purchase** checks the store account and restores the entitlement on a new device.
- If the store product is not configured, the button reports that Remove Ads is unavailable instead of crashing.

## 4. Frequency caps

Configured in `src/config/ads.ts`:

```ts
export const INTERSTITIAL_MIN_ROUNDS = 3;
export const INTERSTITIAL_MIN_INTERVAL_MS = 90_000;
```

Interstitials only appear when the player taps **Next puzzle after a win**. They are skipped after losses, retries, and Daily Feature completion. The frequency state is stored in `localStorage`.

To make the game more conservative, raise `INTERSTITIAL_MIN_ROUNDS` or the interval. To remove interstitials entirely, leave `USE_TEST_ADS` false for development but remove the `maybeShowInterstitial` call in `src/ui/app.ts`.

## 5. Offline fallback

- Ad requests are started after the lobby renders, never before.
- Every ad call is wrapped in error handling and preparation has an 8-second timeout.
- If no ad is available, the next puzzle starts immediately or the rewarded button reports that no ad is available.
- The game, hints, stats, and replay all work without a connection.
- A purchased ad-free entitlement is cached locally so the player does not need a connection to keep ads off.

## 6. Test safely

**Android app ID:** `ca-app-pub-1345063149639557~8575837391`  
**Android rewarded:** `ca-app-pub-1345063149639557/4582294056`  
**Android interstitial:** `ca-app-pub-1345063149639557/4853756790`

`.env` currently has `VITE_ADMOB_USE_TEST=true`. The debug build requests test ads from those production units, so testing cannot generate invalid traffic.

Do **not** set `VITE_ADMOB_USE_TEST=false` and tap your own live ads. Use test mode until the release build is on a store testing track.

**iOS app ID:** still Google's test app ID until the iOS AdMob app is created.

### AdMob account approval

A new AdMob account can return:

```text
Account not approved yet
```

with error code `3`. When that happens, your ad units are configured correctly but Google will not serve ads yet. Complete the AdMob payments profile, identity verification, and tax information, then wait for account approval. This can take several days and is not an app bug.

### UMP forms

If no GDPR/US/IDFA message is published in AdMob, `requestConsentInfo()` fails with a “no form(s) configured” error. The debug build falls back to non-personalized test requests so the integration can still be checked. A release build disables ads rather than bypassing consent. Publish the UMP messages before release.

Test checklist:

- [ ] Rewarded button appears on the game screen on a native build.
- [ ] Watching a rewarded ad reveals a letter and does **not** change total points.
- [ ] Closing before the reward does not reveal a letter.
- [ ] After a win, **Next puzzle** may show an interstitial, but not on a loss or retry.
- [ ] Rounds 1–2 do not show an interstitial.
- [ ] Turning on airplane mode still lets every puzzle be played.
- [ ] The Remove Ads store sheet opens with a localized price after the product is configured.
- [ ] After purchase, the rewarded button and interstitials disappear.
- [ ] **Restore purchase** works after clearing app data.

## 7. Rebuild

```bash
npm run build
npx cap sync
```

Android:

```powershell
$env:JAVA_HOME = "C:\path\to\jdk-21"
cd android
.\gradlew.bat assembleDebug
```

iOS: open `ios/App/App.xcworkspace` or `App.xcodeproj` in Xcode and build on macOS.

## 8. Store disclosures

Before submitting, update:

- Google Play **Data safety**: advertising data, device identifiers, purchase history, and network access are involved.
- App Store **App Privacy**: declare advertising data and purchases; do not claim “Data Not Collected.”
- Privacy policy URL: host `docs/PRIVACY.md` on a public URL.
- Content rating and audience: do not select a child-directed audience unless you reconfigure AdMob and consent for families.
- Replace the placeholder support email.

The app is not configured for child-directed ads. Do not enable “Tag for child-directed treatment” unless you have reviewed the consequences for ad fill and store policy.
