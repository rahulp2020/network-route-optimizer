from app.core.exceptions import BadRequestError, NotFoundError
from app.models import Edge
from app.repositories.edge_repository import EdgeRepository
from app.repositories.exceptions import DuplicateEntityError
from app.services.graph import GraphCache
from app.services.node_service import NodeService


class EdgeService:
    def __init__(self, nodes: NodeService, edges: EdgeRepository, graph_cache: GraphCache) -> None:
        self.nodes = nodes
        self.edges = edges
        self.graph_cache = graph_cache

    def create(self, source_name: str, destination_name: str, latency: float) -> Edge:
        resolved = self.nodes.resolve_or_raise(source_name, destination_name)
        source, destination = resolved[source_name], resolved[destination_name]

        if self.edges.exists_between(source.id, destination.id):
            raise BadRequestError(f"Edge from {source.name} to {destination.name} already exists")

        try:
            edge = self.edges.add(source, destination, latency)
        except DuplicateEntityError as exc:
            raise BadRequestError(exc.message) from exc

        self.graph_cache.invalidate()
        return edge

    def list_all(self) -> list[Edge]:
        return self.edges.list_all()

    def delete(self, edge_id: int) -> None:
        edge = self.edges.get(edge_id)
        if edge is None:
            raise NotFoundError(f"Edge with id {edge_id} not found")
        self.edges.delete(edge)
        self.graph_cache.invalidate()
