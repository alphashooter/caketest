import sys
import traceback

from plamee.cakestory import *
from plamee import log

def __exit(errors=None):
    log.error("Test failed.", False)
    if errors and len(errors):
        log.message("Errors:\n\n%s" % "\n".join("%d. %s" % (i + 1, errors[i]) for i in range(len(errors))))
    sys.exit(-1)


def run(host, config, port=None, http=False) :
    from os.path import dirname, normpath, join
    from plamee.config import ConfigParser, Group

    Net.connect(host=host, port=port, http=http)

    dir = dirname(__file__)

    parser = ConfigParser(config)

    root = Group("plamee", dir=normpath(join(dir, "../../../")))

    prnt = root
    prnt.ignore_failed = True

    chld = Group("cakestory", prnt)
    prnt.modules.append(chld)
    prnt = chld
    prnt.ignore_failed = True

    chld = Group("test", prnt)
    prnt.modules.append(chld)

    try:
        chld.parse(parser)
    except:
        log.error(sys.exc_value.message, False)
        __exit()

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