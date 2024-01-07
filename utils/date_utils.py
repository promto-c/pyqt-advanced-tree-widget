# Standard Library Imports
# ------------------------
from typing import Optional, List, Union
import datetime


def get_date_list(
        start_date: Optional[Union[str, datetime.date, datetime.datetime]] = None, 
        end_date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
        days_relative: Optional[int] = None, 
        date_format: str = '%Y-%m-%d'
    ) -> List[Union[str, datetime.date, datetime.datetime]]:
    """Generates a list of dates within a specified range, or relative to the current date.

    Args:
        start_date: Start date in 'YYYY-MM-DD' format, datetime.date, or datetime.datetime. 
                    Used if days_relative is None.
        end_date: End date in 'YYYY-MM-DD' format, datetime.date, or datetime.datetime. 
                  Used if days_relative is None.
        days_relative: Number of days relative to today. Positive for future, negative for past.
        date_format: Desired format of the date strings.

    Returns:
        A list of date strings, datetime.date, or datetime.datetime in the specified range,
        depending on the input type of start_date.

    Raises:
        ValueError: If neither days_relative nor both start_date and end_date are specified.

    Examples:
        >>> get_date_list(start_date='2023-01-01', end_date='2023-01-03')
        ['2023-01-01', '2023-01-02', '2023-01-03']
        >>> get_date_list(start_date=datetime.date(2023, 1, 1), end_date=datetime.date(2023, 1, 3))
        [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2), datetime.date(2023, 1, 3)]
    """
    input_type = type(start_date) if start_date is not None else str

    if days_relative is not None:
        # Calculate date range based on days relative to today
        reference_date = datetime.datetime.now()
        start_date, end_date = sorted([reference_date, reference_date + datetime.timedelta(days=days_relative)])
    elif start_date and end_date:
        # Check and parse start and end dates based on their type
        if isinstance(start_date, str):
            start_date = datetime.datetime.strptime(start_date, date_format)
        if isinstance(end_date, str):
            end_date = datetime.datetime.strptime(end_date, date_format)
    else:
        # Ensure valid input is provided
        raise ValueError("Either specify days_relative or both start_date and end_date")

    # Generate list of dates in the range in the appropriate format
    date_list = [(start_date + datetime.timedelta(days=i)) for i in range((end_date - start_date).days + 1)]
    date_list = [date.strftime(date_format) for date in date_list] if input_type is str else date_list

    return date_list


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    # Example usage
    print(get_date_list(days_relative=7))  # Next 7 days
    print(get_date_list(days_relative=-7)) # Last 7 days
