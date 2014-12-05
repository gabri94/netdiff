import json
import networkx as nx
from networkx.readwrite import json_graph


class BaseParser(object):
    """ Generic Topology Parser """

    def __init__(self, old=None, new=None, oldint=None, newint=None):
        """
        Initializes a new Parser

        :param str old: a JSON or dict representing the old topology
        :param str new: a JSON or dict representing the new topology
        """
        if old:
            self.old_graph = self._parse(old)
        else:
            if oldint:
                self.old_graph = self._parse_netjson(oldint)
            else:
                self.old_graph = nx.Graph()

        if new:
            self.new_graph = self._parse(new)
        else:
            if newint:
                self.new_graph = self._parse_netjson(newint)
            else:
                self.new_graph = nx.Graph()

    def diff(self, cost=False, python=True, **kwargs):
        """
        Returns netdiff in a python dictionary
        """
        if python:
            return {
                "added": self._make_diff(self.new_graph, self.old_graph, cost),
                "removed": self._make_diff(self.old_graph, self.new_graph, cost)
            }
        else:
            return json.dumps(self.diff(cost),  **kwargs)

    # --- private methods --- #

    def _parse_netjson(self, topology):
        # https://github.com/interop-dev/json-for-networks/blob/master/examples/network-routes.json
        graph = nx.Graph()
        for link in topology['routes']:
            graph.add_edge(link['source'], link['next'], weight=link['cost'])
        return graph

    def _parse(self):
        raise NotImplementedError()

    def _make_diff(self, old, new, cost):
        """
        calculates differences between topologies 'old' and 'new'
        if cost is False: No Metric is used to make the diff.
        otherwise, we use cost as a tolerance factor.
        returns a list of links
        """
        # make a copy of old topology to avoid tampering with it
        diff = old.copy()
        not_different = []
        # loop over all links
        for old_edge in old.edges(data=True):
            # if link is also in new topology add it to the list
            for new_edge in new.edges(data=True):
                if old_edge[0] in new_edge and old_edge[1] in new_edge:
                    if not cost:
                        not_different.append(old_edge)
                    else:
                        # check if the old link metric is inside of the
                        # tolerance windows
                        if(new_edge[2]['weight']/cost
                           <= old_edge[2]['weight'] <=
                           new_edge[2]['weight']*cost):
                            not_different.append(old_edge)
        # keep only differences
        diff.remove_edges_from(not_different)

    # return the edges with the data
        return diff.edges(data=True)

    def gen_graph(self):
        node_bc = nx.betweenness_centrality(self.new_graph, weight="weight")
        node_dc = nx.degree_centrality(self.new_graph)
        edge_bc = nx.edge_betweenness_centrality(self.new_graph, weight="weight")
        nx.set_edge_attributes(self.new_graph, 'betweenness', edge_bc)

        for node in self.new_graph.nodes():
            self.new_graph.node[node]["bw"] = node_bc[node]
            self.new_graph.node[node]["dc"] = node_dc[node]
        # print self.new_graph.edges(data=True)

        graph = json_graph.node_link_data(self.new_graph)
        return json.dumps(graph)
