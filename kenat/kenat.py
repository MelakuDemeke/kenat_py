import datetime
from .geez_converter import toGeez
from . import (
    conversions,
    holidays,
    day_arithmetic,
    formatting,
    bahire_hasab,
    utils
)
from .time import Time
from .exceptions import (
    UnrecognizedInputError,
    InvalidDateFormatError,
    InvalidEthiopianDateError,
    InvalidInputTypeError,
)

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
            self._ethiopian = conversions.toEC(today_greg.year, today_greg.month, today_greg.day)
            self._time = Time.from_gregorian(today_greg.hour, today_greg.minute)

        # From a datetime object
        elif isinstance(year, (datetime.datetime, datetime.date)):
            self._ethiopian = conversions.toEC(year.year, year.month, year.day)
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
        return conversions.toGC(self.year, self.month, self.day)

    # --- Information Methods ---
    def get_bahire_hasab(self, lang='amharic'):
        """Calculates and returns the Bahire Hasab values for the current instance's year.

        Note: unlike TS's Kenat.getBahireHasab() (which never plumbs a lang option
        through), this accepts an optional `lang` -- a harmless superset kept for
        backward compatibility with existing kenat_py consumers.
        """
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

    def get_date(self, calendar='ethiopian'):
        """
        Returns the date in whichever calendar is requested, so callers with a
        user-configurable calendar preference don't need an if/else between
        get_ethiopian() and get_gregorian() at every call site.
        """
        return self.get_gregorian() if calendar == 'gregorian' else self.get_ethiopian()

    def set_time(self, hour, minute, period):
        """Returns a new Kenat instance with the same date and the given time."""
        new_time = Time(hour, minute, period)
        return Kenat(year=dict(self._ethiopian), time_obj=new_time)

    def get_current_time(self):
        """Returns a Time object representing the current Ethiopian time."""
        now = datetime.datetime.now()
        return Time.from_gregorian(now.hour, now.minute)

    # --- Formatting Methods ---
    def format(self, options=None):
        """
        Formats the date according to the specified options.
        Options is a dict: {'calendar', 'lang', 'show_weekday', 'use_geez', 'include_time'}.

        'calendar' is 'ethiopian' (default) or 'gregorian'; when 'gregorian', the date
        is rendered using English Gregorian month names and use_geez is ignored.
        """
        if options is None:
            options = {}
        calendar = options.get('calendar', 'ethiopian')
        lang = options.get('lang', 'amharic')
        show_weekday = options.get('show_weekday', False)
        use_geez = options.get('use_geez', False)
        include_time = options.get('include_time', False)

        if calendar == 'gregorian':
            gregorian = self.get_gregorian()

            if show_weekday and include_time:
                weekday_str = formatting.format_gregorian_with_weekday(gregorian, lang)
                time_str = self._time.format(lang=lang, use_geez=False)
                return f"{weekday_str} {time_str}"

            if show_weekday:
                return formatting.format_gregorian_with_weekday(gregorian, lang)

            if include_time:
                return formatting.format_gregorian_with_time(gregorian, self._time, lang)

            return formatting.format_gregorian_standard(gregorian)

        if show_weekday and include_time:
            weekday_str = formatting.format_with_weekday(self._ethiopian, lang, use_geez)
            time_str = self._time.format(lang=lang, use_geez=use_geez)
            return f"{weekday_str} {time_str}"

        if show_weekday:
            return formatting.format_with_weekday(self._ethiopian, lang, use_geez)

        if include_time:
            return formatting.format_with_time(self._ethiopian, self._time, lang)

        if use_geez and lang == 'amharic':
            return formatting.format_in_geez_amharic(self._ethiopian)
        return formatting.format_standard(self._ethiopian, lang)

    def format_with_weekday(self, lang='amharic', use_geez=False):
        """Formats the Ethiopian date with weekday name, e.g. "ማክሰኞ, መስከረም 1 2016"."""
        return formatting.format_with_weekday(self._ethiopian, lang, use_geez)

    def format_short(self):
        """Returns the Ethiopian date in "yyyy/mm/dd" short format."""
        return formatting.format_short(self._ethiopian)

    def to_iso_string(self, calendar='ethiopian'):
        """
        Returns an ISO-style date string: "YYYY-MM-DD" or "YYYY-MM-DDTHH:mm".

        'gregorian' produces a genuine ISO 8601 string: the date is Gregorian and the
        time is converted from Kenat's Ethiopian 12-hour clock to Gregorian 24-hour
        time, with no non-standard suffix. The default 'ethiopian' calendar keeps the
        Ethiopian-date, Ethiopian-time, ISO-*like* string (including the non-standard
        "+12h" suffix for night times), unchanged for backward compatibility.
        """
        if calendar == 'gregorian':
            return formatting.to_gregorian_iso_date_string(self.get_gregorian(), self._time)
        return formatting.to_iso_date_string(self._ethiopian, self._time)

    def get_ethiopian(self):
        """Returns the Ethiopian date as a dictionary."""
        return self._ethiopian

    def get_gregorian(self):
        """Returns the Gregorian date as a dictionary, for test compatibility."""
        greg_date = self.to_gregorian_date()
        return {'year': greg_date.year, 'month': greg_date.month, 'day': greg_date.day}

    def to_string(self):
        """Returns a specific string format matching the original JS toString()."""
        # This format includes the default time.
        return formatting.format_with_time(self._ethiopian, self._time)

    def format_in_geez_amharic(self):
        """Formats the date with Amharic month and Geez numerals."""
        return formatting.format_in_geez_amharic(self._ethiopian)

    def print_this_month(self, use_geez=False):
        """Prints an ASCII calendar grid for the current Ethiopian month to stdout."""
        from .render import print_month_calendar_grid
        year, month = self.year, self.month
        calendar = self.get_month_calendar(year, month, use_geez)
        print_month_calendar_grid(year, month, calendar, use_geez)

    def is_before(self, other):
        """Checks if this date is before another Kenat instance."""
        if not isinstance(other, Kenat):
            raise TypeError("Can only compare with another Kenat instance.")
        return self.diff_in_days(other) < 0

    def is_after(self, other):
        """Checks if this date is after another Kenat instance."""
        if not isinstance(other, Kenat):
            raise TypeError("Can only compare with another Kenat instance.")
        return self.diff_in_days(other) > 0

    def is_same_day(self, other):
        """Checks if this date is the same as another Kenat instance."""
        if not isinstance(other, Kenat):
            return False
        return self.diff_in_days(other) == 0

    def is_same_month(self, other):
        """Checks if this date is in the same Ethiopian month and year as another."""
        if not isinstance(other, Kenat):
            return False
        return self.year == other.year and self.month == other.month

    def is_same_year(self, other):
        """Checks if this date is in the same Ethiopian year as another."""
        if not isinstance(other, Kenat):
            return False
        return self.year == other.year

    def start_of(self, unit):
        """Returns a new Kenat instance set to the start of the given unit ('day', 'month', 'year')."""
        if unit == 'day':
            result = Kenat(year=dict(self._ethiopian))
            result._time = Time(12, 0, 'day')
            return result
        if unit == 'month':
            result = Kenat(year=self.year, month=self.month, day=1)
            if self._time:
                result._time = self._time
            return result
        if unit == 'year':
            result = Kenat(year=self.year, month=1, day=1)
            if self._time:
                result._time = self._time
            return result
        raise ValueError(f"Invalid unit: {unit}. Use 'day', 'month', or 'year'")

    def end_of(self, unit):
        """Returns a new Kenat instance set to the end of the given unit ('day', 'month', 'year')."""
        if unit == 'day':
            result = Kenat(year=dict(self._ethiopian))
            result._time = Time(12, 0, 'night')
            return result
        if unit == 'month':
            last_day = utils.get_ethiopian_days_in_month(self.year, self.month)
            result = Kenat(year=self.year, month=self.month, day=last_day)
            if self._time:
                result._time = self._time
            return result
        if unit == 'year':
            last_day_of_pagume = utils.get_ethiopian_days_in_month(self.year, 13)
            result = Kenat(year=self.year, month=13, day=last_day_of_pagume)
            if self._time:
                result._time = self._time
            return result
        raise ValueError(f"Invalid unit: {unit}. Use 'day', 'month', or 'year'")

    def start_of_month(self):
        """Returns a new Kenat instance set to the first day of the current month."""
        return self.start_of('month')

    def end_of_month(self):
        """Returns a new Kenat instance set to the last day of the current month."""
        return self.end_of('month')

    def to_json(self):
        """Returns a plain dict representation of this Kenat instance for JSON serialization."""
        return {
            'ethiopian': dict(self._ethiopian),
            'gregorian': self.get_gregorian(),
            'time': (
                {'hour': self._time.hour, 'minute': self._time.minute, 'period': self._time.period}
                if self._time else None
            ),
        }

    # --- Arithmetic Methods ---
    def add(self, years=0, months=0, days=0):
        """Returns a new Kenat instance with the added duration, preserving time-of-day."""
        new_date = dict(self._ethiopian)
        if years:
            new_date = day_arithmetic.addYears(new_date, years)
        if months:
            new_date = day_arithmetic.addMonths(new_date, months)
        if days:
            new_date = day_arithmetic.addDays(new_date, days)
        return Kenat(year=new_date, time_obj=self._time)

    def subtract(self, years=0, months=0, days=0):
        """Returns a new Kenat instance with the duration subtracted. Mirror of add()."""
        return self.add(years=-years, months=-months, days=-days)

    def add_days(self, days):
        """Returns a new Kenat instance with the date advanced by `days`."""
        return self.add(days=days)

    def add_months(self, months):
        """Returns a new Kenat instance with the date advanced by `months`."""
        return self.add(months=months)

    def add_years(self, years):
        """Returns a new Kenat instance with the date advanced by `years`."""
        return self.add(years=years)

    def diff_in_days(self, other):
        """Calculates the difference in days between this and another Kenat instance."""
        return day_arithmetic.diffInDays(self._ethiopian, other._ethiopian)

    def diff_in_months(self, other):
        """Calculates the difference in months between this and another Kenat instance."""
        return day_arithmetic.diffInMonths(self._ethiopian, other._ethiopian)

    def diff_in_years(self, other):
        """Calculates the difference in years between this and another Kenat instance."""
        return day_arithmetic.diffInYears(self._ethiopian, other._ethiopian)

    # --- Distance helpers ---
    def distance_to(self, other, units=None, output='object', lang='english'):
        """
        Returns a breakdown of the distance from this date to another date.

        Args:
            other: Kenat | dict {'year','month','day'} | str | datetime.date/datetime
            units (list[str] | None): subset/order of ['years','months','days'].
            output (str): 'object' (default) or 'string'.
            lang (str): 'english' or 'amharic', used only when output == 'string'.
        """
        target = Kenat._coerce_to_kenat(other)
        if units is None:
            units = ['years', 'months', 'days']
        breakdown = day_arithmetic.diffBreakdown(target._ethiopian, self._ethiopian, units)
        if output == 'string':
            return Kenat.format_distance(breakdown, units=units, lang=lang)
        return breakdown

    def distance_from_today(self, units=None, output='object', lang='english'):
        """Returns a breakdown of the distance from today to this date."""
        today = Kenat()
        return today.distance_to(self, units=units, output=output, lang=lang)

    @staticmethod
    def distance_to_holiday(holiday_key, direction='auto', units=None, output='object', lang='english'):
        """Returns the distance from today to the given holiday's nearest occurrence."""
        today = Kenat()
        next_occurrence = Kenat._get_holiday_occurrence(holiday_key, today._ethiopian, 'next')
        prev_occurrence = Kenat._get_holiday_occurrence(holiday_key, today._ethiopian, 'prev')

        target = next_occurrence
        if direction == 'past':
            target = prev_occurrence
        if direction == 'auto':
            d_next = abs(day_arithmetic.diffInDays(next_occurrence._ethiopian, today._ethiopian))
            d_prev = abs(day_arithmetic.diffInDays(prev_occurrence._ethiopian, today._ethiopian))
            target = next_occurrence if d_next <= d_prev else prev_occurrence

        return today.distance_to(target, units=units, output=output, lang=lang)

    @staticmethod
    def format_distance(breakdown, units=None, lang='english'):
        """Formats a diff_breakdown() result to a human string like "1 year 2 months 5 days"."""
        if units is None:
            units = ['years', 'months', 'days']
        labels_en = {'years': 'year', 'months': 'month', 'days': 'day'}
        labels_am = {'years': 'ዓመት', 'months': 'ወር', 'days': 'ቀን'}
        labels = labels_am if lang == 'amharic' else labels_en

        def pluralize(n, key):
            if lang == 'amharic':
                return labels[key]
            return labels[key] if n == 1 else labels[key] + 's'

        parts = []
        if 'years' in units and 'years' in breakdown:
            parts.append(f"{breakdown['years']} {pluralize(breakdown['years'], 'years')}")
        if 'months' in units and 'months' in breakdown:
            parts.append(f"{breakdown['months']} {pluralize(breakdown['months'], 'months')}")
        if 'days' in units and 'days' in breakdown:
            parts.append(f"{breakdown['days']} {pluralize(breakdown['days'], 'days')}")

        if parts:
            return ' '.join(parts)
        return f"0 {pluralize(0, units[-1])}"

    # --- internal helpers ---
    @staticmethod
    def _coerce_to_kenat(value):
        if isinstance(value, Kenat):
            return value
        if isinstance(value, (datetime.datetime, datetime.date)):
            return Kenat(value)
        if isinstance(value, str):
            return Kenat(value)
        if isinstance(value, dict) and 'year' in value and 'month' in value and 'day' in value:
            return Kenat(value)
        raise ValueError('Unsupported date input')

    @staticmethod
    def _get_holiday_occurrence(holiday_key, ref_eth, which):
        this_year = holidays.get_holiday(holiday_key, ref_eth['year'])
        prev_year = holidays.get_holiday(holiday_key, ref_eth['year'] - 1)
        next_year = holidays.get_holiday(holiday_key, ref_eth['year'] + 1)
        candidates = [Kenat(h['ethiopian']) for h in (this_year, prev_year, next_year) if h]
        ref = Kenat(dict(ref_eth))

        def dist(candidate):
            return day_arithmetic.diffInDays(candidate._ethiopian, ref._ethiopian)

        sorted_by_abs_dist = sorted(candidates, key=lambda c: abs(dist(c)))

        if which == 'prev':
            past = [c for c in candidates if dist(c) <= 0]
            past.sort(key=lambda c: -abs(dist(c)))
            return past[0] if past else (sorted_by_abs_dist[0] if sorted_by_abs_dist else None)

        future = [c for c in candidates if dist(c) >= 0]
        future.sort(key=lambda c: abs(dist(c)))
        return future[0] if future else (sorted_by_abs_dist[0] if sorted_by_abs_dist else None)

    # --- Calendar Grid Generation ---
    @staticmethod
    def get_year_calendar(year, options=None):
        from .month_grid import MonthGrid
        """Generates a full-year calendar as a list of month objects."""
        if options is None: options = {}
        full_year = []
        for month in range(1, 14):
            # Create a MonthGrid for each month and append its data
            month_grid = MonthGrid.create(year=year, month=month, **options)
            full_year.append(month_grid)
        return full_year

    @staticmethod
    def get_month_calendar_grid(year, month, **options):
        """
        MonthGrid-backed calendar for a single month (holidays, saints, weekday
        headers, etc.), distinct from the instance method get_month_calendar()
        (which returns a plain per-day Ethiopian/Gregorian list without any of that
        enrichment). This is the Python counterpart of TS's static
        `Kenat.getMonthCalendar(year, month, options)`; it's under a different name
        here because Python doesn't support overloading a name between an instance
        method and a staticmethod on the same class the way TS/JS does.

        Returns {'month', 'month_name', 'year', 'headers', 'days'} where 'days' is
        the flat, start-padded array (matching MonthGrid.ts's shape), not the
        weeks-of-7 shape used by MonthGrid.generate()'s own 'days' key.
        """
        from .month_grid import MonthGrid
        grid = MonthGrid.create(year=year, month=month, **options)
        return {
            'month': month,
            'month_name': grid['month_name'],
            'year': grid['year'],
            'headers': grid['headers'],
            'days': grid['flat_days'],
        }

    @staticmethod
    def generate_date_range(start_date, end_date):
        """Generates a list of Kenat instances for a given inclusive date range."""
        if not isinstance(start_date, Kenat):
            raise InvalidInputTypeError('generateDateRange', 'startDate', 'Kenat instance', start_date)
        if not isinstance(end_date, Kenat):
            raise InvalidInputTypeError('generateDateRange', 'endDate', 'Kenat instance', end_date)

        if start_date.is_after(end_date):
            return []

        date_range = []
        current_date = start_date
        while current_date.is_before(end_date) or current_date.is_same_day(end_date):
            date_range.append(current_date)
            current_date = current_date.add_days(1)
        return date_range

    def get_month_calendar(self, year=None, month=None, use_geez=False):
        """
        Generates a simple calendar for a given month, mapping each Ethiopian day
        to its Gregorian equivalent, including display strings.
        """
        # These local imports are fine.
        from .constants import MONTH_NAMES
        from .geez_converter import toGeez
        from . import utils, conversions

        year = year or self.year
        month = month or self.month
        days_in_month = utils.get_ethiopian_days_in_month(year, month)
        calendar = []

        for day in range(1, days_in_month + 1):
            eth_date = {'year': year, 'month': month, 'day': day}
            greg_date = conversions.toGC(year, month, day) # This returns a datetime.date object

            ethiopian_display = ""
            if use_geez:
                ethiopian_display = f"{MONTH_NAMES['amharic'][month - 1]} {toGeez(day)} {toGeez(year)}"
            else:
                ethiopian_display = f"{MONTH_NAMES['amharic'][month - 1]} {day} {year}"

            # --- THIS IS THE FIX ---
            # Use dot notation (.year, .month, .day) for the datetime.date object
            gregorian_display = f"{greg_date.year}-{str(greg_date.month).zfill(2)}-{str(greg_date.day).zfill(2)}"

            eth_date['display'] = ethiopian_display

            # We need to create the greg_date dict for the return value
            greg_date_dict = {
                'year': greg_date.year,
                'month': greg_date.month,
                'day': greg_date.day,
                'display': gregorian_display
            }

            calendar.append({
                'ethiopian': eth_date,
                'gregorian': greg_date_dict,
            })
        return calendar

    # --- Python Special Methods ---
    def __str__(self):
        """Returns a user-friendly string representation."""
        return self.format({'lang': 'english'})

    def __repr__(self):
        """Returns an unambiguous string representation of the object."""
        return f"Kenat(year={self.year}, month={self.month}, day={self.day})"

    def __eq__(self, other):
        """Checks for date equality."""
        if not isinstance(other, Kenat):
            return NotImplemented
        return self._ethiopian == other._ethiopian

    def __lt__(self, other):
        """Checks if this date is before another."""
        if not isinstance(other, Kenat):
            return NotImplemented
        return self.diff_in_days(other) < 0

    def __gt__(self, other):
        """Checks if this date is after another."""
        if not isinstance(other, Kenat):
            return NotImplemented
        return self.diff_in_days(other) > 0
