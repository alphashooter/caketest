from plamee.cakestory import *

client = Client()

chapter = client.map.get_chapter(13)

if not chapter:
    raise RuntimeError("Chapter does not exist.")

if len(chapter.levels) != 15:
    raise RuntimeError("Chapter must have 15 levels.")

try:
    chapter.load(True)
except:
    raise RuntimeError("Cannot load levels.")

dialogs = filter(lambda dialog: bool(str(dialog).find("chapter_13") >= 0), client.defs["client"]["dialogs"].keys())

if len(dialogs) == 0:
    raise RuntimeError("Cannot find dialogs for chapter in client's defs.")