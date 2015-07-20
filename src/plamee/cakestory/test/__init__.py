from importlib import import_module

from plamee.Test import Test
from plamee.cakestory import *

def run() :
    Net.connect("m3highload-master.test.nsk.plamee.com")

    import sys
    from os import listdir
    from os.path import isfile, dirname, join

    dir = dirname(__file__)

    files = listdir(dir)
    files = filter(lambda file: isfile(join(dir, file)), files)
    files = filter(lambda file: re.match(r"^.+\.py$", file) is not None, files)
    files = map(lambda file: re.match(r"^(.+)\.py$", file).group(1), files)
    files = filter(lambda file: re.match(r"^__.+__$", file) is None, files)


    Test.start_test(files)

    sys.path.extend([dir])
    map(lambda file: import_module(file), files)

    Test.finish_test()