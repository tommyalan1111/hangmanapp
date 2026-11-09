/**
 * AdMob and purchase configuration.
 *
 * Android production ad units are configured below. The Android app id is in
 * android/app/src/main/res/values/strings.xml. Dev builds load
 * .env.development (npm run build:dev), which forces test ads so they cannot
 * generate invalid traffic. Production builds load .env and must set
 * VITE_ADMOB_USE_TEST=false.
 *
 * To exercise live or mediation ad units on one device, add that device's
 * AdMob test device id to VITE_ADMOB_TESTING_DEVICES.
 *
 * iOS still uses Google's test app/ad unit ids until the iOS AdMob app and
 * units are created in Info.plist and the VITE_ADMOB_IOS_* variables.
 *
 * The non-consumable purchase id must also be created in Google Play Console
 * and App Store Connect.
 */
export const ADS_ENABLED = import.meta.env.VITE_ADS_ENABLED !== "false";

export const USE_TEST_ADS = import.meta.env.VITE_ADMOB_USE_TEST !== "false";

/**
 * Vite mode this bundle was built with: "development" for
 * `npm run build:dev`, "production" for `npm run build`.
 */
export const BUILD_MODE = import.meta.env.MODE;

/**
 * True for local/development APKs. Used only to expose the ad mode in the
 * settings screen and to warn in the logs; it never changes ad behaviour.
 */
export const IS_DEV_BUILD = BUILD_MODE !== "production";

/**
 * Physical devices registered with the Google Mobile Ads SDK as test
 * devices. Comma- or space-separated AdMob test device ids. Use it to load
 * live ad units on one device: Google demand then serves test ads instead of
 * billable impressions. Leave it empty for store builds.
 */
export const TEST_DEVICE_IDS: string[] = String(
  import.meta.env.VITE_ADMOB_TESTING_DEVICES ?? "",
)
  .split(/[\s,]+/)
  .map((id: string) => id.trim())
  .filter((id: string) => id.length > 0);

/**
 * Master switch for the bottom banner ad.
 * Set to false (or set VITE_BANNER_ENABLED=false) to disable the banner.
 */
export const BANNER_ENABLED = import.meta.env.VITE_BANNER_ENABLED !== "false";

const LIVE_REWARDED_ANDROID = "ca-app-pub-1345063149639557/4582294056";
const LIVE_INTERSTITIAL_ANDROID = "ca-app-pub-1345063149639557/4853756790";
const TEST_REWARDED_ANDROID = "ca-app-pub-3940256099942544/5224354917";
const TEST_INTERSTITIAL_ANDROID = "ca-app-pub-3940256099942544/1033173712";
const TEST_BANNER_ANDROID = "ca-app-pub-3940256099942544/6300978111";
const TEST_REWARDED_IOS = "ca-app-pub-3940256099942544/1712485313";
const TEST_INTERSTITIAL_IOS = "ca-app-pub-3940256099942544/4411468910";
const TEST_BANNER_IOS = "ca-app-pub-3940256099942544/2934735716";

export const AD_UNITS = {
  android: {
    // Use Google's test units explicitly in test mode. Relying on
    // isTesting + production IDs causes the plugin to prepare one ID
    // and try to show a different ID on unregistered devices.
    rewarded: USE_TEST_ADS
      ? TEST_REWARDED_ANDROID
      : (import.meta.env.VITE_ADMOB_ANDROID_REWARDED ?? LIVE_REWARDED_ANDROID),
    interstitial: USE_TEST_ADS
      ? TEST_INTERSTITIAL_ANDROID
      : (import.meta.env.VITE_ADMOB_ANDROID_INTERSTITIAL ?? LIVE_INTERSTITIAL_ANDROID),
    banner: USE_TEST_ADS
      ? TEST_BANNER_ANDROID
      : (import.meta.env.VITE_ADMOB_ANDROID_BANNER ?? TEST_BANNER_ANDROID),
  },
  ios: {
    rewarded: import.meta.env.VITE_ADMOB_IOS_REWARDED ?? TEST_REWARDED_IOS,
    interstitial: import.meta.env.VITE_ADMOB_IOS_INTERSTITIAL ?? TEST_INTERSTITIAL_IOS,
    banner: import.meta.env.VITE_ADMOB_IOS_BANNER ?? TEST_BANNER_IOS,
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
