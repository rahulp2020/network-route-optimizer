from pydantic import BaseModel, model_validator

from app.schemas.common import Latency, NodeName


class EdgeCreate(BaseModel):
    source: NodeName
    destination: NodeName
    latency: Latency

    @model_validator(mode="after")
    def reject_self_loop(self) -> "EdgeCreate":
        if self.source == self.destination:
            raise ValueError("source and destination must be different nodes")
        return self


class EdgeResponse(BaseModel):
    id: int
    source: str
    destination: str
    latency: float
