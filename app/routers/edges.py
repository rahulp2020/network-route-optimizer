from fastapi import APIRouter, Depends, status

from app.dependencies import get_edge_service
from app.models import Edge
from app.schemas.edge import EdgeCreate, EdgeResponse
from app.services.edge_service import EdgeService

router = APIRouter(prefix="/edges", tags=["Edges"])


def _to_response(edge: Edge) -> EdgeResponse:
    return EdgeResponse(id=edge.id, source=edge.source.name, destination=edge.destination.name, latency=edge.latency)


@router.post("", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
def create_edge(payload: EdgeCreate, service: EdgeService = Depends(get_edge_service)) -> EdgeResponse:
    edge = service.create(payload.source, payload.destination, payload.latency)
    return _to_response(edge)


@router.get("", response_model=list[EdgeResponse])
def list_edges(service: EdgeService = Depends(get_edge_service)) -> list[EdgeResponse]:
    return [_to_response(edge) for edge in service.list_all()]


@router.delete("/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_edge(edge_id: int, service: EdgeService = Depends(get_edge_service)) -> None:
    service.delete(edge_id)
