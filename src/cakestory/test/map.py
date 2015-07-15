import re
import net
import command


class Level:
    def __init__(self, client, chapter, id, hash, data=None):
        self.client = client
        self.chapter = chapter

        self.id = str(id)
        self.hash = str(hash)
        self.data = None

        if data:
            self.parse(data)

    def parse(self, data):
        self.data = data

    def load(self):
        self.parse(net.Connection.instance.send_get(command.CommandGetLevel(self.hash)))

    def get_is_loaded(self):
        return bool(self.data)

    def get_is_bonus(self):
        return bool(re.search(r"bonus_\d+", self.id))

    def get_user_score(self):
        rsp = net.Connection.instance.send_post(command.CommandQueryLevels(self.client.session, [self.id]))
        if self.id in rsp:
            return rsp[self.id]
        else:
            return 0

    def get_user_stars(self):
        score = self.get_user_score()
        for star in [1, 2, 3]:
            if score < self.get_star(star):
                return star - 1
        return star

    def get_star(self, num):
        if not self.get_is_loaded() : self.load()
        return self.data["scores"][num - 1]

    is_loaded = property(get_is_loaded)
    is_bonus = property(get_is_bonus)

class Chapter:
    def __init__(self, client, data=None):
        self.client = client

        self.id = None
        self.hash = None
        self.levels = None

        if data:
            self.parse(data)

    def parse(self, data):
        self.id = str(data["id"])
        self.hash = str(data["hash"])
        self.levels = list(Level(self.client, self, data["levels"][i]["id"], data["levels"][i]["hash"]) for i in range(len(data["levels"])))
        if "bonus_level" in data:
            self.levels.append(Level(self.client, self, data["bonus_level"]["id"], data["bonus_level"]["hash"]))

    def load(self, separately=False):
        if separately:
            for i in range(len(self.levels)):
                self.levels[i].load()
        else:
            rsp = net.Connection.instance.send_get(command.CommandGetChapter(self.hash))
            for key in list(rsp.keys()):
                self.get_level_by_hash(key).parse(rsp[key])

    def get_is_loaded(self):
        if not self.levels:
            return False
        for i in range(len(self.levels)):
            if not self.levels[i].get_is_loaded():
                return False
        return True

    def get_level_by_hash(self, hash):
        for i in range(len(self.levels)):
            if self.levels[i].hash == str(hash):
                return self.levels[i]
        return None

    def get_level(self, id):
        for i in range(len(self.levels)):
            if self.levels[i].id == str(id):
                return self.levels[i]
        return None

    def get_unlocks(self):
        if "unlocks" in self.client.state.chapters[self.id]:
            return list(self.client.state.chapters[self.id]["unlocks"])
        return list()

    def get_locks_count(self):
        return int(self.client.defs.chapters[self.id]["unlocks_count"])

    def get_unlocks_count(self):
        return len(self.get_unlocks())

    def get_is_locked(self):
        return self.get_unlocks_count() < self.get_locks_count()

    def get_is_unlocked(self):
        return not self.get_is_locked()

    is_loaded = property(get_is_loaded)

    locks = property(get_locks_count)
    unlocks = property(get_unlocks_count)
    is_locked = property(get_is_locked)
    is_unlocked = property(get_is_unlocked)


class Map:
    def __init__(self, client, data=None):
        self.client = client
        self.chapters = None
        if data:
            self.parse(data)

    def parse(self, data):
        self.chapters = list(Chapter(self.client, data[i]) for i in range(len(data)))

    def load(self, separately=False):
        for i in range(len(self.chapters)):
            self.chapters[i].load(separately)

    def get_is_loaded(self):
        if not self.chapters:
            return False
        for i in range(len(self.chapters)):
            if not self.chapters[i].get_is_loaded():
                return False
        return True

    def get_chapter_by_hash(self, hash):
        for i in range(len(self.chapters)):
            if self.chapters[i].hash == str(hash):
                return self.chapters[i]
        return None

    def get_chapter(self, id):
        for i in range(len(self.chapters)):
            if self.chapters[i].id == str(id):
                return self.chapters[i]
        return None

    def get_level_by_hash(self, hash):
        for i in range(len(self.chapters)):
            level = self.chapters[i].get_level_by_hash(hash)
            if level: return level
        return None

    def get_level(self, id):
        for i in range(len(self.chapters)):
            level = self.chapters[i].get_level(id)
            if level: return level
        return None

    is_loaded = property(get_is_loaded)

