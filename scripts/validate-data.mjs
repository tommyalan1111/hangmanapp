import { build } from "esbuild";
import { pathToFileURL } from "node:url";
import { mkdir, rm } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const outDir = path.join(root, ".tmp");
const outFile = path.join(outDir, "puzzles.mjs");

await mkdir(outDir, { recursive: true });
await build({
  entryPoints: [path.join(root, "src/data/index.ts")],
  bundle: true,
  format: "esm",
  platform: "node",
  outfile: outFile,
  logLevel: "silent",
});

const { PUZZLES, CATEGORY_COUNT } = await import(
  pathToFileURL(outFile).href + `?v=${Date.now()}`
);

const errors = [];
const warnings = [];
const seenIds = new Set();
const seenAnswers = new Map();
const allowed = /^[A-Z0-9 '.,\-]+$/;

for (const puzzle of PUZZLES) {
  if (seenIds.has(puzzle.id)) errors.push(`Duplicate id: ${puzzle.id}`);
  seenIds.add(puzzle.id);

  const normalized = puzzle.answer.toUpperCase().replace(/[^A-Z0-9]/g, "");
  if (normalized.length < 3) errors.push(`Too short: ${puzzle.answer}`);
  if (normalized.length > 32) warnings.push(`Long answer (${normalized.length}): ${puzzle.answer}`);
  if (!allowed.test(puzzle.answer)) errors.push(`Unsupported characters: ${puzzle.answer}`);
  if (!/[A-Z]/.test(puzzle.answer)) errors.push(`No letters: ${puzzle.answer}`);
  if (puzzle.answer !== puzzle.answer.toUpperCase()) errors.push(`Not uppercase: ${puzzle.answer}`);

  const previous = seenAnswers.get(normalized);
  if (previous) {
    warnings.push(`Duplicate answer: "${puzzle.answer}" (${puzzle.category}) and "${previous.answer}" (${previous.category})`);
  } else {
    seenAnswers.set(normalized, puzzle);
  }

  if (puzzle.clue.length < 25) warnings.push(`Short clue: ${puzzle.answer}`);
  if (![1, 2, 3].includes(puzzle.difficulty)) errors.push(`Bad difficulty: ${puzzle.answer}`);
}

const total = PUZZLES.length;
console.log(`Puzzle bank: ${total} entries`);
for (const [category, count] of Object.entries(CATEGORY_COUNT)) {
  console.log(`  ${category.padEnd(11)} ${String(count).padStart(3)}`);
}

if (warnings.length) {
  console.log(`\n${warnings.length} warnings:`);
  for (const warning of warnings) console.log(`  - ${warning}`);
}

if (errors.length) {
  console.error(`\n${errors.length} errors:`);
  for (const error of errors) console.error(`  - ${error}`);
  await rm(outDir, { recursive: true, force: true });
  process.exitCode = 1;
} else {
  await rm(outDir, { recursive: true, force: true });
  console.log("\nPuzzle bank is valid.");
}
