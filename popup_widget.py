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
        if event.type() == QtCore.QEvent.Type.Move:
            self.method()
            return True
        return super().eventFilter(obj, event)

class PopupWidget(QtWidgets.QWidget):
    """A popup widget that contains a tree widget.

    Attributes:
        _relative_offset (QtCore.QPoint): The relative offset between the popup widget and the top parent widget.
    """
    # Class constants
    # ---------------
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

        # Store the widget
        self.widget = widget

        # Set up the initial values
        self._setup_attributes()
        # Set up the UI
        self._setup_ui()
        # Set up signal connections
        self._setup_signal_connections()

    def _setup_attributes(self):
        """Set up the initial values for the popup widget.
        """
        # Initialize _is_dragging state
        self._is_dragging = False

        # Relative offset between the popup widget and the top parent widget
        self._relative_offset = QtCore.QPoint(0, 0)

        # Create an opacity animation for visual effects
        self._opacity_animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self._opacity_animation.setDuration(200)

        # Determine the top parent widget of the popup widget
        self.top_parent = self._get_top_parent() or self.parent()

    def _setup_ui(self):
        """Set up the UI for the popup widget, including creating widgets and layouts.
        """
        # Window properties
        self.setWindowFlags(QtCore.Qt.WindowType.SplashScreen)
        self.setMinimumSize(400, 200)
        self.setMouseTracking(True)

        # Create a vertical layout to hold the content of the popup widget.
        layout = QtWidgets.QVBoxLayout()

        # Add the widget to the layout
        layout.addWidget(self.widget)

        # Add a close button to the layout
        self.close_button = QtWidgets.QPushButton('Close')
        layout.addWidget(self.close_button)

        # Set the layout for the popup widget
        self.setLayout(layout)

        # Set the initial position of the popup widget
        self._set_initial_position()

    def _setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect the clicked signal of the close button to the close method
        self.close_button.clicked.connect(self.close)

        # Assign mouse event handlers to the widget
        self.widget.mousePressEvent = self.mousePressEvent
        self.widget.mouseMoveEvent = self.mouseMoveEvent
        self.widget.mouseReleaseEvent = self.mouseReleaseEvent

        # Create an event filter to handle move events of the top parent
        event_filter = MoveEventFilter(self._update_position, self.top_parent)

        # Install the event filter on the top parent widget
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
        # Calculate the relative offset by subtracting the parent's position from the popup widget's position
        self._relative_offset = self.pos() - self.top_parent.pos()

    def _update_position(self):
        """Update the position of the popup widget based on the button's location and the relative offset.
        """
        # Calculate the new position by adding the relative offset to the parent's position
        parent_pos = self.top_parent.pos() + self._relative_offset

        # Move the popup widget to the new position
        self.move(parent_pos)

    def _set_initial_position(self):
        """Set the initial position of the popup widget based on the instance's position.
        """
        # Calculate the initial position by adding the initial offset to the current cursor position
        cursor_pos = QtGui.QCursor.pos() + self.INITIAL_POSITION_OFFSET

        # Move the popup widget to the initial position
        self.move(cursor_pos)

    # Event Handling or Override Methods
    # ----------------------------------
    def enterEvent(self, event: QtGui.QEnterEvent):
        """Event handler for when the mouse enters the popup widget.

        Args:
            event (QtCore.QEvent): The mouse enter event.
        """
        #  Sets the end value of the opacity animation to 1.0 for full opacity.
        self._opacity_animation.setEndValue(1.0)
        # Starts the opacity animation.
        self._opacity_animation.start()

        # Calls the base class implementation to handle the event.
        super().enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent):
        """Event handler for when the mouse leaves the popup widget.

        Args:
            event (QtCore.QEvent): The mouse leave event.
        """
        # Sets the end value of the opacity animation to 0.5 for semi-opacity.
        self._opacity_animation.setEndValue(0.8)
        # Starts the opacity animation.
        self._opacity_animation.start()

        # Calls the base class implementation to handle the event.
        super().leaveEvent(event)

    def setVisible(self, visible: bool):
        """Show or hide the popup widget and update the position.

        Args:
            visible (bool): True to show the widget, False to hide it.
        """
        # Sets the initial position of the popup widget.
        self._set_initial_position()
        # Updates the relative offset between the popup widget and the parent widget.
        self._update_relative_offset()

        # Calls the base class implementation to set the visibility of the widget.
        return super().setVisible(visible)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """Event handler for when a mouse button is pressed within the popup widget.

        Args:
            event (QtCore.QEvent): The mouse press event.
        """
        # If the middle mouse button is pressed, stores the initial drag position and sets the _is_dragging flag to True.
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            # Store the initial drag position
            self._drag_start_position = event.globalPos()

            # Set the _is_dragging flag to True
            self._is_dragging = True
        # If a different mouse button is pressed, the base class implementation is called to handle the event.
        else:
            # Call the base class implementation to handle the event for other mouse buttons
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        """Event handler for when the mouse is moved within the popup widget.

        Args:
            event (QtCore.QEvent): The mouse move event.
        """
        # If dragging is in progress, the popup widget is moved accordingly to simulate dragging.
        if self._is_dragging:
            # Calculate the delta between the current mouse position and the initial drag start position
            delta = event.globalPos() - self._drag_start_position

            # Move the popup widget to the new position
            self.move(self.pos() + delta)

            # Update the drag start position to the current mouse position
            self._drag_start_position = event.globalPos()

        # Call the base class implementation to handle the event
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        """Event handler for when a mouse button is released within the popup widget.

        Args:
            event (QtCore.QEvent): The mouse release event.
        """
        # If the middle mouse button is released, dragging is stopped and the relative offset is updated.
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            # Stop dragging by setting the _is_dragging flag to False
            self._is_dragging = False

            # Update the relative offset between the popup widget and the parent widget
            self._update_relative_offset()
        # If a different mouse button is released, the base class implementation is called to handle the event.
        else:
            # Call the base class implementation to handle the event for other mouse buttons
            super().mouseReleaseEvent(event)
