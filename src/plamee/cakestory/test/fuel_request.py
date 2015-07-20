from plamee.Test import Test
from plamee.cakestory import *

def __check_requests(friend):
    fuel_requests = 0
    if len(friend.inbox.messages) > 0:
        fuel_requests = reduce(lambda res, x: res + x, map(lambda msg: 1 if msg.type == MessageType.FUEL_REQUEST else 0, friend.inbox.messages))
    if fuel_requests > 1:
        raise RuntimeError()

#

def __send_requests(client, friend):
    chapter = client.map.current_chapter
    if chapter is None:
        return False

    #

    Test.next_iteration()

    chapter.force_finish()

    client.request_fuel(friend)
    client.request_fuel(friend)

    __check_requests(friend)
    return True

#

client = Client(network="FB")
friend = Client(network="FB")

Test.start_module("fuel_request", len(client.map.chapters))
while __send_requests(client, friend): pass