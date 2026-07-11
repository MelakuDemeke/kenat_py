from . import holidays
from .geez_converter import toGeez
from .constants import DAYS_OF_WEEK, MONTH_NAMES, HolidayTags, HOLIDAY_INFO
from .utils import get_weekday, validate_numeric_inputs
from .exceptions import InvalidGridConfigError

class MonthGrid:
    def __init__(self, config=None):
        from .kenat import Kenat
        if config is None:
            config = {}
        self._validate_config(config)

        current = Kenat.now()
        current_eth = current._ethiopian
        self.year = config.get('year', current_eth['year'])
        self.month = config.get('month', current_eth['month'])
        self.week_start = config.get('week_start', 1)
        self.use_geez = config.get('use_geez', False)
        self.weekday_lang = config.get('weekday_lang', 'amharic')
        self.holiday_filter = config.get('holiday_filter', None)
        # 'christian' | 'muslim' | 'public' | None. Drives holiday-tag filtering and,
        # for 'christian', attaches nigs.json saints/commemorations; for 'muslim',
        # injects a weekly Jummah (Friday prayer) entry.
        self.mode = config.get('mode', None)
        # When True (and mode == 'christian'), attach every saint/commemoration entry
        # for each day-of-month regardless of whether this month is one of its `negs`
        # (major-feast) months.
        self.show_all_saints = config.get('show_all_saints', False)

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

    @classmethod
    def create(cls, year=None, month=None, **options):
        """
        Creates an instance and generates the grid in one call. `year`/`month` are
        optional -- when omitted, both default to the current Ethiopian date (they
        must either both be provided or both be omitted).
        """
        config = dict(options)
        if year is not None:
            config['year'] = year
        if month is not None:
            config['month'] = month
        instance = cls(config)
        return instance.generate()

    def _get_filtered_holidays(self, year, month):
        """Resolves the effective holiday filter (mode overrides an explicit
        holiday_filter) and fetches the month's holidays."""
        filter_by = self.holiday_filter
        if self.mode == 'christian':
            filter_by = [HolidayTags.CHRISTIAN]
        elif self.mode == 'muslim':
            filter_by = [HolidayTags.MUSLIM]
        elif self.mode == 'public':
            filter_by = [HolidayTags.PUBLIC]
        return holidays.get_holidays_in_month(year, month, lang=self.weekday_lang, filter_by=filter_by)

    def _get_saints_map(self):
        """Builds a {day: [entry, ...]} map of nigs.json saints/commemorations for
        this grid's month, gated by mode == 'christian'. An entry is included if
        this.month is one of its `negs` (major-feast) months, or if show_all_saints
        is True. Tags entries as NIGS (major-feast match) or SAINT_DAY (shown only
        because show_all_saints is set)."""
        if self.mode != 'christian':
            return {}

        from .saints import get_orthodox_days_by_day
        day_entries = get_orthodox_days_by_day()

        result = {}
        for day_str, entries in day_entries.items():
            day = int(day_str)
            for entry in entries:
                is_nigs = self.month in entry.get('negs', [])
                if not is_nigs and not self.show_all_saints:
                    continue

                result.setdefault(day, []).append({
                    'key': entry['id'],
                    'name': entry['name'].get(self.weekday_lang) or entry['name'].get('english'),
                    'description': entry['description'].get(self.weekday_lang) or entry['description'].get('english'),
                    'isNigs': is_nigs,
                    'tags': [HolidayTags.RELIGIOUS, HolidayTags.CHRISTIAN, 'NIGS' if is_nigs else 'SAINT_DAY'],
                })
        return result

    def generate(self):
        """Generates and returns the structured month grid."""
        from .kenat import Kenat
        y, m = self.year, self.month
        today_eth = Kenat.now()._ethiopian

        # Get the raw list of days for the month
        temp = Kenat(year=y, month=m, day=1)
        raw_days = temp.get_month_calendar(y, m, self.use_geez)

        # Get language-specific labels
        labels = DAYS_OF_WEEK.get(self.weekday_lang, DAYS_OF_WEEK['amharic'])
        month_labels = MONTH_NAMES.get(self.weekday_lang, MONTH_NAMES['amharic'])

        # Fetch holidays (respecting mode) and map them by day for quick lookup
        month_holidays = self._get_filtered_holidays(y, m)
        holiday_map = {}
        for h in month_holidays:
            day_key = h['ethiopian']['day']
            if day_key not in holiday_map: holiday_map[day_key] = []
            holiday_map[day_key].append(h)

        saints_map = self._get_saints_map()

        # Enrich each day with additional information
        days_with_weekday = []
        for day_data in raw_days:
            eth = day_data['ethiopian']
            is_today = (eth['year'] == today_eth['year'] and
                        eth['month'] == today_eth['month'] and
                        eth['day'] == today_eth['day'])
            weekday = get_weekday(eth)

            day_holidays = list(holiday_map.get(eth['day'], []))
            if self.mode == 'christian':
                day_holidays = day_holidays + saints_map.get(eth['day'], [])
            if self.mode == 'muslim' and weekday == 5:
                jummah = HOLIDAY_INFO['jummah']
                day_holidays.append({
                    'key': 'jummah',
                    'name': jummah['name'].get(self.weekday_lang) or jummah['name'].get('english'),
                    'description': jummah['description'].get(self.weekday_lang) or jummah['description'].get('english'),
                    'tags': [HolidayTags.RELIGIOUS, HolidayTags.MUSLIM],
                })

            days_with_weekday.append({
                'ethiopian': {
                    'year': toGeez(eth['year']) if self.use_geez else eth['year'],
                    'month': month_labels[eth['month'] - 1],
                    'day': toGeez(eth['day']) if self.use_geez else eth['day']
                },
                'gregorian': day_data['gregorian'],
                'weekday': weekday,
                'weekday_name': labels[weekday],
                'is_today': is_today,
                'holidays': day_holidays
            })

        # Pad the beginning of the list with 'None' for empty days
        offset = (days_with_weekday[0]['weekday'] - self.week_start + 7) % 7
        padded_days = ([None] * offset) + days_with_weekday

        # Also pad the end so the last week is a full 7 entries (kept as an addition
        # on top of the existing weeks-of-7 'days' shape; the flat, TS-equivalent
        # 'flat_days' below is start-padded only, matching MonthGrid.ts exactly).
        trailing = len(padded_days) % 7
        end_padding = (7 - trailing) % 7
        fully_padded = padded_days + ([None] * end_padding)

        # Reorder headers based on week_start
        headers = labels[self.week_start:] + labels[:self.week_start]

        # Structure the final output
        return {
            'headers': headers,
            'days': [fully_padded[i:i + 7] for i in range(0, len(fully_padded), 7)],
            'flat_days': padded_days,
            'year': toGeez(self.year) if self.use_geez else self.year,
            'month': self.month,
            'month_name': month_labels[self.month - 1]
        }

    def up(self):
        """Returns a new MonthGrid configured for the next Ethiopian month."""
        new_year, new_month = self.year, self.month
        if new_month == 13:
            new_month = 1
            new_year += 1
        else:
            new_month += 1
        return self._with(year=new_year, month=new_month)

    def down(self):
        """Returns a new MonthGrid configured for the previous Ethiopian month."""
        new_year, new_month = self.year, self.month
        if new_month == 1:
            new_month = 13
            new_year -= 1
        else:
            new_month -= 1
        return self._with(year=new_year, month=new_month)

    def _with(self, year, month):
        return MonthGrid({
            'year': year,
            'month': month,
            'week_start': self.week_start,
            'use_geez': self.use_geez,
            'weekday_lang': self.weekday_lang,
            'holiday_filter': self.holiday_filter,
            'mode': self.mode,
            'show_all_saints': self.show_all_saints,
        })
