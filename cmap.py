import os
import tldextract
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import defaultdict
from typing import List, Optional, Set, Tuple

from config import STATIC_FOLDER


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
        filename = os.path.join(STATIC_FOLDER, filename)
        nx.write_gpickle(self.graph, filename)

    def load(self, filename: Optional[str] = None):
        filename = filename or f'{str(tldextract.extract(self.root).domain)}.gpickle'
        filename = os.path.join(STATIC_FOLDER, filename)
        self._graph = nx.read_gpickle(filename)
        return self._graph

    def plot(self, filename: Optional[str] = None, height: str = '100%', width: str = '100%'):
        net = Network(height=height, width=width, directed=True)
        net.from_nx(self._graph)
        # TODO: parameterize
        net.set_options(
            """
            var options = {
              "edges": {
                "arrows": {
                  "to": {
                    "enabled": true,
                    "scaleFactor": 0.5
                  }
                },
                "color": {
                  "inherit": true
                },
                "smooth": false
              },
              "physics": {
                "barnesHut": {
                  "gravitationalConstant": -10000,
                  "springConstant": 0.003
                },
                "minVelocity": 0.75
              }
            }
            """
        )
        # net.show_buttons(filter_=['physics'])
        for node in net.nodes:
            node['size'] = 15
            node['label'] = ''
            node['title'] = f'<a href="{node["id"]}">{node["id"]}</a>'
            if node['id'] == self._root:
                node['color'] = '#ff0000'
        filename = filename or f'{str(tldextract.extract(self.root).domain)}.html'
        filename = os.path.join(STATIC_FOLDER, filename)
        net.save_graph(filename)
        return filename


