import hashlib
import utils
import net
import command
import map


class ClientState:
    def __init__(self, client):
        self._client = client
        self._data = None

    def load(self):
        self.merge(net.send(command.GetState(self._client.session)))

    def merge(self, data):
        if self._data:
            utils.merge_objects(self._data, data)
        else:
            self._data = data

    def get_is_loaded(self):
        return bool(self._data)

    def get_user_id(self):
        if not self.get_is_loaded() : self.load()
        return self._data["user_data"]["user_id"]

    def get_progress(self):
        if not self.get_is_loaded() : self.load()
        return self._data["user_data"]["progress"]

    def get_real_balance(self):
        if not self.get_is_loaded() : self.load()
        return self._data["user_data"]["real_balance"]

    def get_game_balance(self):
        if not self.get_is_loaded() : self.load()
        return self._data["user_data"]["game_balance"]

    def get_chapters(self):
        if not self.get_is_loaded() : self.load()
        return self._data["user_data"]["chapters"]

    def get_defs_hash(self):
        if not self.get_is_loaded() : self.load()
        return self._data["defs_hash"]

    is_loaded = property(get_is_loaded)

    user_id = property(get_user_id)
    progress = property(get_progress)
    chapters = property(get_chapters)
    real_balance = property(get_real_balance)
    game_balance = property(get_game_balance)

    defs_hash = property(get_defs_hash)


class ClientDefs:
    def __init__(self, client):
        self._client = client
        self._data = None

    def load(self):
        self.merge(net.send(command.GetDefs(self._client.state.defs_hash)))

    def merge(self, data):
        if self._data:
            utils.merge_objects(self._data, data)
        else:
            self._data = data

    def get_is_loaded(self):
        return bool(self._data)

    def get_mapscreen(self):
        if not self.get_is_loaded() : self.load()
        return self._data["mapscreen"]["chapters"]

    def get_chapters(self):
        if not self.get_is_loaded() : self.load()
        return self._data["chapters"]

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
        self._network = None
        self._uid = None
        self._token = None
        self._session = None

        self._state = ClientState(self)
        self._defs = ClientDefs(self)
        self._map = map.Map(self)

    def get_auth_info(self):
        if not self._network or not self._uid or not self._token:
            return None
        return {
            "network_code": self._network,
            "network_id": self._uid,
            "access_token": self._token
        }

    def session_get(self, network=None, uid=None, token=None, auth=None):
        if not network:
            network = "device"
        if not uid:
            uid = utils.random_string(0x20, "0123456789abcdef")
        if not token:
            token = Client.get_access_token(network, uid, Client.DEVICE_TOKEN)

        self._network = network
        self._uid = uid
        self._token = token

        rsp = net.send(command.SessionGet(network, uid, token, auth))
        self._session = rsp["session"]

    def session_update(self, auth=None):
        rsp = net.send(command.SessionUpdate(self._session, auth))
        self._session = rsp["session"]

    def init(self, network=None, uid=None, token=None, auth=None):
        self.session_get(network, uid, token, auth)
        self._state.load()
        self._defs.load()
        self._map.parse(self._defs.mapscreen)

    def join(self, client, network=None, uid=None, token=None):
        if not self._session:
            self.init(network, uid, token, client.get_auth_info())
        else:
            self.session_update(client.get_auth_info())
            self._state.load()

    def get_session(self):
        if not self._session : self.session_get()
        return self._session

    def get_state(self):
        if not self._state.get_is_loaded() : self._state.load()
        return self._state

    def get_defs(self):
        if not self._defs.get_is_loaded() : self._defs.load()
        return self._defs

    def get_map(self):
        if not self._map.get_is_inited() : self._map.parse(self.get_defs().mapscreen)
        return self._map

    session = property(get_session)
    state = property(get_state)
    defs = property(get_defs)
    map = property(get_map)

