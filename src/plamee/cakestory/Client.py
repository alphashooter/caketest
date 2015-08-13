import hashlib

import plamee.utils as utils
import Net
import Commands
import Map
import Social
import Inbox
import Storage
import Boosters


class NetworkType:
    """
    Enumeration class which contains common network types.
    """

    NAMES = ["device", "FB", "OK", "MM", "VK"]

    DEVICE = None
    FB = None
    OK = None
    MM = None
    VK = None

    def __init__(self, value, mobile=False):
        value = str(value)
        if not value in self.NAMES:
            raise RuntimeError("Network %s is not found." % value)
        self.value = value
        self.mobile = mobile

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == str(other)

    def __ne__(self, other):
        return self.value != str(other)


NetworkType.DEVICE = NetworkType("device", True)
NetworkType.FB = NetworkType("FB")
NetworkType.OK = NetworkType("OK")
NetworkType.MM = NetworkType("MM")
NetworkType.VK = NetworkType("VK")


class ClientNetworkInfo(object):
    """
    Class ClientNetworkInfo contains client's network information, such as:

    * network type;
    * network id;
    * access token.
    """

    def __init__(self, network, nid, token):
        """
        Creates ClientNetworkInfo instance.

        :param network: Network type.
        :param nid: Network id.
        :param token: Access token.
        """
        self.__network = NetworkType(network)
        self.__nid = str(nid)
        self.__token = str(token)

    def copy(self):
        return ClientNetworkInfo(self.network, self.network_id, self.access_token)

    def get_network(self):
        """
        :return: Network type.
        :rtype: NetworkType
        """
        return self.__network

    def get_network_id(self):
        """
        :return: Network id.
        :rtype: str
        """
        return self.__nid

    def get_access_token(self):
        """
        :return: Access token.
        :rtype: str
        """
        return self.__token

    network = property(get_network)
    network_id = property(get_network_id)
    access_token = property(get_access_token)


class ClientState(object):
    """
    Class ClientState provides access to client's state.
    """

    def __init__(self, client):
        self.__client = client
        self.__data = None

    def __autoload(self):
        if not self.is_loaded : self.load()

    def load(self):
        """
        Reloads client's state.
        """
        self.merge(Net.send(Commands.GetState(self.__client.session)).response)

    def update(self):
        """
        Reloads client's state.
        """
        self.load()

    def reset(self):
        """
        Resets client's state.
        """
        self.merge(Net.send(Commands.ResetState(self.__client.session)).response)

    def merge(self, data):
        """
        Merges current client's state with another.
        """
        if self.__data:
            utils.merge_objects(self.__data, data)
        else:
            self.__data = data

    def get_data(self):
        self.__autoload()
        return self.__data

    def get_is_loaded(self):
        """
        :return: True if state is loaded, False otherwise.
        :rtype: bool
        """
        return bool(self.__data)

    def get_user_id(self):
        """
        :return: Game user id.
        :rtype: int
        """
        self.__autoload()
        return self.__data["user_data"]["user_id"]

    def get_loyality(self):
        """
        :return: Current loyality.
        :rtype: float
        """
        self.__autoload()
        return float(self.__data["difficulty"]["mixin"])

    def get_progress(self):
        """
        :return: The current client's progress.
        :rtype: int
        """
        self.__autoload()
        return int(self.__data["user_data"]["progress"])

    def get_real_balance(self):
        """
        :return: The current client's real balance.
        :rtype: int
        """
        self.__autoload()
        return int(self.__data["user_data"]["real_balance"])

    def set_real_balance(self, value):
        """
        Changes the current client's real balance.
        """
        self.add_real_balance(max(0, int(value) - self.get_real_balance()))

    def add_real_balance(self, value):
        """
        Fills the current client's real balance.
        """
        if value > 0:
            cmd = Commands.AddRealBalanceCommand(self.__client, value)
            Net.send(cmd)
            if cmd.rejected:
                raise RuntimeError("Cannot change real balance.")

    def get_game_balance(self):
        """
        :return: The current client's game balance.
        :rtype: int
        """
        self.__autoload()
        return int(self.__data["user_data"]["game_balance"])

    def set_game_balance(self, value):
        """
        Changes the current client's game balance.
        """
        self.add_game_balance(max(0, int(value) - self.get_game_balance()))

    def add_game_balance(self, value):
        """
        Fills the current client's game balance.
        """
        if value > 0:
            cmd = Commands.AddGameBalanceCommand(self.__client, value)
            Net.send(cmd)
            if cmd.rejected:
                raise RuntimeError("Cannot change game balance.")

    def get_chapters(self):
        self.__autoload()
        return self.__data["user_data"]["chapters"]

    def get_defs_hash(self):
        self.__autoload()
        return self.__data["defs_hash"]

    def get_group(self):
        self.__autoload()
        return self.__data["user_data"]["group"]

    def __getitem__(self, item):
        self.__autoload()
        return self.__data[item]

    def __contains__(self, item):
        self.__autoload()
        return item in self.__data

    is_loaded = property(get_is_loaded)

    data = property(get_data)

    user_id = property(get_user_id)
    group = property(get_group)
    progress = property(get_progress)
    chapters = property(get_chapters)
    real_balance = property(get_real_balance, set_real_balance)
    game_balance = property(get_game_balance, set_game_balance)

    defs_hash = property(get_defs_hash)


class ClientDefs(object):
    """
    Class ClientDefs provides access to client's defs.
    """

    def __init__(self, client):
        self.__client = client
        self.__data = None

    def __autoload(self):
        if not self.is_loaded : self.load()

    def merge(self, data):
        """
        Merges current client's defs with another.
        """
        if self.__data:
            utils.merge_objects(self.__data, data)
        else:
            self.__data = data

    def load(self):
        """
        Reloads client's defs.
        """
        self.merge(Net.send(Commands.GetDefs(self.__client.state.defs_hash)).response)

    def update(self):
        """
        Reloads client's defs.
        """
        self.load()

    def get_data(self):
        self.__autoload()
        return self.__data

    def get_is_loaded(self):
        """
        :return: True if defs is loaded, False otherwise.
        :rtype: bool
        """
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

    def get_boosters(self):
        self.__autoload()
        return self.__data["boosters"]

    def get_unlock_price(self, count):
        self.__autoload()
        if count > 0:
            network = self.__client.network
            if not network in self.social_networks:
                network = "default"
            return self.social_networks[network]["game_items"]["unlocks"][count]["price"]["real_balance"]
        return 0

    def __getitem__(self, item):
        self.__autoload()
        return self.__data[item]

    def __contains__(self, item):
        self.__autoload()
        return item in self.__data

    is_loaded = property(get_is_loaded)

    data = property(get_data)

    social_networks = property(get_social_networks)
    mapscreen = property(get_mapscreen)
    chapters = property(get_chapters)
    boosters = property(get_boosters)


class Client(object):
    """
    Class Client provides access to all client features.
    """

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
        self.__map = Map.Map(self)
        self.__friends = []
        self.__inbox = Inbox.Inbox(self)
        self.__boosters = Boosters.Boosters(self)
        self.__storage = Storage.Storage(self)

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
        return None

    def __has_network(self, network):
        return self.__get_network(network) is not None

    def __convert_friend(self, friend):
        self.add_friends(friend)
        return self.get_friend(friend)

    def __get_session(self, network=None, nid=None, token=None, auth=None):
        if not network:
            network = NetworkType.FB
        if not nid:
            nid = utils.random_string(0x20, "0123456789abcdef")
        if not token:
            token = Client.__generate_access_token(network, nid)

        self.__add_network(ClientNetworkInfo(network, nid, token))

        if auth is not None:
            self.__add_network(auth)

        rsp = Net.send(Commands.SessionGet(ClientNetworkInfo(network, nid, token), auth))
        self.__session = rsp["session"]

    def __update_session(self, auth=None):
        if auth is not None:
            self.__add_network(auth)
        rsp = Net.send(Commands.SessionUpdate(self.__session, auth))
        self.__session = rsp["session"]

    def __get_storage_session(self):
        rsp = Net.send(Commands.GetStorage(self.network, self.network_id, self.access_token)).response
        self.__session = rsp["session"]
        self.__storage_session = rsp["storage"]

    def get_auth_info(self, network=None):
        """
        :return: A ClientNetworkInfo instance for the specified network.
        :rtype: ClientNetworkInfo
        """
        if self.__session is None:
            self.init()

        if not network:
            if len(self.__info) > 0:
                return self.__info[0]
            return None
        return self.__get_network(network)

    def get_auth_infos(self):
        if self.__session is None:
            self.init()

        return self.__info[:]

    def get_network(self, network=None):
        info = self.get_auth_info(network)
        if info is not None:
            return info.network
        return None

    def get_network_id(self, network=None):
        """
        :return: Client's network id for the specified network.
        """
        info = self.get_auth_info(network)
        if info is not None:
            return info.network_id
        return None

    def get_access_token(self, network=None):
        """
        :return: Client's access token for the specified network.
        """
        info = self.get_auth_info(network)
        if info is not None:
            return info.access_token
        return None

    def has_friend(self, descriptor):
        """
        :return: True if client has registered friend specified by descriptor, False otherwise.
        """
        return self.get_friend(descriptor) is not None

    def get_friend(self, descriptor):
        """
        :return: Friend instance specified by descriptor if any, None otherwise.
        """
        if isinstance(descriptor, Client):
            for info in descriptor.get_auth_infos():
                friend = self.get_friend(info.network_id)
                if friend is not None : return friend
        else:
            id = None

            if isinstance(descriptor, Social.Friend):
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
        """
        :return: All registered friends.
        """
        return self.__friends[:]

    def add_friends(self, *args):
        """
        Registers friends if no instance already registered with the specified descriptors.
        """
        for arg in args:
            if isinstance(arg, list):
                self.add_friends(*arg)
            elif isinstance(arg, tuple):
                self.add_friends(*arg)
            else:
                if self.has_friend(arg):
                    continue

                if isinstance(arg, Client):
                    self.__friends.append(Social.Friend(self, arg.network_id, arg.network))
                elif isinstance(arg, Social.Friend):
                    self.__friends.append(Social.Friend(self, arg.network_id, arg.network))
                else:
                    self.__friends.append(Social.Friend(self, str(arg)))

    def send_life(self, friend):
        """
        Sends life to friend.
        :return: True in case of success, False otherwise.
        :rtype: bool
        """
        return self.__convert_friend(friend).send_life()

    def send_help(self, friend, level=None):
        """
        Sends help to friend.
        :return: True in case of success, False otherwise.
        :rtype: bool
        """
        return self.__convert_friend(friend).send_help(level)

    def request_life(self, friend):
        """
        Requests life from friend.
        :return: True in case of success, False otherwise.
        :rtype: bool
        """
        return self.__convert_friend(friend).request_life()

    def request_fuel(self, friend):
        """
        Requests fuel from friend.
        :return: True in case of success, False otherwise.
        :rtype: bool
        """
        return self.__convert_friend(friend).request_fuel()


    def init(self, network=None, nid=None, token=None, auth=None):
        """
        Inits client's session.
        """
        if self.__session is not None:
            raise RuntimeError("Client session is already inited.")
        self.__get_session(network, nid, token, auth)

    def join(self, network=None, nid=None, token=None):
        """
        Joins client's sessions.
        """
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
        """
        Resets all client's data including inbox, state and storage.
        """
        self.inbox.delete_messages()
        self.state.reset()
        self.storage.reset()

    def get_session(self):
        """
        :return: Client's session.
        :rtype: str
        """
        if not self.__session : self.__get_session()
        return self.__session

    def get_storage_session(self):
        """
        :return: Client's storage session.
        :rtype: str
        """
        if not self.__session : self.__get_session()
        if self.__storage_session is None : self.__get_storage_session()
        return self.__storage_session

    def get_next_command(self):
        self.__next_command += 1
        return self.__next_command

    def get_state(self):
        """
        :return: The current state instance.
        :rtype: ClientState
        """
        return self.__state

    def get_defs(self):
        """
        :return: The current defs instance.
        :rtype: ClientDefs
        """
        return self.__defs

    def get_map(self):
        """
        :return: The current map instance.
        :rtype: Map.Map
        """
        return self.__map

    def get_inbox(self):
        """
        :return: The current inbox instance.
        :rtype: Inbox.Inbox
        """
        return self.__inbox

    def get_storage(self):
        """
        :return: The current storage instance.
        :rtype: Storage.Storage
        """
        return self.__storage

    def set_storage(self, value):
        """
        Resets the current storage data with the specified by parameter value.
        """
        self.__storage.assign(value)

    def get_boosters(self):
        """
        :return: The current boosters instance.
        :rtype: Boosters.Boosters
        """
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

    #

    def get_user_id(self):
        return self.state.get_user_id()

    def get_progress(self):
        return self.state.get_progress()

    def get_real_balance(self):
        return self.state.get_real_balance()

    def set_real_balance(self, value):
        self.state.set_real_balance(value)

    def get_game_balance(self):
        return self.state.get_game_balance()

    def set_game_balance(self, value):
        self.state.set_game_balance(value)

    def get_group(self):
        return self.state.get_group()

    user_id = property(get_user_id)
    group = property(get_group)
    progress = property(get_progress)
    real_balance = property(get_real_balance, set_real_balance)
    game_balacne = property(get_game_balance, set_game_balance)

    #

    def get_messages(self):
        return self.inbox.get_messages()

    messages = property(get_messages)


