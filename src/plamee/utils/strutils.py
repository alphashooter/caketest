import string
import random


def random_string(length, chars=None):
    if not chars:
        chars = string.printable
    return "".join(random.choice(chars) for i in range(length))
