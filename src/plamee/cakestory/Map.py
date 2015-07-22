import re

import Net
import Commands
import Level


class Chapter(object):
    """
    Class Chapter provides access to chapter information, contents and methods.
    """

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
        """
        Parses chapter from JS-like object.
        """
        self.__levels = list(
            Level.Level(self.__client, self, data["levels"][i]["id"], data["levels"][i]["hash"]) for i in range(len(data["levels"])))
        self.__bonus = list()
        if "bonus_level" in data:
            self.__bonus.append(Level.Level(self.__client, self, data["bonus_level"]["id"], data["bonus_level"]["hash"], True))

    def load(self, separately=False):
        """
        Loads chapter's levels.
        """
        if separately:
            for i in range(len(self.__levels)):
                self.__levels[i].load()
        else:
            rsp = Net.send(Commands.GetChapter(self.hash)).response
            for key in list(rsp.keys()):
                self.get_level_by_hash(key).parse(rsp[key])

    def finish(self):
        """
        Attempts to finish all levels in chapter.

            :return: True in case of success, False otherwise.
            :rtype: bool
        """
        if self.is_locked:
            return False

        levels = self.levels
        for level in levels:
            if not level.is_finished:
                if not level.finish():
                    return False
            else:
                break

        return True

    def force_finish(self):
        """
        Forces attempt to finish all levels in chapter.

            :return: True in case of success, False otherwise.
            :rtype: bool
        """
        if self.is_locked:
            if not self.force_unlock():
                return False

        return self.finish()

    def buy_unlocks(self):
        """
        Attempts to buy unlocks for chapter.

            :return: True in case of success, False otherwise.
            :rtype: bool
        """
        cmd = Commands.BuyChapterUnlocksCommand(self.__client)
        Net.send(cmd)
        return not cmd.rejected

    def force_buy_unlocks(self):
        """
        Forces attempt to buy unlocks for chapter.

        If client has no enough real balance, fills it up.

            :return: True in case of success, False otherwise.
            :rtype: bool
        """
        if self.__client.state.real_balance < self.unlock_price:
            self.__client.state.real_balance = self.unlock_price
        return self.buy_unlocks()

    def unlock(self):
        """
        Attempts to unlock chapter.

            :return: True in case of success, False otherwise.
            :rtype: bool
        """
        cmd = Commands.UnlockChapterCommand(self.__client)
        Net.send(cmd)
        return not cmd.rejected

    def force_unlock(self):
        """
        Forces attempt to unlock chapter.

        If previous chapter is locked, forces its unlock.

        If chapter has no enough unlocks, forces its purchase.

            :return: True in case of success, False otherwise.
            :rtype: bool
        """
        if self.is_unlocked:
            return True

        prev = self.prev
        if prev is not None:
            if not prev.is_unlocked:
                if not prev.force_unlock():
                    return False
            if not prev.finish():
                return False

        if self.unlocks < self.locks:
            self.force_buy_unlocks()

        return self.unlock()

    def get_id(self):
        """
        :return: Chapter id.
        :rtype: int
        """
        return self.__id

    def get_qualified_id(self):
        """
        :return: Chapter qualified id.
        :rtype: str
        """
        return self.__qid

    def get_hash(self):
        """
        :return: Chatper hash.
        :rtype: str
        """
        return self.__hash

    def get_map(self):
        """
        :return: The corresponding map object.
        :rtype: Map
        """
        return self.__map

    def get_next(self):
        """
        :return: The next chapter if exists, None otherwise.
        :rtype: Chapter
        """
        if self.is_last:
            return None

        id = self.id
        while True:
            id += 1
            chapter = self.map.get_chapter(id)
            if chapter : return chapter

    def get_prev(self):
        """
        :return: The previous chapter if exists, None otherwise.
        :rtype: Chapter
        """
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
        """
        :return: True if chapter is first on the map, False otherwise.
        :rtype: bool
        """
        return self.id == self.map.first_chapter.id

    def get_is_last(self):
        """
        :return: True if chapter is last on the map, False otherwise.
        :rtype: bool
        """
        return self.id == self.map.last_chapter.id

    def get_is_current(self):
        """
        :return: True if chapter is current on the map, False otherwise.
        :rtype: bool
        """
        return self.id == self.map.current_chapter.id

    def get_level_by_hash(self, hash):
        """
        :return: Level specified by hash if exists, None otherwise.
        :rtype: Level.Level
        """
        for i in range(len(self.__levels)):
            if self.__levels[i].hash == str(hash):
                return self.__levels[i]
        for i in range(len(self.__bonus)):
            if self.__bonus[i].hash == str(hash):
                return self.__levels[i]
        return None

    def get_level(self, id):
        """
        :return: Level specified by id if exists, None otherwise.
        :rtype: Level.Level
        """
        for i in range(len(self.__levels)):
            if str(self.__levels[i].id) == str(id) or self.__levels[i].qualified_id == str(id):
                return self.__levels[i]
        return None

    def get_level_first(self):
        """
        :return: The first level in chapter.
        :rtype: Level.Level
        """
        ids = sorted(list(self.__levels[i].id for i in range(len(self.__levels))))
        return self.get_level(ids[0])

    def get_level_last(self):
        """
        :return: The last level in chapter.
        :rtype: Level.Level
        """
        ids = sorted(list(self.__levels[i].id for i in range(len(self.__levels))))
        return self.get_level(ids[len(ids) - 1])

    def get_levels(self):
        """
        :return: List of all levels in chapter.
        :rtype: list
        """
        return sorted(self.__levels[:], key=Level.Level.get_id)

    def get_bonus_level(self, id=None):
        """
        :return: Bonus level specified by id if exists, None otherwise.
        :rtype: Level.Level
        """
        if not id :
            id = self.id
        for i in range(len(self.__bonus)):
            if str(self.__bonus[i].id) == str(id) or self.__bonus[i].qualified_id == str(id):
                return self.__bonus[i]
        return None

    def get_bonus_levels(self):
        """
        :return: List of all bonus levels in chapter.
        :rtype: list
        """
        return sorted(self.__bonus[:], key=Level.Level.get_id)

    def get_unlocks(self):
        """
        :return: Chatper unlocks.
        :rtype: list
        """
        if self.qualified_id in self.__client.state.chapters and "unlocks" in self.__client.state.chapters[self.qualified_id]:
            return list(self.__client.state.chapters[self.qualified_id]["unlocks"])
        return list()

    def get_locks_count(self):
        """
        :return: Number of chapter locks.
        :rtype: int
        """
        return int(self.__client.defs.chapters[self.qualified_id]["unlocks_count"])

    def get_unlocks_count(self):
        """
        :return: Number of chapter unlocks.
        :rtype: int
        """
        return len(self.get_unlocks())

    def get_unlock_price(self):
        """
        :return: Price of chapter unlock.
        :rtype: int
        """
        if self.is_unlocked:
            return 0
        return self.__client.defs.get_unlock_price(self.locks - self.unlocks)

    def get_is_locked(self):
        """
        :return: True if chapter is locked, False otherwise.
        :rtype: bool
        """
        return not self.get_is_unlocked()

    def get_is_unlocked(self):
        """
        :return: True if chapter is unlocked, False otherwise.
        :rtype: bool
        """
        if self.qualified_id in self.__client.state.chapters and "unlocked" in self.__client.state.chapters[self.qualified_id]:
            return bool(self.__client.state.chapters[self.qualified_id]["unlocked"])
        return False

    def get_is_finished(self):
        """
        :return: True if chapter is finished, False otherwise.
        :rtype: bool
        """
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
    unlock_price = property(get_unlock_price)
    is_locked = property(get_is_locked)
    is_unlocked = property(get_is_unlocked)
    is_finished = property(get_is_finished)


class Map(object):
    """
    Class Map provides access to map information, contents and methods.
    """

    def __init__(self, client, data=None):
        self.__client = client
        self.__chapters = None
        if data:
            self.parse(data)

    def __autoinit(self):
        if not self.is_inited : self.parse(self.__client.defs.mapscreen)

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
        """
        Parses map from JS-like object.
        """
        self.__chapters = list(Chapter(self.__client, self, data[i]["id"], data[i]["hash"], data[i]) for i in range(len(data)))

    def load(self, separately=False):
        """
        Loads all chapters on map.
        """
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
        """
        :return: Chapter specified by hash if exists, None otherwise.
        :rtype: Chapter
        """
        self.__autoinit()
        for i in range(len(self.__chapters)):
            if self.__chapters[i].hash == str(hash):
                return self.__chapters[i]
        return None

    def get_chapter(self, id):
        """
        :return: Chapter specified by id if exists, None otherwise.
        :rtype: Chapter
        """
        self.__autoinit()
        for i in range(len(self.__chapters)):
            if str(self.__chapters[i].id) == str(id) or str(self.__chapters[i].qualified_id) == str(id):
                return self.__chapters[i]
        return None

    def get_chapter_first(self):
        """
        :return: The first chapter on map.
        :rtype: Chapter
        """
        self.__autoinit()
        ids = sorted(list(self.__chapters[i].id for i in range(len(self.__chapters))))
        return self.get_chapter(ids[0])

    def get_chapter_last(self):
        """
        :return: The last chapter on map.
        :rtype: Chapter
        """
        self.__autoinit()
        ids = sorted(list(self.__chapters[i].id for i in range(len(self.__chapters))))
        return self.get_chapter(ids[len(ids) - 1])

    def get_chapter_current(self):
        """
        :return: The current chapter on map.
        :rtype: Chapter
        """
        self.__autoinit()
        current_level = self.current_level
        current_chapter = current_level.chapter if current_level is not None else None

        if current_chapter is not None:
            prev = current_chapter.prev
            if prev is None or prev.is_unlocked:
                return current_chapter
            else:
                return prev
        else:
            return None

    def get_chapters(self):
        """
        :return: All chapters on map.
        :rtype: list
        """
        self.__autoinit()
        return sorted(self.__chapters[:], key=Chapter.get_id)

    def get_level_by_hash(self, hash):
        """
        :return: Level specified by hash if exists, None otherwise.
        :rtype: Level.Level
        """
        self.__autoinit()
        for i in range(len(self.__chapters)):
            level = self.__chapters[i].get_level_by_hash(hash)
            if level: return level
        return None

    def get_level(self, id):
        """
        :return: Level specified by id if exists, None otherwise.
        :rtype: Level.Level
        """
        self.__autoinit()
        for i in range(len(self.__chapters)):
            level = self.__chapters[i].get_level(id)
            if level: return level
        return None

    def get_level_first(self):
        """
        :return: The first level on map.
        :rtype: Level.Level
        """
        self.__autoinit()
        return self.first_chapter.first_level

    def get_level_last(self):
        """
        :return: The last level on map.
        :rtype: Level.Level
        """
        self.__autoinit()
        return self.last_chapter.last_level

    def get_level_current(self):
        """
        :return: The current level on map.
        :rtype: Level.Level
        """
        self.__autoinit()
        return self.get_level(self.__client.state.progress)

    def get_levels(self):
        """
        :return: All levels on map.
        :rtype: list
        """
        self.__autoinit()
        chapters = self.get_chapters()
        levels = list()
        for i in range(len(chapters)):
            levels += chapters[i].get_levels()
        return levels

    def get_bonus_level(self, id):
        """
        :return: Bonus level specified by id if exists, None otherwise.
        :rtype: Level.Level
        """
        self.__autoinit()
        for i in range(len(self.__chapters)):
            level = self.__chapters[i].get_bonus_level(id)
            if level: return level
        return None

    def get_bonus_levels(self):
        """
        :return: All bonus levels on map.
        :rtype: list
        """
        self.__autoinit()
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
