from typing import Callable, Optional

from PyQt5 import QtWidgets, QtCore, QtGui

class MoveEventFilter(QtCore.QObject):
    def __init__(self, method: Callable, parent: QtCore.QObject = None):
        """Event filter to intercept move events.

        Args:
            method (Callable): A callable object that will be called when a move event occurs.
            parent (QtCore.QObject): The parent QObject. Defaults to None.
        """
        super().__init__(parent)
        self.method = method

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """Filters and handles the events for the given object.

        Args:
            obj (QtCore.QObject): The QObject being filtered.
            event (QtCore.QEvent): The QEvent being filtered.

        Returns:
            bool: True if the event was handled, False otherwise.
        """
        if event.type() == QtCore.QEvent.Move:
            self.method()
            return True
        return super().eventFilter(obj, event)

class PopupWidget(QtWidgets.QWidget):
    """A popup widget that contains a tree widget.

    Attributes:
        _relative_offset (QtCore.QPoint): The relative offset between the popup widget and the top parent widget.
    """
    # Class constant
    INITIAL_POSITION_OFFSET = QtCore.QPoint(-140, 30)

    # Initialization and Setup
    # ------------------------
    def __init__(self, widget: QtWidgets.QWidget, parent: Optional[QtWidgets.QWidget] = None):
        """Initialize the popup widget and set up the UI, signal connections, and position.

        Args:
            widget: The widget to be added to the popup widget.
            parent: The parent widget. Defaults to None.
        """
        super().__init__(parent)

        self.widget = widget

        self._setup_initial_values()
        self._setup_ui()
        self._setup_signal_connections()

    def _setup_initial_values(self):
        """Set up the initial values for the popup widget.
        """
        self.dragging = False

        self._relative_offset = QtCore.QPoint(0, 0)

        self.opacity_animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.opacity_animation.setDuration(200)

        self.top_parent = self._get_top_parent() or self.parent()

    def _setup_ui(self):
        """Set up the UI for the popup widget, including creating widgets and layouts.
        """
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setMouseTracking(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.widget)

        self.close_button = QtWidgets.QPushButton('Close')
        layout.addWidget(self.close_button)

        self.setLayout(layout)

        self._set_initial_position()

    def _setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        self.close_button.clicked.connect(self.close)

        self.widget.mousePressEvent = self.mousePressEvent
        self.widget.mouseMoveEvent = self.mouseMoveEvent
        self.widget.mouseReleaseEvent = self.mouseReleaseEvent

        event_filter = MoveEventFilter(self._update_position, self.top_parent)
        self.top_parent.installEventFilter(event_filter)

    # Private Methods
    # ---------------
    def _get_top_parent(self) -> Optional[QtWidgets.QWidget]:
        """Returns the top-level parent widget of the popup widget.

        Returns:
            QtWidgets.QWidget or None: The top-level parent widget, or None if not found.
        """
        # Get the immediate parent widget of the popup widget
        current_parent = self.parent()

        # Traverse up the parent hierarchy until reaching the top-level parent
        while current_parent and current_parent.parent():
            current_parent = current_parent.parent()

        return current_parent

    def _update_relative_offset(self):
        """Update the relative offset between the popup widget and the parent widget.
        """
        self._relative_offset = self.pos() - self.top_parent.pos()

    def _update_position(self):
        """Update the position of the popup widget based on the button's location and the relative offset.
        """
        parent_pos = self.top_parent.pos() + self._relative_offset
        self.move(parent_pos)

    def _set_initial_position(self):
        """Set the initial position of the popup widget based on the instance's position.
        """
        cursor_pos = QtGui.QCursor.pos() + self.INITIAL_POSITION_OFFSET
        self.move(cursor_pos)

    # Event Handling or Override Methods
    # ----------------------------------
    def enterEvent(self, event):
        """Event handler for when the mouse enters the popup widget.
        """
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Event handler for when the mouse leaves the popup widget.
        """
        self.opacity_animation.setEndValue(0.5)
        self.opacity_animation.start()
        super().leaveEvent(event)

    def setVisible(self, visible: bool):
        """Show or hide the popup widget and update the position.

        Args:
            visible: True to show the widget, False to hide it.
        """
        self._set_initial_position()
        self._update_relative_offset()
        return super().setVisible(visible)

    def mousePressEvent(self, event):
        """Event handler for when a mouse button is pressed within the popup widget.
        """
        if event.button() == QtCore.Qt.MiddleButton:
            self.drag_start_position = event.globalPos()
            self.dragging = True
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Event handler for when the mouse is moved within the popup widget.
        """
        if self.dragging:
            delta = event.globalPos() - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = event.globalPos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Event handler for when a mouse button is released within the popup widget.
        """
        if event.button() == QtCore.Qt.MiddleButton:
            self.dragging = False
            self._update_relative_offset()
        else:
            super().mouseReleaseEvent(event)
