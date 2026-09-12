import abc
import dataclasses

ROLE = "domains"


class AmbientDomainError(ValueError):
    pass


@dataclasses.dataclass(frozen=True)
class Domain(abc.ABC):
    """Abstract base class for ambient-domain declarations."""

    height: int
    width: int

    @property
    @abc.abstractmethod
    def position_count(self) -> int:
        """Number of canonical positions in the domain."""


__all__ = ["AmbientDomainError", "Domain", "ROLE"]
