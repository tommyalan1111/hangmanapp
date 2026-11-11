import csv
import re
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent
XLSX_PATH = ROOT / "actors_trivia_kurt_michael_josh.xlsx"
CSV_PATH = ROOT / "actors_trivia_kurt_michael_josh.csv"

ROWS = [
    # Kurt Russell
    ("actors-kurt-russell-1", "Kurt Russell",
     "Which eyepatched antihero does Kurt Russell play in Escape from New York?", "Snake Plissken", "Easy"),
    ("actors-kurt-russell-2", "Kurt Russell",
     "Which helicopter pilot faces a shape-shifting alien in The Thing?", "R.J. MacReady", "Easy"),
    ("actors-kurt-russell-3", "Kurt Russell",
     "Which cocky truck driver stumbles into a Chinese turf war in Big Trouble in Little China?", "Jack Burton", "Easy"),
    ("actors-kurt-russell-4", "Kurt Russell",
     "Which carpenter takes in an amnesiac heiress in Overboard?", "Dean Proffitt", "Medium"),
    ("actors-kurt-russell-5", "Kurt Russell",
     "Which legendary lawman does Kurt Russell play in Tombstone?", "Wyatt Earp", "Easy"),
    ("actors-kurt-russell-6", "Kurt Russell",
     "Which Stargate colonel does Kurt Russell play?", "Jack O'Neil", "Medium"),
    ("actors-kurt-russell-7", "Kurt Russell",
     "Which Olympic hockey coach does Kurt Russell play in Miracle?", "Herb Brooks", "Easy"),
    ("actors-kurt-russell-8", "Kurt Russell",
     "Which holiday hero does Kurt Russell play in The Christmas Chronicles?", "Santa Claus", "Easy"),
    ("actors-kurt-russell-9", "Kurt Russell",
     "Which living planet does Kurt Russell play in Guardians of the Galaxy Vol. 2?", "Ego", "Easy"),
    ("actors-kurt-russell-10", "Kurt Russell",
     "Which mysterious government operative does Kurt Russell play in the Fast & Furious series?", "Mr. Nobody", "Medium"),
    ("actors-kurt-russell-11", "Kurt Russell",
     "Which killer stunt driver does Kurt Russell play in Death Proof?", "Stuntman Mike", "Medium"),
    ("actors-kurt-russell-12", "Kurt Russell",
     "Which bounty hunter does Kurt Russell play in The Hateful Eight?", "John Ruth", "Medium"),
    ("actors-kurt-russell-13", "Kurt Russell",
     "Which sheriff does Kurt Russell play in Bone Tomahawk?", "Franklin Hunt", "Medium"),
    ("actors-kurt-russell-14", "Kurt Russell",
     "Which music icon does Kurt Russell play in the TV film Elvis?", "Elvis Presley", "Medium"),
    ("actors-kurt-russell-15", "Kurt Russell",
     "Which animated hound does Kurt Russell voice in The Fox and the Hound?", "Copper", "Medium"),
    ("actors-kurt-russell-16", "Kurt Russell",
     "Which Disney student does Kurt Russell play in The Computer Wore Tennis Shoes?", "Dexter Riley", "Medium"),
    ("actors-kurt-russell-17", "Kurt Russell",
     "Which sport did Kurt Russell play professionally before acting?", "Baseball", "Easy"),
    ("actors-kurt-russell-18", "Kurt Russell",
     "Which studio signed Kurt Russell to a ten-year contract?", "Walt Disney Productions", "Medium"),
    ("actors-kurt-russell-19", "Kurt Russell",
     "Which actor is Kurt Russell's father?", "Bing Russell", "Easy"),
    ("actors-kurt-russell-20", "Kurt Russell",
     "Which cop does Kurt Russell play opposite Sylvester Stallone in Tango & Cash?", "Gabriel Cash", "Medium"),

    # Michael B. Jordan
    ("actors-michael-b-jordan-1", "Michael B. Jordan",
     "Which boxer does Michael B. Jordan play in the Creed films?", "Adonis Creed", "Easy"),
    ("actors-michael-b-jordan-2", "Michael B. Jordan",
     "Which Black Panther villain does Michael B. Jordan play?", "Erik Killmonger", "Easy"),
    ("actors-michael-b-jordan-3", "Michael B. Jordan",
     "Which real-life shooting victim does Michael B. Jordan play in Fruitvale Station?", "Oscar Grant", "Easy"),
    ("actors-michael-b-jordan-4", "Michael B. Jordan",
     "Which Fantastic Four hero does Michael B. Jordan play?", "Johnny Storm", "Easy"),
    ("actors-michael-b-jordan-5", "Michael B. Jordan",
     "Which young drug dealer does Michael B. Jordan play in The Wire?", "Wallace", "Medium"),
    ("actors-michael-b-jordan-6", "Michael B. Jordan",
     "Which quarterback does Michael B. Jordan play in Friday Night Lights?", "Vince Howard", "Medium"),
    ("actors-michael-b-jordan-7", "Michael B. Jordan",
     "Which civil rights attorney does Michael B. Jordan play in Just Mercy?", "Bryan Stevenson", "Easy"),
    ("actors-michael-b-jordan-8", "Michael B. Jordan",
     "Which alias does Michael B. Jordan's Without Remorse hero adopt?", "John Clark", "Medium"),
    ("actors-michael-b-jordan-9", "Michael B. Jordan",
     "Which soldier does Michael B. Jordan play in A Journal for Jordan?", "Charles Monroe King", "Medium"),
    ("actors-michael-b-jordan-10", "Michael B. Jordan",
     "Which fireman does Michael B. Jordan play in Fahrenheit 451?", "Guy Montag", "Medium"),
    ("actors-michael-b-jordan-11", "Michael B. Jordan",
     "Which soap opera character did Michael B. Jordan play on All My Children?", "Reggie Montgomery", "Medium"),
    ("actors-michael-b-jordan-12", "Michael B. Jordan",
     "Which telekinetic teenager does Michael B. Jordan play in Chronicle?", "Steve Montgomery", "Medium"),
    ("actors-michael-b-jordan-13", "Michael B. Jordan",
     "Which Gears of War soldier does Michael B. Jordan voice?", "Jace Stratton", "Medium"),
    ("actors-michael-b-jordan-14", "Michael B. Jordan",
     "What is the full name of Michael B. Jordan's Sinners character Smoke?", "Elijah Moore", "Easy"),
    ("actors-michael-b-jordan-15", "Michael B. Jordan",
     "Which DC hero does Michael B. Jordan voice in Justice League: The Flashpoint Paradox?", "Cyborg", "Medium"),
    ("actors-michael-b-jordan-16", "Michael B. Jordan",
     "Which Boondocks character does Michael B. Jordan voice?", "Pretty Boy Flizzy", "Medium"),
    ("actors-michael-b-jordan-17", "Michael B. Jordan",
     "Which sport did Michael B. Jordan play in high school?", "Basketball", "Easy"),
    ("actors-michael-b-jordan-18", "Michael B. Jordan",
     "What is Michael B. Jordan's middle name?", "Bakari", "Easy"),
    ("actors-michael-b-jordan-19", "Michael B. Jordan",
     "Which English football club is Michael B. Jordan a part-owner of?", "AFC Bournemouth", "Easy"),
    ("actors-michael-b-jordan-20", "Michael B. Jordan",
     "Which Oscar did Michael B. Jordan win for Sinners?", "Best Actor", "Easy"),

    # Josh Brolin
    ("actors-josh-brolin-1", "Josh Brolin",
     "Which Infinity Saga villain does Josh Brolin play?", "Thanos", "Easy"),
    ("actors-josh-brolin-2", "Josh Brolin",
     "Which time-traveling mutant does Josh Brolin play in Deadpool 2?", "Cable", "Easy"),
    ("actors-josh-brolin-3", "Josh Brolin",
     "Which House Atreides warrior does Josh Brolin play in Dune?", "Gurney Halleck", "Easy"),
    ("actors-josh-brolin-4", "Josh Brolin",
     "Which older brother does Josh Brolin play in The Goonies?", "Brandon Walsh", "Easy"),
    ("actors-josh-brolin-5", "Josh Brolin",
     "Which doomed hunter does Josh Brolin play in No Country for Old Men?", "Llewelyn Moss", "Easy"),
    ("actors-josh-brolin-6", "Josh Brolin",
     "Which San Francisco supervisor does Josh Brolin play in Milk?", "Dan White", "Medium"),
    ("actors-josh-brolin-7", "Josh Brolin",
     "Which U.S. president does Josh Brolin play in W.?", "George W. Bush", "Medium"),
    ("actors-josh-brolin-8", "Josh Brolin",
     "Which CIA operative does Josh Brolin play in Sicario?", "Matt Graver", "Medium"),
    ("actors-josh-brolin-9", "Josh Brolin",
     "Which younger Men in Black agent does Josh Brolin play?", "Agent K", "Medium"),
    ("actors-josh-brolin-10", "Josh Brolin",
     "Which advertising executive is imprisoned in Oldboy?", "Joe Doucett", "Medium"),
    ("actors-josh-brolin-11", "Josh Brolin",
     "Which DC bounty hunter does Josh Brolin play?", "Jonah Hex", "Medium"),
    ("actors-josh-brolin-12", "Josh Brolin",
     "Which WWII veteran leads the Gangster Squad?", "John O'Mara", "Medium"),
    ("actors-josh-brolin-13", "Josh Brolin",
     "Which eccentric detective does Josh Brolin play in Inherent Vice?", "Bigfoot Bjornsen", "Medium"),
    ("actors-josh-brolin-14", "Josh Brolin",
     "In Hail, Caesar!, which studio fixer does Josh Brolin play?", "Eddie Mannix", "Medium"),
    ("actors-josh-brolin-15", "Josh Brolin",
     "Which rancher does Josh Brolin play in Outer Range?", "Royal Abbott", "Medium"),
    ("actors-josh-brolin-16", "Josh Brolin",
     "Which Western legend does Josh Brolin play in The Young Riders?", "Wild Bill Hickok", "Medium"),
    ("actors-josh-brolin-17", "Josh Brolin",
     "Which singer is Josh Brolin's stepmother?", "Barbra Streisand", "Easy"),
    ("actors-josh-brolin-18", "Josh Brolin",
     "Which actor is Josh Brolin's father?", "James Brolin", "Easy"),
    ("actors-josh-brolin-19", "Josh Brolin",
     "Which punk band has Josh Brolin said he helped start?", "Rich Kids on LSD", "Medium"),
    ("actors-josh-brolin-20", "Josh Brolin",
     "Where was Josh Brolin born?", "Santa Monica", "Easy"),
]

SOURCES = [
    ("Kurt Russell", "Wikipedia — Kurt Russell", "https://en.wikipedia.org/wiki/Kurt_Russell", "Biography and filmography"),
    ("Kurt Russell", "Wikipedia — Overboard", "https://en.wikipedia.org/wiki/Overboard_(1987_film)", "Dean Proffitt"),
    ("Kurt Russell", "Wikipedia — The Thing", "https://en.wikipedia.org/wiki/The_Thing_(1982_film)", "R.J. MacReady"),
    ("Kurt Russell", "Wikipedia — Tombstone", "https://en.wikipedia.org/wiki/Tombstone_(film)", "Wyatt Earp"),
    ("Kurt Russell", "Wikipedia — Guardians of the Galaxy Vol. 2", "https://en.wikipedia.org/wiki/Guardians_of_the_Galaxy_Vol._2", "Ego"),
    ("Michael B. Jordan", "Wikipedia — Michael B. Jordan", "https://en.wikipedia.org/wiki/Michael_B._Jordan", "Biography and filmography"),
    ("Michael B. Jordan", "Wikipedia — Sinners", "https://en.wikipedia.org/wiki/Sinners_(2025_film)", "Elijah 'Smoke' Moore and Best Actor"),
    ("Michael B. Jordan", "Wikipedia — Creed", "https://en.wikipedia.org/wiki/Creed_(film)", "Adonis Creed"),
    ("Michael B. Jordan", "Wikipedia — Black Panther", "https://en.wikipedia.org/wiki/Black_Panther_(film)", "Erik Killmonger"),
    ("Michael B. Jordan", "Wikipedia — Fruitvale Station", "https://en.wikipedia.org/wiki/Fruitvale_Station", "Oscar Grant"),
    ("Michael B. Jordan", "Wikipedia — The Wire", "https://en.wikipedia.org/wiki/The_Wire", "Wallace"),
    ("Josh Brolin", "Wikipedia — Josh Brolin", "https://en.wikipedia.org/wiki/Josh_Brolin", "Biography and filmography"),
    ("Josh Brolin", "Wikipedia — Inherent Vice", "https://en.wikipedia.org/wiki/Inherent_Vice_(film)", "Bigfoot Bjornsen"),
    ("Josh Brolin", "Wikipedia — No Country for Old Men", "https://en.wikipedia.org/wiki/No_Country_for_Old_Men_(film)", "Llewelyn Moss"),
    ("Josh Brolin", "Wikipedia — The Goonies", "https://en.wikipedia.org/wiki/The_Goonies", "Brandon Walsh"),
    ("Josh Brolin", "Wikipedia — Milk", "https://en.wikipedia.org/wiki/Milk_(2008_American_film)", "Dan White"),
    ("Josh Brolin", "Wikipedia — W.", "https://en.wikipedia.org/wiki/W._(film)", "George W. Bush"),
    ("Josh Brolin", "Wikipedia — Sicario", "https://en.wikipedia.org/wiki/Sicario_(2015_film)", "Matt Graver"),
    ("Josh Brolin", "Wikipedia — Men in Black 3", "https://en.wikipedia.org/wiki/Men_in_Black_3", "Agent K"),
    ("Josh Brolin", "Wikipedia — Outer Range", "https://en.wikipedia.org/wiki/Outer_Range", "Royal Abbott"),
]

HEADERS = ["ID", "Actor Name", "Question", "Answer", "Difficulty"]
ACTORS = ["Kurt Russell", "Michael B. Jordan", "Josh Brolin"]


def slug_for(actor):
    special = {
        "Michael B. Jordan": "michael-b-jordan",
    }
    return special.get(actor, actor.lower().replace(" ", "-"))


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
        assert re.search(r"\d", answer) is None, (id_, answer)
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
    style_header(ws, [25, 21, 100, 25, 11])

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
    style_header(src, [21, 42, 82, 38])
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
    notes["A2"] = "20 questions each for Kurt Russell, Michael B. Jordan, and Josh Brolin."
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

    wb.properties.title = "Actor Trivia — Kurt Russell, Michael B. Jordan, Josh Brolin"
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
    print("Validated: 60 rows, 20 per actor, unique answers, <=5 words, <=30 chars, no digits, ASCII only.")
