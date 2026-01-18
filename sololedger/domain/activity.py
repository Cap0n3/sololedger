from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Activity:
    """Describes a type of work (e.g., Developer, Guitar Teacher)."""

    id: UUID
    name: str

    @classmethod
    def create(cls, name: str) -> "Activity":
        """Factory method to create an Activity with a generated UUID."""
        return cls(id=uuid4(), name=name)
