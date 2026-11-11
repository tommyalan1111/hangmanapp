import csv
import re
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent
XLSX_PATH = ROOT / "actors_trivia_tom_benedict_don.xlsx"
CSV_PATH = ROOT / "actors_trivia_tom_benedict_don.csv"

ROWS = [
    # Tom Hiddleston
    ("actors-tom-hiddleston-1", "Tom Hiddleston",
     "Which god of mischief does Tom Hiddleston play in the MCU?", "Loki", "Easy"),
    ("actors-tom-hiddleston-2", "Tom Hiddleston",
     "Which Jazz Age novelist does Tom Hiddleston play in Midnight in Paris?", "F. Scott Fitzgerald", "Medium"),
    ("actors-tom-hiddleston-3", "Tom Hiddleston",
     "Which cavalry officer does Tom Hiddleston play in War Horse?", "Captain Nicholls", "Medium"),
    ("actors-tom-hiddleston-4", "Tom Hiddleston",
     "Which RAF pilot does Tom Hiddleston play in The Deep Blue Sea?", "Freddie Page", "Medium"),
    ("actors-tom-hiddleston-5", "Tom Hiddleston",
     "Which centuries-old vampire does Tom Hiddleston play in Only Lovers Left Alive?", "Adam", "Medium"),
    ("actors-tom-hiddleston-6", "Tom Hiddleston",
     "Which mysterious inventor does Tom Hiddleston play in Crimson Peak?", "Thomas Sharpe", "Medium"),
    ("actors-tom-hiddleston-7", "Tom Hiddleston",
     "Which country legend does Tom Hiddleston play in I Saw the Light?", "Hank Williams", "Medium"),
    ("actors-tom-hiddleston-8", "Tom Hiddleston",
     "Which tracker does Tom Hiddleston play in Kong: Skull Island?", "James Conrad", "Easy"),
    ("actors-tom-hiddleston-9", "Tom Hiddleston",
     "Which hotel night manager does Tom Hiddleston play in The Night Manager?", "Jonathan Pine", "Easy"),
    ("actors-tom-hiddleston-10", "Tom Hiddleston",
     "Which Shakespearean general did Tom Hiddleston play at the Donmar?", "Coriolanus", "Medium"),
    ("actors-tom-hiddleston-11", "Tom Hiddleston",
     "Which Shakespearean prince did Tom Hiddleston play on stage?", "Hamlet", "Easy"),
    ("actors-tom-hiddleston-12", "Tom Hiddleston",
     "Which high-rise doctor does Tom Hiddleston play in High-Rise?", "Robert Laing", "Medium"),
    ("actors-tom-hiddleston-13", "Tom Hiddleston",
     "Which suburban sitcom character did Tom Hiddleston play in Suburban Shootout?", "Bill Hazledine", "Medium"),
    ("actors-tom-hiddleston-14", "Tom Hiddleston",
     "Which Wallander detective does Tom Hiddleston play?", "Magnus Martinsson", "Medium"),
    ("actors-tom-hiddleston-15", "Tom Hiddleston",
     "Which Churchill son does Tom Hiddleston play in The Gathering Storm?", "Randolph Churchill", "Medium"),
    ("actors-tom-hiddleston-16", "Tom Hiddleston",
     "Which naturalist does Tom Hiddleston voice in Galapagos?", "Charles Darwin", "Medium"),
    ("actors-tom-hiddleston-17", "Tom Hiddleston",
     "Which Othello character did Tom Hiddleston play?", "Cassio", "Medium"),
    ("actors-tom-hiddleston-18", "Tom Hiddleston",
     "Which Marvel hero did Tom Hiddleston originally audition to play?", "Thor", "Easy"),
    ("actors-tom-hiddleston-19", "Tom Hiddleston",
     "Which award did Tom Hiddleston win for The Night Manager?", "Golden Globe", "Easy"),
    ("actors-tom-hiddleston-20", "Tom Hiddleston",
     "Where was Tom Hiddleston born?", "Westminster", "Easy"),

    # Benedict Wong
    ("actors-benedict-wong-1", "Benedict Wong",
     "Which MCU sorcerer does Benedict Wong play?", "Wong", "Easy"),
    ("actors-benedict-wong-2", "Benedict Wong",
     "Which Marvel film first introduced Benedict Wong as Wong?", "Doctor Strange", "Easy"),
    ("actors-benedict-wong-3", "Benedict Wong",
     "Which Netflix historical drama casts Benedict Wong as Kublai Khan?", "Marco Polo", "Easy"),
    ("actors-benedict-wong-4", "Benedict Wong",
     "Which Ridley Scott space film casts Benedict Wong as Bruce Ng?", "The Martian", "Easy"),
    ("actors-benedict-wong-5", "Benedict Wong",
     "Which Netflix sci-fi series casts Benedict Wong as Da Shi?", "3 Body Problem", "Easy"),
    ("actors-benedict-wong-6", "Benedict Wong",
     "Which Dirty Pretty Things character earned Benedict Wong a BIFA nomination?", "Guo Yi", "Medium"),
    ("actors-benedict-wong-7", "Benedict Wong",
     "Which 15 Storeys High character does Benedict Wong play?", "Errol Spears", "Medium"),
    ("actors-benedict-wong-8", "Benedict Wong",
     "Which Ridley Scott sci-fi film casts Benedict Wong as the pilot Ravel?", "Prometheus", "Medium"),
    ("actors-benedict-wong-9", "Benedict Wong",
     "Which Alex Garland sci-fi horror film casts Benedict Wong as Lomax?", "Annihilation", "Medium"),
    ("actors-benedict-wong-10", "Benedict Wong",
     "Which existential drama casts Benedict Wong as Kyo?", "Nine Days", "Medium"),
    ("actors-benedict-wong-11", "Benedict Wong",
     "Which Disney animated film casts Benedict Wong as the giant Tong?", "Raya and the Last Dragon", "Easy"),
    ("actors-benedict-wong-12", "Benedict Wong",
     "Which Disney remake casts Benedict Wong as the voice of Bull?", "Lady and the Tramp", "Easy"),
    ("actors-benedict-wong-13", "Benedict Wong",
     "Which Syfy series casts Benedict Wong as Master Lin?", "Deadly Class", "Medium"),
    ("actors-benedict-wong-14", "Benedict Wong",
     "Which Black Mirror episode features Benedict Wong as Shaun Li?", "Hated in the Nation", "Medium"),
    ("actors-benedict-wong-15", "Benedict Wong",
     "Which video game features Benedict Wong as Alex Yu?", "Prey", "Medium"),
    ("actors-benedict-wong-16", "Benedict Wong",
     "Which real-life artist did Benedict Wong play on stage in #aiww?", "Ai Weiwei", "Medium"),
    ("actors-benedict-wong-17", "Benedict Wong",
     "Where was Benedict Wong born?", "Eccles", "Easy"),
    ("actors-benedict-wong-18", "Benedict Wong",
     "Where did Benedict Wong grow up?", "Salford", "Easy"),
    ("actors-benedict-wong-19", "Benedict Wong",
     "Which football club does Benedict Wong support?", "Manchester United", "Easy"),
    ("actors-benedict-wong-20", "Benedict Wong",
     "Which radio play gave Benedict Wong his first role?", "Kai Mei Sauce", "Medium"),

    # Don Cheadle
    ("actors-don-cheadle-1", "Don Cheadle",
     "Which armored Avenger does Don Cheadle play in the MCU?", "War Machine", "Easy"),
    ("actors-don-cheadle-2", "Don Cheadle",
     "Which character does Don Cheadle play in Iron Man 2?", "James Rhodes", "Easy"),
    ("actors-don-cheadle-3", "Don Cheadle",
     "Which real-life hotel manager does Don Cheadle play in Hotel Rwanda?", "Paul Rusesabagina", "Easy"),
    ("actors-don-cheadle-4", "Don Cheadle",
     "Which demolitions expert does Don Cheadle play in Ocean's Eleven?", "Basher Tarr", "Easy"),
    ("actors-don-cheadle-5", "Don Cheadle",
     "Which management consultant does Don Cheadle play in House of Lies?", "Marty Kaan", "Easy"),
    ("actors-don-cheadle-6", "Don Cheadle",
     "Which Wall Street trader does Don Cheadle play in Black Monday?", "Maurice Monroe", "Medium"),
    ("actors-don-cheadle-7", "Don Cheadle",
     "Which dangerous friend does Don Cheadle play in Devil in a Blue Dress?", "Mouse Alexander", "Medium"),
    ("actors-don-cheadle-8", "Don Cheadle",
     "Which Rat Pack singer does Don Cheadle play in The Rat Pack?", "Sammy Davis Jr.", "Medium"),
    ("actors-don-cheadle-9", "Don Cheadle",
     "Which schoolteacher does Don Cheadle play in A Lesson Before Dying?", "Grant Wiggins", "Medium"),
    ("actors-don-cheadle-10", "Don Cheadle",
     "Which DEA agent does Don Cheadle play in Traffic?", "Montel Gordon", "Medium"),
    ("actors-don-cheadle-11", "Don Cheadle",
     "Which Detroit gangster does Don Cheadle play in No Sudden Move?", "Curt Goynes", "Medium"),
    ("actors-don-cheadle-12", "Don Cheadle",
     "Which digital villain does Don Cheadle play in Space Jam: A New Legacy?", "Al-G Rhythm", "Easy"),
    ("actors-don-cheadle-13", "Don Cheadle",
     "Which film did Don Cheadle co-produce that won Best Picture?", "Crash", "Easy"),
    ("actors-don-cheadle-14", "Don Cheadle",
     "Which cartoon duck does Don Cheadle voice in DuckTales?", "Donald Duck", "Easy"),
    ("actors-don-cheadle-15", "Don Cheadle",
     "Which jazz legend does Don Cheadle play in Miles Ahead?", "Miles Davis", "Easy"),
    ("actors-don-cheadle-16", "Don Cheadle",
     "Which Broadway musical did Don Cheadle help produce to a Tony win?", "A Strange Loop", "Medium"),
    ("actors-don-cheadle-17", "Don Cheadle",
     "Where was Don Cheadle born?", "Kansas City", "Easy"),
    ("actors-don-cheadle-18", "Don Cheadle",
     "Which arts school did Don Cheadle attend?", "CalArts", "Easy"),
    ("actors-don-cheadle-19", "Don Cheadle",
     "Who is Don Cheadle's wife?", "Bridgid Coulter", "Medium"),
    ("actors-don-cheadle-20", "Don Cheadle",
     "Which advocacy project did Don Cheadle co-found with George Clooney?", "Not on Our Watch", "Medium"),
]

SOURCES = [
    ("Tom Hiddleston", "Wikipedia — Tom Hiddleston", "https://en.wikipedia.org/wiki/Tom_Hiddleston", "Biography and filmography"),
    ("Tom Hiddleston", "Wikipedia — Thor", "https://en.wikipedia.org/wiki/Thor_(film)", "Loki and Thor audition"),
    ("Tom Hiddleston", "Wikipedia — The Night Manager", "https://en.wikipedia.org/wiki/The_Night_Manager_(British_TV_series)", "Jonathan Pine and Golden Globe"),
    ("Tom Hiddleston", "Wikipedia — Only Lovers Left Alive", "https://en.wikipedia.org/wiki/Only_Lovers_Left_Alive", "Adam"),
    ("Tom Hiddleston", "Wikipedia — Crimson Peak", "https://en.wikipedia.org/wiki/Crimson_Peak", "Thomas Sharpe"),
    ("Benedict Wong", "Wikipedia — Benedict Wong", "https://en.wikipedia.org/wiki/Benedict_Wong", "Biography and filmography"),
    ("Benedict Wong", "Wikipedia — Doctor Strange", "https://en.wikipedia.org/wiki/Doctor_Strange_(2016_film)", "Wong"),
    ("Benedict Wong", "Wikipedia — 3 Body Problem", "https://en.wikipedia.org/wiki/3_Body_Problem_(TV_series)", "Da Shi"),
    ("Benedict Wong", "Wikipedia — Nine Days", "https://en.wikipedia.org/wiki/Nine_Days_(film)", "Kyo"),
    ("Benedict Wong", "Wikipedia — Black Mirror", "https://en.wikipedia.org/wiki/Black_Mirror", "Hated in the Nation"),
    ("Don Cheadle", "Wikipedia — Don Cheadle", "https://en.wikipedia.org/wiki/Don_Cheadle", "Biography and filmography"),
    ("Don Cheadle", "Wikipedia — Hotel Rwanda", "https://en.wikipedia.org/wiki/Hotel_Rwanda", "Paul Rusesabagina"),
    ("Don Cheadle", "Wikipedia — Ocean's Eleven", "https://en.wikipedia.org/wiki/Ocean%27s_Eleven", "Basher Tarr"),
    ("Don Cheadle", "Wikipedia — House of Lies", "https://en.wikipedia.org/wiki/House_of_Lies", "Marty Kaan"),
    ("Don Cheadle", "Wikipedia — Crash", "https://en.wikipedia.org/wiki/Crash_(2004_film)", "Best Picture producer credit"),
    ("Don Cheadle", "Wikipedia — A Strange Loop", "https://en.wikipedia.org/wiki/A_Strange_Loop", "Tony Award producer credit"),
]

HEADERS = ["ID", "Actor Name", "Question", "Answer", "Difficulty"]
ACTORS = ["Tom Hiddleston", "Benedict Wong", "Don Cheadle"]


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
    notes["A2"] = "20 questions each for Tom Hiddleston, Benedict Wong, and Don Cheadle."
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

    wb.properties.title = "Actor Trivia — Tom Hiddleston, Benedict Wong, Don Cheadle"
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
