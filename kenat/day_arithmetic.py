from .utils import (
    get_ethiopian_days_in_month,
    is_ethiopian_leap_year,
    validate_numeric_inputs,
    validate_ethiopian_date_object
)

def addDays(ethiopian, days):
    """
    Adds a specified number of days to an Ethiopian date.

    Args:
        ethiopian (dict): The starting Ethiopian date {'year', 'month', 'day'}.
        days (int): The number of days to add.

    Returns:
        dict: The resulting Ethiopian date.
    """
    validate_ethiopian_date_object(ethiopian, 'addDays', 'ethiopian') # 
    validate_numeric_inputs('addDays', days=days) # 
    
    # Create mutable copies
    year, month, day = ethiopian['year'], ethiopian['month'], ethiopian['day']
    day += days

    # Roll over the days into months and years (moving forward)
    while day > get_ethiopian_days_in_month(year, month): #
        day -= get_ethiopian_days_in_month(year, month) #
        month += 1 #
        if month > 13: #
            month = 1 #
            year += 1 #

    # Roll back across month/year boundaries (moving backward, for negative `days`)
    while day <= 0:
        month -= 1
        if month < 1:
            month = 13
            year -= 1
        day += get_ethiopian_days_in_month(year, month)

    return {'year': year, 'month': month, 'day': day}

def addMonths(ethiopian, months):
    """
    Adds a specified number of months to an Ethiopian date.

    Args:
        ethiopian (dict): The starting Ethiopian date {'year', 'month', 'day'}.
        months (int): The number of months to add.

    Returns:
        dict: The resulting Ethiopian date.
    """
    validate_ethiopian_date_object(ethiopian, 'addMonths', 'ethiopian') # 
    validate_numeric_inputs('addMonths', months=months) # 
    
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

def addYears(ethiopian, years):
    """
    Adds a specified number of years to an Ethiopian date.

    Args:
        ethiopian (dict): The starting Ethiopian date {'year', 'month', 'day'}.
        years (int): The number of years to add.

    Returns:
        dict: The resulting Ethiopian date.
    """
    validate_ethiopian_date_object(ethiopian, 'addYears', 'ethiopian') # 
    validate_numeric_inputs('addYears', years=years) # 

    year, month, day = ethiopian['year'], ethiopian['month'], ethiopian['day']
    year += years # 

    # Handle the case where the original date was a leap day (Pagume 6),
    # and the new date is in a non-leap year.
    if month == 13 and day == 6 and not is_ethiopian_leap_year(year): # 
        day = 5 # 
        
    return {'year': year, 'month': month, 'day': day}

def diffInDays(date_a, date_b):
    """
    Calculates the difference in days between two Ethiopian dates.

    Args:
        date_a (dict): The first Ethiopian date.
        date_b (dict): The second Ethiopian date.

    Returns:
        int: The difference in days.
    """
    validate_ethiopian_date_object(date_a, 'diffInDays', 'a') # 
    validate_ethiopian_date_object(date_b, 'diffInDays', 'b') # 

    def total_days(eth_date): # 
        """Helper to count days from a fixed epoch (year 1, month 1, day 1)."""
        days = 0
        # Add days from full years
        for y in range(1, eth_date['year']): # 
            days += 366 if is_ethiopian_leap_year(y) else 365 # 
        # Add days from full months in the current year
        for m in range(1, eth_date['month']): # 
            days += get_ethiopian_days_in_month(eth_date['year'], m)
        # Add days in the current month
        days += eth_date['day'] # 
        return days

    return total_days(date_a) - total_days(date_b) # 

def diffInMonths(date_a, date_b):
    """
    Calculates the difference in months between two Ethiopian dates.
    """
    validate_ethiopian_date_object(date_a, 'diffInMonths', 'a') # 
    validate_ethiopian_date_object(date_b, 'diffInMonths', 'b') # 
    
    total_months_a = date_a['year'] * 13 + (date_a['month'] - 1) # 
    total_months_b = date_b['year'] * 13 + (date_b['month'] - 1) # 
    
    diff = total_months_a - total_months_b # 
    
    # Adjust if the day of the later date hasn't been reached yet
    if date_a['day'] < date_b['day']: # 
        diff -= 1 # 
        
    return diff

def diffInYears(date_a, date_b):
    """
    Calculates the difference in years between two Ethiopian dates.
    """
    validate_ethiopian_date_object(date_a, 'diffInYears', 'a') #
    validate_ethiopian_date_object(date_b, 'diffInYears', 'b') #

    is_after = (
        date_a['year'] > date_b['year']
        or (date_a['year'] == date_b['year'] and date_a['month'] > date_b['month'])
        or (
            date_a['year'] == date_b['year']
            and date_a['month'] == date_b['month']
            and date_a['day'] >= date_b['day']
        )
    )

    later, earlier = (date_a, date_b) if is_after else (date_b, date_a)
    diff = later['year'] - earlier['year']

    if later['month'] < earlier['month'] or (
        later['month'] == earlier['month'] and later['day'] < earlier['day']
    ):
        diff -= 1

    final_diff = diff if is_after else -diff

    # Coerce -0 to 0 (Python ints don't have -0, but keep this for symmetry with TS).
    return 0 if final_diff == 0 else final_diff


def diffBreakdown(date_a, date_b, units=None):
    """
    Calculates a human-friendly breakdown between two Ethiopian dates.
    Iteratively accumulates years, then months, then days to avoid off-by-one issues.

    Args:
        date_a (dict): First Ethiopian date {'year', 'month', 'day'}.
        date_b (dict): Second Ethiopian date {'year', 'month', 'day'}.
        units (list[str] | None): Units to include, in order. Defaults to
            ['years', 'months', 'days'].

    Returns:
        dict: {'sign': 1 | -1, 'totalDays': int, 'years'?: int, 'months'?: int, 'days'?: int}
    """
    validate_ethiopian_date_object(date_a, 'diffBreakdown', 'a')
    validate_ethiopian_date_object(date_b, 'diffBreakdown', 'b')

    if units is None:
        units = ['years', 'months', 'days']

    total_days_diff = diffInDays(date_a, date_b)  # positive if a after b

    sign = 1 if total_days_diff == 0 else (1 if total_days_diff > 0 else -1)
    later = date_a if sign >= 0 else date_b
    earlier = date_b if sign >= 0 else date_a

    cursor = dict(earlier)
    result = {'sign': sign, 'totalDays': abs(total_days_diff)}

    if 'years' in units:
        years = 0
        while True:
            next_date = addYears(cursor, 1)
            if diffInDays(later, next_date) >= 0:
                years += 1
                cursor = next_date
            else:
                break
        result['years'] = years

    if 'months' in units:
        months = 0
        while True:
            next_date = addMonths(cursor, 1)
            if diffInDays(later, next_date) >= 0:
                months += 1
                cursor = next_date
            else:
                break
        result['months'] = months

    if 'days' in units:
        result['days'] = abs(diffInDays(later, cursor))

    return result