from fastapi import APIRouter, Depends, status

from app.dependencies import get_node_service
from app.models import Node
from app.schemas.node import NodeCreate, NodeResponse
from app.services.node_service import NodeService

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.post("", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(payload: NodeCreate, service: NodeService = Depends(get_node_service)) -> Node:
    return service.create(payload.name)


@router.get("", response_model=list[NodeResponse])
def list_nodes(service: NodeService = Depends(get_node_service)) -> list[Node]:
    return service.list_all()


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(node_id: int, service: NodeService = Depends(get_node_service)) -> None:
    service.delete(node_id)
