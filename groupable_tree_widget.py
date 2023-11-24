import sys
import time
import datetime
import dateutil.parser as date_parser

from typing import Any, Dict, List, Union, Tuple, Type, Callable, Optional
from numbers import Number

from PyQt5 import QtWidgets, QtCore, QtGui

from theme.theme import set_theme

# Define example data
COLUMN_NAME_LIST = [
    'shot_id',
    'sequence',
    'status',
    'start_date',
    'due_date',
    'priority',
    'shot_length',
    'artist',
    'department',
]

ID_TO_DATA_DICT = {
    1: {
        'shot_id': 'SHOT001',
        'sequence': 'SEQ001',
        'status': 'In Progress',
        'start_date': '2023-06-17',
        'due_date': '2023-07-15',
        'priority': 2,
        'shot_length': 150,
        'artist': 'John Smith',
        'department': 'Compositing'
    },
    2: {
        'shot_id': 'SHOT002',
        'sequence': 'SEQ001',
        'status': 'Completed',
        'start_date': '2023-06-20',
        'due_date': '2023-07-10',
        'priority': 1,
        'shot_length': 200,
        'artist': 'Jane Doe',
        'department': 'Animation'
    },
    3: {
        'shot_id': 'SHOT003',
        'sequence': 'SEQ002',
        'status': 'Not Started',
        'start_date': '2023-06-25',
        'due_date': '2023-07-20',
        'priority': 3,
        'shot_length': 120,
        'artist': 'Alex Johnson',
        'department': 'Lighting'
    },
    4: {
        'shot_id': 'SHOT004',
        'sequence': 'SEQ002',
        'status': 'In Progress',
        'start_date': '2023-06-18',
        'due_date': '2023-07-25',
        'priority': 2,
        'shot_length': 180,
        'artist': 'Emily Brown',
        'department': 'Modeling'
    },
    5: {
        'shot_id': 'SHOT005',
        'sequence': 'SEQ003',
        'status': 'Completed',
        'start_date': '2023-06-22',
        'due_date': '2023-07-12',
        'priority': 1,
        'shot_length': 250,
        'artist': 'Michael Johnson',
        'department': 'Rigging'
    },
    6: {
        'shot_id': 'SHOT006',
        'sequence': 'SEQ003',
        'status': 'In Progress',
        'start_date': '2023-06-30',
        'due_date': '2023-07-30',
        'priority': 3,
        'shot_length': 130,
        'artist': 'Sophia Wilson',
        'department': 'Texturing'
    },
    7: {
        'shot_id': 'SHOT007',
        'sequence': 'SEQ004',
        'status': 'Not Started',
        'start_date': '2023-06-16',
        'due_date': '2023-07-18',
        'priority': 2,
        'shot_length': 160,
        'artist': 'Daniel Lee',
        'department': 'Animation'
    },
    8: {
        'shot_id': 'SHOT008',
        'sequence': 'SEQ004',
        'status': 'In Progress',
        'start_date': '2023-06-25',
        'due_date': '2023-07-25',
        'priority': 2,
        'shot_length': 190,
        'artist': 'Olivia Davis',
        'department': 'Compositing'
    },
    9: {
        'shot_id': 'SHOT009',
        'sequence': 'SEQ005',
        'status': 'In Progress',
        'start_date': '2023-06-19',
        'due_date': '2023-07-20',
        'priority': 3,
        'shot_length': 140,
        'artist': 'Noah Johnson',
        'department': 'Lighting'
    },
    10: {
        'shot_id': 'SHOT010',
        'sequence': 'SEQ005',
        'status': 'Completed',
        'start_date': '2023-06-20',
        'due_date': '2023-07-15',
        'priority': 1,
        'shot_length': 220,
        'artist': 'Isabella Clark',
        'department': 'Modeling'
    },
}

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
        value = model_index.data(QtCore.Qt.UserRole)

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
        option.backgroundBrush.setStyle(QtCore.Qt.SolidPattern)

        # Fill the rect with the background brush
        painter.fillRect(option.rect, option.backgroundBrush)

        # Paint the item normally using the parent implementation
        super().paint(painter, option, model_index)

class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    """A custom `QTreeWidgetItem` that can handle different data formats and store additional data in the user role.

    Attributes:
        id (int): The ID of the item.
    """
    # Initialization and Setup
    # ------------------------
    def __init__(self, parent: Union[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem], 
                 item_data: Union[Dict[str, Any], List[str]] = None, 
                 item_id: int = None):
        """Initialize the `TreeWidgetItem` with the given parent and item data.
        
        Args:
            parent (Union[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem]): The parent `QTreeWidget` or QtWidgets.QTreeWidgetItem.
            item_data (Union[Dict[str, Any], List[str]], optional): The data for the item. Can be a list of strings or a dictionary with keys matching the headers of the parent `QTreeWidget`. Defaults to `None`.
            item_id (int, optional): The ID of the item. Defaults to `None`.
        """
        # Set the item's ID
        self.id = item_id

        # If the data for the item is in list form
        if isinstance(item_data, list):
            item_data_list = item_data

        # If the data for the item is in dictionary form
        if isinstance(item_data, dict):
            # Get the header item from the parent tree widget
            header_item = parent.headerItem() if isinstance(parent, QtWidgets.QTreeWidget) else parent.treeWidget().headerItem()

            # Get the column names from the header item
            column_names = [header_item.text(i) for i in range(header_item.columnCount())]

            # Create a list of data for the tree item
            item_data_list = [item_id] + [item_data[column] if column in item_data.keys()
                                                                 else str() 
                                                                 for column in column_names[1:]]

        # Call the superclass's constructor to set the item's data
        super().__init__(parent, map(str, item_data_list))

        # Set the UserRole data for the item.
        self._set_user_role_data(item_data_list)

    # Private Methods
    # ---------------
    def _set_user_role_data(self, item_data_list: List[Any]):
        """Set the UserRole data for the item.

        Args:
            item_data_list (List[Any]): The list of data to set as the item's data.
        """
        # Iterate through each column in the item
        for column_index, value in enumerate(item_data_list):
            # Set the value for the column in the UserRole data
            self.set_value(column_index, value)

    # Extended Methods
    # ----------------
    def get_child_level(self) -> int:
        """Get the child level of TreeWidgetItem

        Returns:
            int: The child level of the TreeWidgetItem
        """
        # Set the current item as self
        item = self
        # Initialize child level
        child_level = 0

        # Iterate through the parent items to determine the child level
        while item.parent():
            # Increment child level for each parent
            child_level += 1
            # Update item to be its parent
            item = item.parent()

        # Return the final child level
        return child_level

    def get_model_indexes(self) -> List[QtCore.QModelIndex]:
        """Get the model index for each column in the tree widget.

        Returns:
            List[QtCore.QModelIndex]: A list of model index for each column in the tree widget.
        """
        # Get a list of the shown column indices
        shown_column_index_list = self.treeWidget().get_shown_column_index_list()

        # Create a list to store the model index
        model_indexes = list()

        # Loop through each shown column index
        for column_index in shown_column_index_list:
            # Get the model index for the current column
            model_index = self.treeWidget().indexFromItem(self, column_index)

            # Add the model index to the list
            model_indexes.append(model_index)

        # Return the list of model index properties
        return model_indexes

    def get_value(self, column: Union[int, str]) -> Any:
        """Get the value of the item's UserRole data for the given column.

        Args:
            column (Union[int, str]): The column index or name.

        Returns:
            Any: The value of the UserRole data.
        """
        # Get the column index from the column name if necessary
        column_index = self.treeWidget().get_column_index(column) if isinstance(column, str) else column

        # Get the UserRole data for the column
        value = self.data(column_index, QtCore.Qt.ItemDataRole.UserRole)
        # Fallback to the DisplayRole data if UserRole data is None
        value = self.data(column_index, QtCore.Qt.ItemDataRole.DisplayRole) if value is None else value

        return value

    def set_value(self, column: Union[int, str], value: Any):
        """Set the value of the item's UserRole data for the given column.

        Args:
            column (Union[int, str]): The column index or name.
            value (Any): The value to set.
        """
        # Get the column index from the column name if necessary
        column_index = self.treeWidget().get_column_index(column) if isinstance(column, str) else column

        # Set the value for the column in the UserRole data
        self.setData(column_index, QtCore.Qt.ItemDataRole.UserRole, value)

    # Special Methods
    # ---------------
    def __getitem__(self, key: Union[int, str]) -> Any:
        """Get the value of the item's UserRole data for the given column.

        Args:
            key (Union[int, str]): The column index or name.

        Returns:
            Any: The value of the UserRole data.
        """
        # Delegate the retrieval of the value to the `get_value` method
        return self.get_value(key)

    def __lt__(self, other_item: QtWidgets.QTreeWidgetItem) -> bool:
        """Sort the items in the tree widget based on their data.

        Args:
            other_item (QtWidgets.QTreeWidgetItem): The item to compare with.

        Returns:
            bool: Whether this item is less than the other item.
        """
        # Get the column that is currently being sorted
        column = self.treeWidget().sortColumn()

        # Get the UserRole data for the column for both this item and the other item
        self_data = self.get_value(column)
        other_data = other_item.get_value(column)

        # If the UserRole data is None, fallback to DisplayRole data
        if other_data is None:
            # Get the DisplayRole data for the column of the other item
            other_data = other_item.data(column, QtCore.Qt.DisplayRole)

        # If both UserRole data are None, compare their texts
        if self_data is None and other_data is None:
            return self.text(column) < other_item.text(column)

        # If this item's UserRole data is None, it is considered greater
        if self_data is None:
            return True

        # If the other item's UserRole data is None, this item is considered greater
        if other_data is None:
            return False

        try:
            # Try to compare the UserRole data directly
            return self_data < other_data
        except TypeError:
            # If the comparison fails, compare their string representations
            return str(self_data) < str(other_data)

class GroupableTreeWidget(QtWidgets.QTreeWidget):
    """A QTreeWidget subclass that displays data in a tree structure with the ability to group data by a specific column.

    Attributes:
        column_name_list (List[str]): The list of column names to be displayed in the tree widget.
        id_to_data_dict (Dict[int, Dict[str, str]]): A dictionary mapping item IDs to their data as a dictionary.
        groups (Dict[str, TreeWidgetItem]): A dictionary mapping group names to their tree widget items.
        _is_middle_button_pressed (bool): Indicates if the middle mouse button is pressed.
            It's used for scrolling functionality when the middle button is pressed and the mouse is moved.
        _middle_button_prev_pos (QtCore.QPoint): The previous position of the mouse when the middle button was pressed.
        _middle_button_start_pos (QtCore.QPoint): The initial position of the mouse when the middle button was pressed.
        _mouse_move_timestamp (float): The timestamp of the last mouse movement.
    """
    # Signals emitted by the GroupableTreeWidget
    ungrouped_all = QtCore.pyqtSignal()
    grouped_by_column = QtCore.pyqtSignal(str)

    # Initialization and Setup
    # ------------------------
    def __init__(self, parent: QtWidgets.QWidget = None, 
                       column_name_list: List[str] = list(), 
                       id_to_data_dict: Dict[int, Dict[str, str]] = dict()):
        # Call the parent class constructor
        super().__init__(parent)

        # Store the column names and data dictionary for later use
        self.column_name_list = column_name_list
        self.id_to_data_dict = id_to_data_dict

        # Set up the initial values
        self._setup_attributes()
        # Set up the UI
        self._setup_ui()
        # Set up signal connections
        self._setup_signal_connections()

    def _setup_attributes(self):
        """Set up the initial values for the widget.
        """
        # Attributes
        # ----------
        # Store the current grouped column name
        self.grouped_column_name = str()

        #
        self.id_to_tree_item = dict()

        # Private Attributes
        # ------------------
        # Initialize middle button pressed flag
        self._is_middle_button_pressed = False

        # Previous position of the middle mouse button
        self._middle_button_prev_pos = QtCore.QPoint()
        # Initial position of the middle mouse button
        self._middle_button_start_pos = QtCore.QPoint()

        # Timestamp of the last mouse move event
        self._mouse_move_timestamp = float()

        self._row_height = 24

    def _setup_ui(self):
        """Set up the UI for the widget, including creating widgets and layouts.
        """
        # Initializes scroll modes for the widget.
        self.setVerticalScrollMode(QtWidgets.QTreeWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QTreeWidget.ScrollMode.ScrollPerPixel)

        # Set up the context menu for the header
        self.header().setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        # Set up the columns
        self.set_column_name_list(self.column_name_list)
        # Add the data to the widget
        self.add_items(self.id_to_data_dict)

        # Enable sorting in the tree widget
        self.setSortingEnabled(True)

        self.setWordWrap(True)

        # Enable ExtendedSelection mode for multi-select and set the selection behavior to SelectItems
        self.setSelectionMode(QtWidgets.QTreeWidget.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QtWidgets.QTreeWidget.SelectionBehavior.SelectItems)

        self.set_row_height(self._row_height)

    def _setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect signal of header
        self.header().customContextMenuRequested.connect(self._on_header_context_menu)
        
        self.itemExpanded.connect(self.toggle_expansion_for_selected)
        self.itemCollapsed.connect(self.toggle_expansion_for_selected)

        self.header().sortIndicatorChanged.connect(lambda _: self.set_row_height(self._row_height))

        # Key Binds
        # ---------
        # Create a shortcut for the copy action and connect its activated signal
        copy_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence.StandardKey.Copy, self)
        copy_shortcut.activated.connect(self.copy_selected_cells)

    # Private Methods
    # ---------------
    def _on_header_context_menu(self, pos: QtCore.QPoint) -> None:
        """Show a context menu for the header of the tree widget.

        Context Menu:
            +-------------------------------+
            | Grouping                      |
            | - Group by this column        |
            | - Ungroup all                 |
            | ----------------------------- |
            | Visualization                 |
            | - Set Color Adaptive          |
            | - Reset All Color Adaptive    |
            | ----------------------------- |
            | - Fit in View                 |
            | ----------------------------- |
            | Manage Columns                |
            | - Show/Hide Columns >         |
            | - Hide This Column            |
            +-------------------------------+

        Args:
            pos (QtCore.QPoint): The position where the right click occurred.
        """
        # Get the index of the column where the right click occurred
        column = self.header().logicalIndexAt(pos)
        
        # Create the context menu
        # NOTE: Check if the widget has a 'scalable_view' attribute and if it is an instance of QtWidgets.QGraphicsView
        # If 'scalable_view' is available and is an instance of QtWidgets.QGraphicsView, use it as the parent for the menu
        # This ensures that the context menu is displayed correctly within the view
        # Otherwise, use self as the parent for the menu
        if hasattr(self, 'scalable_view') and isinstance(self.scalable_view, QtWidgets.QGraphicsView):
            menu = QtWidgets.QMenu(self.scalable_view)
        else:
            menu = QtWidgets.QMenu(self)

        self.add_label_action(menu, 'Grouping')

        # Create the 'Group by this column' action and connect it to the 'group_by_column' method. Pass in the selected column as an argument.
        group_by_action = menu.addAction('Group by this column')
        group_by_action.triggered.connect(lambda: self.group_by_column(column))

        # Create the 'Ungroup all' action and connect it to the 'ungroup_all' method
        ungroup_all_action = menu.addAction('Ungroup all')
        ungroup_all_action.triggered.connect(self.ungroup_all)

        # Add a separator
        menu.addSeparator()

        self.add_label_action(menu, 'Visualization')

        # Create the 'Set Color Adaptive' action and connect it to the 'apply_column_color_adaptive' method
        apply_color_adaptive_action = menu.addAction('Set Color Adaptive')
        apply_color_adaptive_action.triggered.connect(lambda: self.apply_column_color_adaptive(column))

        # Create the 'Reset All Color Adaptive' action and connect it to the 'reset_all_color_adaptive_column' method
        reset_all_color_adaptive_action = menu.addAction('Reset All Color Adaptive')
        reset_all_color_adaptive_action.triggered.connect(self.reset_all_color_adaptive_column)

        # Add a separator
        menu.addSeparator()

        # Add the 'Fit in View' action and connect it to the 'fit_column_in_view' method
        fit_column_in_view_action = menu.addAction('Fit in View')
        fit_column_in_view_action.triggered.connect(self.fit_column_in_view)

        # Add a separator
        menu.addSeparator()

        self.add_label_action(menu, 'Manage Columns')

        # Disable 'Group by this column' on the first column
        if not column:
            group_by_action.setDisabled(True)

        # Show the context menu
        menu.popup(QtGui.QCursor.pos())

    def add_label_action(self, parent_menu: QtWidgets.QMenu, text: str):
        label = QtWidgets.QLabel(text, parent_menu)
        label.setDisabled(True)
        label.setStyleSheet(
            'color: rgb(144, 144, 144); padding: 0px;'
        )

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        action = QtWidgets.QWidgetAction(parent_menu)
        action.setDefaultWidget(widget)

        parent_menu.addAction(action)

    def _create_item_groups(self, data: List[str]) -> Dict[str, List[TreeWidgetItem]]:
        """Group the data into a dictionary mapping group names to lists of tree items.

        Args:
            data (List[str]): The data to be grouped.

        Returns:
            Dict[str, List[TreeWidgetItem]]: A dictionary mapping group names to lists of tree items.
        """
        # Create a dictionary to store the groups
        groups = {}

        # Group the data
        for i, item_data in enumerate(data):
            # If the data is empty, add it to the '_others' group
            if not item_data:
                item_data = '_others'

            # Add the tree item to the appropriate group
            item = self.topLevelItem(i)
            if item_data in groups:
                groups[item_data].append(item)
            else:
                groups[item_data] = [item]

        return groups

    def _apply_scroll_momentum(self, velocity: QtCore.QPointF, momentum_factor: float = 0.5) -> None:
        """Applies momentum to the scroll bars based on the given velocity.

        Args:
            velocity (QtCore.QPointF): The velocity of the mouse movement.
            momentum_factor (float, optional): The factor to control the momentum strength. Defaults to 0.5.
        """
        # Calculate horizontal and vertical momentum based on velocity and momentum factor
        horizontal_momentum = int(velocity.x() * momentum_factor)
        vertical_momentum = int(velocity.y() * momentum_factor)

        # Scroll horizontally and vertically with animation using the calculated momenta
        self._animate_scroll(self.horizontalScrollBar(), horizontal_momentum)
        self._animate_scroll(self.verticalScrollBar(), vertical_momentum)

    def _animate_scroll(self, scroll_bar: QtWidgets.QScrollBar, momentum: int) -> None:
        """Animates the scrolling of the given scroll bar to the target value over the specified duration.

        Args:
            scroll_bar (QtWidgets.QScrollBar): The scroll bar to animate.
            momentum (int): The momentum value to scroll.
        """
        # Get the current value of the scroll bar
        current_value = scroll_bar.value()
        # Calculate the target value by subtracting the momentum from the current value
        target_value = current_value - momentum

        # Calculate the duration of the animation based on the absolute value of the momentum
        duration = min(abs(momentum) * 20, 500)

        # Get the start time of the animation
        start_time = time.time()

        def _perform_scroll_animation():
            """Animates the scrolling of the given scroll bar to the target value over the specified duration.

            The animation interpolates the scroll bar value from the current value to the target value based on the elapsed time.
            """
            # Access the current_value variable from the enclosing scope
            nonlocal current_value

            # Stop the animation if the middle mouse button is pressed
            if self._is_middle_button_pressed:
                return

            # Calculate the elapsed time since the start of the animation
            elapsed_time = int((time.time() - start_time) * 1000)

            # Check if the elapsed time has reached the duration
            if elapsed_time >= duration:
                # Animation complete
                scroll_bar.setValue(target_value)
                return

            # Calculate the interpolated value based on elapsed time and duration
            progress = elapsed_time / duration
            interpolated_value = int(current_value + (target_value - current_value) * progress)

            # Update the scroll bar value and schedule the next animation frame
            scroll_bar.setValue(interpolated_value)
            QtCore.QTimer.singleShot(10, _perform_scroll_animation)

        # Start the animation
        _perform_scroll_animation()

    # Extended Methods
    # ----------------
    # NOTE: for refactoring
    def set_row_height(self, height):

        if not self.topLevelItem(0):
            return

        self.setUniformRowHeights(True)

        for column_index in range(self.columnCount()):
            size_hint = self.sizeHintForColumn(column_index)
            self.topLevelItem(0).setSizeHint(column_index, QtCore.QSize(size_hint, height))

    def reset_row_height(self):

        if not self.topLevelItem(0):
            return

        self.setUniformRowHeights(False)

        for column_index in range(self.columnCount()):
            size_hint = self.sizeHintForColumn(column_index)
            self.topLevelItem(0).setSizeHint(column_index, QtCore.QSize(size_hint, -1))

    def toggle_expansion_for_selected(self, item):
        """Toggles the expansion state of selected items.

        Args:
            item: The clicked item whose expansion state will be used as a reference.

        Returns:
            None.
        """
        # Get the currently selected items
        selected_items = self.selectedItems()

        # If no items are selected, return early
        if not selected_items:
            return

        # Set the expanded state of all selected items to match the expanded state of the clicked item
        for i in selected_items:
            i.setExpanded(item.isExpanded())

    def get_column_value_range(self, column: int, child_level: int = 0) -> Tuple[Optional[Number], Optional[Number]]:
        """Get the value range of a specific column at a given child level.

        Args:
            column (int): The index of the column.
            child_level (int): The child level to calculate the range for. Defaults to 0 (top-level items).

        Returns:
            Tuple[Optional[Number], Optional[Number]]: A tuple containing the minimum and maximum values,
            or (None, None) if no valid values are found.
        """
        # Get the items at the specified child level
        items = self.get_all_items_at_child_level(child_level)

        # Collect the values from the specified column in the items
        values = [
            item.get_value(column)
            for item in items
            if isinstance(item.get_value(column), Number)
        ]

        # If there are no valid values, return None
        if not values:
            return None, None

        # Calculate the minimum and maximum values
        min_value = min(*values)
        max_value = max(*values)

        # Return the value range
        return min_value, max_value

    def get_all_items_at_child_level(self, child_level: int = 0) -> List[TreeWidgetItem]:
        """Retrieve all items at a specific child level in the tree widget.

        Args:
            child_level (int): The child level to retrieve items from. Defaults to 0 (top-level items).

        Returns:
            List[TreeWidgetItem]: List of `QTreeWidgetItem` objects at the specified child level.
        """
        # If child level is 0, return top-level items
        if not child_level:
            # return top-level items
            return [self.topLevelItem(row) for row in range(self.topLevelItemCount())]

        # Get all items in the tree widget
        all_items = self.get_all_items()

        # Filter items to only those at the specified child level
        return [item for item in all_items if item.get_child_level() == child_level]

    def get_shown_column_index_list(self) -> List[int]:
        """Returns a list of indices for the columns that are shown (i.e., not hidden) in the tree widget.

        Returns:
            List[int]: A list of integers, where each integer is the index of a shown column in the tree widget.
        """
        # Get the header of the tree widget
        header = self.header()

        # Generate a list of the indices of the columns that are not hidden
        column_index_list = [column_index for column_index in range(header.count()) if not header.isSectionHidden(column_index)]

        # Return the list of the index of a shown column in the tree widget.
        return column_index_list

    def apply_column_color_adaptive(self, column: int):
        """Apply adaptive color mapping to a specific column at the appropriate child level determined by the group column.

        This method calculates the minimum and maximum values of the column at the appropriate child level determined by the group column
        and applies an adaptive color mapping based on the data distribution within the column.
        The color mapping dynamically adjusts to the range of values.

        Args:
            column (int): The index of the column to apply the adaptive color mapping.
        """
        # Determine the child level based on the presence of a grouped column
        child_level = 1 if self.grouped_column_name else 0

        # Calculate the minimum and maximum values of the column at the determined child level
        min_value, max_value = self.get_column_value_range(column, child_level)

        # Create and set the adaptive color mapping delegate for the column
        delegate = AdaptiveColorMappingDelegate(self, min_value, max_value)
        self.setItemDelegateForColumn(column, delegate)

    def reset_all_color_adaptive_column(self):
        """Reset the color adaptive for all columns in the tree widget.
        """
        for column in range(self.columnCount()):
            self.setItemDelegateForColumn(column, None)

    def set_column_name_list(self, column_name_list: List[str]) -> None:
        """Set the names of the columns in the tree widget.

        Args:
            column_name_list (List[str]): The list of column names to be set.
        """
        # Store the column names for later use
        self.column_name_list = column_name_list

        # Set the number of columns and the column labels
        self.setColumnCount(len(self.column_name_list))
        self.setHeaderLabels(self.column_name_list)

    def get_column_index(self, column_name: str) -> int:
        """Retrieves the index of the specified column name.

        Args:
            column_name: The name of the column.

        Returns:
            int: The index of the column if found.

        Raises:
            ValueError: If the column name is not found.
        """
        # Check if the column name is not in the column_name_list
        if column_name not in self.column_name_list:
            # Raise an exception with a descriptive error message
            raise ValueError(f"Invalid column name: {column_name}")

        # Return the index of the column if found
        return self.column_name_list.index(column_name)

    def get_column_visual_index(self, column_name: str) -> int:
        """
        """
        #
        return self.header().visualIndex(self.column_name_list.index(column_name))

    def add_items(self, id_to_data_dict: Dict[int, Dict[str, str]]) -> None:
        """Add items to the tree widget.

        Args:
            id_to_data_dict (Dict[int, Dict[str, str]]): A dictionary mapping item IDs to their data as a dictionary.
        """
        # Store the data dictionary for later use
        self.id_to_data_dict = id_to_data_dict

        # Iterate through the dictionary of items
        for item_id, item_data in self.id_to_data_dict.items():
            # Create a new custom QTreeWidgetItem for sorting by type of the item data, and add to the self tree widget
            tree_item = TreeWidgetItem(self, item_data=item_data, item_id=item_id)
            # 
            self.id_to_tree_item[item_id] = tree_item

        # Resize all columns to fit their contents
        self.resize_to_contents()

    def group_by_column(self, column: int) -> None:
        """Group the items in the tree widget by the values in the specified column.

        Args:
            column (int): The index of the column to group by.
        """
        # Ungroup all items in the tree widget
        self.ungroup_all()

        # Hide the grouped column
        self.setColumnHidden(column, True)

        # Get the label for the column that we want to group by and the label for the first column 
        self.grouped_column_name = self.headerItem().text(column)
        first_column_label = self.headerItem().text(0)
        
        # Rename the first column
        self.setHeaderLabel(f'{self.grouped_column_name} / {first_column_label}')
        
        # Get the data for each tree item in the column
        data = [self.topLevelItem(row).data(column, QtCore.Qt.UserRole) for row in range(self.topLevelItemCount())]
        
        # Group the data and add the tree items to the appropriate group
        groups = self._create_item_groups(data)

        # Iterate through each group and its items
        for group_name, items in groups.items():
            # Create a new QTreeWidgetItem for the group
            group_item = TreeWidgetItem(self, [group_name])
            
            # Add the items to the group item as children
            for item in items:
                # Save the original parent and position of the tree item
                original_parent = item.parent()
                original_row = original_parent.indexOfChild(item) if original_parent else self.indexOfTopLevelItem(item)

                # Remove the tree item from its original parent
                if original_parent:
                    original_parent.takeChild(original_row)
                else:
                    self.takeTopLevelItem(original_row)

                # Add the tree item to the group item as a child and restore its original position
                group_item.addChild(item)
            
        # Expand all items
        self.expandAll()

        # Resize first columns to fit their contents
        self.resizeColumnToContents(0)

        # Emit signal for grouped by column with column name
        self.grouped_by_column.emit(self.grouped_column_name)
        
    def fit_column_in_view(self) -> None:
        """Adjust the width of all columns to fit the entire view.
    
            This method resizes columns so that their sum is equal to the width of the view minus the width of the vertical scroll bar. 
            It starts by reducing the width of the column with the largest width by 10% until all columns fit within the expected width.
        """
        # Resize all columns to fit their contents
        self.resize_to_contents()
        
        # Get the expected width of the columns (the width of the view minus the width of the scroll bar)
        expect_column_width = self.size().width() - self.verticalScrollBar().width()
        # Calculate the sum of the current column widths
        column_width_sum = sum(self.columnWidth(column) for column in range(self.columnCount()))
        
        # Loop until all columns fit within the expected width
        while column_width_sum > expect_column_width:
            # Find the column with the largest width
            largest_column = max(range(self.columnCount()), key=lambda x: self.columnWidth(x))
            # Reduce the width of the largest column by 10%
            new_width = max(self.columnWidth(largest_column) - expect_column_width // 10, 0)
            self.setColumnWidth(largest_column, new_width)
            # Update the sum of the column widths
            column_width_sum -= self.columnWidth(largest_column) - new_width

    def resize_to_contents(self) -> None:
        """Resize all columns in the object to fit their contents.
        """
        # Iterate through all columns
        for column_index in range(self.columnCount()):  
            # Resize the column to fit its contents
            self.resizeColumnToContents(column_index) 

    def ungroup_all(self) -> None:
        """Ungroup all the items in the tree widget.
        """
        # Return if there are no groups to ungroup
        if not self.grouped_column_name:
            return

        # Reset the header label
        self.setHeaderLabel(self.column_name_list[0])
        
        # Show hidden column
        column_index = self.get_column_index(self.grouped_column_name)
        self.setColumnHidden(column_index, False)

        # Get a list of all the top-level items in the tree widget
        group_item_list = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]

        # Iterate through all the top-level items in the tree widget
        for group_item in group_item_list:

            # Remove all of its children and add them as top-level items
            child_items = group_item.takeChildren()
            self.addTopLevelItems(child_items)

            # Remove the group item from the top-level items
            self.takeTopLevelItem(self.indexOfTopLevelItem(group_item))

        # Clear the grouped column label
        self.grouped_column_name = str()

        # Resize first columns to fit their contents
        self.resizeColumnToContents(0)

        # Emit signal for ungrouped all
        self.ungrouped_all.emit()
    
    def get_all_items(self) -> List[TreeWidgetItem]:
        """This function returns all the items in the tree widget as a list.

        The items are sorted based on their order in the tree structure, 
        with children appearing after their parent items for each grouping.

        Returns:
            List[TreeWidgetItem]: A list containing all the items in the tree widget.
        """
        def traverse_items(item: TreeWidgetItem):
            # Recursively traverse the children of the current item
            for child_index in range(item.childCount()):
                # Get the child item at the current index
                child = item.child(child_index)

                # Add the current child item to the list
                items.append(child)

                # Recursively traverse the children of the current child item
                traverse_items(child)

        # Get the root item of the tree widget
        root = self.invisibleRootItem()

        # Traverse the items in a depth-first manner and collect them in a list
        items = list()
        traverse_items(root)

        # Return the list of items
        return items

    def copy_selected_cells(self):
        # NOTE: For refactoring
        #
        #
        model = self.selectionModel()
        model_indexes = model.selectedIndexes()

        all_items = self.get_all_items()
        # Sort the cells based on their global row and column
        sorted_indexes = sorted(
            model_indexes, 
            key=lambda model_index: (
                all_items.index(self.itemFromIndex(model_index)),
                model_index.column()
                )
            )

        cell_dict = dict()
        column_set = set()

        for model_index in sorted_indexes:
            tree_item = self.itemFromIndex(model_index)

            global_row = all_items.index(tree_item)
            column = model_index.column()

            cell_value = tree_item.get_value(column)
            cell_text = str() if cell_value is None else str(cell_value)
            cell_text = f'"{cell_text}"' if '\t' in cell_text or '\n' in cell_text else cell_text

            cell_dict.setdefault(global_row, dict())
            cell_dict[global_row][column] = cell_text
            column_set.add(column)

        for row_dict in cell_dict.values():
            for column in column_set:
                row_dict.setdefault(column, str())

        row_texts = list()
        for row_dict in cell_dict.values():
            row_text = '\t'.join(row_dict[column] for column in sorted(column_set))
            row_texts.append(row_text)

        full_text = '\n'.join(row_texts)

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(full_text)

        # Show tooltip message
        self.show_tool_tip(f'Copied:\n{full_text}', 5000)

    def show_tool_tip(self, text: str, msc_show_time: Number = 1000):
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), text, self, QtCore.QRect(), msc_show_time)

    def paste_cells_from_clipboard(self):
        # NOTE: Further Implementation Required
        #
        #
        model = self.selectionModel()
        model_indexes = model.selectedIndexes()

        # Get the text from the clipboard
        clipboard = QtWidgets.QApplication.clipboard()
        text = clipboard.text()
        
        # Split the text into rows and columns
        rows = text.split('\n')
        rows = [row.split('\t') for row in rows]

        # Get the current selected item

        # Get the current row and column

        # Paste the values into the tree widget

        print('Not implement')

    # Event Handling or Override Methods
    # ----------------------------------
    def clear(self):
        self.id_to_tree_item.clear()
        super().clear()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """Handles mouse press event.
        
        Overrides the parent class method to handle the event where the middle mouse button is pressed.
        If the middle button is pressed, sets the cursor to SizeAllCursor.
        
        Args:
            event: The mouse event.
        """
        # Check if middle mouse button is pressed
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            # Set middle button press flag to True
            self._is_middle_button_pressed = True
            # Record the initial position where mouse button is pressed
            self._middle_button_start_pos = event.pos()
            # Change the cursor to SizeAllCursor
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeAllCursor)
        else:
            # If not middle button, call the parent class method to handle the event
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        """Handles mouse release event.
        
        Overrides the parent class method to handle the event where the middle mouse button is released.
        If the middle button is released, restores the cursor to the default.
        
        Args:
            event: The mouse event.
        """
        # Check if middle mouse button is released
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            # Set middle button press flag to False
            self._is_middle_button_pressed = False
            # Calculate the velocity based on the change in mouse position and the elapsed time
            # NOTE: The + 0.01 is added to avoid division by zero
            velocity = (event.pos() - self._middle_button_prev_pos) / ((time.time() - self._mouse_move_timestamp + 0.01))
            # Apply momentum based on velocity
            self._apply_scroll_momentum(velocity)
            # Restore the cursor to default
            QtWidgets.QApplication.restoreOverrideCursor()
        else:
            # If not middle button, call the parent class method to handle the event
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        """Handles mouse move event.
        
        Overrides the parent class method to handle the event where the mouse is moved.
        If the middle button is pressed, adjusts the scroll bar values according to the mouse movement.
        
        Args:
            event: The mouse event.
        """
        # Check if middle mouse button is pressed
        if self._is_middle_button_pressed:
            # Calculate the change in mouse position
            delta = event.pos() - self._middle_button_start_pos

            # Get the scroll bars
            horizontal_scroll_bar = self.horizontalScrollBar()
            vertical_scroll_bar = self.verticalScrollBar()

            # Adjust the scroll bar values according to mouse movement
            horizontal_scroll_bar.setValue(horizontal_scroll_bar.value() - int(delta.x()))
            vertical_scroll_bar.setValue(vertical_scroll_bar.value() - int(delta.y()))

            # Update the previous and start positions of the middle mouse button
            self._middle_button_prev_pos = self._middle_button_start_pos
            self._middle_button_start_pos = event.pos()

            # Set the timestamp of the last mouse move event
            self._mouse_move_timestamp = time.time()
        else:
            # If middle button is not pressed, call the parent class method to handle the event
            super().mouseMoveEvent(event)

def main():
    """Create the application and main window, and show the widget.
    """
    # Create the application and the main window
    app = QtWidgets.QApplication(sys.argv)

    # Set theme of QApplication to the dark theme
    set_theme(app, 'dark')

    # Create an instance of the widget and set it as the central widget
    tree_widget = GroupableTreeWidget(
        column_name_list=COLUMN_NAME_LIST,
        id_to_data_dict=ID_TO_DATA_DICT
    )

    # Show the window and run the application
    tree_widget.show()

    # Run the application
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
