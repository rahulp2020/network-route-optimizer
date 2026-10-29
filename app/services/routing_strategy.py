import heapq
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.graph import Graph


@dataclass(frozen=True)
class PathResult:
    total_latency: float
    path: list[str]


class RoutingStrategy(ABC):
    @abstractmethod
    def find_path(self, graph: Graph, source: str, destination: str) -> PathResult | None:
        ...


class DijkstraStrategy(RoutingStrategy):
    def find_path(self, graph: Graph, source: str, destination: str) -> PathResult | None:
        if source == destination:
            return PathResult(total_latency=0.0, path=[source])

        distances: dict[str, float] = {source: 0.0}
        previous: dict[str, str] = {}
        visited: set[str] = set()
        heap: list[tuple[float, str]] = [(0.0, source)]

        while heap:
            distance, node = heapq.heappop(heap)
            if node in visited:
                continue
            if node == destination:
                path = self._rebuild_path(previous, source, destination)
                return PathResult(total_latency=round(distance, 4), path=path)
            visited.add(node)
            for neighbor, latency in graph.get(node, []):
                candidate = distance + latency
                if candidate < distances.get(neighbor, math.inf):
                    distances[neighbor] = candidate
                    previous[neighbor] = node
                    heapq.heappush(heap, (candidate, neighbor))

        return None

    @staticmethod
    def _rebuild_path(previous: dict[str, str], source: str, destination: str) -> list[str]:
        path = [destination]
        while path[-1] != source:
            path.append(previous[path[-1]])
        path.reverse()
        return path
