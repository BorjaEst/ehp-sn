import abc

ROLE = "relations"


class Relation(abc.ABC):
    pass


__all__ = ["ROLE", "Relation"]
