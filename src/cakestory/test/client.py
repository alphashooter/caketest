import hashlib
import utils
import net
import command
import map


class ClientState:
    def __init__(self):
        self.data = {}

    def merge(self, data):
        utils.merge_objects(self.data, data)

    def get_user_id(self):
        return self.data["user_data"]["user_id"]

    def get_progress(self):
        return self.data["user_data"]["progress"]

    def get_real_balance(self):
        return self.data["user_data"]["real_balance"]

    def get_game_balance(self):
        return self.data["user_data"]["game_balance"]

    def get_defs_hash(self):
        return self.data["defs_hash"]

    user_id = property(get_user_id)
    progress = property(get_progress)
    real_balance = property(get_real_balance)
    game_balance = property(get_game_balance)
    defs_hash = property(get_defs_hash)


class ClientDefs:
    def __init__(self):
        self.data = {}

    def load(self, hash):
        self.merge(net.Connection.instance.send_get(command.CommandGetDefs(hash)))

    def merge(self, data):
        utils.merge_objects(self.data, data)

    def get_chapters(self):
        chapters = list()
        for i in range(len(self.data["mapscreen"]["chapters"])):
            chapter = self.data["mapscreen"]["chapters"][i].copy()
            # FIXME: It would be better to merge state.chapters object with state.mapscreen.chapters
            utils.merge_objects(
                chapter,
                self.data["chapters"][str(chapter["id"])] # FIXME: Why chapters ids in state.mapscreen.chapters are ints but in state.chapters are strings?
            )
            chapters.append(chapter)
        return chapters

    chapters = property(get_chapters)


class Client:
    DEVICE_TOKEN = "gFdsrte55UIEEWgsggagtq998joOQ"

    @staticmethod
    def get_access_token(network, uid, token):
        sha = hashlib.sha1()
        sha.update("%s_%s_%s" % (network, uid, token))
        return sha.hexdigest()

    def __init__(self):
        self.network = None
        self.uid = None
        self.token = None
        self.session = None

        self.state = ClientState()
        self.defs = ClientDefs()
        self.chapters = None

    def get_info(self):
        if not self.network or not self.uid or not self.token:
            return None
        return {
            "network_code": self.network,
            "network_id": self.uid,
            "access_token": self.token
        }

    def session_get(self, network=None, uid=None, token=None, auth=None):
        if not network:
            network = "device"
        if not uid:
            uid = utils.random_string(0x20, "0123456789abcdef")
        if not token:
            token = Client.get_access_token(network, uid, Client.DEVICE_TOKEN)

        self.network = network
        self.uid = uid
        self.token = token

        rsp = net.Connection.instance.send_post(command.CommandSessionGet(network, uid, token, auth))
        self.session = rsp["session"]

    def session_update(self, auth=None):
        rsp = net.Connection.instance.send_post(command.CommandSessionUpdate(self.session, auth))
        self.session = rsp["session"]

    def state_update(self):
        self.state.merge(net.Connection.instance.send_post(command.CommandInit(self.session)))

    def defs_update(self):
        self.defs.load(self.state.defs_hash)

    def chapters_update(self):
        self.chapters = list(map.Chapter(self.defs.chapters[i]) for i in range(len(self.defs.chapters)))
        for i in range(len(self.chapters)):
            self.chapters[i].load()

    def init(self, network=None, uid=None, token=None, auth=None):
        self.session_get(network, uid, token, auth)
        self.state_update()
        self.defs_update()
        self.chapters_update()

    def join(self, client, network=None, uid=None, token=None):
        if not self.session:
            self.session_get(network, uid, token, client.get_info())
        else:
            self.session_update(client.get_info())
        self.state_update()
        self.defs_update()

