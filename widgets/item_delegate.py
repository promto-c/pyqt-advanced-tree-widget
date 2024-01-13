from typing import Dict, List, Optional
from numbers import Number
import datetime
import dateutil.parser as date_parser

from PyQt5 import QtCore, QtGui, QtWidgets

from utils.color_utils import ColorUtils


def create_pastel_color(color: QtGui.QColor, saturation: float = 0.4, value: float = 0.9) -> QtGui.QColor:
    """Create a pastel version of the given color.

    Args:
        color (QtGui.QColor): The original color.
        saturation (float): The desired saturation factor (default: 0.4).
        value (float): The desired value/brightness factor (default: 0.9).

    Returns:
        QtGui.QColor: The pastel color.
    """
    h, s, v, a = color.getHsvF()

    # Decrease saturation and value to achieve a more pastel look
    s *= saturation
    v *= value

    pastel_color = QtGui.QColor.fromHsvF(h, s, v, a)
    return pastel_color

def parse_date(date_string: str) -> Optional[datetime.datetime]:
    """Parse the given date string into a datetime.datetime object.

    Args:
        date_string: The date string to parse.

    Returns:
        The parsed datetime object, or None if parsing fails.
    """
    try:
        parsed_date = date_parser.parse(date_string)
        return parsed_date
    except ValueError:
        return None


class HighlightItemDelegate(QtWidgets.QStyledItemDelegate):
    """Custom item delegate class that highlights the rows specified by the `target_model_indexes` list.
    """
    # List of target model index for highlighting
    target_model_indexes: List[QtCore.QModelIndex] = list()
    target_focused_model_indexes: List[QtCore.QModelIndex] = list()
    target_selected_model_indexes: List[QtCore.QModelIndex] = list()

    # Define default highlight color
    DEFAULT_HIGHLIGHT_COLOR = QtGui.QColor(165, 165, 144, 65)
    DEFAULT_SELECTION_COLOR = QtGui.QColor(102, 119, 119, 51)
    
    def __init__(self, parent=None, highlight_color: QtGui.QColor = DEFAULT_HIGHLIGHT_COLOR, 
                 selection_color: QtGui.QColor = DEFAULT_SELECTION_COLOR):
        """Initialize the highlight item delegate.

        Args:
            parent (QtWidgets.QWidget, optional): The parent widget. Defaults to None.
            color (QtGui.QColor, optional): The color to use for highlighting. Defaults to a light grayish-yellow.
        """
        # Initialize the super class
        super().__init__(parent)

        # Set the color attribute
        self.highlight_color = highlight_color
        self.selection_color = selection_color

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, model_index: QtCore.QModelIndex):
        """Paint the delegate.
        
        Args:
            painter (QtGui.QPainter): The painter to use for drawing.
            option (QtWidgets.QStyleOptionViewItem): The style option to use for drawing.
            model_index (QtCore.QModelIndex): The model index of the item to be painted.
        """
        # Check if the current model index is not in the target list
        if model_index not in self.target_selected_model_indexes and model_index not in self.target_model_indexes:
            # If not, paint the item normally using the parent implementation
            super().paint(painter, option, model_index)
            return

        # ...
        color = painter.background().color()

        # ...
        if model_index in self.target_model_indexes:
            color = ColorUtils.blend_colors(color, self.highlight_color)
        if model_index in self.target_focused_model_indexes:
            color = ColorUtils.blend_colors(color, self.highlight_color)
        if model_index in self.target_selected_model_indexes:
            color = ColorUtils.blend_colors(color, self.selection_color)

        # If the current model index is in the target list, set the background color and style
        option.backgroundBrush.setColor(color)
        option.backgroundBrush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

        # Fill the rect with the background brush
        painter.fillRect(option.rect, option.backgroundBrush)

        # Paint the item normally using the parent implementation
        super().paint(painter, option, model_index)

    def clear(self):
        # Reset the previous target model indexes
        self.target_model_indexes.clear()
        self.target_focused_model_indexes.clear()

class AdaptiveColorMappingDelegate(QtWidgets.QStyledItemDelegate):
    """A delegate class for adaptive color mapping in Qt items.

    This delegate maps values to colors based on specified rules and color definitions.
    It provides functionality to map numerical values, keywords, and date strings to colors.

    Class Constants:
        COLOR_DICT: A dictionary that maps color names to corresponding QColor objects.

    Attributes:
        min_value (Optional[Number]): The minimum value of the range.
        max_value (Optional[Number]): The maximum value of the range.
        min_color (QtGui.QColor): The color corresponding to the minimum value.
        max_color (QtGui.QColor): The color corresponding to the maximum value.
        keyword_color_dict (Dict[str, QtGui.QColor]): A dictionary that maps keywords to specific colors.
        date_format (str): The date format string.
        date_color_dict (Dict[str, QtGui.QColor]): A dictionary that caches colors for date values.
    """
    # Class constants
    # ---------------
    COLOR_DICT = {
        'pastel_green': create_pastel_color(QtGui.QColor(65, 144, 0)),
        'pastel_red': create_pastel_color(QtGui.QColor(144, 0, 0)),
        'red': QtGui.QColor(183, 26, 28),
        'light_red': QtGui.QColor(183, 102, 77),
        'light_green': QtGui.QColor(170, 140, 88),
        'dark_green': QtGui.QColor(82, 134, 74),
        'green': QtGui.QColor(44, 65, 44),
        'blue': QtGui.QColor(0, 120, 215),
    }

    # Initialization and Setup
    # ------------------------
    def __init__(
        self,
        parent: Optional[QtCore.QObject] = None,
        min_value: Optional[Number] = None,
        max_value: Optional[Number] = None,
        min_color: QtGui.QColor = COLOR_DICT['pastel_green'],
        max_color: QtGui.QColor = COLOR_DICT['pastel_red'],
        keyword_color_dict: Dict[str, QtGui.QColor] = dict(),
        date_color_dict: Dict[str, QtGui.QColor] = dict(),
        date_format: str = '%Y-%m-%d',
    ):
        """Initialize the AdaptiveColorMappingDelegate.

        Args:
            parent (QtCore.QObject, optional): The parent object. Default is None.
            min_value (Number, optional): The minimum value of the range. Default is None.
            max_value (Number, optional): The maximum value of the range. Default is None.
            min_color (QtGui.QColor, optional): The color corresponding to the minimum value.
                Default is a pastel green.
            max_color (QtGui.QColor, optional): The color corresponding to the maximum value.
                Default is a pastel red.
            keyword_color_dict (Dict[str, QtGui.QColor], optional): A dictionary that maps
                keywords to specific colors. Default is an empty dictionary.
            date_format (str, optional): The date format string. Default is '%Y-%m-%d'.
        """
        # Initialize the super class
        super().__init__(parent)

        # Store the arguments
        self.min_value = min_value
        self.max_value = max_value
        self.min_color = min_color
        self.max_color = max_color
        self.keyword_color_dict = keyword_color_dict
        self.date_color_dict = date_color_dict
        self.date_format = date_format

    # Private Methods
    # ---------------
    def _interpolate_color(self, value: Number) -> QtGui.QColor:
        """Interpolate between the min_color and max_color based on the given value.

        Args:
            value (Number): The value within the range.

        Returns:
            QtGui.QColor: The interpolated color.
        """
        if not value:
            return QtGui.QColor()

        # Normalize the value between 0 and 1
        normalized_value = (value - self.min_value) / (self.max_value - self.min_value)

        # Interpolate between the min_color and max_color based on the normalized value
        color = QtGui.QColor()
        color.setRgbF(
            self.min_color.redF() + (self.max_color.redF() - self.min_color.redF()) * normalized_value,
            self.min_color.greenF() + (self.max_color.greenF() - self.min_color.greenF()) * normalized_value,
            self.min_color.blueF() + (self.max_color.blueF() - self.min_color.blueF()) * normalized_value
        )

        return color

    def _get_keyword_color(self, keyword: str, is_pastel_color: bool = True) -> QtGui.QColor:
        """Get the color associated with a keyword.

        Args:
            keyword (str): The keyword for which to retrieve the color.

        Returns:
            QtGui.QColor: The color associated with the keyword.
        """
        if not keyword:
            return QtGui.QColor()

        # Check if the keyword color is already cached in the keyword_color_dict
        if keyword in self.keyword_color_dict:
            return self.keyword_color_dict[keyword]

        # Generate a new color for the keyword
        hue = (hash(keyword) % 360) / 360
        saturation, value = 0.6, 0.6
        keyword_color = QtGui.QColor.fromHsvF(hue, saturation, value)

        # Optionally create a pastel version of the color
        keyword_color = create_pastel_color(keyword_color, 0.6, 0.9) if is_pastel_color else keyword_color

        # Cache the color in the keyword_color_dict
        self.keyword_color_dict[keyword] = keyword_color

        return keyword_color

    def _get_deadline_color(self, difference: int) -> QtGui.QColor:
        """Get the color based on the difference from the current date.

        Args:
            difference (int): The difference in days from the current date.

        Returns:
            QtGui.QColor: The color corresponding to the difference.
        """
        color_palette = {
            0: self.COLOR_DICT['red'],              # Red (today's deadline)
            1: self.COLOR_DICT['light_red'],        # Slightly lighter tone for tomorrow
            2: self.COLOR_DICT['light_green'],      # Light green for the day after tomorrow
            **{diff: self.COLOR_DICT['dark_green'] 
               for diff in range(3, 8)},            # Dark green for the next 3-7 days
        }

        if difference >= 7:
            # Green for dates more than 7 days away
            return self.COLOR_DICT['green']
        else:
            # Blue for other dates
            return color_palette.get(difference, self.COLOR_DICT['blue'])

    def _get_date_color(self, date_value: str, is_pastel_color: bool = True) -> QtGui.QColor:
        """Get the color based on the given date value.

        Args:
            date_value (str): The date string to determine the color for.
            is_pastel_color (bool, optional): Whether to create a pastel version of the color.
                Default is True.

        Returns:
            QtGui.QColor: The color corresponding to the date.
        """
        # Check if the date color is already cached in the date_color_dict
        if date_value in self.date_color_dict:
            return self.date_color_dict[date_value]

        # Get the current date
        today = datetime.date.today()

        # If a date format is specified, use datetime.strptime to parse the date string
        if self.date_format:
            # Use datetime.strptime to parse the date string
            parsed_date = datetime.datetime.strptime(date_value, self.date_format).date()
        else:
            # Otherwise, use the parse_date function to parse the date string
            parsed_date = parse_date(date_value).date()

        # Calculate the difference in days between the parsed date and today
        difference = (parsed_date - today).days

        # Get the color based on the difference in days
        date_color = self._get_deadline_color(difference)
        # Optionally create a pastel version of the color
        date_color = create_pastel_color(date_color, 0.6, 0.9) if is_pastel_color else date_color

        # Cache the color in the date_color_dict
        self.date_color_dict[date_value] = date_color

        return date_color

    # Event Handling or Override Methods
    # ----------------------------------
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, model_index: QtCore.QModelIndex):
        """Paint the delegate.
        
        Args:
            painter (QtGui.QPainter): The painter to use for drawing.
            option (QtWidgets.QStyleOptionViewItem): The style option to use for drawing.
            model_index (QtCore.QModelIndex): The model index of the item to be painted.
        """
        # Retrieve the value from the model using UserRole
        value = model_index.data(QtCore.Qt.ItemDataRole.UserRole)

        if isinstance(value, Number):
            # If the value is numerical, use _interpolate_color
            color = self._interpolate_color(value)
        elif isinstance(value, str):
            if not parse_date(value):
                # If the value is a string and not a date, use _get_keyword_color
                color = self._get_keyword_color(value)
            else:
                # If the value is a date string, use _get_date_color
                color = self._get_date_color(value)
        else:
            # For other data types, paint the item normally
            super().paint(painter, option, model_index)
            return

        # If the current model index is in the target list, set the background color and style
        option.backgroundBrush.setColor(color)
        option.backgroundBrush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

        # Fill the rect with the background brush
        painter.fillRect(option.rect, option.backgroundBrush)

        # Paint the item normally using the parent implementation
        super().paint(painter, option, model_index)
