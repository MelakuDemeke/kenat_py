import datetime
from . import (
    conversions,
    holidays,
    day_arithmetic,
    formatting,
    bahire_hasab,
    utils
)
from .time import Time
# from .month_grid import MonthGrid
from .exceptions import UnrecognizedInputError, InvalidDateFormatError, InvalidEthiopianDateError

class Kenat:
    """
    A class to represent and manipulate Ethiopian calendar dates. It serves as
    a wrapper for an Ethiopian date, providing conversion, formatting, and
    arithmetic functionalities.
    """
    def __init__(self, year=None, month=None, day=None, time_obj=None):
        """
        Constructs a Kenat instance. Can be initialized with:
         - An Ethiopian date string (e.g., '2016/1/1', '2016-1-1'). 
         - A dictionary with {'year', 'month', 'day'}. 
         - A native Python datetime.date or datetime.datetime object. 
         - No arguments, for the current date. 
         - Year, month, day as separate integer arguments.
        """
        # Default to current date and time if no input is provided 
        if year is None:
            today_greg = datetime.datetime.now()
            self._ethiopian = conversions.to_ec(today_greg.year, today_greg.month, today_greg.day)
            self._time = Time.from_gregorian(today_greg.hour, today_greg.minute)
        
        # From a datetime object 
        elif isinstance(year, (datetime.datetime, datetime.date)):
            self._ethiopian = conversions.to_ec(year.year, year.month, year.day)
            self._time = Time.from_gregorian(year.hour, year.minute) if isinstance(year, datetime.datetime) else Time(12, 0, 'day')

        # From a dictionary {'year', 'month', 'day'} 
        elif isinstance(year, dict):
            self._ethiopian = year
            self._time = time_obj if isinstance(time_obj, Time) else Time(12, 0, 'day')

        # From a string 'YYYY/MM/DD' or 'YYYY-MM-DD' 
        elif isinstance(year, str):
            try:
                parts = list(map(int, year.replace('/', '-').split('-')))
                self._ethiopian = {'year': parts[0], 'month': parts[1], 'day': parts[2]}
                self._time = time_obj if isinstance(time_obj, Time) else Time(12, 0, 'day')
            except (ValueError, IndexError):
                raise InvalidDateFormatError(year)
        
        # From year, month, day integers
        elif isinstance(year, int) and month is not None and day is not None:
            self._ethiopian = {'year': year, 'month': month, 'day': day}
            self._time = time_obj if isinstance(time_obj, Time) else Time(12, 0, 'day')
            
        else:
            raise UnrecognizedInputError(year)

        # Final validation
        if not utils.is_valid_ethiopian_date(self.year, self.month, self.day):
            raise InvalidEthiopianDateError(self.year, self.month, self.day)

    