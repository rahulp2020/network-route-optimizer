from pydantic import BaseModel, ConfigDict

from app.schemas.common import NodeName


class NodeCreate(BaseModel):
    name: NodeName


class NodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
