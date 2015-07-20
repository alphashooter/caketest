import Net
import Commands


class MessageType:
    __VALUES = ["life", "fuel", "booster", "request_life", "request_fuel"]

    LIFE_REQUEST = None
    FUEL_REQUEST = None
    LIFE = None
    FUEL = None
    HELP = None

    def __init__(self, value):
        value = str(value)
        if not value in MessageType.__VALUES:
            raise RuntimeError("Invalid value %s." % value)
        self.value = value

    def __str__(self):
        return self.value


MessageType.LIFE = MessageType("life")
MessageType.FUEL = MessageType("fuel")
MessageType.HELP = MessageType("booster")
MessageType.LIFE_REQUEST = MessageType("request_life")
MessageType.FUEL_REQUEST = MessageType("request_fuel")


class Message(object):
    def __init__(self, client, data):
        self.__client = client
        self.__id = int(data["id"])
        self.__from = int(data["from_user_id"])
        self.__type = MessageType(data["type"])
        self.__data = data["params"]
        self.__date = int(data["created_at"])

    def read(self):
        return not Net.send(Commands.ReadMessageCommand(self.__client, self.__id)).rejected

    def delete(self):
        return not Net.send(Commands.DeleteMessagesCommand(self.__client, [self.__id])).rejected

    def get_id(self):
        return self.__id

    def get_type(self):
        return self.__type

    def get_data(self):
        return self.__data

    def get_date(self):
        return self.__date

    def get_friend_id(self):
        return self.__from

    id = property(get_id)
    type = property(get_type)
    data = property(get_data)
    date = property(get_date)
    friend_id = property(get_friend_id)


class Inbox(object):
    def __init__(self, client):
        self.__client = client

    def get_is_empty(self):
        return len(self.messages) == 0

    def get_messages(self):
        response = Net.send(Commands.GetMessages(self.__client.session)).response
        messages = []
        for message in response["messages"]:
            messages.append(Message(self.__client, message))
        return messages

    def read_all(self):
        result = True
        messages = self.messages
        for message in messages:
            result = result and message.read()
        return result

    def delete_all(self):
        result = True
        messages = self.messages
        for message in messages:
            result = result and message.delete()
        return result

    messages = property(get_messages)
    is_empty = property(get_is_empty)
