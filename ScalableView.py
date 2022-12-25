import sys
from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui

from GroupableTreeWidget import GroupableTreeWidget, COLUMN_NAME_LIST, ID_TO_DATA_DICT

class ScalableView(QtWidgets.QGraphicsView):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, 
                       widget: Optional[QtWidgets.QWidget] = None):
        # Call the parent class constructor
        super(ScalableView, self).__init__(parent)

        # Store argument(s)
        self.widget = widget

        # Set up the initial values
        self._setup_initial_values()
        # Set up the UI
        self._setup_ui()
        # Set up signal connections
        self._setup_signal_connections()

    def _setup_initial_values(self):
        ''' Set up the initial values for the widget.
        '''
        # Set the minimum and maximum scale values
        self.min_zoom_level = 0.5
        self.max_zoom_level = 4.0

    def _setup_ui(self):
        ''' Set up the UI for the widget, including creating widgets and layouts.
        '''
        # Set the scene
        self.setScene(QtWidgets.QGraphicsScene(self))
        # Set the tree widget as the central widget of the scene
        self.scene().addWidget(self.widget)
        # Set the default scaling
        self.scale(1, 1)
        # Set the alignment of the widget to the top left corner
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        # Set the viewport update mode to full viewport update to ensure that the entire view is updated when scaling
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        # Set the drag mode to scroll hand to allow the user to pan the view by dragging with the mouse
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        # Set the rendering hints to smooth pixels to improve the quality of the rendering
        self.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)

        # Set the size policy of the tree widget to expanding in both directions
        self.widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # Set the horizontal scroll bar policy to always off
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # Set the vertical scroll bar policy to always off
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        ''' Handle resize events to resize the tree widget to the full size of the view.
        '''
        # Get the size of the view
        view_size = self.size()
        # Create a QRectF object with the size of the view
        rect = QtCore.QRect(0, 0, view_size.width(), view_size.height())
        # Set the size of the tree widget to the size of the view
        self.widget.setGeometry(rect)

    def _setup_signal_connections(self):
        ''' Set up signal connections between widgets and slots.
        '''
        # Connect the wheel event signal to the scaling slot
        self.viewport().installEventFilter(self)
        self.viewport().wheelEvent = self.wheelEvent

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        ''' Handle wheel events to allow the user to scale the contents of the view.
        '''
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
            # Clamp the zoom level between the min and max zoom levels
            new_zoom_level = max(self.min_zoom_level, min(new_zoom_level, self.max_zoom_level))

            # Set the new zoom level
            self.setTransform( QtGui.QTransform().scale( new_zoom_level, new_zoom_level ) )

            # Update current zoom level
            self.current_zoom_level = new_zoom_level
            
            # Update the size of the widget to fit the view window
            self.resizeEvent(None)

        # If the Ctrl key is not pressed, pass the event on to the parent class
        else:
            self.widget.wheelEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        ''' Handle key press events to allow the user to reset the scaling of the view.
        '''
        # Check if the F key is pressed
        if event.key() == QtCore.Qt.Key_F:
            # Reset the scaling of the view
            self.resetTransform()
        # If the F key is not pressed, pass the event on to the parent class
        else:
            super(ScalableView, self).keyPressEvent(event)

def main():
    # Create the Qt application
    app = QtWidgets.QApplication(sys.argv)

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
    