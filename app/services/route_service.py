import logging

from app.core.decorators import log_execution_time
from app.core.exceptions import NotFoundError
from app.models import RouteQuery
from app.repositories.edge_repository import EdgeRepository
from app.repositories.route_repository import HistoryFilter, RouteQueryRepository
from app.services.graph import GraphCache, build_graph
from app.services.node_service import NodeService
from app.services.routing_strategy import RoutingStrategy

logger = logging.getLogger("network_route_optimizer")


class RouteService:
    def __init__(
        self,
        nodes: NodeService,
        edges: EdgeRepository,
        history: RouteQueryRepository,
        strategy: RoutingStrategy,
        graph_cache: GraphCache,
    ) -> None:
        self.nodes = nodes
        self.edges = edges
        self.history = history
        self.strategy = strategy
        self.graph_cache = graph_cache

    @log_execution_time(logger)
    def find_shortest(self, source: str, destination: str) -> RouteQuery:
        self.nodes.resolve_or_raise(source, destination)

        graph = self.graph_cache.get_or_build(lambda: build_graph(self.edges.list_all()))
        result = self.strategy.find_path(graph, source, destination)
        if result is None:
            raise NotFoundError(f"No path exists between {source} and {destination}")

        return self.history.add(source, destination, result.path, result.total_latency)

    def get_history(self, filters: HistoryFilter) -> list[RouteQuery]:
        return self.history.search(filters)
