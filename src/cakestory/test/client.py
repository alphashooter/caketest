import hashlib
import utils
import net
import command
import map
import social
import inbox
import storage
import Boosters


class Network:
    DEVICE = "device"
    FB = "FB"


class ClientInfo(object):
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


class ClientState(object):
    def __init__(self, client):
        self.__client = client
        self.__data = None

    def __autoload(self):
        if not self.is_loaded : self.load()

    def load(self):
        self.merge(net.send(command.GetState(self.__client.session)).response)

    def update(self):
        self.load()

    def merge(self, data):
        if self.__data:
            utils.merge_objects(self.__data, data)
        else:
            self.__data = data

    def get_is_loaded(self):
        return bool(self.__data)

    def get_user_id(self):
        self.__autoload()
        return self.__data["user_data"]["user_id"]

    def get_progress(self):
        self.__autoload()
        return int(self.__data["user_data"]["progress"])

    def get_real_balance(self):
        self.__autoload()
        return int(self.__data["user_data"]["real_balance"])

    def set_real_balance(self, value):
        self.add_real_balance(max(0, int(value) - self.get_real_balance()))

    def add_real_balance(self, value):
        if value > 0:
            cmd = command.AddRealBalanceCommand(self.__client, value)
            net.send(cmd)
            if cmd.rejected:
                raise RuntimeError("Cannot change real balance.")

    def get_game_balance(self):
        self.__autoload()
        return int(self.__data["user_data"]["game_balance"])

    def set_game_balance(self, value):
        self.add_game_balance(max(0, int(value) - self.get_game_balance()))

    def add_game_balance(self, value):
        if value > 0:
            cmd = command.AddGameBalanceCommand(self.__client, value)
            net.send(cmd)
            if cmd.rejected:
                raise RuntimeError("Cannot change game balance.")

    def get_chapters(self):
        self.__autoload()
        return self.__data["user_data"]["chapters"]

    def get_defs_hash(self):
        self.__autoload()
        return self.__data["defs_hash"]

    is_loaded = property(get_is_loaded)

    user_id = property(get_user_id)
    progress = property(get_progress)
    chapters = property(get_chapters)
    real_balance = property(get_real_balance, set_real_balance)
    game_balance = property(get_game_balance, set_game_balance)

    defs_hash = property(get_defs_hash)


class ClientDefs(object):
    def __init__(self, client):
        self.__client = client
        self.__data = None

    def __autoload(self):
        if not self.is_loaded : self.load()

    def merge(self, data):
        if self.__data:
            utils.merge_objects(self.__data, data)
        else:
            self.__data = data

    def load(self):
        self.merge(net.send(command.GetDefs(self.__client.state.defs_hash)).response)

    def update(self):
        self.load()

    def get_is_loaded(self):
        return bool(self.__data)

    def get_mapscreen(self):
        self.__autoload()
        return self.__data["mapscreen"]["chapters"]

    def get_chapters(self):
        self.__autoload()
        return self.__data["chapters"]

    def get_social_networks(self):
        self.__autoload()
        return self.__data["social_networks"]

    def get_unlock_price(self, count):
        self.__autoload()
        if count > 0:
            network = self.__client.network
            if not network in self.social_networks:
                network = "default"
            return self.social_networks[network]["game_items"]["unlocks"][count]["price"]["real_balance"]
        return 0

    is_loaded = property(get_is_loaded)

    social_networks = property(get_social_networks)
    mapscreen = property(get_mapscreen)
    chapters = property(get_chapters)


class Client(object):
    __DEVICE_TOKEN = "gFdsrte55UIEEWgsggagtq998joOQ"

    @staticmethod
    def __generate_access_token(network, uid):
        sha = hashlib.sha1()
        sha.update("%s_%s_%s" % (network, uid, Client.__DEVICE_TOKEN))
        return sha.hexdigest()

    def __init__(self, network=None, nid=None, token=None):
        self.__info = list()
        self.__session = None
        self.__storage_session = None
        self.__next_command = 0

        self.__state = ClientState(self)
        self.__defs = ClientDefs(self)
        self.__map = map.Map(self)
        self.__friends = []
        self.__inbox = inbox.Inbox(self)
        self.__boosters = Boosters.Boosters(self)
        self.__storage = storage.Storage(self)

        if network is not None or nid is not None:
            self.init(network, nid, token)

    def __add_network(self, info):
        if self.__has_network(info.network):
            raise RuntimeError("Network is already added.")
        self.__info.append(info.copy())

    def __get_network(self, network):
        for i in range(len(self.__info)):
            if self.__info[i].network == str(network):
                return self.__info[i]

    def __has_network(self, network):
        return self.__get_network(network) is not None

    def __convert_friend(self, friend):
        self.add_friends(friend)
        return self.get_friend(friend)

    def __get_session(self, network=None, nid=None, token=None, auth=None):
        if not network:
            network = Network.DEVICE
        if not nid:
            nid = utils.random_string(0x20, "0123456789abcdef")
        if not token:
            token = Client.__generate_access_token(network, nid)

        self.__add_network(ClientInfo(network, nid, token))

        if auth is not None:
            self.__add_network(auth)

        rsp = net.send(command.SessionGet(ClientInfo(network, nid, token), auth))
        self.__session = rsp["session"]

    def __update_session(self, auth=None):
        if auth is not None:
            self.__add_network(auth)
        rsp = net.send(command.SessionUpdate(self.__session, auth))
        self.__session = rsp["session"]

    def __get_storage_session(self):
        rsp = net.send(command.GetStorage(self.network, self.network_id, self.access_token)).response
        self.__session = rsp["session"]
        self.__storage_session = rsp["storage"]

    def get_auth_info(self, network=None):
        if not network:
            if len(self.__info) > 0:
                return self.__info[0]
            else:
                return 0
        return self.__get_network(network)

    def get_network(self, network=None):
        info = self.get_auth_info(network)
        if info is not None:
            return info.network
        return None

    def get_network_id(self, network=None):
        info = self.get_auth_info(network)
        if info is not None:
            return info.network_id
        return None

    def get_access_token(self, network=None):
        info = self.get_auth_info(network)
        if info is not None:
            return info.access_token
        return None

    def has_friend(self, descriptor):
        return self.get_friend(descriptor) is not None

    def get_friend(self, descriptor):
        if isinstance(descriptor, Client):
            for info in descriptor.__info:
                friend = self.get_friend(info.network_id)
                if friend is not None : return friend
        else:
            id = None

            if isinstance(descriptor, social.Friend):
                id = descriptor.network_id
            else:
                id = descriptor

            for friend in self.__friends:
                    if friend.network_id == str(id):
                        return friend
            for friend in self.__friends:
                    if friend.exist and str(friend.user_id) == str(id):
                        return friend
        return None

    def get_friends(self):
        return self.__friends[:]

    def add_friends(self, *args):
        for arg in args:
            if isinstance(arg, list):
                self.add_friends(*arg)
            elif isinstance(arg, tuple):
                self.add_friends(*arg)
            else:
                if self.has_friend(arg):
                    continue

                if isinstance(arg, Client):
                    self.__friends.append(social.Friend(self, arg.network, arg.network_id))
                elif isinstance(arg, social.Friend):
                    self.__friends.append(arg)
                else:
                    self.__friends.append(social.Friend(self, self.network, str(arg)))

    def send_life(self, friend):
        return self.__convert_friend(friend).send_life()

    def send_help(self, friend, level=None):
        return self.__convert_friend(friend).send_help(level)

    def request_life(self, friend):
        return self.__convert_friend(friend).request_life()

    def request_fuel(self, friend):
        return self.__convert_friend(friend).request_fuel()


    def init(self, network=None, nid=None, token=None, auth=None):
        if self.__session is not None:
            raise RuntimeError("Client session is already inited.")
        self.__get_session(network, nid, token, auth)

    def join(self, network=None, nid=None, token=None):
        if not self.__session:
            self.init()
        self.__update_session(
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
        if not self.__session : self.__get_session()
        return self.__session

    def get_storage_session(self):
        if self.__storage_session is None : self.__get_storage_session()
        return self.__storage_session

    def get_next_command(self):
        self.__next_command += 1
        return self.__next_command

    def get_state(self):
        return self.__state

    def get_defs(self):
        return self.__defs

    def get_map(self):
        return self.__map

    def get_inbox(self):
        return self.__inbox

    def get_storage(self):
        return self.__storage

    def set_storage(self, value):
        self.__storage.assign(value)

    def get_boosters(self):
        return self.__boosters

    network = property(get_network)
    network_id = property(get_network_id)
    access_token = property(get_access_token)
    session = property(get_session)
    storage_session = property(get_storage_session)
    next_command = property(get_next_command)

    state = property(get_state)
    defs = property(get_defs)
    map = property(get_map)
    friends = property(get_friends)
    inbox = property(get_inbox)
    boosters = property(get_boosters)
    storage = property(get_storage, set_storage)

