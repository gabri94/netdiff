import os
import json
import urllib
from netdiff.olsr1 import Olsr1Parser

firenze = "http://10.150.25.1:9090/"
response = urllib.urlopen(firenze)
topology = json.loads(response.read())
parser = Olsr1Parser(old=topology, new=topology)
graph = parser.gen_graph()

print(graph)
