import sys
from typing import Tuple

from PyQt5 import QtWidgets, QtCore, QtGui
from tablerqicon import TablerQIcon

class RangeCalendarWidget(QtWidgets.QCalendarWidget):
    """Custom PyQt5 Calendar Widget for selecting a range of dates.
    
    Attributes:
        start_date (QtCore.QDate): The start date of the selected range.
        end_date (QtCore.QDate): The end date of the selected range.
        _is_shift_pressed (bool): Internal state to track shift key press.
    """
    # Signal emitted when a date range is selected. It passes the start and end dates.
    range_selected = QtCore.pyqtSignal(QtCore.QDate, QtCore.QDate)

    # Class constants
    HIGHLIGHT_COLOR = QtGui.QColor(0, 150, 255, 51)

    # Initialization and Setup
    # ------------------------
    def __init__(self, parent: QtWidgets.QWidget = None):
        """Initialize the custom calendar widget.
        """
        super().__init__(parent)

        # Initialize setup
        self.__setup_attributes()
        self.__setup_ui()
        self.__setup_signal_connections()

    def __setup_attributes(self):
        """Set up the initial values for the widget.
        """
        # Attributes
        # ----------
        self.start_date, self.end_date = None, None

        # Private Attributes
        # ------------------
        self._is_shift_pressed = False

    def __setup_ui(self):
        """Set up the UI for the widget, including creating widgets and layouts.
        """
        # Create widgets and layouts
        self.tabler_icon = TablerQIcon(opacity=0.6)

        # Find the previous and next month buttons and set their icons
        self.qt_calendar_prevmonth_button = self.findChild(QtWidgets.QToolButton, 'qt_calendar_prevmonth')
        self.qt_calendar_prevmonth_button.setIcon(self.tabler_icon.chevron_left)
        self.qt_calendar_nextmonth_button = self.findChild(QtWidgets.QToolButton, 'qt_calendar_nextmonth')
        self.qt_calendar_nextmonth_button.setIcon(self.tabler_icon.chevron_right)

        # Find the month and year buttons
        self.qt_calendar_monthbutton = self.findChild(QtWidgets.QToolButton, 'qt_calendar_monthbutton')
        self.qt_calendar_yearbutton = self.findChild(QtWidgets.QToolButton, 'qt_calendar_yearbutton')

    def __setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect signals to slots
        self.clicked.connect(self.handle_date_clicked)
        self.range_selected.connect(self.select_date_range)

    # Extended Methods
    # ----------------
    def handle_date_clicked(self, date: QtCore.QDate):
        """Handles the logic when a date is clicked on the calendar.

        If shift is pressed and a start date exists, it selects an end date to form a range.
        Otherwise, it resets to a new start date.

        Args:
            date (QtCore.QDate): The date that was clicked.
        """
        # Check if the shift key is pressed and a start date has already been selected, the clicked date becomes the end date
        if self._is_shift_pressed and self.start_date:
            self.end_date = date

            # Swap dates if start date is greater than end date
            if self.start_date > self.end_date:
                self.start_date, self.end_date = self.end_date, self.start_date

        else:
            # Set or reset the start date and end date to the clicked date
            self.start_date = self.end_date = date

        # Emit the range_selected signal with the start and end dates
        self.range_selected.emit(self.start_date, self.end_date)

        # Update the calendar display to reflect the new selection
        self.updateCells()

    def clear(self):
        """Clears any date selections and resets the calendar to the current date, and updates the calendar display to reflect these changes.
        """
        # Clear any selections made in the calendar
        self.start_date, self.end_date = None, None

        # Set the calendar's selected date to today
        today = QtCore.QDate.currentDate()
        self.setSelectedDate(today)

        # Refresh the calendar display
        self.updateCells()

        # Reset the calendar to the current month
        self.setCurrentPage(today.year(), today.month())

    def get_date_range(self) -> Tuple[QtCore.QDate, QtCore.QDate]:
        """Retrieves the currently selected date range.

        Returns:
            Tuple[QtCore.QDate, QtCore.QDate]: A tuple containing the start and end dates
                of the selected range. If no range is selected, both values in the tuple will be None.
        """
        return self.start_date, self.end_date

    def select_date_range(self, start_date: QtCore.QDate, end_date: QtCore.QDate):
        """Selects a date range in the calendar.

        Args:
            start_date (QtCore.QDate): The start date of the range to be selected.
            end_date (QtCore.QDate): The end date of the range to be selected.
        """
        # Set the start and end dates for the calendar
        self.start_date, self.end_date = start_date, end_date

        # Determine which date to focus on in the calendar view
        date_to_show = end_date or start_date or QtCore.QDate.currentDate()
        self.setSelectedDate(date_to_show)

        # Refresh the calendar display
        self.updateCells()

    # Private Methods
    # ---------------
    def _update_shift_state(self, event: QtGui.QKeyEvent):
        """Updates the state of the shift key.

        Args:
            event (QtGui.QKeyEvent): The key event.
        """
        self._is_shift_pressed = event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier

    # Event Handling or Override Methods
    # ----------------------------------
    def paintCell(self, painter: QtGui.QPainter, rect: QtCore.QRect, date: QtCore.QDate):
        """Custom painting for calendar cells.

        Overrides the default cell painting to highlight the range of selected dates.

        Args:
            painter (QtGui.QPainter): The painter used to draw the cell.
            rect (QtCore.QRect): The rectangle area of the cell.
            date (QtCore.QDate): The date of the cell being painted.
        """
        super().paintCell(painter, rect, date)

        # Return early if the date is outside the selected range or if either the start or end date is not set.
        if not (self.start_date and self.end_date and self.start_date <= date <= self.end_date):
            return

        # Fill the cell with the highlight color
        painter.fillRect(rect, self.HIGHLIGHT_COLOR)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Handles key press events for the calendar.

        Specifically, updates the shift key state when a key is pressed.
        """
        super().keyPressEvent(event)

        # Updates the shift key state when a key is pressed.
        self._update_shift_state(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        """Handles key release events for the calendar.

        Specifically, updates the shift key state when a key is released.
        """
        super().keyReleaseEvent(event)

        # Updates the shift key state when a key is pressed.
        self._update_shift_state(event)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    calendar_widget = RangeCalendarWidget()
    calendar_widget.show()
    sys.exit(app.exec_())
