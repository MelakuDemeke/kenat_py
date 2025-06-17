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

    @classmethod
    def now(cls):
        """Creates and returns a new Kenat instance for the current date and time."""
        return cls()

    # --- Properties ---
    @property
    def year(self):
        return self._ethiopian['year']

    @property
    def month(self):
        return self._ethiopian['month']
        
    @property
    def day(self):
        return self._ethiopian['day']

    @property
    def time(self):
        return self._time
        
    def to_gregorian_date(self):
        """Returns the Gregorian date as a Python datetime.date object."""
        return conversions.to_gc(self.year, self.month, self.day)

    # --- Information Methods ---
    def get_bahire_hasab(self, lang='amharic'):
        """Calculates and returns the Bahire Hasab values for the current instance's year."""
        return bahire_hasab.get_bahire_hasab(self.year, lang)

    def is_holiday(self, lang='amharic'):
        """Checks if the current date is a holiday and returns a list of holiday objects if it is."""
        holidays_in_month = holidays.get_holidays_in_month(self.year, self.month, lang) 
        return [h for h in holidays_in_month if h['ethiopian']['day'] == self.day]

    def is_leap_year(self):
        """Checks if the current Ethiopian year is a leap year."""
        return utils.is_ethiopian_leap_year(self.year)

    def weekday(self):
        """Returns the weekday number (0 for Sunday, 6 for Saturday)."""
        return utils.get_weekday(self._ethiopian)

    # --- Formatting Methods ---
    def format(self, options=None):
        """
        Formats the Ethiopian date according to the specified options.
        Options is a dict: {'lang', 'show_weekday', 'use_geez', 'include_time'}
        """
        if options is None:
            options = {}
        lang = options.get('lang', 'amharic')
        show_weekday = options.get('show_weekday', False)
        use_geez = options.get('use_geez', False)
        include_time = options.get('include_time', False)

        if use_geez:
             return formatting.format_in_geez_amharic(self._ethiopian)
        if show_weekday:
            return formatting.format_with_weekday(self._ethiopian, lang)
        if include_time:
            return formatting.format_with_time(self._ethiopian, self._time, lang)
        
        return formatting.format_standard(self._ethiopian, lang)

    