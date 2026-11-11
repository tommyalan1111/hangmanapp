import csv
import re
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent
XLSX_PATH = ROOT / "actors_trivia_chris_paul_sebastian.xlsx"
CSV_PATH = ROOT / "actors_trivia_chris_paul_sebastian.csv"

ROWS = [
    # Chris Pratt
    ("actors-chris-pratt-1", "Chris Pratt",
     "Which Guardians of the Galaxy leader does Chris Pratt play?", "Peter Quill", "Easy"),
    ("actors-chris-pratt-2", "Chris Pratt",
     "Which raptor trainer does Chris Pratt play in Jurassic World?", "Owen Grady", "Easy"),
    ("actors-chris-pratt-3", "Chris Pratt",
     "Which lovably lazy parks employee does Chris Pratt play?", "Andy Dwyer", "Easy"),
    ("actors-chris-pratt-4", "Chris Pratt",
     "Which Lego construction worker does Chris Pratt voice?", "Emmet Brickowski", "Easy"),
    ("actors-chris-pratt-5", "Chris Pratt",
     "Which Nintendo plumber does Chris Pratt voice?", "Mario", "Easy"),
    ("actors-chris-pratt-6", "Chris Pratt",
     "Which Monday-hating cat does Chris Pratt voice?", "Garfield", "Easy"),
    ("actors-chris-pratt-7", "Chris Pratt",
     "Which elf brother does Chris Pratt voice in Onward?", "Barley Lightfoot", "Easy"),
    ("actors-chris-pratt-8", "Chris Pratt",
     "Which gunslinger does Chris Pratt play in The Magnificent Seven?", "Josh Farraday", "Medium"),
    ("actors-chris-pratt-9", "Chris Pratt",
     "Which space traveler does Chris Pratt play in Passengers?", "Jim Preston", "Easy"),
    ("actors-chris-pratt-10", "Chris Pratt",
     "Which time-traveling soldier does Chris Pratt play in The Tomorrow War?", "Dan Forester", "Medium"),
    ("actors-chris-pratt-11", "Chris Pratt",
     "Which Navy SEAL does Chris Pratt play in The Terminal List?", "James Reece", "Medium"),
    ("actors-chris-pratt-12", "Chris Pratt",
     "Which Oakland A's player does Chris Pratt play in Moneyball?", "Scott Hatteberg", "Medium"),
    ("actors-chris-pratt-13", "Chris Pratt",
     "Which Everwood character does Chris Pratt play?", "Bright Abbott", "Medium"),
    ("actors-chris-pratt-14", "Chris Pratt",
     "Which fake FBI agent does Chris Pratt's Andy Dwyer invent?", "Burt Macklin", "Medium"),
    ("actors-chris-pratt-15", "Chris Pratt",
     "Which fake children's entertainer does Andy Dwyer perform as?", "Johnny Karate", "Medium"),
    ("actors-chris-pratt-16", "Chris Pratt",
     "Where did Chris Pratt grow up?", "Lake Stevens", "Easy"),
    ("actors-chris-pratt-17", "Chris Pratt",
     "Who is Chris Pratt's wife?", "Katherine Schwarzenegger", "Easy"),
    ("actors-chris-pratt-18", "Chris Pratt",
     "Who is Chris Pratt's ex-wife?", "Anna Faris", "Easy"),
    ("actors-chris-pratt-19", "Chris Pratt",
     "Which restaurant did Chris Pratt work at when discovered?", "Bubba Gump", "Medium"),
    ("actors-chris-pratt-20", "Chris Pratt",
     "Where was Chris Pratt homeless before acting?", "Maui", "Medium"),

    # Paul Bettany
    ("actors-paul-bettany-1", "Paul Bettany",
     "Which MCU android does Paul Bettany play?", "Vision", "Easy"),
    ("actors-paul-bettany-2", "Paul Bettany",
     "Which AI butler does Paul Bettany voice in Iron Man?", "J.A.R.V.I.S.", "Easy"),
    ("actors-paul-bettany-3", "Paul Bettany",
     "Which poet does Paul Bettany play in A Knight's Tale?", "Geoffrey Chaucer", "Easy"),
    ("actors-paul-bettany-4", "Paul Bettany",
     "Which ship's surgeon does Paul Bettany play in Master and Commander?", "Stephen Maturin", "Medium"),
    ("actors-paul-bettany-5", "Paul Bettany",
     "Which film marked Paul Bettany's directorial debut?", "Shelter", "Medium"),
    ("actors-paul-bettany-6", "Paul Bettany",
     "Which monk does Paul Bettany play in The Da Vinci Code?", "Silas", "Medium"),
    ("actors-paul-bettany-7", "Paul Bettany",
     "Which fire-eater does Paul Bettany play in Inkheart?", "Dustfinger", "Medium"),
    ("actors-paul-bettany-8", "Paul Bettany",
     "Which archangel does Paul Bettany play in Legion?", "Archangel Michael", "Medium"),
    ("actors-paul-bettany-9", "Paul Bettany",
     "Which tennis star does Paul Bettany play in Wimbledon?", "Peter Colt", "Medium"),
    ("actors-paul-bettany-10", "Paul Bettany",
     "Which domestic terrorist does Paul Bettany play in Manhunt?", "Ted Kaczynski", "Medium"),
    ("actors-paul-bettany-11", "Paul Bettany",
     "Which Star Wars crime boss does Paul Bettany play in Solo?", "Dryden Vos", "Easy"),
    ("actors-paul-bettany-12", "Paul Bettany",
     "Which pop artist did Paul Bettany play on stage?", "Andy Warhol", "Medium"),
    ("actors-paul-bettany-13", "Paul Bettany",
     "Which uncle does Paul Bettany play in Uncle Frank?", "Frank Bledsoe", "Medium"),
    ("actors-paul-bettany-14", "Paul Bettany",
     "Which mathematician's roommate does Paul Bettany play in A Beautiful Mind?", "Charles Herman", "Medium"),
    ("actors-paul-bettany-15", "Paul Bettany",
     "Which risk analyst does Paul Bettany play in Margin Call?", "Will Emerson", "Medium"),
    ("actors-paul-bettany-16", "Paul Bettany",
     "Who is Paul Bettany's wife?", "Jennifer Connelly", "Easy"),
    ("actors-paul-bettany-17", "Paul Bettany",
     "Where was Paul Bettany born?", "London", "Easy"),
    ("actors-paul-bettany-18", "Paul Bettany",
     "Which drama school did Paul Bettany attend?", "Drama Centre", "Medium"),
    ("actors-paul-bettany-19", "Paul Bettany",
     "Which job did Paul Bettany have before acting?", "Busker", "Medium"),
    ("actors-paul-bettany-20", "Paul Bettany",
     "Which actor is Paul Bettany's father?", "Thane Bettany", "Medium"),

    # Sebastian Stan
    ("actors-sebastian-stan-1", "Sebastian Stan",
     "Which Captain America ally does Sebastian Stan play?", "Bucky Barnes", "Easy"),
    ("actors-sebastian-stan-2", "Sebastian Stan",
     "Which brainwashed assassin does Sebastian Stan play?", "Winter Soldier", "Easy"),
    ("actors-sebastian-stan-3", "Sebastian Stan",
     "Which Gossip Girl schemer does Sebastian Stan play?", "Carter Baizen", "Medium"),
    ("actors-sebastian-stan-4", "Sebastian Stan",
     "Which Motley Crue drummer does Sebastian Stan play in Pam & Tommy?", "Tommy Lee", "Easy"),
    ("actors-sebastian-stan-5", "Sebastian Stan",
     "Which U.S. president does Sebastian Stan play in The Apprentice?", "Donald Trump", "Easy"),
    ("actors-sebastian-stan-6", "Sebastian Stan",
     "Which disfigured actor does Sebastian Stan play in A Different Man?", "Edward Lemuel", "Medium"),
    ("actors-sebastian-stan-7", "Sebastian Stan",
     "Which figure skater's ex-husband does Sebastian Stan play in I, Tonya?", "Jeff Gillooly", "Medium"),
    ("actors-sebastian-stan-8", "Sebastian Stan",
     "Which warlock does Sebastian Stan play in The Covenant?", "Chase Collins", "Medium"),
    ("actors-sebastian-stan-9", "Sebastian Stan",
     "Which prince does Sebastian Stan play in Kings?", "Jack Benjamin", "Medium"),
    ("actors-sebastian-stan-10", "Sebastian Stan",
     "Which astronaut does Sebastian Stan play in The Martian?", "Chris Beck", "Medium"),
    ("actors-sebastian-stan-11", "Sebastian Stan",
     "Which sheriff does Sebastian Stan play in The Devil All the Time?", "Lee Bodecker", "Medium"),
    ("actors-sebastian-stan-12", "Sebastian Stan",
     "Which CIA agent does Sebastian Stan play in The 355?", "Nick Fowler", "Medium"),
    ("actors-sebastian-stan-13", "Sebastian Stan",
     "Which Eric Bogosian play marked Sebastian Stan's Broadway debut?", "Talk Radio", "Medium"),
    ("actors-sebastian-stan-14", "Sebastian Stan",
     "Which William Inge character did Sebastian Stan play on Broadway?", "Hal Carter", "Medium"),
    ("actors-sebastian-stan-15", "Sebastian Stan",
     "Where was Sebastian Stan born?", "Romania", "Easy"),
    ("actors-sebastian-stan-16", "Sebastian Stan",
     "Which city did Sebastian Stan move to at age eight?", "Vienna", "Easy"),
    ("actors-sebastian-stan-17", "Sebastian Stan",
     "Which university did Sebastian Stan attend?", "Rutgers", "Easy"),
    ("actors-sebastian-stan-18", "Sebastian Stan",
     "Which London theater did Sebastian Stan study at?", "Shakespeare's Globe", "Medium"),
    ("actors-sebastian-stan-19", "Sebastian Stan",
     "Who is Sebastian Stan's partner?", "Annabelle Wallis", "Easy"),
    ("actors-sebastian-stan-20", "Sebastian Stan",
     "Which award did Sebastian Stan win at Berlin for A Different Man?", "Silver Bear", "Medium"),
]

SOURCES = [
    ("Chris Pratt", "Wikipedia — Chris Pratt", "https://en.wikipedia.org/wiki/Chris_Pratt", "Biography and filmography"),
    ("Chris Pratt", "Wikipedia — Guardians of the Galaxy", "https://en.wikipedia.org/wiki/Guardians_of_the_Galaxy_(film)", "Peter Quill"),
    ("Chris Pratt", "Wikipedia — Jurassic World", "https://en.wikipedia.org/wiki/Jurassic_World", "Owen Grady"),
    ("Chris Pratt", "Wikipedia — Parks and Recreation", "https://en.wikipedia.org/wiki/Parks_and_Recreation", "Andy Dwyer and Burt Macklin"),
    ("Chris Pratt", "Wikipedia — The Super Mario Bros. Movie", "https://en.wikipedia.org/wiki/The_Super_Mario_Bros._Movie", "Mario"),
    ("Chris Pratt", "Wikipedia — The Terminal List", "https://en.wikipedia.org/wiki/The_Terminal_List", "James Reece"),
    ("Paul Bettany", "Wikipedia — Paul Bettany", "https://en.wikipedia.org/wiki/Paul_Bettany", "Biography and filmography"),
    ("Paul Bettany", "Wikipedia — A Knight's Tale", "https://en.wikipedia.org/wiki/A_Knight%27s_Tale", "Geoffrey Chaucer"),
    ("Paul Bettany", "Wikipedia — Master and Commander", "https://en.wikipedia.org/wiki/Master_and_Commander:_The_Far_Side_of_the_World", "Stephen Maturin"),
    ("Paul Bettany", "Wikipedia — WandaVision", "https://en.wikipedia.org/wiki/WandaVision", "Vision"),
    ("Paul Bettany", "Wikipedia — The Da Vinci Code", "https://en.wikipedia.org/wiki/The_Da_Vinci_Code_(film)", "Silas"),
    ("Paul Bettany", "Wikipedia — Shelter", "https://en.wikipedia.org/wiki/Shelter_(2014_film)", "Directorial debut"),
    ("Paul Bettany", "Wikipedia — Manhunt", "https://en.wikipedia.org/wiki/Manhunt_(2017_TV_series)", "Ted Kaczynski"),
    ("Sebastian Stan", "Wikipedia — Sebastian Stan", "https://en.wikipedia.org/wiki/Sebastian_Stan", "Biography and filmography"),
    ("Sebastian Stan", "Wikipedia — Captain America: The First Avenger", "https://en.wikipedia.org/wiki/Captain_America:_The_First_Avenger", "Bucky Barnes"),
    ("Sebastian Stan", "Wikipedia — I, Tonya", "https://en.wikipedia.org/wiki/I,_Tonya", "Jeff Gillooly"),
    ("Sebastian Stan", "Wikipedia — Pam & Tommy", "https://en.wikipedia.org/wiki/Pam_%26_Tommy", "Tommy Lee"),
    ("Sebastian Stan", "Wikipedia — The Apprentice", "https://en.wikipedia.org/wiki/The_Apprentice_(2024_film)", "Donald Trump"),
    ("Sebastian Stan", "Wikipedia — A Different Man", "https://en.wikipedia.org/wiki/A_Different_Man", "Edward Lemuel and Silver Bear"),
]

HEADERS = ["ID", "Actor Name", "Question", "Answer", "Difficulty"]
ACTORS = ["Chris Pratt", "Paul Bettany", "Sebastian Stan"]


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
    style_header(ws, [25, 21, 100, 27, 11])

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
    notes["A2"] = "20 questions each for Chris Pratt, Paul Bettany, and Sebastian Stan."
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

    wb.properties.title = "Actor Trivia — Chris Pratt, Paul Bettany, Sebastian Stan"
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
