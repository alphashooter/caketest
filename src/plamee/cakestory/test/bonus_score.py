import random
from plamee.cakestory import *
from plamee import log

client1 = Client()
client2 = Client()

for level in client1.map.bonus_levels:
    if not level.chapter.force_finish():
        log.error("Cannot finish chapter.")

    score = random.randint(10000, 50000)
    level.finish(score=score)

    if level.get_user_score() != score:
        raise RuntimeError("Test failed.")

    if client2.map.get_bonus_level(level.id).get_friend_score(client1) != score:
        raise RuntimeError("Test failed.")