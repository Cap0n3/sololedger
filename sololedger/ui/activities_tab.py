from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Label, Static

from sololedger import Activity
from sololedger.persistence.repository import LedgerRepository


class ActivitiesTab(Widget):
    """Manages activities: displays list and provides form to add new ones."""

    class ActivityAdded(Message):
        """Posted when a new activity is saved."""

    def __init__(self, repository: LedgerRepository) -> None:
        super().__init__()
        self.repository = repository

    def compose(self) -> ComposeResult:
        with ScrollableContainer():
            with Vertical(classes="form-container"):
                yield Label("Add New Activity")
                with Horizontal(classes="form-row"):
                    yield Label("Name:")
                    yield Input(placeholder="Activity name", id="activity-name")
                yield Button("Add Activity", id="add-activity-btn", variant="primary")
                yield Static("", id="activity-message", classes="message")
            yield DataTable(id="activities-table")

    def on_mount(self) -> None:
        table = self.query_one("#activities-table", DataTable)
        table.add_columns("Name")
        self.refresh_activities()

    def refresh_activities(self) -> None:
        table = self.query_one("#activities-table", DataTable)
        table.clear()
        for activity in self.repository.get_all_activities():
            table.add_row(activity.name)

    @on(Button.Pressed, "#add-activity-btn")
    def add_activity(self) -> None:
        message = self.query_one("#activity-message", Static)
        name = self.query_one("#activity-name", Input).value.strip()

        if not name:
            message.update("Please enter an activity name")
            message.set_classes("message error")
            return

        activity = Activity.create(name)
        self.repository.save_activity(activity)

        self.query_one("#activity-name", Input).value = ""
        message.update(f"Activity '{name}' added!")
        message.set_classes("message success")
        self.refresh_activities()
        self.post_message(self.ActivityAdded())
