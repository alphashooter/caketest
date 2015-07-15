import re
import net
import command


class Level:
    def __init__(self, client, chapter, id, hash, bonus=False, data=None):
        self.__client = client
        self.__chapter = chapter

        self.__id = None
        self.__qid = None
        self.__bonus = bool(bonus)

        if self.__bonus:
            self.__id = int(re.match(r"bonus_(\d+)", str(id)).group(1))
            self.__qid = str(id)
        else:
            self.__id = int(id)
            self.__qid = str(id)

        self.__hash = str(hash)
        self.__data = None

        if data:
            self.parse(data)

    def parse(self, data):
        self.__data = data

    def load(self):
        self.parse(net.send(command.GetLevel(self.__hash)))

    def get_id(self):
        return self.__id

    def get_qualified_id(self):
        return self.__qid

    def get_hash(self):
        return self.__hash

    def get_chapter(self):
        return self.__chapter

    def get_map(self):
        return self.__chapter.get_map()

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
        return self.__data is not None

    def get_is_bonus(self):
        return self.__bonus

    def get_user_score(self):
        rsp = net.send(command.QueryLevels(self.__client.session, [self.get_qualified_id()]))
        if self.__id in rsp:
            return rsp[self.__id]
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
        return self.__data["scores"][num - 1]

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
        self.__client = client
        self.__map = map

        self.__id = int(id)
        self.__qid = str(id)
        self.__hash = str(hash)
        self.__levels = None
        self.__bonus = None

        if data:
            self.parse(data)

    def parse(self, data):
        self.__levels = list(Level(self.__client, self, data["levels"][i]["id"], data["levels"][i]["hash"]) for i in range(len(data["levels"])))
        self.__bonus = []
        if "bonus_level" in data:
            self.__bonus.append(Level(self.__client, self, data["bonus_level"]["id"], data["bonus_level"]["hash"], True))

    def load(self, separately=False):
        if separately:
            for i in range(len(self.__levels)):
                self.__levels[i].load()
        else:
            rsp = net.send(command.GetChapter(self.__hash))
            for key in list(rsp.keys()):
                self.get_level_by_hash(key).parse(rsp[key])

    def get_id(self):
        return self.__id

    def get_qualified_id(self):
        return self.__qid

    def get_hash(self):
        return self.__hash

    def get_map(self):
        return self.__map

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
        return self.__levels is not None and self.__bonus is not None

    def get_is_loaded(self):
        if not self.get_is_inited():
            return False
        for i in range(len(self.__levels)):
            if not self.__levels[i].get_is_loaded():
                return False
        return True

    def get_level_by_hash(self, hash):
        for i in range(len(self.__levels)):
            if self.__levels[i].get_hash() == str(hash):
                return self.__levels[i]
        for i in range(len(self.__bonus)):
            if self.__bonus[i].get_hash() == str(hash):
                return self.__levels[i]
        return None

    def get_level(self, id):
        for i in range(len(self.__levels)):
            if str(self.__levels[i].get_id()) == str(id) or self.__levels[i].get_qualified_id() == str(id):
                return self.__levels[i]
        return None

    def get_level_first(self):
        ids = sorted(list(self.__levels[i].get_id() for i in range(len(self.__levels))))
        return self.get_level(ids[0])

    def get_level_last(self):
        ids = sorted(list(self.__levels[i].get_id() for i in range(len(self.__levels))))
        return self.get_level(ids[len(ids) - 1])

    def get_levels(self):
        return self.__levels[:]

    def get_bonus_level(self, id=None):
        if not id :
            id = self.get_id()
        for i in range(len(self.__bonus)):
            if str(self.__bonus[i].get_id()) == str(id) or self.__bonus[i].get_qualified_id() == str(id):
                return self.__bonus[i]
        return None

    def get_unlocks(self):
        if "unlocks" in self.__client.state.chapters[self.__id]:
            return list(self.__client.state.chapters[self.__id]["unlocks"])
        return list()

    def get_locks_count(self):
        return int(self.__client.defs.chapters[self.__id]["unlocks_count"])

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
        self.__client = client
        self.__chapters = None
        if data:
            self.parse(data)

    def parse(self, data):
        self.__chapters = list(Chapter(self.__client, self, data[i]["id"], data[i]["hash"], data[i]) for i in range(len(data)))

    def load(self, separately=False):
        for i in range(len(self.__chapters)):
            self.__chapters[i].load(separately)

    def get_is_inited(self):
        return bool(self.__chapters)

    def get_is_loaded(self):
        if not self.get_is_inited():
            return False
        for i in range(len(self.__chapters)):
            if not self.__chapters[i].get_is_loaded():
                return False
        return True

    def get_chapter_by_hash(self, hash):
        for i in range(len(self.__chapters)):
            if self.__chapters[i].get_hash() == str(hash):
                return self.__chapters[i]
        return None

    def get_chapter(self, id):
        for i in range(len(self.__chapters)):
            if str(self.__chapters[i].get_id()) == str(id) or str(self.__chapters[i].get_qualified_id()) == str(id):
                return self.__chapters[i]
        return None

    def get_chapter_first(self):
        ids = sorted(list(self.__chapters[i].get_id() for i in range(len(self.__chapters))))
        return self.get_chapter(ids[0])

    def get_chapter_last(self):
        ids = sorted(list(self.__chapters[i].get_id() for i in range(len(self.__chapters))))
        return self.get_chapter(ids[len(ids) - 1])

    def get_chapters(self):
        return self.__chapters[:]

    def get_level_by_hash(self, hash):
        for i in range(len(self.__chapters)):
            level = self.__chapters[i].get_level_by_hash(hash)
            if level: return level
        return None

    def get_level(self, id):
        for i in range(len(self.__chapters)):
            level = self.__chapters[i].get_level(id)
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
        for i in range(len(self.__chapters)):
            level = self.__chapters[i].get_bonus_level(id)
            if level: return level
        return None

    is_loaded = property(get_is_loaded)
    is_inited = property(get_is_inited)

    first_chapter = property(get_chapter_first)
    last_chapter = property(get_chapter_last)
    first_level = property(get_level_first)
    last_level = property(get_level_last)
