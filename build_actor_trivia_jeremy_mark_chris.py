import csv
import re
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent
XLSX_PATH = ROOT / "actors_trivia_jeremy_mark_chris.xlsx"
CSV_PATH = ROOT / "actors_trivia_jeremy_mark_chris.csv"

ROWS = [
    # Jeremy Renner
    ("actors-jeremy-renner-1", "Jeremy Renner",
     "Which MCU archer does Jeremy Renner play?", "Clint Barton", "Easy"),
    ("actors-jeremy-renner-2", "Jeremy Renner",
     "Which superhero alias does Clint Barton use?", "Hawkeye", "Easy"),
    ("actors-jeremy-renner-3", "Jeremy Renner",
     "Which darker alias does Clint Barton adopt after the snap?", "Ronin", "Medium"),
    ("actors-jeremy-renner-4", "Jeremy Renner",
     "Which bomb disposal expert does Jeremy Renner play in The Hurt Locker?", "William James", "Easy"),
    ("actors-jeremy-renner-5", "Jeremy Renner",
     "Which hot-headed robber does Jeremy Renner play in The Town?", "Jem Coughlin", "Medium"),
    ("actors-jeremy-renner-6", "Jeremy Renner",
     "Which Bourne operative does Jeremy Renner play?", "Aaron Cross", "Easy"),
    ("actors-jeremy-renner-7", "Jeremy Renner",
     "Which Mission: Impossible agent does Jeremy Renner play?", "William Brandt", "Easy"),
    ("actors-jeremy-renner-8", "Jeremy Renner",
     "Which fairy-tale hunter does Jeremy Renner play?", "Hansel", "Medium"),
    ("actors-jeremy-renner-9", "Jeremy Renner",
     "Which politician does Jeremy Renner play in American Hustle?", "Carmine Polito", "Medium"),
    ("actors-jeremy-renner-10", "Jeremy Renner",
     "Which tracker does Jeremy Renner play in Wind River?", "Cory Lambert", "Medium"),
    ("actors-jeremy-renner-11", "Jeremy Renner",
     "Which physicist does Jeremy Renner play in Arrival?", "Ian Donnelly", "Medium"),
    ("actors-jeremy-renner-12", "Jeremy Renner",
     "Which journalist does Jeremy Renner play in Kill the Messenger?", "Gary Webb", "Medium"),
    ("actors-jeremy-renner-13", "Jeremy Renner",
     "Which Kingstown power broker does Jeremy Renner play?", "Mike McLusky", "Easy"),
    ("actors-jeremy-renner-14", "Jeremy Renner",
     "Which serial killer does Jeremy Renner play in Dahmer?", "Jeffrey Dahmer", "Medium"),
    ("actors-jeremy-renner-15", "Jeremy Renner",
     "Which doctor does Jeremy Renner play in Wake Up Dead Man?", "Nat Sharp", "Medium"),
    ("actors-jeremy-renner-16", "Jeremy Renner",
     "Where was Jeremy Renner born?", "Modesto", "Easy"),
    ("actors-jeremy-renner-17", "Jeremy Renner",
     "Which college did Jeremy Renner attend?", "Modesto Junior College", "Medium"),
    ("actors-jeremy-renner-18", "Jeremy Renner",
     "Which job did Jeremy Renner do between acting roles?", "Makeup artist", "Medium"),
    ("actors-jeremy-renner-19", "Jeremy Renner",
     "Which vehicle caused Jeremy Renner's near-fatal accident?", "Snowplow", "Easy"),
    ("actors-jeremy-renner-20", "Jeremy Renner",
     "Who was Jeremy Renner's wife?", "Sonni Pacheco", "Medium"),

    # Mark Ruffalo
    ("actors-mark-ruffalo-1", "Mark Ruffalo",
     "Which MCU scientist does Mark Ruffalo play?", "Bruce Banner", "Easy"),
    ("actors-mark-ruffalo-2", "Mark Ruffalo",
     "Which angry alter ego does Bruce Banner become?", "Hulk", "Easy"),
    ("actors-mark-ruffalo-3", "Mark Ruffalo",
     "Which Olympic wrestler does Mark Ruffalo play in Foxcatcher?", "Dave Schultz", "Easy"),
    ("actors-mark-ruffalo-4", "Mark Ruffalo",
     "Which Boston Globe reporter does Mark Ruffalo play?", "Michael Rezendes", "Easy"),
    ("actors-mark-ruffalo-5", "Mark Ruffalo",
     "Which debauched lawyer does Mark Ruffalo play in Poor Things?", "Duncan Wedderburn", "Easy"),
    ("actors-mark-ruffalo-6", "Mark Ruffalo",
     "Which U.S. Marshal does Mark Ruffalo play in Shutter Island?", "Chuck Aule", "Medium"),
    ("actors-mark-ruffalo-7", "Mark Ruffalo",
     "Which SFPD inspector does Mark Ruffalo play in Zodiac?", "Dave Toschi", "Medium"),
    ("actors-mark-ruffalo-8", "Mark Ruffalo",
     "Which 13 Going on 30 character does Mark Ruffalo play?", "Matty Flamhaff", "Medium"),
    ("actors-mark-ruffalo-9", "Mark Ruffalo",
     "Which music producer does Mark Ruffalo play in Begin Again?", "Dan Mulligan", "Medium"),
    ("actors-mark-ruffalo-10", "Mark Ruffalo",
     "Which AIDS activist does Mark Ruffalo play in The Normal Heart?", "Ned Weeks", "Medium"),
    ("actors-mark-ruffalo-11", "Mark Ruffalo",
     "Which Birdsey twin does Mark Ruffalo play in I Know This Much Is True?", "Dominick Birdsey", "Medium"),
    ("actors-mark-ruffalo-12", "Mark Ruffalo",
     "Which corporate lawyer does Mark Ruffalo play in Dark Waters?", "Robert Bilott", "Medium"),
    ("actors-mark-ruffalo-13", "Mark Ruffalo",
     "Which FBI agent does Mark Ruffalo play in Now You See Me?", "Dylan Rhodes", "Medium"),
    ("actors-mark-ruffalo-14", "Mark Ruffalo",
     "Which estranged brother does Mark Ruffalo play in You Can Count on Me?", "Terry Prescott", "Medium"),
    ("actors-mark-ruffalo-15", "Mark Ruffalo",
     "Where was Mark Ruffalo born?", "Kenosha", "Easy"),
    ("actors-mark-ruffalo-16", "Mark Ruffalo",
     "Who is Mark Ruffalo's wife?", "Sunrise Coigney", "Easy"),
    ("actors-mark-ruffalo-17", "Mark Ruffalo",
     "Which Clifford Odets play earned Mark Ruffalo a Tony nomination?", "Awake and Sing!", "Medium"),
    ("actors-mark-ruffalo-18", "Mark Ruffalo",
     "Which film marked Mark Ruffalo's directorial debut?", "Sympathy for Delicious", "Medium"),
    ("actors-mark-ruffalo-19", "Mark Ruffalo",
     "Which acting school did Mark Ruffalo attend?", "Stella Adler", "Medium"),
    ("actors-mark-ruffalo-20", "Mark Ruffalo",
     "Which job did Mark Ruffalo have for nearly a decade?", "Bartender", "Medium"),

    # Chris Hemsworth
    ("actors-chris-hemsworth-1", "Chris Hemsworth",
     "Which Marvel hero does Chris Hemsworth play?", "Thor Odinson", "Easy"),
    ("actors-chris-hemsworth-2", "Chris Hemsworth",
     "Which black-ops mercenary does Chris Hemsworth play in Extraction?", "Tyler Rake", "Easy"),
    ("actors-chris-hemsworth-3", "Chris Hemsworth",
     "Which Formula One driver does Chris Hemsworth play in Rush?", "James Hunt", "Easy"),
    ("actors-chris-hemsworth-4", "Chris Hemsworth",
     "Which Home and Away character does Chris Hemsworth play?", "Kim Hyde", "Medium"),
    ("actors-chris-hemsworth-5", "Chris Hemsworth",
     "Which Star Trek character does Chris Hemsworth play?", "George Kirk", "Easy"),
    ("actors-chris-hemsworth-6", "Chris Hemsworth",
     "Which fairy-tale huntsman does Chris Hemsworth play?", "Eric the Huntsman", "Easy"),
    ("actors-chris-hemsworth-7", "Chris Hemsworth",
     "Which Ghostbusters receptionist does Chris Hemsworth play?", "Kevin Beckman", "Easy"),
    ("actors-chris-hemsworth-8", "Chris Hemsworth",
     "Which cult leader does Chris Hemsworth play in Bad Times at the El Royale?", "Billy Lee", "Medium"),
    ("actors-chris-hemsworth-9", "Chris Hemsworth",
     "Which Men in Black agent does Chris Hemsworth play?", "Agent H", "Easy"),
    ("actors-chris-hemsworth-10", "Chris Hemsworth",
     "Which Mad Max warlord does Chris Hemsworth play?", "Dementus", "Medium"),
    ("actors-chris-hemsworth-11", "Chris Hemsworth",
     "Which Transformers leader does Chris Hemsworth voice?", "Optimus Prime", "Easy"),
    ("actors-chris-hemsworth-12", "Chris Hemsworth",
     "Which Green Beret does Chris Hemsworth play in 12 Strong?", "Mitch Nelson", "Medium"),
    ("actors-chris-hemsworth-13", "Chris Hemsworth",
     "Which whaling ship first mate does Chris Hemsworth play?", "Owen Chase", "Medium"),
    ("actors-chris-hemsworth-14", "Chris Hemsworth",
     "Which Spiderhead scientist does Chris Hemsworth play?", "Steve Abnesti", "Medium"),
    ("actors-chris-hemsworth-15", "Chris Hemsworth",
     "Which Cabin in the Woods jock does Chris Hemsworth play?", "Curt Vaughan", "Medium"),
    ("actors-chris-hemsworth-16", "Chris Hemsworth",
     "Where was Chris Hemsworth born?", "Melbourne", "Easy"),
    ("actors-chris-hemsworth-17", "Chris Hemsworth",
     "Who is Chris Hemsworth's wife?", "Elsa Pataky", "Easy"),
    ("actors-chris-hemsworth-18", "Chris Hemsworth",
     "Which younger brother of Chris Hemsworth is also an actor?", "Liam Hemsworth", "Easy"),
    ("actors-chris-hemsworth-19", "Chris Hemsworth",
     "Where in Australia does Chris Hemsworth live?", "Byron Bay", "Medium"),
    ("actors-chris-hemsworth-20", "Chris Hemsworth",
     "Which disease risk did Chris Hemsworth discover he has?", "Alzheimer's", "Medium"),
]

SOURCES = [
    ("Jeremy Renner", "Wikipedia — Jeremy Renner", "https://en.wikipedia.org/wiki/Jeremy_Renner", "Biography and filmography"),
    ("Jeremy Renner", "Wikipedia — The Hurt Locker", "https://en.wikipedia.org/wiki/The_Hurt_Locker", "William James"),
    ("Jeremy Renner", "Wikipedia — The Town", "https://en.wikipedia.org/wiki/The_Town_(2010_film)", "Jem Coughlin"),
    ("Jeremy Renner", "Wikipedia — Hawkeye", "https://en.wikipedia.org/wiki/Hawkeye_(miniseries)", "Clint Barton and Ronin"),
    ("Jeremy Renner", "Wikipedia — Mayor of Kingstown", "https://en.wikipedia.org/wiki/Mayor_of_Kingstown", "Mike McLusky"),
    ("Jeremy Renner", "Wikipedia — Dahmer", "https://en.wikipedia.org/wiki/Dahmer_(film)", "Jeffrey Dahmer"),
    ("Mark Ruffalo", "Wikipedia — Mark Ruffalo", "https://en.wikipedia.org/wiki/Mark_Ruffalo", "Biography and filmography"),
    ("Mark Ruffalo", "Wikipedia — Spotlight", "https://en.wikipedia.org/wiki/Spotlight_(film)", "Michael Rezendes"),
    ("Mark Ruffalo", "Wikipedia — Foxcatcher", "https://en.wikipedia.org/wiki/Foxcatcher", "Dave Schultz"),
    ("Mark Ruffalo", "Wikipedia — Poor Things", "https://en.wikipedia.org/wiki/Poor_Things_(film)", "Duncan Wedderburn"),
    ("Mark Ruffalo", "Wikipedia — Shutter Island", "https://en.wikipedia.org/wiki/Shutter_Island_(film)", "Chuck Aule"),
    ("Mark Ruffalo", "Wikipedia — I Know This Much Is True", "https://en.wikipedia.org/wiki/I_Know_This_Much_Is_True_(miniseries)", "Dominick Birdsey"),
    ("Chris Hemsworth", "Wikipedia — Chris Hemsworth", "https://en.wikipedia.org/wiki/Chris_Hemsworth", "Biography and filmography"),
    ("Chris Hemsworth", "Wikipedia — Thor", "https://en.wikipedia.org/wiki/Thor_(film)", "Thor Odinson"),
    ("Chris Hemsworth", "Wikipedia — Extraction", "https://en.wikipedia.org/wiki/Extraction_(2020_film)", "Tyler Rake"),
    ("Chris Hemsworth", "Wikipedia — Rush", "https://en.wikipedia.org/wiki/Rush_(2013_film)", "James Hunt"),
    ("Chris Hemsworth", "Wikipedia — Furiosa", "https://en.wikipedia.org/wiki/Furiosa:_A_Mad_Max_Saga", "Dementus"),
    ("Chris Hemsworth", "Wikipedia — Ghostbusters", "https://en.wikipedia.org/wiki/Ghostbusters_(2016_film)", "Kevin Beckman"),
]

HEADERS = ["ID", "Actor Name", "Question", "Answer", "Difficulty"]
ACTORS = ["Jeremy Renner", "Mark Ruffalo", "Chris Hemsworth"]


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
    style_header(ws, [25, 20, 100, 27, 11])

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
    notes["A2"] = "20 questions each for Jeremy Renner, Mark Ruffalo, and Chris Hemsworth."
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

    wb.properties.title = "Actor Trivia — Jeremy Renner, Mark Ruffalo, Chris Hemsworth"
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
