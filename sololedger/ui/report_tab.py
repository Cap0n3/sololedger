from datetime import date

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widget import Widget
from textual.widgets import Button, DataTable, Label, Select, Static

from sololedger import MonthlyPeriod, ReportCalculator, YearlyPeriod
from sololedger.persistence.repository import LedgerRepository


class ReportTab(Widget):
    """Generates and displays financial reports for a given period."""

    def __init__(self, repository: LedgerRepository) -> None:
        super().__init__()
        self.repository = repository

    def compose(self) -> ComposeResult:
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
        table = self.query_one("#report-table", DataTable)
        table.add_columns("Activity", "Income", "Expense", "Net")

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

        ledger = self.repository.load_ledger()
        calculator = ReportCalculator()
        report = calculator.calculate(ledger, period)

        entry_count = len(ledger.get_entries())
        period_entries = len(ledger.get_entries_for_period(period))

        summary = (
            f"Report for {period_label}\n"
            f"({period_entries} entries in period, {entry_count} total)\n\n"
            f"  Income:  {report.income_total:>10.2f}\n"
            f"  Expense: {report.expense_total:>10.2f}\n"
            f"  Net:     {report.net_total:>10.2f}"
        )
        content.update(summary)

        table = self.query_one("#report-table", DataTable)
        table.clear()
        for activity, totals in report.totals_by_activity.items():
            table.add_row(
                activity.name,
                f"{totals.income:.2f}",
                f"{totals.expense:.2f}",
                f"{totals.net:.2f}",
            )
