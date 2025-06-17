from .exceptions import InvalidInputTypeError

# --- Validation Helpers ---

def validate_numeric_inputs(func_name, **kwargs):
    """
    Validates that all provided keyword arguments are numbers.
    
    Raises:
        InvalidInputTypeError: If any value is not a number.
    """
    for name, value in kwargs.items():
        if not isinstance(value, (int, float)) or value != value: # Checks for NaN
            raise InvalidInputTypeError(func_name, name, 'number', value)

