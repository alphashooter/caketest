import plamee.log as log
import plamee.cakestory.test as test
import re

__DEFAULT_CONF_FILE = "global.conf"

config = None
host = "m3highload-stable.test.nsk.plamee.com"
port = None
http = False

def __load_config(file):
    from os.path import exists, isfile, dirname, join, abspath, normpath

    global config

    #

    default = False
    if file is None:
        file = __DEFAULT_CONF_FILE
        default = True

    if not exists(file) or not isfile(file):
        file = join(join(dirname(__file__), "../"), file)

    file = normpath(abspath(file))

    if not exists(file) or not isfile(file):
        if default:
            log.warn("Config file '%s' is not found." % file)
            file = "/tmp/m3highload-test.conf.tmp"
            __generate_config(file)
        else:
            log.error("Config file '%s' is not found." % file)

    config = file
    log.debug("Configuration file '%s' loaded.\n\n%s" % (config, open(config, "r").read()))


def __generate_config(file):
    from os.path import dirname, join
    config = __create_config(join(dirname(__file__), "plamee/cakestory/test"))
    open(file, "w").write(config)


def __create_group(root, indent=0):
    from os import listdir
    from os.path import isfile, isdir, join

    result = ""
    contents = listdir(root)

    #

    files = filter(lambda file: isfile(join(root, file)), contents)
    files = filter(lambda file: re.match(r"^.+\.py$", file) is not None, files)
    files = map(lambda file: re.match(r"^(.+)\.py$", file).group(1), files)
    files = filter(lambda file: re.match(r"^__.+__$", file) is None, files)

    if len(files):
        for file in files:
            result += "\n"
            result += __create_module(file, indent)

    #

    dirs = filter(lambda name: isdir(join(root, name)), contents)

    if len(dirs):
        result += "\n\n"
        for dir in dirs:
            if isfile(join(join(root, dir), "__init__.py")):
                if indent > 0:
                    format = "{: >%ds}group {:s}:" % int(4 * indent)
                else:
                    format = "{:s}group {:s}:"
                result += format.format("", dir)

                result += __create_group(join(root, dir), indent + 1)

    #

    return result


def __create_module(name, indent=0):
    if indent > 0:
        format = "{: >%ds}module {:s}" % int(4 * indent)
    else:
        format = "{:s}module {:s}"
    return format.format("", name)


def __create_config(root):
    result = str()
    result += "ignore failed\n"
    result += __create_group(root)
    return result


def print_help():
    print "usage: m3highload-test [--verbose] [--no-decoration] [--log file] [--help | --generate-config | [--config path] [--host path] [--port port] [--use-http]]\n" \
            "  --config          Load config from the specified file.\n" \
            "  --host            Server host.\n" \
            "  --port            Server port.\n" \
            "  --use-http        Force to use http instead of https.\n" \
            "  --verbose         Print debug information during execution.\n" \
            "  --log             Write logs into the specified file.\n" \
            "  --no-decoration   Turn off output formatting.\n" \
            "  --generate-config Generate configuration file.\n" \
            "  --help            Show this message.\n"

def init():
    import sys
    from plamee import log

    global config
    global host
    global port
    global http

    alist = list()
    map(lambda arg: alist.append([arg, None]) if not arg.find("--") else alist[len(alist) - 1].__setitem__(1, arg), sys.argv[1:])

    amap = dict(alist)


    if "--no-decoration" in amap:
        if amap["--no-decoration"] is not None:
            log.error("Invalid argument '%s'." % amap["--no-decoration"], False)
            print_help()
            sys.exit(-1)
        log.decoration = False
        del amap["--no-decoration"]

    if "--verbose" in amap:
        if amap["--verbose"] is not None:
            log.error("Invalid argument '%s'." % amap["--verbose"], False)
            print_help()
            sys.exit(-1)
        log.level = 0
        del amap["--verbose"]

    if "--log" in amap:
        file = amap["--log"]
        if file is None:
            log.error("Output file is not specified.", False)
        log.file = file
        del amap["--log"]

    if "--help" in amap:
        if amap["--help"] is not None:
            log.error("Invalid argument '%s'." % amap["--help"], False)
            print_help()
            sys.exit(-1)
        if len(amap.keys()) > 1:
            log.error("Too many arguments.", False)
            print_help()
            sys.exit(-1)
        print_help()
        sys.exit(0)

    if "--generate-config" in amap:
        if len(amap.keys()) > 1:
            print_help()
            log.error("Too many arguments.", False)
            sys.exit(-1)
        file = amap["--generate-config"]
        if file is None:
            log.error("Output file is not specified.", False)
        __generate_config(file)
        sys.exit(0)

    for arg in amap:
        if arg == "--config":
            if amap[arg] is not None:
                config = str(amap[arg])
            else:
                log.error("Config file is not specified.", False)
        elif arg == "--host":
            if amap[arg] is not None:
                host = str(amap[arg])
            else:
                log.error("Host is not specified.", False)
        elif arg == "--port":
            if amap[arg] is not None:
                port = int(amap[arg])
            else:
                log.error("Port is not specified.", False)
        elif arg == "--use-http":
            if amap["--use-http"] is not None:
                log.error("Invalid argument '%s'." % amap["--use-http"], False)
                print_help()
                sys.exit(-1)
            http = True
        else:
            log.error("Invalid argument '%s'." % arg, False)
            print_help()
            sys.exit(-1)

    __load_config(config)

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