from PyQt5 import QtWidgets, QtCore, QtGui

from typing import Any, Optional, List, Tuple
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
    """Custom PyQt5 Calendar Widget for selecting a range of dates.
    """
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

    def clear(self):
        # Clear any selections made in the calendar
        self.start_date, self.end_date = None, None

        # Set the calendar's selected date to today
        today = QtCore.QDate.currentDate()
        self.setSelectedDate(today)
        self.updateCells()

        # Reset the calendar to the current month
        self.setCurrentPage(QtCore.QDate.currentDate().year(), QtCore.QDate.currentDate().month())

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
        self.tabler_icon = TablerQIcon()

        if self.filter_widget:
            self.update_button_text()
            self.icon = QtGui.QIcon(self.filter_widget.windowIcon())
        # self.__setup_signal_connections()
            
        self.is_active = False

    def __setup_ui(self):
        self.popup_menu = QtWidgets.QMenu(self)

        self.set_filter_widget(self.filter_widget)

        self.setMinimumSize(self.MINIMUM_WIDTH, self.MINIMUM_HEIGHT)
        self.setFixedHeight(self.MINIMUM_HEIGHT)

        self.setProperty('widget-style', 'round')
        self.setStyleSheet(f'''
            QComboBox[widget-style="round"] {{
                padding: 0 0 0 {self.LEFT_PADDING+16};
            }}
        ''')

    def set_active(self, state: bool = True):
        self.is_active = state
        self.setProperty('active', self.is_active)
        self.update_style()
        
    def update_style(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def set_filter_widget(self, widget: 'FilterWidget'):

        if not widget:
            return

        # ...
        self.filter_widget = widget
        # Connect signals
        self.filter_widget.close_requested.connect(self.popup_menu.hide)
        self.filter_widget.label_changed.connect(self.update_button_text)
        self.filter_widget.activated.connect(self.update_active_state)

        self.popup_menu.clear()

        action = QtWidgets.QWidgetAction(self.popup_menu)
        action.setDefaultWidget(self.filter_widget)
        self.popup_menu.addAction(action)
        
    def update_active_state(self):
        self.set_active(self.filter_widget.is_active)

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

    def setIcon(self, icon: QtGui.QIcon):
        self.icon = icon

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)

        # Set the opacity based on the active state
        opacity = 1.0 if self.is_active else 0.6
        painter.setOpacity(opacity)

        icon_size = self.iconSize()
        rect = self.rect()
        iconRect = QtCore.QRect(self.LEFT_PADDING, (rect.height() - icon_size.height()) // 2, icon_size.width()-2, icon_size.height())
        self.icon.paint(painter, iconRect)

class FilterWidget(QtWidgets.QWidget):
    close_requested = QtCore.pyqtSignal(bool)
    label_changed = QtCore.pyqtSignal(str)
    activated = QtCore.pyqtSignal(list)

    # Initialization and Setup
    # ------------------------
    def __init__(self, filter_name: str = str(), parent=None, *args, **kwargs):
        super().__init__(parent, QtCore.Qt.WindowType.Popup, *args, **kwargs)

        # Store the filter name
        self.filter_name = filter_name
        self._is_filter_applied = False

        # Initialize setup
        self.__setup_attributes()
        self.__setup_ui()
        self.__setup_signal_connections()

    def __setup_attributes(self):
        """Set up the initial values for the widget.
        """
        # Attributes
        # ------------------

        # Private Attributes
        # ------------------
        self._saved_state = dict()

    def __setup_ui(self):
        """Set up the UI for the widget, including creating widgets and layouts.
        """
        self.setWindowTitle(self.filter_name)  # Set window title

        self.tabler_icon = TablerQIcon(opacity=0.6)

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Title bar with remove icon
        self.title_widget = QtWidgets.QWidget(self)
        self.title_layout = QtWidgets.QHBoxLayout()
        self.title_widget.setLayout(self.title_layout)

        self.title_layout.setContentsMargins(0, 0, 0, 0)

        self.condition_combo_box = QtWidgets.QComboBox()
        self.condition_combo_box.setProperty('widget-style', 'clean')
        self.condition_combo_box.addItems(['Condition1', 'Condition2'])

        self.clear_button = QtWidgets.QToolButton(self.title_widget)
        self.clear_button.setIcon(self.tabler_icon.clear_all)
        self.clear_button.setToolTip("Clear all")

        self.remove_button = QtWidgets.QToolButton(self.title_widget)
        self.remove_button.setIcon(self.tabler_icon.trash)
        self.remove_button.setToolTip("Remove this filter from Quick Access")

        # Set the style for the hover state
        self.remove_button.setProperty('color', 'red')
        self.title_layout.addWidget(self.condition_combo_box)  # Filter name label
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

        self.apply_button.setProperty('color', 'blue')  # Set object name for styling

    def __setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect signals to slots
        self.apply_button.clicked.connect(self.set_filter_applied)
        self.clear_button.clicked.connect(self.set_filter_applied)
        self.clear_button.clicked.connect(self.clear_state)

        self.cancel_button.clicked.connect(self.discard_change)
        self.apply_button.clicked.connect(self.save_change)
        self.clear_button.clicked.connect(self.clear_filter)
        self.remove_button.clicked.connect(self.remove_filter)

        self.apply_button.clicked.connect(lambda: self.close_requested.emit(True))
        self.cancel_button.clicked.connect(lambda: self.close_requested.emit(False))
        self.clear_button.clicked.connect(self.emit_clear_signals)

    def set_filter_applied(self):
        self._is_filter_applied = True

    def emit_clear_signals(self):
        # Emit the label_changed signal with an empty string to indicate that the condition is cleared
        self.label_changed.emit("")
        # Emit the activated signal with an empty list to indicate no active date range
        self.activated.emit([])

        self.close_requested.emit(True)

    @property
    def is_active(self):
        raise NotImplementedError('')

    def save_state(self, key, value: Any = None):
        """Saves the given state with the specified key.
        """
        self._saved_state[key] = value

    def load_state(self, key, default_value: Any = None):
        """Loads the state associated with the given key.
        """
        return self._saved_state.get(key, default_value)

    def clear_state(self):
        """Clears all saved states.
        """
        self._saved_state.clear()

    # Slot Implementations
    # --------------------
    def discard_change(self):
        """Method to discard changes. This should be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement discard_change")

    def save_change(self):
        """Method to save changes. This should be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement save_change")

    def remove_filter(self):
        """Method to remove the filter. This should be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement remove_filter")

    def clear_filter(self):
        """Method to clear the condition. This should be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement clear_filter")

    # Event Handling or Override Methods
    # ----------------------------------
    def hideEvent(self, event):
        """Overrides the hide event to discard changes if not applying the filter.
        """
        if not self._is_filter_applied:
            self.discard_change()
        else:
            # Reset the flag if the widget is hidden after applying the filter
            self._is_filter_applied = False
        
        super().hideEvent(event)

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
        # ----------
        today = QtCore.QDate.currentDate()
        # Mapping of indices to their corresponding date range logic
        self.date_ranges = {
            1: (today, today),                           # "Today"
            2: (today.addDays(-1), today.addDays(-1)),   # "Yesterday"
            3: (today.addDays(-7), today),               # "Last 7 Days"
            4: (today.addDays(-15), today),              # "Last 15 Days"
            # Add more date ranges here if needed
        }

        self.start_date, self.end_date = None, None

        # Private Attributes
        # ------------------
        ...

    def __setup_ui(self):
        """Set up the UI for the widget, including creating widgets and layouts.
        """
        self.setWindowIcon(self.tabler_icon.calendar)

        # Create widgets and layouts here
        self.calendar = RangeSelectionCalendar(self)
        self.relative_date_combo_box = QtWidgets.QComboBox(self)
        self.relative_date_combo_box.addItems(self.RELATIVE_DATES)

        # Set the layout for the widget
        self.widget_layout.addWidget(self.relative_date_combo_box)
        self.widget_layout.addWidget(self.calendar)

    def __setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect signals to slots
        self.relative_date_combo_box.currentIndexChanged.connect(self.select_relative_date_range)
        self.calendar.range_selected.connect(self.select_absolute_date_range)

    @property
    def is_active(self):
        return self.relative_date_combo_box.currentIndex() != 0 or \
            self.relative_date_combo_box.itemText(0) != self.RELATIVE_DATES[0]

    # Slot Implementations
    # --------------------
    def discard_change(self):
        current_index = self.load_state('current_index', 0)
        self.start_date, self.end_date = self.load_state('date_range', (None, None))
        filter_label = self.load_state('filter_label', str())

        self.relative_date_combo_box.setCurrentIndex(current_index)

        if current_index == 0:
            self.relative_date_combo_box.setItemText(0, filter_label)
        self.calendar.select_date_range(self.start_date, self.end_date)

    def save_change(self):
        
        current_index = self.relative_date_combo_box.currentIndex()
        filter_label = self.relative_date_combo_box.currentText()
        
        date_range = self.get_date_range()
        self.start_date, self.end_date = date_range

        self.save_state('current_index', current_index)
        self.save_state('date_range', date_range)
        self.save_state('filter_label', filter_label)

        start_date_str = self.start_date.toString(QtCore.Qt.DateFormat.ISODate) if self.start_date else str()
        end_date_str = self.end_date.toString(QtCore.Qt.DateFormat.ISODate) if self.end_date else str()

        if start_date_str or end_date_str:
            date_list = get_date_list(start_date_str, end_date_str)
        else:
            date_list = list()
            filter_label = str()

        self.label_changed.emit(filter_label)
        self.activated.emit(date_list)

    def clear_filter(self):
        """Clears the selected date range and resets the relative date selector.
        """
        # Reset the relative date selector to its initial state
        self.relative_date_combo_box.setCurrentIndex(0)
        self.relative_date_combo_box.setItemText(0, self.RELATIVE_DATES[0])

        # Clear any selections made in the calendar
        self.start_date, self.end_date = None, None
        self.calendar.clear()

    def select_relative_date_range(self, index):
        # Reset the first item text if a predefined relative date is selected
        if index > 0:
            self.relative_date_combo_box.setItemText(0, "Selected Date Range")

        start_date, end_date = self.date_ranges.get(index, (None, None))
        self.select_date_range(start_date, end_date)

    def select_absolute_date_range(self, start_date, end_date):
        # Check if end_date is None (single date selection)
        if end_date is None or start_date == end_date:
            formatted_range = start_date.toString(QtCore.Qt.DateFormat.ISODate)
        else:
            formatted_range = f"{start_date.toString(QtCore.Qt.DateFormat.ISODate)} to {end_date.toString(QtCore.Qt.DateFormat.ISODate)}"

        # Update the first item in the relative date selector
        self.relative_date_combo_box.setItemText(0, formatted_range)

        # Set the first item as the current item
        self.relative_date_combo_box.setCurrentIndex(0)

    def get_date_range(self):
        return self.calendar.get_date_range()

    def select_date_range(self, start_date, end_date):
        self.calendar.select_date_range(start_date, end_date)  # Method to be implemented in RangeSelectionCalendar

class MultiSelectFilter(FilterWidget):
    """A widget representing a filter with a checkable tree.
    """

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

    @property
    def is_active(self):
        return bool(self.line_edit.text())

    def restore_checked_state(self, checked_state_dict: dict, parent_item: QtWidgets.QTreeWidgetItem = None):
        parent_item = parent_item or self.tree_widget.invisibleRootItem()

        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            key = child.text(0)
            checked_state = checked_state_dict.get(key, False)
            child.setCheckState(0, checked_state)

            self.restore_checked_state(checked_state_dict, child)

    def get_checked_state_dict(self, checked_state_dict: dict = dict(), parent_item: QtWidgets.QTreeWidgetItem = None):
        parent_item = parent_item or self.tree_widget.invisibleRootItem()

        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            # Assuming the first column is used for unique identification
            key = child.text(0)
            checked_state_dict[key] = child.checkState(0)
            checked_state_dict = self.get_checked_state_dict(checked_state_dict, child)

        return checked_state_dict

    def clear_filter(self):
        """Clears all selections in the tree widget.
        """
        # Uncheck all items in the tree widget
        self.unchecked_all()

        # Clear the line edit
        self.line_edit.clear()

    def unchecked_all(self, parent_item: QtWidgets.QTreeWidgetItem = None):
        """Recursively unchecks all child items.
        """
        parent_item = parent_item or self.tree_widget.invisibleRootItem()

        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            child.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
            self.unchecked_all(child)

    def add_items(self, sequence, shots):
        """Adds items to the tree widget.
        """
        parent_item = QtWidgets.QTreeWidgetItem(self.tree_widget, [sequence])
        parent_item.setFlags(parent_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsAutoTristate)
        parent_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)

        for shot in shots:
            child_item = QtWidgets.QTreeWidgetItem(parent_item, [shot])
            child_item.setFlags(child_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsAutoTristate)
            child_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)

        self.tree_widget.expandAll()

    def get_checked_items(self):
        """Returns the checked items in the tree.
        """
        checked_items = []
        for i in range(self.tree_widget.topLevelItemCount()):
            parent_item = self.tree_widget.topLevelItem(i)
            for j in range(parent_item.childCount()):
                child_item = parent_item.child(j)
                if child_item.checkState(0) == QtCore.Qt.CheckState.Checked:
                    checked_items.append(child_item.text(0))
        return checked_items

    # Slot Implementations
    # --------------------
    def discard_change(self):
        checked_state_dict = self.load_state('checked_state', dict())
        self.restore_checked_state(checked_state_dict)

    def save_change(self):
        checked_state_dict = self.get_checked_state_dict()
        self.save_state('checked_state', checked_state_dict)
        # self.save_state('text_data', self.line_edit.text())

        self.label_changed.emit(self.line_edit.text())
        self.activated.emit(self.get_checked_items())

class FileTypeFilter(FilterWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__setup_ui()
        self.__setup_signal_connections()

    def __setup_ui(self):
        """Set up the UI for the widget, including creating widgets and layouts.
        """
        self.setWindowIcon(self.tabler_icon.file)

        # Preset file type groups with tooltips and extensions
        self.file_type_groups = {
            "Image Sequences": (["exr", "dpx", "jpg", "jpeg"], "Image sequence formats like EXR, DPX"),
            "Video Files": (["mp4", "avi", "mkv", 'mov'], "Video formats like MP4, AVI, MKV"),
            "Audio Files": (["mp3", "wav", "aac"], "Audio formats like MP3, WAV, AAC"),
            "Image Files": (["jpg", "png", "gif"], "Image formats like JPG, PNG, GIF"),
            "Document Files": (["pdf", "docx", "txt"], "Document formats like PDF, DOCX, TXT"),
        }

        self.checkboxes = {}
        for group, (extensions, tooltip) in self.file_type_groups.items():
            checkbox = QtWidgets.QCheckBox(group)
            checkbox.setToolTip(tooltip)
            checkbox.extensions = extensions  # Store the extensions with the checkbox
            self.widget_layout.addWidget(checkbox)
            self.checkboxes[group] = checkbox

        # Custom file type input
        self.custom_input = QtWidgets.QLineEdit()
        self.custom_input.setPlaceholderText("Enter custom file types (e.g., txt)")
        self.custom_input.setProperty('has_placeholder', True)
        self.custom_input.textChanged.connect(self.update_style)
        self.widget_layout.addWidget(self.custom_input)

    def update_style(self):
        self.custom_input.style().unpolish(self.custom_input)
        self.custom_input.style().polish(self.custom_input)

    def __setup_signal_connections(self):
        """Set up signal connections.
        """
        ...

    @property
    def is_active(self):
        """Checks if the filter is active (any file type is selected or custom types are specified).
        """
        # Check if any checkbox is checked
        if any(checkbox.isChecked() for checkbox in self.checkboxes.values()):
            return True

        # Check if there is any text in the custom input
        if self.custom_input.text().strip():
            return True

        # If none of the above conditions are met, return False
        return False


    def get_selected_extensions(self):
        selected_extensions = list()
        
        for checkbox in self.checkboxes.values():
            if not checkbox.isChecked():
                continue

            selected_extensions.extend(checkbox.extensions)

        custom_types = self.get_custom_types()
        selected_extensions.extend(custom_types)

        return list(set(selected_extensions))

    def get_custom_types(self):
        custom_types = self.custom_input.text().strip().split(',')
        custom_types = [ext.strip() for ext in custom_types if ext.strip()]
        return custom_types

    def get_checked_state_dict(self):
        """Returns a dictionary of the checked state for each checkbox.
        """
        return {checkbox.text(): checkbox.isChecked() for checkbox in self.checkboxes.values()}

    def uncheck_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)

    def clear_filter(self):
        """Clears all selections and resets the filter to its initial state.
        """
        # Uncheck all checkboxes
        self.uncheck_all()
        # Clear the custom input field
        self.custom_input.clear()

    # Slot Implementations
    # --------------------
    def save_change(self):
        """Save the changes and emit the filter data.
        """
        custom_types = self.get_custom_types()
        checked_state_dict = self.get_checked_state_dict()
        
        # Save and add custom extensions
        self.save_state('custom_input', custom_types)
        self.save_state('checked_state', checked_state_dict)

        # 
        selected_extensions = self.get_selected_extensions()

        # Emit the signal with the selected file extensions
        self.label_changed.emit(", ".join(selected_extensions))
        self.activated.emit(selected_extensions)

    def discard_change(self):
        """Revert any changes made.
        """
        custom_input = self.load_state('custom_input', list())
        checked_state_dict = self.load_state('checked_state', dict())

        if not checked_state_dict:
            self.uncheck_all()

        # Restore the state of checkboxes from the saved state
        for checkbox_text, checked in checked_state_dict.items():
            self.checkboxes[checkbox_text].setChecked(checked)

        # Restore the text of the custom input from the saved state
        custom_input_text = ', '.join(custom_input)
        self.custom_input.setText(custom_input_text)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    set_theme(app, 'dark')

    main_window = QtWidgets.QMainWindow()
    main_layout = QtWidgets.QHBoxLayout()

    # Date Filter Setup
    date_filter_widget = DateRangeFilterWidget(filter_name="Date")
    date_filter_widget.activated.connect(print)
    date_filter_button = FilterPopupButton(date_filter_widget)
    date_filter_button.setFixedSize(200, 24)

    # Shot Filter Setup
    shot_filter_widget = MultiSelectFilter(filter_name="Shot")
    shot_filter_widget.add_items("100", ["100_010_001", "100_020_050"])
    shot_filter_widget.add_items("101", ["101_022_232", "101_023_200"])
    shot_filter_widget.activated.connect(print)
    shot_filter_button = FilterPopupButton(shot_filter_widget)

    # File Type Filter Setup
    file_type_filter_widget = FileTypeFilter(filter_name="File Type")
    file_type_filter_widget.activated.connect(print)
    file_type_filter_button = FilterPopupButton(file_type_filter_widget)
    file_type_filter_button.setFixedSize(200, 24)

    # Adding widgets to the layout
    main_layout.addWidget(date_filter_button)
    main_layout.addWidget(shot_filter_button)
    main_layout.addWidget(file_type_filter_button)

    main_widget = QtWidgets.QWidget()
    main_widget.setLayout(main_layout)
    main_window.setCentralWidget(main_widget)

    main_window.show()
    app.exec_()

