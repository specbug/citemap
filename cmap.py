from typing import List, Optional
from collections import defaultdict


class CMap:
    def __init__(self):
        self._edges = set()
        self._hmap = dict()
        self._root = None

    @property
    def edges(self):
        return self._edges

    @property
    def root(self):
        return self._root

    @property
    def size(self):
        return len(self._edges)

    def connected(self, source: str, destination: str) -> bool:
        return self._hmap.get(f'{source} –– {destination}', False)

    def connect(self, source: Optional[str], destination: str):
        if self.connected(source, destination):
            return
        print(f'{source} –> {destination}')
        self._edges.add((source, destination))
        self._hmap[f'{source} –– {destination}'] = True
        if not source:
            self._root = destination

