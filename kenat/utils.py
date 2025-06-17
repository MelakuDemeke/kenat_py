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
    g = conversions.to_gc(eth_date['year'], eth_date['month'], eth_date['day'])
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

