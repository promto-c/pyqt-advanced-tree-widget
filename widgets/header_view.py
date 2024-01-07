from typing import List

from PyQt5 import QtWidgets, QtCore, QtGui

class HeaderColumnWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__( *args, **kwargs)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 4)
        # layout.setSpacing(0)

        # label = QtWidgets.QLabel('test', self)
        # layout.addSpacing(20)
        line_edit = QtWidgets.QLineEdit(self)

        # layout.addWidget(label)
        layout.addWidget(line_edit)
        
        line_edit.setPlaceholderText(f"Header")

class SearchableHeaderView(QtWidgets.QHeaderView):

    # Initialization and Setup
    # ------------------------
    def __init__(self, parent: QtWidgets.QTreeWidget, orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal, *args, **kwargs):
        super().__init__(orientation, parent, *args, **kwargs)

        # Initialize setup
        self._setup_attributes()
        self._setup_ui()
        self._setup_icons()
        self._setup_signal_connections()

    def _setup_attributes(self):
        """Set up the initial values for the widget.
        """
        # Attributes
        # ------------------
        self.line_edits: List[QtWidgets.QLineEdit] = []

        # Private Attributes
        # ------------------
        ...

    def _setup_ui(self):
        """Set up the UI for the widget, including creating widgets and layouts.
        """
        # Create widgets and layouts
        self.setFixedHeight(int(self.height()*1.5))
        self.setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.set_line_edits()

        if self.parent():
            self.parent().setHeader(self)
            self.update_positions()

    def _setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect signals to slots
        self.sectionResized.connect(self.update_positions)
        self.parent().horizontalScrollBar().valueChanged.connect(self.update_positions)

    def _setup_icons(self):
        """Set the icons for the widgets.
        """
        # Set the icons for the widgets
        pass

    # Private Methods
    # ---------------

    # Extended Methods
    # ----------------
    def update_positions(self):
        for i, line_edit in enumerate(self.line_edits):
            section_rect = self.sectionViewportPosition(i)
            rect = QtCore.QRect(section_rect+4, 11, self.sectionSize(i)-8, self.height())
            line_edit.setGeometry(rect)

    def set_line_edits(self):
        for _ in range(self.parent().model().columnCount()):
            widget = HeaderColumnWidget(self)
            self.line_edits.append(widget)

    # Event Handling or Override Methods
    # ----------------------------------
    def mousePressEvent(self, event):
        for line_edit in self.line_edits:
            if line_edit.geometry().contains(event.pos()):
                line_edit.setFocus()
                return

        super().mousePressEvent(event)

