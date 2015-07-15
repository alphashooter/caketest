import httplib
import hashlib
import json

class RequestMethod:
    POST = "POST"
    GET = "GET"


class Connection:
    SECRET_TOKEN = "gghdfuuw9oll;[-&66wtgg00091835gfbns76dferRREjqls,,cll;0,cnnsggsiwuwiiwhhfbdsfkhkhkjhkjiuoiueqeroiujfkb"

    instance = None

    @staticmethod
    def get_request_string(data):
        if isinstance(data, dict):
            return "|".join("[%s=%s]" % (key, Connection.get_request_string(data[key])) for key in sorted(list(data.keys())))
        elif isinstance(data, list):
            return "|".join("[%d=%s]" % (key, Connection.get_request_string(data[key])) for key in range(len(data)))
        else:
            return str(data)

    @staticmethod
    def get_message_token(data, token):
        sha = hashlib.sha1()
        sha.update(Connection.get_request_string(data) + token)
        return sha.hexdigest()

    def __init__(self, host):
        self.connection = httplib.HTTPSConnection(host)

    def send_post(self, command):
        data = command.data
        if not data:
            data = {}
        data["token"] = Connection.get_message_token(data, Connection.SECRET_TOKEN)

        print "Server request\n" \
              "Command: %s\n" \
              "Data:    %s\n" % (command.name, json.dumps(data))

        self.connection.request("POST", command.name, json.dumps(data), {"Content-Type": "application/json"})

        response = self.connection.getresponse()
        if response.status != 200:
            raise RuntimeError("Invalid server response status %d: %s" % (response.status, response.reason))
        data = response.read()

        print "Server response\n" \
              "Data:    %s\n" % data
        return json.loads(data)

    def send_get(self, command):
        data = command.data

        if data:
            query = "&".join("%s=%s" % (key, str(data[key])) for key in data)
            print "Server request\n" \
                  "Command: %s\n" \
                  "Data:    %s\n" % (command.name, query)
            self.connection.request("GET", "%s?%s" % (command.name, query))
        else:
            print "Server request:\n" \
                  "Command: %s\n" \
                  "Data:    None\n" % command.name
            self.connection.request("GET", command.name)

        response = self.connection.getresponse()
        if response.status != 200:
            raise RuntimeError("Invalid server response status %d: %s" % (response.status, response.reason))
        data = response.read()

        print "Server response\n" \
              "Data:    %s\n" % data
        return json.loads(data)

    def send(self, command):
        if command.method == RequestMethod.POST:
            return self.send_post(command)
        elif command.method == RequestMethod.GET:
            return self.send_get(command)
        else:
            raise RuntimeError("Unknown request method '%s'." % command.method)


__connection = None


def connection(host):
    global __connection
    __connection = Connection(host)


def send(command):
    global __connection
    if not __connection:
        raise RuntimeError("Connection must be inited.")
    return __connection.send(command)