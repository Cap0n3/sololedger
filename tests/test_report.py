from decimal import Decimal

import pytest

from sololedger import Activity, ActivityTotals, MonthlyPeriod, Report


@pytest.fixture
def developer():
    return Activity.create(name="Developer")


@pytest.fixture
def guitar_teacher():
    return Activity.create(name="Guitar Teacher")


class TestActivityTotals:
    def test_create_activity_totals(self):
        totals = ActivityTotals(
            income=Decimal("1000.00"),
            expense=Decimal("200.00"),
        )

        assert totals.income == Decimal("1000.00")
        assert totals.expense == Decimal("200.00")

    def test_net_is_income_minus_expense(self):
        totals = ActivityTotals(
            income=Decimal("1000.00"),
            expense=Decimal("200.00"),
        )

        assert totals.net == Decimal("800.00")

    def test_net_can_be_negative(self):
        totals = ActivityTotals(
            income=Decimal("100.00"),
            expense=Decimal("500.00"),
        )

        assert totals.net == Decimal("-400.00")

    def test_is_immutable(self):
        totals = ActivityTotals(
            income=Decimal("1000.00"),
            expense=Decimal("200.00"),
        )

        with pytest.raises(AttributeError):
            totals.income = Decimal("2000.00")


class TestReport:
    def test_create_report(self, developer, guitar_teacher):
        period = MonthlyPeriod(year=2024, month=3)
        totals_by_activity = {
            developer: ActivityTotals(
                income=Decimal("1000.00"),
                expense=Decimal("50.00"),
            ),
            guitar_teacher: ActivityTotals(
                income=Decimal("200.00"),
                expense=Decimal("0.00"),
            ),
        }

        report = Report(
            period=period,
            income_total=Decimal("1200.00"),
            expense_total=Decimal("50.00"),
            totals_by_activity=totals_by_activity,
        )

        assert report.period == period
        assert report.income_total == Decimal("1200.00")
        assert report.expense_total == Decimal("50.00")
        assert len(report.totals_by_activity) == 2

    def test_net_total_is_income_minus_expense(self, developer):
        period = MonthlyPeriod(year=2024, month=3)

        report = Report(
            period=period,
            income_total=Decimal("1000.00"),
            expense_total=Decimal("300.00"),
            totals_by_activity={},
        )

        assert report.net_total == Decimal("700.00")

    def test_net_total_can_be_negative(self, developer):
        period = MonthlyPeriod(year=2024, month=3)

        report = Report(
            period=period,
            income_total=Decimal("100.00"),
            expense_total=Decimal("500.00"),
            totals_by_activity={},
        )

        assert report.net_total == Decimal("-400.00")

    def test_empty_report(self):
        period = MonthlyPeriod(year=2024, month=3)

        report = Report(
            period=period,
            income_total=Decimal("0.00"),
            expense_total=Decimal("0.00"),
            totals_by_activity={},
        )

        assert report.income_total == Decimal("0.00")
        assert report.expense_total == Decimal("0.00")
        assert report.net_total == Decimal("0.00")
        assert report.totals_by_activity == {}
