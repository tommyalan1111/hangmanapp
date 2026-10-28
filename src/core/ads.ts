import { Capacitor } from "@capacitor/core";
import {
  AdMob,
  AdmobConsentStatus,
  MaxAdContentRating,
} from "@capacitor-community/admob";
import {
  NativePurchases,
  PURCHASE_TYPE,
  type Product,
  type Transaction,
} from "@capgo/native-purchases";
import {
  ADS_ENABLED,
  AD_LOAD_TIMEOUT_MS,
  AD_UNITS,
  INTERSTITIAL_MIN_INTERVAL_MS,
  INTERSTITIAL_MIN_ROUNDS,
  REMOVE_ADS_PRODUCT_ID,
  USE_TEST_ADS,
} from "../config/ads";

type Platform = "android" | "ios";

export type PurchaseResult = "purchased" | "cancelled" | "unavailable" | "error";

interface AdRuntimeState {
  lastInterstitialAt: number;
  lastInterstitialRound: number;
}

interface AdsCallbacks {
  onEntitlementChange?: (removeAds: boolean) => void;
  onCatalogChange?: () => void;
}

const AD_STATE_KEY = "reel-hangman-ad-state-v1";

function readRuntimeState(): AdRuntimeState {
  try {
    const raw = localStorage.getItem(AD_STATE_KEY);
    if (!raw) return { lastInterstitialAt: 0, lastInterstitialRound: 0 };
    const parsed = JSON.parse(raw) as Partial<AdRuntimeState>;
    return {
      lastInterstitialAt:
        typeof parsed.lastInterstitialAt === "number" ? parsed.lastInterstitialAt : 0,
      lastInterstitialRound:
        typeof parsed.lastInterstitialRound === "number" ? parsed.lastInterstitialRound : 0,
    };
  } catch {
    return { lastInterstitialAt: 0, lastInterstitialRound: 0 };
  }
}

function writeRuntimeState(state: AdRuntimeState): void {
  try {
    localStorage.setItem(AD_STATE_KEY, JSON.stringify(state));
  } catch {
    // Ads are optional; a storage failure must not affect gameplay.
  }
}

function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timer = window.setTimeout(() => reject(new Error("Ad load timed out")), timeoutMs);
    promise.then(
      (value) => {
        window.clearTimeout(timer);
        resolve(value);
      },
      (error) => {
        window.clearTimeout(timer);
        reject(error);
      },
    );
  });
}

function errorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  if (error && typeof error === "object" && "message" in error) {
    return String((error as { message?: unknown }).message ?? "");
  }
  return "";
}

/**
 * AdMob + one-time "Remove Ads" purchase.
 *
 * All methods are safe to call on the web: they turn into no-ops. Native ad
 * failures are swallowed so the game can always continue.
 */
class AdsService {
  private readonly platform = Capacitor.getPlatform();
  private readonly supported =
    ADS_ENABLED && (this.platform === "android" || this.platform === "ios");

  private callbacks: AdsCallbacks = {};
  private initialized = false;
  private initializing = false;
  private consentReady = false;
  private canRequestAds = false;
  private privacyOptionsRequired = false;
  private consentFallback = false;
  private removeAds = false;
  private trackingAuthorized = false;

  private rewardedReady = false;
  private interstitialReady = false;
  private rewardedPreparePromise: Promise<void> | null = null;
  private interstitialPreparePromise: Promise<void> | null = null;
  private showingRewarded = false;
  private showingInterstitial = false;
  private purchasing = false;

  private product: Product | null = null;

  setCallbacks(callbacks: AdsCallbacks): void {
    this.callbacks = callbacks;
  }

  isSupported(): boolean {
    return this.supported;
  }

  isRemoved(): boolean {
    return this.removeAds;
  }

  canShowAds(): boolean {
    return this.supported && this.consentReady && this.canRequestAds && !this.removeAds;
  }

  privacyOptionsAvailable(): boolean {
    return this.supported && this.privacyOptionsRequired;
  }

  setRemoveAds(value: boolean): void {
    if (this.removeAds === value) return;
    this.removeAds = value;
    if (value) {
      this.rewardedReady = false;
      this.interstitialReady = false;
    }
    this.callbacks.onEntitlementChange?.(value);
  }

  getRemoveAdsProduct(): Product | null {
    return this.product;
  }

  getRemoveAdsPrice(): string | null {
    return this.product?.priceString ?? null;
  }

  getRemoveAdsTitle(): string {
    return this.product?.title ?? "Remove ads";
  }

  async initialize(alreadyOwned: boolean): Promise<void> {
    if (!this.supported || this.initialized || this.initializing) return;
    this.initializing = true;
    this.removeAds = alreadyOwned;

    try {
      if (this.removeAds) return;

      // Restore entitlements silently before asking for consent/ads. A player
      // who already purchased ad removal must never see a consent prompt.
      await this.restoreEntitlementSilently();
      if (this.removeAds) return;

      let info: Awaited<ReturnType<typeof AdMob.requestConsentInfo>> | null = null;
      try {
        info = await AdMob.requestConsentInfo();
        if (
          info.isConsentFormAvailable &&
          info.status === AdmobConsentStatus.REQUIRED
        ) {
          info = await AdMob.showConsentForm();
        }
      } catch {
        // A brand-new AdMob app can throw here until a UMP message is
        // published. In production that is a configuration error: do not
        // bypass consent. In test mode, continue with non-personalized ads so
        // the integration can still be exercised.
        if (!USE_TEST_ADS) throw new Error("UMP consent form is not configured");
        this.consentFallback = true;
        this.consentReady = true;
        this.canRequestAds = true;
        this.privacyOptionsRequired = false;
      }

      if (info) {
        this.consentReady = true;
        this.canRequestAds = info.canRequestAds;
        this.privacyOptionsRequired =
          String(info.privacyOptionsRequirementStatus) === "REQUIRED";
      }

      if (!this.canRequestAds) return;

      await AdMob.initialize({
        initializeForTesting: false,
        maxAdContentRating: MaxAdContentRating.General,
      });

      await this.ensureTrackingAuthorization();
      await this.refreshProduct();
      await Promise.all([this.prepareRewarded(), this.prepareInterstitial()]);
    } catch {
      // No ads is a valid state: the game remains fully playable.
      this.canRequestAds = false;
    } finally {
      this.initializing = false;
      this.initialized = true;
    }
  }

  async showRewarded(): Promise<boolean> {
    if (!this.canShowAds() || this.showingRewarded) return false;

    if (!this.rewardedReady) {
      await this.prepareRewarded();
    }
    if (!this.rewardedReady) return false;

    this.showingRewarded = true;
    try {
      for (let attempt = 0; attempt < 2; attempt += 1) {
        try {
          const reward = await AdMob.showRewardVideoAd({ adId: this.adUnit("rewarded") });
          this.rewardedReady = false;
          void this.prepareRewarded();
          return Boolean(reward && reward.amount > 0);
        } catch (error) {
          // The SDK may invalidate a previously prepared ad. Clear the stale
          // flag, then prepare once and retry. Do not retry a normal dismissal.
          this.rewardedReady = false;
          const retryable = /not prepared|can be shown|not loaded/i.test(errorMessage(error));
          if (!retryable || attempt === 1) {
            void this.prepareRewarded();
            return false;
          }
          await this.prepareRewarded();
          if (!this.rewardedReady) return false;
        }
      }
      return false;
    } finally {
      this.showingRewarded = false;
    }
  }

  /**
   * Shows an interstitial only after a win, no more than once per
   * INTERSTITIAL_MIN_ROUNDS completed rounds and once per 90 seconds.
   */
  async maybeShowInterstitial(completedRounds: number): Promise<boolean> {
    if (!this.canShowAds() || this.showingInterstitial) return false;
    if (completedRounds < INTERSTITIAL_MIN_ROUNDS) return false;

    const state = readRuntimeState();
    if (
      state.lastInterstitialRound > 0 &&
      completedRounds - state.lastInterstitialRound < INTERSTITIAL_MIN_ROUNDS
    ) {
      return false;
    }
    if (Date.now() - state.lastInterstitialAt < INTERSTITIAL_MIN_INTERVAL_MS) {
      return false;
    }

    if (!this.interstitialReady) {
      void this.prepareInterstitial();
      return false;
    }

    this.showingInterstitial = true;
    try {
      await AdMob.showInterstitial({ adId: this.adUnit("interstitial") });
      const nextState: AdRuntimeState = {
        lastInterstitialAt: Date.now(),
        lastInterstitialRound: completedRounds,
      };
      writeRuntimeState(nextState);
      this.interstitialReady = false;
      void this.prepareInterstitial();
      return true;
    } catch {
      this.interstitialReady = false;
      void this.prepareInterstitial();
      return false;
    } finally {
      this.showingInterstitial = false;
    }
  }

  async purchaseRemoveAds(): Promise<PurchaseResult> {
    if (!this.supported || this.purchasing) return "unavailable";
    this.purchasing = true;
    try {
      await this.refreshProduct();
      if (!this.product) return "unavailable";

      await NativePurchases.purchaseProduct({
        productIdentifier: REMOVE_ADS_PRODUCT_ID,
        productType: PURCHASE_TYPE.INAPP,
        isConsumable: false,
        quantity: 1,
        autoAcknowledgePurchases: true,
      });
      this.setRemoveAds(true);
      return "purchased";
    } catch (error) {
      const message = errorMessage(error);
      if (/cancel|dismiss|abort/i.test(message)) return "cancelled";
      return "error";
    } finally {
      this.purchasing = false;
    }
  }

  async restoreRemoveAds(): Promise<boolean> {
    if (!this.supported) return false;
    try {
      await NativePurchases.restorePurchases();
    } catch {
      // Android has no separate restore call; getPurchases is the source of truth.
    }

    const owned = await this.hasRemoveAdsPurchase();
    if (owned) this.setRemoveAds(true);
    return owned;
  }

  resetFrequencyCaps(): void {
    writeRuntimeState({ lastInterstitialAt: 0, lastInterstitialRound: 0 });
  }

  async showPrivacyOptions(): Promise<boolean> {
    if (!this.supported) return false;
    try {
      await AdMob.showPrivacyOptionsForm();
      return true;
    } catch {
      return false;
    }
  }

  private adUnit(kind: "rewarded" | "interstitial"): string {
    const platform: Platform = this.platform === "ios" ? "ios" : "android";
    return AD_UNITS[platform][kind];
  }

  private isNonPersonalized(): boolean {
    return this.consentFallback || (this.platform === "ios" && !this.trackingAuthorized);
  }

  private async ensureTrackingAuthorization(): Promise<void> {
    if (this.platform !== "ios") {
      this.trackingAuthorized = true;
      return;
    }

    try {
      let status = await AdMob.trackingAuthorizationStatus();
      if (status.status === "notDetermined") {
        await AdMob.requestTrackingAuthorization();
        status = await AdMob.trackingAuthorizationStatus();
      }
      this.trackingAuthorized = status.status === "authorized";
    } catch {
      this.trackingAuthorized = false;
    }
  }

  private async prepareRewarded(): Promise<void> {
    if (!this.canRequestAds || this.removeAds || this.rewardedReady) {
      return;
    }
    if (this.rewardedPreparePromise) return this.rewardedPreparePromise;

    const promise = (async () => {
      try {
        await withTimeout(
          AdMob.prepareRewardVideoAd({
            adId: this.adUnit("rewarded"),
            isTesting: false,
            npa: this.isNonPersonalized(),
          }),
          AD_LOAD_TIMEOUT_MS,
        );
        this.rewardedReady = true;
      } catch {
        this.rewardedReady = false;
      }
    })();

    this.rewardedPreparePromise = promise;
    try {
      await promise;
    } finally {
      if (this.rewardedPreparePromise === promise) {
        this.rewardedPreparePromise = null;
      }
    }
  }

  private async prepareInterstitial(): Promise<void> {
    if (!this.canRequestAds || this.removeAds || this.interstitialReady) {
      return;
    }
    if (this.interstitialPreparePromise) return this.interstitialPreparePromise;

    const promise = (async () => {
      try {
        await withTimeout(
          AdMob.prepareInterstitial({
            adId: this.adUnit("interstitial"),
            isTesting: false,
            npa: this.isNonPersonalized(),
          }),
          AD_LOAD_TIMEOUT_MS,
        );
        this.interstitialReady = true;
      } catch {
        this.interstitialReady = false;
      }
    })();

    this.interstitialPreparePromise = promise;
    try {
      await promise;
    } finally {
      if (this.interstitialPreparePromise === promise) {
        this.interstitialPreparePromise = null;
      }
    }
  }

  private async refreshProduct(): Promise<void> {
    if (!this.supported || this.removeAds) return;
    try {
      const { products } = await NativePurchases.getProducts({
        productIdentifiers: [REMOVE_ADS_PRODUCT_ID],
        productType: PURCHASE_TYPE.INAPP,
      });
      this.product = products[0] ?? null;
      this.callbacks.onCatalogChange?.();
    } catch {
      this.product = null;
      this.callbacks.onCatalogChange?.();
    }
  }

  private async restoreEntitlementSilently(): Promise<void> {
    const owned = await this.hasRemoveAdsPurchase();
    if (owned) this.setRemoveAds(true);
  }

  private async hasRemoveAdsPurchase(): Promise<boolean> {
    try {
      const { purchases } = await NativePurchases.getPurchases({
        productType: PURCHASE_TYPE.INAPP,
      });
      return purchases.some((purchase: Transaction) => {
        if (purchase.productIdentifier !== REMOVE_ADS_PRODUCT_ID) return false;
        if (purchase.purchaseState && purchase.purchaseState !== "1") return false;
        return purchase.isActive !== false;
      });
    } catch {
      return false;
    }
  }
}

export const ads = new AdsService();
