import type { CategoryId, Puzzle } from "../types";
import { ACTORS } from "./actors";
import { ACTRESSES } from "./actresses";
import { CHARACTERS } from "./characters";
import { DIRECTORS } from "./directors";
import { FAMILIES } from "./families";
import { MOVIES } from "./movies";
import { TV } from "./tv";

export const PUZZLES: Puzzle[] = [
  ...MOVIES,
  ...TV,
  ...ACTORS,
  ...ACTRESSES,
  ...CHARACTERS,
  ...DIRECTORS,
  ...FAMILIES,
];

export const PUZZLE_MAP = new Map(PUZZLES.map((puzzle) => [puzzle.id, puzzle]));

export const CATEGORY_COUNT = PUZZLES.reduce(
  (counts, puzzle) => {
    counts[puzzle.category] += 1;
    return counts;
  },
  {
    movies: 0,
    tv: 0,
    actors: 0,
    actresses: 0,
    characters: 0,
    directors: 0,
    families: 0,
  } satisfies Record<CategoryId, number>,
);

export const CATEGORY_PUZZLES = PUZZLES.reduce(
  (groups, puzzle) => {
    groups[puzzle.category].push(puzzle);
    return groups;
  },
  {
    movies: [],
    tv: [],
    actors: [],
    actresses: [],
    characters: [],
    directors: [],
    families: [],
  } as Record<CategoryId, Puzzle[]>,
);
