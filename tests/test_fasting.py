import pytest
from kenat.fasting import get_fasting_period, get_fasting_info, get_fasting_days, is_tsome_dihnet_fast_day
from kenat.constants import FastingKeys
from kenat.bahire_hasab import getBahireHasab
from kenat.day_arithmetic import addDays
from kenat.utils import get_weekday, get_ethiopian_days_in_month


class TestGetFastingPeriodChristianFasts2016:
    """Mirrors kenat/tests/fasting.test.ts's 'Christian Fasts for 2016 E.C.' block."""
    year = 2016

    def test_great_lent_abiy_tsome(self):
        period = get_fasting_period(FastingKeys.ABIY_TSOME, self.year)
        assert period['start'] == {'year': 2016, 'month': 7, 'day': 2}
        assert period['end'] == {'year': 2016, 'month': 8, 'day': 25}

    def test_apostles_fast_tsome_hawaryat(self):
        period = get_fasting_period(FastingKeys.TSOME_HAWARYAT, self.year)
        assert period['end'] == {'year': 2016, 'month': 11, 'day': 4}

    def test_fast_of_nineveh(self):
        period = get_fasting_period(FastingKeys.NINEVEH, self.year)
        assert period['start'] == {'year': 2016, 'month': 6, 'day': 18}
        assert period['end'] == {'year': 2016, 'month': 6, 'day': 20}

    def test_fast_of_the_prophets(self):
        period = get_fasting_period(FastingKeys.TSOME_NEBIYAT, self.year)
        assert period['start'] == {'year': 2016, 'month': 3, 'day': 15}
        assert period['end'] == {'year': 2016, 'month': 4, 'day': 28}


class TestGetFastingPeriodEdgeCases:
    def test_unknown_fast_key_returns_none(self):
        assert get_fasting_period('UNKNOWN_FAST_KEY', 2016) is None

    def test_future_year_does_not_crash(self):
        period = get_fasting_period(FastingKeys.ABIY_TSOME, 2020)
        assert period is not None
        assert period['start'] is not None
        assert period['end'] is not None


class TestGetFastingInfo:
    year = 2016

    def test_abiy_tsome_multilingual_info(self):
        info_am = get_fasting_info(FastingKeys.ABIY_TSOME, self.year, lang='amharic')
        assert info_am is not None
        assert info_am['key'] == FastingKeys.ABIY_TSOME
        assert info_am['name'] == 'ዐቢይ ጾም (ሁዳዴ)'
        assert info_am['description']
        assert info_am['period']['start'] == {'year': 2016, 'month': 7, 'day': 2}

        info_en = get_fasting_info(FastingKeys.ABIY_TSOME, self.year, lang='english')
        assert 'Great Lent' in info_en['name']
        assert info_en['period']['end'] == {'year': 2016, 'month': 8, 'day': 25}

    def test_nineveh_three_day_period(self):
        info = get_fasting_info(FastingKeys.NINEVEH, self.year)
        assert info['name'] == 'ጾመ ነነዌ'
        assert info['period']['start'] == {'year': 2016, 'month': 6, 'day': 18}
        assert info['period']['end'] == {'year': 2016, 'month': 6, 'day': 20}

    def test_ramadan_info_includes_tags(self):
        info = get_fasting_info(FastingKeys.RAMADAN, self.year, lang='english')
        assert info['name'] == 'Ramadan'
        assert isinstance(info['tags'], list)
        assert info['period']['start'] is not None

    def test_filseta_fixed_period(self):
        info = get_fasting_info(FastingKeys.FILSETA, self.year, lang='amharic')
        assert info is not None
        assert info['key'] == FastingKeys.FILSETA
        assert info['name'] == 'ፍልሰታ'
        assert info['period']['start'] == {'year': 2016, 'month': 12, 'day': 1}
        assert info['period']['end'] == {'year': 2016, 'month': 12, 'day': 14}

    def test_tsome_dihenet_has_no_contiguous_period(self):
        info = get_fasting_info(FastingKeys.TSOME_DIHENET, self.year)
        assert info is not None
        assert info['period'] is None


class TestOrthodoxWeeklyFasting:
    """Mirrors kenat/tests/fasting.test.ts's 'Orthodox Weekly Fasting (Tsome Dihnet)' block."""

    def test_wednesdays_and_fridays_are_fasting_days_outside_easter_season(self):
        year = 2016
        month = 3  # Hidar: well before Easter season.
        days_in_month = get_ethiopian_days_in_month(year, month)
        days = get_fasting_days('TSOME_DIHENET', year, month)

        found_wed = False
        found_fri = False
        for day in range(1, days_in_month + 1):
            date = {'year': year, 'month': month, 'day': day}
            wd = get_weekday(date)
            if wd == 3:
                found_wed = True
                assert day in days
            if wd == 5:
                found_fri = True
                assert day in days
        assert found_wed or found_fri

    def test_no_fasting_during_the_50_days_after_easter_through_pentecost(self):
        year = 2016
        bh = getBahireHasab(year)
        easter = bh['movableFeasts']['fasika']['ethiopian']
        pentecost = bh['movableFeasts']['paraclete']['ethiopian']

        d = addDays(easter, 1)
        # Bound the loop defensively (the real window is ~49 days).
        for _ in range(60):
            wd = get_weekday(d)
            if wd in (3, 5):
                day_list = get_fasting_days('TSOME_DIHENET', d['year'], d['month'])
                assert d['day'] not in day_list
                assert is_tsome_dihnet_fast_day(d) is False
            if (d['year'], d['month'], d['day']) == (pentecost['year'], pentecost['month'], pentecost['day']):
                break
            d = addDays(d, 1)

    def test_fasting_resumes_on_wed_fri_after_pentecost(self):
        year = 2016
        bh = getBahireHasab(year)
        pentecost = bh['movableFeasts']['paraclete']['ethiopian']

        found = False
        for i in range(1, 22):
            d = addDays(pentecost, i)
            wd = get_weekday(d)
            if wd in (3, 5):
                day_list = get_fasting_days('TSOME_DIHENET', d['year'], d['month'])
                assert d['day'] in day_list
                assert is_tsome_dihnet_fast_day(d) is True
                found = True
                break
        assert found
