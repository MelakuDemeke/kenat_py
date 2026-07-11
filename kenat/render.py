"""
Console ASCII calendar-grid printer, ported from kenat/src/render/printMonthCalendarGrid.ts.
"""
import datetime
from .constants import MONTH_NAMES
from .geez_converter import toGeez
from .utils import validate_numeric_inputs
from .exceptions import InvalidInputTypeError


def print_month_calendar_grid(ethiopian_year, ethiopian_month, calendar_data, use_geez=False):
    """
    Prints an ASCII calendar grid (Ethiopian day/Gregorian day pairs) for a month
    to stdout.

    Args:
        ethiopian_year (int)
        ethiopian_month (int): 1-13.
        calendar_data (list[dict]): as returned by Kenat.get_month_calendar(), i.e.
            a list of {'ethiopian': {'day': ...}, 'gregorian': {'year','month','day'}}.
        use_geez (bool): render Ethiopian day numbers in Geez numerals.
    """
    validate_numeric_inputs('printMonthCalendarGrid', ethiopianYear=ethiopian_year, ethiopianMonth=ethiopian_month)
    if ethiopian_month < 1 or ethiopian_month > 13:
        raise InvalidInputTypeError('printMonthCalendarGrid', 'ethiopianMonth', 'number between 1 and 13', ethiopian_month)
    if not isinstance(calendar_data, list) or len(calendar_data) == 0:
        # This function would have nothing to print if calendar_data is empty, so
        # just report the problem instead of crashing.
        print("Calendar data is empty or invalid. Cannot print grid.")
        return

    days_of_week = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    year_label = toGeez(ethiopian_year) if use_geez else ethiopian_year
    print(f"\n   {MONTH_NAMES['amharic'][ethiopian_month - 1]} {year_label}")
    print('  '.join(days_of_week))

    first_day_gregorian = calendar_data[0]['gregorian']
    js_date = datetime.date(first_day_gregorian['year'], first_day_gregorian['month'], first_day_gregorian['day'])
    # Python's weekday(): Monday=0..Sunday=6, which already matches "Monday is 0".
    week_day = js_date.weekday()

    row = ['    '] * week_day

    for day in calendar_data:
        eth_day = toGeez(day['ethiopian']['day']).rjust(2, '፩') if use_geez else str(day['ethiopian']['day']).rjust(2, ' ')
        greg_day = str(day['gregorian']['day']).rjust(2, ' ')
        row.append(f"{eth_day}/{greg_day}")

        if len(row) == 7:
            print(' '.join(row))
            row = []

    if len(row) > 0:
        print(' '.join(row).ljust(27, ' '))
