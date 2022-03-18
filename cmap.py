from typing import List, Optional
from collections import defaultdict


class CNode:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.children = []

    def get_children(self) -> List['CNode']:
        return self.children

    def add_children(self, children: List['CNode']):
        self.children.extend(children)


class CMap:
    def __init__(self, base_url: str):
        self._states = defaultdict(None)
        self.root = CNode('root', base_url)
        self.__post_init__()

    def __post_init__(self):
        self._states['root'] = self.root

    def __repr__(self):
        return self.__show(self.root)

    @property
    def states(self) -> List[CNode]:
        return list(self._states.values())

    def add(self, name: str, url: str, parent: Optional[str] = None):
        if parent is None:
            parent = 'root'
        if parent not in self._states:
            self._states[parent] = CNode(parent, self._states[parent].url)
        self._states[parent].add_children([CNode(name, url)])

    def get(self, name: str) -> Optional[CNode]:
        return self._states.get(name)

    def destroy(self):
        self._states.clear()
        self.root = None

    def __show(self, node: CNode, indent: int = 4):
        representation = [f'–{node.name.split("-")[-1]}']
        for child in node.children:
            representation.extend(['\n', ' ' * indent, self.__show(child, indent * 2)])
        return ''.join(representation)
