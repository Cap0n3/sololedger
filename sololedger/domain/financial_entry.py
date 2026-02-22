from abc import ABC
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sololedger.domain.activity import Activity
from sololedger.domain.client import Client


@dataclass(frozen=True)
class FinancialEntry(ABC):
    """Abstract base class for financial events.

    Represents a single money event (income or expense) at a point in time.
    Amount is always positive; the type (IncomeEntry/ExpenseEntry) determines meaning.
    """

    id: UUID
    date: date
    amount: Decimal
    activity: Activity
    description: str | None = None
    client: Client | None = None

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError(f"Amount must be positive, got {self.amount}")


@dataclass(frozen=True)
class IncomeEntry(FinancialEntry):
    """Represents money coming in."""

    pass

    @classmethod
    def create(
        cls,
        date: date,
        amount: Decimal,
        activity: Activity,
        description: str | None = None,
        client: Client | None = None,
    ) -> "IncomeEntry":
        """Factory method to create an IncomeEntry with a generated UUID."""
        return cls(
            id=uuid4(),
            date=date,
            amount=amount,
            activity=activity,
            description=description,
            client=client,
        )


@dataclass(frozen=True)
class ExpenseEntry(FinancialEntry):
    """Represents money going out."""

    pass

    @classmethod
    def create(
        cls,
        date: date,
        amount: Decimal,
        activity: Activity,
        description: str | None = None,
        client: Client | None = None,
    ) -> "ExpenseEntry":
        """Factory method to create an ExpenseEntry with a generated UUID."""
        return cls(
            id=uuid4(),
            date=date,
            amount=amount,
            activity=activity,
            description=description,
            client=client,
        )
