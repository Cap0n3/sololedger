from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable

from sololedger import IncomeEntry
from sololedger.persistence.repository import LedgerRepository


class EntriesTab(Widget):
    """Displays a table of all financial entries."""

    def __init__(self, repository: LedgerRepository) -> None:
        super().__init__()
        self.repository = repository

    def compose(self) -> ComposeResult:
        yield DataTable(id="entries-table")

    def on_mount(self) -> None:
        table = self.query_one("#entries-table", DataTable)
        table.add_columns("Date", "Type", "Amount", "Activity", "Client", "Description")
        self.refresh_entries()

    def refresh_entries(self) -> None:
        table = self.query_one("#entries-table", DataTable)
        table.clear()
        ledger = self.repository.load_ledger()
        for entry in ledger.get_entries():
            entry_type = "Income" if isinstance(entry, IncomeEntry) else "Expense"
            client_name = entry.client.full_name if entry.client else ""
            table.add_row(
                str(entry.date),
                entry_type,
                f"{entry.amount:.2f}",
                entry.activity.name,
                client_name,
                entry.description or "",
            )
