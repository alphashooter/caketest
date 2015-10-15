from plamee.cakestory import *

client = Client()

actions = dict(filter(lambda item: bool(item[1]["type"] == "pushing_payment"), client.defs["actions_1"]["list"].items()))

for action in actions.values():
    if not "countries" in action or not len(action["countries"]):
        raise RuntimeError("Target countries not found.")
    if not "platforms" in action or not len(action["platforms"]):
        raise RuntimeError("Target platforms not found.")
    if not "events" in action or not len(action["events"].items()):
        raise RuntimeError("Action events not found.")

    #

    if not "requirements" in action or not len(action["requirements"].items()):
        raise RuntimeError("Action requirements not found.")

    requirements =  action["requirements"]
    for requirement in requirements.items():
        field = client.state
        selectors = requirement[0].split(".")

        for i in range(len(selectors)):
            selector = selectors[i]
            if not selector in field:
                raise RuntimeError("Field '%s' not found in client state." % ".".join(selectors[:i]))
            field = field[selector]

        for value in requirement[1]:
            if type(field) is not type(value):
                raise RuntimeError("Field '%s' type assertion failed." % requirement)

    if not "rewards" in action or not len(action["rewards"]):
        raise RuntimeError("Rewards not found.")

    #

    rewards = action["rewards"]
    for reward in rewards:
        if not "progress" in reward:
            raise RuntimeError("Progress for reward not found.")
        if not "bonus_count" in reward:
            raise RuntimeError("Bonuses count for reward not found.")
        if not "bonuses" in reward or not len(reward["bonuses"]):
            raise RuntimeError("Bonuses for reward not found.")
        for bonus in reward["bonuses"]:
            if not len(bonus.items()):
                raise RuntimeError("Bonus field is empty.")