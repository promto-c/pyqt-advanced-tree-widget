from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets

class HighlightItemDelegate(QtWidgets.QStyledItemDelegate):
    """Custom item delegate class that highlights the rows specified by the `target_model_indexes` list.
    """
    # List of target model index for highlighting
    target_model_indexes: List[QtCore.QModelIndex] = list()
    target_focused_model_indexes: List[QtCore.QModelIndex] = list()

    # Define default highlight color
    DEFAULT_COLOR = QtGui.QColor(165, 165, 144, 65)
    DEFAULT_FOCUSED_COLOR = QtGui.QColor(165, 165, 144, 129)
    
    def __init__(self, parent=None, color: QtGui.QColor = DEFAULT_COLOR, 
                 focused_color: QtGui.QColor = DEFAULT_FOCUSED_COLOR):
        """Initialize the highlight item delegate.

        Args:
            parent (QtWidgets.QWidget, optional): The parent widget. Defaults to None.
            color (QtGui.QColor, optional): The color to use for highlighting. Defaults to a light grayish-yellow.
        """
        # Initialize the super class
        super().__init__(parent)

        # Set the color attribute
        self.color = color
        self.focused_color = focused_color
    
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, model_index: QtCore.QModelIndex):
        """Paint the delegate.
        
        Args:
            painter (QtGui.QPainter): The painter to use for drawing.
            option (QtWidgets.QStyleOptionViewItem): The style option to use for drawing.
            model_index (QtCore.QModelIndex): The model index of the item to be painted.
        """
        # Check if the current model index is not in the target list
        if model_index not in self.target_model_indexes:
            # If not, paint the item normally using the parent implementation
            super().paint(painter, option, model_index)
            return

        color = self.focused_color if model_index in self.target_focused_model_indexes else self.color

        # If the current model index is in the target list, set the background color and style
        option.backgroundBrush.setColor(color)
        option.backgroundBrush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

        # Fill the rect with the background brush
        painter.fillRect(option.rect, option.backgroundBrush)

        # Paint the item normally using the parent implementation
        super().paint(painter, option, model_index)

    def clear(self):
        # Reset the previous target model indexes
        self.target_model_indexes.clear()
        self.target_focused_model_indexes.clear()
