from cakestory.test import *

net.connection("m3highload-master.test.nsk.plamee.com")

client = Client(network="FB", nid="test")
friend1 = Client(network="FB", nid="friend1")

for message in friend1.inbox.messages:
    message.read()

for message in client.inbox.messages:
    print message.type
    message.read()