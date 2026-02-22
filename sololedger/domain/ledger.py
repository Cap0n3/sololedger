from sololedger.domain.activity import Activity
from sololedger.domain.client import Client
from sololedger.domain.financial_entry import FinancialEntry
from sololedger.domain.period import Period


class Ledger:
    """Collection of financial entries.

    Stores and retrieves entries. Does not perform calculations (SRP).
    """

    def __init__(self) -> None:
        self._entries: list[FinancialEntry] = []

    def add_entry(self, entry: FinancialEntry) -> None:
        """Add a financial entry to the ledger."""
        self._entries.append(entry)

    def get_entries(self) -> list[FinancialEntry]:
        """Return all entries in the ledger."""
        return list(self._entries)

    def get_entries_for_period(self, period: Period) -> list[FinancialEntry]:
        """Return entries that fall within the given period."""
        return [entry for entry in self._entries if period.contains(entry.date)]

    def get_entries_for_activity(self, activity: Activity) -> list[FinancialEntry]:
        """Return entries for the given activity."""
        return [entry for entry in self._entries if entry.activity == activity]

    def get_entries_for_client(self, client: Client) -> list[FinancialEntry]:
        """Return entries for the given client."""
        return [entry for entry in self._entries if entry.client == client]
