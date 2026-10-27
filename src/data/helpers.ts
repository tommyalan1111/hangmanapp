import type { CategoryId, Difficulty, Puzzle } from "../types";

export function slugify(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function makePuzzle(
  category: CategoryId,
  answer: string,
  clue: string,
  _fact: string,
  difficulty: Difficulty,
): Puzzle {
  return {
    id: `${category}-${slugify(answer)}`,
    category,
    answer: answer.toUpperCase(),
    clue,
    difficulty,
  };
}
