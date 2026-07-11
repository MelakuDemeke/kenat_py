"""
Fasting period calculations (Great Lent, Nineveh, Ramadan, etc.), ported from
kenat/src/fasting.ts. Built on top of bahire_hasab.py and holidays.py's Hijri
range finder.
"""
from .bahire_hasab import getBahireHasab
from .holidays import find_hijri_month_ranges
from .day_arithmetic import addDays, diffInDays
from .constants import FASTING_INFO, FastingKeys
from .utils import get_weekday, get_ethiopian_days_in_month, validate_numeric_inputs, validate_ethiopian_date_object


def get_fasting_period(fast_key, ethiopian_year):
    """
    Calculates the start and end dates of a specific fasting period for a given year.

    Args:
        fast_key (str): One of the FastingKeys values (e.g. FastingKeys.ABIY_TSOME).
        ethiopian_year (int): The Ethiopian year.

    Returns:
        dict | None: {'start': EthiopianDate, 'end': EthiopianDate}, or None if the
            fast key is unknown or the period cannot be computed.
    """
    bh = getBahireHasab(ethiopian_year)
    movable_feasts = bh['movableFeasts']

    if fast_key == FastingKeys.ABIY_TSOME:
        start = movable_feasts.get('abiyTsome', {}).get('ethiopian')
        end = movable_feasts.get('siklet', {}).get('ethiopian')
        if start and end:
            return {'start': start, 'end': end}
        return None

    if fast_key == FastingKeys.TSOME_HAWARYAT:
        start = movable_feasts.get('tsomeHawaryat', {}).get('ethiopian')
        end = {'year': ethiopian_year, 'month': 11, 'day': 4}
        if start:
            return {'start': start, 'end': end}
        return None

    if fast_key == FastingKeys.NINEVEH:
        start = movable_feasts.get('nineveh', {}).get('ethiopian')
        if start:
            end = addDays(start, 2)
            return {'start': start, 'end': end}
        return None

    if fast_key == FastingKeys.TSOME_NEBIYAT:
        start = {'year': ethiopian_year, 'month': 3, 'day': 15}
        end = {'year': ethiopian_year, 'month': 4, 'day': 28}
        return {'start': start, 'end': end}

    if fast_key == FastingKeys.FILSETA:
        # Nehase 1 to Nehase 14
        start = {'year': ethiopian_year, 'month': 12, 'day': 1}
        end = {'year': ethiopian_year, 'month': 12, 'day': 14}
        return {'start': start, 'end': end}

    if fast_key == FastingKeys.RAMADAN:
        ranges = find_hijri_month_ranges(ethiopian_year, 9)
        return ranges[0] if ranges else None

    return None


def get_fasting_info(fast_key, ethiopian_year, lang='amharic'):
    """
    Returns fasting information (names, descriptions, period) for a given fast and year.

    Returns:
        dict | None: {'key', 'name', 'description', 'tags', 'period'}, or None if
            the fast key is unrecognized.
    """
    validate_numeric_inputs('getFastingInfo', ethiopianYear=ethiopian_year)
    info = FASTING_INFO.get(fast_key)
    if not info:
        return None

    name = info.get('name', {}).get(lang) or info.get('name', {}).get('english')
    description = info.get('description', {}).get(lang) or info.get('description', {}).get('english')

    # TSOME_DIHENET is a weekly fast (Wed/Fri) with an exception; it doesn't have a
    # single contiguous period.
    if fast_key == FastingKeys.TSOME_DIHENET:
        return {
            'key': fast_key,
            'name': name,
            'description': description,
            'tags': info.get('tags', []),
            'period': None,
        }

    period = get_fasting_period(fast_key, ethiopian_year)
    if not period:
        return None

    return {
        'key': fast_key,
        'name': name,
        'description': description,
        'tags': info.get('tags', []),
        'period': period,
    }


def is_tsome_dihnet_fast_day(et_date):
    """
    Checks if a given Ethiopian date is an Orthodox weekly fasting day (Tsome Dihnet).

    Rules:
    - Fasting occurs every Wednesday and Friday.
    - Exception: for the 50 days after Easter (Fasika) up to and including Pentecost
      (Paraclete), Wednesdays and Fridays are NOT considered fasting days.

    Args:
        et_date (dict): Ethiopian date {'year', 'month', 'day'}.

    Returns:
        bool: True if it's a fasting day, False otherwise.
    """
    validate_ethiopian_date_object(et_date, 'isTsomeDihnetFastDay', 'etDate')

    weekday = get_weekday(et_date)  # 0=Sun ... 6=Sat
    is_wed_or_fri = weekday in (3, 5)
    if not is_wed_or_fri:
        return False

    # Get Easter (Fasika) for the year and apply the 50-day exception window.
    bh = getBahireHasab(et_date['year'])
    fasika = bh.get('movableFeasts', {}).get('fasika', {}).get('ethiopian')
    paraclete = bh.get('movableFeasts', {}).get('paraclete', {}).get('ethiopian')
    if not fasika or not paraclete:
        # If for some reason we cannot compute the window, default to standard Wed/Fri fasting.
        return True

    days_from_easter = diffInDays(et_date, fasika)
    in_pentecost_season = days_from_easter >= 1 and diffInDays(et_date, paraclete) <= 0
    return not in_pentecost_season


def get_fasting_days(fast_key, year, month):
    """
    Returns an array of day numbers in the given Ethiopian month that belong to a
    fasting period.

    For TSOME_DIHENET, returns all Wednesdays and Fridays excluding the 50-day
    period after Easter (through Pentecost). For fixed/range fasts, returns the
    days intersecting the fast period.

    Args:
        fast_key (str): One of FastingKeys.
        year (int): Ethiopian year.
        month (int): Ethiopian month (1-13).

    Returns:
        list[int]
    """
    validate_numeric_inputs('getFastingDays', year=year, month=month)
    days_in_month = get_ethiopian_days_in_month(year, month)

    if fast_key == FastingKeys.TSOME_DIHENET:
        out = []
        for d in range(1, days_in_month + 1):
            if is_tsome_dihnet_fast_day({'year': year, 'month': month, 'day': d}):
                out.append(d)
        return out

    # For other fasts: compute period and intersect with the month.
    period = get_fasting_period(fast_key, year)
    if not period:
        return []

    start_y, start_m = period['start']['year'], period['start']['month']
    end_y, end_m = period['end']['year'], period['end']['month']

    before = (year < start_y) or (year == start_y and month < start_m)
    after = (year > end_y) or (year == end_y and month > end_m)
    if before or after:
        return []

    start_day = period['start']['day'] if (year == start_y and month == start_m) else 1
    end_day = period['end']['day'] if (year == end_y and month == end_m) else days_in_month
    return list(range(start_day, end_day + 1))
