from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from sololedger import Activity, Client, ExpenseEntry, FinancialEntry, IncomeEntry


@pytest.fixture
def developer_activity():
    return Activity.create(name="Developer")


@pytest.fixture
def guitar_teacher_activity():
    return Activity.create(name="Guitar Teacher")


@pytest.fixture
def acme_client():
    return Client.create(
        first_name="John",
        last_name="Doe",
        email="john@acme.com",
    )


class TestIncomeEntry:
    def test_create_with_explicit_id(self, developer_activity):
        entry_id = uuid4()
        entry = IncomeEntry(
            id=entry_id,
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer_activity,
            description="Project payment",
        )

        assert entry.id == entry_id
        assert entry.date == date(2024, 3, 15)
        assert entry.amount == Decimal("1000.00")
        assert entry.activity == developer_activity
        assert entry.description == "Project payment"

    def test_create_with_factory(self, developer_activity):
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer_activity,
        )

        assert isinstance(entry.id, UUID)
        assert entry.date == date(2024, 3, 15)
        assert entry.amount == Decimal("1000.00")
        assert entry.description is None

    def test_description_is_optional(self, developer_activity):
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("500.00"),
            activity=developer_activity,
        )

        assert entry.description is None

    def test_is_a_financial_entry(self, developer_activity):
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("500.00"),
            activity=developer_activity,
        )

        assert isinstance(entry, FinancialEntry)

    def test_is_immutable(self, developer_activity):
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("500.00"),
            activity=developer_activity,
        )

        with pytest.raises(AttributeError):
            entry.amount = Decimal("1000.00")


class TestExpenseEntry:
    def test_create_with_explicit_id(self, developer_activity):
        entry_id = uuid4()
        entry = ExpenseEntry(
            id=entry_id,
            date=date(2024, 3, 15),
            amount=Decimal("50.00"),
            activity=developer_activity,
            description="Software license",
        )

        assert entry.id == entry_id
        assert entry.date == date(2024, 3, 15)
        assert entry.amount == Decimal("50.00")
        assert entry.activity == developer_activity
        assert entry.description == "Software license"

    def test_create_with_factory(self, developer_activity):
        entry = ExpenseEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("50.00"),
            activity=developer_activity,
        )

        assert isinstance(entry.id, UUID)
        assert entry.date == date(2024, 3, 15)
        assert entry.amount == Decimal("50.00")

    def test_is_a_financial_entry(self, developer_activity):
        entry = ExpenseEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("50.00"),
            activity=developer_activity,
        )

        assert isinstance(entry, FinancialEntry)

    def test_is_immutable(self, developer_activity):
        entry = ExpenseEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("50.00"),
            activity=developer_activity,
        )

        with pytest.raises(AttributeError):
            entry.amount = Decimal("100.00")


class TestFinancialEntryValidation:
    def test_amount_must_be_positive(self, developer_activity):
        with pytest.raises(ValueError, match="Amount must be positive"):
            IncomeEntry.create(
                date=date(2024, 3, 15),
                amount=Decimal("0"),
                activity=developer_activity,
            )

        with pytest.raises(ValueError, match="Amount must be positive"):
            IncomeEntry.create(
                date=date(2024, 3, 15),
                amount=Decimal("-100.00"),
                activity=developer_activity,
            )

        with pytest.raises(ValueError, match="Amount must be positive"):
            ExpenseEntry.create(
                date=date(2024, 3, 15),
                amount=Decimal("-50.00"),
                activity=developer_activity,
            )


class TestFinancialEntryEquality:
    def test_entries_with_same_id_are_equal(self, developer_activity):
        entry_id = uuid4()
        entry1 = IncomeEntry(
            id=entry_id,
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer_activity,
        )
        entry2 = IncomeEntry(
            id=entry_id,
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer_activity,
        )

        assert entry1 == entry2

    def test_entries_with_different_ids_are_not_equal(self, developer_activity):
        entry1 = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer_activity,
        )
        entry2 = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer_activity,
        )

        assert entry1 != entry2

    def test_income_and_expense_with_same_values_are_not_equal(self, developer_activity):
        entry_id = uuid4()
        income = IncomeEntry(
            id=entry_id,
            date=date(2024, 3, 15),
            amount=Decimal("100.00"),
            activity=developer_activity,
        )
        expense = ExpenseEntry(
            id=entry_id,
            date=date(2024, 3, 15),
            amount=Decimal("100.00"),
            activity=developer_activity,
        )

        assert income != expense


class TestFinancialEntryWithClient:
    def test_income_entry_without_client(self, developer_activity):
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer_activity,
        )

        assert entry.client is None

    def test_income_entry_with_client(self, developer_activity, acme_client):
        entry = IncomeEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer_activity,
            client=acme_client,
        )

        assert entry.client == acme_client
        assert entry.client.full_name == "John Doe"

    def test_expense_entry_without_client(self, developer_activity):
        entry = ExpenseEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("50.00"),
            activity=developer_activity,
        )

        assert entry.client is None

    def test_expense_entry_with_client(self, developer_activity, acme_client):
        entry = ExpenseEntry.create(
            date=date(2024, 3, 15),
            amount=Decimal("50.00"),
            activity=developer_activity,
            client=acme_client,
        )

        assert entry.client == acme_client

    def test_entry_with_explicit_client(self, developer_activity, acme_client):
        entry_id = uuid4()
        entry = IncomeEntry(
            id=entry_id,
            date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            activity=developer_activity,
            description="Project payment",
            client=acme_client,
        )

        assert entry.client == acme_client
        assert entry.client.email == "john@acme.com"
