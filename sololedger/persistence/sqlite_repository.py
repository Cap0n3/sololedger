import sqlite3
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from sololedger.domain.activity import Activity
from sololedger.domain.financial_entry import ExpenseEntry, FinancialEntry, IncomeEntry
from sololedger.domain.ledger import Ledger
from sololedger.persistence.repository import LedgerRepository


class SQLiteLedgerRepository(LedgerRepository):
    """SQLite implementation of LedgerRepository."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._connection = sqlite3.connect(self._db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self._connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT PRIMARY KEY,
                entry_type TEXT NOT NULL,
                date TEXT NOT NULL,
                amount TEXT NOT NULL,
                activity_id TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (activity_id) REFERENCES activities(id)
            )
        """)
        self._connection.commit()

    def save_activity(self, activity: Activity) -> None:
        """Persist an activity."""
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO activities (id, name) VALUES (?, ?)",
            (str(activity.id), activity.name),
        )
        self._connection.commit()

    def get_activity(self, id: UUID) -> Activity | None:
        """Retrieve an activity by ID. Returns None if not found."""
        cursor = self._connection.cursor()
        cursor.execute("SELECT id, name FROM activities WHERE id = ?", (str(id),))
        row = cursor.fetchone()
        if row is None:
            return None
        return Activity(id=UUID(row[0]), name=row[1])

    def get_all_activities(self) -> list[Activity]:
        """Retrieve all persisted activities."""
        cursor = self._connection.cursor()
        cursor.execute("SELECT id, name FROM activities")
        rows = cursor.fetchall()
        return [Activity(id=UUID(row[0]), name=row[1]) for row in rows]

    def save_entry(self, entry: FinancialEntry) -> None:
        """Persist a financial entry."""
        entry_type = "income" if isinstance(entry, IncomeEntry) else "expense"
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO entries
            (id, entry_type, date, amount, activity_id, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(entry.id),
                entry_type,
                entry.date.isoformat(),
                str(entry.amount),
                str(entry.activity.id),
                entry.description,
            ),
        )
        self._connection.commit()

    def get_all_entries(self) -> list[FinancialEntry]:
        """Retrieve all persisted entries."""
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT e.id, e.entry_type, e.date, e.amount, e.activity_id, e.description,
                   a.name
            FROM entries e
            JOIN activities a ON e.activity_id = a.id
        """)
        rows = cursor.fetchall()

        entries: list[FinancialEntry] = []
        for row in rows:
            activity = Activity(id=UUID(row[4]), name=row[6])
            entry_cls = IncomeEntry if row[1] == "income" else ExpenseEntry
            entry = entry_cls(
                id=UUID(row[0]),
                date=date.fromisoformat(row[2]),
                amount=Decimal(row[3]),
                activity=activity,
                description=row[5],
            )
            entries.append(entry)
        return entries

    def save_ledger(self, ledger: Ledger) -> None:
        """Persist all entries from a ledger."""
        for entry in ledger.get_entries():
            self.save_activity(entry.activity)
            self.save_entry(entry)

    def load_ledger(self) -> Ledger:
        """Load a ledger with all persisted entries."""
        ledger = Ledger()
        for entry in self.get_all_entries():
            ledger.add_entry(entry)
        return ledger

    def close(self) -> None:
        """Close the database connection."""
        self._connection.close()
