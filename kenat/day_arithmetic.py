from .utils import (
    get_ethiopian_days_in_month,
    is_ethiopian_leap_year,
    validate_numeric_inputs,
    validate_ethiopian_date_object
)

def add_days(ethiopian, days):
    """
    Adds a specified number of days to an Ethiopian date.

    Args:
        ethiopian (dict): The starting Ethiopian date {'year', 'month', 'day'}.
        days (int): The number of days to add.

    Returns:
        dict: The resulting Ethiopian date.
    """
    validate_ethiopian_date_object(ethiopian, 'add_days', 'ethiopian') # 
    validate_numeric_inputs('add_days', days=days) # 
    
    # Create mutable copies
    year, month, day = ethiopian['year'], ethiopian['month'], ethiopian['day']
    day += days

    # Roll over the days into months and years
    while day > get_ethiopian_days_in_month(year, month): # 
        day -= get_ethiopian_days_in_month(year, month) # 
        month += 1 # 
        if month > 13: # 
            month = 1 # 
            year += 1 # 
            
    return {'year': year, 'month': month, 'day': day}

