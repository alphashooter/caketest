from plamee.cakestory import *

client = Client()

types = client.defs["level_types"]

for type in types.keys():
    if not "process_extra" in types[type]["boosters"]:
        raise RuntimeError("No 'process_extra' field for level '%s'." % type)