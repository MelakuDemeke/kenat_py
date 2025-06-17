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

def get_holiday(holiday_key, eth_year, lang='amharic'):
    """Gets details for a single holiday for a given year. """
    validate_numeric_inputs('get_holiday', eth_year=eth_year)  
    info = HOLIDAY_INFO.get(holiday_key)  
    if not info:  
        return None  
        
    name = info.get('name', {}).get(lang) or info.get('name', {}).get('english')  
    description = info.get('description', {}).get(lang) or info.get('description', {}).get('english')  

    if holiday_key in FIXED_HOLIDAYS:  
        rules = FIXED_HOLIDAYS[holiday_key]  
        return {  
            'key': holiday_key, 'tags': rules.get('tags', []), 'movable': False,  
            'name': name, 'description': description,  
            'ethiopian': {'year': eth_year, 'month': rules['month'], 'day': rules['day']}  
        }

    tewsak_key = KEY_TO_TEWSAK_MAP.get(holiday_key)  
    if tewsak_key:  
        date = bahire_hasab.get_movable_holiday(tewsak_key, eth_year)  
        gregorian = conversions.to_gc(date['year'], date['month'], date['day'])  
        return {  
            'key': holiday_key, 'tags': MOVABLE_HOLIDAYS.get(holiday_key, {}).get('tags', []), 'movable': True,  
            'name': name, 'description': description, 'ethiopian': date, 'gregorian': gregorian  
        }

    muslim_date_data = None  
    if holiday_key == 'eidFitr': muslim_date_data = _get_all_eid_fitr_dates(eth_year)  
    elif holiday_key == 'eidAdha': muslim_date_data = _get_all_eid_adha_dates(eth_year)  
    elif holiday_key == 'moulid': muslim_date_data = _get_all_moulid_dates(eth_year)  
    
    if muslim_date_data:  
        data = muslim_date_data[0]  
        return {  
            'key': holiday_key, 'tags': MOVABLE_HOLIDAYS.get(holiday_key, {}).get('tags', []), 'movable': True,  
            'name': name, 'description': description, 'ethiopian': data['ethiopian'], 'gregorian': data['gregorian']  
        }
    
    return None  

