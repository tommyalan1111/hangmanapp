/**
 * AdMob and purchase configuration.
 *
 * The defaults below are Google's official TEST ids, so the first builds can
 * be exercised without earning invalid traffic. Before publishing:
 *   1. Replace the AdMob app ids in:
 *        android/app/src/main/AndroidManifest.xml
 *        ios/App/App/Info.plist
 *   2. Set VITE_ADMOB_USE_TEST=false and provide real ad unit ids through
 *      VITE_ADMOB_ANDROID_REWARDED / VITE_ADMOB_ANDROID_INTERSTITIAL and their
 *      iOS equivalents.
 *   3. Create the non-consumable purchase with the product id below in Google
 *      Play Console and App Store Connect.
 */
export const ADS_ENABLED = import.meta.env.VITE_ADS_ENABLED !== "false";

export const USE_TEST_ADS = import.meta.env.VITE_ADMOB_USE_TEST !== "false";

const TEST_REWARDED_ANDROID = "ca-app-pub-3940256099942544/5224354917";
const TEST_INTERSTITIAL_ANDROID = "ca-app-pub-3940256099942544/1033173712";
const TEST_REWARDED_IOS = "ca-app-pub-3940256099942544/1712485313";
const TEST_INTERSTITIAL_IOS = "ca-app-pub-3940256099942544/4411468910";

export const AD_UNITS = {
  android: {
    rewarded: import.meta.env.VITE_ADMOB_ANDROID_REWARDED ?? TEST_REWARDED_ANDROID,
    interstitial: import.meta.env.VITE_ADMOB_ANDROID_INTERSTITIAL ?? TEST_INTERSTITIAL_ANDROID,
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
