from .geez_converter import to_geez, to_arabic
from .constants import PERIOD_LABELS
from .exceptions import InvalidTimeError
from .utils import validate_numeric_inputs

class Time:
    """
    A class to represent and work with Ethiopian time (1-12 hour cycles for day/night).
    """
    def __init__(self, hour, minute=0, period='day'):
        """
        Constructs a Time instance representing an Ethiopian time. 
        
        Args:
            hour (int): The Ethiopian hour (1-12). 
            minute (int): The minute (0-59). 
            period (str): The period ('day' or 'night'). 
        """
        validate_numeric_inputs('Time.constructor', hour=hour, minute=minute) # 
        if not 1 <= hour <= 12: # 
            raise InvalidTimeError(f"Invalid Ethiopian hour: {hour}. Must be between 1 and 12.") # 
        if not 0 <= minute <= 59: # 
            raise InvalidTimeError(f"Invalid minute: {minute}. Must be between 0 and 59.") # 
        if period not in ['day', 'night']: # 
            raise InvalidTimeError(f"Invalid period: \"{period}\". Must be 'day' or 'night'.") # 

        self.hour = hour # 
        self.minute = minute # 
        self.period = period # 

    