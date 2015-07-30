from plamee.cakestory import *

client = Client()
if not client.map.last_chapter.force_finish():
    raise RuntimeError("Test failed.")