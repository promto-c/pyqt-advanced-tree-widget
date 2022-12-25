import sys
from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui

from TreeWidget import TreeWidget, COLUMN_NAME_LIST, ID_TO_DATA_DICT

class ScalableView(QtWidgets.QGraphicsView):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, 
                       tree_widget: Optional[QtWidgets.QTreeWidget] = None):
        # Call the parent class constructor
        super(ScalableView, self).__init__(parent)

        # Set up the initial values
        self._setup_initial_values(tree_widget)
        # Set up the UI
        self._setup_ui()
        # Set up signal connections
        self._setup_signal_connections()

    def _setup_initial_values(self, tree_widget: Optional[QtWidgets.QTreeWidget]):
        ''' Set up the initial values for the widget.
        '''
        # Set the scene
        self.setScene(QtWidgets.QGraphicsScene(self))
        # Set the tree widget as the central widget of the scene
        self.scene().addWidget(tree_widget)
        # Set the default scaling
        self.scale(1, 1)

    def _setup_ui(self):
        ''' Set up the UI for the widget, including creating widgets and layouts.
        '''
        # Set the viewport update mode to full viewport update to ensure that the entire view is updated when scaling
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        # Set the drag mode to scroll hand to allow the user to pan the view by dragging with the mouse
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        # Set the rendering hints to smooth pixels to improve the quality of the rendering
        self.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)

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
            # Calculate the scaling factor based on the wheel delta
            scale_factor = 1 + (event.angleDelta().y() / 120) / 10
            # Scale the view
            self.scale(scale_factor, scale_factor)
        # If the Ctrl key is not pressed, pass the event on to the parent class
        else:
            super(ScalableView, self).wheelEvent(event)

def main():
    # Create the Qt application
    app = QtWidgets.QApplication(sys.argv)

    # Create the tree widget with example data
    tree_widget = TreeWidget(column_name_list=COLUMN_NAME_LIST, id_to_data_dict=ID_TO_DATA_DICT)

    # Create the scalable view and set the tree widget as its central widget
    view = ScalableView(tree_widget=tree_widget)

    # Set the size of the view and show it
    view.resize(800, 600)
    view.show()

    # Run the application loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    