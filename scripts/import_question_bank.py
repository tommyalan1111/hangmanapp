#!/usr/bin/env python3
"""Import the seven-sheet Reel Hangman question workbook into the game.

Dry run (default):
    python scripts/import_question_bank.py

Apply additions and updates:
    python scripts/import_question_bank.py --write

Also remove game puzzles that are absent from the workbook:
    python scripts/import_question_bank.py --write --delete

Rules:
- Workbook IDs are authoritative.
- Existing questions are updated by ID.
- Missing questions are reported; they are preserved unless --delete is used.
- Facts are no longer part of the game.
- Time and year answers are skipped.
- Pure-number answers become words; common Roman numerals are converted.
- Duplicate answers are allowed (the ID is the unique key).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
WORKBOOK = ROOT / "docs" / "Reel-Hangman-Question-Bank.xlsx"
ESBUILD = ROOT / "node_modules" / "esbuild" / "bin" / "esbuild"
BUNDLE = ROOT / ".tmp-question-bank-bundle.cjs"

# sheet name -> (category, export name, source file, display-name header)
SHEETS = {
    "Movies": ("movies", "MOVIES", "src/data/movies.ts", "Movie Name"),
    "TV Series": ("tv", "TV", "src/data/tv.ts", "Show Name"),
    "Actors": ("actors", "ACTORS", "src/data/actors.ts", "Actor Name"),
    "Actresses": ("actresses", "ACTRESSES", "src/data/actresses.ts", "Actress Name"),
    "Characters": ("characters", "CHARACTERS", "src/data/characters.ts", "Character Name"),
    "Directors": ("directors", "DIRECTORS", "src/data/directors.ts", "Director Name"),
    "Film Families": ("families", "FAMILIES", "src/data/families.ts", "Family Name"),
}

DIFFICULTY = {"Easy": 1, "Medium": 2, "Hard": 3}
TIME_RE = re.compile(r"^\d{1,2}:\d{2}(?:\s*[AP]M)?$", re.I)
YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")
DIGITS_RE = re.compile(r"^\d+$")
ALLOWED_RE = re.compile(r"^[A-Z0-9 '.,\-]+$")

ROMAN = {
    "I": "ONE", "II": "TWO", "III": "THREE", "IV": "FOUR", "V": "FIVE",
    "VI": "SIX", "VII": "SEVEN", "VIII": "EIGHT", "IX": "NINE", "X": "TEN",
}
UNITS = [
    "ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT",
    "NINE", "TEN", "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN",
    "SIXTEEN", "SEVENTEEN", "EIGHTEEN", "NINETEEN",
]
TENS = ["", "", "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY"]


def norm(value: str) -> str:
    return value.strip().upper()


def number_to_words(number: int) -> str:
    if number < 20:
        return UNITS[number]
    if number < 100:
        tens, remainder = divmod(number, 10)
        return TENS[tens] + (f" {UNITS[remainder]}" if remainder else "")
    if number < 1000:
        hundreds, remainder = divmod(number, 100)
        return f"{UNITS[hundreds]} HUNDRED" + (f" {number_to_words(remainder)}" if remainder else "")
    thousands, remainder = divmod(number, 1000)
    return f"{number_to_words(thousands)} THOUSAND" + (f" {number_to_words(remainder)}" if remainder else "")


def clean_answer(raw: object) -> tuple[str | None, str]:
    """Return (answer, reason); answer is None when the row should be skipped."""
    answer = norm(str(raw or ""))
    if TIME_RE.fullmatch(answer):
        return None, "time answer"
    if YEAR_RE.fullmatch(answer):
        return None, "year answer"
    if DIGITS_RE.fullmatch(answer):
        value = int(answer)
        if 1900 <= value <= 2099:
            return None, "year answer"
        return number_to_words(value), "number normalized"
    if answer in ROMAN:
        return ROMAN[answer], "roman numeral normalized"
    if answer == "BB":
        return "BEE BEE", "short answer normalized"
    if answer == "C4":
        return "C FOUR", "short answer normalized"
    return answer, ""


def load_current_puzzles() -> list[dict]:
    if not ESBUILD.exists():
        raise SystemExit(f"esbuild not found: {ESBUILD}")
    node = shutil.which("node")
    if not node:
        raise SystemExit("node was not found on PATH")
    try:
        subprocess.run(
            [node, str(ESBUILD), "src/data/index.ts", "--bundle", "--platform=node",
             "--format=cjs", f"--outfile={BUNDLE}", "--log-level=error"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        script = (
            f"const {{PUZZLES}} = require({json.dumps(str(BUNDLE))});"
            "process.stdout.write(JSON.stringify(PUZZLES));"
        )
        result = subprocess.run(
            [node, "-e", script], cwd=ROOT, check=True, capture_output=True, text=True,
        )
        return json.loads(result.stdout)
    finally:
        BUNDLE.unlink(missing_ok=True)


def entry_block(puzzle: dict) -> str:
    return (
        "  {\n"
        f"    id: {json.dumps(puzzle['id'])},\n"
        f"    category: {json.dumps(puzzle['category'])},\n"
        f"    answer: {json.dumps(puzzle['answer'], ensure_ascii=False)},\n"
        f"    clue: {json.dumps(puzzle['clue'], ensure_ascii=False)},\n"
        f"    difficulty: {puzzle['difficulty']},\n"
        "  },\n"
    )


def write_category_file(relative: str, export_name: str, puzzles: list[dict]) -> None:
    body = "".join(entry_block(puzzle) for puzzle in puzzles)
    text = (
        'import type { Puzzle } from "../types";\n\n'
        f"export const {export_name}: Puzzle[] = [\n"
        f"{body}"
        "];\n"
    )
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="rewrite the seven data files")
    parser.add_argument("--delete", action="store_true", help="remove questions absent from the workbook")
    args = parser.parse_args()

    wb = load_workbook(WORKBOOK, data_only=True)
    missing_sheets = [name for name in SHEETS if name not in wb.sheetnames]
    if missing_sheets:
        raise SystemExit(f"Workbook is missing sheets: {', '.join(missing_sheets)}")

    current = load_current_puzzles()
    current_by_id = {puzzle["id"]: puzzle for puzzle in current}

    workbook_by_id: dict[str, dict] = {}
    workbook_ids: set[str] = set()
    skipped: list[tuple[str, str, str]] = []
    normalized: list[tuple[str, str, str]] = []
    errors: list[tuple[str, str]] = []

    for sheet_name, (category, _export, _relative, _header) in SHEETS.items():
        ws = wb[sheet_name]
        for row in ws.iter_rows(min_row=2, max_col=5, values_only=True):
            if not row[0] or not row[3]:
                continue
            puzzle_id = str(row[0]).strip()
            name = str(row[1] or "").strip()
            question = str(row[2] or "").strip()
            difficulty_text = str(row[4] or "").strip()

            if puzzle_id in workbook_ids:
                errors.append((puzzle_id, "duplicate ID in workbook"))
                continue
            workbook_ids.add(puzzle_id)

            answer, reason = clean_answer(row[3])
            if answer is None:
                skipped.append((puzzle_id, str(row[3]).strip(), reason))
                continue
            if reason:
                normalized.append((puzzle_id, str(row[3]).strip(), answer, reason))

            if not question:
                errors.append((puzzle_id, "missing question"))
                continue
            if difficulty_text not in DIFFICULTY:
                errors.append((puzzle_id, f"bad difficulty: {difficulty_text!r}"))
                continue

            normalized_answer = re.sub(r"[^A-Z0-9]", "", answer)
            if not ALLOWED_RE.fullmatch(answer):
                errors.append((puzzle_id, f"unsupported characters: {answer!r}"))
                continue
            if not re.search(r"[A-Z]", answer):
                errors.append((puzzle_id, f"no letters: {answer!r}"))
                continue
            if len(normalized_answer) < 3:
                errors.append((puzzle_id, f"too short: {answer!r}"))
                continue
            if len(normalized_answer) > 32:
                errors.append((puzzle_id, f"too long ({len(normalized_answer)}): {answer!r}"))
                continue

            clue = question
            if category in {"movies", "tv"} and name and norm(name) != norm(answer):
                clue = f"{name}: {question}"

            workbook_by_id[puzzle_id] = {
                "id": puzzle_id,
                "category": category,
                "answer": answer,
                "clue": clue,
                "difficulty": DIFFICULTY[difficulty_text],
                "name": name,
            }

    new_ids = [pid for pid in workbook_by_id if pid not in current_by_id]
    common_ids = [pid for pid in workbook_by_id if pid in current_by_id]
    updated_ids = []
    for pid in common_ids:
        old = current_by_id[pid]
        new = workbook_by_id[pid]
        if (
            old["answer"] != new["answer"]
            or old["clue"] != new["clue"]
            or old["difficulty"] != new["difficulty"]
            or old["category"] != new["category"]
        ):
            updated_ids.append(pid)

    absent = [pid for pid in current_by_id if pid not in workbook_by_id]

    print(f"Workbook rows read: {len(workbook_ids)}")
    print(f"Workbook importable: {len(workbook_by_id)}")
    print(f"Current game puzzles: {len(current)}")
    print(f"New: {len(new_ids)}")
    print(f"Updated: {len(updated_ids)}")
    print(f"Removed from workbook: {len(absent)}")
    print(f"Skipped time/year rows: {len(skipped)}")
    print(f"Answers normalized: {len(normalized)}")
    if updated_ids:
        print("Updated IDs:")
        for puzzle_id in updated_ids:
            print(f"  UPDATE {puzzle_id}")

    if skipped:
        print("\nSkipped rows:")
        for puzzle_id, answer, reason in skipped:
            print(f"  SKIP {puzzle_id}: {answer!r} ({reason})")

    if normalized:
        print("\nNormalized answers:")
        for puzzle_id, before, after, reason in normalized:
            print(f"  {puzzle_id}: {before!r} -> {after!r} ({reason})")

    if absent:
        print("\nIn game but not in workbook:")
        for puzzle_id in absent:
            print(f"  ABSENT {puzzle_id}")
        if args.delete:
            print("  --delete is enabled: these will be removed.")
        else:
            print("  Preserved because --delete was not supplied.")

    if errors:
        print(f"\n{len(errors)} rows cannot be imported:")
        for puzzle_id, reason in errors:
            print(f"  ERROR {puzzle_id}: {reason}")
        print("\nNo file was changed. Fix these rows and run the script again.")
        return 1

    absent_set = set(absent) if args.delete else set()

    # Build the final arrays: workbook order first, preserved current rows last.
    final: dict[str, list[dict]] = {cfg[0]: [] for cfg in SHEETS.values()}
    for puzzle_id, puzzle in workbook_by_id.items():
        final[puzzle["category"]].append(
            {
                "id": puzzle["id"],
                "category": puzzle["category"],
                "answer": puzzle["answer"],
                "clue": puzzle["clue"],
                "difficulty": puzzle["difficulty"],
            }
        )

    if not args.delete:
        for pid, puzzle in current_by_id.items():
            if pid in workbook_by_id or pid in absent_set:
                continue
            final[puzzle["category"]].append(
                {
                    "id": puzzle["id"],
                    "category": puzzle["category"],
                    "answer": puzzle["answer"],
                    "clue": puzzle["clue"],
                    "difficulty": puzzle["difficulty"],
                }
            )

    # If --delete was requested without --write, the report already explains it.
    total = sum(len(items) for items in final.values())
    print("\nFinal counts:")
    for sheet_name, (category, _export, _relative, _header) in SHEETS.items():
        print(f"  {sheet_name}: {len(final[category])}")
    print(f"  TOTAL: {total}")

    if not args.write:
        print("\nDry run only. Re-run with --write to apply additions/updates.")
        if args.delete:
            print("--delete will also remove the ABSENT rows.")
        return 0

    for sheet_name, (category, export_name, relative, _header) in SHEETS.items():
        write_category_file(relative, export_name, final[category])
        print(f"  wrote {relative}: {len(final[category])} rows")

    print("\nNow run: npm run validate:data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
