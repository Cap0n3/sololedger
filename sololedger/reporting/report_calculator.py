from collections import defaultdict
from decimal import Decimal

from sololedger.domain.activity import Activity
from sololedger.domain.financial_entry import ExpenseEntry, IncomeEntry
from sololedger.domain.ledger import Ledger
from sololedger.domain.period import Period
from sololedger.reporting.report import ActivityTotals, Report


class ReportCalculator:
    """Aggregation service that calculates reports from ledger entries.

    Takes a Ledger and Period, produces a Report.
    Pure calculation - no storage, no UI, no domain mutation.
    """

    def calculate(self, ledger: Ledger, period: Period) -> Report:
        """Calculate totals for the given period."""
        entries = ledger.get_entries_for_period(period)

        income_total = Decimal("0.00")
        expense_total = Decimal("0.00")
        income_by_activity: dict[Activity, Decimal] = defaultdict(lambda: Decimal("0.00"))
        expense_by_activity: dict[Activity, Decimal] = defaultdict(lambda: Decimal("0.00"))

        for entry in entries:
            if isinstance(entry, IncomeEntry):
                income_total += entry.amount
                income_by_activity[entry.activity] += entry.amount
            elif isinstance(entry, ExpenseEntry):
                expense_total += entry.amount
                expense_by_activity[entry.activity] += entry.amount

        # Build totals by activity
        all_activities = set(income_by_activity.keys()) | set(expense_by_activity.keys())
        totals_by_activity = {
            activity: ActivityTotals(
                income=income_by_activity[activity],
                expense=expense_by_activity[activity],
            )
            for activity in all_activities
        }

        return Report(
            period=period,
            income_total=income_total,
            expense_total=expense_total,
            totals_by_activity=totals_by_activity,
        )
