from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Header, TabbedContent, TabPane

from sololedger import SQLiteLedgerRepository
from sololedger.ui.activities_tab import ActivitiesTab
from sololedger.ui.add_entry_tab import AddEntryTab
from sololedger.ui.clients_tab import ClientsTab
from sololedger.ui.entries_tab import EntriesTab
from sololedger.ui.report_tab import ReportTab

DEFAULT_DB_PATH = Path.home() / ".sololedger.db"


class SoloLedgerApp(App):
    """A simple ledger application."""

    CSS_PATH = "sololedger.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        super().__init__()
        self.db_path = db_path
        self.repository = SQLiteLedgerRepository(db_path)

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            with TabbedContent():
                with TabPane("Entries", id="entries-tab"):
                    yield EntriesTab(self.repository)
                with TabPane("Add Entry", id="add-entry-tab"):
                    yield AddEntryTab(self.repository)
                with TabPane("Activities", id="activities-tab"):
                    yield ActivitiesTab(self.repository)
                with TabPane("Clients", id="clients-tab"):
                    yield ClientsTab(self.repository)
                with TabPane("Report", id="report-tab"):
                    yield ReportTab(self.repository)
        yield Footer()

    def on_activities_tab_activity_added(self) -> None:
        self.query_one(AddEntryTab).refresh_activity_select()

    def on_clients_tab_client_added(self) -> None:
        self.query_one(AddEntryTab).refresh_client_select()

    def action_refresh(self) -> None:
        self.query_one(EntriesTab).refresh_entries()
        self.query_one(ActivitiesTab).refresh_activities()
        self.query_one(ClientsTab).refresh_clients()
        self.query_one(AddEntryTab).refresh_activity_select()
        self.query_one(AddEntryTab).refresh_client_select()

    def action_quit(self) -> None:
        self.repository.close()
        self.exit()


def main():
    app = SoloLedgerApp()
    app.run()


if __name__ == "__main__":
    main()
