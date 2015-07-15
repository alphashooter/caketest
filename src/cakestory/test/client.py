import hashlib
import utils
import net
import command
import map


class ClientState:
    def __init__(self, client):
        self.client = client
        self.data = None

    def load(self):
        self.merge(net.Connection.instance.send_post(command.CommandInit(self.client.session)))

    def merge(self, data):
        if self.data:
            utils.merge_objects(self.data, data)
        else:
            self.data = data

    def get_is_loaded(self):
        return bool(self.data)

    def get_user_id(self):
        if not self.get_is_loaded() : self.load()
        return self.data["user_data"]["user_id"]

    def get_progress(self):
        if not self.get_is_loaded() : self.load()
        return self.data["user_data"]["progress"]

    def get_real_balance(self):
        if not self.get_is_loaded() : self.load()
        return self.data["user_data"]["real_balance"]

    def get_game_balance(self):
        if not self.get_is_loaded() : self.load()
        return self.data["user_data"]["game_balance"]

    def get_chapters(self):
        if not self.get_is_loaded() : self.load()
        return self.data["user_data"]["chapters"]

    def get_defs_hash(self):
        if not self.get_is_loaded() : self.load()
        return self.data["defs_hash"]

    is_loaded = property(get_is_loaded)

    user_id = property(get_user_id)
    progress = property(get_progress)
    chapters = property(get_chapters)
    real_balance = property(get_real_balance)
    game_balance = property(get_game_balance)

    defs_hash = property(get_defs_hash)


class ClientDefs:
    def __init__(self, client):
        self.client = client
        self.data = None

    def load(self):
        self.merge(net.Connection.instance.send_get(command.CommandGetDefs(self.client.state.defs_hash)))

    def merge(self, data):
        if self.data:
            utils.merge_objects(self.data, data)
        else:
            self.data = data

    def get_is_loaded(self):
        return bool(self.data)

    def get_mapscreen(self):
        if not self.get_is_loaded() : self.load()
        return self.data["mapscreen"]["chapters"]

    def get_chapters(self):
        if not self.get_is_loaded() : self.load()
        return self.data["chapters"]

    is_loaded = property(get_is_loaded)

    mapscreen = property(get_mapscreen)
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

        self.state = ClientState(self)
        self.defs = ClientDefs(self)
        self.map = map.Map(self)

    def get_auth_info(self):
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

    def init(self, network=None, uid=None, token=None, auth=None):
        self.session_get(network, uid, token, auth)
        self.state.load()
        self.defs.load()
        self.map.parse(self.defs.mapscreen)

    def join(self, client, network=None, uid=None, token=None):
        if not self.session:
            self.init(network, uid, token, client.get_auth_info())
        else:
            self.session_update(client.get_auth_info())
            self.state.load()

