import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const DEBUG_PORT = Number(process.env.CHROME_DEBUG_PORT || 9333);
const APP_URL = process.env.APP_URL || "http://127.0.0.1:4173/";
const OUT_DIR = path.join(process.cwd(), ".screens");
const SAVE_KEY = "reel-hangman-save-v1";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

class Cdp {
  constructor(socket) {
    this.socket = socket;
    this.nextId = 1;
    this.pending = new Map();
    this.events = new Map();
    this.consoleErrors = [];
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
      if (payload.method === "Runtime.exceptionThrown") {
        this.consoleErrors.push(payload.params.exceptionDetails?.text || "Unknown exception");
      }
      if (payload.method === "Runtime.consoleAPICalled" && payload.params.type === "error") {
        this.consoleErrors.push(
          payload.params.args.map((arg) => arg.value ?? arg.description ?? "").join(" "),
        );
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

  once(method, timeout = 5000) {
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
    if (result.exceptionDetails) {
      throw new Error(result.exceptionDetails.text || "Evaluation failed");
    }
    return result.result?.value;
  }

  async screenshot(filename) {
    const result = await this.send("Page.captureScreenshot", {
      format: "png",
      fromSurface: true,
      captureBeyondViewport: false,
    });
    await writeFile(path.join(OUT_DIR, filename), Buffer.from(result.data, "base64"));
    console.log(`  screenshot: ${filename}`);
  }

  close() {
    this.socket.close();
  }
}

async function connect() {
  const target = await fetch(
    `http://127.0.0.1:${DEBUG_PORT}/json/new?${encodeURIComponent("about:blank")}`,
    { method: "PUT" },
  ).then((response) => response.json());
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
  });
  return new Cdp(ws);
}

async function setViewport(cdp, width, height, scale = 2) {
  cdp.viewport = { width, height, scale };
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: scale,
    mobile: true,
    screenWidth: width,
    screenHeight: height,
  });
  await cdp.send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
}

async function navigate(cdp, url = APP_URL, wait = 700) {
  const loaded = cdp.once("Page.loadEventFired", 8000).catch(() => null);
  await cdp.send("Page.navigate", { url });
  await loaded;
  await sleep(wait);
  // Chrome can reset the compositor viewport on navigation, even though
  // window.innerWidth still reports the emulated size. Re-apply it after load.
  if (cdp.viewport) {
    await setViewport(cdp, cdp.viewport.width, cdp.viewport.height, cdp.viewport.scale);
    await sleep(350);
  }
}

function baseSave(overrides = {}) {
  return {
    version: 1,
    stats: { played: 0, won: 0, currentStreak: 0, bestStreak: 0, points: 0 },
    solvedIds: [],
    recentIds: [],
    history: [],
    settings: { sound: true, haptics: false, reduceMotion: false },
    activeRound: null,
    daily: null,
    ...overrides,
  };
}

async function setSave(cdp, save) {
  await cdp.evaluate(`localStorage.setItem(${JSON.stringify(SAVE_KEY)}, ${JSON.stringify(JSON.stringify(save))}); true`);
  await navigate(cdp);
}

async function click(cdp, selector) {
  await cdp.evaluate(`(() => { const el = document.querySelector(${JSON.stringify(selector)}); if (!el) throw new Error("Missing ${selector.replace(/"/g, '\\"')}"); el.click(); return true; })()`);
  await sleep(260);
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });
  const cdp = await connect();
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Page.addScriptToEvaluateOnNewDocument", {
    source:
      "if (navigator.serviceWorker) { navigator.serviceWorker.register = () => Promise.reject(new Error('Service worker disabled during visual checks')); }",
  });
  await setViewport(cdp, 390, 844);

  console.log("Home:");
  await navigate(cdp);
  await cdp.evaluate("localStorage.clear(); true");
  await navigate(cdp);
  const layout = await cdp.evaluate(`(() => {
    const frame = document.querySelector('.app-frame');
    return {
      innerWidth: window.innerWidth,
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      frameWidth: frame ? Math.round(frame.getBoundingClientRect().width) : null,
      frameHeight: frame ? Math.round(frame.getBoundingClientRect().height) : null,
      title: document.title,
      categories: document.querySelectorAll('.genre-card').length,
    };
  })()`);
  console.log(layout);
  await cdp.screenshot("home-390.png");

  console.log("Game:");
  await click(cdp, '[data-action="quick"]');
  const game = await cdp.evaluate(`(() => ({
    clue: document.querySelector('.clue-text')?.textContent,
    keys: document.querySelectorAll('.key').length,
    word: document.querySelector('.word-display')?.getAttribute('aria-label'),
    lives: document.querySelector('.lives-label')?.textContent,
    overflow: document.documentElement.scrollWidth - window.innerWidth,
    height: document.querySelector('.game-main')?.scrollHeight - document.querySelector('.game-main')?.clientHeight,
  }))()`);
  console.log(game);
  await cdp.screenshot("game-390.png");

  console.log("Win state:");
  const winGuesses = ["T", "H", "E", "G", "O", "D", "F", "A"];
  await setSave(
    cdp,
    baseSave({
      activeRound: {
        puzzleId: "movies-the-godfather",
        mode: "category",
        category: "movies",
        guessed: winGuesses,
        wrong: 2,
        hintsUsed: 0,
        status: "playing",
        startedAt: Date.now(),
        score: 0,
      },
    }),
  );
  await click(cdp, '[data-action="resume"]');
  await cdp.screenshot("game-near-win-390.png");
  await click(cdp, '[data-action="letter"][data-letter="R"]');
  await sleep(500);
  await cdp.screenshot("result-win-390.png");
  const win = await cdp.evaluate(`(() => ({
    heading: document.querySelector('.result-sheet h2')?.textContent,
    answer: document.querySelector('.result-answer')?.textContent,
    score: document.querySelector('.result-score')?.textContent?.replace(/\\s+/g, ' ').trim(),
    active: localStorage.getItem(${JSON.stringify(SAVE_KEY)})?.includes('"activeRound":null'),
    solved: document.querySelector('.streak-chip strong')?.textContent,
  }))()`);
  console.log(win);

  console.log("Stats:");
  await click(cdp, '[data-action="home"]');
  await click(cdp, '[data-action="nav"][data-screen="stats"]');
  await cdp.screenshot("stats-390.png");
  const stats = await cdp.evaluate(`(() => ({
    rate: document.querySelector('.ring-label strong')?.textContent,
    tiles: [...document.querySelectorAll('.stat-tile')].map((el) => el.textContent.replace(/\\s+/g, ' ').trim()),
    history: document.querySelectorAll('.history-row').length,
  }))()`);
  console.log(stats);

  console.log("Settings:");
  await click(cdp, '[data-action="nav"][data-screen="settings"]');
  await cdp.screenshot("settings-390.png");

  console.log("How to play:");
  await click(cdp, '[data-action="howto"]');
  await cdp.screenshot("howto-390.png");

  console.log("Mobile 320 x 568:");
  await setViewport(cdp, 320, 568, 2);
  await navigate(cdp);
  await cdp.screenshot("home-320.png");
  await click(cdp, '[data-action="quick"]');
  const small = await cdp.evaluate(`(() => ({
    overflowX: document.documentElement.scrollWidth - window.innerWidth,
    gameScroll: document.querySelector('.game-main')?.scrollHeight - document.querySelector('.game-main')?.clientHeight,
    keyHeight: Math.round(document.querySelector('.key')?.getBoundingClientRect().height || 0),
    wordWidth: Math.round(document.querySelector('.word-display')?.getBoundingClientRect().width || 0),
  }))()`);
  console.log(small);
  await cdp.screenshot("game-320.png");

  console.log("Desktop 1280 x 900:");
  await setViewport(cdp, 1280, 900, 1);
  await navigate(cdp);
  await cdp.screenshot("home-desktop.png");

  if (cdp.consoleErrors.length) {
    console.log("Console errors:", cdp.consoleErrors);
    process.exitCode = 1;
  } else {
    console.log("No console errors.");
  }
  cdp.close();
}

await main();
