from plamee.cakestory import *

Net.connect("m3highload-master.test.nsk.plamee.com")

import fuel_request
import bonus_score

def run() :
    fuel_request.run()
    bonus_score.run()