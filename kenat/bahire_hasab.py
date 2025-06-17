from .utils import validate_numeric_inputs, get_weekday
from .day_arithmetic import add_days
from .conversions import to_gc
from .exceptions import UnknownHolidayError
from .constants import (
    DAYS_OF_WEEK,
    EVANGELIST_NAMES,
    TEWSAK_MAP,
    MOVABLE_HOLIDAY_TEWSAK,
    KEY_TO_TEWSAK_MAP,
    HOLIDAY_INFO,
    MOVABLE_HOLIDAYS
)

def _calculate_bahire_hasab_base(ethiopian_year):
    """
    Calculates and returns all base values for the Bahire Hasab system. 
    This internal helper is the single source of truth for the core computational logic. 
    """
    amete_alem = 5500 + ethiopian_year  
    metene_rabiet = amete_alem // 4  
    medeb = amete_alem % 19  
    wenber = 18 if medeb == 0 else medeb - 1  
    abektie = (wenber * 11) % 30  
    metqi = (wenber * 19) % 30  

    beale_metqi_month = 1 if metqi > 14 else 2  
    beale_metqi_day = metqi  
    beale_metqi_date = {'year': ethiopian_year, 'month': beale_metqi_month, 'day': beale_metqi_day}  
    
    beale_metqi_weekday = DAYS_OF_WEEK['english'][get_weekday(beale_metqi_date)]  
    tewsak = TEWSAK_MAP[beale_metqi_weekday]  
    
    mebaja_hamer_sum = beale_metqi_day + tewsak  
    mebaja_hamer = mebaja_hamer_sum % 30 if mebaja_hamer_sum > 30 else mebaja_hamer_sum  
    
    nineveh_month = 5 if metqi > 14 else 6  
    if mebaja_hamer_sum > 30:  
        nineveh_month += 1  
        
    nineveh_date = {'year': ethiopian_year, 'month': nineveh_month, 'day': mebaja_hamer}  
    
    return {  
        'amete_alem': amete_alem,  
        'metene_rabiet': metene_rabiet,  
        'medeb': medeb,  
        'wenber': wenber,  
        'abektie': abektie,  
        'metqi': metqi,  
        'beale_metqi_date': beale_metqi_date,  
        'beale_metqi_weekday': beale_metqi_weekday,  
        'mebaja_hamer': mebaja_hamer,  
        'nineveh_date': nineveh_date,  
    }
