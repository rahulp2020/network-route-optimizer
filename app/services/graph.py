from collections import defaultdict
from collections.abc import Callable, Iterable

from app.models import Edge

Graph = dict[str, list[tuple[str, float]]]


def build_graph(edges: Iterable[Edge]) -> Graph:
    graph: Graph = defaultdict(list)
    for edge in edges:
        graph[edge.source.name].append((edge.destination.name, edge.latency))
    return graph


class GraphCache:
    def __init__(self) -> None:
        self._graph: Graph | None = None

    def get_or_build(self, builder: Callable[[], Graph]) -> Graph:
        if self._graph is None:
            self._graph = builder()
        return self._graph

    def invalidate(self) -> None:
        self._graph = None
