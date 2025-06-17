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

def validate_ethiopian_date_object(date_obj, func_name, param_name):
    """
    Validates that the input is a valid Ethiopian date object.
    
    Raises:
        InvalidInputTypeError: If the object is not a dict or its components are not numbers.
    """
    if not isinstance(date_obj, dict):
        raise InvalidInputTypeError(func_name, param_name, 'dict', date_obj)
    validate_numeric_inputs(
        func_name,
        **{
            f'{param_name}.year': date_obj.get('year'),
            f'{param_name}.month': date_obj.get('month'),
            f'{param_name}.day': date_obj.get('day'),
        }
    )

