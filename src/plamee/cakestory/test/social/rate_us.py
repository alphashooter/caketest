import random
from plamee.cakestory import *

client = Client()

defs = client.defs.social_networks[client.network]

if not "rate_game" in defs:
    raise RuntimeError("Object 'rate_game' is not found.")

defs = defs["rate_game"]

if "require" in defs:
    if "progress" in defs["require"]:
        client.map.get_level(defs["require"]["progress"]).force_finish()

#

version = None
country = random.choice(defs["countries"].keys())
rewards = defs["countries"][country]["rewards"]

if client.network.mobile:
    version = client.state["versions"]["min_mobile_version"]
else:
    version = client.state["versions"]["min_canvas_version"]


command = Commands.ExecuteCommand(client, "rate_game", {"network_code": str(client.network), "country_code": country, "client_version": version})
Net.send(command)

#

if command.rejected:
    raise RuntimeError("Server command was rejected.")

if not "latest_rated_versions" in command["user_data"] or not str(client.network) in command["user_data"]["latest_rated_versions"]:
    raise RuntimeError("State was not updated.")

for reward in rewards["first"]:
    if reward == "real_balance":
        if client.real_balance != rewards["first"][reward]:
            raise RuntimeError("Reward assertion failed.")