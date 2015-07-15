import re
import net
import command


class Level:
    def __init__(self, client, chapter, id, hash, bonus=False, data=None):
        self._client = client
        self._chapter = chapter

        self._id = None
        self._qid = None
        self._bonus = bool(bonus)

        if self._bonus:
            self._id = int(re.match(r"bonus_(\d+)", str(id)).group(1))
            self._qid = str(id)
        else:
            self._id = int(id)
            self._qid = str(id)

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

    def get_qualified_id(self):
        return self._qid

    def get_hash(self):
        return self._hash

    def get_chapter(self):
        return self._chapter

    def get_map(self):
        return self._chapter.get_map()

    def get_next(self):
        if self.get_is_last():
            return None

        id = self.get_id()
        while True:
            id += 1
            level = self.get_map().get_level(id)
            if level : return level

    def get_next_in_chapter(self):
        if self.get_is_last_in_chapter():
            return None

        id = self.get_id()
        while True:
            id += 1
            level = self.get_map().get_level(id)
            if level : return level

    def get_prev(self):
        if self.get_is_first():
            return None

        id = self.get_id()
        while True:
            id -= 1
            level = self.get_map().get_level(id)
            if level : return level

    def get_prev_in_chapter(self):
        if self.get_is_first_in_chapter():
            return None

        id = self.get_id()
        while True:
            id -= 1
            level = self.get_map().get_level(id)
            if level : return level

    def get_is_last(self):
        return self.get_id() == self.get_map().get_level_last().get_id()

    def get_is_first(self):
        return self.get_id() == self.get_map().get_level_first().get_id()

    def get_is_last_in_chapter(self):
        return self.get_id() == self.get_chapter().get_level_last().get_id()

    def get_is_first_in_chapter(self):
        return self.get_id() == self.get_chapter().get_level_first().get_id()

    def get_is_inited(self):
        return True

    def get_is_loaded(self):
        return self._data is not None

    def get_is_bonus(self):
        return self._bonus

    def get_user_score(self):
        rsp = net.send(command.QueryLevels(self._client.session, [self.get_qualified_id()]))
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
    qualified_id = property(get_qualified_id)
    hash = property(get_hash)
    is_loaded = property(get_is_loaded)
    is_inited = property(get_is_inited)

    chapter = property(get_chapter)
    map = property(get_map)

    next = property(get_next)
    prev = property(get_prev)
    next_in_chapter = property(get_next_in_chapter)
    prev_in_chapter = property(get_prev_in_chapter)

    is_first = property(get_is_first)
    is_last = property(get_is_last)
    is_first_in_chapter = property(get_is_first_in_chapter)
    is_last_in_chapter = property(get_is_last_in_chapter)

    is_bonus = property(get_is_bonus)

class Chapter:
    def __init__(self, client, map, id, hash, data=None):
        self._client = client
        self._map = map

        self._id = int(id)
        self._qid = str(id)
        self._hash = str(hash)
        self._levels = None
        self._bonus = None

        if data:
            self.parse(data)

    def parse(self, data):
        self._levels = list(Level(self._client, self, data["levels"][i]["id"], data["levels"][i]["hash"]) for i in range(len(data["levels"])))
        self._bonus = []
        if "bonus_level" in data:
            self._bonus.append(Level(self._client, self, data["bonus_level"]["id"], data["bonus_level"]["hash"], True))

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

    def get_qualified_id(self):
        return self._qid

    def get_hash(self):
        return self._hash

    def get_map(self):
        return self._map

    def get_next(self):
        if self.get_is_last():
            return None

        id = self.get_id()
        while True:
            id += 1
            chapter = self.get_map().get_chapter(id)
            if chapter : return chapter

    def get_prev(self):
        if self.get_is_first():
            return None

        id = self.get_id()
        while True:
            id -= 1
            chapter = self.get_map().get_chapter(id)
            if chapter : return chapter

    def get_is_first(self):
        return self.get_id() == self.get_map().get_chapter_first().get_id()

    def get_is_last(self):
        return self.get_id() == self.get_map().get_chapter_last().get_id()

    def get_is_inited(self):
        return self._levels is not None and self._bonus is not None

    def get_is_loaded(self):
        if not self.get_is_inited():
            return False
        for i in range(len(self._levels)):
            if not self._levels[i].get_is_loaded():
                return False
        return True

    def get_level_by_hash(self, hash):
        for i in range(len(self._levels)):
            if self._levels[i].get_hash() == str(hash):
                return self._levels[i]
        for i in range(len(self._bonus)):
            if self._bonus[i].get_hash() == str(hash):
                return self._levels[i]
        return None

    def get_level(self, id):
        for i in range(len(self._levels)):
            if str(self._levels[i].get_id()) == str(id) or self._levels[i].get_qualified_id() == str(id):
                return self._levels[i]
        return None

    def get_level_first(self):
        ids = sorted(list(self._levels[i].get_id() for i in range(len(self._levels))))
        return self.get_level(ids[0])

    def get_level_last(self):
        ids = sorted(list(self._levels[i].get_id() for i in range(len(self._levels))))
        return self.get_level(ids[len(ids) - 1])

    def get_levels(self):
        return self._levels[:]

    def get_bonus_level(self, id=None):
        if not id :
            id = self.get_id()
        for i in range(len(self._bonus)):
            if str(self._bonus[i].get_id()) == str(id) or self._bonus[i].get_qualified_id() == str(id):
                return self._bonus[i]
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
    qualified_id = property(get_qualified_id)
    hash = property(get_hash)
    is_loaded = property(get_is_loaded)
    is_inited = property(get_is_inited)

    map = property(get_map)

    next = property(get_next)
    prev = property(get_prev)
    is_first = property(get_is_first)
    is_last = property(get_is_last)

    first_level = property(get_level_first)
    last_level = property(get_level_last)

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
        self._chapters = list(Chapter(self._client, self, data[i]["id"], data[i]["hash"], data[i]) for i in range(len(data)))

    def load(self, separately=False):
        for i in range(len(self._chapters)):
            self._chapters[i].load(separately)

    def get_is_inited(self):
        return bool(self._chapters)

    def get_is_loaded(self):
        if not self.get_is_inited():
            return False
        for i in range(len(self._chapters)):
            if not self._chapters[i].get_is_loaded():
                return False
        return True

    def get_chapter_by_hash(self, hash):
        for i in range(len(self._chapters)):
            if self._chapters[i].get_hash() == str(hash):
                return self._chapters[i]
        return None

    def get_chapter(self, id):
        for i in range(len(self._chapters)):
            if str(self._chapters[i].get_id()) == str(id) or str(self._chapters[i].get_qualified_id()) == str(id):
                return self._chapters[i]
        return None

    def get_chapter_first(self):
        ids = sorted(list(self._chapters[i].get_id() for i in range(len(self._chapters))))
        return self.get_chapter(ids[0])

    def get_chapter_last(self):
        ids = sorted(list(self._chapters[i].get_id() for i in range(len(self._chapters))))
        return self.get_chapter(ids[len(ids) - 1])

    def get_chapters(self):
        return self._chapters[:]

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

    def get_level_first(self):
        return self.get_chapter_first().get_level_first()

    def get_level_last(self):
        return self.get_chapter_last().get_level_last()

    def get_levels(self):
        chapters = self.get_chapters()
        levels = list()
        for i in range(len(chapters)):
            levels += chapters[i].get_levels()
        return levels

    def get_bonus_level(self, id):
        for i in range(len(self._chapters)):
            level = self._chapters[i].get_bonus_level(id)
            if level: return level
        return None

    is_loaded = property(get_is_loaded)
    is_inited = property(get_is_inited)

    first_chapter = property(get_chapter_first)
    last_chapter = property(get_chapter_last)
    first_level = property(get_level_first)
    last_level = property(get_level_last)
