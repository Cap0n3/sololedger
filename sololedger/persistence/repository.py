from abc import ABC, abstractmethod
from uuid import UUID

from sololedger.domain.activity import Activity
from sololedger.domain.financial_entry import FinancialEntry
from sololedger.domain.ledger import Ledger


class LedgerRepository(ABC):
    """Abstract interface for ledger persistence."""

    @abstractmethod
    def save_activity(self, activity: Activity) -> None:
        """Persist an activity."""
        pass

    @abstractmethod
    def get_activity(self, id: UUID) -> Activity | None:
        """Retrieve an activity by ID. Returns None if not found."""
        pass

    @abstractmethod
    def get_all_activities(self) -> list[Activity]:
        """Retrieve all persisted activities."""
        pass

    @abstractmethod
    def save_entry(self, entry: FinancialEntry) -> None:
        """Persist a financial entry."""
        pass

    @abstractmethod
    def get_all_entries(self) -> list[FinancialEntry]:
        """Retrieve all persisted entries."""
        pass

    @abstractmethod
    def save_ledger(self, ledger: Ledger) -> None:
        """Persist all entries from a ledger."""
        pass

    @abstractmethod
    def load_ledger(self) -> Ledger:
        """Load a ledger with all persisted entries."""
        pass
