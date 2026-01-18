from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


class Period(ABC):
    """Abstract base class for time periods.

    A Period answers: "Does this date belong to me?"
    """

    @abstractmethod
    def contains(self, d: date) -> bool:
        """Check if the given date falls within this period."""
        pass


@dataclass(frozen=True)
class MonthlyPeriod(Period):
    """A period representing a single calendar month."""

    year: int
    month: int

    def __post_init__(self):
        if not 1 <= self.month <= 12:
            raise ValueError(f"Month must be between 1 and 12, got {self.month}")

    def contains(self, d: date) -> bool:
        return d.year == self.year and d.month == self.month


@dataclass(frozen=True)
class YearlyPeriod(Period):
    """A period representing a single calendar year."""

    year: int

    def contains(self, d: date) -> bool:
        return d.year == self.year
