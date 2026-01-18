from datetime import date

import pytest

from sololedger import MonthlyPeriod, Period, YearlyPeriod


class TestMonthlyPeriod:
    def test_contains_date_in_same_month(self):
        period = MonthlyPeriod(year=2024, month=3)

        assert period.contains(date(2024, 3, 1)) is True
        assert period.contains(date(2024, 3, 15)) is True
        assert period.contains(date(2024, 3, 31)) is True

    def test_does_not_contain_date_in_different_month(self):
        period = MonthlyPeriod(year=2024, month=3)

        assert period.contains(date(2024, 2, 28)) is False
        assert period.contains(date(2024, 4, 1)) is False

    def test_does_not_contain_date_in_different_year(self):
        period = MonthlyPeriod(year=2024, month=3)

        assert period.contains(date(2023, 3, 15)) is False
        assert period.contains(date(2025, 3, 15)) is False

    def test_invalid_month_raises_error(self):
        with pytest.raises(ValueError):
            MonthlyPeriod(year=2024, month=0)

        with pytest.raises(ValueError):
            MonthlyPeriod(year=2024, month=13)

    def test_is_immutable(self):
        period = MonthlyPeriod(year=2024, month=3)

        with pytest.raises(AttributeError):
            period.year = 2025

    def test_is_a_period(self):
        period = MonthlyPeriod(year=2024, month=3)
        assert isinstance(period, Period)


class TestYearlyPeriod:
    def test_contains_date_in_same_year(self):
        period = YearlyPeriod(year=2024)

        assert period.contains(date(2024, 1, 1)) is True
        assert period.contains(date(2024, 6, 15)) is True
        assert period.contains(date(2024, 12, 31)) is True

    def test_does_not_contain_date_in_different_year(self):
        period = YearlyPeriod(year=2024)

        assert period.contains(date(2023, 12, 31)) is False
        assert period.contains(date(2025, 1, 1)) is False

    def test_is_immutable(self):
        period = YearlyPeriod(year=2024)

        with pytest.raises(AttributeError):
            period.year = 2025

    def test_is_a_period(self):
        period = YearlyPeriod(year=2024)
        assert isinstance(period, Period)


class TestPeriodEquality:
    def test_monthly_periods_with_same_values_are_equal(self):
        period1 = MonthlyPeriod(year=2024, month=3)
        period2 = MonthlyPeriod(year=2024, month=3)

        assert period1 == period2

    def test_monthly_periods_with_different_values_are_not_equal(self):
        period1 = MonthlyPeriod(year=2024, month=3)
        period2 = MonthlyPeriod(year=2024, month=4)

        assert period1 != period2

    def test_yearly_periods_with_same_values_are_equal(self):
        period1 = YearlyPeriod(year=2024)
        period2 = YearlyPeriod(year=2024)

        assert period1 == period2

    def test_yearly_periods_with_different_values_are_not_equal(self):
        period1 = YearlyPeriod(year=2024)
        period2 = YearlyPeriod(year=2025)

        assert period1 != period2
