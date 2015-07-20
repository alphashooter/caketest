from cakestory.test import *

net.connection("m3highload-master.test.nsk.plamee.com")

client = Client(network="FB", nid="test")

if not "hello" in client.storage:
    print "hello: " + "undefined"
    client.storage["hello"] = "world"
else:
    print "hello: " + client.storage["hello"]