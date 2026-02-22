from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Client:
    """Represents a client that can be associated with financial entries."""

    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    description: str | None = None

    @property
    def full_name(self) -> str:
        """Return the client's full name."""
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: str,
        phone: str | None = None,
        description: str | None = None,
    ) -> "Client":
        """Factory method to create a Client with a generated UUID."""
        return cls(
            id=uuid4(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            description=description,
        )
