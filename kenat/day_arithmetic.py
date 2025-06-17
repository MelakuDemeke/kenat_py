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

def add_months(ethiopian, months):
    """
    Adds a specified number of months to an Ethiopian date.

    Args:
        ethiopian (dict): The starting Ethiopian date {'year', 'month', 'day'}.
        months (int): The number of months to add.

    Returns:
        dict: The resulting Ethiopian date.
    """
    validate_ethiopian_date_object(ethiopian, 'add_months', 'ethiopian') # 
    validate_numeric_inputs('add_months', months=months) # 
    
    year, month, day = ethiopian['year'], ethiopian['month'], ethiopian['day']
    
    total_months = month + months # 
    year += (total_months - 1) // 13 # 
    month = ((total_months - 1) % 13) + 1 # 

    # If the original day is greater than the number of days in the new month,
    # cap it at the last day of the new month.
    days_in_target_month = get_ethiopian_days_in_month(year, month) # 
    if day > days_in_target_month: # 
        day = days_in_target_month # 
        
    return {'year': year, 'month': month, 'day': day}

