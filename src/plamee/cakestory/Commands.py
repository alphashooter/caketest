import re

import plamee.utils as utils
import Net


class ServerCommand(object):
    def __init__(self, name, data=None, method=Net.RequestMethod.POST):
        self.name = name
        self.data = data
        self.method = method

    def __iter__(self):
        return self.response.__iter__()

    def __contains__(self, item):
        return item in self.response

    def __getitem__(self, item):
        return self.response[item]

    def __setitem__(self, item, value):
        self.response[item] = value

    def process(self, response):
        self.response = response
        pass


class SessionGet(ServerCommand):
    def __init__(self, info, auth=None):
        data = {
            "client_network": {
                "network_code": str(info.network),
                "network_id": info.network_id,
                "access_token": info.access_token
            }
        }
        if auth:
            data["auth_network"] = {
                "network_code": str(auth.network),
                "network_id": auth.network_id,
                "access_token": auth.access_token
            }
        ServerCommand.__init__(self, "/session/get", data, Net.RequestMethod.POST)


class SessionUpdate(ServerCommand):
    def __init__(self, session, auth=None):
        data = {"session": session}
        if auth:
            data["auth_network"] = {
                "network_code": str(auth.network),
                "network_id": auth.network_id,
                "access_token": auth.access_token
            }
        ServerCommand.__init__(self, "/session/update", data, Net.RequestMethod.POST)


class GetState(ServerCommand):
    def __init__(self, session):
        ServerCommand.__init__(self, "/init", {"session": session}, Net.RequestMethod.POST)


class GetDefs(ServerCommand):
    def __init__(self, hash):
        ServerCommand.__init__(self, "/defs", {"hash": hash}, Net.RequestMethod.GET)


class GetLevel(ServerCommand):
    def __init__(self, hash):
        ServerCommand.__init__(self, "/map/level", {"hash": hash}, Net.RequestMethod.GET)


class GetChapter(ServerCommand):
    def __init__(self, hash):
        ServerCommand.__init__(self, "/map/chapter", {"hash": hash}, Net.RequestMethod.GET)


class QueryLevels(ServerCommand):
    def __init__(self, session, levels):
        ServerCommand.__init__(self, "/query/levels", {"session": session, "levels": levels[:]}, Net.RequestMethod.POST)


class QueryUsers(ServerCommand):
    def __init__(self, session, network, nids):
        credentials = utils.sdict()
        credentials[network] = nids[:]

        ServerCommand.__init__(
            self,
            "/query/users",
            {
                "session": session,
                "credentials": credentials
            },
            Net.RequestMethod.POST
        )


class QueryUsersProgress(ServerCommand):
    def __init__(self, session, uids):
        ServerCommand.__init__(
            self,
            "/query/users/progress",
            {
                "session": session,
                "users": uids[:]
            },
            Net.RequestMethod.POST
        )


class QueryUsersLevels(ServerCommand):
    def __init__(self, session, levels, uids):
        ServerCommand.__init__(
            self,
            "/query/users/levels",
            {
                "session": session,
                "levels": levels[:],
                "users": uids[:]
            },
            Net.RequestMethod.POST
        )


class QueryUsersTime(ServerCommand):
    def __init__(self, session, uids):
        ServerCommand.__init__(
            self,
            "/query/users/time",
            {
                "session": session,
                "users": uids[:]
            },
            Net.RequestMethod.POST
        )


class GetMessages(ServerCommand):
    def __init__(self, session):
        ServerCommand.__init__(self, "/messages/unread", {"session": str(session)}, Net.RequestMethod.POST)


class GetStorage(ServerCommand):
    def __init__(self, network, nid, token):
        ServerCommand.__init__(self, "/storage/get", {"client_network": {"network_code": str(network), "network_id": str(nid), "access_token": str(token)}}, Net.RequestMethod.POST)


class FetchStorage(ServerCommand):
    def __init__(self, storage, session):
        ServerCommand.__init__(self, "/storage/fetch", {"storage": str(storage), "session": str(session)}, Net.RequestMethod.POST)


class UpdateStorage(ServerCommand):
    def __init__(self, storage, session, data):
        ServerCommand.__init__(self, "/storage/store", {"storage": str(storage), "session": str(session), "data": data.copy()}, Net.RequestMethod.POST)


class ResetState(ServerCommand):
    def __init__(self, session):
        ServerCommand.__init__(self, "/reset", {"session": session}, Net.RequestMethod.POST)


class ExecuteCommand(ServerCommand):
    def __init__(self, client, name, params):
        self.__client = client
        self.__id = self.__client.next_command

        ServerCommand.__init__(
            self,
            "/commands",
            {
                "session": client.session,
                "commands": [
                    {
                        "id": self.__id,
                        "name": name,
                        "params": params.copy()
                    }
                ]
            },
            Net.RequestMethod.POST
        )

    def __get_client(self):
        return self.__client

    def process(self, response):
        ServerCommand.process(self, response)
        self.rejected = False
        if "rejected_commands" in response:
            for id in response["rejected_commands"]:
                if id == self.__id:
                    self.rejected = True
                    break
        self.__client.state.merge(response)
        for event in response["events"]:
            for event_name in event:
                if event_name == "add_boosters":
                    for booster_name in event[event_name]:
                        booster = self.__client.boosters[booster_name]
                        booster.set_count(booster.get_count() + event[event_name][booster_name]["count"])

    client = property(__get_client)

class FinishLevelCommand(ExecuteCommand):
    def __init__(self, client, level, score, used_moves=None, used_time=None, used_lives=None, used_boosters=None):
        params = {
            "level": int(level),
            "score": int(score)
        }
        if used_moves is not None:
            params["used_moves"] = int(used_moves)
        if used_time is not None:
            params["used_time"] = int(used_time)
        if used_lives is not None:
            params["used_lives"] = int(used_lives)
        if used_boosters is not None:
            if isinstance(used_boosters, list):
                used_boosters_map = utils.sdict()
                for i in range(len(used_boosters)):
                    used_boosters_map[used_boosters[i]] = used_boosters_map[used_boosters[i]] + 1 if used_boosters[i] in used_boosters_map else 1
                params["used_boosters"] = used_boosters_map
            else:
                params["used_boosters"] = utils.sdict(used_boosters)

        ExecuteCommand.__init__(self, client, "finish_level", params)


class FinishBonusLevelCommand(ExecuteCommand):
    def __init__(self, client, level, score, rewards=None):
        if rewards is None:
            rewards = []

        params = {
            "level": str(level),
            "score": int(score),
            "rewards": list(rewards)
        }

        ExecuteCommand.__init__(self, client, "finish_bonus_level", params)


class LoseLevelCommand(ExecuteCommand):
    def __init__(self, client, level, completion=None, used_boosters=None):
        level = str(level)
        if re.match(r"^\d+$", level):
            level = int(level)

        if completion is None:
            completion = 0
        else:
            completion = int(completion)

        if used_boosters is None:
            used_boosters = 0
        elif isinstance(used_boosters, dict):
            used_boosters = int( sum(used_boosters.values()) )
        elif isinstance(used_boosters, list):
            used_boosters = len(used_boosters)
        else:
            used_boosters = int(used_boosters)

        params = {
            "level_id": level,
            "completion_rate": completion,
            "used_boosters_count": used_boosters
        }

        ExecuteCommand.__init__(self, client, "lose_level", params)


class UnlockChapterCommand(ExecuteCommand):
    def __init__(self, client):
        ExecuteCommand.__init__(self, client, "unlock_chapter", {"api_version": "1"})


class BuyChapterUnlocksCommand(ExecuteCommand):
    def __init__(self, client):
        network = str(client.network)
        if not network in client.defs.social_networks:
            network = "default"
        ExecuteCommand.__init__(self, client, "buy_chapter_unlocks", {"network_code": network, "api_version": "1"})


class BuyBoosterCommand(ExecuteCommand):
    def __init__(self, client, pack):
        network = str(client.network)
        if not network in client.defs.social_networks:
            network = "default"
        ExecuteCommand.__init__(self, client, "buy_booster_pack", {"network_code": network, "name": str(pack)})


class SendLifeCommand(ExecuteCommand):
    def __init__(self, client, uid):
        ExecuteCommand.__init__(self, client, "send_life", {"user_id": int(uid)})


class SendHelpCommand(ExecuteCommand):
    def __init__(self, client, uid, level):
        ExecuteCommand.__init__(self, client, "send_help_for_level", {"user_id": int(uid), "level": int(level)})


class RequestLifeCommand(ExecuteCommand):
    def __init__(self, client, uid):
        ExecuteCommand.__init__(self, client, "request_life", {"user_id": int(uid)})


class RequestFuelCommand(ExecuteCommand):
    def __init__(self, client, uid):
        ExecuteCommand.__init__(self, client, "request_fuel", {"user_id": int(uid)})


class ReadMessageCommand(ExecuteCommand):
    def __init__(self, client, id):
        ExecuteCommand.__init__(self, client, "read_message", {"message_id": int(id)})


class DeleteMessagesCommand(ExecuteCommand):
    def __init__(self, client, ids):
        ExecuteCommand.__init__(self, client, "delete_messages", {"ids": ids[:]})


class AddRealBalanceCommand(ExecuteCommand):
    def __init__(self, client, value):
        ExecuteCommand.__init__(self, client, "idkfa", {"real_balance": int(value)})


class AddGameBalanceCommand(ExecuteCommand):
    def __init__(self, client, value):
        ExecuteCommand.__init__(self, client, "idkfa", {"game_balance": int(value)})