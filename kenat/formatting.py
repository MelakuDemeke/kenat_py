from .geez_converter import toGeez
from .constants import MONTH_NAMES, DAYS_OF_WEEK
from .utils import get_weekday

def _month_name_or_fallback(names, month):
    """Returns names[month-1] or a 'Month{n}' placeholder for an out-of-range month,
    mirroring TS's `names[etDate.month - 1] || 'Month' + etDate.month` fallback."""
    if 1 <= month <= len(names):
        return names[month - 1]
    return f"Month{month}"

def format_standard(et_date, lang='amharic'):
    """
    Formats an Ethiopian date using a language-specific month name and Arabic numerals.
    Example: "መስከረም 10 2016"
    """
    names = MONTH_NAMES.get(lang, MONTH_NAMES['amharic'])
    month_name = _month_name_or_fallback(names, et_date['month'])
    return f"{month_name} {et_date['day']} {et_date['year']}"

def format_in_geez_amharic(et_date):
    """
    Formats an Ethiopian date in Geez numerals with Amharic month name.
    Example: "መስከረም ፲፩ ፳፻፲፮" 
    """
    month_name = _month_name_or_fallback(MONTH_NAMES['amharic'], et_date['month'])
    return f"{month_name} {toGeez(et_date['day'])} {toGeez(et_date['year'])}"

def format_with_time(et_date, time_obj, lang='amharic'):
    """
    Formats an Ethiopian date and time as a string.
    Example: "መስከረም 10 2016 08:30 ጠዋት" 
    """
    base = format_standard(et_date, lang)
    time_string = time_obj.format(lang=lang, use_geez=False, zero_as_dash=False)  
    return f"{base} {time_string}" 

def format_with_weekday(et_date, lang='amharic', use_geez=False):
    """
    Formats a date with the weekday name, month name, day, and year. 
    Example: "ማክሰኞ, መስከረም 1 2016" 
    """
    weekday_index = get_weekday(et_date) 
    weekday_name = DAYS_OF_WEEK.get(lang, DAYS_OF_WEEK['amharic'])[weekday_index]
    month_name = _month_name_or_fallback(MONTH_NAMES.get(lang, MONTH_NAMES['amharic']), et_date['month'])
    day = toGeez(et_date['day']) if use_geez else et_date['day']
    year = toGeez(et_date['year']) if use_geez else et_date['year'] 

    return f"{weekday_name}, {month_name} {day} {year}" 

def format_short(et_date):
    """
    Returns Ethiopian date in short "yyyy/mm/dd" format. 
    Example: "2017/10/25"
    """
    y = et_date['year'] 
    m = str(et_date['month']).zfill(2) 
    d = str(et_date['day']).zfill(2) 
    return f"{y}/{m}/{d}" 

def to_iso_date_string(et_date, time_obj=None):
    """
    Returns an ISO-like string: "YYYY-MM-DD" or "YYYY-MM-DDTHH:mm".
    A non-standard "+12h" suffix is appended when the time's period is 'night',
    matching TS's toISODateString.
    """
    y = et_date['year']
    m = str(et_date['month']).zfill(2)
    d = str(et_date['day']).zfill(2)

    if not time_obj:
        return f"{y}-{m}-{d}"

    hr = str(time_obj.hour).zfill(2)
    minute = str(time_obj.minute).zfill(2)
    suffix = '+12h' if getattr(time_obj, 'period', None) == 'night' else ''
    return f"{y}-{m}-{d}T{hr}:{minute}{suffix}"


def format_gregorian_standard(g_date):
    """
    Formats a Gregorian date using its English month name.
    Example: "September 11, 2023"
    """
    names = MONTH_NAMES['gregorian']
    month_name = _month_name_or_fallback(names, g_date['month'])
    return f"{month_name} {g_date['day']}, {g_date['year']}"


def format_gregorian_with_weekday(g_date, lang='english'):
    """
    Formats a Gregorian date object with the weekday name, month name, day, and year.
    Example: "Monday, September 11, 2023"
    """
    import datetime as _datetime
    weekday_index = (_datetime.date(g_date['year'], g_date['month'], g_date['day']).isoweekday()) % 7
    weekday_name = DAYS_OF_WEEK.get(lang, DAYS_OF_WEEK['english'])[weekday_index]
    return f"{weekday_name}, {format_gregorian_standard(g_date)}"


def format_gregorian_with_time(g_date, time_obj, lang='amharic'):
    """
    Formats a Gregorian date and time as a string.
    Example: "September 11, 2023 08:30 ጠዋት"
    """
    base = format_gregorian_standard(g_date)
    time_string = time_obj.format(lang=lang, use_geez=False, zero_as_dash=False)
    return f"{base} {time_string}"


def to_gregorian_iso_date_string(g_date, time_obj=None):
    """
    Returns a standard ISO 8601 date-time string for a Gregorian date. Unlike
    to_iso_date_string(), the Ethiopian `time_obj` (12-hour, day/night) is converted
    to Gregorian 24-hour time via Time.to_gregorian() and no non-standard suffix is
    appended, so the result is a valid ISO 8601 string parsers can consume.
    """
    y = g_date['year']
    m = str(g_date['month']).zfill(2)
    d = str(g_date['day']).zfill(2)

    if not time_obj:
        return f"{y}-{m}-{d}"

    greg_time = time_obj.to_gregorian()
    hr = str(greg_time['hour']).zfill(2)
    minute = str(greg_time['minute']).zfill(2)
    return f"{y}-{m}-{d}T{hr}:{minute}"
