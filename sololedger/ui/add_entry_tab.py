from datetime import date
from decimal import Decimal, InvalidOperation
from uuid import UUID as UUIDType

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Select, Static

from sololedger import ExpenseEntry, IncomeEntry
from sololedger.persistence.repository import LedgerRepository


class AddEntryTab(Widget):
    """Form for adding new financial entries."""

    def __init__(self, repository: LedgerRepository) -> None:
        super().__init__()
        self.repository = repository

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="add-entry-scroll"):
            with Vertical(classes="form-container"):
                yield Label("Add New Entry", classes="form-title")
                with Horizontal(classes="form-row"):
                    yield Label("Type:")
                    yield Select(
                        [("Income", "income"), ("Expense", "expense")],
                        id="entry-type",
                        value="income",
                    )
                with Horizontal(classes="form-row"):
                    yield Label("Amount:")
                    yield Input(placeholder="0.00", id="entry-amount")
                with Horizontal(classes="form-row"):
                    yield Label("Activity:")
                    yield Select([], id="entry-activity")
                with Horizontal(classes="form-row"):
                    yield Label("Client:")
                    yield Select([], id="entry-client", allow_blank=True)
                with Horizontal(classes="form-row"):
                    yield Label("Description:")
                    yield Input(placeholder="Optional", id="entry-description")
                yield Button("Add Entry", id="add-entry-btn", variant="primary")
                yield Static("", id="entry-message", classes="message")

    def on_mount(self) -> None:
        self.refresh_activity_select()
        self.refresh_client_select()

    def refresh_activity_select(self) -> None:
        select = self.query_one("#entry-activity", Select)
        activities = self.repository.get_all_activities()
        options = [(a.name, str(a.id)) for a in activities]
        select.set_options(options)
        if options:
            select.value = options[0][1]

    def refresh_client_select(self) -> None:
        select = self.query_one("#entry-client", Select)
        clients = self.repository.get_all_clients()
        options = [(c.full_name, str(c.id)) for c in clients]
        select.set_options(options)

    @on(Button.Pressed, "#add-entry-btn")
    def add_entry(self) -> None:
        message = self.query_one("#entry-message", Static)

        entry_type = self.query_one("#entry-type", Select).value
        amount_str = self.query_one("#entry-amount", Input).value
        activity_id = self.query_one("#entry-activity", Select).value
        client_id = self.query_one("#entry-client", Select).value
        description = self.query_one("#entry-description", Input).value or None

        if not amount_str:
            message.update("Please enter an amount")
            message.set_classes("message error")
            return

        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            message.update("Invalid amount")
            message.set_classes("message error")
            return

        if amount <= 0:
            message.update("Amount must be positive")
            message.set_classes("message error")
            return

        if activity_id is None or activity_id == Select.BLANK:
            message.update("Please select an activity")
            message.set_classes("message error")
            return

        activity = self.repository.get_activity(UUIDType(str(activity_id)))
        if not activity:
            message.update("Activity not found")
            message.set_classes("message error")
            return

        client = None
        if client_id is not None and client_id != Select.BLANK:
            client = self.repository.get_client(UUIDType(str(client_id)))

        if entry_type == "income":
            entry = IncomeEntry.create(
                date=date.today(),
                amount=amount,
                activity=activity,
                description=description,
                client=client,
            )
        else:
            entry = ExpenseEntry.create(
                date=date.today(),
                amount=amount,
                activity=activity,
                description=description,
                client=client,
            )

        self.repository.save_entry(entry)

        self.query_one("#entry-amount", Input).value = ""
        self.query_one("#entry-description", Input).value = ""
        message.update("Entry added successfully!")
        message.set_classes("message success")
