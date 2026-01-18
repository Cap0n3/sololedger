from dataclasses import dataclass
from decimal import Decimal

from sololedger.domain.activity import Activity
from sololedger.domain.period import Period


@dataclass(frozen=True)
class ActivityTotals:
    """Totals for a single activity."""

    income: Decimal
    expense: Decimal

    @property
    def net(self) -> Decimal:
        """Net result (income - expense)."""
        return self.income - self.expense


@dataclass(frozen=True)
class Report:
    """Read-only report containing calculated totals for a period.

    This is a data class holding results, not behavior.
    """

    period: Period
    income_total: Decimal
    expense_total: Decimal
    totals_by_activity: dict[Activity, ActivityTotals]

    @property
    def net_total(self) -> Decimal:
        """Net result (income - expense)."""
        return self.income_total - self.expense_total
