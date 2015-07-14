class Command:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data


class CommandSessionGet(Command):
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
        Command.__init__(self, "/session/get", data)


class CommandSessionUpdate(Command):
    def __init__(self, session, auth=None):
        data = {"session": session}
        if auth:
            data["auth_network"] = auth
        Command.__init__(self, "/session/update", data)


class CommandInit(Command):
    def __init__(self, session):
        Command.__init__(self, "/init", {"session": session})


class CommandGetDefs(Command):
    def __init__(self, hash):
        Command.__init__(self, "/defs", {"hash": hash})


class CommandGetLevel(Command):
    def __init__(self, hash):
        Command.__init__(self, "/map/level", {"hash": hash})


class CommandGetChapter(Command):
    def __init__(self, hash):
        Command.__init__(self, "/map/chapter", {"hash": hash})