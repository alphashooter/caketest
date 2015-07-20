import net
import command
import utils

class Storage(utils.sdict):
    def __init__(self, client, data=None, parent=None):
        self.__client = client
        self.__parent = parent
        self.__loaded = False
        self.__locks  = 0

        if data is not None:
            self.__loaded = True
            utils.sdict.__init__(self, data)
            self.__init()
        else:
            utils.sdict.__init__(self)

    def __lock(self):
        if self.__get_parent() is not None:
            self.__get_parent().__lock()
        else:
            self.__locks += 1

    def __unlock(self):
        if self.__get_parent() is not None:
            self.__get_parent().__unlock()
        else:
            self.__locks -= 1
            if self.__locks < 0:
                raise RuntimeError("Illegal unlock.")

    def __is_locked(self):
        return self.__locks > 0 if self.__get_parent() is None else self.__get_parent().__is_locked()

    def __autoload(self):
        if not self.__loaded: self.load()

    def __parse(self):
        for key in self.keys():
            if isinstance(self[key], dict):
                self[key] = Storage(self.__client, self[key], self)

    def __init(self):
        if self.__get_parent() is None and not "boosters" in self:
            self["boosters"] = {}
        self.__parse()

    def __get_parent(self):
        storage = self.__parent
        if storage is not None:
            while storage.__parent:
                storage = storage.__parent
        return storage

    def merge(self, data):
        utils.merge_objects(self, data)
        self.__init()

    def assign(self, data):
        self.__loaded = True
        self.__lock()
        self.clear()
        self.merge(data)
        self.__unlock()
        self.upload()

    def load(self):
        rsp = net.send(command.FetchStorage(self.__client.storage_session, self.__client.session)).response
        self.__loaded = True
        self.__lock()
        self.merge(rsp["data"])
        self.__unlock()

    def upload(self):
        if self.__get_parent() is not None:
            self.__get_parent().upload()
        else:
            if not self.__is_locked():
                self.__lock()
                net.send(command.UpdateStorage(self.__client.storage_session, self.__client.session, self))
                self.__unlock()

    def __getitem__(self, item):
        self.__autoload()
        return utils.sdict.__getitem__(self, item)

    def __setitem__(self, key, value):
        self.__autoload()
        if isinstance(value, Storage):
            utils.sdict.__setitem__(self, key, value)
        else:
            self.__lock()
            if isinstance(value, dict):
                utils.sdict.__setitem__(self, key, Storage(self.__client, value, self))
            else:
                utils.sdict.__setitem__(self, key, value)
            self.__unlock()
            self.upload()

    def __delitem__(self, item):
        self.__autoload()
        utils.sdict.__delitem__(self, item)
        self.upload()

    def __contains__(self, item):
        self.__autoload()
        return utils.sdict.__contains__(self, item)

    def __iter__(self):
        self.__autoload()
        return utils.sdict.__iter__(self)