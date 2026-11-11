import csv
import re
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent
XLSX_PATH = ROOT / "actors_trivia_jon_bradley_dave.xlsx"
CSV_PATH = ROOT / "actors_trivia_jon_bradley_dave.csv"

ROWS = [
    # Jon Favreau
    ("actors-jon-favreau-1", "Jon Favreau",
     "Which MCU character does Jon Favreau play?", "Happy Hogan", "Easy"),
    ("actors-jon-favreau-2", "Jon Favreau",
     "Which MCU film did Jon Favreau direct first?", "Iron Man", "Easy"),
    ("actors-jon-favreau-3", "Jon Favreau",
     "Which Christmas comedy did Jon Favreau direct starring Will Ferrell?", "Elf", "Easy"),
    ("actors-jon-favreau-4", "Jon Favreau",
     "Which live-action Disney remake did Jon Favreau direct about Mowgli?", "The Jungle Book", "Easy"),
    ("actors-jon-favreau-5", "Jon Favreau",
     "Which photorealistic Disney remake did Jon Favreau direct?", "The Lion King", "Easy"),
    ("actors-jon-favreau-6", "Jon Favreau",
     "Which Star Wars series did Jon Favreau create?", "The Mandalorian", "Easy"),
    ("actors-jon-favreau-7", "Jon Favreau",
     "Which food-truck comedy did Jon Favreau direct and star in?", "Chef", "Easy"),
    ("actors-jon-favreau-8", "Jon Favreau",
     "Which comedy did Jon Favreau write and star in as Mike Peters?", "Swingers", "Medium"),
    ("actors-jon-favreau-9", "Jon Favreau",
     "Which college football film cast Jon Favreau as D-Bob?", "Rudy", "Medium"),
    ("actors-jon-favreau-10", "Jon Favreau",
     "Which football comedy cast Jon Favreau as Daniel Bateman?", "The Replacements", "Medium"),
    ("actors-jon-favreau-11", "Jon Favreau",
     "Which Marvel film cast Jon Favreau as Foggy Nelson?", "Daredevil", "Medium"),
    ("actors-jon-favreau-12", "Jon Favreau",
     "Which space adventure did Jon Favreau direct?", "Zathura", "Medium"),
    ("actors-jon-favreau-13", "Jon Favreau",
     "Which sci-fi Western did Jon Favreau direct?", "Cowboys & Aliens", "Medium"),
    ("actors-jon-favreau-14", "Jon Favreau",
     "Which film marked Jon Favreau's directorial debut?", "Made", "Medium"),
    ("actors-jon-favreau-15", "Jon Favreau",
     "Which Mandalorian warrior does Jon Favreau voice?", "Paz Vizsla", "Medium"),
    ("actors-jon-favreau-16", "Jon Favreau",
     "Which Clone Wars warrior does Jon Favreau voice?", "Pre Vizsla", "Medium"),
    ("actors-jon-favreau-17", "Jon Favreau",
     "Which IFC talk show did Jon Favreau host?", "Dinner for Five", "Medium"),
    ("actors-jon-favreau-18", "Jon Favreau",
     "Which cooking series does Jon Favreau host with Roy Choi?", "The Chef Show", "Easy"),
    ("actors-jon-favreau-19", "Jon Favreau",
     "Where was Jon Favreau born?", "Flushing", "Easy"),
    ("actors-jon-favreau-20", "Jon Favreau",
     "Which Disney honor did Jon Favreau receive?", "Disney Legend", "Medium"),

    # Bradley Cooper
    ("actors-bradley-cooper-1", "Bradley Cooper",
     "Which Marvel raccoon does Bradley Cooper voice?", "Rocket", "Easy"),
    ("actors-bradley-cooper-2", "Bradley Cooper",
     "Which teacher does Bradley Cooper play in The Hangover?", "Phil Wenneck", "Easy"),
    ("actors-bradley-cooper-3", "Bradley Cooper",
     "Which troubled singer does Bradley Cooper play in A Star Is Born?", "Jackson Maine", "Easy"),
    ("actors-bradley-cooper-4", "Bradley Cooper",
     "Which bipolar former teacher does Bradley Cooper play in Silver Linings Playbook?", "Pat Solitano", "Easy"),
    ("actors-bradley-cooper-5", "Bradley Cooper",
     "Which Navy SEAL does Bradley Cooper play in American Sniper?", "Chris Kyle", "Easy"),
    ("actors-bradley-cooper-6", "Bradley Cooper",
     "Which conductor does Bradley Cooper play in Maestro?", "Leonard Bernstein", "Easy"),
    ("actors-bradley-cooper-7", "Bradley Cooper",
     "Which FBI agent does Bradley Cooper play in American Hustle?", "Richie DiMaso", "Medium"),
    ("actors-bradley-cooper-8", "Bradley Cooper",
     "Which reporter does Bradley Cooper play in Alias?", "Will Tippin", "Medium"),
    ("actors-bradley-cooper-9", "Bradley Cooper",
     "Which obnoxious boyfriend does Bradley Cooper play in Wedding Crashers?", "Sack Lodge", "Medium"),
    ("actors-bradley-cooper-10", "Bradley Cooper",
     "Which writer does Bradley Cooper play in Limitless?", "Eddie Morra", "Medium"),
    ("actors-bradley-cooper-11", "Bradley Cooper",
     "Which cop does Bradley Cooper play in The Place Beyond the Pines?", "Avery Cross", "Medium"),
    ("actors-bradley-cooper-12", "Bradley Cooper",
     "Which chef does Bradley Cooper play in Burnt?", "Adam Jones", "Medium"),
    ("actors-bradley-cooper-13", "Bradley Cooper",
     "Which A-Team con man does Bradley Cooper play?", "Faceman", "Medium"),
    ("actors-bradley-cooper-14", "Bradley Cooper",
     "Which Elephant Man did Bradley Cooper play on Broadway?", "Joseph Merrick", "Medium"),
    ("actors-bradley-cooper-15", "Bradley Cooper",
     "Which Lady Gaga duet did Bradley Cooper sing?", "Shallow", "Easy"),
    ("actors-bradley-cooper-16", "Bradley Cooper",
     "Which film did Bradley Cooper produce about the Joker?", "Joker", "Easy"),
    ("actors-bradley-cooper-17", "Bradley Cooper",
     "Which People honor did Bradley Cooper receive?", "Sexiest Man Alive", "Easy"),
    ("actors-bradley-cooper-18", "Bradley Cooper",
     "Where was Bradley Cooper born?", "Abington", "Easy"),
    ("actors-bradley-cooper-19", "Bradley Cooper",
     "Which university did Bradley Cooper attend?", "Georgetown", "Easy"),
    ("actors-bradley-cooper-20", "Bradley Cooper",
     "Which actress was Bradley Cooper briefly married to?", "Jennifer Esposito", "Medium"),

    # Dave Bautista
    ("actors-dave-bautista-1", "Dave Bautista",
     "Which Marvel warrior does Dave Bautista play?", "Drax", "Easy"),
    ("actors-dave-bautista-2", "Dave Bautista",
     "Which Dune villain does Dave Bautista play?", "Rabban", "Easy"),
    ("actors-dave-bautista-3", "Dave Bautista",
     "Which Bond henchman does Dave Bautista play?", "Mr. Hinx", "Easy"),
    ("actors-dave-bautista-4", "Dave Bautista",
     "Which replicant does Dave Bautista play in the Blade Runner sequel?", "Sapper Morton", "Medium"),
    ("actors-dave-bautista-5", "Dave Bautista",
     "Which zombie-heist leader does Dave Bautista play in Army of the Dead?", "Scott Ward", "Easy"),
    ("actors-dave-bautista-6", "Dave Bautista",
     "Which character does Dave Bautista play in Glass Onion?", "Duke Cody", "Easy"),
    ("actors-dave-bautista-7", "Dave Bautista",
     "Which character does Dave Bautista play in Knock at the Cabin?", "Leonard", "Medium"),
    ("actors-dave-bautista-8", "Dave Bautista",
     "Which character does Dave Bautista play in The Man with the Iron Fists?", "Brass Body", "Medium"),
    ("actors-dave-bautista-9", "Dave Bautista",
     "Which Muay Thai champion does Dave Bautista play in the Kickboxer remake?", "Tong Po", "Medium"),
    ("actors-dave-bautista-10", "Dave Bautista",
     "Which LAPD detective does Dave Bautista play in Stuber?", "Vic Manning", "Medium"),
    ("actors-dave-bautista-11", "Dave Bautista",
     "Which former soldier does Dave Bautista play in Final Score?", "Michael Knox", "Medium"),
    ("actors-dave-bautista-12", "Dave Bautista",
     "What is Dave Bautista's WWE ring name?", "Batista", "Easy"),
    ("actors-dave-bautista-13", "Dave Bautista",
     "What is Batista's finishing move?", "Batista Bomb", "Easy"),
    ("actors-dave-bautista-14", "Dave Bautista",
     "Which wrestling stable did Batista join with Triple H?", "Evolution", "Medium"),
    ("actors-dave-bautista-15", "Dave Bautista",
     "Which battle royal did Batista win twice?", "Royal Rumble", "Easy"),
    ("actors-dave-bautista-16", "Dave Bautista",
     "Which wrestler did Batista face in his first WrestleMania main event?", "Triple H", "Medium"),
    ("actors-dave-bautista-17", "Dave Bautista",
     "Where was Dave Bautista born?", "Washington, D.C.", "Easy"),
    ("actors-dave-bautista-18", "Dave Bautista",
     "Which ancestry does Dave Bautista have from his father?", "Filipino", "Medium"),
    ("actors-dave-bautista-19", "Dave Bautista",
     "Which job did Dave Bautista have before wrestling?", "Bouncer", "Medium"),
    ("actors-dave-bautista-20", "Dave Bautista",
     "Which Marvel team does Drax belong to?", "Guardians of the Galaxy", "Easy"),
]

SOURCES = [
    ("Jon Favreau", "Wikipedia — Jon Favreau", "https://en.wikipedia.org/wiki/Jon_Favreau", "Biography and filmography"),
    ("Jon Favreau", "Wikipedia — Iron Man", "https://en.wikipedia.org/wiki/Iron_Man_(2008_film)", "Happy Hogan and directing"),
    ("Jon Favreau", "Wikipedia — Elf", "https://en.wikipedia.org/wiki/Elf_(film)", "Directing"),
    ("Jon Favreau", "Wikipedia — The Mandalorian", "https://en.wikipedia.org/wiki/The_Mandalorian", "Creation and Paz Vizsla"),
    ("Jon Favreau", "Wikipedia — Chef", "https://en.wikipedia.org/wiki/Chef_(2014_film)", "Directing and starring"),
    ("Jon Favreau", "Wikipedia — Swingers", "https://en.wikipedia.org/wiki/Swingers_(1996_film)", "Mike Peters"),
    ("Bradley Cooper", "Wikipedia — Bradley Cooper", "https://en.wikipedia.org/wiki/Bradley_Cooper", "Biography and filmography"),
    ("Bradley Cooper", "Wikipedia — The Hangover", "https://en.wikipedia.org/wiki/The_Hangover", "Phil Wenneck"),
    ("Bradley Cooper", "Wikipedia — Silver Linings Playbook", "https://en.wikipedia.org/wiki/Silver_Linings_Playbook", "Pat Solitano"),
    ("Bradley Cooper", "Wikipedia — A Star Is Born", "https://en.wikipedia.org/wiki/A_Star_Is_Born_(2018_film)", "Jackson Maine and Shallow"),
    ("Bradley Cooper", "Wikipedia — Maestro", "https://en.wikipedia.org/wiki/Maestro_(2023_film)", "Leonard Bernstein"),
    ("Bradley Cooper", "Wikipedia — American Sniper", "https://en.wikipedia.org/wiki/American_Sniper", "Chris Kyle"),
    ("Dave Bautista", "Wikipedia — Dave Bautista", "https://en.wikipedia.org/wiki/Dave_Bautista", "Biography and filmography"),
    ("Dave Bautista", "Wikipedia — Dune", "https://en.wikipedia.org/wiki/Dune_(2021_film)", "Rabban"),
    ("Dave Bautista", "Wikipedia — Spectre", "https://en.wikipedia.org/wiki/Spectre_(2015_film)", "Mr. Hinx"),
    ("Dave Bautista", "Wikipedia — Glass Onion", "https://en.wikipedia.org/wiki/Glass_Onion:_A_Knives_Out_Mystery", "Duke Cody"),
    ("Dave Bautista", "Wikipedia — Army of the Dead", "https://en.wikipedia.org/wiki/Army_of_the_Dead", "Scott Ward"),
    ("Dave Bautista", "Wikipedia — Final Score", "https://en.wikipedia.org/wiki/Final_Score_(2018_film)", "Michael Knox"),
]

HEADERS = ["ID", "Actor Name", "Question", "Answer", "Difficulty"]
ACTORS = ["Jon Favreau", "Bradley Cooper", "Dave Bautista"]


def slug_for(actor):
    return actor.lower().replace(" ", "-")


def validate(rows):
    assert len(rows) == 60, len(rows)
    ids = [row[0] for row in rows]
    assert len(ids) == len(set(ids)), "Duplicate IDs"

    for actor in ACTORS:
        actor_rows = [row for row in rows if row[1] == actor]
        assert len(actor_rows) == 20, (actor, len(actor_rows))
        expected_ids = [f"actors-{slug_for(actor)}-{i}" for i in range(1, 21)]
        assert [row[0] for row in actor_rows] == expected_ids, actor

    answers = [row[3] for row in rows]
    lowered = [answer.casefold() for answer in answers]
    assert len(lowered) == len(set(lowered)), "Duplicate answers"
    assert len({row[2] for row in rows}) == 60, "Duplicate questions"

    for id_, actor, question, answer, difficulty in rows:
        assert answer.strip() == answer and answer, (id_, answer)
        assert len(answer.split()) <= 5, (id_, answer, len(answer.split()))
        assert len(answer) <= 30, (id_, answer, len(answer))
        assert re.search(r"\b(?:19|20)\d{2}\b", answer) is None, (id_, answer)
        assert answer.isascii(), (id_, answer)
        assert question.endswith("?"), (id_, question)
        assert difficulty in {"Easy", "Medium"}, (id_, difficulty)
        assert actor in ACTORS, (id_, actor)


def style_header(sheet, widths):
    header_fill = PatternFill("solid", fgColor="171717")
    header_font = Font(name="Arial", size=11, bold=True, color="F4C95D")
    bottom = Border(bottom=Side(style="medium", color="C9A227"))
    for col, width in enumerate(widths, start=1):
        cell = sheet.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="left", vertical="center")
        cell.border = bottom
        sheet.column_dimensions[get_column_letter(col)].width = width
    sheet.row_dimensions[1].height = 32


def build_workbook():
    wb = Workbook()
    ws = wb.active
    ws.title = "Trivia"
    ws.sheet_properties.tabColor = "C9A227"
    ws.sheet_view.showGridLines = False

    ws.append(HEADERS)
    for row in ROWS:
        ws.append(row)
    style_header(ws, [25, 20, 100, 26, 11])

    thin = Side(style="thin", color="E4E0D8")
    for r in range(2, len(ROWS) + 2):
        band = "FFFFFF" if r % 2 == 0 else "FBF9F4"
        for c in range(1, 6):
            cell = ws.cell(row=r, column=c)
            cell.fill = PatternFill("solid", fgColor=band)
            cell.border = Border(bottom=thin, right=thin)
            cell.alignment = Alignment(
                vertical="top",
                horizontal="center" if c in (1, 5) else "left",
                wrap_text=(c == 3),
            )
            cell.font = Font(
                name="Arial",
                size=10,
                color="1C1C1C",
                bold=(c == 2),
            )
        ws.cell(row=r, column=1).font = Font(name="Arial", size=9, color="7A7468")
        ws.cell(row=r, column=4).font = Font(name="Arial", size=10, bold=True, color="111111")
        diff = ws.cell(row=r, column=5)
        if diff.value == "Easy":
            diff.font = Font(name="Arial", size=9, bold=True, color="1B6B44")
            diff.fill = PatternFill("solid", fgColor="EAF6EE")
        else:
            diff.font = Font(name="Arial", size=9, bold=True, color="8A5200")
            diff.fill = PatternFill("solid", fgColor="FFF2D8")
        ws.row_dimensions[r].height = 34

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:E{len(ROWS) + 1}"
    ws.print_area = f"A1:E{len(ROWS) + 1}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "1:1"

    src = wb.create_sheet("Sources")
    src.sheet_properties.tabColor = "7A7468"
    src.sheet_view.showGridLines = False
    src.append(["Actor", "Source", "URL", "Used For"])
    for row in SOURCES:
        src.append(row)
    style_header(src, [20, 42, 84, 38])
    for r in range(2, len(SOURCES) + 2):
        band = "FFFFFF" if r % 2 == 0 else "FBF9F4"
        for c in range(1, 5):
            cell = src.cell(row=r, column=c)
            cell.fill = PatternFill("solid", fgColor=band)
            cell.border = Border(bottom=thin, right=thin)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.font = Font(name="Arial", size=10, color="1C1C1C")
        src.cell(row=r, column=2).font = Font(name="Arial", size=10, bold=True, color="1C1C1C")
        url_cell = src.cell(row=r, column=3)
        url_cell.hyperlink = url_cell.value
        url_cell.font = Font(name="Arial", size=9, color="0563C1", underline="single")
        src.row_dimensions[r].height = 30
    src.freeze_panes = "A2"
    src.auto_filter.ref = f"A1:D{len(SOURCES) + 1}"

    notes = wb.create_sheet("Read Me")
    notes.sheet_properties.tabColor = "C9A227"
    notes.sheet_view.showGridLines = False
    notes.column_dimensions["A"].width = 24
    notes.column_dimensions["B"].width = 68
    notes["A1"] = "Actor Trivia — 60 Questions"
    notes["A1"].font = Font(name="Arial", size=18, bold=True, color="171717")
    notes["A2"] = "20 questions each for Jon Favreau, Bradley Cooper, and Dave Bautista."
    notes["A2"].font = Font(name="Arial", size=11, color="5B574E")
    notes.merge_cells("A1:B1")
    notes.merge_cells("A2:B2")

    checks = [
        ("Total questions", "60"),
        ("Questions per actor", "20"),
        ("IDs", "Restart at 1 for each actor"),
        ("Unique answers", "Yes — all 60"),
        ("Answer length", "1–5 words and ≤30 characters"),
        ("Year rule", "No answer contains a year"),
        ("Language rule", "All answers are English/ASCII"),
        ("Difficulty", "Easy or Medium"),
    ]
    for i, (label, value) in enumerate(checks, start=4):
        notes.cell(row=i, column=1, value=label)
        notes.cell(row=i, column=2, value=value)
        notes.cell(row=i, column=1).font = Font(name="Arial", size=10, bold=True, color="171717")
        notes.cell(row=i, column=2).font = Font(name="Arial", size=10, color="3D3A33")
        notes.cell(row=i, column=1).fill = PatternFill("solid", fgColor="F4EFE2")
        notes.cell(row=i, column=2).fill = PatternFill("solid", fgColor="FBF9F4")
        notes.cell(row=i, column=1).border = Border(bottom=thin, right=thin)
        notes.cell(row=i, column=2).border = Border(bottom=thin, right=thin)
        notes.row_dimensions[i].height = 24

    notes["A13"] = "Research"
    notes["A13"].font = Font(name="Arial", size=12, bold=True, color="171717")
    notes["A14"] = (
        "Facts were checked against the actors' Wikipedia filmographies and the linked "
        "production/character pages. Source links are on the Sources sheet."
    )
    notes["A14"].alignment = Alignment(wrap_text=True, vertical="top")
    notes["A14"].font = Font(name="Arial", size=10, color="3D3A33")
    notes.merge_cells("A14:B14")
    notes.row_dimensions[14].height = 48

    wb.properties.title = "Actor Trivia — Jon Favreau, Bradley Cooper, Dave Bautista"
    wb.properties.subject = "60 researched actor trivia questions"
    wb.properties.creator = "DeepSeek Harness"
    wb.save(XLSX_PATH)

    with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADERS)
        writer.writerows(ROWS)


def verify_saved():
    wb = load_workbook(XLSX_PATH, data_only=False)
    assert wb.sheetnames == ["Trivia", "Sources", "Read Me"], wb.sheetnames
    ws = wb["Trivia"]
    assert ws.max_row == 61 and ws.max_column == 5, (ws.max_row, ws.max_column)
    headers = [ws.cell(row=1, column=c).value for c in range(1, 6)]
    assert headers == HEADERS, headers

    saved_rows = [
        tuple(ws.cell(row=r, column=c).value for c in range(1, 6))
        for r in range(2, 62)
    ]
    assert saved_rows == ROWS
    assert ws.freeze_panes == "A2"
    assert ws.auto_filter.ref == "A1:E61"
    assert wb["Sources"].max_row == len(SOURCES) + 1
    assert wb["Read Me"]["B4"].value == "60"
    wb.close()


if __name__ == "__main__":
    validate(ROWS)
    build_workbook()
    verify_saved()
    print(f"Built {XLSX_PATH.name} and {CSV_PATH.name}")
    print("Validated: 60 rows, 20 per actor, unique answers, <=5 words, <=30 chars, no years, ASCII only.")
