from plamee.cakestory.test import *

Net.connect("m3highload-master.test.nsk.plamee.com")

client = Client(network="FB", nid="test")
client.boosters[BoosterType.REVERSE].force_spend(10)