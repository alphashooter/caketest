import re
import net
import command


class Limit:
    """
    An enumeration containing level limit types.

    Possible values are held in static variables:

    - Limit.MOVES -- for levels with moves limit
    - Limit.TIME -- for levels with time limit
    """

    __VALUES = ["moves", "time"]

    MOVES = None
    TIME = None

    def __init__(self, value):
        value = str(value)
        if not value in Limit.__VALUES:
            raise RuntimeError("Invalid value %s." % value)
        self.value = value

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == str(other)

    def __ne__(self, other):
        return self.value == str(other)


Limit.MOVES = Limit("moves")
Limit.TIME = Limit("time")


class Target:
    """
    An enumeration containing level target types.

    Possible values are held in static variables:

    - Target.SCORE -- for levels with score target
    - Target.GLAZE -- for levels with clear-backs target
    - Target.INGREDIENTS -- for levels with get-ingredients target
    - Target.COLORS -- for levels with get-colors target
    - Target.TOYS -- for levels with free-toys target
    - Target.MINE -- for bonus levels
    """
    __VALUES = ["score", "clearbacks", "get_ingredients", "get_colors", "glass", "toys"]

    SCORE = None
    GLAZE = None
    INGREDIENTS = None
    COLORS = None
    TOYS = None
    MINE = None

    def __init__(self, value):
        value = str(value)
        if not value in Target.__VALUES:
            raise RuntimeError("Invalid value %s." % value)
        self.value = value

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == str(other)

    def __ne__(self, other):
        return self.value == str(other)


Target.SCORE = Target("score")
Target.GLAZE = Target("clearbacks")
Target.INGREDIENTS = Target("get_ingredients")
Target.COLORS = Target("get_colors")
Target.TOYS = Target("toys")
Target.MINE = Target("glass")


class Star:
    __VALUES = [1, 2, 3]

    FIRST = None
    SECOND = None
    THIRD = None

    def __init__(self, value):
        value = int(value)
        if not value in Star.__VALUES:
            raise RuntimeError("Invalid value %d." % value)
        self.value = value

    def __int__(self):
        return self.value

    def __coerce__(self, other):
        return (int(self), other)

    def __cmp__(self, other):
        return int(self) - int(other)


Star.FIRST = Star(1)
Star.SECOND = Star(2)
Star.THIRD = Star(3)


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

    def __autoload(self):
        if not self.is_loaded : self.load()

    def parse(self, data):
        self.__data = data

    def load(self):
        self.parse(net.send(command.GetLevel(self.hash)))

    def finish(self, score=None, limit=None, lives=None, boosters=None):
        if score is None:
            score = self.get_star(Star.FIRST)
        elif isinstance(score, Star):
            score = self.get_star(score.value)
        else:
            score = int(score)

        if limit is None:
            limit = self.get_limit()
        else:
            limit = int(limit)
        if lives is None:
            lives = 0
        else:
            lives = int(lives)

        cmd = None
        if self.get_limit_type() == Limit.MOVES:
            cmd = command.FinishLevelCommand(self.__client, self.qualified_id, score, used_moves=limit, used_lives=lives, used_boosters=boosters)
        elif self.get_limit_type() == Limit.TIME:
            cmd = command.FinishLevelCommand(self.__client, self.qualified_id, score, used_time=limit, used_lives=lives, used_boosters=boosters)
        else:
            raise RuntimeError("Unknown limit type %s." % limit)

        net.send(cmd)
        return not cmd.rejected

    def force_finish(self, score=None, limit=None, lives=None, boosters=None):
        prev = self.prev

        if prev is not None and not prev.is_finished:
            if not prev.force_finish():
                return False

        if self.chapter.is_locked:
            if not self.chapter.force_unlock():
                return False

        return self.finish(score, limit, lives, boosters)

    def lose(self, completion=None, used_boosters=None):
        if completion is None:
            completion = None
        if used_boosters is None:
            used_boosters = 0

        cmd = command.LoseLevelCommand(self.__client, self.qualified_id, completion, used_boosters)
        net.send(cmd)
        return not cmd.rejected

    def force_lose(self, completion=None, used_boosters=None):
        prev = self.prev

        if prev is not None and not prev.is_finished:
            if not prev.force_finish():
                return False

        if self.chapter.is_locked:
            if not self.chapter.force_unlock():
                return False

        return self.lose(completion, used_boosters)

    def get_id(self):
        return self.__id

    def get_qualified_id(self):
        return self.__qid

    def get_hash(self):
        return self.__hash

    def get_chapter(self):
        return self.__chapter

    def get_map(self):
        return self.__chapter.map

    def get_next(self):
        if self.is_last:
            return None

        id = self.id
        while True:
            id += 1
            level = self.map.get_level(id)
            if level : return level

    def get_next_in_chapter(self):
        if self.is_last_in_chapter:
            return None

        id = self.id
        while True:
            id += 1
            level = self.map.get_level(id)
            if level : return level

    def get_prev(self):
        if self.is_first:
            return None

        id = self.id
        while True:
            id -= 1
            level = self.map.get_level(id)
            if level : return level

    def get_prev_in_chapter(self):
        if self.is_first_in_chapter:
            return None

        id = self.id
        while True:
            id -= 1
            level = self.map.get_level(id)
            if level : return level

    def get_is_inited(self):
        return True

    def get_is_loaded(self):
        return self.__data is not None

    def get_is_last(self):
        return self.id == self.map.last_level.id

    def get_is_first(self):
        return self.id == self.map.first_level.id

    def get_is_current(self):
        return self.id == self.map.current_level.id

    def get_is_last_in_chapter(self):
        return self.id == self.chapter.last_level.id

    def get_is_first_in_chapter(self):
        return self.id == self.chapter.first_level.id

    def get_is_bonus(self):
        return self.__bonus

    def get_user_finished(self):
        return self.__client.state.progress > self.id

    def get_user_score(self):
        rsp = net.send(command.QueryLevels(self.__client.session, [self.qualified_id]))
        if self.qualified_id in rsp:
            return rsp[self.qualified_id]
        else:
            return 0

    def get_user_star(self):
        score = self.get_user_score()

        star = 0
        for star in [1, 2, 3]:
            if score < self.get_star(star):
                break
        star = star - 1

        if not star:
            return None

        return Star(star)

    def get_friend_finished(self, friend):
        return friend.progress > self.id

    def get_friend_score(self, friend):
        rsp = net.send(command.QueryUsersLevels(self.__client.session, [self.qualified_id], [friend.user_id]))
        if self.qualified_id in rsp and friend.user_id in rsp[self.qualified_id]:
            return rsp[self.qualified_id][friend.user_id]
        return 0

    def get_friend_stars(self, friend):
        score = self.get_friend_score(friend)
        star = 0
        for star in [1, 2, 3]:
            if score < self.get_star(star):
                return star - 1
        return star

    def get_star(self, star):
        self.__autoload()
        return self.__data["scores"][int(star) - 1]

    def get_limit(self):
        self.__autoload()
        return self.__data["limit"][self.get_limit_type()]

    def get_limit_type(self):
        self.__autoload()
        for key in self.__data["limit"] : return Limit(key)

    def get_level_type(self):
        self.__autoload()
        if len(self.__data["objectives"]) > 0:
            for key in self.__data["objectives"] : return Target(key)
        return Target("score")


    id = property(get_id)
    qualified_id = property(get_qualified_id)
    hash = property(get_hash)
    is_loaded = property(get_is_loaded)
    is_inited = property(get_is_inited)

    chapter = property(get_chapter)
    map = property(get_map)

    next = property(get_next)
    prev = property(get_prev)
    is_first = property(get_is_first)
    is_last = property(get_is_last)
    is_current = property(get_is_current)

    next_in_chapter = property(get_next_in_chapter)
    prev_in_chapter = property(get_prev_in_chapter)
    is_first_in_chapter = property(get_is_first_in_chapter)
    is_last_in_chapter = property(get_is_last_in_chapter)

    limit_type = property(get_limit_type)
    level_type = property(get_level_type)

    limit = property(get_limit)
    star1 = property(lambda self: self.get_star(1))
    star2 = property(lambda self: self.get_star(2))
    star3 = property(lambda self: self.get_star(3))

    is_bonus = property(get_is_bonus)
    is_finished = property(get_user_finished)

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

    def __getattr__(self, item):
        match = re.match(r"level_(\d+)", item)
        if match:
            return self.get_level(int(match.group(1)))

        match = re.match(r"bonus_(\d+)", item)
        if match:
            return self.get_bonus_level(int(match.group(1)))

        raise AttributeError()

    def parse(self, data):
        self.__levels = list(Level(self.__client, self, data["levels"][i]["id"], data["levels"][i]["hash"]) for i in range(len(data["levels"])))
        self.__bonus = list()
        if "bonus_level" in data:
            self.__bonus.append(Level(self.__client, self, data["bonus_level"]["id"], data["bonus_level"]["hash"], True))

    def load(self, separately=False):
        if separately:
            for i in range(len(self.__levels)):
                self.__levels[i].load()
        else:
            rsp = net.send(command.GetChapter(self.hash))
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
        return sorted(self.__levels[:], key=Level.get_id)

    def get_bonus_level(self, id=None):
        if not id :
            id = self.id
        for i in range(len(self.__bonus)):
            if str(self.__bonus[i].id) == str(id) or self.__bonus[i].qualified_id == str(id):
                return self.__bonus[i]
        return None

    def get_bonus_levels(self):
        return sorted(self.__bonus[:], key=Level.get_id)

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


class Map:
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
