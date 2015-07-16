import re
import net
import utils

class ServerCommand:
    def __init__(self, name, data=None, method=net.RequestMethod.POST):
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
                "network_code": info.network,
                "network_id": info.network_id,
                "access_token": info.access_token
            }
        }
        if auth:
            data["auth_network"] = {
                "network_code": auth.network,
                "network_id": auth.network_id,
                "access_token": auth.access_token
            }
        ServerCommand.__init__(self, "/session/get", data, net.RequestMethod.POST)


class SessionUpdate(ServerCommand):
    def __init__(self, session, auth=None):
        data = {"session": session}
        if auth:
            data["auth_network"] = {
                "network_code": auth.network,
                "network_id": auth.network_id,
                "access_token": auth.access_token
            }
        ServerCommand.__init__(self, "/session/update", data, net.RequestMethod.POST)


class GetState(ServerCommand):
    def __init__(self, session):
        ServerCommand.__init__(self, "/init", {"session": session}, net.RequestMethod.POST)


class GetDefs(ServerCommand):
    def __init__(self, hash):
        ServerCommand.__init__(self, "/defs", {"hash": hash}, net.RequestMethod.GET)


class GetLevel(ServerCommand):
    def __init__(self, hash):
        ServerCommand.__init__(self, "/map/level", {"hash": hash}, net.RequestMethod.GET)


class GetChapter(ServerCommand):
    def __init__(self, hash):
        ServerCommand.__init__(self, "/map/chapter", {"hash": hash}, net.RequestMethod.GET)


class QueryLevels(ServerCommand):
    def __init__(self, session, levels):
        ServerCommand.__init__(self, "/query/levels", {"session": session, "levels": levels[:]}, net.RequestMethod.POST)


class QueryUsers(ServerCommand):
    def __init__(self, session, network, nids):
        credentials = dict()
        credentials[network] = nids[:]

        ServerCommand.__init__(
            self,
            "/query/users",
            {
                "session": session,
                "credentials": credentials
            },
            net.RequestMethod.POST
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
            net.RequestMethod.POST
        )


class QueryUsersLevels(ServerCommand):
    def __init__(self, session, levels, uids):
        ServerCommand.__init__(
            self,
            "/query/users/progress",
            {
                "session": session,
                "levels": levels[:],
                "users": uids[:]
            },
            net.RequestMethod.POST
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
            net.RequestMethod.POST
        )


class ResetState(ServerCommand):
    def __init__(self, session):
        ServerCommand.__init__(self, "/reset", {"session": session}, net.RequestMethod.POST)


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
            net.RequestMethod.POST
        )

    def process(self, response):
        ServerCommand.process(self, response)
        self.rejected = False
        if "rejected_commands" in response:
            for id in response["rejected_commands"]:
                if id == self.__id:
                    self.rejected = True
                    break
        self.__client.state.merge(response)

class FinishLevelCommand(ExecuteCommand):
    def __init__(self, client, level, score, used_moves=None, used_time=None, used_lives=None, used_boosters=None):
        level = str(level)
        if re.match(r"^\d+$", level):
            level = int(level)

        params = {
            "level": level,
            "score": int(score)
        }
        if used_moves is not None:
            params["used_moves"] = int(used_moves)
        if used_time is not None:
            params["used_time"] = int(used_time)
        if used_lives is not None:
            params["used_lives"] = int(used_lives)
        if used_boosters is not None:
            params["used_boosters"] = utils.sdict(used_boosters)

        ExecuteCommand.__init__(self, client, "finish_level", params)

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
            used_boosters = len(used_boosters)
        else:
            used_boosters = int(used_boosters)

        params = {
            "level_id": level,
            "completion_rate": completion,
            "used_boosters_count": used_boosters
        }

        ExecuteCommand.__init__(self, client, "lose_level", params)