# Kenat / ቀናት [![PyPI Version](https://img.shields.io/pypi/v/kenat)](https://pypi.org/project/kenat/)

![banner](https://raw.githubusercontent.com/MelakuDemeke/kenat_py/master/assets/img/py_banner.png)

![GitHub issues](https://img.shields.io/github/issues/MelakuDemeke/kenat_py)
![GitHub Repo stars](https://img.shields.io/github/stars/MelakuDemeke/kenat_py?logo=github&style=flat)
![GitHub forks](https://img.shields.io/github/forks/MelakuDemeke/kenat_py?logo=github&style=falt)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/MelakuDemeke/kenat_py?logo=github)


**A complete Ethiopian Calendar & Bahire Hasab toolkit for Python**

---

## 📌 Overview

**Kenat** (Amharic: ቀናት) is a powerful and authentic Ethiopian calendar library for Python. It offers full support for date conversion, holiday computation (including Bahire Hasab), localized formatting, Geez numerals, and more — all without external dependencies.

> 🚀 Ported from the original [kenat JS library](https://github.com/MelakuDemeke/kenat).

---

## ✨ Features

* 🔄 **Bidirectional Conversion**: Ethiopian ↔ Gregorian calendars
* 📅 **Full Holiday System**: Christian, Muslim, cultural, and public holidays
* ⛪ **Bahire Hasab**: Accurate movable feast calculations (e.g. Fasika, Tsome Nebiyat)
* 🙏 **Fasting Periods**: Abiy Tsome, Nineveh, Tsome Nebiyat, Filseta, Tsome Hawaryat, Tsome Dihnet, Ramadan
* 🏛️ **Orthodox Saints (Nigs)**: Monthly commemoration/saints-day data for calendar grids
* 🏷️ **Holiday Filtering**: Filter holidays by type (`public`, `christian`, `muslim`, etc.)
* 📆 **Date Arithmetic**: Add/subtract days, months, years (13-month calendar support)
* 📏 **Date Difference & Distance**: Precise diffs plus human-friendly "distance to date/holiday" strings
* 🌐 **Calendar Preference**: Render dates in Ethiopian or Gregorian on demand
* 🔠 **Localized Formatting**: Amharic and English support
* 🔢 **Geez Numerals**: Convert integers to ግዕዝ numeral strings
* ⏰ **Ethiopian Time Support**: 12-hour Ethiopian ↔ 24-hour Gregorian
* 🗓️ **Calendar Grids**: Monthly/yearly calendar generation, with holiday/saint overlays and console printing
* 🧾 **Serialization**: `to_json()` for clean `Kenat` → dict/JSON output
* ⚠️ **Structured Errors**: Typed exceptions with `to_json()` for consistent error handling

---

## 🚀 Installation

Install the library from source:

```bash
pip install kenat
```

For development/testing:

```bash
pip install -e ".[test]"
```

---

## 🟢 Quick Start

```python
from kenat import Kenat

today = Kenat.now()

print(today.get_ethiopian())
# → {'year': 2017, 'month': 9, 'day': 26}

print(today.format({'lang': 'english', 'show_weekday': True}))
# → "Tuesday, Ginbot 26 2017"
```

---

## ⛪ Bahire Hasab & Holiday System

### Get All Holidays in a Year

```python
from kenat import get_holidays_for_year

holidays = get_holidays_for_year(2017)

# Example: Find Fasika (Easter)
fasika = next(h for h in holidays if h['key'] == 'fasika')
print(fasika['ethiopian'])  # → {'year': 2017, 'month': 8, 'day': 21}
```

### Filter Holidays by Type

```python
from kenat import get_holidays_for_year, HolidayTags

# Public only
get_holidays_for_year(2017, filter_by=HolidayTags.PUBLIC)

# Christian and Muslim holidays
get_holidays_for_year(2017, filter_by=[HolidayTags.CHRISTIAN, HolidayTags.MUSLIM])
```

### Check if a Date is a Holiday

```python
from kenat import Kenat

meskel = Kenat("2017/1/17")
print(meskel.is_holiday())  # → [Holiday object]

non_holiday = Kenat("2017/1/18")
print(non_holiday.is_holiday())  # → []
```

### Access Bahire Hasab Calculations

```python
from kenat import Kenat

bh = Kenat("2017/1/1").get_bahire_hasab()

print(bh['evangelist'])  # → {'name': 'ማቴዎስ', 'remainder': 1}
print(bh['movableFeasts']['fasika']['ethiopian'])
# → {'year': 2017, 'month': 8, 'day': 21}
```

---

## ➕ More API Examples

### Date Arithmetic

```python
from kenat import Kenat

date = Kenat("2017/2/10")
print(date.add(days=10))     # → Add days
print(date.add(months=-1))   # → Subtract a month
print(date.subtract(years=1))

# Single-unit convenience wrappers
print(date.add_days(7))
print(date.add_months(2))
print(date.add_years(1))
```

### Comparing Dates

```python
a = Kenat("2016/1/1")
b = Kenat("2016/2/5")

a.is_before(b)     # → True
b.is_after(a)      # → True
a.is_same_day(a)   # → True
a.is_same_month(b) # → False
a.is_same_year(b)  # → True
```

### Start / End of a Period

```python
date = Kenat("2016/5/15")

date.start_of_month().get_ethiopian()  # → {'year': 2016, 'month': 5, 'day': 1}
date.end_of_month().get_ethiopian()    # → {'year': 2016, 'month': 5, 'day': 30}

date.start_of('year').get_ethiopian()  # → {'year': 2016, 'month': 1, 'day': 1}

# endOf('year') correctly returns Pagume 6 in leap years, Pagume 5 otherwise
Kenat("2015/5/1").end_of('year').get_ethiopian()
# → {'year': 2015, 'month': 13, 'day': 6}
```

### Date Difference & Distance API

```python
from kenat import Kenat

a = Kenat("2015/5/15")
b = Kenat("2012/5/15")

print(a.diff_in_days(b))     # → 1095
print(a.diff_in_years(b))    # → 3

# Human-friendly distance
print(a.distance_to(b, units=['years', 'months', 'days'], output='string'))
# → "3 years 0 months 0 days"

print(Kenat("2018/1/1").distance_from_today(output='string'))
```

### Holiday Distance Helpers

```python
from kenat import Kenat, HolidayNames

print(Kenat.distance_to_holiday(HolidayNames['fasika'], direction='future', units=['days'], output='string'))
```

### Fasting Periods

```python
from kenat import get_fasting_period, get_fasting_info, get_fasting_days, is_tsome_dihnet_fast_day, FastingKeys

# Start/end of the fast
lent = get_fasting_period(FastingKeys.ABIY_TSOME, 2017)
# → {'start': {'year': 2017, 'month': 7, 'day': 16}, 'end': {'year': 2017, 'month': 8, 'day': 12}}

# Localized name/description alongside the period
info = get_fasting_info(FastingKeys.FILSETA, 2017, lang='english')

# Every day within the fast
days = get_fasting_days(FastingKeys.NINEVEH, 2017)

# Weekly Wednesday/Friday fast (skips the 50 days after Fasika)
is_tsome_dihnet_fast_day({'year': 2017, 'month': 1, 'day': 6})  # → True/False
```

### Orthodox Saints (Nigs) & Calendar Grid Modes

`MonthGrid` can attach Orthodox monthly commemoration ("Nigs") data per day, sourced from the same `nigs.json` data as the JS/TS library:

```python
from kenat import MonthGrid

grid = MonthGrid.create(2017, 1, mode='christian')
# Each day only lists a saint if this month is one of that saint's major-feast
# months (its `negs` list); pass show_all_saints=True to list every saint that
# recurs on that day-of-month, every month.

grid_all = MonthGrid.create(2017, 1, mode='christian', show_all_saints=True)

# mode='muslim' additionally injects a weekly Jummah (Friday prayer) entry;
# mode='public' filters holidays down to public-only.
friday_grid = MonthGrid.create(2017, 1, mode='muslim')

print(grid['month_name'])  # "መስከረም"
print(grid['days'])        # weeks-of-7, padded with None
print(grid['flat_days'])   # flat, start-padded list (mirrors the JS/TS shape)

# Month navigation: instantiate MonthGrid directly (rather than via .create())
# to get an object with .up()/.down(), then call .generate() when ready
grid_instance = MonthGrid({'year': 2017, 'month': 1, 'mode': 'christian'})
next_month = grid_instance.up().generate()
prev_month = grid_instance.down().generate()
```

### Calendar Preference (Ethiopian / Gregorian)

If your app lets users choose between the Ethiopian and Gregorian calendar, pass `calendar='gregorian'` to `format()`, `to_iso_string()`, or `get_date()` instead of branching at every call site:

```python
date = Kenat("2016/1/1")
user_pref = 'gregorian'  # e.g. from a user setting

date.format({'calendar': user_pref})        # → "September 12, 2023"
date.get_date(calendar=user_pref)           # → {'year': 2023, 'month': 9, 'day': 12}
date.to_iso_string(calendar=user_pref)      # → "2023-09-12T06:00" (standard ISO 8601)

date.format()  # → defaults to 'ethiopian': "መስከረም 1 2016"
```

### Calendar Generation

```python
from kenat import Kenat

calendar = Kenat.get_month_calendar_grid(2017, 1, use_geez=False, weekday_lang='amharic')
year_calendar = Kenat.get_year_calendar(2017)

start = Kenat("2017/1/1")
end = Kenat("2017/1/10")
date_range = Kenat.generate_date_range(start, end)

# Print the current month as a grid to the console
Kenat.now().print_this_month()
```

### Serialization

`Kenat` instances serialize cleanly via `to_json()`:

```python
date = Kenat("2017/1/15")
print(date.to_json())
# → {
#     'ethiopian': {'year': 2017, 'month': 1, 'day': 15},
#     'gregorian': {'year': 2024, 'month': 9, 'day': 25},
#     'time': {'hour': 12, 'minute': 0, 'period': 'day'}
#   }
```

Custom exceptions (`InvalidEthiopianDateError`, `UnknownHolidayError`, etc.) also expose `to_json()` for structured error handling/logging.

### Geez Numerals

```python
from kenat import to_geez

print(to_geez(2017))  # → ፳፻፲፯
```

---

## 🧱 Contributing

1. Fork & clone the repo
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes, add tests in `/tests/`
4. Run `pytest` to ensure everything passes
5. Submit a pull request 🚀

---

## 👨‍💻 Author

**Melaku Demeke**
GitHub: [@MelakuDemeke](https://github.com/MelakuDemeke)

---

## contributors
<a href="https://github.com/MelakuDemeke/kenat_py/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=MelakuDemeke/kenat_py" />
</a>


## 📄 License

**MIT License** — see [LICENSE](./LICENSE) for details.
