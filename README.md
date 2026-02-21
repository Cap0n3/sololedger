# SoloLedger

A simple terminal-based personal finance tracker for freelancers and solo entrepreneurs.

## Features

- **Track Income & Expenses** - Record financial entries with amounts, activities, and descriptions
- **Activity-Based Organization** - Categorize entries by custom activities (clients, projects, expense types)
- **Financial Reports** - Generate monthly or yearly summaries with breakdowns by activity
- **Local SQLite Storage** - Data stored locally at `~/.sololedger.db`
- **Terminal UI** - Clean, keyboard-driven interface built with Textual

## Installation

Requires Python 3.13+

```bash
# Clone the repository
git clone https://github.com/cap0n3/SoloLedger.git
cd SoloLedger

# Install with Poetry
poetry install
```

## Usage

```bash
# Run the application
poetry run sololedger
```

### Keyboard Shortcuts

| Key | Action  |
|-----|---------|
| `q` | Quit    |
| `r` | Refresh |

### Tabs

- **Entries** - View all recorded financial entries
- **Add Entry** - Record a new income or expense
- **Activities** - Manage activity categories
- **Report** - Generate monthly or yearly financial summaries

## Development

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=sololedger
```

## Project Structure

```
SoloLedger/
├── sololedger/
│   ├── domain/          # Core domain models
│   │   ├── activity.py
│   │   ├── financial_entry.py
│   │   ├── ledger.py
│   │   └── period.py
│   ├── reporting/       # Report generation
│   │   ├── report.py
│   │   └── report_calculator.py
│   ├── persistence/     # Data storage
│   │   ├── repository.py
│   │   └── sqlite_repository.py
│   └── app.py           # Textual TUI application
├── tests/               # Test suite
└── pyproject.toml
```

## License

MIT
