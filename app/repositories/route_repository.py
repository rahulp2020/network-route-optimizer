from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RouteQuery


@dataclass(frozen=True)
class HistoryFilter:
    source: str | None = None
    destination: str | None = None
    limit: int = 50
    date_from: datetime | None = None
    date_to: datetime | None = None


class RouteQueryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, source: str, destination: str, path: list[str], total_latency: float) -> RouteQuery:
        record = RouteQuery(source=source, destination=destination, path=path, total_latency=total_latency)
        self.db.add(record)
        self.db.commit()
        return record

    def search(self, filters: HistoryFilter) -> list[RouteQuery]:
        statement = select(RouteQuery)
        if filters.source:
            statement = statement.where(RouteQuery.source == filters.source)
        if filters.destination:
            statement = statement.where(RouteQuery.destination == filters.destination)
        if filters.date_from:
            statement = statement.where(RouteQuery.created_at >= filters.date_from.replace(tzinfo=None))
        if filters.date_to:
            statement = statement.where(RouteQuery.created_at <= filters.date_to.replace(tzinfo=None))
        statement = statement.order_by(RouteQuery.created_at.desc(), RouteQuery.id.desc()).limit(filters.limit)
        return list(self.db.scalars(statement).all())
