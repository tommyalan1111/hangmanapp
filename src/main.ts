import "./styles.css";
import { hideSplash, isNative, setupNativeChrome } from "./core/platform";
import { ReelHangmanApp } from "./ui/app";

const root = document.getElementById("app");
if (root) {
  const app = new ReelHangmanApp(root);
  app.start();
  void setupNativeChrome(() => app.onNativeBack());
}

function revealWhenPainted(): void {
  const hold = isNative() ? 1100 : 380;
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      window.setTimeout(() => {
        document.documentElement.classList.add("app-ready");
        void hideSplash();
        const boot = document.getElementById("boot-screen");
        if (boot) {
          boot.classList.add("is-hidden");
          window.setTimeout(() => boot.remove(), 450);
        }
      }, hold);
    });
  });
}

if (document.readyState === "complete") {
  revealWhenPainted();
} else {
  window.addEventListener("load", revealWhenPainted, { once: true });
}

if (
  !isNative() &&
  "serviceWorker" in navigator &&
  import.meta.env.PROD &&
  location.protocol.startsWith("http")
) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => undefined);
  });
}
