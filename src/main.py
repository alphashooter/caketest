import sys
from os.path import dirname

import plamee.cakestory.test as test

sys.path.extend([dirname(__file__)])

test.run()