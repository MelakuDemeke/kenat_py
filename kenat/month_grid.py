from .kenat import Kenat
from . import holidays
from .geez_converter import to_geez
from .constants import DAYS_OF_WEEK, MONTH_NAMES
from .utils import get_weekday, validate_numeric_inputs
from .exceptions import InvalidGridConfigError

class MonthGrid:
    def __init__(self, config=None):
        if config is None:
            config = {}
        self._validate_config(config)

        current = Kenat.now()
        self.year = config.get('year', current.year)
        self.month = config.get('month', current.month)
        self.week_start = config.get('week_start', 1)
        self.use_geez = config.get('use_geez', False)
        self.weekday_lang = config.get('weekday_lang', 'amharic')
        self.holiday_filter = config.get('holiday_filter', None)

    def _validate_config(self, config):
        """Validates the configuration dictionary."""
        year = config.get('year')
        month = config.get('month')
        week_start = config.get('week_start')
        weekday_lang = config.get('weekday_lang')

        if (year is not None and month is None) or (year is None and month is not None):
            raise InvalidGridConfigError('If providing year or month, both must be provided.')
        if year is not None: validate_numeric_inputs('MonthGrid.constructor', year=year)
        if month is not None: validate_numeric_inputs('MonthGrid.constructor', month=month)
        if week_start is not None:
            validate_numeric_inputs('MonthGrid.constructor', week_start=week_start)
            if not 0 <= week_start <= 6: #
                raise InvalidGridConfigError(f"Invalid week_start value: {week_start}. Must be 0-6.")

        if weekday_lang is not None and weekday_lang not in DAYS_OF_WEEK:
            raise InvalidGridConfigError(f"Invalid weekday_lang: '{weekday_lang}'.")

    