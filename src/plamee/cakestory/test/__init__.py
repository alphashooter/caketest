import sys
import traceback

from time import sleep
from importlib import import_module

from plamee.cakestory import *

def run_module(file):
    try:
        import_module(file)
    except:
        print "\033[1m\033[31mError occured during executing module '%s'\033[0m\n" % file

        traceback.print_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)
        print ""

        return False
    return True

def exit():
    print "\033[1mTest failed.\033[0m"
    print ""
    sys.exit(-1)

def run() :
    Net.connect("m3highload-master.test.nsk.plamee.com")

    from os import listdir
    from os.path import isfile, dirname, join

    dir = dirname(__file__)

    files = listdir(dir)
    files = filter(lambda file: isfile(join(dir, file)), files)
    files = filter(lambda file: re.match(r"^.+\.py$", file) is not None, files)
    files = map(lambda file: re.match(r"^(.+)\.py$", file).group(1), files)
    files = filter(lambda file: re.match(r"^__.+__$", file) is None, files)

    print "\033[1mLoading modules: \033[31m" + "".join(map(lambda file: "\n  * %s" % file, files)) + "\033[0m"
    print ""

    sys.path.extend([dir])
    for file in files:
        print "\033[1mStarting module '\033[31m%s\033[30m'...\033[0m" % file
        print ""
        sleep(3)
        if run_module(file):
            print "\033[1m\033[32mModule '%s' executed successfully.\033[0m" % file
            print ""
        else:
            print "\033[1m\033[31mModule '%s' failed.\033[0m" % file
            print ""
            exit()

    print "\033[1mAll tests passed.\033[0m"
    print ""