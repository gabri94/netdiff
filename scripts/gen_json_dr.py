import os
import json
import urllib
from netdiff.olsr1 import Olsr1Parser


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
roma = open('{0}/topology.json'.format(CURRENT_DIR)).read()

firenze = "http://10.150.25.1:9090/"
response = urllib.urlopen(firenze).read()
topology = json.loads(response)
parser = Olsr1Parser(old=topology, new=topology)
graph = parser.gen_graph()

print(graph)
