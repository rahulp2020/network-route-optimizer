from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_route_service
from app.models import RouteQuery
from app.repositories.route_repository import HistoryFilter
from app.schemas.route import (
    RouteHistoryQuery,
    RouteHistoryResponse,
    ShortestRouteRequest,
    ShortestRouteResponse,
)
from app.services.route_service import RouteService

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post("/shortest", response_model=ShortestRouteResponse)
def find_shortest_route(
    payload: ShortestRouteRequest,
    service: RouteService = Depends(get_route_service),
) -> ShortestRouteResponse:
    record = service.find_shortest(payload.source, payload.destination)
    return ShortestRouteResponse(total_latency=record.total_latency, path=record.path)


@router.get("/history", response_model=list[RouteHistoryResponse])
def get_route_history(
    query: Annotated[RouteHistoryQuery, Query()],
    service: RouteService = Depends(get_route_service),
) -> list[RouteQuery]:
    filters = HistoryFilter(
        source=query.source,
        destination=query.destination,
        limit=query.limit,
        date_from=query.date_from,
        date_to=query.date_to,
    )
    return service.get_history(filters)
