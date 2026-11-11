import csv
import re
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent
XLSX_PATH = ROOT / "actors_trivia_wyatt_david_kit.xlsx"
CSV_PATH = ROOT / "actors_trivia_wyatt_david_kit.csv"

ROWS = [
    # Wyatt Russell
    ("actors-wyatt-russell-1", "Wyatt Russell",
     "Which MCU character does Wyatt Russell play in Thunderbolts*?", "John Walker", "Easy"),
    ("actors-wyatt-russell-2", "Wyatt Russell",
     "Which alias does John Walker adopt after losing the Captain America mantle?", "U.S. Agent", "Easy"),
    ("actors-wyatt-russell-3", "Wyatt Russell",
     "Which character does Wyatt Russell play in 22 Jump Street?", "Zook Haythe", "Easy"),
    ("actors-wyatt-russell-4", "Wyatt Russell",
     "Which Richard Linklater college-baseball comedy casts Wyatt Russell as Charlie Willoughby?", "Everybody Wants Some!!", "Medium"),
    ("actors-wyatt-russell-5", "Wyatt Russell",
     "What is the name of the tough paratrooper Wyatt Russell plays in Overlord?", "Lewis Ford", "Medium"),
    ("actors-wyatt-russell-6", "Wyatt Russell",
     "Which Black Mirror episode casts Wyatt Russell as a gamer testing a VR horror game?", "Playtest", "Easy"),
    ("actors-wyatt-russell-7", "Wyatt Russell",
     "What is the name of the secret fraternal order Dud joins in Lodge 49?", "Order of the Lynx", "Medium"),
    ("actors-wyatt-russell-8", "Wyatt Russell",
     "Which Monarch: Legacy of Monsters character does Wyatt Russell play as a young man?", "Lee Shaw", "Easy"),
    ("actors-wyatt-russell-9", "Wyatt Russell",
     "Which real-life Lafferty brother does Wyatt Russell play in Under the Banner of Heaven?", "Dan Lafferty", "Medium"),
    ("actors-wyatt-russell-10", "Wyatt Russell",
     "What is the name of the father who moves his family into a haunted pool in Night Swim?", "Ray Waller", "Easy"),
    ("actors-wyatt-russell-11", "Wyatt Russell",
     "Which character does Wyatt Russell play in Ingrid Goes West?", "Ezra O'Keefe", "Medium"),
    ("actors-wyatt-russell-12", "Wyatt Russell",
     "Who does Wyatt Russell play in Table 19?", "Teddy", "Medium"),
    ("actors-wyatt-russell-13", "Wyatt Russell",
     "Which hockey captain does Wyatt Russell play in Goon: Last of the Enforcers?", "Anders Cain", "Medium"),
    ("actors-wyatt-russell-14", "Wyatt Russell",
     "What dark family secret is Deputy Anders investigating in We Are What We Are?", "Cannibalism", "Medium"),
    ("actors-wyatt-russell-15", "Wyatt Russell",
     "Which character does Wyatt Russell play in Cold in July?", "Freddy Russell", "Medium"),
    ("actors-wyatt-russell-16", "Wyatt Russell",
     "Who does Wyatt Russell play in The Woman in the Window?", "David Winter", "Medium"),
    ("actors-wyatt-russell-17", "Wyatt Russell",
     "Which character does Wyatt Russell play in Love and Honor?", "Topher Lincoln", "Medium"),
    ("actors-wyatt-russell-18", "Wyatt Russell",
     "Which sport did Wyatt Russell play professionally before acting?", "Ice hockey", "Easy"),
    ("actors-wyatt-russell-19", "Wyatt Russell",
     "Which famous actress is Wyatt Russell's mother?", "Goldie Hawn", "Easy"),
    ("actors-wyatt-russell-20", "Wyatt Russell",
     "Which canned cocktail brand did Wyatt Russell co-found?", "Lake Hour", "Medium"),

    # David Harbour
    ("actors-david-harbour-1", "David Harbour",
     "Which Netflix series turned David Harbour into Chief Jim Hopper?", "Stranger Things", "Easy"),
    ("actors-david-harbour-2", "David Harbour",
     "What is Hopper's job in Hawkins, Indiana?", "Hawkins police chief", "Easy"),
    ("actors-david-harbour-3", "David Harbour",
     "What is the name of Hopper's daughter who died of cancer?", "Sara Hopper", "Medium"),
    ("actors-david-harbour-4", "David Harbour",
     "What is Eleven's birth name, which Hopper discovers?", "Jane Ives", "Medium"),
    ("actors-david-harbour-5", "David Harbour",
     "Which comic-book demon does David Harbour play in the Hellboy reboot?", "Hellboy", "Easy"),
    ("actors-david-harbour-6", "David Harbour",
     "Which Russian superhero does David Harbour play in Black Widow?", "Red Guardian", "Easy"),
    ("actors-david-harbour-7", "David Harbour",
     "Which Black Widow assassin is Red Guardian's younger adoptive daughter?", "Yelena Belova", "Medium"),
    ("actors-david-harbour-8", "David Harbour",
     "What is Santa's Viking name in Violent Night?", "Nicomund the Red", "Medium"),
    ("actors-david-harbour-9", "David Harbour",
     "What is the name of Santa's lost Viking war hammer in Violent Night?", "Skullcrusher", "Easy"),
    ("actors-david-harbour-10", "David Harbour",
     "What is the name of David Harbour's racing mentor in Gran Turismo?", "Jack Salter", "Easy"),
    ("actors-david-harbour-11", "David Harbour",
     "Which DC monster does David Harbour voice in Creature Commandos?", "Eric Frankenstein", "Medium"),
    ("actors-david-harbour-12", "David Harbour",
     "Which CIA agent does David Harbour play in Quantum of Solace?", "Gregg Beam", "Medium"),
    ("actors-david-harbour-13", "David Harbour",
     "Which Revolutionary Road character does David Harbour play?", "Shep Campbell", "Medium"),
    ("actors-david-harbour-14", "David Harbour",
     "Which ACN host does David Harbour play in The Newsroom?", "Elliot Hirsch", "Medium"),
    ("actors-david-harbour-15", "David Harbour",
     "Which FBI agent does David Harbour play in Black Mass?", "John Morris", "Medium"),
    ("actors-david-harbour-16", "David Harbour",
     "Which character does David Harbour play in Suicide Squad?", "Dexter Tolliver", "Medium"),
    ("actors-david-harbour-17", "David Harbour",
     "What is David Harbour's role in Extraction?", "Gaspar", "Medium"),
    ("actors-david-harbour-18", "David Harbour",
     "Which Brokeback Mountain character does David Harbour play?", "Randall Malone", "Medium"),
    ("actors-david-harbour-19", "David Harbour",
     "Which Ivy League college did David Harbour attend?", "Dartmouth", "Easy"),
    ("actors-david-harbour-20", "David Harbour",
     "Which British singer did David Harbour marry in Las Vegas?", "Lily Allen", "Easy"),

    # Kit Connor
    ("actors-kit-connor-1", "Kit Connor",
     "Which Heartstopper character does Kit Connor play?", "Nick Nelson", "Easy"),
    ("actors-kit-connor-2", "Kit Connor",
     "Which sport does Nick Nelson play in Heartstopper?", "Rugby", "Easy"),
    ("actors-kit-connor-3", "Kit Connor",
     "What is the name of Nick Nelson's older brother?", "David Nelson", "Medium"),
    ("actors-kit-connor-4", "Kit Connor",
     "Which Oscar-winning actress plays Nick Nelson's mother?", "Olivia Colman", "Easy"),
    ("actors-kit-connor-5", "Kit Connor",
     "Which actor plays Nick's boyfriend Charlie Spring?", "Joe Locke", "Easy"),
    ("actors-kit-connor-6", "Kit Connor",
     "Who created the Heartstopper graphic novels?", "Alice Oseman", "Easy"),
    ("actors-kit-connor-7", "Kit Connor",
     "Which school do Nick and Charlie attend?", "Truham Grammar", "Easy"),
    ("actors-kit-connor-8", "Kit Connor",
     "Which music legend does Kit Connor play as a teenager in Rocketman?", "Elton John", "Easy"),
    ("actors-kit-connor-9", "Kit Connor",
     "Which daemon does Kit Connor voice in His Dark Materials?", "Pantalaimon", "Medium"),
    ("actors-kit-connor-10", "Kit Connor",
     "Which gosling does Kit Connor voice in The Wild Robot?", "Brightbill", "Easy"),
    ("actors-kit-connor-11", "Kit Connor",
     "Which character does Kit Connor play in Little Joe?", "Joe Woodard", "Medium"),
    ("actors-kit-connor-12", "Kit Connor",
     "Which character does Kit Connor play in Get Santa?", "Tom Anderson", "Medium"),
    ("actors-kit-connor-13", "Kit Connor",
     "Which War & Peace character does Kit Connor play?", "Petya Rostov", "Medium"),
    ("actors-kit-connor-14", "Kit Connor",
     "Which character does Kit Connor play in The Mercy?", "Simon Crowhurst", "Medium"),
    ("actors-kit-connor-15", "Kit Connor",
     "Which Slaughterhouse Rulez character does Kit Connor play?", "Wootton", "Medium"),
    ("actors-kit-connor-16", "Kit Connor",
     "Who played Juliet opposite Kit Connor on Broadway?", "Rachel Zegler", "Easy"),
    ("actors-kit-connor-17", "Kit Connor",
     "Which character does Kit Connor voice in A Plague Tale: Requiem?", "Lucas", "Medium"),
    ("actors-kit-connor-18", "Kit Connor",
     "Which Heartstopper role did Kit Connor originally audition for?", "Charlie Spring", "Medium"),
    ("actors-kit-connor-19", "Kit Connor",
     "Which London borough was Kit Connor born in?", "Croydon", "Easy"),
    ("actors-kit-connor-20", "Kit Connor",
     "What is Kit Connor's middle name?", "Sebastian", "Easy"),
]

SOURCES = [
    ("Wyatt Russell", "Wikipedia — Wyatt Russell", "https://en.wikipedia.org/wiki/Wyatt_Russell", "Biography and filmography"),
    ("Wyatt Russell", "Wikipedia — Thunderbolts*", "https://en.wikipedia.org/wiki/Thunderbolts*", "John Walker / U.S. Agent"),
    ("Wyatt Russell", "Wikipedia — Lodge 49", "https://en.wikipedia.org/wiki/Lodge_49", "Dud Dudley"),
    ("David Harbour", "Wikipedia — David Harbour", "https://en.wikipedia.org/wiki/David_Harbour", "Biography and filmography"),
    ("David Harbour", "Wikipedia — Jim Hopper", "https://en.wikipedia.org/wiki/Jim_Hopper_(Stranger_Things)", "Hopper details"),
    ("David Harbour", "Wikipedia — Violent Night", "https://en.wikipedia.org/wiki/Violent_Night", "Santa details"),
    ("David Harbour", "Wikipedia — The Newsroom", "https://en.wikipedia.org/wiki/The_Newsroom_(American_TV_series)", "Elliot Hirsch"),
    ("David Harbour", "Wikipedia — Black Widow", "https://en.wikipedia.org/wiki/Black_Widow_(2021_film)", "Red Guardian"),
    ("Kit Connor", "Wikipedia — Kit Connor", "https://en.wikipedia.org/wiki/Kit_Connor", "Biography and filmography"),
    ("Kit Connor", "Wikipedia — Nick Nelson", "https://en.wikipedia.org/wiki/Nick_Nelson_(Heartstopper)", "Nick Nelson details"),
    ("Kit Connor", "Wikipedia — Heartstopper", "https://en.wikipedia.org/wiki/Heartstopper_(TV_series)", "Series details"),
    ("Kit Connor", "Wikipedia — Rocketman", "https://en.wikipedia.org/wiki/Rocketman_(film)", "Young Elton John"),
    ("Kit Connor", "Wikipedia — His Dark Materials", "https://en.wikipedia.org/wiki/His_Dark_Materials_(TV_series)", "Pantalaimon"),
    ("Kit Connor", "Wikipedia — The Wild Robot", "https://en.wikipedia.org/wiki/The_Wild_Robot", "Brightbill"),
    ("Reference", "Wikipedia — 22 Jump Street", "https://en.wikipedia.org/wiki/22_Jump_Street", "Zook Haythe"),
    ("Reference", "Wikipedia — Overlord", "https://en.wikipedia.org/wiki/Overlord_(2018_film)", "Lewis Ford"),
    ("Reference", "Wikipedia — We Are What We Are", "https://en.wikipedia.org/wiki/We_Are_What_We_Are_(2013_film)", "Deputy Anders and cannibalism"),
    ("Reference", "Wikipedia — Monarch: Legacy of Monsters", "https://en.wikipedia.org/wiki/Monarch:_Legacy_of_Monsters", "Lee Shaw"),
    ("Reference", "Wikipedia — Under the Banner of Heaven", "https://en.wikipedia.org/wiki/Under_the_Banner_of_Heaven_(TV_series)", "Dan Lafferty"),
    ("Reference", "Wikipedia — Night Swim", "https://en.wikipedia.org/wiki/Night_Swim", "Ray Waller"),
    ("Reference", "Wikipedia — Gran Turismo", "https://en.wikipedia.org/wiki/Gran_Turismo_(film)", "Jack Salter"),
    ("Reference", "Wikipedia — Creature Commandos", "https://en.wikipedia.org/wiki/Creature_Commandos_(TV_series)", "Eric Frankenstein"),
    ("Reference", "Wikipedia — Romeo + Juliet", "https://en.wikipedia.org/wiki/Romeo_%26_Juliet", "Broadway production"),
    ("Reference", "Wikipedia — A Plague Tale: Requiem", "https://en.wikipedia.org/wiki/A_Plague_Tale:_Requiem", "Lucas"),
]

HEADERS = ["ID", "Actor Name", "Question", "Answer", "Difficulty"]
ACTORS = ["Wyatt Russell", "David Harbour", "Kit Connor"]


def validate(rows):
    assert len(rows) == 60, len(rows)
    ids = [row[0] for row in rows]
    assert len(ids) == len(set(ids)), "Duplicate IDs"

    for actor in ACTORS:
        actor_rows = [row for row in rows if row[1] == actor]
        assert len(actor_rows) == 20, (actor, len(actor_rows))
        expected_ids = [
            f"actors-{actor.lower().replace(' ', '-')}-{i}" for i in range(1, 21)
        ]
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


def style_header(sheet, headers, widths):
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
    style_header(ws, HEADERS, [25, 19, 100, 24, 11])

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

    # Sources sheet
    src = wb.create_sheet("Sources")
    src.sheet_properties.tabColor = "7A7468"
    src.sheet_view.showGridLines = False
    src.append(["Actor", "Source", "URL", "Used For"])
    for row in SOURCES:
        src.append(row)
    style_header(src, ["Actor", "Source", "URL", "Used For"], [18, 40, 80, 38])
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

    # Read Me sheet
    notes = wb.create_sheet("Read Me")
    notes.sheet_properties.tabColor = "C9A227"
    notes.sheet_view.showGridLines = False
    notes.column_dimensions["A"].width = 24
    notes.column_dimensions["B"].width = 68
    notes["A1"] = "Actor Trivia — 60 Questions"
    notes["A1"].font = Font(name="Arial", size=18, bold=True, color="171717")
    notes["A2"] = "20 questions each for Wyatt Russell, David Harbour, and Kit Connor."
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

    wb.properties.title = "Actor Trivia — Wyatt Russell, David Harbour, Kit Connor"
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
