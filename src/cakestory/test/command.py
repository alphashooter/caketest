import net

class Command:
    def __init__(self, name, data=None, method=net.RequestMethod.POST):
        self.name = name
        self.data = data
        self.method = method


class SessionGet(Command):
    def __init__(self, network, uid, token, auth=None):
        data = {
            "client_network": {
                "network_code": network,
                "network_id": uid,
                "access_token": token
            }
        }
        if auth:
            data["auth_network"] = auth
        Command.__init__(self, "/session/get", data, net.RequestMethod.POST)


class SessionUpdate(Command):
    def __init__(self, session, auth=None):
        data = {"session": session}
        if auth:
            data["auth_network"] = auth
        Command.__init__(self, "/session/update", data, net.RequestMethod.POST)


class GetState(Command):
    def __init__(self, session):
        Command.__init__(self, "/init", {"session": session}, net.RequestMethod.POST)


class GetDefs(Command):
    def __init__(self, hash):
        Command.__init__(self, "/defs", {"hash": hash}, net.RequestMethod.GET)


class GetLevel(Command):
    def __init__(self, hash):
        Command.__init__(self, "/map/level", {"hash": hash}, net.RequestMethod.GET)


class GetChapter(Command):
    def __init__(self, hash):
        Command.__init__(self, "/map/chapter", {"hash": hash}, net.RequestMethod.GET)

class QueryLevels(Command):
    def __init__(self, session, levels):
        Command.__init__(self, "/query/levels", {"session": session, "levels": levels}, net.RequestMethod.POST)