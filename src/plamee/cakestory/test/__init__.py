import sys
import traceback
import plamee.log as log

from time import sleep
from importlib import import_module

from plamee.cakestory import *
from plamee import log

def run_module(file):
    try:
        import_module(file)
    except:
        log.error("Error occured during executing module '%s'" % file, False)
        log.message("".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
        return False
    return True

def exit():
    log.message("Test failed.")
    sys.exit(-1)

def run(host, port=None, http=False, config=None) :
    Net.connect(host=host, port=port, http=http)

    from os import listdir
    from os.path import isfile, dirname, join

    dir = dirname(__file__)

    files = listdir(dir)
    files = filter(lambda file: isfile(join(dir, file)), files)
    files = filter(lambda file: re.match(r"^.+\.py$", file) is not None, files)
    files = map(lambda file: re.match(r"^(.+)\.py$", file).group(1), files)
    files = filter(lambda file: re.match(r"^__.+__$", file) is None, files)
    files = filter(lambda file: re.match(r"^.*?_example$", file) is None, files)

    log.info("Loading modules:\n%s" % "\n".join(map(lambda file: str("  * %s" % file), files)))

    sys.path.extend([dir])
    for file in files:
        log.info("Starting module '%s'..." % file)
        sleep(3)
        if run_module(file):
            log.info("Module '%s' executed successfully." % file)
        else:
            log.error("Module '%s' failed." % file, False)
            exit()

    log.message("All tests passed.")
