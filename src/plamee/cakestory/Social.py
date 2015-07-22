import Net
import Commands


class Friend(object):
    """
    Provides access to friends information and methods.
    """

    def __init__(self, client, network, nid):
        self.__client = client
        self.__network = str(network)
        self.__nid = str(nid)
        self.__uid = None

    def __assert_exist(self):
        if not self.exist:
            raise RuntimeError("Friend does not exist.")

    def get_network(self):
        """
        :return: Friend's network.
        :rtype: str
        """
        return self.__network

    def get_network_id(self):
        """
        :return: Friend's network id.
        :rtype: str
        """
        return self.__nid

    def get_user_id(self):
        """
        :return: Friend's game user id.
        :rtype: int
        """
        if self.__uid is None:
            rsp = Net.send(Commands.QueryUsers(self.__client.session, self.network, [self.network_id]))
            if self.network in rsp and self.network_id in rsp[self.network]:
                self.__uid = int(rsp[self.network][self.network_id])
        return self.__uid

    def send_life(self):
        """
        Attempts to send life to friend.

            :return: True in case of success, False otherwise.
            :rtype: bool
        """
        self.__assert_exist()
        return not Net.send(Commands.SendLifeCommand(self.__client, self.user_id)).rejected

    def send_help(self, level=None):
        """
        Attempts to send help to friend.

            :return: True in case of success, False otherwise.
            :rtype: bool
        """
        self.__assert_exist()
        if level is None:
            level = self.progress
        return not Net.send(Commands.SendHelpCommand(self.__client, self.user_id, level)).rejected

    def request_life(self):
        """
        Attempts to request life from friend.

            :return: True in case of success, False otherwise.
            :rtype: bool
        """
        self.__assert_exist()
        return not Net.send(Commands.RequestLifeCommand(self.__client, self.user_id)).rejected

    def request_fuel(self):
        """
        Attempts to request fuel from friend.

            :return: True in case of success, False otherwise.
            :rtype: bool
        """
        self.__assert_exist()
        return not Net.send(Commands.RequestFuelCommand(self.__client, self.user_id)).rejected

    def get_exist(self):
        """
        :return: True if friend is registered on game server, False otherwise.
        :rtype: bool
        """
        return self.user_id is not None

    def get_progress(self):
        """
        :return: Friend's progress.
        :rtype: int
        """
        self.__assert_exist()
        rsp = Net.send(Commands.QueryUsersProgress(self.__client.session, [self.user_id])).response
        return int(rsp[self.user_id])

    def get_last_activity(self):
        """
        :return: Friend's last activity time.
        :rtype: int
        """
        self.__assert_exist()
        rsp = Net.send(Commands.QueryUsersTime(self.__client.session, [self.user_id]))
        if self.user_id in rsp and "last_activity" in rsp[self.user_id]:
            return int(rsp[self.user_id]["last_activity"])
        return None

    def get_last_level_activity(self):
        """
        :return: Friend's last level activity time.
        :rtype: int
        """
        self.__assert_exist()
        rsp = Net.send(Commands.QueryUsersTime(self.__client.session, [self.user_id]))
        if self.user_id in rsp and "finish_level_time" in rsp[self.user_id]:
            return int(rsp[self.user_id]["finish_level_time"])
        return None

    network = property(get_network)
    network_id = property(get_network_id)
    user_id = property(get_user_id)
    exist = property(get_exist)
    progress = property(get_progress)
    last_activity = property(get_last_activity)
    last_level_activity = property(get_last_level_activity)
