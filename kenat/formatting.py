from .geez_converter import to_geez
from .constants import MONTH_NAMES, DAYS_OF_WEEK
from .utils import get_weekday

def format_standard(et_date, lang='amharic'):
    """
    Formats an Ethiopian date using a language-specific month name and Arabic numerals.
    Example: "መስከረም 10 2016" 
    """
    names = MONTH_NAMES.get(lang, MONTH_NAMES['amharic']) 
    month_name = names[et_date['month'] - 1] 
    return f"{month_name} {et_date['day']} {et_date['year']}" 

def format_in_geez_amharic(et_date):
    """
    Formats an Ethiopian date in Geez numerals with Amharic month name.
    Example: "መስከረም ፲፩ ፳፻፲፮" 
    """
    month_name = MONTH_NAMES['amharic'][et_date['month'] - 1] 
    return f"{month_name} {to_geez(et_date['day'])} {to_geez(et_date['year'])}" 
