from PyQt5 import QtWidgets, QtCore, QtGui

from typing import Optional, List, Tuple
from datetime import datetime, timedelta

from tablerqicon import TablerQIcon
from theme import set_theme

def get_date_list(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_relative: Optional[int] = None,
        date_format: str = '%Y-%m-%d'
    ) -> List[str]:
    """Generates a list of dates within a specified range, or relative to the current date.

    Args:
        start_date: Start date in 'YYYY-MM-DD' format or None. Used if days_relative is None.
        end_date: End date in 'YYYY-MM-DD' format or None. Used if days_relative is None.
        days_relative: Number of days relative to today. Positive for future, negative for past.
        date_format: Desired format of the date strings.

    Returns:
        A list of date strings in the specified range.

    Raises:
        ValueError: If neither days_relative nor both start_date and end_date are specified.

    Examples:
        >>> get_date_list(start_date='2023-01-01', end_date='2023-01-03')
        ['2023-01-01', '2023-01-02', '2023-01-03']
    """
    if days_relative is not None:
        # Calculate date range based on days relative to today
        reference_date = datetime.now()
        start_date, end_date = sorted([reference_date, reference_date + timedelta(days=days_relative)])

    elif start_date and end_date:
        # Parse given start and end dates based on date_format
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)

    else:
        # Ensure valid input is provided
        raise ValueError("Either specify days_relative or both start_date and end_date")

    # Generate list of formatted date strings in the range
    return [(start_date + timedelta(days=i)).strftime(date_format) for i in range((end_date - start_date).days + 1)]


class RangeSelectionCalendar(QtWidgets.QCalendarWidget):
    """Custom PyQt5 Calendar Widget for selecting a range of dates."""
    range_selected = QtCore.pyqtSignal(QtCore.QDate, QtCore.QDate)

    # Initialization and Setup
    # ------------------------
    def __init__(self, parent=None):
        """Initialize the custom calendar widget.
        """
        super().__init__(parent)

        self.start_date = None
        self.end_date = None
        self.is_shift_pressed = False
        self.clicked.connect(self.handle_date_clicked)
        self.range_selected.connect(self.select_date_range)
        self.tabler_icon = TablerQIcon(opacity=0.6)

        self.qt_calendar_prevmonth_button = self.findChild(QtWidgets.QToolButton, 'qt_calendar_prevmonth')
        self.qt_calendar_prevmonth_button.setIcon(self.tabler_icon.chevron_left)
        self.qt_calendar_nextmonth_button = self.findChild(QtWidgets.QToolButton, 'qt_calendar_nextmonth')
        self.qt_calendar_nextmonth_button.setIcon(self.tabler_icon.chevron_right)

        self.qt_calendar_monthbutton = self.findChild(QtWidgets.QToolButton, 'qt_calendar_monthbutton')
        self.qt_calendar_yearbutton = self.findChild(QtWidgets.QToolButton, 'qt_calendar_yearbutton')

    def handle_date_clicked(self, date):
        """Handles the logic when a date is clicked on the calendar.

        If shift is pressed and a start date exists, it selects an end date to form a range.
        Otherwise, it resets to a new start date.

        Args:
            date (QtCore.QDate): The date that was clicked.
        """
        if self.is_shift_pressed and self.start_date:
            self.end_date = date

            # Swap dates if start date is greater than end date using a more Pythonic approach
            if self.start_date > self.end_date:
                self.start_date, self.end_date = self.end_date, self.start_date

        else:
            # Set or reset the start date and end date to the clicked date
            self.start_date = self.end_date = date

        # ...
        self.range_selected.emit(self.start_date, self.end_date)

        # Update the calendar display to reflect the new selection
        self.updateCells()

    def paintCell(self, painter, rect, date):
        
        super().paintCell(painter, rect, date)
        if self.start_date and self.start_date <= date:
            if self.end_date and date <= self.end_date:
                painter.fillRect(rect, QtGui.QColor(0, 150, 255, 50))

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        super().keyPressEvent(event)
        self.update_shift_state(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        super().keyReleaseEvent(event)
        self.update_shift_state(event)

    def update_shift_state(self, event: QtGui.QKeyEvent):
        self.is_shift_pressed = event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier

    def get_date_range(self) -> Tuple[QtCore.QDate, QtCore.QDate]:
        return self.start_date, self.end_date

    def select_date_range(self, start_date, end_date):
        self.start_date, self.end_date = start_date, end_date

        if end_date:
            # Update the calendar's selection
            self.setSelectedDate(end_date)
        elif start_date:
            self.setSelectedDate(start_date)
        else:
            self.setSelectedDate(QtCore.QDate.currentDate())
        # Refresh the calendar display
        self.updateCells()

class FilterPopupButton(QtWidgets.QComboBox):

    MINIMUM_WIDTH, MINIMUM_HEIGHT  = 42, 24
    LEFT_PADDING = 8

    def __init__(self, filter_widget: 'FilterWidget' = None, parent = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.filter_widget = filter_widget

        # Initialize setup
        self.__setup_ui()
        self.tabler_icon = TablerQIcon(opacity=0.6)

        if self.filter_widget:
            self.update_button_text()
            self.icon = QtGui.QIcon(self.filter_widget.windowIcon())
        # self.__setup_signal_connections()

    def __setup_ui(self):
        self.popup_menu = QtWidgets.QMenu(self)

        self.set_filter_widget(self.filter_widget)

        self.setMinimumSize(self.MINIMUM_WIDTH, self.MINIMUM_HEIGHT)
        self.setFixedHeight(self.MINIMUM_HEIGHT)

        self.setStyleSheet(f'''
            QComboBox {{
                background-color: transparent;
                color: rgb(144, 144, 144);
                text-align: left;
                padding: 0 0 0 {self.LEFT_PADDING+16};
                border-radius: 12px;
            }}
            QComboBox:focus {{
                border-color: rgb(125, 134, 138);
            }}
        ''')

    def setIcon(self, icon: QtGui.QIcon):
        self.icon = icon

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        iconSize = self.iconSize()
        rect = self.rect()
        iconRect = QtCore.QRect(self.LEFT_PADDING, (rect.height() - iconSize.height()) // 2, iconSize.width()-2, iconSize.height())
        self.icon.paint(painter, iconRect)


    def set_filter_widget(self, widget: 'FilterWidget'):

        if not widget:
            return

        # ...
        self.filter_widget = widget
        # Connect signals
        self.filter_widget.close_requested.connect(self.popup_menu.hide)
        self.filter_widget.label_changed.connect(self.update_button_text)

        self.popup_menu.clear()

        action = QtWidgets.QWidgetAction(self.popup_menu)
        action.setDefaultWidget(self.filter_widget)
        self.popup_menu.addAction(action)

    def update_button_text(self, text: str = str(), use_format: bool = True):
        
        if use_format:
            text = f"{self.filter_widget.filter_name} • {text}"

        # Update the button's text
        self.setCurrentText(text)

    # Event Handling or Override Methods
    # ----------------------------------
    def setCurrentText(self, text):
        self.clear()
        self.addItem(text)
        super().setCurrentText(text)

    def showPopup(self):
        self.popup_menu.popup(self.mapToGlobal(QtCore.QPoint(0, self.height())))

class FilterWidget(QtWidgets.QWidget):
    close_requested = QtCore.pyqtSignal(bool)
    label_changed = QtCore.pyqtSignal(str)
    activated = QtCore.pyqtSignal(list)

    def __init__(self, filter_name: str = str(), parent=None, *args, **kwargs):
        super().__init__(parent, QtCore.Qt.WindowType.Popup, *args, **kwargs)

        # Store the filter name
        self.filter_name = filter_name

        # Initialize setup
        self.__setup_ui()
        self.__setup_signal_connections()

    def __setup_ui(self):
        """Set up the UI for the widget, including creating widgets and layouts."""
        self.setWindowTitle(self.filter_name)  # Set window title

        self.tabler_icon = TablerQIcon(opacity=0.6)

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Title bar with remove icon
        self.title_widget = QtWidgets.QWidget(self)
        self.title_layout = QtWidgets.QHBoxLayout()
        self.title_widget.setLayout(self.title_layout)


        self.title_layout.setContentsMargins(0, 0, 0, 0)

        self.condition_selector = QtWidgets.QComboBox()  # Dropdown for selecting condition
        self.title_widget.setStyleSheet('''
            QComboBox {
                padding: 0 0;
                border: None;
                text-align: left;
                font-size: 12px;
            }
            QComboBox:hover {
                color: rgb(210, 210, 210);
            }
                                              ''')

        self.condition_selector.addItems(['Condition1', 'Condition2'])
        self.clear_button = QtWidgets.QToolButton(self.title_widget)
        self.clear_button.setIcon(self.tabler_icon.clear_all)
        self.clear_button.setToolTip("Clear all")

        self.remove_button = QtWidgets.QToolButton(self.title_widget)
        self.remove_button.setIcon(self.tabler_icon.trash)
        self.remove_button.setToolTip("Remove this filter from Quick Access")

        # Set the style for the hover state
        self.remove_button.setStyleSheet("""
            QToolButton:hover {
                background-color: #8B0000;  /* Dark Red */
            }
        """)
        self.title_layout.addWidget(self.condition_selector)  # Filter name label
        self.title_layout.addStretch()  # Pushes the remove button to the right
        self.title_layout.addWidget(self.clear_button)
        self.title_layout.addWidget(self.remove_button)
        
        self.main_layout.addWidget(self.title_widget)

        # Widget-specific content area
        self.widget_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.widget_layout)

        # Add Confirm and Cancel buttons
        self.buttons_widget = QtWidgets.QWidget(self)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.apply_button = QtWidgets.QPushButton("Apply Filter")  # Renamed Confirm to Apply Filter
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addWidget(self.apply_button)
        self.main_layout.addWidget(self.buttons_widget)


        self.buttons_widget.setStyleSheet('''

            QPushButton {
                border: 0px solid;
                border-radius: 4px;  /* Rounded corners */
                padding: 4px 8;  /* Padding around text */
                background-color: #333;  /* Dark background for buttons */
                color: #ddd;  /* Light text */
            }
            QPushButton:hover {
                background-color: #555;  /* Slightly lighter background on hover */
            }
            QPushButton:pressed {
                background-color: #444;  /* Darker background when pressed */
            }
            QPushButton#ApplyButton {
                background-color: #4CAF50;  /* A green background for the apply button */
                color: white;  /* White text for contrast */
            }
            QPushButton#ApplyButton:hover {
                background-color: #5DBF60;  /* Slightly lighter on hover */
            }
        ''')

        self.apply_button.setObjectName("ApplyButton")  # Set object name for styling


    def __setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect signals to slots
        self.cancel_button.clicked.connect(self.discard_change)
        self.apply_button.clicked.connect(self.save_change)

        self.cancel_button.clicked.connect(lambda: self.close_requested.emit(False))
        self.apply_button.clicked.connect(lambda: self.close_requested.emit(True))
        self.remove_button.clicked.connect(self.remove_filter)
        self.clear_button.clicked.connect(self.clear_condition)

    def discard_change(self):
        """Method to discard changes. This should be implemented in subclasses."""
        raise NotImplementedError("Subclasses must implement discard_change")

    def save_change(self):
        """Method to save changes. This should be implemented in subclasses."""
        raise NotImplementedError("Subclasses must implement save_change")

    def remove_filter(self):
        """Method to remove the filter. This should be implemented in subclasses."""
        raise NotImplementedError("Subclasses must implement remove_filter")

    def clear_condition(self):
        """Method to clear the condition. This should be implemented in subclasses."""
        raise NotImplementedError("Subclasses must implement clear_condition")

class DateRangeFilterWidget(FilterWidget):
    RELATIVE_DATES = ["Selected Date Range", "Today", "Yesterday", "Last 7 Days", "Last 15 Days"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize setup
        self.__setup_attributes()
        self.__setup_ui()
        self.__setup_signal_connections()

    def __setup_attributes(self):
        """Set up the initial values for the widget.
        """
        # Attributes
        # ------------------
        today = QtCore.QDate.currentDate()
        # Mapping of indices to their corresponding date range logic
        self.date_ranges = {
            1: (today, today),                           # "Today"
            2: (today.addDays(-1), today.addDays(-1)),   # "Yesterday"
            3: (today.addDays(-7), today),               # "Last 7 Days"
            4: (today.addDays(-15), today),              # "Last 15 Days"
            # Add more date ranges here if needed
        }

        self.filter_label = str()
        self.current_index = int()
        self.start_date, self.end_date = None, None
        # self.relative_date_selector.currentText()

        # Private Attributes
        # ------------------
        ...

    def __setup_ui(self):
        """Set up the UI for the widget, including creating widgets and layouts.
        """
        self.setWindowIcon(self.tabler_icon.calendar)

        # Create widgets and layouts here
        self.calendar = RangeSelectionCalendar(self)
        self.relative_date_selector = QtWidgets.QComboBox(self)
        self.relative_date_selector.addItems(self.RELATIVE_DATES)

        # Set the layout for the widget
        self.widget_layout.addWidget(self.relative_date_selector)
        self.widget_layout.addWidget(self.calendar)

    def __setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect signals to slots
        self.relative_date_selector.currentIndexChanged.connect(self.select_relative_date_range)
        self.calendar.range_selected.connect(self.select_absolute_date_range)

    def discard_change(self):
        self.relative_date_selector.setCurrentIndex(self.current_index)

        if self.current_index == 0:
            self.relative_date_selector.setItemText(0, self.filter_label)
        self.calendar.select_date_range(self.start_date, self.end_date)

    def save_change(self):
        
        self.current_index = self.relative_date_selector.currentIndex()
        self.filter_label = self.relative_date_selector.currentText()
        
        self.start_date, self.end_date = self.get_date_range()

        start_date_str = self.start_date.toString(QtCore.Qt.DateFormat.ISODate)
        end_date_str = self.end_date.toString(QtCore.Qt.DateFormat.ISODate)

        date_list = get_date_list(start_date_str, end_date_str)

        self.label_changed.emit(self.filter_label)
        self.activated.emit(date_list)

    def select_relative_date_range(self, index):
        # Reset the first item text if a predefined relative date is selected
        if index > 0:
            self.relative_date_selector.setItemText(0, "Selected Date Range")

        start_date, end_date = self.date_ranges.get(index, (None, None))
        self.select_date_range(start_date, end_date)

    def select_absolute_date_range(self, start_date, end_date):
        # Check if end_date is None (single date selection)
        if end_date is None or start_date == end_date:
            formatted_range = start_date.toString(QtCore.Qt.DateFormat.ISODate)
        else:
            formatted_range = f"{start_date.toString(QtCore.Qt.DateFormat.ISODate)} to {end_date.toString(QtCore.Qt.DateFormat.ISODate)}"

        # Update the first item in the relative date selector
        self.relative_date_selector.setItemText(0, formatted_range)

        # Set the first item as the current item
        self.relative_date_selector.setCurrentIndex(0)

    def get_date_range(self):
        return self.calendar.get_date_range()

    def select_date_range(self, start_date, end_date):
        self.calendar.select_date_range(start_date, end_date)  # Method to be implemented in RangeSelectionCalendar

class MultiSelectFilter(FilterWidget):
    """A widget representing a filter with a checkable tree."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowIcon(self.tabler_icon.list_check)

        self.line_edit = QtWidgets.QLineEdit(self)

        self.tree_widget = QtWidgets.QTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setRootIsDecorated(False)

        self.widget_layout.addWidget(self.line_edit)
        self.widget_layout.addWidget(self.tree_widget)
        self.tree_widget.itemChanged.connect(self.update_line_edit_as_checked)

    def update_line_edit_as_checked(self):
        self.line_edit.setText(', '.join(self.get_checked_items()))

    def discard_change(self):
        self.load_state()

    def save_change(self):
        self.save_state()
        self.label_changed.emit(self.line_edit.text())
        self.activated.emit(self.get_checked_items())

    def load_state(self):
        self._load_state_recursive(self.tree_widget.invisibleRootItem())
        # self.line_edit.setText(self.text_data)

    def _load_state_recursive(self, item: QtWidgets.QTreeWidgetItem):
        for i in range(item.childCount()):
            child = item.child(i)
            key = child.text(0)
            if key in self.state:
                child.setCheckState(0, self.state[key])
            self._load_state_recursive(child)

    def save_state(self):
        self.state = {}
        self._save_state_recursive(self.tree_widget.invisibleRootItem())
        # self.text_data = self.line_edit.text()

    def _save_state_recursive(self, item):
        for i in range(item.childCount()):
            child = item.child(i)
            # Assuming the first column is used for unique identification
            key = child.text(0)
            self.state[key] = child.checkState(0)
            self._save_state_recursive(child)

    def add_items(self, sequence, shots):
        """Adds items to the tree widget."""
        parent_item = QtWidgets.QTreeWidgetItem(self.tree_widget, [sequence])
        parent_item.setFlags(parent_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsAutoTristate)
        parent_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)

        for shot in shots:
            child_item = QtWidgets.QTreeWidgetItem(parent_item, [shot])
            child_item.setFlags(child_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsAutoTristate)
            child_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)

        self.tree_widget.expandAll()

    def on_item_changed(self, item, column):
        """Handles item change events."""
        print(self.get_checked_items())

    def get_checked_items(self):
        """Returns the checked items in the tree."""
        checked_items = []
        for i in range(self.tree_widget.topLevelItemCount()):
            parent_item = self.tree_widget.topLevelItem(i)
            for j in range(parent_item.childCount()):
                child_item = parent_item.child(j)
                if child_item.checkState(0) == QtCore.Qt.CheckState.Checked:
                    checked_items.append(child_item.text(0))
        return checked_items

    # def focusOutEvent(self, event):
    #     self.hide()
    #     super().focusOutEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    set_theme(app, 'dark')

    main_window = QtWidgets.QMainWindow()
    main_layout = QtWidgets.QHBoxLayout()

    date_filter_widget = DateRangeFilterWidget(filter_name="Date")
    date_filter_widget.activated.connect(print)
    
    date_filter_button = FilterPopupButton(date_filter_widget)

    date_filter_button.setFixedSize(200, 24)
    

    shot_filter_widget = MultiSelectFilter(filter_name="Shot")
    shot_filter_widget.add_items("100", ["100_010_001", "100_020_050"])
    shot_filter_widget.add_items("101", ["101_022_232", "101_023_200"])
    shot_filter_widget.activated.connect(print)

    shot_filter_button = FilterPopupButton(shot_filter_widget)
    
    main_layout.addWidget(date_filter_button)
    main_layout.addWidget(shot_filter_button)

    main_widget = QtWidgets.QWidget()
    main_widget.setLayout(main_layout)
    main_window.setCentralWidget(main_widget)

    main_window.show()
    # import tablerqicon
    # main_window.setWindowIcon(tablerqicon.TablerQIcon.select)
    app.exec_()
