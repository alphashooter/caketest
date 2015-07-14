import net
import command


class Level:
    def __init__(self, id, hash, data=None):
        self.id = id
        self.hash = hash
        self.data = None
        if data:
            self.parse(data)

    def parse(self, data):
        self.data = data

    def load(self):
        self.parse(net.Connection.instance.send_get(command.CommandGetLevel(self.hash)))

    def star(self, num):
        return self.data["scores"][num - 1]


class Chapter:
    def __init__(self, data=None):
        self.id = None
        self.hash = None
        self.levels = None
        self.bonus = None
        self.locks = 0
        self.unlocks = 0

        if data:
            self.parse(data)

    def get_level_by_hash(self, hash):
        for i in range(len(self.levels)):
            if str(self.levels[i].hash) == str(hash):
                return self.levels[i]
        return None

    def get_level_by_id(self, id):
        for i in range(len(self.levels)):
            if str(self.levels[i].id) == str(id):
                return self.levels[i]
        return None

    def get_is_locked(self):
        return self.unlocks < self.locks

    def get_is_unlocked(self):
        return not self.get_is_locked()

    def parse(self, data):
        self.id = data["id"]
        self.hash = data["hash"]
        self.locks = data["unlocks_count"]
        self.levels = list(Level(data["levels"][i]["id"], data["levels"][i]["hash"]) for i in range(len(data["levels"])))
        if "bonus_level" in data:
            self.levels.append(Level(data["bonus_level"]["id"], data["bonus_level"]["hash"]))

    def load(self, separately=False):
        if separately:
            for i in range(len(self.levels)):
                self.levels[i].load()
        else:
            rsp = net.Connection.instance.send_get(command.CommandGetChapter(self.hash))
            for key in list(rsp.keys()):
                self.get_level_by_hash(key).parse(rsp[key])

