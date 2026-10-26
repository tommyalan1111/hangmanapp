import type { CategoryId, GameMode, Puzzle, Round } from "../types";

export const MAX_LIVES = 6;
export const KEY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"] as const;

export function normalizeAnswer(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toUpperCase();
}

export function answerLetters(answer: string): string[] {
  return Array.from(new Set(normalizeAnswer(answer).replace(/[^A-Z]/g, "").split("")));
}

export function isPunctuation(char: string): boolean {
  return !/[A-Z0-9]/.test(normalizeAnswer(char));
}

export function displayChar(char: string): string {
  return normalizeAnswer(char);
}

export function isPuzzleSolved(puzzle: Puzzle, guessed: readonly string[]): boolean {
  const set = new Set(guessed);
  return answerLetters(puzzle.answer).every((letter) => set.has(letter));
}

export function livesLeft(round: Round): number {
  return Math.max(0, MAX_LIVES - round.wrong);
}

export function createRound(puzzle: Puzzle, mode: GameMode): Round {
  return {
    puzzleId: puzzle.id,
    mode,
    category: puzzle.category,
    guessed: [],
    wrong: 0,
    hintsUsed: 0,
    status: "playing",
    startedAt: Date.now(),
    score: 0,
  };
}

export function scoreRound(puzzle: Puzzle, round: Round): number {
  if (round.status !== "won") return 0;
  const base = 100 + livesLeft(round) * 25 + (puzzle.difficulty - 1) * 40;
  const multiplier = round.mode === "daily" ? 2 : 1;
  return Math.max(25, base) * multiplier;
}

function settle(puzzle: Puzzle, next: Round): Round {
  if (isPuzzleSolved(puzzle, next.guessed)) {
    next.status = "won";
    next.score = scoreRound(puzzle, next);
  } else if (next.wrong >= MAX_LIVES) {
    next.status = "lost";
    next.score = 0;
  }
  return next;
}

export function guessLetter(puzzle: Puzzle, round: Round, letter: string): Round {
  const clean = letter.toUpperCase();
  if (round.status !== "playing") return round;
  if (!/^[A-Z]$/.test(clean)) return round;
  if (round.guessed.includes(clean)) return round;

  const next: Round = {
    ...round,
    guessed: [...round.guessed, clean],
  };

  if (!normalizeAnswer(puzzle.answer).includes(clean)) {
    next.wrong = Math.min(MAX_LIVES, next.wrong + 1);
  }

  return settle(puzzle, next);
}

export function revealHint(puzzle: Puzzle, round: Round): Round {
  if (round.status !== "playing") return round;

  const guessed = new Set(round.guessed);
  const remaining = answerLetters(puzzle.answer).filter((letter) => !guessed.has(letter));
  if (remaining.length === 0) return round;

  const frequencies = new Map<string, number>();
  for (const char of normalizeAnswer(puzzle.answer)) {
    if (/[A-Z]/.test(char) && remaining.includes(char)) {
      frequencies.set(char, (frequencies.get(char) ?? 0) + 1);
    }
  }

  const [choice] = [...frequencies.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0];
  const next: Round = {
    ...round,
    guessed: [...round.guessed, choice],
    hintsUsed: round.hintsUsed + 1,
  };

  return settle(puzzle, next);
}

export function isCorrectGuess(puzzle: Puzzle, letter: string): boolean {
  return normalizeAnswer(puzzle.answer).includes(letter.toUpperCase());
}

export function letterState(
  puzzle: Puzzle,
  round: Round,
  letter: string,
): "unused" | "correct" | "wrong" {
  if (!round.guessed.includes(letter)) return "unused";
  return isCorrectGuess(puzzle, letter) ? "correct" : "wrong";
}

function hashString(value: string): number {
  let hash = 2166136261;
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

export function localDateKey(date = new Date()): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function dailyPuzzle(puzzles: readonly Puzzle[], dateKey = localDateKey()): Puzzle {
  const pool = puzzles.filter((puzzle) => puzzle.difficulty >= 2);
  const index = hashString(`reel-daily-${dateKey}`) % pool.length;
  return pool[index];
}

export interface PickOptions {
  category?: CategoryId;
  mode: GameMode;
  solvedIds: ReadonlySet<string>;
  recentIds: readonly string[];
  dateKey?: string;
}

export function pickPuzzle(puzzles: readonly Puzzle[], options: PickOptions): Puzzle {
  if (options.mode === "daily") {
    const daily = dailyPuzzle(puzzles, options.dateKey);
    return daily;
  }

  const inCategory = options.category
    ? puzzles.filter((puzzle) => puzzle.category === options.category)
    : puzzles;
  const unsolved = inCategory.filter((puzzle) => !options.solvedIds.has(puzzle.id));
  const fresh = unsolved.filter((puzzle) => !options.recentIds.includes(puzzle.id));

  let pool: readonly Puzzle[] = fresh;
  if (pool.length === 0) pool = unsolved;
  if (pool.length === 0) {
    pool = inCategory.filter((puzzle) => !options.recentIds.includes(puzzle.id));
  }
  if (pool.length === 0) pool = inCategory;

  return pool[Math.floor(Math.random() * pool.length)];
}
