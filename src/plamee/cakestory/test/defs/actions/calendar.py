from plamee.cakestory import *

defs = Net.send(Commands.ServerCommand("/defs?group=default", None, Net.RequestMethod.GET)).response


actions_start = dict(
    filter(lambda item: bool(item[1]["type"] == "special_offer_start"), defs["actions_1"]["list"].items()))
actions_epic = dict(
    filter(lambda item: bool(item[1]["type"] == "epic_discount"),defs["actions_1"]["list"].items()))
actions_process = dict(
    filter(lambda item: bool(item[1]["type"] == "special_offer_process"), defs["actions_1"]["list"].items()))

with open("actions.txt", "w") as actionfile:
    for action in actions_start.values():
        actionfile.write(action["type"] + " " + str(action["start_time"]) + " " + str(action["end_time"]) + " " + str(action["discount"]) + "\n")
        action.clear()

    for action in actions_epic.values():
        actionfile.write(action["type"] + " " + str(action["start_time"]) + " " + str(action["end_time"]) + " " + str(action["offers"]) + "\n")
        action.clear()

    for action in actions_process.values():
        actionfile.write(action["type"] + " " + str(action["start_time"]) + " " + str(action["end_time"]) + " " + str(action["discount"]) + "\n")
        action.clear()
