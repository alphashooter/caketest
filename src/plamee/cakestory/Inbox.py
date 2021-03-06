import Net
import Commands


class MessageType:
    """
    Enumeration class which contains common message types.
    """

    __VALUES = ["life", "fuel", "booster", "request_life", "request_fuel"]

    REQUEST_LIFE = None
    REQUEST_FUEL = None
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

    def __eq__(self, other):
        return self.value == str(other)

    def __ne__(self, other):
        return self.value != str(other)


MessageType.LIFE = MessageType("life")
MessageType.FUEL = MessageType("fuel")
MessageType.HELP = MessageType("booster")
MessageType.REQUEST_LIFE = MessageType("request_life")
MessageType.REQUEST_FUEL = MessageType("request_fuel")


class Message(object):
    """
    Class message provides access to inbox messages.
    """

    def __init__(self, client, data):
        self.__client = client
        self.__id = int(data["id"])
        self.__from = int(data["from_user_id"])
        self.__type = MessageType(data["type"])
        self.__data = data["params"]
        self.__date = int(data["created_at"])

    def read(self):
        """
        Marks message as read.
        """
        return not Net.send(Commands.ReadMessageCommand(self.__client, self.__id)).rejected

    def delete(self):
        """
        Deletes message from inbox.
        """
        return not Net.send(Commands.DeleteMessagesCommand(self.__client, [self.__id])).rejected

    def get_id(self):
        """
        :return: Message id.
        :rtype: int
        """
        return self.__id

    def get_type(self):
        """
        :return: Message type.
        :rtype: MessageType
        """
        return self.__type

    def get_data(self):
        """
        :return: Message optional data.
        :type: dict
        """
        return self.__data

    def get_date(self):
        """
        :return: Message send time.
        :rtype: int
        """
        return self.__date

    def get_friend_id(self):
        """
        :return: Message sender's game user id.
        :rtype: int
        """
        return self.__from

    id = property(get_id)
    type = property(get_type)
    data = property(get_data)
    date = property(get_date)
    friend_id = property(get_friend_id)


class Inbox(object):
    """
    Class Inbox provides access to client's inbox.
    """

    def __init__(self, client):
        self.__client = client

    def get_is_empty(self):
        """
        :return: True if inbox has no messages, False otherwise.
        :rtype: bool
        """
        return len(self.messages) == 0

    def get_messages(self):
        """
        :return: All messages from inbox.
        :rtype: list
        """
        response = Net.send(Commands.GetMessages(self.__client.session)).response
        messages = []
        for message in response["messages"]:
            messages.append(Message(self.__client, message))
        return messages

    def read_messages(self):
        """
        Marks all messages from inbox as read.
        """
        result = True
        messages = self.messages
        for message in messages:
            result = result and message.read()
        return result

    def delete_messages(self):
        """
        Deletes all messages from inbox.
        """
        result = True
        messages = self.messages
        for message in messages:
            result = result and message.delete()
        return result

    messages = property(get_messages)
    is_empty = property(get_is_empty)
