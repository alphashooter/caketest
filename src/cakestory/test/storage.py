import net
import command
import utils

class Storage(object):
    def __init__(self, client):
        self.__client = client
        self.__data = None

    def __autoload(self):
        if self.__data is None: self.load()

    def merge(self, data):
        if self.__data is None:
            self.__data = utils.sdict(data)
        else:
            utils.merge_objects(self.__data, data)

    def assign(self, data):
        self.__data = utils.sdict(data)
        self.upload()

    def load(self):
        rsp = net.send(command.FetchStorage(self.__client.storage_session, self.__client.session)).response
        self.merge(rsp["data"])

    def upload(self):
        net.send(command.UpdateStorage(self.__client.storage_session, self.__client.session, self.__data))

    def __getitem__(self, item):
        self.__autoload()
        return self.__data[item]

    def __setitem__(self, key, value):
        self.__autoload()
        self.__data[key] = value
        self.upload()

    def __delitem__(self, item):
        self.__autoload()
        del self.__data[item]
        self.upload()

    def __contains__(self, item):
        self.__autoload()
        return item in self.__data

    def __iter__(self):
        self.__autoload()
        return iter(self.__data)