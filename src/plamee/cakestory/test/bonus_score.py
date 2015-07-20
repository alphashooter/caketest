import random
from plamee.Test import Test
from plamee.cakestory import *

client1 = Client()
client2 = Client()

Test.start_module("bonus_score", len(client1.map.bonus_levels))

for level in client1.map.bonus_levels:
    Test.next_iteration()

    score = random.randint(10000, 50000)
    level.chapter.force_finish()

    level.finish(score=score)
    if level.get_user_score() != score:
        raise RuntimeError()

    if client2.map.get_bonus_level(level.id).get_friend_score(client1) != score:
        raise RuntimeError()
