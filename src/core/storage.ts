import type {
  CategoryId,
  DailyRecord,
  HistoryItem,
  Puzzle,
  Round,
  SaveData,
  Settings,
  Stats,
} from "../types";
import { localDateKey } from "./game";

const STORAGE_KEY = "reel-hangman-save-v1";

export function defaultSave(): SaveData {
  return {
    version: 1,
    stats: {
      played: 0,
      won: 0,
      currentStreak: 0,
      bestStreak: 0,
      points: 0,
    },
    solvedIds: [],
    recentIds: [],
    history: [],
    settings: {
      sound: true,
      haptics: true,
      reduceMotion: false,
    },
    activeRound: null,
    daily: null,
  };
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function asSettings(value: unknown): Settings {
  const base = defaultSave().settings;
  if (!value || typeof value !== "object") return base;
  const settings = value as Partial<Settings>;
  return {
    sound: typeof settings.sound === "boolean" ? settings.sound : base.sound,
    haptics: typeof settings.haptics === "boolean" ? settings.haptics : base.haptics,
    reduceMotion:
      typeof settings.reduceMotion === "boolean" ? settings.reduceMotion : base.reduceMotion,
  };
}

function asStats(value: unknown): Stats {
  const base = defaultSave().stats;
  if (!value || typeof value !== "object") return base;
  const stats = value as Partial<Stats>;
  return {
    played: Math.max(0, asNumber(stats.played, base.played)),
    won: Math.max(0, asNumber(stats.won, base.won)),
    currentStreak: Math.max(0, asNumber(stats.currentStreak, base.currentStreak)),
    bestStreak: Math.max(0, asNumber(stats.bestStreak, base.bestStreak)),
    points: Math.max(0, asNumber(stats.points, base.points)),
  };
}

function asHistory(value: unknown): HistoryItem[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is HistoryItem => Boolean(item) && typeof item === "object")
    .filter((item) => typeof item.puzzleId === "string" && typeof item.answer === "string")
    .slice(0, 20)
    .map((item) => ({
      puzzleId: item.puzzleId,
      answer: item.answer,
      category: item.category as CategoryId,
      won: Boolean(item.won),
      score: Math.max(0, asNumber(item.score)),
      at: asNumber(item.at, Date.now()),
    }));
}

function asActiveRound(value: unknown): Round | null {
  if (!value || typeof value !== "object") return null;
  const round = value as Partial<Round>;
  if (typeof round.puzzleId !== "string") return null;
  if (round.status !== "playing" && round.status !== "won" && round.status !== "lost") return null;
  if (!Array.isArray(round.guessed)) return null;
  return {
    puzzleId: round.puzzleId,
    mode: round.mode === "daily" ? "daily" : round.mode === "category" ? "category" : "quick",
    category: round.category as CategoryId,
    guessed: round.guessed.filter((letter): letter is string => typeof letter === "string"),
    wrong: Math.max(0, Math.min(6, asNumber(round.wrong))),
    hintUsed: Boolean(round.hintUsed),
    status: round.status,
    startedAt: asNumber(round.startedAt, Date.now()),
    score: Math.max(0, asNumber(round.score)),
  };
}

function asDaily(value: unknown): DailyRecord | null {
  if (!value || typeof value !== "object") return null;
  const daily = value as Partial<DailyRecord>;
  if (typeof daily.date !== "string" || typeof daily.puzzleId !== "string") return null;
  return {
    date: daily.date,
    puzzleId: daily.puzzleId,
    won: Boolean(daily.won),
    score: Math.max(0, asNumber(daily.score)),
  };
}

export function loadSave(): SaveData {
  const fallback = defaultSave();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw) as Partial<SaveData>;
    if (!parsed || typeof parsed !== "object") return fallback;
    return {
      version: 1,
      stats: asStats(parsed.stats),
      solvedIds: [...new Set(asStringArray(parsed.solvedIds))],
      recentIds: [...new Set(asStringArray(parsed.recentIds))].slice(0, 20),
      history: asHistory(parsed.history),
      settings: asSettings(parsed.settings),
      activeRound: asActiveRound(parsed.activeRound),
      daily: asDaily(parsed.daily),
    };
  } catch {
    return fallback;
  }
}

export function persistSave(data: SaveData): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {
    // The game remains playable even when storage is unavailable.
  }
}

export function saveActiveRound(data: SaveData, round: Round | null): SaveData {
  return { ...data, activeRound: round };
}

export function isDailyComplete(data: SaveData, dateKey = localDateKey()): boolean {
  return data.daily?.date === dateKey;
}

export function recordResult(data: SaveData, puzzle: Puzzle, round: Round): SaveData {
  const won = round.status === "won";
  const alreadyToday = round.mode === "daily" && data.daily?.date === localDateKey();
  const nextStreak = alreadyToday
    ? data.stats.currentStreak
    : won
      ? data.stats.currentStreak + 1
      : 0;
  const stats: Stats = {
    played: data.stats.played + (alreadyToday ? 0 : 1),
    won: data.stats.won + (won && !alreadyToday ? 1 : 0),
    currentStreak: nextStreak,
    bestStreak: Math.max(data.stats.bestStreak, nextStreak),
    points: data.stats.points + (alreadyToday ? 0 : round.score),
  };

  const solvedIds = won
    ? [...new Set([...data.solvedIds, puzzle.id])]
    : data.solvedIds;

  const history: HistoryItem[] = [
    {
      puzzleId: puzzle.id,
      answer: puzzle.answer,
      category: puzzle.category,
      won,
      score: round.mode === "daily" && alreadyToday ? 0 : round.score,
      at: Date.now(),
    },
    ...data.history,
  ].slice(0, 20);

  const recentIds = [puzzle.id, ...data.recentIds.filter((id) => id !== puzzle.id)].slice(0, 20);

  const daily: DailyRecord | null =
    round.mode === "daily" && !alreadyToday
      ? {
          date: localDateKey(),
          puzzleId: puzzle.id,
          won,
          score: round.score,
        }
      : data.daily;

  return {
    ...data,
    stats,
    solvedIds,
    history,
    recentIds,
    daily,
    activeRound: null,
  };
}

export function resetProgress(data: SaveData): SaveData {
  return {
    ...defaultSave(),
    settings: data.settings,
  };
}

export function solvedInCategory(data: SaveData, category: CategoryId): number {
  return data.solvedIds.filter((id) => id.startsWith(`${category}-`)).length;
}
