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

    @classmethod
    def from_gregorian(cls, hour, minute=0):
        """
        Creates a Time instance from a Gregorian 24-hour time. 
        """
        validate_numeric_inputs('Time.from_gregorian', hour=hour, minute=minute) # 
        if not 0 <= hour <= 23: # 
            raise InvalidTimeError(f"Invalid Gregorian hour: {hour}. Must be between 0 and 23.") # 
        
        # Normalize Gregorian hour to an Ethiopian base (where 6 AM is 0)
        temp_hour = hour - 6 # 
        if temp_hour < 0: # 
            temp_hour += 24 # 

        period = 'day' if temp_hour < 12 else 'night' # 
        eth_hour = temp_hour % 12 # 
        eth_hour = 12 if eth_hour == 0 else eth_hour # 

        return cls(eth_hour, minute, period) # 

    