from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Label, Static

from sololedger import Client
from sololedger.persistence.repository import LedgerRepository


class ClientsTab(Widget):
    """Manages clients: displays list and provides form to add new ones."""

    class ClientAdded(Message):
        """Posted when a new client is saved."""

    def __init__(self, repository: LedgerRepository) -> None:
        super().__init__()
        self.repository = repository

    def compose(self) -> ComposeResult:
        with ScrollableContainer():
            with Vertical(classes="form-container"):
                yield Label("Add New Client")
                with Horizontal(classes="form-row"):
                    yield Label("First Name:")
                    yield Input(placeholder="First name", id="client-first-name")
                with Horizontal(classes="form-row"):
                    yield Label("Last Name:")
                    yield Input(placeholder="Last name", id="client-last-name")
                with Horizontal(classes="form-row"):
                    yield Label("Email:")
                    yield Input(placeholder="Email", id="client-email")
                with Horizontal(classes="form-row"):
                    yield Label("Phone:")
                    yield Input(placeholder="Optional", id="client-phone")
                with Horizontal(classes="form-row"):
                    yield Label("Description:")
                    yield Input(placeholder="Optional", id="client-description")
                yield Button("Add Client", id="add-client-btn", variant="primary")
                yield Static("", id="client-message", classes="message")
            yield DataTable(id="clients-table")

    def on_mount(self) -> None:
        table = self.query_one("#clients-table", DataTable)
        table.add_columns("Name", "Email", "Phone", "Description")
        self.refresh_clients()

    def refresh_clients(self) -> None:
        table = self.query_one("#clients-table", DataTable)
        table.clear()
        for client in self.repository.get_all_clients():
            table.add_row(
                client.full_name,
                client.email,
                client.phone or "",
                client.description or "",
            )

    @on(Button.Pressed, "#add-client-btn")
    def add_client(self) -> None:
        message = self.query_one("#client-message", Static)
        first_name = self.query_one("#client-first-name", Input).value.strip()
        last_name = self.query_one("#client-last-name", Input).value.strip()
        email = self.query_one("#client-email", Input).value.strip()
        phone = self.query_one("#client-phone", Input).value.strip() or None
        description = self.query_one("#client-description", Input).value.strip() or None

        if not first_name:
            message.update("Please enter a first name")
            message.set_classes("message error")
            return

        if not last_name:
            message.update("Please enter a last name")
            message.set_classes("message error")
            return

        if not email:
            message.update("Please enter an email")
            message.set_classes("message error")
            return

        client = Client.create(first_name, last_name, email, phone, description)
        self.repository.save_client(client)

        self.query_one("#client-first-name", Input).value = ""
        self.query_one("#client-last-name", Input).value = ""
        self.query_one("#client-email", Input).value = ""
        self.query_one("#client-phone", Input).value = ""
        self.query_one("#client-description", Input).value = ""
        message.update(f"Client '{first_name} {last_name}' added!")
        message.set_classes("message success")
        self.refresh_clients()
        self.post_message(self.ClientAdded())
