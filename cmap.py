import tldextract
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import defaultdict
from typing import List, Optional, Set, Tuple


class CMap:
    def __init__(self):
        self._edges = set()
        self._hmap = dict()
        self._root = None
        self._graph = None

    @property
    def edges(self):
        return self._edges

    @edges.setter
    def edges(self, edges: Set[Tuple[str, str]]):
        self._edges = set(edges)

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, root: str):
        self._root = root

    @property
    def size(self):
        return len(self._edges)

    @property
    def graph(self):
        return self._graph

    def connected(self, source: str, destination: str) -> bool:
        return self._hmap.get(f'{source} - {destination}', False) or self._hmap.get(f'{destination} - {source}', False)

    def connect(self, source: Optional[str], destination: str):
        if self.connected(source, destination):
            return
        print(f'{source} –> {destination}')
        self._edges.add((source, destination))
        self._hmap[f'{source} - {destination}'] = True
        if not source:
            self._root = destination

    def cart(self):
        edges = self._edges - {(None, self._root)}
        self._graph = nx.DiGraph()
        self._graph.add_edges_from(edges)
        return self._graph

    def save(self, filename: Optional[str] = None):
        filename = filename or f'{str(tldextract.extract(self.root).domain)}.gpickle'
        nx.write_gpickle(self.graph, filename)

    def load(self, filename: Optional[str] = None):
        filename = filename or f'{str(tldextract.extract(self.root).domain)}.gpickle'
        self._graph = nx.read_gpickle(filename)
        return self._graph

    def plot(self, filename: Optional[str] = None, height: int = 1200, width: str = '100%'):
        net = Network(height=height, width=width, directed=True, heading=self._root)
        net.from_nx(self._graph)
        # net.show_buttons(filter_=['physics'])
        net.set_options(
            """
            var options = {
              "physics": {
                "barnesHut": {
                  "gravitationalConstant": -15000,
                  "centralGravity": 1
                },
                "minVelocity": 0.75
              }
            }
            """
        )
        for node in net.nodes:
            node['size'] = 15
            node['label'] = ''
            node['title'] = f'<a href="{node["id"]}">{node["id"]}</a>'
            if node['id'] == self._root:
                node['color'] = '#ff0000'
        net.save_graph(filename or f'{str(tldextract.extract(self.root).domain)}.html')


