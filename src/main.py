from cakestory.test import *

net.connection("m3highload-master.test.nsk.plamee.com")

client = Client(network="FB", nid="test")
friend1 = Client(network="FB", nid="friend1")

print client.send_life(friend1)