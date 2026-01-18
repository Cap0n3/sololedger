from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from sololedger import (
    Activity,
    ExpenseEntry,
    IncomeEntry,
    Ledger,
    MonthlyPeriod,
    ReportCalculator,
    SQLiteLedgerRepository,
    YearlyPeriod,
)

DEFAULT_DB_PATH = Path.home() / ".sololedger.db"


class SoloLedgerApp(App):
    """A simple ledger application."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #main-container {
        height: 1fr;
        padding: 1;
    }

    .form-row {
        height: auto;
        margin-bottom: 1;
    }

    .form-row Label {
        width: 15;
    }

    .form-row Input, .form-row Select {
        width: 1fr;
    }

    .form-container {
        height: auto;
        padding: 1;
        border: solid green;
        margin-bottom: 1;
    }

    .message {
        height: 3;
        padding: 1;
    }

    .success {
        color: green;
    }

    .error {
        color: red;
    }

    Button {
        margin-top: 1;
    }

    DataTable {
        height: 1fr;
    }

    .report-summary {
        height: auto;
        padding: 1;
        border: solid cyan;
        margin-bottom: 1;
    }

    .report-total {
        text-style: bold;
    }

    .income {
        color: green;
    }

    .expense {
        color: red;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        super().__init__()
        self.db_path = db_path
        self.repository = SQLiteLedgerRepository(db_path)
        self.ledger = self.repository.load_ledger()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            with TabbedContent():
                with TabPane("Entries", id="entries-tab"):
                    yield DataTable(id="entries-table")
                with TabPane("Add Entry", id="add-entry-tab"):
                    yield from self._compose_add_entry_form()
                with TabPane("Activities", id="activities-tab"):
                    yield from self._compose_activities_tab()
                with TabPane("Report", id="report-tab"):
                    yield from self._compose_report_tab()
        yield Footer()

    def _compose_add_entry_form(self) -> ComposeResult:
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
                yield Label("Description:")
                yield Input(placeholder="Optional", id="entry-description")
            yield Button("Add Entry", id="add-entry-btn", variant="primary")
            yield Static("", id="entry-message", classes="message")

    def _compose_activities_tab(self) -> ComposeResult:
        with Vertical(classes="form-container"):
            yield Label("Add New Activity")
            with Horizontal(classes="form-row"):
                yield Label("Name:")
                yield Input(placeholder="Activity name", id="activity-name")
            yield Button("Add Activity", id="add-activity-btn", variant="primary")
            yield Static("", id="activity-message", classes="message")
        yield DataTable(id="activities-table")

    def _compose_report_tab(self) -> ComposeResult:
        current_year = date.today().year
        current_month = date.today().month
        years = [(str(y), y) for y in range(current_year - 5, current_year + 1)]
        months = [
            ("January", 1), ("February", 2), ("March", 3), ("April", 4),
            ("May", 5), ("June", 6), ("July", 7), ("August", 8),
            ("September", 9), ("October", 10), ("November", 11), ("December", 12),
        ]

        with ScrollableContainer():
            with Vertical(classes="form-container"):
                yield Label("Generate Report")
                with Horizontal(classes="form-row"):
                    yield Label("Period:")
                    yield Select(
                        [("Monthly", "monthly"), ("Yearly", "yearly")],
                        id="report-period-type",
                        value="monthly",
                    )
                with Horizontal(classes="form-row"):
                    yield Label("Year:")
                    yield Select(years, id="report-year", value=current_year)
                with Horizontal(classes="form-row", id="month-row"):
                    yield Label("Month:")
                    yield Select(months, id="report-month", value=current_month)
                yield Button("Generate Report", id="generate-report-btn", variant="primary")

            with Vertical(classes="report-summary", id="report-summary"):
                yield Static("Select a period and generate a report", id="report-content")
            yield DataTable(id="report-table")

    def on_mount(self) -> None:
        self._setup_entries_table()
        self._setup_activities_table()
        self._setup_report_table()
        self._refresh_data()

    def _setup_entries_table(self) -> None:
        table = self.query_one("#entries-table", DataTable)
        table.add_columns("Date", "Type", "Amount", "Activity", "Description")

    def _setup_activities_table(self) -> None:
        table = self.query_one("#activities-table", DataTable)
        table.add_columns("Name")

    def _setup_report_table(self) -> None:
        table = self.query_one("#report-table", DataTable)
        table.add_columns("Activity", "Income", "Expense", "Net")

    def _refresh_data(self) -> None:
        self._refresh_entries_table()
        self._refresh_activities_table()
        self._refresh_activity_select()

    def _refresh_entries_table(self) -> None:
        table = self.query_one("#entries-table", DataTable)
        table.clear()
        for entry in self.ledger.get_entries():
            entry_type = "Income" if isinstance(entry, IncomeEntry) else "Expense"
            table.add_row(
                str(entry.date),
                entry_type,
                f"{entry.amount:.2f}",
                entry.activity.name,
                entry.description or "",
            )

    def _refresh_activities_table(self) -> None:
        table = self.query_one("#activities-table", DataTable)
        table.clear()
        for activity in self.repository.get_all_activities():
            table.add_row(activity.name)

    def _refresh_activity_select(self) -> None:
        select = self.query_one("#entry-activity", Select)
        activities = self.repository.get_all_activities()
        options = [(a.name, str(a.id)) for a in activities]
        select.set_options(options)
        if options:
            select.value = options[0][1]

    @on(Button.Pressed, "#add-entry-btn")
    def add_entry(self) -> None:
        message = self.query_one("#entry-message", Static)

        entry_type = self.query_one("#entry-type", Select).value
        amount_str = self.query_one("#entry-amount", Input).value
        activity_id = self.query_one("#entry-activity", Select).value
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

        activity = self.repository.get_activity(
            __import__("uuid").UUID(str(activity_id))
        )
        if not activity:
            message.update("Activity not found")
            message.set_classes("message error")
            return

        if entry_type == "income":
            entry = IncomeEntry.create(
                date=date.today(),
                amount=amount,
                activity=activity,
                description=description,
            )
        else:
            entry = ExpenseEntry.create(
                date=date.today(),
                amount=amount,
                activity=activity,
                description=description,
            )

        self.ledger.add_entry(entry)
        self.repository.save_entry(entry)

        self.query_one("#entry-amount", Input).value = ""
        self.query_one("#entry-description", Input).value = ""
        message.update("Entry added successfully!")
        message.set_classes("message success")
        self._refresh_entries_table()

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
        self._refresh_activities_table()
        self._refresh_activity_select()

    @on(Button.Pressed, "#generate-report-btn")
    def generate_report(self) -> None:
        content = self.query_one("#report-content", Static)

        period_type = self.query_one("#report-period-type", Select).value
        year = self.query_one("#report-year", Select).value

        if year is None or year == Select.BLANK:
            content.update("Please select a year")
            return

        if period_type == "monthly":
            month = self.query_one("#report-month", Select).value
            if month is None or month == Select.BLANK:
                content.update("Please select a month")
                return
            period = MonthlyPeriod(year=int(year), month=int(month))
            period_label = f"{date(int(year), int(month), 1):%B %Y}"
        else:
            period = YearlyPeriod(year=int(year))
            period_label = str(year)

        calculator = ReportCalculator()
        report = calculator.calculate(self.ledger, period)

        # Build summary with entry count for debugging
        entry_count = len(self.ledger.get_entries())
        period_entries = len(self.ledger.get_entries_for_period(period))

        summary = (
            f"Report for {period_label}\n"
            f"({period_entries} entries in period, {entry_count} total)\n\n"
            f"  Income:  {report.income_total:>10.2f}\n"
            f"  Expense: {report.expense_total:>10.2f}\n"
            f"  Net:     {report.net_total:>10.2f}"
        )
        content.update(summary)

        # Update table
        table = self.query_one("#report-table", DataTable)
        table.clear()
        for activity, totals in report.totals_by_activity.items():
            table.add_row(
                activity.name,
                f"{totals.income:.2f}",
                f"{totals.expense:.2f}",
                f"{totals.net:.2f}",
            )

    def action_refresh(self) -> None:
        self.ledger = self.repository.load_ledger()
        self._refresh_data()

    def action_quit(self) -> None:
        self.repository.close()
        self.exit()


def main():
    app = SoloLedgerApp()
    app.run()


if __name__ == "__main__":
    main()
