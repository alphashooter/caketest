import sys
import traceback

from plamee.cakestory import *
from plamee import log

def __exit(errors):
    log.error("Test failed.", False)
    log.message("Errors:\n\n%s" % "\n".join("%d. %s" % (i + 1, errors[i]) for i in range(len(errors))))
    sys.exit(-1)

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



def run(host, port=None, http=False, config=None) :
    from os.path import dirname, normpath, join
    from plamee.parser import Parser, Group

    Net.connect(host=host, port=port, http=http)

    dir = dirname(__file__)

    if not config:
        config = "/tmp/test.conf"
        file = open(config, "w")
        file.write(__create_config(dir))
        log.debug("Generated configuration file:\n\n%s" % config)

    parser = Parser(config)

    root = Group("plamee", dir=normpath(join(dir, "../../../")))

    prnt = root
    prnt.ignore_failed = True

    chld = Group("cakestory", prnt)
    prnt.modules.append(chld)
    prnt = chld
    prnt.ignore_failed = True

    chld = Group("test", prnt)
    prnt.modules.append(chld)

    chld.parse(parser)

    result = False
    try:
        result = chld.run()
    except:
        log.error("Group 'test' failed.", False)
        log.message("".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))

    log.info("All tests finished.")

    if not result:
        __exit(root.errors)
    else:
        log.ok("All tests successfully passed.")