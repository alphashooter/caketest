__messages = []

LEVEL_DEBUG = 0
LEVEL_INFO = 1
LEVEL_OK = 2
LEVEL_WARNING = 3
LEVEL_ERROR = 4
LEVEL_MESSAGE = 5

level = 1
file = None

class Message:
    def __init__(self, level, message):
        self.level = level
        self.message = message

def __convert_message(level, message):
    import time
    return "%s\n%s\n%s\n\n" % (time.strftime("%a, %d %b %Y %H:%M:%S.{:0>3d} +0000", time.gmtime()).format(divmod(int(time.time() * 1000 + 0.5), 1000)[1]), level, "\n".join(map(lambda line: ">> %s" % line, message.splitlines())))

def __format_message(message):
    if message.level <= LEVEL_DEBUG:
        return "\033[90m%s\033[0m\n" % message.message
    elif message.level <= LEVEL_INFO:
        return "\033[1m\033[30m%s\033[0m\n" % message.message
    elif message.level <= LEVEL_OK:
        return "\033[1m\033[32m%s\033[0m\n" % message.message
    elif message.level <= LEVEL_WARNING:
        return "\033[1m\033[33m%s\033[0m\n" % message.message
    elif message.level <= LEVEL_ERROR:
        return "\033[1m\033[31m%s\033[0m\n" % message.message
    else:
        return "\033[30m%s\033[0m\n" % message.message

def __format_time_message(message):
    if message.level <= LEVEL_DEBUG:
        return __convert_message("DEBUG", message.message)
    elif message.level <= LEVEL_INFO:
        return __convert_message("INFO", message.message)
    elif message.level <= LEVEL_OK:
        return __convert_message("INFO", message.message)
    elif message.level <= LEVEL_WARNING:
        return __convert_message("WARNING", message.message)
    elif message.level <= LEVEL_ERROR:
        return __convert_message("ERROR", message.message)
    else:
        return __convert_message("MESSAGE", message.message)

def log(level, message):
    m = Message(level, message)

    global file
    global __messages

    __messages.append(m)
    if level >= globals()["level"]:
        print __format_message(m)

    if file is not None:
        open(file, "a").write(__format_time_message(m))


def debug(message):
    log(LEVEL_DEBUG, message)

def info(message):
    log(LEVEL_INFO, message)

def ok(message):
    log(LEVEL_OK, message)

def warn(message):
    log(LEVEL_WARNING, message)

def error(message, exc=True):
    log(LEVEL_ERROR, message)
    if exc:
        raise RuntimeError(message)

def message(message):
    log(LEVEL_MESSAGE, message)