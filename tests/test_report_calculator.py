from datetime import date
from decimal import Decimal

import pytest

from sololedger import (
    Activity,
    ExpenseEntry,
    IncomeEntry,
    Ledger,
    MonthlyPeriod,
    ReportCalculator,
    YearlyPeriod,
)


@pytest.fixture
def developer():
    return Activity.create(name="Developer")


@pytest.fixture
def guitar_teacher():
    return Activity.create(name="Guitar Teacher")


@pytest.fixture
def calculator():
    return ReportCalculator()


@pytest.fixture
def populated_ledger(developer, guitar_teacher):
    ledger = Ledger()

    # Developer income - March 2024
    ledger.add_entry(
        IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer,
        )
    )
    ledger.add_entry(
        IncomeEntry.create(
            date=date(2024, 3, 25),
            amount=Decimal("500.00"),
            activity=developer,
        )
    )

    # Developer expense - March 2024
    ledger.add_entry(
        ExpenseEntry.create(
            date=date(2024, 3, 20),
            amount=Decimal("50.00"),
            activity=developer,
        )
    )

    # Guitar Teacher income - March 2024
    ledger.add_entry(
        IncomeEntry.create(
            date=date(2024, 3, 10),
            amount=Decimal("200.00"),
            activity=guitar_teacher,
        )
    )

    # Guitar Teacher expense - March 2024
    ledger.add_entry(
        ExpenseEntry.create(
            date=date(2024, 3, 12),
            amount=Decimal("30.00"),
            activity=guitar_teacher,
        )
    )

    # Developer income - April 2024
    ledger.add_entry(
        IncomeEntry.create(
            date=date(2024, 4, 5),
            amount=Decimal("1500.00"),
            activity=developer,
        )
    )

    return ledger


class TestReportCalculatorTotals:
    def test_calculate_income_total(self, calculator, populated_ledger):
        march_2024 = MonthlyPeriod(year=2024, month=3)

        report = calculator.calculate(populated_ledger, march_2024)

        # Developer: 1000 + 500, Guitar Teacher: 200
        assert report.income_total == Decimal("1700.00")

    def test_calculate_expense_total(self, calculator, populated_ledger):
        march_2024 = MonthlyPeriod(year=2024, month=3)

        report = calculator.calculate(populated_ledger, march_2024)

        # Developer: 50, Guitar Teacher: 30
        assert report.expense_total == Decimal("80.00")

    def test_calculate_net_total(self, calculator, populated_ledger):
        march_2024 = MonthlyPeriod(year=2024, month=3)

        report = calculator.calculate(populated_ledger, march_2024)

        # 1700 - 80 = 1620
        assert report.net_total == Decimal("1620.00")

    def test_report_has_correct_period(self, calculator, populated_ledger):
        march_2024 = MonthlyPeriod(year=2024, month=3)

        report = calculator.calculate(populated_ledger, march_2024)

        assert report.period == march_2024


class TestReportCalculatorByActivity:
    def test_totals_by_activity(self, calculator, populated_ledger, developer, guitar_teacher):
        march_2024 = MonthlyPeriod(year=2024, month=3)

        report = calculator.calculate(populated_ledger, march_2024)

        assert developer in report.totals_by_activity
        assert guitar_teacher in report.totals_by_activity

        dev_totals = report.totals_by_activity[developer]
        assert dev_totals.income == Decimal("1500.00")
        assert dev_totals.expense == Decimal("50.00")
        assert dev_totals.net == Decimal("1450.00")

        guitar_totals = report.totals_by_activity[guitar_teacher]
        assert guitar_totals.income == Decimal("200.00")
        assert guitar_totals.expense == Decimal("30.00")
        assert guitar_totals.net == Decimal("170.00")

    def test_activity_with_only_income(self, calculator, developer):
        ledger = Ledger()
        ledger.add_entry(
            IncomeEntry.create(
                date=date(2024, 3, 15),
                amount=Decimal("1000.00"),
                activity=developer,
            )
        )
        march_2024 = MonthlyPeriod(year=2024, month=3)

        report = calculator.calculate(ledger, march_2024)

        dev_totals = report.totals_by_activity[developer]
        assert dev_totals.income == Decimal("1000.00")
        assert dev_totals.expense == Decimal("0.00")

    def test_activity_with_only_expense(self, calculator, developer):
        ledger = Ledger()
        ledger.add_entry(
            ExpenseEntry.create(
                date=date(2024, 3, 15),
                amount=Decimal("100.00"),
                activity=developer,
            )
        )
        march_2024 = MonthlyPeriod(year=2024, month=3)

        report = calculator.calculate(ledger, march_2024)

        dev_totals = report.totals_by_activity[developer]
        assert dev_totals.income == Decimal("0.00")
        assert dev_totals.expense == Decimal("100.00")


class TestReportCalculatorPeriodFiltering:
    def test_yearly_period(self, calculator, populated_ledger):
        year_2024 = YearlyPeriod(year=2024)

        report = calculator.calculate(populated_ledger, year_2024)

        # March: 1000 + 500 + 200 = 1700, April: 1500
        assert report.income_total == Decimal("3200.00")
        # March: 50 + 30 = 80
        assert report.expense_total == Decimal("80.00")

    def test_different_month(self, calculator, populated_ledger):
        april_2024 = MonthlyPeriod(year=2024, month=4)

        report = calculator.calculate(populated_ledger, april_2024)

        assert report.income_total == Decimal("1500.00")
        assert report.expense_total == Decimal("0.00")

    def test_period_with_no_entries(self, calculator, populated_ledger):
        january_2024 = MonthlyPeriod(year=2024, month=1)

        report = calculator.calculate(populated_ledger, january_2024)

        assert report.income_total == Decimal("0.00")
        assert report.expense_total == Decimal("0.00")
        assert report.net_total == Decimal("0.00")
        assert report.totals_by_activity == {}


class TestReportCalculatorEmptyLedger:
    def test_empty_ledger(self, calculator):
        ledger = Ledger()
        march_2024 = MonthlyPeriod(year=2024, month=3)

        report = calculator.calculate(ledger, march_2024)

        assert report.income_total == Decimal("0.00")
        assert report.expense_total == Decimal("0.00")
        assert report.net_total == Decimal("0.00")
        assert report.totals_by_activity == {}
