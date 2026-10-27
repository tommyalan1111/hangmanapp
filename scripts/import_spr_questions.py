import json
from pathlib import Path
from openpyxl import load_workbook

root=Path(r"E:\Work\Hangman app")
wb=load_workbook(root/"docs/Reel-Hangman-Question-Bank.xlsx", data_only=True)
ws=wb["Movies"]
rows=[]
for row in ws.iter_rows(min_row=2, max_col=5, values_only=True):
    if row[0] and str(row[0]).startswith("movies-saving-private-ryan-"):
        rows.append(row)
rows.sort(key=lambda r: int(str(r[0]).rsplit("-",1)[1]))
assert len(rows)==29, len(rows)

facts={
1:"Tom Hanks was nominated for Best Actor for playing Captain Miller.",
2:"Damon played Private James Francis Ryan, the soldier the squad is sent to find.",
3:"The film's opening recreates the D-Day landings in Normandy on June 6, 1944.",
4:"Spielberg won Best Director for the film, one of its five Academy Awards.",
5:"The Ryan family loses three brothers before James is found.",
6:"Dog Green was one of the sectors of Omaha Beach depicted in the opening.",
7:"Barry Pepper plays Private Daniel Jackson, the squad's sharpshooter.",
8:"Private Ryan was serving with the 101st Airborne Division.",
9:"Rodat wrote the screenplay, which was nominated for an Academy Award.",
10:"The film won five Oscars, including Best Director and Best Cinematography.",
11:"Vin Diesel plays Private Adrian Caparzo, killed by a sniper in Neuville.",
12:"Upham admits he has not held a weapon since basic training.",
13:"The captain's full name is John H. Miller; the H. is never explained on screen.",
14:"Mellish is played by Adam Goldberg; Caparzo calls him Fish.",
15:"Private Ryan's full name is James Francis Ryan.",
16:"Eight men set out from the beach in Miller's squad.",
17:"After Caparzo's death, Upham is told to fill the squad's canteens.",
18:"John Williams composed the film's score.",
19:"Miller explains that gripes go up the chain of command, never down.",
20:"The squad's first stop is Neuville, where they meet a French family.",
21:"The squad's pool on Miller's civilian life reaches $300.",
22:"Tom Sizemore plays Sergeant Michael Horvath, Miller's right-hand man.",
23:"The soldiers improvise sticky bombs from socks and explosives to stop tanks.",
24:"Caparzo is shot and falls against a piano in the ruined town.",
25:"The bridge's last-ditch defensive position is nicknamed the Alamo.",
26:"Caparzo gives Mellish the Hitler Youth knife and calls it a Shabbat challah cutter.",
27:"Upham kills one German soldier, the man the squad had earlier released.",
28:"Horvath collects soil from France, Italy, and Africa as a reminder of his service.",
29:"Reiben and Upham are the two members of Miller's squad who survive the final battle.",
}
overrides={21:"THREE HUNDRED DOLLARS"}
dmap={"Easy":1,"Medium":2,"Hard":3}
entries=[]
for row in rows:
    sid,name,question,answer,difficulty=row
    n=int(str(sid).rsplit("-",1)[1])
    ans=overrides.get(n,str(answer))
    clue="Saving Private Ryan: "+str(question)
    entries.append((str(sid),ans.upper(),clue,facts[n],dmap[str(difficulty)]))

path=root/"src/data/movies.ts"
text=path.read_text(encoding="utf-8")
if "const movieTrivia" not in text:
    marker='  makePuzzle("movies", answer, clue, fact, difficulty);\n'
    assert marker in text
    helper='''\nconst movieTrivia = (id: string, answer: string, clue: string, fact: string, difficulty: 1 | 2 | 3): Puzzle => ({\n  id,\n  category: "movies",\n  answer: answer.toUpperCase(),\n  clue,\n  fact,\n  difficulty,\n});\n'''
    text=text.replace(marker, marker+helper, 1)
# Insert before final ];, preserving the array close.
insert_at=text.rfind("\n];")
assert insert_at!=-1
block="\n"
for sid,ans,clue,fact,difficulty in entries:
    if f'"{sid}"' in text:
        continue
    block += f'  movieTrivia(\n    {json.dumps(sid)},\n    {json.dumps(ans, ensure_ascii=False)},\n    {json.dumps(clue, ensure_ascii=False)},\n    {json.dumps(fact, ensure_ascii=False)},\n    {difficulty},\n  ),\n'
text=text[:insert_at]+block+text[insert_at:]
path.write_text(text, encoding="utf-8")
print("inserted", len(entries), "entries; movieTrivia helper present:", "const movieTrivia" in text)
