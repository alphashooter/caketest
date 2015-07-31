from plamee.cakestory import *

client = Client()
chapter = client.map.current_chapter

while chapter is not None:
    if chapter.id > 5:
        if chapter.locks <= 3:
            raise RuntimeError("Expected more than 3 locks for chapter %d." % chapter.id)

    if chapter.is_locked:
        chapter.force_buy_unlocks()
        if chapter.unlocks != chapter.locks:
            raise RuntimeError("Unlocks assertion failed for chapter %d." % chapter.id)
        chapter.unlock()

    if not chapter.force_finish():
        raise RuntimeError("Cannot finish chapter %d" % chapter.id)

    chapter = chapter.next