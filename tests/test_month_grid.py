import pytest
from kenat.month_grid import MonthGrid
from kenat.exceptions import InvalidGridConfigError

# A mock version of get_weekday that is predictable for testing
# It returns 0 for day 1, 1 for day 2, etc.
def mock_get_weekday(eth_date):
    return (eth_date['day'] - 1) % 7

@pytest.fixture
def mock_kenat_dependencies(mocker):
    """A pytest fixture to mock all external dependencies for MonthGrid."""
    
    # 1. Create a mock object that will be the return value of Kenat.now()
    mock_now_instance = mocker.MagicMock()
    
    # 2. Set the desired attribute on this mock object
    mock_now_instance._ethiopian = {'year': 2016, 'month': 9, 'day': 10}
    
    # 3. Patch Kenat.now WHERE IT LIVES (in kenat.kenat)
    mocker.patch('kenat.kenat.Kenat.now', return_value=mock_now_instance)

    # Mock the calendar data to return a predictable list of 5 days
    mock_calendar_data = [
        {'ethiopian': {'year': 2016, 'month': 9, 'day': d}, 'gregorian': {}}
        for d in range(8, 13) # Days 8, 9, 10, 11, 12
    ]
    # Also patch get_month_calendar WHERE IT LIVES
    mocker.patch(
        'kenat.kenat.Kenat.get_month_calendar',
        return_value=mock_calendar_data
    )
    
    # These other mocks are correct because they are looked up from within the month_grid module
    mocker.patch('kenat.month_grid.holidays.get_holidays_in_month', return_value=[])
    mocker.patch('kenat.month_grid.get_weekday', side_effect=mock_get_weekday)


class TestMonthGrid:
    """Tests the MonthGrid class."""

    def test_returns_valid_grid_structure(self, mock_kenat_dependencies):
        """Tests that the create method returns a grid with the correct shape."""
        grid = MonthGrid.create(year=2016, month=9)
        assert 'headers' in grid
        assert 'days' in grid
        assert isinstance(grid['headers'], list)
        assert isinstance(grid['days'], list)
        assert len(grid['headers']) == 7

    def test_flags_today_correctly(self, mock_kenat_dependencies):
        """Tests that the correct day is marked with is_today=True."""
        grid = MonthGrid.create(year=2016, month=9)
        
        # Flatten the list of days and find the one marked as "today"
        all_days = [day for week in grid['days'] for day in week if day]
        today_obj = next((d for d in all_days if d.get('is_today')), None)
        
        assert today_obj is not None
        # Our mock "today" is day 10, which is in our mock calendar data
        assert today_obj['ethiopian']['day'] == 10

    def test_accepts_object_input_and_custom_week_start(self, mock_kenat_dependencies):
        """
        Tests custom options like week_start and weekday_lang.
        NOTE: In our library, week starts on Sunday (0). Monday is 1.
        """
        grid = MonthGrid.create(
            year=2016, month=9, week_start=1, weekday_lang='english'
        )
        assert grid['headers'][0] == 'Monday'
        
        # The first day in our mock data is day 8.
        # mock_get_weekday(day=8) returns (8-1)%7 = 0 (Sunday).
        # Since week starts on Monday, the offset is (0 - 1 + 7) % 7 = 6.
        # The first day should be at the end of the first week.
        first_day_obj = grid['days'][0][6] 
        assert first_day_obj['weekday_name'] == 'Sunday'

    def test_pads_days_array_correctly(self, mock_kenat_dependencies):
        """Tests that padding changes based on weekStart."""
        # First day of mock data has weekday 0.
        # With week_start=0 (Sunday), offset is (0 - 0 + 7) % 7 = 0. No padding.
        grid_sun_start = MonthGrid.create(year=2016, month=9, week_start=0)
        offset_sun = next(i for i, d in enumerate(grid_sun_start['days'][0]) if d is not None)
        assert offset_sun == 0

        # With week_start=1 (Monday), offset is (0 - 1 + 7) % 7 = 6. 6 padding days.
        grid_mon_start = MonthGrid.create(year=2016, month=9, week_start=1)
        offset_mon = next(i for i, d in enumerate(grid_mon_start['days'][0]) if d is not None)
        assert offset_mon == 6
    
    def test_throws_error_for_invalid_config(self):
        """
        Tests that the constructor validates its input.
        This replaces the "invalid string" test from JS, as our constructor is stricter.
        """
        # Should fail if only year is provided without month
        with pytest.raises(InvalidGridConfigError):
            # We test the constructor directly, not the create method
            MonthGrid(config={'year': 2016})

        # Should fail if week_start is out of range
        with pytest.raises(InvalidGridConfigError):
            MonthGrid(config={'year': 2016, 'month': 9, 'week_start': 7})

    def test_flat_days_is_start_padded_only(self, mock_kenat_dependencies):
        """flat_days mirrors MonthGrid.ts's shape: a flat list, padded with None only
        at the start (unlike 'days', which is also end-padded to full weeks)."""
        grid = MonthGrid.create(year=2016, month=9, week_start=1)
        assert 'flat_days' in grid
        assert isinstance(grid['flat_days'], list)
        # 6 leading None entries (per test_pads_days_array_correctly) + 5 mock days.
        assert grid['flat_days'][:6] == [None] * 6
        assert len(grid['flat_days']) == 11
        assert grid['flat_days'][-1] is not None

    def test_days_shape_is_end_padded_to_full_weeks(self, mock_kenat_dependencies):
        grid = MonthGrid.create(year=2016, month=9, week_start=1)
        for week in grid['days']:
            assert len(week) == 7

    def test_create_with_no_args_uses_current_ethiopian_date(self, mock_kenat_dependencies):
        # mock_now_instance._ethiopian is {'year': 2016, 'month': 9, 'day': 10}.
        grid = MonthGrid.create()
        assert grid['year'] == 2016
        assert grid['month'] == 9


class TestMonthGridModes:
    """Tests mode ('christian'/'muslim'/'public') and show_all_saints, using the
    real (unmocked) holidays/nigs.json data for a known Ethiopian year/month."""

    def test_christian_mode_attaches_nigs_saints_gated_by_month(self):
        # Meskerem (month 1) day 1 -> 'ledeta_mariam' declares negs: [9] in nigs.json,
        # so it should NOT show up as a NIGS entry for month 1 unless show_all_saints.
        grid_month1 = MonthGrid.create(year=2016, month=1, mode='christian')
        flat = [d for d in grid_month1['flat_days'] if d]
        day1 = next(d for d in flat if d['ethiopian']['day'] == 1)
        nigs_keys = [h['key'] for h in day1['holidays'] if h.get('isNigs')]
        assert 'ledeta_mariam' not in nigs_keys

        # Genbot (month 9) day 1 -> negs includes 9, so it should show as NIGS.
        grid_month9 = MonthGrid.create(year=2016, month=9, mode='christian')
        flat9 = [d for d in grid_month9['flat_days'] if d]
        day1_m9 = next(d for d in flat9 if d['ethiopian']['day'] == 1)
        nigs_entry = next(h for h in day1_m9['holidays'] if h['key'] == 'ledeta_mariam')
        assert nigs_entry['isNigs'] is True
        assert 'NIGS' in nigs_entry['tags']

    def test_show_all_saints_attaches_entries_regardless_of_month_match(self):
        grid = MonthGrid.create(year=2016, month=1, mode='christian', show_all_saints=True)
        flat = [d for d in grid['flat_days'] if d]
        day1 = next(d for d in flat if d['ethiopian']['day'] == 1)
        entry = next(h for h in day1['holidays'] if h['key'] == 'ledeta_mariam')
        # Shown because show_all_saints=True, not because month 1 is in its negs.
        assert entry['isNigs'] is False
        assert 'SAINT_DAY' in entry['tags']

    def test_saints_are_absent_without_christian_mode(self):
        grid = MonthGrid.create(year=2016, month=9)  # mode defaults to None
        flat = [d for d in grid['flat_days'] if d]
        day1 = next(d for d in flat if d['ethiopian']['day'] == 1)
        assert all(h['key'] != 'ledeta_mariam' for h in day1['holidays'])

    def test_muslim_mode_injects_jummah_on_fridays(self):
        grid = MonthGrid.create(year=2016, month=1, mode='muslim')
        flat = [d for d in grid['flat_days'] if d]
        fridays = [d for d in flat if d['weekday'] == 5]
        assert len(fridays) > 0
        for friday in fridays:
            assert any(h['key'] == 'jummah' for h in friday['holidays'])
        non_fridays = [d for d in flat if d['weekday'] != 5]
        assert all(all(h['key'] != 'jummah' for h in d['holidays']) for d in non_fridays)

    def test_public_mode_filters_to_public_holidays_only(self):
        grid = MonthGrid.create(year=2016, month=1, mode='public')
        flat = [d for d in grid['flat_days'] if d]
        all_tags = [tag for d in flat for h in d['holidays'] for tag in h.get('tags', [])]
        # Every holiday entry present should carry the 'public' tag.
        for d in flat:
            for h in d['holidays']:
                assert 'public' in h.get('tags', [])


class TestMonthGridNavigation:
    def test_up_advances_one_month(self):
        grid_instance = MonthGrid({'year': 2016, 'month': 9})
        next_grid = grid_instance.up()
        assert (next_grid.year, next_grid.month) == (2016, 10)

    def test_up_rolls_over_pagume_into_new_year(self):
        grid_instance = MonthGrid({'year': 2016, 'month': 13})
        next_grid = grid_instance.up()
        assert (next_grid.year, next_grid.month) == (2017, 1)

    def test_down_retreats_one_month(self):
        grid_instance = MonthGrid({'year': 2016, 'month': 9})
        prev_grid = grid_instance.down()
        assert (prev_grid.year, prev_grid.month) == (2016, 8)

    def test_down_rolls_back_across_year_boundary(self):
        grid_instance = MonthGrid({'year': 2016, 'month': 1})
        prev_grid = grid_instance.down()
        assert (prev_grid.year, prev_grid.month) == (2015, 13)

    def test_up_returns_new_monthgrid_instance_not_mutated_self(self):
        grid_instance = MonthGrid({'year': 2016, 'month': 9})
        next_grid = grid_instance.up()
        assert next_grid is not grid_instance
        assert grid_instance.month == 9  # original untouched

    def test_up_and_down_are_generatable(self):
        grid_instance = MonthGrid({'year': 2016, 'month': 9})
        generated = grid_instance.up().generate()
        assert generated['month'] == 10