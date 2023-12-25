from PyQt5 import QtWidgets, QtCore, QtGui

from theme import set_theme
from tablerqicon import TablerQIcon


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

class FilterWidget(QtWidgets.QWidget):
    close_requested = QtCore.pyqtSignal()
    selection_changed = QtCore.pyqtSignal(str)
    def __init__(self, filter_name=str(), parent=None, *args, **kwargs):
        super().__init__(parent, QtCore.Qt.WindowType.Popup, *args, **kwargs)
        self.filter_name = filter_name  # Store the filter name

        self.main_layout = QtWidgets.QVBoxLayout(self)
        # Add specific UI components here
        self.widget_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.widget_layout)
        # Add Confirm and Close buttons
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.confirm_button = QtWidgets.QPushButton("Confirm")
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addWidget(self.confirm_button)
        self.main_layout.addLayout(self.buttons_layout)

        self.cancel_button.clicked.connect(self.request_close)
        self.confirm_button.clicked.connect(self.request_confirm)
        # Connect confirm_button to appropriate slot
        
        self.tabler_icon = TablerQIcon(opacity=0.6)

    def request_close(self):
        # Emit the signal when the close is requested
        self.close_requested.emit()

    def request_confirm(self):

        # NOTE: emit some confirm signal when closing
        self.close_requested.emit()

    def emit_selection_changed(self, selection):
        # Format the text using the filter name and emit the signal
        formatted_text = f"{self.filter_name} • {selection}"
        self.selection_changed.emit(formatted_text)

class FilterPopupButton(QtWidgets.QComboBox):

    MINIMUM_WIDTH, MINIMUM_HEIGHT  = 42, 24
    LEFT_PADDING = 8

    def __init__(self, filter_widget: FilterWidget = None, parent = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.filter_widget = filter_widget

        # Initialize setup
        self.__setup_ui()
        self.tabler_icon = TablerQIcon(opacity=0.6)

        if self.filter_widget:
            self.update_button_text(self.filter_widget.filter_name)
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



    # def __setup_signal_connections(self):
    #     self.clicked.connect(self.show_popup)

    def showPopup(self):
        self.popup_menu.popup(self.mapToGlobal(QtCore.QPoint(0, self.height())))

    def set_filter_widget(self, widget: FilterWidget):

        if not widget:
            return
        # Instantiate and display the filter widget
        self.filter_widget = widget


        self.filter_widget.close_requested.connect(self.popup_menu.hide)
        # Connect the selection_changed signal of the filter widget to the update_button_text slot
        self.filter_widget.selection_changed.connect(self.update_button_text)


        self.popup_menu.clear()

        action = QtWidgets.QWidgetAction(self.popup_menu)
        action.setDefaultWidget(self.filter_widget)
        self.popup_menu.addAction(action)

    def update_button_text(self, text):
        # Slot to update the button's text
        self.setCurrentText(text)

    def setCurrentText(self, text):

        self.clear()
        self.addItem(text)
        super().setCurrentText(text)


class DateRangeFilterWidget(FilterWidget):
    RELATIVE_DATES = ["Selected Date Range", "Today", "Yesterday", "Last 7 Days", "Last 15 Days"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowIcon(self.tabler_icon.calendar)


        today = QtCore.QDate.currentDate()
        # Mapping of indices to their corresponding date range logic
        self.date_ranges = {
            1: (today, today),                           # "Today"
            2: (today.addDays(-1), today.addDays(-1)),   # "Yesterday"
            3: (today.addDays(-7), today),               # "Last 7 Days"
            4: (today.addDays(-15), today),              # "Last 15 Days"
            # Add more date ranges here if needed
        }

        self.calendar = RangeSelectionCalendar(self)
        self.relative_date_selector = QtWidgets.QComboBox(self)
        self.relative_date_selector.addItems(self.RELATIVE_DATES)

        # Layout
        self.widget_layout.addWidget(self.relative_date_selector)
        self.widget_layout.addWidget(self.calendar)

        # Connect signals
        self.relative_date_selector.currentIndexChanged.connect(self.select_relative_date_range)
        self.calendar.range_selected.connect(self.select_absolute_date_range)

    def select_relative_date_range(self, index):
        # Reset the first item text if a predefined relative date is selected
        if index > 0:
            self.relative_date_selector.setItemText(0, "Selected Date Range")

        start_date, end_date = self.date_ranges.get(index, (None, None))
        self.select_date_range(start_date, end_date)

        if index > 0:
            self.emit_selection_changed(self.RELATIVE_DATES[index])


    def select_absolute_date_range(self, start_date, end_date):
        # Check if end_date is None (single date selection)
        if end_date is None or start_date == end_date:
            formatted_range = start_date.toString(QtCore.Qt.ISODate)
        else:
            formatted_range = f"{start_date.toString(QtCore.Qt.ISODate)} to {end_date.toString(QtCore.Qt.ISODate)}"

        # Update the first item in the relative date selector
        self.relative_date_selector.setItemText(0, formatted_range)

        # Set the first item as the current item
        self.relative_date_selector.setCurrentIndex(0)

        self.emit_selection_changed(formatted_range)

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

        self.emit_selection_changed(self.line_edit.text())

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
    date_filter_button = FilterPopupButton(date_filter_widget)

    date_filter_button.setFixedSize(200, 24)
    

    shot_filter_widget = MultiSelectFilter(filter_name="Shot")
    shot_filter_widget.add_items("100", ["100_010_001", "100_020_050"])
    shot_filter_widget.add_items("101", ["101_022_232", "101_023_200"])



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