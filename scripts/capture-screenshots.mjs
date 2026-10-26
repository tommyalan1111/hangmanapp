import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const DEBUG_PORT = Number(process.env.CHROME_DEBUG_PORT || 9333);
const APP_URL = process.env.APP_URL || "http://127.0.0.1:4173/";
const OUT_DIR = path.join(process.cwd(), "docs", "screenshots");
const SAVE_KEY = "reel-hangman-save-v1";
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

class Cdp {
  constructor(socket) {
    this.socket = socket;
    this.nextId = 1;
    this.pending = new Map();
    this.events = new Map();
    socket.onmessage = (message) => {
      const payload = JSON.parse(message.data);
      if (payload.id) {
        const pending = this.pending.get(payload.id);
        if (!pending) return;
        this.pending.delete(payload.id);
        if (payload.error) pending.reject(new Error(payload.error.message));
        else pending.resolve(payload.result);
        return;
      }
      const listeners = this.events.get(payload.method) || [];
      for (const listener of listeners) listener(payload.params);
    };
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.nextId++;
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }

  once(method, timeout = 6000) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error(`Timed out waiting for ${method}`)), timeout);
      const listener = (params) => {
        clearTimeout(timer);
        const list = this.events.get(method) || [];
        this.events.set(
          method,
          list.filter((item) => item !== listener),
        );
        resolve(params);
      };
      const list = this.events.get(method) || [];
      list.push(listener);
      this.events.set(method, list);
    });
  }

  async evaluate(expression) {
    const result = await this.send("Runtime.evaluate", {
      expression,
      awaitPromise: true,
      returnByValue: true,
      userGesture: true,
    });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || "Evaluation failed");
    return result.result?.value;
  }
}

const target = await fetch(
  `http://127.0.0.1:${DEBUG_PORT}/json/new?${encodeURIComponent("about:blank")}`,
  { method: "PUT" },
).then((response) => response.json());
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.onopen = resolve;
  socket.onerror = reject;
});
const cdp = new Cdp(socket);

const viewport = { width: 390, height: 844, scale: 2 };

async function metrics() {
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: viewport.width,
    height: viewport.height,
    deviceScaleFactor: viewport.scale,
    mobile: true,
    screenWidth: viewport.width,
    screenHeight: viewport.height,
  });
  await cdp.send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
}

async function navigate() {
  const loaded = cdp.once("Page.loadEventFired", 8000).catch(() => null);
  await cdp.send("Page.navigate", { url: APP_URL });
  await loaded;
  await sleep(650);
  await metrics();
  await sleep(1200);
}

async function reload() {
  const loaded = cdp.once("Page.loadEventFired", 8000).catch(() => null);
  await cdp.send("Page.reload", { ignoreCache: true });
  await loaded;
  await sleep(650);
  await metrics();
  await sleep(1200);
}

async function click(selector) {
  await cdp.evaluate(`(() => {
    const el = document.querySelector(${JSON.stringify(selector)});
    if (!el) throw new Error("Missing " + ${JSON.stringify(selector)});
    el.click();
    return true;
  })()`);
  await sleep(420);
}

async function screenshot(name) {
  const result = await cdp.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  await writeFile(path.join(OUT_DIR, name), Buffer.from(result.data, "base64"));
  console.log(`  ${name}`);
}

function baseSave(overrides = {}) {
  return {
    version: 1,
    stats: { played: 0, won: 0, currentStreak: 0, bestStreak: 0, points: 0 },
    solvedIds: [],
    recentIds: [],
    history: [],
    settings: { sound: true, haptics: true, reduceMotion: false },
    activeRound: null,
    daily: null,
    ...overrides,
  };
}

async function setSave(data) {
  await cdp.evaluate(
    `localStorage.setItem(${JSON.stringify(SAVE_KEY)}, ${JSON.stringify(JSON.stringify(data))}); true`,
  );
  await navigate();
}

const history = [
  ["movies-the-godfather", "THE GODFATHER", "movies", true, 300, 0],
  ["tv-breaking-bad", "BREAKING BAD", "tv", true, 350, 1],
  ["actresses-meryl-streep", "MERYL STREEP", "actresses", true, 400, 2],
  ["characters-darth-vader", "DARTH VADER", "characters", false, 0, 3],
  ["directors-steven-spielberg", "STEVEN SPIELBERG", "directors", true, 325, 4],
  ["actors-tom-hanks", "TOM HANKS", "actors", true, 375, 5],
].map(([puzzleId, answer, category, won, score, daysAgo]) => ({
  puzzleId,
  answer,
  category,
  won,
  score,
  at: Date.now() - daysAgo * 86400000,
}));

const solvedIds = [
  "movies-the-godfather",
  "movies-casablanca",
  "movies-jaws",
  "movies-titanic",
  "movies-the-matrix",
  "movies-the-shawshank-redemption",
  "tv-friends",
  "tv-seinfeld",
  "tv-breaking-bad",
  "tv-the-sopranos",
  "actors-tom-hanks",
  "actresses-meryl-streep",
  "characters-darth-vader",
  "directors-steven-spielberg",
];

const activeRound = {
  puzzleId: "movies-the-godfather",
  mode: "category",
  category: "movies",
  guessed: ["T", "H", "E", "G", "D", "F", "A", "R"],
  wrong: 2,
  hintsUsed: 0,
  status: "playing",
  startedAt: Date.now(),
  score: 0,
};

await mkdir(OUT_DIR, { recursive: true });
await cdp.send("Page.enable");
await cdp.send("Runtime.enable");
await cdp.send("Page.addScriptToEvaluateOnNewDocument", {
  source:
    "if (navigator.serviceWorker) { navigator.serviceWorker.register = () => Promise.reject(new Error('SW disabled for screenshots')); }",
});
await metrics();
await navigate();
await cdp.evaluate("localStorage.clear(); true");
await reload();
await sleep(500);
await screenshot("home.png");

await setSave(
  baseSave({
    activeRound,
    stats: {
      played: 14,
      won: 10,
      currentStreak: 3,
      bestStreak: 6,
      points: 3820,
    },
  }),
);
await click('[data-action="resume"]');
await sleep(400);
await screenshot("game.png");
await click('[data-action="letter"][data-letter="O"]');
await sleep(900);
await screenshot("result.png");

await setSave(
  baseSave({
    stats: {
      played: 14,
      won: 10,
      currentStreak: 3,
      bestStreak: 6,
      points: 3820,
    },
    solvedIds,
    history,
    recentIds: solvedIds.slice(0, 8),
  }),
);
await click('[data-action="nav"][data-screen="stats"]');
await sleep(300);
await screenshot("stats.png");

await click('[data-action="nav"][data-screen="settings"]');
await sleep(300);
await screenshot("settings.png");

await click('[data-action="howto"]');
await sleep(300);
await screenshot("howto.png");

await setSave(baseSave());
await click('[data-action="daily"]');
await sleep(400);
await screenshot("daily.png");

socket.close();
console.log("Screenshots written to docs/screenshots.");

