import sys
from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui

from theme.theme import set_theme

from groupable_tree_widget import GroupableTreeWidget, COLUMN_NAME_LIST, ID_TO_DATA_DICT

class ScalableView(QtWidgets.QGraphicsView):
    """A QGraphicsView subclass that allows the user to scale the contents of the view 
    using the mouse wheel and keyboard.

    Attributes:
        widget (QtWidgets.QWidget): The widget to be displayed in the view.
        min_zoom_level (float): The minimum zoom level allowed for the view.
        max_zoom_level (float): The maximum zoom level allowed for the view.
        current_zoom_level (float): The current zoom level of the view.
    """

    # Initialization and Setup
    # ------------------------
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None,
                       widget: Optional[QtWidgets.QWidget] = None):
        # Call the parent class constructor
        super().__init__(parent)

        # Store argument(s)
        self.widget = widget

        # Set up the initial values
        self._setup_attributes()
        # Set up the UI
        self._setup_ui()
        # Set up signal connections
        self._setup_signal_connections()

    def _setup_attributes(self):
        """Set up the initial values for the widget.
        """
        # Create a reference in the widget to the ScalableView object
        # NOTE: This reference ensures that context menus are displayed correctly within the view
        # Also, use this reference as an argument when creating context menu (QMenu) instances in the widget
        self.widget.scalable_view = self

        # Set the minimum and maximum scale values
        self.min_zoom_level = 0.5
        self.max_zoom_level = 4.0

        # Set the current zoom level to 1.0 (no zoom)
        self.current_zoom_level = 1.0

    def _setup_ui(self):
        """Set up the UI for the widget, including creating widgets and layouts.
        """
        # Set the scene
        self.setScene(QtWidgets.QGraphicsScene(self))
        # Set the widget as the central widget of the scene
        self.scene().addWidget(self.widget)
        # Set the alignment of the widget to the top left corner
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        # Set the viewport update mode to full viewport update to ensure that the entire view is updated when scaling
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        # Set the rendering hints to smooth pixels to improve the quality of the rendering
        self.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)

        # Set the horizontal scroll bar policy to always off
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # Set the vertical scroll bar policy to always off
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def _setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect the wheel event signal to the scaling slot
        self.viewport().installEventFilter(self)
        self.viewport().wheelEvent = self.wheelEvent

        # Key Binds
        # ---------
        # Create a QShortcut for the F key to reset the scaling of the view.
        shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F), self)
        shortcut.activated.connect(self.reset_scale)

    # Extended Methods
    # ----------------
    def set_scale(self, zoom_level: float = 1.0) -> None:
        """Set scale of the view to specified zoom level.
        """
        # Clamp the zoom level between the min and max zoom levels
        zoom_level = max(self.min_zoom_level, min(zoom_level, self.max_zoom_level))

        # Set the new zoom level
        self.setTransform(QtGui.QTransform().scale(zoom_level, zoom_level))
        # Update current zoom level
        self.current_zoom_level = zoom_level

        # Update the size of the widget to fit the view window
        self.resizeEvent(None)

    def reset_scale(self) -> None:
        """Reset scaling of the view to default zoom level (1.0 or no zoom).
        """
        # Reset the scaling of the view
        self.resetTransform()
        # Reset the current zoom level to 1.0 (no zoom)
        self.current_zoom_level = 1.0

        # Update the size of the widget to fit the view window
        self.resizeEvent(None)

    # Event Handling or Override Methods
    # ----------------------------------
    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """Handle resize events to resize the widget to the full size of the view, reserved for scaling.
        """
        # Get the size of the view
        view_size = self.size()
        # Get the QGraphicItem containing the widget
        graphic_item = self.scene().itemAt(0, 0, QtGui.QTransform())

        # Create a QRectF object with the size of the view reserved for scaling
        rect = QtCore.QRectF(
            0, 0,
            view_size.width() / self.current_zoom_level-2,
            view_size.height() / self.current_zoom_level-2)

        # Set the size of the widget to the size of the view
        graphic_item.setGeometry(rect)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """Handle wheel events to allow the user to scale the contents of the view.
        """
        # Check if the Ctrl key is pressed
        if event.modifiers() == QtCore.Qt.ControlModifier:
            # Get the scroll delta
            scroll_delta = event.angleDelta().y()
            # Calculate the scaling factor based on the wheel delta
            scale_factor = 1 + (scroll_delta / 120) / 10
            # Get the current scaling of the view
            self.current_zoom_level = self.transform().m11()

            # Calculate the new zoom level
            new_zoom_level = self.current_zoom_level * scale_factor
            # Set scale of the view to new zoom level.
            self.set_scale(new_zoom_level)

        # If the Ctrl key is not pressed, pass the event on to the parent class
        else:
            self.widget.wheelEvent(event)

def main():
    # Create the Qt application
    app = QtWidgets.QApplication(sys.argv)

    # Set theme of QApplication to the dark theme
    set_theme(app, 'dark')

    # Create the tree widget with example data
    tree_widget = GroupableTreeWidget(column_name_list=COLUMN_NAME_LIST, id_to_data_dict=ID_TO_DATA_DICT)

    # Create the scalable view and set the tree widget as its central widget
    scalable_tree_widget_view = ScalableView(widget=tree_widget)

    # Set the size of the view and show it
    scalable_tree_widget_view.resize(800, 600)
    scalable_tree_widget_view.show()

    # Run the application loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
