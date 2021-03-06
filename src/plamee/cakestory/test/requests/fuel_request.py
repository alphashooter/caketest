from plamee.cakestory import *

def __check_requests(friend):
    fuel_requests = 0
    if len(friend.inbox.messages) > 0:
        fuel_requests = reduce(lambda res, x: res + x, map(lambda msg: 1 if msg.type == MessageType.REQUEST_FUEL else 0, friend.inbox.messages))
    if fuel_requests > 1:
        raise RuntimeError("Test failed.")

#

def __send_requests(client, friend):
    chapter = client.map.current_chapter
    if chapter is None:
        return False

    #

    chapter.force_finish()

    client.request_fuel(friend)
    client.request_fuel(friend)

    __check_requests(friend)
    return True

#

client = Client(network="FB")
friend = Client(network="FB")

while __send_requests(client, friend): pass