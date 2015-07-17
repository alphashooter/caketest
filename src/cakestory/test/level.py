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
    """
    An enumeration containing values corresponding to score stars in level.

    Possible values are held in static variables:

    - Star.FIRST -- for first star
    - Star.SECOND -- for second star
    - Star.THIRD -- for third star
    """

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
        return (self.value, other)

    def __cmp__(self, other):
        return self.value - int(other)


Star.FIRST = Star(1)
Star.SECOND = Star(2)
Star.THIRD = Star(3)


class Level(object):
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

    def __int__(self):
        return self.__id

    def __str__(self):
        return self.__qid

    def __autoload(self):
        if not self.is_loaded : self.load()

    def parse(self, data):
        self.__data = data

    def load(self):
        self.parse(net.send(command.GetLevel(self.hash)).response)

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
        if self.chapter.is_locked:
            if not self.chapter.force_unlock():
                return False

        levels = self.chapter.levels
        for level in levels:
            if level.id != self.id:
                if not level.is_finished:
                    if not level.finish():
                        return False
            else:
                break

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
        if self.chapter.is_locked:
            if not self.chapter.force_unlock():
                return False

        levels = self.chapter.levels
        for level in levels:
            if level.id != self.id:
                if not level.is_finished:
                    if not level.finish():
                        return False
            else:
                break

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