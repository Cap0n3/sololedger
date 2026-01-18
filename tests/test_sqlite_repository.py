import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from sololedger import Activity, ExpenseEntry, IncomeEntry, Ledger, SQLiteLedgerRepository


@pytest.fixture
def db_path():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield Path(f.name)


@pytest.fixture
def repository(db_path):
    """Create a repository with a temporary database."""
    repo = SQLiteLedgerRepository(db_path)
    yield repo
    repo.close()


@pytest.fixture
def developer():
    return Activity.create(name="Developer")


@pytest.fixture
def guitar_teacher():
    return Activity.create(name="Guitar Teacher")


class TestActivityPersistence:
    def test_save_and_get_activity(self, repository, developer):
        repository.save_activity(developer)

        loaded = repository.get_activity(developer.id)

        assert loaded is not None
        assert loaded.id == developer.id
        assert loaded.name == developer.name

    def test_get_nonexistent_activity_returns_none(self, repository, developer):
        result = repository.get_activity(developer.id)

        assert result is None

    def test_get_all_activities_empty(self, repository):
        activities = repository.get_all_activities()

        assert activities == []

    def test_get_all_activities(self, repository, developer, guitar_teacher):
        repository.save_activity(developer)
        repository.save_activity(guitar_teacher)

        activities = repository.get_all_activities()

        assert len(activities) == 2
        activity_ids = {a.id for a in activities}
        assert developer.id in activity_ids
        assert guitar_teacher.id in activity_ids

    def test_save_activity_is_idempotent(self, repository, developer):
        repository.save_activity(developer)
        repository.save_activity(developer)

        activities = repository.get_all_activities()

        assert len(activities) == 1


class TestEntryPersistence:
    def test_save_and_load_income_entry(self, repository, developer):
        repository.save_activity(developer)
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.50"),
            activity=developer,
            description="Project payment",
        )

        repository.save_entry(entry)
        loaded_entries = repository.get_all_entries()

        assert len(loaded_entries) == 1
        loaded = loaded_entries[0]
        assert isinstance(loaded, IncomeEntry)
        assert loaded.id == entry.id
        assert loaded.date == entry.date
        assert loaded.amount == entry.amount
        assert loaded.activity.id == developer.id
        assert loaded.description == entry.description

    def test_save_and_load_expense_entry(self, repository, developer):
        repository.save_activity(developer)
        entry = ExpenseEntry.create(
            date=date(2024, 3, 20),
            amount=Decimal("50.00"),
            activity=developer,
            description="Software license",
        )

        repository.save_entry(entry)
        loaded_entries = repository.get_all_entries()

        assert len(loaded_entries) == 1
        loaded = loaded_entries[0]
        assert isinstance(loaded, ExpenseEntry)
        assert loaded.id == entry.id
        assert loaded.date == entry.date
        assert loaded.amount == entry.amount

    def test_save_entry_without_description(self, repository, developer):
        repository.save_activity(developer)
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer,
        )

        repository.save_entry(entry)
        loaded_entries = repository.get_all_entries()

        assert len(loaded_entries) == 1
        assert loaded_entries[0].description is None

    def test_decimal_precision_preserved(self, repository, developer):
        repository.save_activity(developer)
        precise_amount = Decimal("1234.56789")
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=precise_amount,
            activity=developer,
        )

        repository.save_entry(entry)
        loaded_entries = repository.get_all_entries()

        assert loaded_entries[0].amount == precise_amount


class TestLedgerPersistence:
    def test_save_and_load_empty_ledger(self, repository):
        ledger = Ledger()

        repository.save_ledger(ledger)
        loaded = repository.load_ledger()

        assert loaded.get_entries() == []

    def test_save_and_load_ledger_with_entries(self, repository, developer, guitar_teacher):
        ledger = Ledger()
        income = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer,
            description="Project A",
        )
        expense = ExpenseEntry.create(
            date=date(2024, 3, 20),
            amount=Decimal("50.00"),
            activity=developer,
            description="License",
        )
        guitar_income = IncomeEntry.create(
            date=date(2024, 3, 10),
            amount=Decimal("200.00"),
            activity=guitar_teacher,
            description="Lessons",
        )
        ledger.add_entry(income)
        ledger.add_entry(expense)
        ledger.add_entry(guitar_income)

        repository.save_ledger(ledger)
        loaded = repository.load_ledger()

        loaded_entries = loaded.get_entries()
        assert len(loaded_entries) == 3

        entry_ids = {e.id for e in loaded_entries}
        assert income.id in entry_ids
        assert expense.id in entry_ids
        assert guitar_income.id in entry_ids

    def test_ledger_roundtrip_preserves_entry_types(self, repository, developer):
        ledger = Ledger()
        income = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer,
        )
        expense = ExpenseEntry.create(
            date=date(2024, 3, 20),
            amount=Decimal("50.00"),
            activity=developer,
        )
        ledger.add_entry(income)
        ledger.add_entry(expense)

        repository.save_ledger(ledger)
        loaded = repository.load_ledger()

        loaded_entries = loaded.get_entries()
        income_entries = [e for e in loaded_entries if isinstance(e, IncomeEntry)]
        expense_entries = [e for e in loaded_entries if isinstance(e, ExpenseEntry)]
        assert len(income_entries) == 1
        assert len(expense_entries) == 1


class TestPersistenceAcrossInstances:
    def test_data_persists_across_repository_instances(self, db_path, developer):
        repo1 = SQLiteLedgerRepository(db_path)
        repo1.save_activity(developer)
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer,
            description="Test",
        )
        repo1.save_entry(entry)
        repo1.close()

        repo2 = SQLiteLedgerRepository(db_path)
        loaded_activities = repo2.get_all_activities()
        loaded_entries = repo2.get_all_entries()
        repo2.close()

        assert len(loaded_activities) == 1
        assert loaded_activities[0].id == developer.id
        assert len(loaded_entries) == 1
        assert loaded_entries[0].id == entry.id

    def test_ledger_persists_across_instances(self, db_path, developer, guitar_teacher):
        ledger = Ledger()
        ledger.add_entry(
            IncomeEntry.create(
                date=date(2024, 3, 15),
                amount=Decimal("1000.00"),
                activity=developer,
            )
        )
        ledger.add_entry(
            ExpenseEntry.create(
                date=date(2024, 3, 20),
                amount=Decimal("200.00"),
                activity=guitar_teacher,
            )
        )

        repo1 = SQLiteLedgerRepository(db_path)
        repo1.save_ledger(ledger)
        repo1.close()

        repo2 = SQLiteLedgerRepository(db_path)
        loaded = repo2.load_ledger()
        repo2.close()

        assert len(loaded.get_entries()) == 2


class TestRepositoryWithPathTypes:
    def test_accepts_string_path(self, db_path):
        repo = SQLiteLedgerRepository(str(db_path))
        activity = Activity.create("Test")
        repo.save_activity(activity)
        repo.close()

        assert True

    def test_accepts_path_object(self, db_path):
        repo = SQLiteLedgerRepository(db_path)
        activity = Activity.create("Test")
        repo.save_activity(activity)
        repo.close()

        assert True
