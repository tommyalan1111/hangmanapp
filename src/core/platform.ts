import { Capacitor } from "@capacitor/core";
import { Haptics, ImpactStyle, NotificationType } from "@capacitor/haptics";
import { SplashScreen } from "@capacitor/splash-screen";
import { StatusBar, Style } from "@capacitor/status-bar";

export type HapticKind = "light" | "medium" | "success" | "error";

export function isNative(): boolean {
  return Capacitor.isNativePlatform();
}

export async function haptic(kind: HapticKind, enabled: boolean): Promise<void> {
  if (!enabled) return;
  try {
    if (isNative()) {
      if (kind === "success") {
        await Haptics.notification({ type: NotificationType.Success });
      } else if (kind === "error") {
        await Haptics.notification({ type: NotificationType.Error });
      } else {
        await Haptics.impact({
          style: kind === "medium" ? ImpactStyle.Medium : ImpactStyle.Light,
        });
      }
      return;
    }
    if ("vibrate" in navigator) {
      navigator.vibrate(
        kind === "success" ? [18, 40, 18] : kind === "error" ? [40, 30, 40] : kind === "medium" ? 18 : 10,
      );
    }
  } catch {
    // Haptics are a bonus, never a requirement for play.
  }
}

export async function setupNativeChrome(onBack: () => void): Promise<void> {
  if (!isNative()) return;
  try {
    await StatusBar.setStyle({ style: Style.Dark });
    await StatusBar.setBackgroundColor({ color: "#08090f" });
  } catch {
    // Some platforms do not allow every status-bar option.
  }

  try {
    const { App } = await import("@capacitor/app");
    await App.addListener("backButton", () => onBack());
  } catch {
    // The web build has no native back button.
  }
}

export async function hideSplash(): Promise<void> {
  if (!isNative()) return;
  try {
    await SplashScreen.hide();
  } catch {
    // The splash may already be hidden by the native configuration.
  }
}
