import sqlite3
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from sololedger.domain.activity import Activity
from sololedger.domain.client import Client
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
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                description TEXT
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
        self._migrate_entries_table(cursor)
        self._migrate_clients_table(cursor)
        self._connection.commit()

    def _migrate_entries_table(self, cursor) -> None:
        """Add client_id column to entries table if it doesn't exist."""
        cursor.execute("PRAGMA table_info(entries)")
        columns = [row[1] for row in cursor.fetchall()]
        if "client_id" not in columns:
            cursor.execute("""
                ALTER TABLE entries ADD COLUMN client_id TEXT REFERENCES clients(id)
            """)

    def _migrate_clients_table(self, cursor) -> None:
        """Migrate clients table to new schema if needed."""
        cursor.execute("PRAGMA table_info(clients)")
        columns = [row[1] for row in cursor.fetchall()]
        if "first_name" not in columns and "name" in columns:
            # Old schema detected - need to recreate table
            cursor.execute("ALTER TABLE clients RENAME TO clients_old")
            cursor.execute("""
                CREATE TABLE clients (
                    id TEXT PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    description TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO clients (id, first_name, last_name, email, phone, description)
                SELECT id, name, '', COALESCE(email, ''), NULL, NULL FROM clients_old
            """)
            cursor.execute("DROP TABLE clients_old")

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

    def save_client(self, client: Client) -> None:
        """Persist a client."""
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO clients
            (id, first_name, last_name, email, phone, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(client.id),
                client.first_name,
                client.last_name,
                client.email,
                client.phone,
                client.description,
            ),
        )
        self._connection.commit()

    def get_client(self, id: UUID) -> Client | None:
        """Retrieve a client by ID. Returns None if not found."""
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT id, first_name, last_name, email, phone, description FROM clients WHERE id = ?",
            (str(id),),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Client(
            id=UUID(row[0]),
            first_name=row[1],
            last_name=row[2],
            email=row[3],
            phone=row[4],
            description=row[5],
        )

    def get_all_clients(self) -> list[Client]:
        """Retrieve all persisted clients."""
        cursor = self._connection.cursor()
        cursor.execute("SELECT id, first_name, last_name, email, phone, description FROM clients")
        rows = cursor.fetchall()
        return [
            Client(
                id=UUID(row[0]),
                first_name=row[1],
                last_name=row[2],
                email=row[3],
                phone=row[4],
                description=row[5],
            )
            for row in rows
        ]

    def save_entry(self, entry: FinancialEntry) -> None:
        """Persist a financial entry."""
        entry_type = "income" if isinstance(entry, IncomeEntry) else "expense"
        client_id = str(entry.client.id) if entry.client else None
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO entries
            (id, entry_type, date, amount, activity_id, description, client_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(entry.id),
                entry_type,
                entry.date.isoformat(),
                str(entry.amount),
                str(entry.activity.id),
                entry.description,
                client_id,
            ),
        )
        self._connection.commit()

    def get_all_entries(self) -> list[FinancialEntry]:
        """Retrieve all persisted entries."""
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT e.id, e.entry_type, e.date, e.amount, e.activity_id, e.description,
                   a.name, e.client_id, c.first_name, c.last_name, c.email, c.phone, c.description
            FROM entries e
            JOIN activities a ON e.activity_id = a.id
            LEFT JOIN clients c ON e.client_id = c.id
        """)
        rows = cursor.fetchall()

        entries: list[FinancialEntry] = []
        for row in rows:
            activity = Activity(id=UUID(row[4]), name=row[6])
            client = None
            if row[7] is not None:
                client = Client(
                    id=UUID(row[7]),
                    first_name=row[8],
                    last_name=row[9],
                    email=row[10],
                    phone=row[11],
                    description=row[12],
                )
            entry_cls = IncomeEntry if row[1] == "income" else ExpenseEntry
            entry = entry_cls(
                id=UUID(row[0]),
                date=date.fromisoformat(row[2]),
                amount=Decimal(row[3]),
                activity=activity,
                description=row[5],
                client=client,
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
