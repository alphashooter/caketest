from plamee.cakestory import *

client1 = Client(network=NetworkType.FB)
client2 = Client(network=NetworkType.DEVICE)

client2.join(client1.network, client1.network_id, client1.access_token)

if not "setup_app_on_mobile" in client2.defs.data["actions_1"]["list"]:
    raise RuntimeError("Could not found action in defs.")

progress = client2.defs.data["actions_1"]["list"]["setup_app_on_mobile"]["requirements"]["user_data.progress"][0]
client2.map.get_level(progress).force_finish()

if not "user_data" in client2.state.data:
    raise RuntimeError("Could not found user data in client's state.")

if not "actions" in client2.state.data["user_data"]:
    raise RuntimeError("Could not found actions in client's state.")

if not "GC" in client2.state.data["user_data"]["actions"]:
    raise RuntimeError("Could not found GC actions in client's state.")

if not "setup_app_on_mobile" in client2.state.data["user_data"]["actions"]["GC"]:
    raise RuntimeError("Could not found setup_app_on_mobile action in client's state.")

if not client2.state.data["user_data"]["actions"]["GC"]["setup_app_on_mobile"]["ready"]:
    raise RuntimeError("Action is not ready.")

command = Commands.GetActionRewardCommand(client2, "setup_app_on_mobile", "GC")

Net.send(command)
if command.rejected:
    raise RuntimeError("Could not get reward for setup_app_on_mobile action.")