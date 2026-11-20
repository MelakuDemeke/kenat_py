import pytest
from kenat.utils import (
    day_of_year,
    month_day_from_day_of_year,
    is_gregorian_leap_year,
    is_ethiopian_leap_year,
    get_ethiopian_days_in_month,
    get_ethiopian_new_year_for_gregorian,
    get_gregorian_date_of_ethiopian_new_year
)

@pytest.mark.parametrize("year, month, day, expected_doy", [
    (2023, 1, 1, 1),
    (2023, 2, 1, 32),
    (2023, 2, 28, 59),
    (2023, 3, 1, 60),
    (2024, 2, 29, 60),  # Leap year
    (2024, 3, 1, 61),   # Leap year
    (2023, 12, 31, 365),
    (2024, 12, 31, 366), # Leap year
])
def test_day_of_year(year, month, day, expected_doy):
    assert day_of_year(year, month, day) == expected_doy


@pytest.mark.parametrize("year, doy, expected_date", [
    (2023, 1, {'month': 1, 'day': 1}),
    (2023, 32, {'month': 2, 'day': 1}),
    (2023, 60, {'month': 3, 'day': 1}),
    (2024, 60, {'month': 2, 'day': 29}), # Leap year
    (2024, 61, {'month': 3, 'day': 1}),  # Leap year
    (2023, 365, {'month': 12, 'day': 31}),
    (2024, 366, {'month': 12, 'day': 31}),# Leap year
])
def test_month_day_from_day_of_year(year, doy, expected_date):
    assert month_day_from_day_of_year(year, doy) == expected_date


class TestLeapYearFunctions:
    @pytest.mark.parametrize("year, expected", [
        (2024, True), (1996, True), # Divisible by 4, not 100
        (2023, False), (2019, False),# Not divisible by 4
        (1900, False), (2100, False),# Divisible by 100, not 400
        (2000, True), (1600, True),  # Divisible by 400
    ])
    def test_is_gregorian_leap_year(self, year, expected):
        assert is_gregorian_leap_year(year) is expected

    @pytest.mark.parametrize("year, expected", [
        (2011, True), (2015, True), # year % 4 == 3
        (2010, False), (2012, False),# year % 4 != 3
    ])
    def test_is_ethiopian_leap_year(self, year, expected):
        assert is_ethiopian_leap_year(year) is expected


class TestGetEthiopianDaysInMonth:
    @pytest.mark.parametrize("month", range(1, 13))
    def test_returns_30_for_standard_months(self, month):
        assert get_ethiopian_days_in_month(2010, month) == 30
        assert get_ethiopian_days_in_month(2011, month) == 30 # Also for leap years

    @pytest.mark.parametrize("leap_year", [2011, 2015, 2019])
    def test_returns_6_for_pagume_in_leap_year(self, leap_year):
        assert get_ethiopian_days_in_month(leap_year, 13) == 6

    @pytest.mark.parametrize("non_leap_year", [2010, 2012, 2013, 2014])
    def test_returns_5_for_pagume_in_non_leap_year(self, non_leap_year):
        assert get_ethiopian_days_in_month(non_leap_year, 13) == 5

class TestEthiopianNewYearHelpers:
    @pytest.mark.parametrize("eth_year, expected", [
        (1876, {'gregorianYear': 1883, 'month': 9, 'day': 11}),
        (1888, {'gregorianYear': 1895, 'month': 9, 'day': 11}),
        (1892, {'gregorianYear': 1899, 'month': 9, 'day': 11}),
        (1893, {'gregorianYear': 1900, 'month': 9, 'day': 11}),
        (2016, {'gregorianYear': 2023, 'month': 9, 'day': 12}),
        (2092, {'gregorianYear': 2099, 'month': 9, 'day': 12}),
        (2093, {'gregorianYear': 2100, 'month': 9, 'day': 12}),
    ])
    def test_get_gregorian_date_of_ethiopian_new_year(self, eth_year, expected):
        assert get_gregorian_date_of_ethiopian_new_year(eth_year) == expected

    @pytest.mark.parametrize("g_year, expected_day", [
        (1883, 11), (1895, 11), (1899, 11), (1900, 11),
        (2023, 12), (2024, 11), (2099, 12), (2100, 12),
    ])
    def test_get_ethiopian_new_year_for_gregorian(self, g_year, expected_day):
        assert get_ethiopian_new_year_for_gregorian(g_year) == {'gregorianYear': g_year, 'month': 9, 'day': expected_day}
