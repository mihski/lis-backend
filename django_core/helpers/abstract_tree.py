from abc import ABC, abstractmethod
from collections import defaultdict


class AbstractNode(ABC):
    children: set['AbstractNode']

    @abstractmethod
    def obj(self):
        pass

    @abstractmethod
    def id(self):
        pass

    @abstractmethod
    def next_ids(self) -> list[str]:
        pass


class AbstractNodeTree(ABC):
    node_cls = None

    def __init__(self):
        self.tree = self.node_cls(self._get_first_element())
        self.tree_elements: dict[str, AbstractNode] = {self.tree.id: self.tree}
        self._build_tree()

    @abstractmethod
    def _get_first_element(self):
        pass

    @abstractmethod
    def _get_element_by_id(self, element_id: str):
        pass

    def _build_tree(self):
        queue = [self.tree.local_id]
        visited = defaultdict(bool)
        i = 0

        while i < len(queue):
            node_local_id = queue[i]
            node = self.tree_elements[node_local_id]

            if visited[node_local_id]:
                i += 1
                continue

            visited[node_local_id] = True

            for child_local_id in node.next_ids:
                if child_local_id not in self.tree_elements:
                    self.tree_elements[child_local_id] = self.node_cls(
                        self._get_element_by_id(child_local_id)
                    )

                child = self.tree_elements[child_local_id]

                node.children.add(child)
                queue.append(child_local_id)

            i += 1
