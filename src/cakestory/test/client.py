import hashlib
import utils
import net
import command
import map


class ClientState:
    def __init__(self, client):
        self.__client = client
        self.__data = None

    def load(self):
        self.merge(net.send(command.GetState(self.__client.session)))

    def merge(self, data):
        if self.__data:
            utils.merge_objects(self.__data, data)
        else:
            self.__data = data

    def get_is_loaded(self):
        return bool(self.__data)

    def get_user_id(self):
        if not self.get_is_loaded() : self.load()
        return self.__data["user_data"]["user_id"]

    def get_progress(self):
        if not self.get_is_loaded() : self.load()
        return int(self.__data["user_data"]["progress"])

    def get_real_balance(self):
        if not self.get_is_loaded() : self.load()
        return int(self.__data["user_data"]["real_balance"])

    def get_game_balance(self):
        if not self.get_is_loaded() : self.load()
        return int(self.__data["user_data"]["game_balance"])

    def get_chapters(self):
        if not self.get_is_loaded() : self.load()
        return self.__data["user_data"]["chapters"]

    def get_defs_hash(self):
        if not self.get_is_loaded() : self.load()
        return self.__data["defs_hash"]

    is_loaded = property(get_is_loaded)

    user_id = property(get_user_id)
    progress = property(get_progress)
    chapters = property(get_chapters)
    real_balance = property(get_real_balance)
    game_balance = property(get_game_balance)

    defs_hash = property(get_defs_hash)


class ClientDefs:
    def __init__(self, client):
        self.__client = client
        self.__data = None

    def load(self):
        self.merge(net.send(command.GetDefs(self.__client.state.defs_hash)))

    def merge(self, data):
        if self.__data:
            utils.merge_objects(self.__data, data)
        else:
            self.__data = data

    def get_is_loaded(self):
        return bool(self.__data)

    def get_mapscreen(self):
        if not self.get_is_loaded() : self.load()
        return self.__data["mapscreen"]["chapters"]

    def get_chapters(self):
        if not self.get_is_loaded() : self.load()
        return self.__data["chapters"]

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
        self.__network = None
        self.__uid = None
        self.__token = None
        self.__session = None

        self.__state = ClientState(self)
        self.__defs = ClientDefs(self)
        self.__map = map.Map(self)

    def get_auth_info(self):
        if not self.__network or not self.__uid or not self.__token:
            return None
        return {
            "network_code": self.__network,
            "network_id": self.__uid,
            "access_token": self.__token
        }

    def session_get(self, network=None, uid=None, token=None, auth=None):
        if not network:
            network = "device"
        if not uid:
            uid = utils.random_string(0x20, "0123456789abcdef")
        if not token:
            token = Client.get_access_token(network, uid, Client.DEVICE_TOKEN)

        self.__network = network
        self.__uid = uid
        self.__token = token

        rsp = net.send(command.SessionGet(network, uid, token, auth))
        self.__session = rsp["session"]

    def session_update(self, auth=None):
        rsp = net.send(command.SessionUpdate(self.__session, auth))
        self.__session = rsp["session"]

    def init(self, network=None, uid=None, token=None, auth=None):
        self.session_get(network, uid, token, auth)
        self.__state.load()
        self.__defs.load()
        self.__map.parse(self.__defs.mapscreen)

    def join(self, client, network=None, uid=None, token=None):
        if not self.__session:
            self.init(network, uid, token, client.get_auth_info())
        else:
            self.session_update(client.get_auth_info())
            self.__state.load()

    def get_session(self):
        if not self.__session : self.session_get()
        return self.__session

    def get_state(self):
        if not self.__state.get_is_loaded() : self.__state.load()
        return self.__state

    def get_defs(self):
        if not self.__defs.get_is_loaded() : self.__defs.load()
        return self.__defs

    def get_map(self):
        if not self.__map.get_is_inited() : self.__map.parse(self.get_defs().mapscreen)
        return self.__map

    session = property(get_session)
    state = property(get_state)
    defs = property(get_defs)
    map = property(get_map)

