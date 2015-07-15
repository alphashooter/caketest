import re
import net
import command


class Level:
    def __init__(self, client, chapter, id, hash, data=None):
        self._client = client
        self._chapter = chapter

        self._id = str(id)
        self._hash = str(hash)
        self._data = None

        if data:
            self.parse(data)

    def parse(self, data):
        self._data = data

    def load(self):
        self.parse(net.send(command.GetLevel(self._hash)))

    def get_id(self):
        return self._id

    def get_hash(self):
        return self._hash

    def get_chapter(self):
        return self._chapter

    def get_map(self):
        return self._chapter.get_map()

    def get_is_loaded(self):
        return bool(self._data)

    def get_is_bonus(self):
        return bool(re.search(r"bonus_\d+", self._id))

    def get_user_score(self):
        rsp = net.Connection.instance.send_post(command.QueryLevels(self._client.session, [self._id]))
        if self._id in rsp:
            return rsp[self._id]
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
        return self._data["scores"][num - 1]

    id = property(get_id)
    hash = property(get_hash)
    is_loaded = property(get_is_loaded)

    chapter = property(get_chapter)
    map = property(get_map)
    is_bonus = property(get_is_bonus)

class Chapter:
    def __init__(self, client, map, data=None):
        self._client = client
        self._map = map

        self._id = None
        self._hash = None
        self._levels = None

        if data:
            self.parse(data)

    def parse(self, data):
        self._id = str(data["id"])
        self._hash = str(data["hash"])
        self._levels = list(Level(self._client, self, data["levels"][i]["id"], data["levels"][i]["hash"]) for i in range(len(data["levels"])))
        if "bonus_level" in data:
            self._levels.append(Level(self._client, self, data["bonus_level"]["id"], data["bonus_level"]["hash"]))

    def load(self, separately=False):
        if separately:
            for i in range(len(self._levels)):
                self._levels[i].load()
        else:
            rsp = net.send(command.GetChapter(self._hash))
            for key in list(rsp.keys()):
                self.get_level_by_hash(key).parse(rsp[key])

    def get_id(self):
        return self._id

    def get_hash(self):
        return self._hash

    def get_map(self):
        return self._map

    def get_is_loaded(self):
        if not self._levels:
            return False
        for i in range(len(self._levels)):
            if not self._levels[i].get_is_loaded():
                return False
        return True

    def get_level_by_hash(self, hash):
        for i in range(len(self._levels)):
            if self._levels[i].hash == str(hash):
                return self._levels[i]
        return None

    def get_level(self, id):
        for i in range(len(self._levels)):
            if self._levels[i].id == str(id):
                return self._levels[i]
        return None

    def get_unlocks(self):
        if "unlocks" in self._client.state.chapters[self._id]:
            return list(self._client.state.chapters[self._id]["unlocks"])
        return list()

    def get_locks_count(self):
        return int(self._client.defs.chapters[self._id]["unlocks_count"])

    def get_unlocks_count(self):
        return len(self.get_unlocks())

    def get_is_locked(self):
        return self.get_unlocks_count() < self.get_locks_count()

    def get_is_unlocked(self):
        return not self.get_is_locked()

    id = property(get_id)
    hash = property(get_hash)
    is_loaded = property(get_is_loaded)

    map = property(get_map)
    locks = property(get_locks_count)
    unlocks = property(get_unlocks_count)
    is_locked = property(get_is_locked)
    is_unlocked = property(get_is_unlocked)


class Map:
    def __init__(self, client, data=None):
        self._client = client
        self._chapters = None
        if data:
            self.parse(data)

    def parse(self, data):
        self._chapters = list(Chapter(self._client, self, data[i]) for i in range(len(data)))

    def load(self, separately=False):
        for i in range(len(self._chapters)):
            self._chapters[i].load(separately)

    def get_is_loaded(self):
        if not self._chapters:
            return False
        for i in range(len(self._chapters)):
            if not self._chapters[i].get_is_loaded():
                return False
        return True

    def get_chapter_by_hash(self, hash):
        for i in range(len(self._chapters)):
            if self._chapters[i].hash == str(hash):
                return self._chapters[i]
        return None

    def get_chapter(self, id):
        for i in range(len(self._chapters)):
            if self._chapters[i].id == str(id):
                return self._chapters[i]
        return None

    def get_level_by_hash(self, hash):
        for i in range(len(self._chapters)):
            level = self._chapters[i].get_level_by_hash(hash)
            if level: return level
        return None

    def get_level(self, id):
        for i in range(len(self._chapters)):
            level = self._chapters[i].get_level(id)
            if level: return level
        return None

    is_loaded = property(get_is_loaded)

