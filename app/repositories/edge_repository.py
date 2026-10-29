
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Edge, Node
from app.repositories.exceptions import DuplicateEntityError


class EdgeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, edge_id: int) -> Edge | None:
        return self.db.get(Edge, edge_id)

    def exists_between(self, source_id: int, destination_id: int) -> bool:
        return (
            self.db.scalar(
                select(Edge.id).where(
                    Edge.source_id == source_id,
                    Edge.destination_id == destination_id,
                )
            )
            is not None
        )

    def list_all(self) -> list[Edge]:
        statement = (
            select(Edge)
            .options(joinedload(Edge.source), joinedload(Edge.destination))
            .order_by(Edge.id)
        )
        return list(self.db.scalars(statement).all())

    def add(self, source: Node, destination: Node, latency: float) -> Edge:
        edge = Edge(source=source, destination=destination, latency=latency)
        self.db.add(edge)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateEntityError(
                f"Edge from {source.name} to {destination.name} already exists"
            ) from exc
        return edge

    def delete(self, edge: Edge) -> None:
        self.db.delete(edge)
        self.db.commit()
