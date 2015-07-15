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
            rsp = net.send(command.QueryUsers(self.__client.session, self.__network, [self.__nid]))
            if self.__network in rsp and self.__nid in rsp[self.__network]:
                self.__uid = int(rsp[self.__network][self.__nid])
        return self.__uid

    def get_exist(self):
        return self.get_user_id() is not None

    def get_progress(self):
        if not self.get_exist():
            raise RuntimeError("Friend does not exist.")
        rsp = net.send(command.QueryUsersProgress(self.__client.session, [self.__uid]))
        return rsp[str(self.__uid)]

    network = property(get_network)
    network_id = property(get_network_id)
    user_id = property(get_user_id)
    exist = property(get_exist)
    progress = property(get_progress)
