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
    this.viewport = null;
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

const cdp = await (async () => {
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
})();

const failures = [];
function check(name, condition, details = "") {
  if (condition) {
    console.log(`  PASS ${name}`);
  } else {
    console.log(`  FAIL ${name}${details ? ` — ${details}` : ""}`);
    failures.push(name);
  }
}

async function viewport(width, height) {
  cdp.viewport = { width, height };
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 2,
    mobile: true,
    screenWidth: width,
    screenHeight: height,
  });
  await cdp.send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
}

async function navigate(wait = 700) {
  const loaded = cdp.once("Page.loadEventFired", 8000).catch(() => null);
  await cdp.send("Page.navigate", { url: APP_URL });
  await loaded;
  await sleep(wait);
  if (cdp.viewport) {
    await viewport(cdp.viewport.width, cdp.viewport.height);
    await sleep(300);
  }
}

async function reload() {
  const loaded = cdp.once("Page.loadEventFired", 8000).catch(() => null);
  await cdp.send("Page.reload", { ignoreCache: true });
  await loaded;
  await sleep(600);
  if (cdp.viewport) {
    await viewport(cdp.viewport.width, cdp.viewport.height);
    await sleep(300);
  }
}

async function click(selector) {
  await cdp.evaluate(`(() => {
    const el = document.querySelector(${JSON.stringify(selector)});
    if (!el) throw new Error("Missing " + ${JSON.stringify(selector)});
    el.click();
    return true;
  })()`);
  await sleep(300);
}

async function screenshot(name) {
  const result = await cdp.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  await writeFile(path.join(OUT_DIR, name), Buffer.from(result.data, "base64"));
  console.log(`  screenshot: ${name}`);
}

function save(overrides = {}) {
  return {
    version: 1,
    stats: { played: 0, won: 0, currentStreak: 0, bestStreak: 0, points: 0 },
    solvedIds: [],
    recentIds: [],
    history: [],
    settings: { sound: false, haptics: false, reduceMotion: true },
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

const round = (puzzleId, category, mode, guessed, wrong = 0, hintsUsed = 0) => ({
  puzzleId,
  mode,
  category,
  guessed,
  wrong,
  hintsUsed,
  status: "playing",
  startedAt: Date.now(),
  score: 0,
});

async function main() {
  await mkdir(OUT_DIR, { recursive: true });
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Page.addScriptToEvaluateOnNewDocument", {
    source:
      "if (navigator.serviceWorker) { navigator.serviceWorker.register = () => Promise.reject(new Error('SW disabled in tests')); }",
  });
  await viewport(390, 844);
  await navigate();
  await cdp.evaluate("localStorage.clear(); true");
  await reload();

  console.log("Home");
  const home = await cdp.evaluate(`({
    categories: document.querySelectorAll('.genre-card').length,
    daily: !!document.querySelector('.daily-card'),
    overflow: document.documentElement.scrollWidth - window.innerWidth,
    width: Math.round(document.querySelector('.app-frame').getBoundingClientRect().width)
  })`);
  check("7 categories render", home.categories === 7, JSON.stringify(home));
  check("home has no horizontal overflow", home.overflow === 0, `overflow ${home.overflow}`);
  check("home is 390 CSS px wide", home.width === 390, `width ${home.width}`);

  console.log("Category + persistence");
  await click('[data-action="category"][data-category="movies"]');
  const started = await cdp.evaluate(`({
    mode: document.querySelector('.game-mode')?.textContent,
    category: document.querySelector('.game-category')?.textContent,
    active: JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}))?.activeRound?.puzzleId
  })`);
  check("category round starts", started.mode === "CATEGORY ROUND" && started.category === "Movies");
  check("active round is persisted", Boolean(started.active), JSON.stringify(started));
  const clueSize = await cdp.evaluate(
    `parseFloat(getComputedStyle(document.querySelector('.clue-text')).fontSize)`,
  );
  check("clue text is easy to read", clueSize >= 16, `clue font-size ${clueSize}px`);
  await cdp.evaluate(`document.querySelector('[data-action="letter"][data-letter="Z"]')?.click(); true`);
  await sleep(350);
  await reload();
  const resumedHome = await cdp.evaluate(`({
    continueButton: !!document.querySelector('[data-action="resume"]'),
    copy: document.querySelector('[data-action="resume"]')?.textContent?.replace(/\\s+/g, ' ').trim()
  })`);
  check("home offers resume after reload", resumedHome.continueButton, JSON.stringify(resumedHome));
  await click('[data-action="resume"]');
  const resumed = await cdp.evaluate(`({
    screen: document.querySelector('.app-frame')?.dataset.screen,
    guessed: JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}))?.activeRound?.guessed
  })`);
  check("resume restores the same round", resumed.screen === "game" && resumed.guessed.includes("Z"));

  console.log("Punctuation and win");
  await setSave(
    save({
      activeRound: round(
        "movies-pan-s-labyrinth",
        "movies",
        "category",
        ["P", "A", "N", "S", "B", "Y", "R", "I", "T", "H"],
        1,
      ),
    }),
  );
  await click('[data-action="resume"]');
  const punctuation = await cdp.evaluate(`({
    apostrophes: [...document.querySelectorAll('.punct')].map((el) => el.textContent).join(""),
    aria: document.querySelector('.word-display')?.getAttribute('aria-label'),
    overflow: document.documentElement.scrollWidth - window.innerWidth
  })`);
  check("apostrophe is rendered", punctuation.apostrophes.includes("'"), JSON.stringify(punctuation));
  check("punctuation does not break layout", punctuation.overflow === 0, JSON.stringify(punctuation));
  await screenshot("test-punctuation.png");
  await click('[data-action="letter"][data-letter="L"]');
  await sleep(500);
  const win = await cdp.evaluate(`({
    heading: document.querySelector('.result-sheet h2')?.textContent,
    answer: document.querySelector('.result-answer')?.textContent,
    activeNull: JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}))?.activeRound === null,
    solved: JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}))?.solvedIds.includes('movies-pan-s-labyrinth')
  })`);
  check("win shows result", win.heading === "You got it.", JSON.stringify(win));
  check("apostrophe answer is correct", win.answer === "PAN'S LABYRINTH", win.answer);
  check("win clears active round", win.activeNull);
  check("win adds solved puzzle", win.solved);

  console.log("Loss");
  await setSave(
    save({
      activeRound: round("movies-jaws", "movies", "category", ["E", "I", "O", "U", "B", "C"], 5),
    }),
  );
  await click('[data-action="resume"]');
  await screenshot("test-loss-near.png");
  await click('[data-action="letter"][data-letter="Z"]');
  await sleep(500);
  const loss = await cdp.evaluate(`({
    heading: document.querySelector('.result-sheet h2')?.textContent,
    answer: document.querySelector('.result-answer')?.textContent,
    missed: document.querySelectorAll('.tile.is-missed').length,
    streak: JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}))?.stats.currentStreak
  })`);
  check("loss shows result", loss.heading === "Out of takes.", JSON.stringify(loss));
  check("loss reveals answer", loss.answer === "JAWS", loss.answer);
  check("loss marks missing letters", loss.missed === 4, `missed ${loss.missed}`);
  const lossActions = await cdp.evaluate(`({
    retry: document.querySelector('[data-action="retry"]')?.textContent?.replace(/\\s+/g, ' ').trim(),
    next: !!document.querySelector('[data-action="next"]')
  })`);
  check("loss offers replay", lossActions.retry?.includes("Replay this puzzle"), JSON.stringify(lossActions));
  check("loss does not offer a different question", lossActions.next === false, JSON.stringify(lossActions));
  await screenshot("test-loss-result.png");

  await click('[data-action="retry"]');
  const retried = await cdp.evaluate(`(() => {
    const saved = JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}));
    return {
      puzzle: saved.activeRound?.puzzleId,
      status: saved.activeRound?.status,
      guessed: saved.activeRound?.guessed?.length,
      wrong: saved.activeRound?.wrong,
      lives: document.querySelector('.lives-label')?.textContent
    };
  })()`);
  check("retry opens the same puzzle", retried.puzzle === "movies-jaws", JSON.stringify(retried));
  check("retry resets the board", retried.status === "playing" && retried.guessed === 0 && retried.wrong === 0, JSON.stringify(retried));
  check("retry restores all six takes", retried.lives === "6 TAKES LEFT", retried.lives);
  await screenshot("test-retry.png");

  console.log("Hint");
  await setSave(
    save({
      stats: { played: 0, won: 0, currentStreak: 0, bestStreak: 0, points: 1000 },
      activeRound: round("tv-sherlock", "tv", "category", [], 0),
    }),
  );
  await click('[data-action="resume"]');
  await click('[data-action="hint"]');
  await click('[data-action="hint"]');
  await click('[data-action="hint"]');
  const hint = await cdp.evaluate(`(() => {
    const saved = JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}));
    const button = document.querySelector('.hint-button');
    return {
      hintsUsed: saved.activeRound.hintsUsed,
      wrong: saved.activeRound.wrong,
      guessed: saved.activeRound.guessed,
      points: saved.stats.points,
      label: button?.querySelector('span')?.textContent,
      cost: button?.querySelector('small')?.textContent,
      disabled: button?.disabled,
      chip: document.querySelector('.game-points')?.textContent?.replace(/\\s+/g, ' ').trim()
    };
  })()`);
  check("hint is used", hint.hintsUsed === 3, JSON.stringify(hint));
  check("hints remain unlimited", hint.disabled === false && hint.label === "Reveal a letter", JSON.stringify(hint));
  check("hint does not cost a take", hint.wrong === 0, JSON.stringify(hint));
  check("each hint reveals a letter", hint.guessed.length === 3, JSON.stringify(hint));
  check("each hint deducts 40 total points", hint.points === 880, JSON.stringify(hint));
  check("points chip updates immediately", hint.chip?.includes("880 PTS"), JSON.stringify(hint));
  check("hint still shows its cost", hint.cost === "−40 PTS", JSON.stringify(hint));
  await screenshot("test-hint.png");

  console.log("Daily feature");
  await setSave(save());
  await click('[data-action="daily"]');
  const daily = await cdp.evaluate(`(() => {
    const saved = JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}));
    return {
      mode: saved.activeRound?.mode,
      label: document.querySelector('.game-mode')?.textContent,
      double: !!document.querySelector('.clue-double')
    };
  })()`);
  check("daily starts in daily mode", daily.mode === "daily" && daily.label === "DAILY FEATURE", JSON.stringify(daily));
  check("daily shows a double-points badge", daily.double);
  await screenshot("test-daily.png");

  await setSave(
    save({
      activeRound: round(
        "movies-the-godfather",
        "movies",
        "daily",
        ["T", "H", "E", "G", "O", "D", "F", "A"],
        2,
      ),
    }),
  );
  await click('[data-action="resume"]');
  await click('[data-action="letter"][data-letter="R"]');
  await sleep(500);
  const dailyWin = await cdp.evaluate(`(() => {
    const saved = JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}));
    return {
      score: saved.history[0]?.score,
      daily: saved.daily,
      resultScore: document.querySelector('.result-score strong')?.textContent
    };
  })()`);
  check("daily score is doubled", dailyWin.score === 400, JSON.stringify(dailyWin));
  check("daily result is recorded", Boolean(dailyWin.daily?.won), JSON.stringify(dailyWin));
  await screenshot("test-daily-result.png");

  console.log("Stats and reset");
  await click('[data-action="home"]');
  await click('[data-action="nav"][data-screen="settings"]');
  await click('[data-action="reset"]');
  const modal = await cdp.evaluate(`({
    open: !!document.querySelector('.confirm-sheet'),
    title: document.querySelector('#reset-title')?.textContent,
    focus: document.activeElement?.textContent
  })`);
  check("reset confirmation opens", modal.open && modal.title === "Reset all progress?", JSON.stringify(modal));
  await screenshot("test-reset.png");
  await click('[data-action="cancel-reset"]');
  const statsBefore = await cdp.evaluate(`JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}))?.stats`);
  await click('[data-action="reset"]');
  await click('[data-action="confirm-reset"]');
  const reset = await cdp.evaluate(`(() => {
    const saved = JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}));
    return { screen: document.querySelector('.app-frame')?.dataset.screen, stats: saved.stats, settings: saved.settings };
  })()`);
  check("cancel preserves stats", statsBefore.played > 0 || statsBefore.won > 0, JSON.stringify(statsBefore));
  check("reset clears stats", reset.stats.played === 0 && reset.stats.won === 0, JSON.stringify(reset));
  check("reset keeps settings", reset.settings.reduceMotion === true, JSON.stringify(reset.settings));

  console.log("320 x 568 result");
  await viewport(320, 568);
  await setSave(
    save({
      activeRound: round("movies-jaws", "movies", "category", ["E", "I", "O", "U", "B", "C"], 5),
    }),
  );
  await click('[data-action="resume"]');
  await click('[data-action="letter"][data-letter="Z"]');
  await sleep(500);
  const smallResult = await cdp.evaluate(`(() => {
    const sheet = document.querySelector('.result-sheet');
    const box = sheet?.getBoundingClientRect();
    return {
      overflowX: document.documentElement.scrollWidth - window.innerWidth,
      sheetHeight: Math.round(box?.height || 0),
      viewport: window.innerHeight,
      scrollable: sheet ? sheet.scrollHeight > sheet.clientHeight : null
    };
  })()`);
  check("small result has no horizontal overflow", smallResult.overflowX === 0, JSON.stringify(smallResult));
  check("small result is on screen", smallResult.sheetHeight > 0 && smallResult.sheetHeight <= smallResult.viewport, JSON.stringify(smallResult));
  await screenshot("test-result-320.png");

  console.log("Keyboard");
  await setSave(
    save({
      activeRound: round("movies-jaws", "movies", "category", [], 0),
    }),
  );
  await click('[data-action="resume"]');
  await cdp.evaluate(`document.dispatchEvent(new KeyboardEvent('keydown', { key: 'J', bubbles: true })); true`);
  await sleep(300);
  const keyboard = await cdp.evaluate(`JSON.parse(localStorage.getItem(${JSON.stringify(SAVE_KEY)}))?.activeRound?.guessed`);
  check("physical keyboard guesses letters", keyboard.includes("J"), JSON.stringify(keyboard));

  if (cdp.consoleErrors.length) {
    console.log("Console errors:", cdp.consoleErrors);
    failures.push("console errors");
  }
  cdp.socket.close();

  console.log(`\n${failures.length === 0 ? "ALL CHECKS PASSED" : `${failures.length} FAILURE(S)`}`);
  if (failures.length) process.exitCode = 1;
}

await main();
