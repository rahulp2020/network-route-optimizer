from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.common import NodeName, to_utc
from app.settings import get_settings

_settings = get_settings()


class ShortestRouteRequest(BaseModel):
    source: NodeName
    destination: NodeName


class ShortestRouteResponse(BaseModel):
    total_latency: float
    path: list[str]


class RouteHistoryQuery(BaseModel):
    source: NodeName | None = None
    destination: NodeName | None = None
    limit: int = Field(default=_settings.history_default_limit, ge=1, le=_settings.history_max_limit)
    date_from: datetime | None = None
    date_to: datetime | None = None

    @field_validator("date_from", "date_to")
    @classmethod
    def normalize_to_utc(cls, value: datetime | None) -> datetime | None:
        return to_utc(value) if value is not None else None

    @model_validator(mode="after")
    def check_date_range(self) -> "RouteHistoryQuery":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be earlier than or equal to date_to")
        return self


class RouteHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    destination: str
    total_latency: float
    path: list[str]
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def ensure_utc(cls, value: datetime) -> datetime:
        return to_utc(value)
