import random
from plamee.cakestory import *

client1 = Client()
client2 = Client()

for level in client1.map.bonus_levels:
    score = random.randint(10000, 50000)
    level.chapter.force_finish()

    level.finish(score=score)
    if level.get_user_score() != score:
        raise RuntimeError()

    if client2.map.get_bonus_level(level.id).get_friend_score(client1) != score:
        raise RuntimeError()