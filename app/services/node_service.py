from app.core.exceptions import BadRequestError, NotFoundError
from app.models import Node
from app.repositories.exceptions import DuplicateEntityError
from app.repositories.node_repository import NodeRepository
from app.services.graph import GraphCache


class NodeService:
    def __init__(self, nodes: NodeRepository, graph_cache: GraphCache) -> None:
        self.nodes = nodes
        self.graph_cache = graph_cache

    def create(self, name: str) -> Node:
        if self.nodes.exists(name):
            raise BadRequestError(f"Node '{name}' already exists")
        try:
            return self.nodes.add(name)
        except DuplicateEntityError as exc:
            raise BadRequestError(exc.message) from exc

    def list_all(self) -> list[Node]:
        return self.nodes.list_all()

    def delete(self, node_id: int) -> None:
        node = self.nodes.get(node_id)
        if node is None:
            raise NotFoundError(f"Node with id {node_id} not found")
        self.nodes.delete(node)
        self.graph_cache.invalidate()

    def resolve_or_raise(self, *names: str) -> dict[str, Node]:
        found = self.nodes.get_many_by_names(names)
        missing = [name for name in dict.fromkeys(names) if name not in found]
        if missing:
            raise BadRequestError(f"Node not found: {', '.join(missing)}")
        return found
