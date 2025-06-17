import json
from . import conversions, bahire_hasab
from .constants import (
    FIXED_HOLIDAYS,
    MOVABLE_HOLIDAYS,
    HOLIDAY_INFO,
    KEY_TO_TEWSAK_MAP
)
from .utils import validate_numeric_inputs
from .exceptions import InvalidInputTypeError

def _find_all_islamic_occurrences(ethiopian_year, hijri_month, hijri_day):
    """
    Finds all occurrences of an Islamic date within an Ethiopian year. 
    This is a dependency-free implementation.
    """
    occurrences = []
    start_gc_date = conversions.to_gc(ethiopian_year, 1, 1)  
    
    start_hijri_year = conversions.get_hijri_year(start_gc_date)  

    hijri_years_to_check = [start_hijri_year, start_hijri_year + 1, start_hijri_year + 2]  
    
    for h_year in hijri_years_to_check:  
        try:
            greg_date = conversions.hijri_to_gregorian(h_year, hijri_month, hijri_day)  
            ec_date = conversions.to_ec(greg_date.year, greg_date.month, greg_date.day)  
            
            if ec_date['year'] == ethiopian_year:  
                occurrences.append({  
                    'gregorian': {'year': greg_date.year, 'month': greg_date.month, 'day': greg_date.day},  
                    'ethiopian': ec_date  
                }) 
        except Exception:
            continue
            
    return list({json.dumps(item['ethiopian']): item for item in occurrences}.values())  

_get_all_moulid_dates = lambda year: _find_all_islamic_occurrences(year, 3, 12)  
_get_all_eid_fitr_dates = lambda year: _find_all_islamic_occurrences(year, 10, 1)  
_get_all_eid_adha_dates = lambda year: _find_all_islamic_occurrences(year, 12, 10)  

