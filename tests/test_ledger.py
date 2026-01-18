from datetime import date
from decimal import Decimal

import pytest

from sololedger import Activity, ExpenseEntry, IncomeEntry, Ledger, MonthlyPeriod, YearlyPeriod


@pytest.fixture
def developer():
    return Activity.create(name="Developer")


@pytest.fixture
def guitar_teacher():
    return Activity.create(name="Guitar Teacher")


@pytest.fixture
def empty_ledger():
    return Ledger()


@pytest.fixture
def populated_ledger(developer, guitar_teacher):
    ledger = Ledger()

    # Developer income - March 2024
    ledger.add_entry(
        IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer,
            description="Project A",
        )
    )

    # Developer expense - March 2024
    ledger.add_entry(
        ExpenseEntry.create(
            date=date(2024, 3, 20),
            amount=Decimal("50.00"),
            activity=developer,
            description="Software license",
        )
    )

    # Guitar Teacher income - March 2024
    ledger.add_entry(
        IncomeEntry.create(
            date=date(2024, 3, 10),
            amount=Decimal("200.00"),
            activity=guitar_teacher,
            description="Lessons",
        )
    )

    # Developer income - April 2024
    ledger.add_entry(
        IncomeEntry.create(
            date=date(2024, 4, 5),
            amount=Decimal("1500.00"),
            activity=developer,
            description="Project B",
        )
    )

    # Developer income - March 2023 (different year)
    ledger.add_entry(
        IncomeEntry.create(
            date=date(2023, 3, 15),
            amount=Decimal("800.00"),
            activity=developer,
            description="Old project",
        )
    )

    return ledger


class TestLedgerAddEntry:
    def test_add_single_entry(self, empty_ledger, developer):
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer,
        )

        empty_ledger.add_entry(entry)

        assert len(empty_ledger.get_entries()) == 1
        assert empty_ledger.get_entries()[0] == entry

    def test_add_multiple_entries(self, empty_ledger, developer):
        entry1 = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer,
        )
        entry2 = ExpenseEntry.create(
            date=date(2024, 3, 20),
            amount=Decimal("50.00"),
            activity=developer,
        )

        empty_ledger.add_entry(entry1)
        empty_ledger.add_entry(entry2)

        assert len(empty_ledger.get_entries()) == 2


class TestLedgerGetEntries:
    def test_empty_ledger_returns_empty_list(self, empty_ledger):
        assert empty_ledger.get_entries() == []

    def test_returns_copy_of_entries(self, empty_ledger, developer):
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer,
        )
        empty_ledger.add_entry(entry)

        entries = empty_ledger.get_entries()
        entries.clear()

        assert len(empty_ledger.get_entries()) == 1


class TestLedgerGetEntriesForPeriod:
    def test_filter_by_monthly_period(self, populated_ledger):
        march_2024 = MonthlyPeriod(year=2024, month=3)

        entries = populated_ledger.get_entries_for_period(march_2024)

        assert len(entries) == 3
        for entry in entries:
            assert entry.date.year == 2024
            assert entry.date.month == 3

    def test_filter_by_yearly_period(self, populated_ledger):
        year_2024 = YearlyPeriod(year=2024)

        entries = populated_ledger.get_entries_for_period(year_2024)

        assert len(entries) == 4
        for entry in entries:
            assert entry.date.year == 2024

    def test_no_entries_for_period(self, populated_ledger):
        january_2024 = MonthlyPeriod(year=2024, month=1)

        entries = populated_ledger.get_entries_for_period(january_2024)

        assert entries == []


class TestLedgerGetEntriesForActivity:
    def test_filter_by_activity(self, populated_ledger, developer):
        entries = populated_ledger.get_entries_for_activity(developer)

        assert len(entries) == 4
        for entry in entries:
            assert entry.activity == developer

    def test_filter_by_different_activity(self, populated_ledger, guitar_teacher):
        entries = populated_ledger.get_entries_for_activity(guitar_teacher)

        assert len(entries) == 1
        assert entries[0].activity == guitar_teacher

    def test_no_entries_for_activity(self, populated_ledger):
        unknown_activity = Activity.create(name="Unknown")

        entries = populated_ledger.get_entries_for_activity(unknown_activity)

        assert entries == []
