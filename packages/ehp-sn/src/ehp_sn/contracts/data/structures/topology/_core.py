import abc

ROLE = "topology"


class Topology(abc.ABC):
    pass


__all__ = ["ROLE", "Topology"]
