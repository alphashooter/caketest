from plamee.cakestory import *

import time
import json
from os.path import join, dirname

config = json.loads(open(join(dirname(__file__), "config.json"), "r").read().decode("utf-8"))

threshold    = config["threshold"]
speed_limit  = config["speed_limit"]
possibility  = float(threshold * speed_limit)
requirements = config["requirements"]
groups       = config["groups"]

def combination(n, k):
    if k == 0:
        return 1

    divident = float(n)
    divisor  = float(k)

    i = n - 1
    while i > (n - k):
        divident *= i
        i -= 1

    j = k - 1
    while j > 1:
        divisor *= j
        j -= 1

    return divident / divisor

def get_error(nu, ng, p):
    na = range(0, ng - 1) + range(ng + 1, nu)
    da = map(lambda x: abs(1 - x / (nu * p)), na)
    pa = map(lambda x: combination(nu, x) * pow(p, x) * pow(1.0 - p, nu - x), na)
    return sum(map(lambda x: da[x] * pa[x], range(len(da))), 0)

def create_user():
    global requirements

    user = None

    for i in range(0, 5):
        user = Client()
        user.init()
        for req in requirements:
            if user.state.data.get_dotted(req) != requirements[req]:
                if isinstance(requirements[req], list):
                    if not user.state.data.get_dotted(req) in requirements[req]:
                        user = None
                        break
                else:
                    user = None
                    break
        if user is not None:
            break

    if user is None:
        raise RuntimeError("Cannot generate new user according to test requirements.")
    return user


def create_users(num):
    users = list()
    while(len(users) < num):
        users.append(create_user())
    return users


def check_defs(users):
    default = users["default"]
    default_defs = default[0].defs.data.copy()

    for user in default[1:]:
        if user.defs.data != default_defs:
            raise RuntimeError("Defs in group 'default' are different.")

    for group in users:
        if group == "default":
            continue

        group_defs = users[group][0].defs.data.copy()
        for user in users[group][1:]:
            if user.defs.data != group_defs:
                raise RuntimeError("Defs in group '%s' are different." % group)

        common_default_defs = default_defs.copy()
        common_group_defs = group_defs.copy()
        for prop in groups[group]["changes"]["defs"]:
            common_default_defs.delete_dotted(prop)
            common_group_defs.delete_dotted(prop)
            if group_defs.get_dotted(prop) != groups[group]["changes"]["defs"][prop]:
                raise RuntimeError("Defs changes check failed for group '%s'." % group)

        if common_default_defs != common_group_defs:
            raise RuntimeError("Defs for group '%s' has too many differences." % group)


def check_groups_1():
    global groups

    # summary number of users in all groups
    N_g = sum(map(lambda group: group["size"], groups.values()), 0)
    # number of users to be generated
    N_u = int(0.5 * N_g / possibility)

    users  = create_users(N_u)
    mapped = dict()

    mapped["default"] = list()
    for group in groups:
        mapped[group] = list()

    map(lambda user: mapped[user.state.group].append(user), users)

    S_g = sum(map(lambda group: len(mapped[group]) if group != "default" else 0, groups.keys()), 0)

    deviation = abs(float(S_g) / (0.5 * N_g) - 1.0)
    if deviation > get_error(N_u, int(0.5 * N_g), possibility):
        raise RuntimeError("Invalid distribution first wave: expected deviation less than %d%% but got %d%%." % (100.0 * get_error(N_u, int(0.5 * N_g), possibility) + 0.5, 100.0 * deviation + 0.5))

    check_defs(mapped)

    return mapped


def check_groups_2():
    global groups

    # summary number of users in all groups
    N_g = sum(map(lambda group: group["size"], groups.values()), 0)
    # number of users to be generated
    N_u = int(0.5 * N_g / possibility)

    users  = create_users(N_u)
    mapped = dict()

    mapped["default"] = list()
    for group in groups:
        mapped[group] = list()

    map(lambda user: mapped[user.state.group].append(user), users)

    S_g = sum(map(lambda group: len(mapped[group]) if group != "default" else 0, groups.keys()), 0)

    deviation = abs(float(S_g) / (0.5 * N_g) - 1.0)
    if deviation > get_error(N_u, int(0.5 * N_g), possibility):
        raise RuntimeError("Invalid distribution second wave: expected deviation less than %d%% but got %d%%." % (100.0 * get_error(N_u, int(0.5 * N_g), possibility) + 0.5, 100.0 * deviation + 0.5))

    check_defs(mapped)

    return mapped

def check_groups_3():
    global groups

    # summary number of users in all groups
    N_g = sum(map(lambda group: group["size"], groups.values()), 0)
    # number of users to be generated
    N_u = int(N_g / possibility)

    users  = create_users(N_u)
    mapped = dict()

    mapped["default"] = list()
    for group in groups:
        mapped[group] = list()

    map(lambda user: mapped[user.state.group].append(user), users)

    check_defs(mapped)

    return mapped



#
# Test start
#

mapped = dict()
mapped["default"] = list()
for group in groups.keys():
    mapped[group] = list()

# Test 1:

mapped_tmp = check_groups_1()
for group in mapped_tmp:
    mapped[group] += mapped_tmp[group]

time.sleep(3600)

# Test 2:

mapped_tmp = check_groups_2()
for group in mapped_tmp:
    mapped[group] += mapped_tmp[group]

time.sleep(3600)

# Test 3:

mapped_tmp = check_groups_3()
for group in mapped_tmp:
    mapped[group] += mapped_tmp[group]

for group in mapped:
    if group == "default":
        continue
    if len(mapped[group]) > groups[group]["size"]:
        raise RuntimeError("Too many users in group '%s'" % group)