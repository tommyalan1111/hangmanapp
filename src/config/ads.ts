/**
 * AdMob and purchase configuration.
 *
 * Android production ad units are configured below. The Android app id is in
 * android/app/src/main/res/values/strings.xml. The debug build keeps
 * VITE_ADMOB_USE_TEST=true by default, so it requests test ads and cannot
 * generate invalid traffic. For a release build set VITE_ADMOB_USE_TEST=false.
 *
 * iOS still uses Google's test app/ad unit ids until the iOS AdMob app and
 * units are created in Info.plist and the VITE_ADMOB_IOS_* variables.
 *
 * The non-consumable purchase id must also be created in Google Play Console
 * and App Store Connect.
 */
export const ADS_ENABLED = import.meta.env.VITE_ADS_ENABLED !== "false";

export const USE_TEST_ADS = import.meta.env.VITE_ADMOB_USE_TEST !== "false";

const LIVE_REWARDED_ANDROID = "ca-app-pub-1345063149639557/4582294056";
const LIVE_INTERSTITIAL_ANDROID = "ca-app-pub-1345063149639557/4853756790";
const TEST_REWARDED_IOS = "ca-app-pub-3940256099942544/1712485313";
const TEST_INTERSTITIAL_IOS = "ca-app-pub-3940256099942544/4411468910";

export const AD_UNITS = {
  android: {
    rewarded: import.meta.env.VITE_ADMOB_ANDROID_REWARDED ?? LIVE_REWARDED_ANDROID,
    interstitial: import.meta.env.VITE_ADMOB_ANDROID_INTERSTITIAL ?? LIVE_INTERSTITIAL_ANDROID,
  },
  ios: {
    rewarded: import.meta.env.VITE_ADMOB_IOS_REWARDED ?? TEST_REWARDED_IOS,
    interstitial: import.meta.env.VITE_ADMOB_IOS_INTERSTITIAL ?? TEST_INTERSTITIAL_IOS,
  },
} as const;

export const REMOVE_ADS_PRODUCT_ID =
  import.meta.env.VITE_REMOVE_ADS_PRODUCT_ID ?? "com.reelhangman.game.removeads";

/** Show an interstitial only after this many finished rounds. */
export const INTERSTITIAL_MIN_ROUNDS = 3;

/** Never show two interstitials closer together than this. */
export const INTERSTITIAL_MIN_INTERVAL_MS = 90_000;

/** Max time to wait for the native ad SDK to hand back an ad. */
export const AD_LOAD_TIMEOUT_MS = 8_000;
