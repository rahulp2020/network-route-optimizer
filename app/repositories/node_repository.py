from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Node
from app.repositories.exceptions import DuplicateEntityError


class NodeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, node_id: int) -> Node | None:
        return self.db.get(Node, node_id)

    def get_by_name(self, name: str) -> Node | None:
        return self.db.scalar(select(Node).where(Node.name == name))

    def get_many_by_names(self, names: Iterable[str]) -> dict[str, Node]:
        unique_names = list(dict.fromkeys(names))
        if not unique_names:
            return {}
        nodes = self.db.scalars(select(Node).where(Node.name.in_(unique_names))).all()
        return {node.name: node for node in nodes}

    def exists(self, name: str) -> bool:
        return self.db.scalar(select(Node.id).where(Node.name == name)) is not None

    def list_all(self) -> list[Node]:
        return list(self.db.scalars(select(Node).order_by(Node.id)).all())

    def add(self, name: str) -> Node:
        node = Node(name=name)
        self.db.add(node)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateEntityError(f"Node '{name}' already exists") from exc
        return node

    def delete(self, node: Node) -> None:
        self.db.delete(node)
        self.db.commit()
