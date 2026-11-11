import csv
import re
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent
XLSX_PATH = ROOT / "actors_trivia_anthony_paul_benedict.xlsx"
CSV_PATH = ROOT / "actors_trivia_anthony_paul_benedict.csv"

ROWS = [
    # Anthony Mackie
    ("actors-anthony-mackie-1", "Anthony Mackie",
     "Which MCU hero does Anthony Mackie play?", "Sam Wilson", "Easy"),
    ("actors-anthony-mackie-2", "Anthony Mackie",
     "Which winged alias does Sam Wilson use?", "Falcon", "Easy"),
    ("actors-anthony-mackie-3", "Anthony Mackie",
     "Which title does Sam Wilson take after Endgame?", "Captain America", "Easy"),
    ("actors-anthony-mackie-4", "Anthony Mackie",
     "Which Netflix sci-fi character does Anthony Mackie play?", "Takeshi Kovacs", "Medium"),
    ("actors-anthony-mackie-5", "Anthony Mackie",
     "Which civil rights leader does Anthony Mackie play in All the Way?", "Martin Luther King Jr.", "Medium"),
    ("actors-anthony-mackie-6", "Anthony Mackie",
     "Which rapper does Anthony Mackie play in Notorious?", "Tupac Shakur", "Medium"),
    ("actors-anthony-mackie-7", "Anthony Mackie",
     "Which 8 Mile rival does Anthony Mackie play?", "Papa Doc", "Medium"),
    ("actors-anthony-mackie-8", "Anthony Mackie",
     "Which bomb squad sergeant does Anthony Mackie play in The Hurt Locker?", "J.T. Sanborn", "Medium"),
    ("actors-anthony-mackie-9", "Anthony Mackie",
     "Which paramedic does Anthony Mackie play in Synchronic?", "Steve Denube", "Medium"),
    ("actors-anthony-mackie-10", "Anthony Mackie",
     "Which Twisted Metal driver does Anthony Mackie play?", "John Doe", "Easy"),
    ("actors-anthony-mackie-11", "Anthony Mackie",
     "Which android does Anthony Mackie play in Outside the Wire?", "Leo", "Medium"),
    ("actors-anthony-mackie-12", "Anthony Mackie",
     "Which Black Mirror episode does Anthony Mackie appear in?", "Striking Vipers", "Medium"),
    ("actors-anthony-mackie-13", "Anthony Mackie",
     "Which Marshall football player does Anthony Mackie play?", "Nate Ruffin", "Medium"),
    ("actors-anthony-mackie-14", "Anthony Mackie",
     "Which boxer does Anthony Mackie play in Million Dollar Baby?", "Shawrelle Berry", "Medium"),
    ("actors-anthony-mackie-15", "Anthony Mackie",
     "Which play did Anthony Mackie understudy for Don Cheadle?", "Topdog/Underdog", "Medium"),
    ("actors-anthony-mackie-16", "Anthony Mackie",
     "Where was Anthony Mackie born?", "New Orleans", "Easy"),
    ("actors-anthony-mackie-17", "Anthony Mackie",
     "Who was Anthony Mackie's wife?", "Sheletta Chapital", "Medium"),
    ("actors-anthony-mackie-18", "Anthony Mackie",
     "Which brother of Anthony Mackie is a motivational speaker?", "Calvin Mackie", "Medium"),
    ("actors-anthony-mackie-19", "Anthony Mackie",
     "Which Brooklyn bar did Anthony Mackie open?", "NoBar", "Medium"),
    ("actors-anthony-mackie-20", "Anthony Mackie",
     "Which announced film is Anthony Mackie's directorial debut?", "Spark", "Medium"),

    # Paul Rudd
    ("actors-paul-rudd-1", "Paul Rudd",
     "Which MCU hero does Paul Rudd play?", "Scott Lang", "Easy"),
    ("actors-paul-rudd-2", "Paul Rudd",
     "Which shrinking superhero alias does Paul Rudd use?", "Ant-Man", "Easy"),
    ("actors-paul-rudd-3", "Paul Rudd",
     "Which Friends husband does Paul Rudd play?", "Mike Hannigan", "Easy"),
    ("actors-paul-rudd-4", "Paul Rudd",
     "Which Wet Hot American Summer counselor does Paul Rudd play?", "Andy", "Medium"),
    ("actors-paul-rudd-5", "Paul Rudd",
     "Which Anchorman reporter does Paul Rudd play?", "Brian Fantana", "Easy"),
    ("actors-paul-rudd-6", "Paul Rudd",
     "Which Clueless ex-stepbrother does Paul Rudd play?", "Josh", "Medium"),
    ("actors-paul-rudd-7", "Paul Rudd",
     "Which Halloween character does Paul Rudd play?", "Tommy Doyle", "Medium"),
    ("actors-paul-rudd-8", "Paul Rudd",
     "Which Beatle does Paul Rudd play in Walk Hard?", "John Lennon", "Medium"),
    ("actors-paul-rudd-9", "Paul Rudd",
     "Which slacker does Paul Rudd play in I Love You, Man?", "Sydney Fife", "Easy"),
    ("actors-paul-rudd-10", "Paul Rudd",
     "Which Pawnee candidate does Paul Rudd play?", "Bobby Newport", "Medium"),
    ("actors-paul-rudd-11", "Paul Rudd",
     "Which Ghostbusters scientist does Paul Rudd play?", "Gary Grooberson", "Easy"),
    ("actors-paul-rudd-12", "Paul Rudd",
     "Which caregiver does Paul Rudd play in The Fundamentals of Caring?", "Ben Benjamin", "Medium"),
    ("actors-paul-rudd-13", "Paul Rudd",
     "Which baseball spy does Paul Rudd play?", "Moe Berg", "Medium"),
    ("actors-paul-rudd-14", "Paul Rudd",
     "Which Living with Yourself clone does Paul Rudd play?", "Miles Elliot", "Medium"),
    ("actors-paul-rudd-15", "Paul Rudd",
     "Which therapist does Paul Rudd play in The Shrink Next Door?", "Isaac Herschkopf", "Medium"),
    ("actors-paul-rudd-16", "Paul Rudd",
     "Which Only Murders victim does Paul Rudd play?", "Ben Glenroy", "Medium"),
    ("actors-paul-rudd-17", "Paul Rudd",
     "Where was Paul Rudd born?", "Passaic", "Easy"),
    ("actors-paul-rudd-18", "Paul Rudd",
     "Who is Paul Rudd's wife?", "Julie Yaeger", "Easy"),
    ("actors-paul-rudd-19", "Paul Rudd",
     "Which film does Paul Rudd repeatedly prank Conan O'Brien with?", "Mac and Me", "Medium"),
    ("actors-paul-rudd-20", "Paul Rudd",
     "Which candy store does Paul Rudd co-own?", "Samuel's Sweet Shop", "Medium"),

    # Benedict Cumberbatch
    ("actors-benedict-cumberbatch-1", "Benedict Cumberbatch",
     "Which MCU sorcerer does Benedict Cumberbatch play?", "Stephen Strange", "Easy"),
    ("actors-benedict-cumberbatch-2", "Benedict Cumberbatch",
     "Which detective does Benedict Cumberbatch play in Sherlock?", "Sherlock Holmes", "Easy"),
    ("actors-benedict-cumberbatch-3", "Benedict Cumberbatch",
     "Which Star Trek villain does Benedict Cumberbatch play?", "Khan Noonien Singh", "Easy"),
    ("actors-benedict-cumberbatch-4", "Benedict Cumberbatch",
     "Which dragon does Benedict Cumberbatch voice in The Hobbit?", "Smaug", "Easy"),
    ("actors-benedict-cumberbatch-5", "Benedict Cumberbatch",
     "Which Dark Lord does Benedict Cumberbatch voice in The Hobbit?", "Sauron", "Medium"),
    ("actors-benedict-cumberbatch-6", "Benedict Cumberbatch",
     "Which mathematician does Benedict Cumberbatch play in The Imitation Game?", "Alan Turing", "Easy"),
    ("actors-benedict-cumberbatch-7", "Benedict Cumberbatch",
     "Which rancher does Benedict Cumberbatch play in The Power of the Dog?", "Phil Burbank", "Easy"),
    ("actors-benedict-cumberbatch-8", "Benedict Cumberbatch",
     "Which troubled title character does Benedict Cumberbatch play in Patrick Melrose?", "Patrick Melrose", "Medium"),
    ("actors-benedict-cumberbatch-9", "Benedict Cumberbatch",
     "Which physicist does Benedict Cumberbatch play in Hawking?", "Stephen Hawking", "Medium"),
    ("actors-benedict-cumberbatch-10", "Benedict Cumberbatch",
     "Which WikiLeaks founder does Benedict Cumberbatch play?", "Julian Assange", "Medium"),
    ("actors-benedict-cumberbatch-11", "Benedict Cumberbatch",
     "Which spy does Benedict Cumberbatch play in Tinker Tailor Soldier Spy?", "Peter Guillam", "Medium"),
    ("actors-benedict-cumberbatch-12", "Benedict Cumberbatch",
     "Which king does Benedict Cumberbatch play in The Hollow Crown?", "Richard III", "Medium"),
    ("actors-benedict-cumberbatch-13", "Benedict Cumberbatch",
     "Which stage play earned Benedict Cumberbatch an Olivier?", "Frankenstein", "Medium"),
    ("actors-benedict-cumberbatch-14", "Benedict Cumberbatch",
     "Which Dr. Seuss character does Benedict Cumberbatch voice?", "The Grinch", "Easy"),
    ("actors-benedict-cumberbatch-15", "Benedict Cumberbatch",
     "Which radio sitcom casts Benedict Cumberbatch as Martin Crieff?", "Cabin Pressure", "Medium"),
    ("actors-benedict-cumberbatch-16", "Benedict Cumberbatch",
     "Where was Benedict Cumberbatch born?", "Hammersmith", "Easy"),
    ("actors-benedict-cumberbatch-17", "Benedict Cumberbatch",
     "Who is Benedict Cumberbatch's wife?", "Sophie Hunter", "Easy"),
    ("actors-benedict-cumberbatch-18", "Benedict Cumberbatch",
     "Which university did Benedict Cumberbatch attend?", "University of Manchester", "Easy"),
    ("actors-benedict-cumberbatch-19", "Benedict Cumberbatch",
     "Which drama school did Benedict Cumberbatch attend?", "LAMDA", "Medium"),
    ("actors-benedict-cumberbatch-20", "Benedict Cumberbatch",
     "Which production company did Benedict Cumberbatch co-found?", "SunnyMarch", "Medium"),
]

SOURCES = [
    ("Anthony Mackie", "Wikipedia — Anthony Mackie", "https://en.wikipedia.org/wiki/Anthony_Mackie", "Biography and filmography"),
    ("Anthony Mackie", "Wikipedia — The Hurt Locker", "https://en.wikipedia.org/wiki/The_Hurt_Locker", "J.T. Sanborn"),
    ("Anthony Mackie", "Wikipedia — The Falcon and the Winter Soldier", "https://en.wikipedia.org/wiki/The_Falcon_and_the_Winter_Soldier", "Sam Wilson and Captain America"),
    ("Anthony Mackie", "Wikipedia — Twisted Metal", "https://en.wikipedia.org/wiki/Twisted_Metal_(TV_series)", "John Doe"),
    ("Anthony Mackie", "Wikipedia — Altered Carbon", "https://en.wikipedia.org/wiki/Altered_Carbon_(TV_series)", "Takeshi Kovacs"),
    ("Anthony Mackie", "Wikipedia — 8 Mile", "https://en.wikipedia.org/wiki/8_Mile_(film)", "Papa Doc"),
    ("Paul Rudd", "Wikipedia — Paul Rudd", "https://en.wikipedia.org/wiki/Paul_Rudd", "Biography and filmography"),
    ("Paul Rudd", "Wikipedia — Ant-Man", "https://en.wikipedia.org/wiki/Ant-Man_(film)", "Scott Lang"),
    ("Paul Rudd", "Wikipedia — Friends", "https://en.wikipedia.org/wiki/Friends", "Mike Hannigan"),
    ("Paul Rudd", "Wikipedia — Anchorman", "https://en.wikipedia.org/wiki/Anchorman:_The_Legend_of_Ron_Burgundy", "Brian Fantana"),
    ("Paul Rudd", "Wikipedia — I Love You, Man", "https://en.wikipedia.org/wiki/I_Love_You,_Man", "Sydney Fife"),
    ("Paul Rudd", "Wikipedia — Living with Yourself", "https://en.wikipedia.org/wiki/Living_with_Yourself", "Miles Elliot"),
    ("Benedict Cumberbatch", "Wikipedia — Benedict Cumberbatch", "https://en.wikipedia.org/wiki/Benedict_Cumberbatch", "Biography and filmography"),
    ("Benedict Cumberbatch", "Wikipedia — Sherlock", "https://en.wikipedia.org/wiki/Sherlock_(TV_series)", "Sherlock Holmes"),
    ("Benedict Cumberbatch", "Wikipedia — The Imitation Game", "https://en.wikipedia.org/wiki/The_Imitation_Game", "Alan Turing"),
    ("Benedict Cumberbatch", "Wikipedia — The Power of the Dog", "https://en.wikipedia.org/wiki/The_Power_of_the_Dog_(film)", "Phil Burbank"),
    ("Benedict Cumberbatch", "Wikipedia — Doctor Strange", "https://en.wikipedia.org/wiki/Doctor_Strange_(2016_film)", "Stephen Strange"),
    ("Benedict Cumberbatch", "Wikipedia — Frankenstein", "https://en.wikipedia.org/wiki/Frankenstein_(2011_play)", "Olivier-winning stage role"),
]

HEADERS = ["ID", "Actor Name", "Question", "Answer", "Difficulty"]
ACTORS = ["Anthony Mackie", "Paul Rudd", "Benedict Cumberbatch"]


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
    style_header(ws, [25, 22, 100, 27, 11])

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
    style_header(src, [22, 42, 84, 38])
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
    notes["A2"] = "20 questions each for Anthony Mackie, Paul Rudd, and Benedict Cumberbatch."
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

    wb.properties.title = "Actor Trivia — Anthony Mackie, Paul Rudd, Benedict Cumberbatch"
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
