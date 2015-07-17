import re
import net
import command
import level


class Chapter(object):
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

    def __getattr__(self, item):
        match = re.match(r"level_(\d+)", item)
        if match:
            return self.get_level(int(match.group(1)))

        match = re.match(r"bonus_(\d+)", item)
        if match:
            return self.get_bonus_level(int(match.group(1)))

        raise AttributeError()

    def parse(self, data):
        self.__levels = list(level.Level(self.__client, self, data["levels"][i]["id"], data["levels"][i]["hash"]) for i in range(len(data["levels"])))
        self.__bonus = list()
        if "bonus_level" in data:
            self.__bonus.append(level.Level(self.__client, self, data["bonus_level"]["id"], data["bonus_level"]["hash"], True))

    def load(self, separately=False):
        if separately:
            for i in range(len(self.__levels)):
                self.__levels[i].load()
        else:
            rsp = net.send(command.GetChapter(self.hash)).response
            for key in list(rsp.keys()):
                self.get_level_by_hash(key).parse(rsp[key])

    def finish(self):
        if self.is_finished:
            return True
        return self.last_level.force_finish()

    def unlock(self):
        if not self.is_current:
            return False
        if self.is_unlocked:
            return True

        cmd = command.UnlockChapterCommand(self.__client)
        net.send(cmd)

        return not cmd.rejected

    def force_unlock(self):
        if self.is_unlocked:
            return True
        if not self.finish():
            return False

        cmd = command.BuyChapterUnlocksCommand(self.__client)
        net.send(cmd)

        return not cmd.rejected

    def get_id(self):
        return self.__id

    def get_qualified_id(self):
        return self.__qid

    def get_hash(self):
        return self.__hash

    def get_map(self):
        return self.__map

    def get_next(self):
        if self.is_last:
            return None

        id = self.id
        while True:
            id += 1
            chapter = self.map.get_chapter(id)
            if chapter : return chapter

    def get_prev(self):
        if self.is_first:
            return None

        id = self.id
        while True:
            id -= 1
            chapter = self.map.get_chapter(id)
            if chapter : return chapter

    def get_is_inited(self):
        return self.__levels is not None and self.__bonus is not None

    def get_is_loaded(self):
        if not self.is_inited:
            return False
        for i in range(len(self.__levels)):
            if not self.__levels[i].is_loaded:
                return False
        return True

    def get_is_first(self):
        return self.id == self.map.first_chapter.id

    def get_is_last(self):
        return self.id == self.map.last_chapter.id

    def get_is_current(self):
        return self.id == self.map.current_chapter.id

    def get_level_by_hash(self, hash):
        for i in range(len(self.__levels)):
            if self.__levels[i].hash == str(hash):
                return self.__levels[i]
        for i in range(len(self.__bonus)):
            if self.__bonus[i].hash == str(hash):
                return self.__levels[i]
        return None

    def get_level(self, id):
        for i in range(len(self.__levels)):
            if str(self.__levels[i].id) == str(id) or self.__levels[i].qualified_id == str(id):
                return self.__levels[i]
        return None

    def get_level_first(self):
        ids = sorted(list(self.__levels[i].id for i in range(len(self.__levels))))
        return self.get_level(ids[0])

    def get_level_last(self):
        ids = sorted(list(self.__levels[i].id for i in range(len(self.__levels))))
        return self.get_level(ids[len(ids) - 1])

    def get_levels(self):
        return sorted(self.__levels[:], key=level.Level.get_id)

    def get_bonus_level(self, id=None):
        if not id :
            id = self.id
        for i in range(len(self.__bonus)):
            if str(self.__bonus[i].id) == str(id) or self.__bonus[i].qualified_id == str(id):
                return self.__bonus[i]
        return None

    def get_bonus_levels(self):
        return sorted(self.__bonus[:], key=level.Level.get_id)

    def get_unlocks(self):
        if self.qualified_id in self.__client.state and "unlocks" in self.__client.state.chapters[self.qualified_id]:
            return list(self.__client.state.chapters[self.qualified_id]["unlocks"])
        return list()

    def get_locks_count(self):
        return int(self.__client.defs.chapters[self.qualified_id]["unlocks_count"])

    def get_unlocks_count(self):
        return len(self.get_unlocks())

    def get_is_locked(self):
        if self.qualified_id in self.__client.state and "unlocked" in self.__client.state.chapters[self.qualified_id]:
            return not self.__client.state.chapters[self.qualified_id]["unlocked"]
        return True

    def get_is_unlocked(self):
        return not self.get_is_locked()

    def get_is_finished(self):
        return self.__client.state.progress > self.last_level.id

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
    is_current = property(get_is_current)

    levels = property(get_levels)
    bonus_levels = property(get_bonus_levels)
    first_level = property(get_level_first)
    last_level = property(get_level_last)

    locks = property(get_locks_count)
    unlocks = property(get_unlocks_count)
    is_locked = property(get_is_locked)
    is_unlocked = property(get_is_unlocked)
    is_finished = property(get_is_finished)


class Map(object):
    def __init__(self, client, data=None):
        self.__client = client
        self.__chapters = None
        if data:
            self.parse(data)

    def __getattr__(self, item):
        match = re.match(r"level_(\d+)", item)
        if match:
            return self.get_level(int(match.group(1)))

        match = re.match(r"bonus_(\d+)", item)
        if match:
            return self.get_bonus_level(int(match.group(1)))

        match = re.match(r"chapter_(\d+)", item)
        if match:
            return self.get_chapter(int(match.group(1)))

        raise AttributeError()


    def parse(self, data):
        self.__chapters = list(Chapter(self.__client, self, data[i]["id"], data[i]["hash"], data[i]) for i in range(len(data)))

    def load(self, separately=False):
        for i in range(len(self.__chapters)):
            self.__chapters[i].load(separately)

    def get_is_inited(self):
        return bool(self.__chapters)

    def get_is_loaded(self):
        if not self.is_inited:
            return False
        for i in range(len(self.__chapters)):
            if not self.__chapters[i].is_loaded:
                return False
        return True

    def get_chapter_by_hash(self, hash):
        for i in range(len(self.__chapters)):
            if self.__chapters[i].hash == str(hash):
                return self.__chapters[i]
        return None

    def get_chapter(self, id):
        for i in range(len(self.__chapters)):
            if str(self.__chapters[i].id) == str(id) or str(self.__chapters[i].qualified_id) == str(id):
                return self.__chapters[i]
        return None

    def get_chapter_first(self):
        ids = sorted(list(self.__chapters[i].id for i in range(len(self.__chapters))))
        return self.get_chapter(ids[0])

    def get_chapter_last(self):
        ids = sorted(list(self.__chapters[i].id for i in range(len(self.__chapters))))
        return self.get_chapter(ids[len(ids) - 1])

    def get_chapter_current(self):
        current = self.current_level.chapter
        prev = current.prev
        if prev is None or prev.is_unlocked:
            return current
        else:
            return prev

    def get_chapters(self):
        return sorted(self.__chapters[:], key=Chapter.get_id)

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
        return self.first_chapter.first_level

    def get_level_last(self):
        return self.last_chapter.last_level

    def get_level_current(self):
        return self.get_level(self.__client.state.progress)

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

    def get_bonus_levels(self):
        chapters = self.get_chapters()
        levels = list()
        for i in range(len(chapters)):
            levels += chapters[i].get_bonus_levels()
        return levels

    is_loaded = property(get_is_loaded)
    is_inited = property(get_is_inited)

    chapters = property(get_chapters)
    first_chapter = property(get_chapter_first)
    last_chapter = property(get_chapter_last)
    current_chapter = property(get_chapter_current)

    levels = property(get_levels)
    first_level = property(get_level_first)
    last_level = property(get_level_last)
    current_level = property(get_level_current)

    bonus_levels = property(get_bonus_levels)
