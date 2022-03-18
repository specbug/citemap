from dataclasses import dataclass
from typing import List, Optional
from collections import defaultdict


@dataclass
class CNode:
    def __init__(self, url: str, title: str, desc: str, name: Optional[str] = None):
        self.url = url
        self.desc = desc
        self.name = name
        self.title = title
        self.children = []

    def __post_init__(self):
        self.title = self.title.strip().capitalize()
        self.desc = self.desc.strip()
        if self.name is None:
            self.name = self.title[:7]
        self.name = self.name.strip().lower()

    def get_children(self) -> List['CNode']:
        return self.children

    def add_children(self, children: List['CNode']):
        self.children.extend(children)


class CMap:
    def __init__(self):
        self._states = defaultdict(None)

    @property
    def states(self) -> List[CNode]:
        return list(self._states.values())

    def add(self, url: str, **kwargs):
        node = CNode(url=url, **kwargs)
        self._states[url] = node

    def get(self, url: str) -> Optional[CNode]:
        return self._states.get(url)

    @staticmethod
    def map(child: CNode, parent: CNode):
        parent.add_children([child])

    def destroy(self):
        self._states.clear()

    def show(self, node: CNode, indent: int = 4):
        representation = [f'–{node.name.split("-")[-1]}']
        for child in node.children:
            representation.extend(['\n', ' ' * indent, self.show(child, indent * 2)])
        return ''.join(representation)
