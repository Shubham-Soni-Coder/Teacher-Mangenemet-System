import calendar
from datetime import datetime


def get_total_days_in_month(year: int, month: int) -> int:
    """Return the total number of days in a specific month of a year."""
    try:
        _, total_days = calendar.monthrange(year, month)
        return total_days
    except Exception as e:
        print(f"Error calculating days: {e}")
        return 0
