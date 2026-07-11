# tests/test_kenat.py

import pytest
import datetime
from kenat import Kenat

class TestKenatClass:
    """
    This class corresponds to the 'Kenat class' describe block in the JS test.
    It tests the constructor and formatting methods.
    """

    def test_should_create_an_instance_with_current_date(self):
        now = datetime.datetime.now()
        kenat = Kenat()
        gregorian = kenat.get_gregorian()

        # Check that the date parts match today's date
        assert gregorian['year'] == now.year
        assert gregorian['month'] == now.month
        assert gregorian['day'] == now.day

        # Check that the ethiopian property exists
        ethiopian = kenat.get_ethiopian()
        assert 'year' in ethiopian
        assert 'month' in ethiopian
        assert 'day' in ethiopian

    def test_should_convert_a_specific_ethiopian_date_correctly(self):
        kenat = Kenat("2016/9/15")
        assert kenat.get_gregorian() == {'year': 2024, 'month': 5, 'day': 23}
        assert kenat.get_ethiopian() == {'year': 2016, 'month': 9, 'day': 15}

    def test_to_string_should_return_ethiopian_date_string(self):
        kenat = Kenat("2016/9/15")
        # The 9th Ethiopian month is 'Ginbot'. The to_string() method uses Amharic.
        assert kenat.to_string() == "ግንቦት 15 2016 12:00 ጠዋት"

    def test_format_returns_ethiopian_date_string_in_english_and_amharic(self):
        kenat = Kenat("2017/1/15")  # Meskerem 15, 2017
        assert kenat.format({'lang': 'english'}) == "Meskerem 15 2017"
        assert kenat.format({'lang': 'amharic'}) == "መስከረም 15 2017"

    def test_format_in_geez_amharic_returns_correct_string(self):
        kenat = Kenat("2017/1/15")  # Meskerem 15, 2017
        assert kenat.format_in_geez_amharic() == "መስከረም ፲፭ ፳፻፲፯"


class TestKenatApiHelperMethods:
    """
    This class corresponds to the 'Kenat API Helper Methods' describe block.
    """

    @pytest.fixture(scope="class")
    def dates(self):
        """Provides a set of dates for testing comparisons."""
        return {
            "date1": Kenat("2016/8/15"),
            "date2": Kenat("2016/8/20"),
            "date3": Kenat("2016/8/15"),
            "leap": Kenat("2015/1/1"),      # 2015 is a leap year
            "non_leap": Kenat("2016/1/1"),  # 2016 is not
        }

    def test_is_before_should_correctly_compare_dates(self, dates):
        assert dates['date1'].is_before(dates['date2']) is True
        assert dates['date2'].is_before(dates['date1']) is False
        assert dates['date1'].is_before(dates['date3']) is False

    def test_is_after_should_correctly_compare_dates(self, dates):
        assert dates['date2'].is_after(dates['date1']) is True
        assert dates['date1'].is_after(dates['date2']) is False
        assert dates['date1'].is_after(dates['date3']) is False

    def test_is_same_day_should_correctly_compare_dates(self, dates):
        assert dates['date1'].is_same_day(dates['date3']) is True
        assert dates['date1'].is_same_day(dates['date2']) is False

    def test_start_of_month_should_return_first_day(self, dates):
        start = dates['date1'].start_of_month()
        assert start.get_ethiopian() == {'year': 2016, 'month': 8, 'day': 1}

    def test_end_of_month_should_return_last_day_of_standard_month(self, dates):
        end = dates['date1'].end_of_month()
        assert end.get_ethiopian() == {'year': 2016, 'month': 8, 'day': 30}

    def test_end_of_month_should_return_last_day_of_pagume_in_leap_year(self):
        pagume = Kenat("2015/13/1")  # 2015 is a leap year
        end = pagume.end_of_month()
        assert end.get_ethiopian() == {'year': 2015, 'month': 13, 'day': 6}

    def test_is_leap_year_should_correctly_identify_leap_years(self, dates):
        assert dates['leap'].is_leap_year() is True
        assert dates['non_leap'].is_leap_year() is False

    def test_weekday_should_return_correct_day_of_the_week(self):
        # 2016/9/15 ET is May 23, 2024 GC, which is a Thursday.
        # In JS getDay(), Thursday is 4.
        specific_date = Kenat("2016/9/15")
        assert specific_date.weekday() == 4

    def test_end_of_year_returns_pagume_6_for_leap_years(self):
        # Ethiopian year 2015 has year % 4 == 3, so it IS a leap year.
        leap_year = Kenat('2015/5/10')
        end = leap_year.end_of('year')
        assert end.get_ethiopian() == {'year': 2015, 'month': 13, 'day': 6}

    def test_end_of_year_returns_pagume_5_for_non_leap_years(self):
        non_leap_year = Kenat('2016/5/10')
        end = non_leap_year.end_of('year')
        assert end.get_ethiopian() == {'year': 2016, 'month': 13, 'day': 5}

    def test_is_same_month_true_for_same_month_and_year(self):
        a = Kenat('2017/5/1')
        b = Kenat('2017/5/30')
        assert a.is_same_month(b) is True

    def test_is_same_month_false_for_different_months(self):
        a = Kenat('2017/5/15')
        b = Kenat('2017/6/15')
        assert a.is_same_month(b) is False

    def test_is_same_month_false_for_same_month_different_year(self):
        a = Kenat('2016/5/15')
        b = Kenat('2017/5/15')
        assert a.is_same_month(b) is False

    def test_is_same_year_true(self):
        a = Kenat('2017/1/1')
        b = Kenat('2017/12/30')
        assert a.is_same_year(b) is True

    def test_is_same_year_false(self):
        a = Kenat('2016/5/15')
        b = Kenat('2017/5/15')
        assert a.is_same_year(b) is False

    def test_to_json_returns_serializable_plain_dict(self):
        kenat = Kenat('2017/1/15')
        result = kenat.to_json()
        assert result['ethiopian'] == {'year': 2017, 'month': 1, 'day': 15}
        assert 'year' in result['gregorian']
        assert 'month' in result['gregorian']
        assert 'day' in result['gregorian']
        assert result['time'] is not None
        assert 'hour' in result['time']
        assert 'minute' in result['time']
        assert 'period' in result['time']

    def test_diff_in_months_reversed_matches_ts_reference(self):
        # Mirrors kenat/tests/dayArtimetic.test.ts's KenatDiffInMonthsTests.
        a = Kenat('2016/05/01')
        b = Kenat('2016/06/06')
        assert a.diff_in_months(b) == -2

    def test_diff_in_years_reversed_matches_ts_reference(self):
        a = Kenat('2016/01/01')
        b = Kenat('2018/01/01')
        assert a.diff_in_years(b) == -2

    def test_add_days_negative_crosses_month_boundary(self):
        k = Kenat('2016/1/3')
        result = k.add_days(-5)
        # Rolls back into Pagume of 2015 (a leap year -> 6 days): 6 - 2 = 4.
        assert result.get_ethiopian() == {'year': 2015, 'month': 13, 'day': 4}

    def test_add_preserves_time_of_day(self):
        from kenat.time import Time
        k = Kenat('2016/1/10', time_obj=Time(8, 30, 'night'))
        result = k.add(days=5)
        assert result.time == Time(8, 30, 'night')

    def test_subtract_is_inverse_of_add(self):
        k = Kenat('2016/6/15')
        forward = k.add(years=1, months=2, days=3)
        back = forward.subtract(years=1, months=2, days=3)
        assert back.get_ethiopian() == k.get_ethiopian()

    def test_generate_date_range_returns_inclusive_range(self):
        start = Kenat('2016/1/1')
        end = Kenat('2016/1/5')
        date_range = Kenat.generate_date_range(start, end)
        assert len(date_range) == 5
        assert date_range[0].get_ethiopian() == {'year': 2016, 'month': 1, 'day': 1}
        assert date_range[-1].get_ethiopian() == {'year': 2016, 'month': 1, 'day': 5}

    def test_generate_date_range_returns_empty_when_start_after_end(self):
        start = Kenat('2016/1/5')
        end = Kenat('2016/1/1')
        assert Kenat.generate_date_range(start, end) == []


class TestKenatDistanceHelpers:
    def test_distance_to_returns_breakdown_object(self):
        a = Kenat('2016/1/1')
        b = Kenat('2018/3/10')
        breakdown = a.distance_to(b)
        assert breakdown['years'] == 2
        assert breakdown['months'] == 2
        assert breakdown['days'] == 9

    def test_distance_to_string_output(self):
        a = Kenat('2016/1/1')
        b = Kenat('2018/1/1')
        result = a.distance_to(b, output='string', lang='english')
        assert '2 years' in result

    def test_distance_from_today_matches_distance_to(self):
        target = Kenat('2016/1/1')
        today = Kenat()
        assert target.distance_from_today() == today.distance_to(target)


class TestKenatCalendarPreference:
    """Mirrors kenat/tests/Kenat.test.ts's 'Calendar preference option' describe block."""

    def test_get_date_defaults_to_ethiopian(self):
        kenat = Kenat('2016/1/1')
        assert kenat.get_date() == {'year': 2016, 'month': 1, 'day': 1}

    def test_get_date_gregorian(self):
        kenat = Kenat('2016/1/1')
        assert kenat.get_date(calendar='gregorian') == {'year': 2023, 'month': 9, 'day': 12}

    def test_format_defaults_to_ethiopian(self):
        kenat = Kenat('2016/1/1')
        assert kenat.format() == 'መስከረም 1 2016'

    def test_format_gregorian(self):
        kenat = Kenat('2016/1/1')
        assert kenat.format({'calendar': 'gregorian'}) == 'September 12, 2023'

    def test_format_gregorian_show_weekday(self):
        kenat = Kenat('2016/1/1')
        assert kenat.format({'calendar': 'gregorian', 'show_weekday': True}) == 'ማክሰኞ, September 12, 2023'
        assert kenat.format({'calendar': 'gregorian', 'show_weekday': True, 'lang': 'english'}) == 'Tuesday, September 12, 2023'

    def test_format_gregorian_include_time(self):
        from kenat.time import Time
        timed_kenat = Kenat('2016/1/1', time_obj=Time(8, 30, 'day'))
        assert timed_kenat.format({'calendar': 'gregorian', 'include_time': True}) == 'September 12, 2023 08:30 ጠዋት'

    def test_to_iso_string_defaults_to_ethiopian(self):
        kenat = Kenat('2016/1/1')
        assert kenat.to_iso_string() == '2016-01-01T12:00'

    def test_to_iso_string_appends_plus12h_suffix_for_night(self):
        from kenat.time import Time
        night_kenat = Kenat('2016/1/1', time_obj=Time(8, 15, 'night'))
        assert night_kenat.to_iso_string() == '2016-01-01T08:15+12h'

    def test_to_iso_string_gregorian_converts_time_to_24_hour(self):
        kenat = Kenat('2016/1/1')
        # 12:00 day Ethiopian time is 06:00 Gregorian, not 12:00.
        assert kenat.to_iso_string(calendar='gregorian') == '2023-09-12T06:00'

    def test_to_iso_string_gregorian_night_no_nonstandard_suffix(self):
        from kenat.time import Time
        night_kenat = Kenat('2016/1/1', time_obj=Time(8, 15, 'night'))
        iso = night_kenat.to_iso_string(calendar='gregorian')
        assert iso == '2023-09-12T02:15'
        import re
        assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$', iso)


class TestKenatStaticMonthCalendarGrid:
    def test_get_month_calendar_grid_matches_month_grid_flat_shape(self):
        result = Kenat.get_month_calendar_grid(2016, 9)
        assert set(['month', 'month_name', 'year', 'headers', 'days']) <= set(result.keys())
        assert result['month'] == 9
        assert isinstance(result['days'], list)
        # Flat shape (start-padded only), so length isn't necessarily a multiple of 7.
        non_null_days = [d for d in result['days'] if d is not None]
        assert len(non_null_days) == 30