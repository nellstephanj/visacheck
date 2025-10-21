"""
Dutch Formatting Utilities
Formats numbers and dates according to Dutch conventions
"""
from datetime import datetime


def format_dutch_number(number, decimal_places=0):
    """
    Format number using Dutch conventions: periods for thousands, comma for decimal
    
    Args:
        number: The number to format
        decimal_places: Number of decimal places to show (default: 0)
    
    Returns:
        Formatted string with Dutch number formatting
    
    Examples:
        format_dutch_number(1234) -> "1.234"
        format_dutch_number(1234.56, 2) -> "1.234,56"
        format_dutch_number(1234567.89, 1) -> "1.234.567,9"
    """
    if decimal_places == 0:
        # For integers, use period as thousands separator
        formatted = f"{int(number):,}".replace(',', '.')
    else:
        # For decimals, format with specified decimal places
        formatted = f"{number:,.{decimal_places}f}"
        # Split at decimal point
        parts = formatted.split('.')
        if len(parts) == 2:
            # Has decimal part
            integer_part = parts[0].replace(',', '.')  # Replace thousands separator
            decimal_part = parts[1]
            formatted = f"{integer_part},{decimal_part}"  # Use comma as decimal separator
        else:
            # No decimal part, just replace thousands separator
            formatted = formatted.replace(',', '.')
    
    return formatted


def format_dutch_date(date_obj, include_time=False):
    """
    Format date using Dutch conventions: dd-mm-yyyy or dd-mm-yyyy HH:mm:ss
    
    Args:
        date_obj: datetime object or string in ISO format
        include_time: Whether to include time in the format (default: False)
    
    Returns:
        Formatted string with Dutch date formatting
    
    Examples:
        format_dutch_date(datetime(2024, 3, 15)) -> "15-03-2024"
        format_dutch_date(datetime(2024, 3, 15, 14, 30), True) -> "15-03-2024 14:30"
        format_dutch_date("2024-03-15T14:30:00") -> "15-03-2024"
    """
    # Handle string input (ISO format)
    if isinstance(date_obj, str):
        try:
            # Try parsing various ISO formats
            if 'T' in date_obj:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        except ValueError:
            return str(date_obj)  # Return original if parsing fails
    
    # Handle datetime object
    if isinstance(date_obj, datetime):
        if include_time:
            return date_obj.strftime("%d-%m-%Y %H:%M")
        else:
            return date_obj.strftime("%d-%m-%Y")
    
    # Fallback for other types
    return str(date_obj)