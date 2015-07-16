import hashlib
import utils
import net
import command
import map


class Network:
    DEVICE = "device"
    FB = "FB"


class ClientInfo:
    def __init__(self, network, nid, token):
        self.__network = network
        self.__nid = nid
        self.__token = token

    def copy(self):
        return ClientInfo(self.network, self.network_id, self.access_token)

    def get_network(self):
        return self.__network

    def get_network_id(self):
        return self.__nid

    def get_access_token(self):
        return self.__token

    network = property(get_network)
    network_id = property(get_network_id)
    access_token = property(get_access_token)


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
        if not self.is_loaded : self.load()
        return self.__data["user_data"]["user_id"]

    def get_progress(self):
        if not self.is_loaded : self.load()
        return int(self.__data["user_data"]["progress"])

    def get_real_balance(self):
        if not self.is_loaded : self.load()
        return int(self.__data["user_data"]["real_balance"])

    def get_game_balance(self):
        if not self.is_loaded : self.load()
        return int(self.__data["user_data"]["game_balance"])

    def get_chapters(self):
        if not self.is_loaded : self.load()
        return self.__data["user_data"]["chapters"]

    def get_defs_hash(self):
        if not self.is_loaded : self.load()
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
        if not self.is_loaded : self.load()
        return self.__data["mapscreen"]["chapters"]

    def get_chapters(self):
        if not self.is_loaded : self.load()
        return self.__data["chapters"]

    is_loaded = property(get_is_loaded)

    mapscreen = property(get_mapscreen)
    chapters = property(get_chapters)


class Client:
    __DEVICE_TOKEN = "gFdsrte55UIEEWgsggagtq998joOQ"

    @staticmethod
    def __generate_access_token(network, uid):
        sha = hashlib.sha1()
        sha.update("%s_%s_%s" % (network, uid, Client.__DEVICE_TOKEN))
        return sha.hexdigest()

    def __init__(self):
        self.__info = dict()
        self.__session = None

        self.__state = ClientState(self)
        self.__defs = ClientDefs(self)
        self.__map = map.Map(self)

    def __session_get(self, network=None, nid=None, token=None, auth=None):
        if not network:
            network = Network.DEVICE
        if not nid:
            nid = utils.random_string(0x20, "0123456789abcdef")
        if not token:
            token = Client.__generate_access_token(network, nid)

        self.__info[network] = ClientInfo(network, nid, token)

        if auth is not None:
            self.__info[auth.network] = auth.copy()

        rsp = net.send(command.SessionGet(ClientInfo(network, nid, token), auth))
        self.__session = rsp["session"]

    def __session_update(self, auth=None):
        if auth is not None:
            self.__info[auth.network] = auth.copy()
        rsp = net.send(command.SessionUpdate(self.__session, auth))
        self.__session = rsp["session"]

    def get_auth_info(self, network):
        if not network in self.__info:
            return None
        return self.__info[network]

    def get_network_id(self, network):
        if not network in self.__info:
            return None
        return self.__info[network].network_id

    def get_access_token(self, network):
        if not network in self.__info:
            return None
        return self.__info[network].access_token

    def init(self, network=None, nid=None, token=None, auth=None):
        self.__session_get(network, nid, token, auth)

    def join(self, network=None, nid=None, token=None):
        if not self.__session:
            self.init()
        self.__session_update(
            {
                "network_code": str(network),
                "network_id": str(nid),
                "access_token": str(token)
            }
        )
        self.__state.load()

    def reset(self):
        net.send(command.ResetState(self.session))
        self.__state.load()

    def get_session(self):
        if not self.__session : self.__session_get()
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

