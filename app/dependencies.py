from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.edge_repository import EdgeRepository
from app.repositories.node_repository import NodeRepository
from app.repositories.route_repository import RouteQueryRepository
from app.services.edge_service import EdgeService
from app.services.graph import GraphCache
from app.services.node_service import NodeService
from app.services.route_service import RouteService
from app.services.routing_strategy import DijkstraStrategy, RoutingStrategy


def get_node_repository(db: Session = Depends(get_db)) -> NodeRepository:
    return NodeRepository(db)


def get_edge_repository(db: Session = Depends(get_db)) -> EdgeRepository:
    return EdgeRepository(db)


def get_route_history_repository(db: Session = Depends(get_db)) -> RouteQueryRepository:
    return RouteQueryRepository(db)


def get_graph_cache(request: Request) -> GraphCache:
    return request.app.state.graph_cache


def get_routing_strategy() -> RoutingStrategy:
    return DijkstraStrategy()


def get_node_service(
    nodes: NodeRepository = Depends(get_node_repository),
    graph_cache: GraphCache = Depends(get_graph_cache),
) -> NodeService:
    return NodeService(nodes, graph_cache)


def get_edge_service(
    node_service: NodeService = Depends(get_node_service),
    edges: EdgeRepository = Depends(get_edge_repository),
    graph_cache: GraphCache = Depends(get_graph_cache),
) -> EdgeService:
    return EdgeService(node_service, edges, graph_cache)


def get_route_service(
    node_service: NodeService = Depends(get_node_service),
    edges: EdgeRepository = Depends(get_edge_repository),
    history: RouteQueryRepository = Depends(get_route_history_repository),
    strategy: RoutingStrategy = Depends(get_routing_strategy),
    graph_cache: GraphCache = Depends(get_graph_cache),
) -> RouteService:
    return RouteService(node_service, edges, history, strategy, graph_cache)
