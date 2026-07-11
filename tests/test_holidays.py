import pytest
from kenat.holidays import get_holidays_in_month, get_holiday
from kenat.bahire_hasab import getMovableHoliday
from kenat.exceptions import InvalidInputTypeError, UnknownHolidayError


# -------------------
# get_holidays_in_month
# -------------------

def test_returns_fixed_and_movable_holidays_for_month():
    holidays = get_holidays_in_month(2016, 1)
    keys = [h['key'] for h in holidays]
    assert 'enkutatash' in keys
    assert 'meskel' in keys


def test_returns_correct_movable_christian_holidays():
    holidays = get_holidays_in_month(2016, 8)
    fasika = next((h for h in holidays if h['key'] == 'fasika'), None)
    siklet = next((h for h in holidays if h['key'] == 'siklet'), None)

    assert fasika is not None
    assert fasika['ethiopian']['day'] == 27

    assert siklet is not None
    assert siklet['ethiopian']['day'] == 25


# -------------------
# get_movable_holiday (Bahire Hasab)
# -------------------

@pytest.mark.parametrize("year, expected", [
    (2012, {'year': 2012, 'month': 8, 'day': 11}),
    (2013, {'year': 2013, 'month': 8, 'day': 24}),
    (2014, {'year': 2014, 'month': 8, 'day': 16}),
    (2015, {'year': 2015, 'month': 8, 'day': 8}),
    (2016, {'year': 2016, 'month': 8, 'day': 27}),
])
def test_returns_correct_tinsaye_date(year, expected):
    assert getMovableHoliday('TINSAYE', year) == expected


@pytest.mark.parametrize("year, expected", [
    (2012, {'year': 2012, 'month': 8, 'day': 9}),
    (2013, {'year': 2013, 'month': 8, 'day': 22}),
    (2014, {'year': 2014, 'month': 8, 'day': 14}),
    (2015, {'year': 2015, 'month': 8, 'day': 6}),
    (2016, {'year': 2016, 'month': 8, 'day': 25}),
])
def test_returns_correct_siklet_date(year, expected):
    assert getMovableHoliday('SIKLET', year) == expected


# -------------------
# Error Handling
# -------------------

@pytest.mark.parametrize("year, month", [
    ('2016', 1),
    (2016, 'one'),
])
def test_get_holidays_in_month_invalid_input_type(year, month):
    with pytest.raises(InvalidInputTypeError):
        get_holidays_in_month(year, month)


@pytest.mark.parametrize("month", [0, 14])
def test_get_holidays_in_month_invalid_month_range(month):
    with pytest.raises(InvalidInputTypeError):
        get_holidays_in_month(2016, month)


@pytest.mark.parametrize("year", [None, '2016'])
def test_get_movable_holiday_invalid_year_type(year):
    with pytest.raises(InvalidInputTypeError):
        getMovableHoliday('TINSAYE', year)


def test_get_movable_holiday_unknown_key():
    with pytest.raises(UnknownHolidayError):
        getMovableHoliday('UNKNOWN_HOLIDAY', 2016)


# -------------------
# Muslim Holidays
# -------------------

def test_returns_correct_moulid_date_2016():
    holiday = get_holiday('moulid', 2016)
    assert holiday is not None
    assert holiday['ethiopian'] == {'year': 2016, 'month': 1, 'day': 15}


def test_returns_correct_eid_fitr_date_2016():
    holiday = get_holiday('eidFitr', 2016)
    assert holiday is not None
    assert holiday['ethiopian'] == {'year': 2016, 'month': 8, 'day': 1}


def test_returns_correct_eid_adha_date_2016():
    holiday = get_holiday('eidAdha', 2016)
    assert holiday is not None
    assert holiday['ethiopian'] == {'year': 2016, 'month': 10, 'day': 9}


# -------------------
# Fixed-holiday data regression
# -------------------

def test_beherbehereseb_falls_on_day_29():
    # Regression test: Nations, Nationalities and Peoples' Day is Megabit 29, not 20.
    holiday = get_holiday('beherbehereseb', 2016)
    assert holiday is not None
    assert holiday['ethiopian'] == {'year': 2016, 'month': 3, 'day': 29}


def test_siklet_is_tagged_public():
    # Regression test: Good Friday (siklet) must carry the PUBLIC tag.
    holiday = get_holiday('siklet', 2016)
    assert holiday is not None
    assert 'public' in holiday['tags']


def test_find_hijri_month_ranges_returns_ramadan_range_for_2016():
    from kenat.holidays import find_hijri_month_ranges
    ranges = find_hijri_month_ranges(2016, 9)  # 9 = Ramadan
    assert len(ranges) >= 1
    start = ranges[0]['start']
    end = ranges[0]['end']
    assert start['year'] == 2016
    assert end['year'] == 2016
    # The range should span roughly a lunar month (29 or 30 days).
    from kenat.day_arithmetic import diffInDays
    span = diffInDays(end, start)
    assert 27 <= span <= 30
