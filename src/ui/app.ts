import type {
  CategoryId,
  GameMode,
  IconName,
  Puzzle,
  Round,
  SaveData,
  Settings,
} from "../types";
import { CATEGORIES, CATEGORY_MAP, DIFFICULTY_LABEL } from "../data/categories";
import { CATEGORY_COUNT, PUZZLES, PUZZLE_MAP } from "../data/index";
import {
  answerLetters,
  createRound,
  dailyPuzzle,
  guessLetter,
  isCorrectGuess,
  letterState,
  livesLeft,
  localDateKey,
  MAX_LIVES,
  normalizeAnswer,
  pickPuzzle,
  revealHint,
} from "../core/game";
import {
  isDailyComplete,
  loadSave,
  persistSave,
  recordResult,
  resetProgress,
  saveActiveRound,
  solvedInCategory,
} from "../core/storage";
import { sounds } from "../core/audio";
import { haptic } from "../core/platform";
import { icon } from "./icons";

type Screen = "home" | "game" | "stats" | "settings" | "howto";
type SettingKey = keyof Settings;

const SCREENS: Screen[] = ["home", "game", "stats", "settings", "howto"];

const WEEKDAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
const MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (character) => {
    switch (character) {
      case "&":
        return "&amp;";
      case "<":
        return "&lt;";
      case ">":
        return "&gt;";
      case '"':
        return "&quot;";
      default:
        return "&#39;";
    }
  });
}

function formatNumber(value: number): string {
  return Math.max(0, Math.round(value)).toLocaleString("en-US");
}

function dateLabel(date = new Date()): string {
  return `${WEEKDAYS[date.getDay()]} · ${MONTHS[date.getMonth()]} ${date.getDate()}`;
}

function shortDate(timestamp: number): string {
  const date = new Date(timestamp);
  return `${MONTHS[date.getMonth()]} ${date.getDate()}`;
}

function plural(value: number, singular: string, pluralForm = `${singular}s`): string {
  return `${value} ${value === 1 ? singular : pluralForm}`;
}

export class ReelHangmanApp {
  private readonly root: HTMLElement;
  private save: SaveData;
  private screen: Screen = "home";
  private round: Round | null = null;
  private puzzle: Puzzle | null = null;
  private resetConfirm = false;
  private toastTimer: number | null = null;
  private scrollOnRender = false;

  constructor(root: HTMLElement) {
    this.root = root;
    this.save = loadSave();

    const active = this.save.activeRound;
    if (active) {
      const puzzle = PUZZLE_MAP.get(active.puzzleId);
      if (puzzle) {
        this.round = active;
        this.puzzle = puzzle;
      } else {
        this.save = saveActiveRound(this.save, null);
        persistSave(this.save);
      }
    }

    sounds.setEnabled(this.save.settings.sound);
  }

  start(): void {
    this.root.addEventListener("click", this.handleClick);
    document.addEventListener("keydown", this.handleKeyDown);
    window.addEventListener("popstate", this.handlePopState);
    history.replaceState({ screen: "home" }, "", "#home");
    this.render();
  }

  onNativeBack(): void {
    if (this.resetConfirm) {
      this.resetConfirm = false;
      this.render();
      return;
    }
    if (this.screen === "home") {
      void this.exitApp();
      return;
    }
    this.goBack();
  }

  private handleClick = (event: MouseEvent): void => {
    if (!(event.target instanceof Element)) return;
    const actionEl = event.target.closest<HTMLElement>("[data-action]");
    if (!actionEl || !this.root.contains(actionEl)) return;

    const action = actionEl.dataset.action ?? "";
    if (action === "letter") {
      const letter = actionEl.dataset.letter;
      if (letter) this.handleLetter(letter);
      return;
    }
    if (action === "hint") {
      this.handleHint();
      return;
    }

    sounds.unlock();
    sounds.tap();

    switch (action) {
      case "quick":
        this.beginRound(null, "quick");
        break;
      case "resume":
        this.resumeRound();
        break;
      case "category": {
        const category = actionEl.dataset.category as CategoryId | undefined;
        if (category && CATEGORY_MAP[category]) this.beginRound(category, "category");
        break;
      }
      case "daily":
        this.startDaily();
        break;
      case "next":
        this.nextRound();
        break;
      case "home":
        this.goHome();
        break;
      case "back":
        this.goBack();
        break;
      case "stats":
        this.go("stats", true);
        break;
      case "settings":
        this.go("settings", true);
        break;
      case "howto":
        this.go("howto");
        break;
      case "nav": {
        const screen = actionEl.dataset.screen as Screen | undefined;
        if (screen && SCREENS.includes(screen)) this.go(screen, true);
        break;
      }
      case "toggle-setting": {
        const setting = actionEl.dataset.setting as SettingKey | undefined;
        if (setting && setting in this.save.settings) this.toggleSetting(setting);
        break;
      }
      case "reset":
        this.resetConfirm = true;
        this.render();
        break;
      case "cancel-reset":
        this.resetConfirm = false;
        this.render();
        break;
      case "confirm-reset":
        this.resetAll();
        break;
      case "result-stats":
        this.round = null;
        this.puzzle = null;
        this.go("stats", true);
        break;
      default:
        break;
    }
  };

  private handleKeyDown = (event: KeyboardEvent): void => {
    if (this.resetConfirm) {
      if (event.key === "Escape") {
        event.preventDefault();
        this.resetConfirm = false;
        this.render();
      } else if (event.key === "Tab") {
        this.trapFocus(event, ".confirm-sheet");
      }
      return;
    }

    if (this.screen === "game" && this.round && this.round.status !== "playing") {
      if (event.key === "Escape") {
        event.preventDefault();
        this.leaveResult();
      } else if (event.key === "Tab") {
        this.trapFocus(event, ".result-sheet");
      }
      return;
    }

    if (this.screen === "game" && this.round?.status === "playing") {
      if (/^[a-zA-Z]$/.test(event.key) && !event.ctrlKey && !event.metaKey && !event.altKey) {
        event.preventDefault();
        this.handleLetter(event.key.toUpperCase());
        return;
      }
      if (event.key === "Escape") {
        event.preventDefault();
        this.goBack();
        return;
      }
    }

    if (event.key === "Escape" && this.screen !== "home") {
      event.preventDefault();
      this.goBack();
    }
  };

  private handlePopState = (): void => {
    const state = history.state as { screen?: Screen } | null;
    const target = state?.screen;
    this.screen = target && SCREENS.includes(target) ? target : "home";

    if (this.screen !== "game" && this.round?.status !== "playing") {
      this.round = null;
      this.puzzle = null;
    }
    if (this.screen === "game" && (!this.round || !this.puzzle)) {
      this.screen = "home";
    }

    this.scrollOnRender = true;
    this.render();
  };

  private go(screen: Screen, replace = false): void {
    if (this.screen === screen) {
      this.render();
      return;
    }
    this.screen = screen;
    this.scrollOnRender = true;
    const state = { screen };
    if (replace) {
      history.replaceState(state, "", `#${screen}`);
    } else {
      history.pushState(state, "", `#${screen}`);
    }
    this.render();
  }

  private goBack(): void {
    if (this.screen === "home") return;
    const state = history.state as { screen?: Screen } | null;
    if (state?.screen === this.screen && history.length > 1) {
      history.back();
    } else {
      this.go("home", true);
    }
  }

  private goHome(): void {
    if (this.round?.status !== "playing") {
      this.round = null;
      this.puzzle = null;
    }
    this.go("home", true);
  }

  private leaveResult(): void {
    this.round = null;
    this.puzzle = null;
    this.go("home", true);
  }

  private async exitApp(): Promise<void> {
    try {
      const { App } = await import("@capacitor/app");
      await App.exitApp();
    } catch {
      // Browser builds simply stay on the home screen.
    }
  }

  private beginRound(category: CategoryId | null, mode: GameMode, replace = false): void {
    const puzzle = pickPuzzle(PUZZLES, {
      category: category ?? undefined,
      mode,
      solvedIds: new Set(this.save.solvedIds),
      recentIds: this.save.recentIds,
    });
    this.startPuzzle(puzzle, mode, replace);
  }

  private startPuzzle(puzzle: Puzzle, mode: GameMode, replace = false): void {
    this.puzzle = puzzle;
    this.round = createRound(puzzle, mode);
    this.save = saveActiveRound(this.save, this.round);
    persistSave(this.save);
    this.go("game", replace);
  }

  private resumeRound(): void {
    if (this.round?.status === "playing" && this.puzzle) {
      this.go("game");
      return;
    }
    this.showToast("That round has already wrapped.");
    this.round = null;
    this.puzzle = null;
    this.render();
  }

  private startDaily(): void {
    const today = localDateKey();
    if (isDailyComplete(this.save, today)) {
      this.showToast("Today's feature is already in the books.");
      return;
    }

    const feature = dailyPuzzle(PUZZLES, today);
    if (this.round?.status === "playing" && this.round.mode === "daily" && this.puzzle?.id === feature.id) {
      this.go("game");
      return;
    }
    this.startPuzzle(feature, "daily");
  }

  private nextRound(): void {
    if (!this.round) return;
    const mode = this.round.mode;
    const category = this.round.category;
    if (mode === "daily") {
      this.leaveResult();
      return;
    }
    this.round = null;
    this.puzzle = null;
    this.beginRound(mode === "category" ? category : null, mode === "category" ? "category" : "quick", true);
  }

  private handleLetter(letter: string): void {
    if (!this.round || !this.puzzle || this.round.status !== "playing") return;
    const previous = this.round;
    const next = guessLetter(this.puzzle, previous, letter);
    if (next === previous) return;

    this.round = next;
    const correct = isCorrectGuess(this.puzzle, letter);

    if (next.status === "playing") {
      this.save = saveActiveRound(this.save, next);
      persistSave(this.save);
      if (correct) {
        sounds.correct();
        void haptic("light", this.save.settings.haptics);
        const remaining = answerLetters(this.puzzle.answer).filter(
          (item) => !next.guessed.includes(item),
        ).length;
        this.announce(`Correct. ${plural(remaining, "letter")} still missing.`);
      } else {
        sounds.wrong();
        void haptic("medium", this.save.settings.haptics);
        this.announce(`Not in the answer. ${plural(livesLeft(next), "take")} left.`);
      }
      this.render();
      return;
    }

    this.finishRound();
  }

  private handleHint(): void {
    if (!this.round || !this.puzzle || this.round.status !== "playing") return;
    const next = revealHint(this.puzzle, this.round);
    if (next === this.round) return;

    this.round = next;
    sounds.hint();
    void haptic("light", this.save.settings.haptics);

    if (next.status === "playing") {
      this.save = saveActiveRound(this.save, next);
      persistSave(this.save);
      const revealed = next.guessed[next.guessed.length - 1];
      this.announce(`Hint revealed ${revealed}. Forty points deducted.`);
      this.render();
      return;
    }

    this.finishRound();
  }

  private finishRound(): void {
    if (!this.round || !this.puzzle) return;
    const won = this.round.status === "won";
    this.save = recordResult(this.save, this.puzzle, this.round);
    persistSave(this.save);

    if (won) {
      sounds.win();
      void haptic("success", this.save.settings.haptics);
      this.announce(`Solved. ${formatNumber(this.round.score)} points.`);
    } else {
      sounds.lose();
      void haptic("error", this.save.settings.haptics);
      this.announce(`Out of takes. The answer was ${this.puzzle.answer}.`);
    }

    this.render();
  }

  private toggleSetting(setting: SettingKey): void {
    const enabled = !this.save.settings[setting];
    this.save = {
      ...this.save,
      settings: {
        ...this.save.settings,
        [setting]: enabled,
      },
    };
    persistSave(this.save);

    if (setting === "sound") {
      sounds.setEnabled(enabled);
      if (enabled) sounds.tap();
    }
    if (setting === "haptics" && enabled) {
      void haptic("light", true);
    }

    this.render();
    const labels: Record<SettingKey, string> = {
      sound: "Sound effects",
      haptics: "Haptics",
      reduceMotion: "Reduced motion",
    };
    this.showToast(`${labels[setting]} ${enabled ? "on" : "off"}.`);
  }

  private resetAll(): void {
    this.save = resetProgress(this.save);
    this.round = null;
    this.puzzle = null;
    this.resetConfirm = false;
    persistSave(this.save);
    sounds.setEnabled(this.save.settings.sound);
    this.go("home", true);
    this.showToast("Progress reset. A clean slate.");
  }

  private showToast(message: string): void {
    const toast = document.getElementById("toast");
    if (!toast) return;
    if (this.toastTimer) window.clearTimeout(this.toastTimer);
    toast.textContent = message;
    toast.classList.add("is-visible");
    this.toastTimer = window.setTimeout(() => {
      toast.classList.remove("is-visible");
    }, 2400);
  }

  private announce(message: string): void {
    const live = document.getElementById("live-region");
    if (live) live.textContent = message;
  }

  private trapFocus(event: KeyboardEvent, selector: string): void {
    const container = this.root.querySelector<HTMLElement>(selector);
    if (!container) return;
    const focusables = [...container.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    )].filter((element) => element.offsetParent !== null);

    if (focusables.length === 0) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const active = document.activeElement;

    if (event.shiftKey) {
      if (active === first || !container.contains(active)) {
        event.preventDefault();
        last.focus();
      }
    } else if (active === last || !container.contains(active)) {
      event.preventDefault();
      first.focus();
    }
  }

  private render(): void {
    if (this.screen === "game" && (!this.round || !this.puzzle)) {
      this.screen = "home";
    }

    const reduced =
      this.save.settings.reduceMotion ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let content = "";

    switch (this.screen) {
      case "game":
        content = this.renderGame();
        break;
      case "stats":
        content = this.renderStats();
        break;
      case "settings":
        content = this.renderSettings();
        break;
      case "howto":
        content = this.renderHowTo();
        break;
      default:
        content = this.renderHome();
        break;
    }

    this.root.innerHTML = `<div class="app-frame${reduced ? " reduce-motion" : ""}" data-screen="${this.screen}">${content}${this.resetConfirm ? this.confirmOverlay() : ""}</div>`;

    const titles: Record<Screen, string> = {
      home: "Reel Hangman — Movie & TV Hangman",
      game: "Reel Hangman — Play",
      stats: "Reel Hangman — Your Stats",
      settings: "Reel Hangman — Settings",
      howto: "Reel Hangman — How to Play",
    };
    document.title = titles[this.screen];

    if (this.scrollOnRender) {
      const scroller = this.root.querySelector<HTMLElement>(".scroll-area");
      if (scroller) scroller.scrollTop = 0;
      this.scrollOnRender = false;
    }

    requestAnimationFrame(() => {
      const target = this.root.querySelector<HTMLElement>("[data-autofocus]");
      if (target) target.focus({ preventScroll: true });
    });
  }

  private topbar(): string {
    return `
      <header class="topbar">
        <button class="brand" type="button" data-action="home" aria-label="Reel Hangman home">
          <span class="brand-mark">${icon("clapper")}</span>
          <span class="brand-type"><span>REEL</span><strong>HANGMAN</strong></span>
        </button>
        <div class="topbar-actions">
          <span class="streak-chip" title="Current win streak">${icon("spark")}<strong>${this.save.stats.currentStreak}</strong></span>
          <button class="icon-button" type="button" data-action="settings" aria-label="Settings">${icon("settings")}</button>
        </div>
      </header>
    `;
  }

  private pageTopbar(title: string, showBack = false): string {
    return `
      <header class="topbar page-topbar">
        ${
          showBack
            ? `<button class="icon-button" type="button" data-action="back" aria-label="Back">${icon("back")}</button>`
            : `<span class="topbar-spacer" aria-hidden="true"></span>`
        }
        <span class="page-topbar-title">${escapeHtml(title)}</span>
        <span class="topbar-spacer" aria-hidden="true"></span>
      </header>
    `;
  }

  private bottomNav(active: "home" | "stats" | "settings"): string {
    const tabs = [
      { id: "home", label: "Play", icon: "play" as IconName },
      { id: "stats", label: "Stats", icon: "chart" as IconName },
      { id: "settings", label: "Settings", icon: "settings" as IconName },
    ];

    return `
      <nav class="bottom-nav" aria-label="Main navigation">
        ${tabs
          .map(
            (tab) => `
              <button class="nav-item${active === tab.id ? " is-active" : ""}" type="button" data-action="nav" data-screen="${tab.id}" ${active === tab.id ? 'aria-current="page"' : ""}>
                ${icon(tab.icon)}
                <span>${tab.label}</span>
              </button>
            `,
          )
          .join("")}
      </nav>
    `;
  }

  private renderHome(): string {
    const activeRound = this.round?.status === "playing" ? this.round : null;
    const activePuzzle = activeRound ? PUZZLE_MAP.get(activeRound.puzzleId) : null;
    const activeCategory = activeRound ? CATEGORY_MAP[activeRound.category] : null;

    const heroAction =
      activeRound && activePuzzle && activeCategory
        ? `
          <button class="primary-button" type="button" data-action="resume">
            <span class="primary-icon">${icon("play")}</span>
            <span class="primary-copy">
              <strong>Continue round</strong>
              <span>${activeCategory.name} · ${plural(livesLeft(activeRound), "take")} left</span>
            </span>
            ${icon("arrow", "primary-arrow")}
          </button>
          <button class="text-button" type="button" data-action="quick">Start a new puzzle</button>
        `
        : `
          <button class="primary-button" type="button" data-action="quick">
            <span class="primary-icon">${icon("play")}</span>
            <span class="primary-copy">
              <strong>Play a random puzzle</strong>
              <span>${PUZZLES.length} clues across seven categories</span>
            </span>
            ${icon("arrow", "primary-arrow")}
          </button>
          <button class="text-button" type="button" data-action="howto">How it works</button>
        `;

    const totalSolved = Math.min(this.save.solvedIds.length, PUZZLES.length);

    return `
      <div class="screen home-screen">
        ${this.topbar()}
        <main class="scroll-area home-scroll">
          <section class="hero">
            <p class="eyebrow"><span class="eyebrow-line"></span>OFFLINE CINEMA TRIVIA</p>
            <h1>Name the<br><em>screen classic.</em></h1>
            <p class="hero-copy">A movie and TV hangman game for people who quote the credits. Every answer is a film, show, star, character, director, or famous screen family.</p>
            <div class="hero-actions">${heroAction}</div>
            <p class="hero-note">${icon("lock")} No ads. No accounts. No signal needed.</p>
          </section>

          ${this.renderDailyCard()}

          <section class="genre-section">
            <div class="section-heading">
              <div>
                <p class="kicker">THE ARCHIVE</p>
                <h2>Pick a category</h2>
              </div>
              <span class="section-count">${totalSolved}/${PUZZLES.length}<small>solved</small></span>
            </div>
            <div class="genre-grid">
              ${CATEGORIES.map((category) => this.categoryCard(category.id)).join("")}
            </div>
          </section>

          <footer class="home-footer">
            <span>NO ADS</span><i></i><span>NO ACCOUNTS</span><i></i><span>NO SIGNAL</span>
          </footer>
        </main>
        ${this.bottomNav("home")}
      </div>
    `;
  }

  private renderDailyCard(): string {
    const today = localDateKey();
    const record = this.save.daily?.date === today ? this.save.daily : null;
    const activeDaily =
      this.round?.status === "playing" &&
      this.round.mode === "daily" &&
      this.puzzle?.id === dailyPuzzle(PUZZLES, today).id;

    let title = "One clue. Double points.";
    let copy = "A hand-picked puzzle from the archive, refreshed every day.";
    if (record) {
      title = record.won ? "Today's feature is solved." : "The credits rolled early.";
      copy = record.won
        ? `You banked ${formatNumber(record.score)} points. A new feature arrives at midnight.`
        : "No takes left today. Tomorrow brings a brand-new feature.";
    } else if (activeDaily) {
      title = "Your feature is still running.";
      copy = "Pick up your daily round where you left off.";
    }

    return `
      <section class="daily-card${record ? " is-complete" : ""}" aria-labelledby="daily-title">
        <div class="daily-glow" aria-hidden="true"></div>
        <div class="daily-top">
          <span class="daily-kicker">${icon("calendar")}DAILY FEATURE</span>
          <span class="daily-date">${dateLabel()}</span>
        </div>
        <div class="daily-main">
          <h2 id="daily-title">${title}</h2>
          <p>${copy}</p>
        </div>
        <div class="daily-bottom">
          <span class="double-badge">${icon("spark")}2× POINTS</span>
          ${
            record
              ? `<span class="daily-done">${icon(record.won ? "check" : "ticket")}${record.won ? `+${formatNumber(record.score)} PTS` : "COMPLETE"}</span>`
              : `<button class="daily-button" type="button" data-action="daily">${activeDaily ? "RESUME" : "PLAY"} ${icon("arrow")}</button>`
          }
        </div>
      </section>
    `;
  }

  private categoryCard(categoryId: CategoryId): string {
    const category = CATEGORY_MAP[categoryId];
    const solved = solvedInCategory(this.save, categoryId);
    const total = CATEGORY_COUNT[categoryId];
    const percent = total > 0 ? Math.min(100, Math.round((solved / total) * 100)) : 0;
    const wide = categoryId === "families";

    return `
      <button class="genre-card${wide ? " genre-card-wide" : ""}" type="button" data-action="category" data-category="${categoryId}" style="--accent:${category.accent}" aria-label="${escapeHtml(category.name)}: ${solved} of ${total} solved">
        <span class="genre-icon">${icon(category.icon)}</span>
        <span class="genre-body">
          <span class="genre-name">${category.name}</span>
          <span class="genre-tagline">${category.tagline}</span>
          <span class="genre-meter" role="progressbar" aria-label="${solved} of ${total} solved" aria-valuemin="0" aria-valuemax="${total}" aria-valuenow="${solved}"><span style="width:${percent}%"></span></span>
        </span>
        <span class="genre-count">${solved}<small>/${total}</small></span>
      </button>
    `;
  }

  private renderGame(): string {
    if (!this.round || !this.puzzle) return this.renderHome();
    const round = this.round;
    const puzzle = this.puzzle;
    const category = CATEGORY_MAP[round.category];
    const modeLabel =
      round.mode === "daily" ? "DAILY FEATURE" : round.mode === "category" ? "CATEGORY ROUND" : "QUICK PLAY";
    const remaining = livesLeft(round);
    const usedLetters = new Set(round.guessed);
    const ended = round.status !== "playing";

    return `
      <div class="screen game-screen">
        <header class="game-header">
          <button class="icon-button" type="button" data-action="back" aria-label="Back">${icon("back")}</button>
          <div class="game-heading">
            <span class="game-category">${category.name}</span>
            <span class="game-mode">${modeLabel}</span>
          </div>
          <button class="icon-button" type="button" data-action="toggle-setting" data-setting="sound" aria-label="${this.save.settings.sound ? "Mute sound" : "Enable sound"}">${icon(this.save.settings.sound ? "sound" : "mute")}</button>
        </header>

        <main class="game-main">
          <section class="clue-card" style="--accent:${category.accent}">
            <div class="clue-top">
              <span class="clue-category">${category.name}</span>
              <span class="clue-difficulty">${DIFFICULTY_LABEL[puzzle.difficulty]}</span>
              ${round.mode === "daily" ? '<span class="clue-double">2×</span>' : ""}
            </div>
            <h1 class="clue-text">${escapeHtml(puzzle.clue)}</h1>
          </section>

          <section class="stage">
            <div class="stage-halo" aria-hidden="true"></div>
            ${this.hangman(round.wrong)}
            <div class="lives">
              <span class="lives-label">${remaining} ${remaining === 1 ? "TAKE" : "TAKES"} LEFT</span>
              <span class="lives-dots" aria-hidden="true">
                ${Array.from({ length: MAX_LIVES }, (_, index) => `<i class="${index < remaining ? "is-full" : ""}"></i>`).join("")}
              </span>
            </div>
          </section>

          <section class="word-wrap" aria-label="Answer">
            ${this.wordMarkup(puzzle, round)}
          </section>

          <section class="keyboard" aria-label="Letter keyboard">
            ${this.keyboard(puzzle, round)}
          </section>

          <div class="game-actions">
            <button class="hint-button" type="button" data-action="hint" ${round.hintUsed || ended ? "disabled" : ""}>
              ${icon("bulb")}
              <span>${round.hintUsed ? "Hint used" : "Reveal a letter"}</span>
              <small>${round.hintUsed ? "ONE PER ROUND" : "−40 PTS"}</small>
            </button>
            <span class="game-tip">${usedLetters.size === 0 ? "Tap a letter to begin" : `${plural(remaining, "take")} between you and the credits`}</span>
          </div>
        </main>
        ${this.resultOverlay()}
      </div>
    `;
  }

  private hangman(wrong: number): string {
    const clamped = Math.max(0, Math.min(MAX_LIVES, wrong));
    const parts = [
      `<circle class="figure-part" cx="168" cy="68" r="16" pathLength="1" style="--part-delay:0ms"/>`,
      `<path class="figure-part" d="M168 84V132" pathLength="1" style="--part-delay:80ms"/>`,
      `<path class="figure-part" d="m168 98-24 20" pathLength="1" style="--part-delay:160ms"/>`,
      `<path class="figure-part" d="m168 98 24 20" pathLength="1" style="--part-delay:240ms"/>`,
      `<path class="figure-part" d="m168 132-20 34" pathLength="1" style="--part-delay:320ms"/>`,
      `<path class="figure-part" d="m168 132 20 34" pathLength="1" style="--part-delay:400ms"/>`,
    ];

    return `
      <svg class="hangman${clamped >= MAX_LIVES ? " is-dead" : ""}" viewBox="0 0 230 205" fill="none" aria-hidden="true">
        <g class="gallows">
          <path d="M22 190h186"/>
          <path d="M58 190V30"/>
          <path d="M58 30h110"/>
          <path d="m58 56 30-26"/>
          <path d="M168 30v22"/>
          <path d="M38 190h40"/>
        </g>
        <g class="figure">
          ${parts.slice(0, clamped).join("")}
          ${
            clamped >= 1
              ? clamped >= MAX_LIVES
                ? `<g class="dead-eyes"><path d="m162 65 4 4m0-4-4 4M170 65l4 4m0-4-4 4"/></g>`
                : `<circle cx="163" cy="66" r="1.4" fill="currentColor"/><circle cx="173" cy="66" r="1.4" fill="currentColor"/>`
              : ""
          }
        </g>
      </svg>
    `;
  }

  private wordMarkup(puzzle: Puzzle, round: Round): string {
    const guessed = new Set(round.guessed);
    const showAll = round.status === "won" || round.status === "lost";
    const words = puzzle.answer.split(/\s+/);
    let tileIndex = 0;

    const wordsHtml = words
      .map((word) => {
        const chars = Array.from(word).map((char) => {
          const letter = normalizeAnswer(char);
          if (!/^[A-Z]$/.test(letter)) {
            return `<span class="punct">${escapeHtml(char)}</span>`;
          }
          const revealed = guessed.has(letter) || showAll;
          const missed = round.status === "lost" && !guessed.has(letter);
          const classes = [
            "tile",
            revealed ? "is-revealed" : "",
            round.status === "won" ? "is-solved" : "",
            missed ? "is-missed" : "",
          ]
            .filter(Boolean)
            .join(" ");
          const style = `style="--i:${tileIndex}"`;
          tileIndex += 1;
          return `<span class="${classes}" ${style}>${revealed ? letter : ""}</span>`;
        });
        return `<span class="word">${chars.join("")}</span>`;
      })
      .join("");

    const totalLetters = normalizeAnswer(puzzle.answer).replace(/[^A-Z]/g, "").length;
    const guessedCount = answerLetters(puzzle.answer).filter((letter) => guessed.has(letter)).length;

    return `<div class="word-display" role="group" aria-label="${totalLetters} letters, ${words.length} words, ${guessedCount} letters found">${wordsHtml}</div>`;
  }

  private keyboard(puzzle: Puzzle, round: Round): string {
    const ended = round.status !== "playing";
    const rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"];

    return rows
      .map(
        (row) => `
          <div class="keyboard-row">
            ${Array.from(row)
              .map((letter) => {
                const state = letterState(puzzle, round, letter);
                const used = round.guessed.includes(letter);
                const disabled = used || ended;
                return `<button class="key key-${state}" type="button" data-action="letter" data-letter="${letter}" ${disabled ? "disabled" : ""} aria-label="${letter}${state === "correct" ? ", correct" : state === "wrong" ? ", wrong" : ""}">${letter}</button>`;
              })
              .join("")}
          </div>
        `,
      )
      .join("");
  }

  private resultOverlay(): string {
    if (!this.round || !this.puzzle || this.round.status === "playing") return "";
    const won = this.round.status === "won";
    const round = this.round;
    const puzzle = this.puzzle;
    const category = CATEGORY_MAP[round.category];

    return `
      <div class="result-overlay" role="dialog" aria-modal="true" aria-labelledby="result-title">
        ${won ? this.confetti() : ""}
        <div class="result-sheet">
          <div class="result-seal${won ? " is-win" : ""}">${icon(won ? "trophy" : "ticket")}</div>
          <p class="result-kicker">${won ? "THAT'S A WRAP" : "CURTAIN CALL"}</p>
          <h2 id="result-title">${won ? "You got it." : "Out of takes."}</h2>
          <p class="result-answer">${escapeHtml(puzzle.answer)}</p>
          <p class="result-copy">${won ? "The answer was hiding in plain sight. Cue the applause." : "No more takes, but every great flop becomes a cult classic. The answer is above."}</p>

          <div class="result-fact">
            <span class="fact-label">BEHIND THE SCENES</span>
            <p>${escapeHtml(puzzle.fact)}</p>
          </div>

          <div class="result-score">
            <span><small>${won ? "SCORE" : "SCORE"}</small><strong>${won ? `+${formatNumber(round.score)}` : "0"}</strong></span>
            <span><small>STREAK</small><strong>${this.save.stats.currentStreak}</strong></span>
            <span><small>CATEGORY</small><strong>${category.name}</strong></span>
          </div>

          <div class="result-actions">
            ${
              round.mode === "daily"
                ? `
                  <button class="primary-button compact" type="button" data-action="home" data-autofocus>
                    <span class="primary-copy"><strong>Back to the lobby</strong></span>
                    ${icon("arrow")}
                  </button>
                  <button class="text-button" type="button" data-action="result-stats">View your stats</button>
                `
                : `
                  <button class="primary-button compact" type="button" data-action="next" data-autofocus>
                    <span class="primary-copy"><strong>Next puzzle</strong></span>
                    ${icon("arrow")}
                  </button>
                  <button class="text-button" type="button" data-action="home">Back to the lobby</button>
                `
            }
          </div>
        </div>
      </div>
    `;
  }

  private confetti(): string {
    const colors = ["#f4c95d", "#f0926f", "#80d9e8", "#f28fb6", "#b49cff"];
    return `<div class="confetti" aria-hidden="true">${Array.from({ length: 24 }, (_, index) => {
      const x = (index * 41 + 7) % 100;
      const delay = (index % 8) * 55;
      const duration = 1700 + (index % 6) * 170;
      const rotation = (index * 47) % 360;
      const color = colors[index % colors.length];
      return `<i style="--x:${x}%;--delay:${delay}ms;--duration:${duration}ms;--rot:${rotation}deg;--color:${color}"></i>`;
    }).join("")}</div>`;
  }

  private renderStats(): string {
    const { played, won, currentStreak, bestStreak, points } = this.save.stats;
    const rate = played > 0 ? Math.round((won / played) * 100) : 0;
    const circumference = 2 * Math.PI * 56;
    const offset = circumference * (1 - rate / 100);
    const totalSolved = Math.min(this.save.solvedIds.length, PUZZLES.length);
    const history = this.save.history.slice(0, 6);

    return `
      <div class="screen page-screen">
        ${this.pageTopbar("The box office")}
        <main class="scroll-area page-scroll">
          <section class="stats-hero">
            <div class="win-ring" aria-hidden="true">
              <svg viewBox="0 0 140 140">
                <circle class="ring-track" cx="70" cy="70" r="56"/>
                <circle class="ring-value" cx="70" cy="70" r="56" stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"/>
              </svg>
              <span class="ring-label"><strong>${rate}<small>%</small></strong><span>WIN RATE</span></span>
            </div>
            <div class="stats-heading">
              <p class="kicker">YOUR RECORD</p>
              <h1>The box office.</h1>
              <p>${played === 0 ? "Your first solved puzzle starts the reel." : `${plural(won, "win")} from ${plural(played, "round")}. Every answer adds a frame.`}</p>
            </div>
          </section>

          <div class="stat-grid">
            <div class="stat-tile"><span class="stat-icon">${icon("check")}</span><strong>${formatNumber(totalSolved)}</strong><small>PUZZLES SOLVED</small></div>
            <div class="stat-tile"><span class="stat-icon">${icon("spark")}</span><strong>${formatNumber(currentStreak)}</strong><small>CURRENT STREAK</small></div>
            <div class="stat-tile"><span class="stat-icon">${icon("trophy")}</span><strong>${formatNumber(bestStreak)}</strong><small>BEST STREAK</small></div>
            <div class="stat-tile"><span class="stat-icon">${icon("ticket")}</span><strong>${formatNumber(points)}</strong><small>TOTAL POINTS</small></div>
          </div>

          <section class="panel">
            <div class="section-heading compact">
              <div><p class="kicker">THE ARCHIVE</p><h2>Genre progress</h2></div>
              <span class="section-count">${totalSolved}/${PUZZLES.length}</span>
            </div>
            <div class="progress-list">
              ${CATEGORIES.map((category) => {
                const solved = solvedInCategory(this.save, category.id);
                const total = CATEGORY_COUNT[category.id];
                const percent = total > 0 ? Math.round((solved / total) * 100) : 0;
                return `
                  <div class="progress-row" style="--accent:${category.accent}">
                    <span class="progress-icon">${icon(category.icon)}</span>
                    <span class="progress-name">${category.name}</span>
                    <span class="progress-track" role="progressbar" aria-label="${category.name} progress" aria-valuemin="0" aria-valuemax="${total}" aria-valuenow="${solved}"><span style="width:${percent}%"></span></span>
                    <span class="progress-value">${solved}<small>/${total}</small></span>
                  </div>
                `;
              }).join("")}
            </div>
          </section>

          <section class="panel">
            <div class="section-heading compact">
              <div><p class="kicker">THE LOG</p><h2>Recent screenings</h2></div>
            </div>
            ${
              history.length === 0
                ? `<div class="empty-history">${icon("ticket")}<p>No screenings yet. Your first puzzle is waiting in the lobby.</p><button class="small-button" type="button" data-action="quick">Play a puzzle</button></div>`
                : `<div class="history-list">${history
                    .map(
                      (item) => `
                        <div class="history-row">
                          <span class="history-mark${item.won ? " is-win" : ""}">${icon(item.won ? "check" : "close")}</span>
                          <span class="history-copy"><strong>${escapeHtml(item.answer)}</strong><small>${CATEGORY_MAP[item.category]?.name ?? "Screen"} · ${shortDate(item.at)}</small></span>
                          <span class="history-score">${item.won ? `+${formatNumber(item.score)}` : "—"}</span>
                        </div>
                      `,
                    )
                    .join("")}</div>`
            }
          </section>

          <button class="text-button stats-play" type="button" data-action="quick">Play a random puzzle ${icon("arrow")}</button>
        </main>
        ${this.bottomNav("stats")}
      </div>
    `;
  }

  private renderSettings(): string {
    return `
      <div class="screen page-screen">
        ${this.pageTopbar("Projection booth")}
        <main class="scroll-area page-scroll">
          <section class="page-intro">
            <p class="kicker">PREFERENCES</p>
            <h1>Make it yours.</h1>
            <p>Reel Hangman runs entirely on this device. Your progress, streaks, and settings never leave it.</p>
          </section>

          <section class="panel settings-panel">
            ${this.settingRow("sound", this.save.settings.sound ? "sound" : "mute", "Sound effects", "Chimes, stings, and the occasional wrong-letter thud.")}
            ${this.settingRow("haptics", "haptic", "Haptics", "A small tap when a letter lands.")}
            ${this.settingRow("reduceMotion", "motion", "Reduced motion", "Calmer transitions and no falling confetti.")}
          </section>

          <section class="panel link-panel">
            <button class="link-row" type="button" data-action="howto">
              <span class="link-icon">${icon("info")}</span>
              <span class="link-copy"><strong>How to play</strong><small>Rules, scoring, and six takes</small></span>
              ${icon("arrow")}
            </button>
            <button class="link-row danger" type="button" data-action="reset">
              <span class="link-icon">${icon("reset")}</span>
              <span class="link-copy"><strong>Reset progress</strong><small>Clear stats, streaks, and solved puzzles</small></span>
              ${icon("arrow")}
            </button>
          </section>

          <section class="about-card">
            <div class="about-mark">${icon("clapper")}</div>
            <div class="about-copy">
              <h2>Reel Hangman</h2>
              <p>Version 1.0.0 · ${PUZZLES.length} hand-written clues</p>
            </div>
            <p class="about-note">Built for movie lovers who quote the credits. No ads, no accounts, no tracking—just you, the clue, and the letters.</p>
            <p class="about-fine">Movie titles, show titles, and names are used for trivia purposes and belong to their respective owners.</p>
          </section>
        </main>
        ${this.bottomNav("settings")}
      </div>
    `;
  }

  private settingRow(
    key: SettingKey,
    iconName: IconName,
    title: string,
    description: string,
  ): string {
    const enabled = this.save.settings[key];
    return `
      <button class="toggle-row" type="button" role="switch" aria-checked="${enabled}" data-action="toggle-setting" data-setting="${key}">
        <span class="setting-icon">${icon(iconName)}</span>
        <span class="setting-copy"><strong>${title}</strong><span>${description}</span></span>
        <span class="switch${enabled ? " is-on" : ""}" aria-hidden="true"><span></span></span>
      </button>
    `;
  }

  private renderHowTo(): string {
    return `
      <div class="screen page-screen">
        ${this.pageTopbar("How to play", true)}
        <main class="scroll-area page-scroll">
          <section class="page-intro howto-intro">
            <p class="kicker">THE RULES</p>
            <h1>Six takes.<br><em>One answer.</em></h1>
            <p>Every clue points to a movie, TV show, actor, actress, character, director, or film family. Fill in the answer one letter at a time.</p>
          </section>

          <section class="steps">
            <div class="step">
              <span class="step-number">01</span>
              <div><h2>Read the clue</h2><p>The category and difficulty are your trailer. The clue is the plot.</p></div>
            </div>
            <div class="step">
              <span class="step-number">02</span>
              <div><h2>Tap a letter</h2><p>Right letters fill the tiles. Wrong letters cost one of your six takes. Spaces and punctuation are free.</p></div>
            </div>
            <div class="step">
              <span class="step-number">03</span>
              <div><h2>Beat the credits</h2><p>Reveal every letter to solve the round, build a streak, and add the answer to your archive.</p></div>
            </div>
          </section>

          <section class="panel">
            <div class="section-heading compact"><div><p class="kicker">THE MATH</p><h2>Scoring</h2></div></div>
            <div class="score-table">
              <div><span>Base solve</span><strong>100</strong></div>
              <div><span>Each take left</span><strong>+25</strong></div>
              <div><span>Difficulty bonus</span><strong>+0 to +80</strong></div>
              <div><span>Hint</span><strong>−40</strong></div>
              <div><span>Daily feature</span><strong>2×</strong></div>
            </div>
            <p class="panel-note">A hint reveals the most common missing letter and never costs a take. The daily feature pays double once per day.</p>
          </section>

          <section class="panel short-panel">
            <div class="hint-line">${icon("bulb")}<p>Stuck? Use the hint. Careless? Use the backspace. There is no timer—only the streak.</p></div>
          </section>

          <button class="primary-button compact howto-button" type="button" data-action="back">
            <span class="primary-copy"><strong>Back to the lobby</strong></span>
            ${icon("arrow")}
          </button>
        </main>
      </div>
    `;
  }

  private confirmOverlay(): string {
    return `
      <div class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="reset-title">
        <div class="confirm-sheet">
          <div class="modal-icon">${icon("reset")}</div>
          <p class="kicker">START OVER</p>
          <h2 id="reset-title">Reset all progress?</h2>
          <p>This clears your stats, streaks, solved puzzles, and today's daily result. Your sound and motion settings stay put.</p>
          <div class="modal-actions">
            <button class="ghost-button" type="button" data-action="cancel-reset" data-autofocus>Cancel</button>
            <button class="danger-button" type="button" data-action="confirm-reset">Reset everything</button>
          </div>
        </div>
      </div>
    `;
  }
}
