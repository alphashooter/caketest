import httplib
import hashlib
import json

import plamee.utils as utils
import plamee.log as log


class RequestMethod:
    POST = "POST"
    GET = "GET"


class Connection:
    SECRET_TOKEN = "gghdfuuw9oll;[-&66wtgg00091835gfbns76dferRREjqls,,cll;0,cnnsggsiwuwiiwhhfbdsfkhkhkjhkjiuoiueqeroiujfkb"

    @staticmethod
    def get_request_string(data):
        if isinstance(data, dict):
            return "|".join("[%s=%s]" % (key, Connection.get_request_string(data[key])) for key in sorted(list(data.keys())))
        elif isinstance(data, list):
            return "|".join("[%d=%s]" % (key, Connection.get_request_string(data[key])) for key in range(len(data)))
        elif isinstance(data, bool):
            return "true" if data else "false"
        else:
            return str(data)

    @staticmethod
    def get_message_token(data, token):
        sha = hashlib.sha1()
        sha.update(Connection.get_request_string(data) + token)
        return sha.hexdigest()

    def __init__(self, host, port=None, http=False):
        self.__connection = None
        if http:
            self.__connection = httplib.HTTPConnection(host=host, port=port)
        else:
            self.__connection = httplib.HTTPSConnection(host=host, port=port)

    def send_post(self, command):
        data = command.data
        if not data:
            data = {}
        data["token"] = Connection.get_message_token(data, Connection.SECRET_TOKEN)

        log.debug("Server request\n" \
              "Command: %s\n" \
              "Data:    %s\n" % (command.name, json.dumps(data)))

        self.__connection.request("POST", command.name, json.dumps(data), {"Content-Type": "application/json"})

        response = self.__connection.getresponse()
        if response.status != 200:
            raise RuntimeError("Invalid server response status %d: %s" % (response.status, response.reason))
        data = response.read()

        log.debug("Server response\n" \
              "Data:    %s\n" % data)

        command.process(utils.sdict(json.loads(data.decode("utf-8"))))
        return command

    def send_get(self, command):
        data = command.data

        if data:
            query = "&".join("%s=%s" % (key, str(data[key])) for key in data)
            log.debug("Server request\n" \
                  "Command: %s\n" \
                  "Data:    %s\n" % (command.name, query))
            self.__connection.request("GET", "%s?%s" % (command.name, query))
        else:
            log.debug("Server request:\n" \
                  "Command: %s\n" \
                  "Data:    None\n" % command.name)
            self.__connection.request("GET", command.name)

        response = self.__connection.getresponse()
        if response.status != 200:
            log.error("Invalid server response status %d: %s" % (response.status, response.reason))
        data = response.read()

        log.debug("Server response\n" \
              "Data:    %s\n" % data)

        command.process(utils.sdict(json.loads(data.decode("utf-8"))))
        return command

    def send(self, command):
        if command.method == RequestMethod.POST:
            return self.send_post(command)
        elif command.method == RequestMethod.GET:
            return self.send_get(command)
        else:
            log.error("Unknown request method '%s'." % command.method)

    def get_host(self):
        return self.__connection.host

    host = property(get_host)


__connection = None


def connect(host, port=None, http=False):
    global __connection
    __connection = Connection(host=host, port=port, http=http)


def send(command):
    global __connection
    if not __connection:
        raise RuntimeError("Connection must be inited.")
    return __connection.send(command)

def get_host():
    global __connection
    return __connection.host