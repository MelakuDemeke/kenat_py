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


