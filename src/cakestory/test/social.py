import net
import command

class Friend:
    def __init__(self, client, network, nid):
        self.__client = client
        self.__network = network
        self.__nid = str(nid)
        self.__uid = None

    def get_network(self):
        return self.__network

    def get_network_id(self):
        return self.__nid

    def get_user_id(self):
        if self.__uid is None:
            rsp = net.send(command.QueryUsers(self.__client.session, self.network, [self.network_id]))
            if self.network in rsp and self.network_id in rsp[self.network]:
                self.__uid = int(rsp[self.network][self.network_id])
        return self.__uid

    def get_exist(self):
        return self.user_id is not None

    def get_progress(self):
        if not self.exist:
            raise RuntimeError("Friend does not exist.")
        rsp = net.send(command.QueryUsersProgress(self.__client.session, [self.user_id]))
        return rsp[str(self.user_id)]

    network = property(get_network)
    network_id = property(get_network_id)
    user_id = property(get_user_id)
    exist = property(get_exist)
    progress = property(get_progress)
