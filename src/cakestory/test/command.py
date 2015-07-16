import net

class ServerCommand:
    def __init__(self, name, data=None, method=net.RequestMethod.POST):
        self.name = name
        self.data = data
        self.method = method


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

class ResetState(ServerCommand):
    def __init__(self, session):
        ServerCommand.__init__(self, "/reset", {"session": session}, net.RequestMethod.POST)