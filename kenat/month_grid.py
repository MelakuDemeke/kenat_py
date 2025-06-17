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

    