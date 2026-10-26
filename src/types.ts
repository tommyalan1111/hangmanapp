export type CategoryId =
  | "movies"
  | "tv"
  | "actors"
  | "actresses"
  | "characters"
  | "directors"
  | "families";

export type Difficulty = 1 | 2 | 3;

export type GameMode = "quick" | "category" | "daily";

export interface Category {
  id: CategoryId;
  name: string;
  tagline: string;
  description: string;
  icon: IconName;
  accent: string;
}

export type IconName =
  | "clapper"
  | "tv"
  | "actor"
  | "actress"
  | "mask"
  | "director"
  | "family"
  | "play"
  | "arrow"
  | "back"
  | "close"
  | "spark"
  | "trophy"
  | "settings"
  | "home"
  | "chart"
  | "sound"
  | "mute"
  | "haptic"
  | "motion"
  | "bulb"
  | "calendar"
  | "check"
  | "ticket"
  | "heart"
  | "lock"
  | "info"
  | "reset"
  | "share";

export interface Puzzle {
  id: string;
  category: CategoryId;
  answer: string;
  clue: string;
  fact: string;
  difficulty: Difficulty;
}

export interface Round {
  puzzleId: string;
  mode: GameMode;
  category: CategoryId;
  guessed: string[];
  wrong: number;
  hintsUsed: number;
  status: "playing" | "won" | "lost";
  startedAt: number;
  score: number;
}

export interface Stats {
  played: number;
  won: number;
  currentStreak: number;
  bestStreak: number;
  points: number;
}

export interface HistoryItem {
  puzzleId: string;
  answer: string;
  category: CategoryId;
  won: boolean;
  score: number;
  at: number;
}

export interface Settings {
  sound: boolean;
  haptics: boolean;
  reduceMotion: boolean;
}

export interface DailyRecord {
  date: string;
  puzzleId: string;
  won: boolean;
  score: number;
}

export interface SaveData {
  version: 1;
  stats: Stats;
  solvedIds: string[];
  recentIds: string[];
  history: HistoryItem[];
  settings: Settings;
  activeRound: Round | null;
  daily: DailyRecord | null;
  /** Cached store entitlement; restored from the store at startup. */
  removeAds: boolean;
}
