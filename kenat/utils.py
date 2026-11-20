import datetime
from .exceptions import InvalidInputTypeError

# --- Validation Helpers ---

def validate_numeric_inputs(func_name, **kwargs):
    """
    Validates that all provided keyword arguments are numbers.
    
    Raises:
        InvalidInputTypeError: If any value is not a number.
    """
    for name, value in kwargs.items():
        if not isinstance(value, (int, float)) or value != value: # Checks for NaN
            raise InvalidInputTypeError(func_name, name, 'number', value)

def validate_ethiopian_date_object(date_obj, func_name, param_name):
    """
    Validates that the input is a valid Ethiopian date object.
    
    Raises:
        InvalidInputTypeError: If the object is not a dict or its components are not numbers.
    """
    if not isinstance(date_obj, dict):
        raise InvalidInputTypeError(func_name, param_name, 'dict', date_obj)
    validate_numeric_inputs(
        func_name,
        **{
            f'{param_name}.year': date_obj.get('year'),
            f'{param_name}.month': date_obj.get('month'),
            f'{param_name}.day': date_obj.get('day'),
        }
    )

def validate_ethiopian_time_object(time_obj, func_name, param_name):
    """
    Validates that the input is a valid Ethiopian time object.

    Raises:
        InvalidInputTypeError: If the object is not a dict, has an invalid period,
            or its hour/minute are not numbers.
    """
    if not isinstance(time_obj, dict):
        raise InvalidInputTypeError(func_name, param_name, 'dict', time_obj)
    period = time_obj.get('period')
    if period not in ('day', 'night'):
        raise InvalidInputTypeError(func_name, f'{param_name}.period', "'day' or 'night'", period)
    validate_numeric_inputs(
        func_name,
        **{
            f'{param_name}.hour': time_obj.get('hour'),
            f'{param_name}.minute': time_obj.get('minute'),
        }
    )

# --- Date Property Helpers ---

def is_gregorian_leap_year(year):
    """
    Checks if the given Gregorian year is a leap year.
    Leap years occur every 4 years, except for centuries not divisible by 400.
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def is_ethiopian_leap_year(year):
    """
    Checks if the given Ethiopian year is a leap year.
    Ethiopian leap years happen when the year modulo 4 equals 3.
    """
    return year % 4 == 3

def get_ethiopian_days_in_month(year, month):
    """
    Returns the number of days in the given Ethiopian month and year.
    """
    if month == 13:
        return 6 if is_ethiopian_leap_year(year) else 5
    return 30

def get_weekday(eth_date):
    """
    Returns the weekday (0=Sunday, 6=Saturday) for a given Ethiopian date.
    """
    # Import locally to prevent circular dependency with the 'conversions' module
    from . import conversions
    g = conversions.toGC(eth_date['year'], eth_date['month'], eth_date['day'])
    # The getDay() method in JS returns 0 for Sunday, which matches Python's isoweekday() % 7 behavior.
    # Python's weekday() is 0 for Monday. JS getDay() is 0 for Sunday.
    # The source new Date(...).getDay() is 0 for Sunday.
    return (g.isoweekday() % 7)

def is_valid_ethiopian_date(year, month, day):
    """
    Checks if a given Ethiopian date is valid.
    """
    if not 1 <= month <= 13:
        return False
    if not 1 <= day <= get_ethiopian_days_in_month(year, month):
        return False
    return True

def get_ethiopian_new_year_for_gregorian(g_year):
    """
    Returns the Ethiopian New Year date that falls within the given Gregorian year.
    """
    validate_numeric_inputs('get_ethiopian_new_year_for_gregorian', gYear=g_year)
    # Meskerem 1 in September of Gregorian year G belongs to Ethiopian year G - 7.
    return get_gregorian_date_of_ethiopian_new_year(g_year - 7)

def get_gregorian_date_of_ethiopian_new_year(ethiopian_year):
    """
    Returns the Gregorian date of the Ethiopian New Year for the given Ethiopian year.
    """
    validate_numeric_inputs('get_gregorian_date_of_ethiopian_new_year', ethiopianYear=ethiopian_year)
    # Count days from a known anchor (Meskerem 1, 1964 ET = Sep 12, 1971 GC) using the
    # Ethiopian leap cycle (every 4th year, no century exception), so the result is
    # correct outside 1900-2099 GC where the Gregorian leap rule would disagree.
    days = 365 * (ethiopian_year - 1964) + ethiopian_year // 4 - 1964 // 4
    date = datetime.date(1971, 9, 12) + datetime.timedelta(days=days)
    return {'gregorianYear': date.year, 'month': date.month, 'day': date.day}

def day_of_year(year, month, day):
    """Calculates the day of the year for a given Gregorian date."""
    month_lengths = [31, 29 if is_gregorian_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    doy = day
    for i in range(month - 1):
        doy += month_lengths[i]
    return doy

def month_day_from_day_of_year(year, day_of_year):
    """Converts a day of year to a Gregorian month and day."""
    month_lengths = [31, 29 if is_gregorian_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    month = 1
    while day_of_year > month_lengths[month - 1]:
        day_of_year -= month_lengths[month - 1]
        month += 1
    return {'month': month, 'day': day_of_year}