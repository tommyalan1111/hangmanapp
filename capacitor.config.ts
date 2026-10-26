import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.reelhangman.game",
  appName: "Reel Hangman",
  webDir: "dist",
  backgroundColor: "#08090f",
  android: {
    allowMixedContent: false,
  },
  ios: {
    contentInset: "never",
    backgroundColor: "#08090f",
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 0,
      launchAutoHide: false,
      backgroundColor: "#08090f",
      androidSplashResourceName: "splash",
      androidScaleType: "CENTER_CROP",
      showSpinner: false,
      splashFullScreen: true,
      splashImmersive: true,
    },
    StatusBar: {
      style: "DARK",
      backgroundColor: "#08090f",
      overlaysWebView: false,
    },
  },
};

export default config;
