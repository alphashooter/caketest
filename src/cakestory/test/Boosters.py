import net
import command

class BoosterType:
    NAMES = [
        "pastry_tongs",
        "gingerbread_man",
        "confectionery_blade",
        "rainbow_cake",
        "pastry_bag",
        "reverse_move",
        "change_cakes_places",
        "extra_time",
        "striped_cake_on_plate",
        "cafetiere",
        "boss_protection",
        "extra_moves"
    ]

    PASTRY_TONGS = None
    GIFT_MOVES = None
    SPATULA = None
    RAINBOW_CUPCAKE = None
    PASTRY_BAG = None
    REVERSE = None
    SWAP = None
    EXTRA_TIME = None
    STRIPED_AND_PLATED = None
    COFFEE_POT = None
    BOSS_PROTECTION = None
    EXTRA_MOVES = None

    def __init__(self, value):
        value = str(value)
        if not value in BoosterType.NAMES:
            raise RuntimeError("Invalid type %s." % value)
        self.value = value

    def __str__(self):
        return self.value


BoosterType.PASTRY_TONGS = BoosterType("pastry_tongs")
BoosterType.GIFT_MOVES = BoosterType("gingerbread_man")
BoosterType.SPATULA = BoosterType("confectionery_blade")
BoosterType.RAINBOW_CUPCAKE = BoosterType("rainbow_cake")
BoosterType.PASTRY_BAG = BoosterType("pastry_bag")
BoosterType.REVERSE = BoosterType("reverse_move")
BoosterType.SWAP = BoosterType("change_cakes_places")
BoosterType.EXTRA_TIME = BoosterType("extra_time")
BoosterType.STRIPED_AND_PLATED = BoosterType("striped_cake_on_plate")
BoosterType.COFFEE_POT = BoosterType("cafetiere")
BoosterType.BOSS_PROTECTION = BoosterType("boss_protection")
BoosterType.EXTRA_MOVES = BoosterType("extra_moves")


class Booster(object):
    def __init__(self, client, type):
        self.__client = client
        self.__type = type

    def __convert_count(self, count):
        if self.pack_count == 0:
            raise RuntimeError("Pack is not for sell.")
        packs = 0
        while self.pack_count * packs < count:
            packs += 1
        return packs

    def buy(self, count=1):
        packs_count = self.__convert_count(count)
        for i in range(packs_count):
            if not net.send(command.BuyBoosterCommand(self.__client, self.__type)).rejected:
                self.set_count(self.get_count() + self.pack_count)
            else:
                return False
        return True

    def force_buy(self, count=1):
        packs_count = self.__convert_count(count)
        if self.__client.state.real_balance < packs_count * self.pack_price:
            self.__client.state.real_balance = packs_count * self.pack_price
        return self.buy(count)

    def spend(self, count=1):
        if self.count < count:
            return False

        self.count = self.count - count
        return True

    def force_spend(self, count=1):
        if self.count < count:
            self.force_buy(count - self.count)
        return self.spend(count)

    def get_pack_price(self):
        network = self.__client.network
        if not network in self.__client.defs.social_networks:
            network = "default"
        if str(self.__type) in self.__client.defs.social_networks[network]["game_items"]["booster_packs"]:
            return self.__client.defs.social_networks[network]["game_items"]["booster_packs"][self.__type]["price"]["real_balance"]
        return 0

    def get_pack_count(self):
        network = self.__client.network
        if not network in self.__client.defs.social_networks:
            network = "default"
        if str(self.__type) in self.__client.defs.social_networks[network]["game_items"]["booster_packs"]:
            return sum(self.__client.defs.social_networks[network]["game_items"]["booster_packs"][self.__type]["contents"].values())
        return 0

    def get_type(self):
        return BoosterType(self.__type)

    def get_count(self):
        return self.__client.storage["boosters"][self.__type] if self.__type in self.__client.storage["boosters"] else 0

    def set_count(self, value):
        self.__client.storage["boosters"][self.__type] = int(value)

    type = property(get_type)
    count = property(get_count, set_count)
    pack_price = property(get_pack_price)
    pack_count = property(get_pack_count)


class Boosters(object):
    def __init__(self, client):
        self.__client = client

    def __getitem__(self, item):
        return Booster(self.__client, BoosterType(item))

    def __contains__(self, item):
        return str(item) in BoosterType.NAMES

    def __iter__(self):
        boosters = list(Booster(self.__client, BoosterType(name)) for name in BoosterType.NAMES)
        return iter(boosters)