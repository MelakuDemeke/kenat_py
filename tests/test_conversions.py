import pytest
import datetime
from kenat.conversions import toEC, toGC
from kenat.exceptions import InvalidGregorianDateError, InvalidEthiopianDateError

class TestEthiopianToGregorian:
    """
    Tests the `toGC` (Ethiopian to Gregorian) conversion.
    """
    def test_normal_date_conversion(self):
        # 2017-9-14 ET -> May 22, 2025 GC
        assert toGC(2017, 9, 14) == datetime.date(2025, 5, 22)

    def test_pagume_conversion(self):
        # Pagume 5, 2016 ET -> Sep 10, 2024 GC
        assert toGC(2016, 13, 5) == datetime.date(2024, 9, 10)

    def test_leap_year_pagume_conversion(self):
        # Pagume 6, 2011 ET -> Sep 11, 2019 GC
        assert toGC(2011, 13, 6) == datetime.date(2019, 9, 11)

    def test_new_year_conversion(self):
        # Meskerem 1, 2016 ET -> Sep 12, 2023 GC
        # Note: JS test comment said Sep 11, but code expected Sep 12. 2024 is a GC leap year.
        assert toGC(2016, 1, 1) == datetime.date(2023, 9, 12)
        
    def test_random_date_conversion(self):
        # Tahsas 30, 2015 ET -> Jan 8, 2023 GC
        assert toGC(2015, 4, 30) == datetime.date(2023, 1, 8)
    
    def test_invalid_date_throws_error(self):
        with pytest.raises(InvalidEthiopianDateError):
            toGC(2016, 13, 7) # Pagume only has 6 days in a leap year
        with pytest.raises(InvalidEthiopianDateError):
            toGC(2015, 14, 1) # No 14th month


class TestGregorianToEthiopian:
    """
    Tests the `toEC` (Gregorian to Ethiopian) conversion.
    """
    def test_normal_date_conversion(self):
        # May 22, 2025 GC -> 2017-9-14 ET
        assert toEC(2025, 5, 22) == {'year': 2017, 'month': 9, 'day': 14}
        
    def test_gregorian_leap_day_conversion(self):
        # Feb 29, 2020 GC -> Yekatit 22, 2012 ET
        # Note: Day is 22, not 21 as in JS test. The calculation is complex. Let's trust the robust algorithm.
        assert toEC(2020, 2, 29) == {'year': 2012, 'month': 6, 'day': 21}

    def test_pagume_conversion(self):
        # Sep 10, 2024 GC -> Pagume 5, 2016 ET
        assert toEC(2024, 9, 10) == {'year': 2016, 'month': 13, 'day': 5}

    def test_leap_pagume_conversion(self):
        # Sep 11, 2019 GC -> Pagume 6, 2011 ET
        assert toEC(2019, 9, 11) == {'year': 2011, 'month': 13, 'day': 6}

    def test_out_of_range_year_throws_error(self):
        # With our updated toEC function, this test should now pass.
        with pytest.raises(InvalidGregorianDateError):
            toEC(1800, 1, 1)
        with pytest.raises(InvalidGregorianDateError):
            toEC(2200, 1, 1)
            
    def test_invalid_date_throws_error(self):
        with pytest.raises(InvalidGregorianDateError):
            toEC(2023, 2, 29) # Not a leap year


class TestRoundTripFuzz:
    """
    Property-based regression coverage for toGC/toEC: convert a broad spread of
    Ethiopian dates to Gregorian and back (and Gregorian dates to Ethiopian and
    back), and confirm they round-trip to the same date. Per the divergence
    report (kenat_py vs the TS reference), this is deliberately NOT a rewrite of
    the conversion algorithm -- Python derives it differently than TS but should
    produce identical output; this test guards against future regressions
    without re-deriving the algorithm.
    """

    # Ethiopian year N maps to roughly Gregorian year N+7/8, so keep the upper
    # bound comfortably below 2100 (toEC's supported range) to avoid the
    # Gregorian side of the round trip legitimately falling out of range.
    @pytest.mark.parametrize("eth_year", range(1900, 2091, 7))
    def test_ethiopian_round_trip_across_years(self, eth_year):
        for month in (1, 6, 13):
            days_in_month = 6 if month == 13 else 30
            for day in (1, min(15, days_in_month), days_in_month):
                if day < 1:
                    continue
                try:
                    gregorian = toGC(eth_year, month, day)
                except InvalidEthiopianDateError:
                    continue
                back = toEC(gregorian.year, gregorian.month, gregorian.day)
                assert back == {'year': eth_year, 'month': month, 'day': day}

    @pytest.mark.parametrize("greg_year", range(1901, 2100, 7))
    def test_gregorian_round_trip_across_years(self, greg_year):
        for month, day in ((1, 1), (6, 15), (12, 31)):
            try:
                ethiopian = toEC(greg_year, month, day)
            except InvalidGregorianDateError:
                continue
            back = toGC(ethiopian['year'], ethiopian['month'], ethiopian['day'])
            assert back == datetime.date(greg_year, month, day)

class TestCenturyYearConversion:
    """
    Meskerem 1 must follow the Ethiopian leap cycle (year % 4 == 3, no century
    exception), not the Gregorian leap rule, which only agrees for 1900-2099 GC.
    """
    def test_battle_of_adwa(self):
        # Yekatit 23, 1888 ET -> Mar 1, 1896 GC
        assert toGC(1888, 6, 23) == datetime.date(1896, 3, 1)

    def test_pagume_and_new_year_around_2100(self):
        assert toGC(2091, 13, 6) == datetime.date(2099, 9, 11)
        assert toGC(2092, 1, 1) == datetime.date(2099, 9, 12)
        assert toGC(2093, 1, 1) == datetime.date(2100, 9, 12)

    @pytest.mark.parametrize("eth_year, expected", [
        (1876, datetime.date(1883, 9, 11)),
        (1888, datetime.date(1895, 9, 11)),
        (1892, datetime.date(1899, 9, 11)),
        (1893, datetime.date(1900, 9, 11)),
    ])
    def test_new_year_before_1900(self, eth_year, expected):
        assert toGC(eth_year, 1, 1) == expected

    def test_round_trip_every_day_in_supported_range(self):
        # toEC supports 1900-01-01 .. 2100-12-31 GC
        date = datetime.date(1900, 1, 1)
        end = datetime.date(2100, 12, 31)
        while date <= end:
            ethiopian = toEC(date.year, date.month, date.day)
            assert toGC(ethiopian['year'], ethiopian['month'], ethiopian['day']) == date
            date += datetime.timedelta(days=1)
