import plamee.log as log
import plamee.cakestory.test as test

__DEFAULT_CONF_FILE = "./test.conf"

config = None
host = "m3highload-master.test.nsk.plamee.com"
port = None
http = False

def load_config(file):
    from os.path import exists, isfile
    import json

    global config

    #

    default = False
    if file is None:
        file = __DEFAULT_CONF_FILE
        default = True

    if not exists(file) or not isfile(file):
        if default:
            log.warn("Config file '%s' is not found." % file)
        else:
            log.error("Config file '%s' is not found." % file)
    else:
        config = json.loads(open(file, "r").read())


def init():
    import sys

    global config
    global host
    global port
    global http

    config_file = None

    argc = len(sys.argv)
    for i in range(1, argc):
        arg = sys.argv[i]
        if arg == "--config":
            if i + 1 < argc:
                i += 1
                config_file = sys.argv[i]
            else:
                log.error("Config file is not specified.")
        elif arg == "--host":
            if i + 1 < argc:
                i += 1
                host = sys.argv[i]
            else:
                log.error("Host is not specified.")
        elif arg == "--port":
            if i + 1 < argc:
                i += 1
                port = int(sys.argv[i])
            else:
                log.error("Port must be specified.")
        elif arg == "--log":
            if i + 1 < argc:
                i += 1
                log.file = sys.argv[i]
            else:
                log.error("File must be specified.")
        elif arg == "--verbose":
            log.level = 0
        elif arg == "--use-http":
            http = True


    load_config(config_file)

#

def run():
    from os.path import dirname
    import sys

    global config
    global host
    global port
    global http

    init()

    sys.path.extend([dirname(__file__)])
    test.run(host = host, port = port, http = http, config = config)

#

run()