import datetime
from .utils import (
    is_gregorian_leap_year,
    is_ethiopian_leap_year,
    get_ethiopian_days_in_month,
    validate_numeric_inputs
)
from .exceptions import InvalidEthiopianDateError, InvalidGregorianDateError, KenatError


def to_gc(eth_year, eth_month, eth_day):
    """
    Converts an Ethiopian date to its corresponding Gregorian date.

    Args:
        eth_year (int): The Ethiopian year.
        eth_month (int): The Ethiopian month (1-13).
        eth_day (int): The Ethiopian day.

    Returns:
        datetime.date: The equivalent Gregorian date object.
    """
    # 1. Validate input types and date range 
    validate_numeric_inputs('to_gc', eth_year=eth_year, eth_month=eth_month, eth_day=eth_day)
    if not 1 <= eth_month <= 13 or not 1 <= eth_day <= get_ethiopian_days_in_month(eth_year, eth_month):
        raise InvalidEthiopianDateError(eth_year, eth_month, eth_day)

    # 2. Determine the Gregorian date of the Ethiopian New Year 
    gregorian_year = eth_year + 7
    new_year_day = 12 if is_gregorian_leap_year(gregorian_year + 1) else 11
    new_year_date = datetime.date(gregorian_year, 9, new_year_day)

    # 3. Calculate days elapsed since the Ethiopian new year and add to the new year date 
    days_to_add = (eth_month - 1) * 30 + (eth_day - 1)
    
    return new_year_date + datetime.timedelta(days=days_to_add)

def to_ec(greg_year, greg_month, greg_day):
    """
    Converts a Gregorian date to the Ethiopian calendar (EC) date. 

    Args:
        greg_year (int): The Gregorian year.
        greg_month (int): The Gregorian month (1-12).
        greg_day (int): The Gregorian day.

    Returns:
        dict: A dictionary {'year', 'month', 'day'} for the Ethiopian date.
    """
    # 1. Validate input types and date validity 
    validate_numeric_inputs('to_ec', g_year=greg_year, g_month=greg_month, g_day=greg_day)
    try:
        greg_date = datetime.date(greg_year, greg_month, greg_day)
    except ValueError:
        raise InvalidGregorianDateError(greg_year, greg_month, greg_day)

    # 2. Determine the corresponding Ethiopian year
    # The Ethiopian year starts roughly 7-8 years before the Gregorian year.
    eth_year = greg_year - 8
    greg_of_eth_new_year = to_gc(eth_year + 1, 1, 1)
    if greg_date >= greg_of_eth_new_year:
        eth_year += 1

    # 3. Calculate the difference in days from that Ethiopian New Year
    new_year_greg_date = to_gc(eth_year, 1, 1)
    days_diff = (greg_date - new_year_greg_date).days
    
    # 4. Convert the day difference into Ethiopian month and day
    eth_month = (days_diff // 30) + 1
    eth_day = (days_diff % 30) + 1
    
    return {'year': eth_year, 'month': eth_month, 'day': eth_day}

def _gregorian_to_jd(year, month, day):
    """Converts a Gregorian date to Julian Day Number."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + ((153 * m + 2) // 5) + 365 * y + (y // 4) - (y // 100) + (y // 400) - 32045

def _jd_to_gregorian(jd):
    """Converts a Julian Day Number to a Gregorian date."""
    L = jd + 68569
    N = (4 * L) // 146097
    L = L - (146097 * N + 3) // 4
    I = (4000 * (L + 1)) // 1461001
    L = L - (1461 * I) // 4 + 31
    J = (80 * L) // 2447
    day = L - (2447 * J) // 80
    L = J // 11
    month = J + 2 - 12 * L
    year = 100 * (N - 49) + I + L
    return datetime.date(year, month, day)

