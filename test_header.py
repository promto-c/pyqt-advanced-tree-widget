import typing
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QRect
from PyQt5.QtWidgets import QApplication, QTreeView, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QHeaderView, QLabel, QFrame

class DummyModel(QAbstractItemModel):
    def rowCount(self, parent=QModelIndex()):
        return 10

    def columnCount(self, parent=QModelIndex()):
        return 3

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column)

    def parent(self, index):
        return QModelIndex()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return f"Item {index.row()}, {index.column()}"

class HeaderColumnWidget(QWidget):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__( *args, **kwargs)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(0)

        label = QLabel('test', self)
        line_edit = QLineEdit(self)

        layout.addWidget(label)
        layout.addWidget(line_edit)
        
        line_edit.setPlaceholderText(f"Header")

class CustomHeaderView(QHeaderView):
    def __init__(self, parent, orientation: Qt.Orientation = Qt.Orientation.Horizontal, *args, **kwargs):
        super().__init__(orientation, parent, *args, **kwargs)
        self.line_edits = []

        # Double the header's height to fit the QLineEdit
        # widget = HeaderColumnWidget(self)

        self.setFixedHeight(self.height()*2)

        self.set_line_edits()

        self.sectionResized.connect(self.updateLineEditPositions)

        self.setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

    def set_line_edits(self):
        for i in range(self.parent().model().columnCount()):
            widget = HeaderColumnWidget(self)
            self.line_edits.append(widget)

    def mousePressEvent(self, event):
        for line_edit in self.line_edits:
            if line_edit.geometry().contains(event.pos()):
                line_edit.setFocus()
                return
        super().mousePressEvent(event)

    def updateLineEditPositions(self):
        for i, line_edit in enumerate(self.line_edits):
            section_rect = self.sectionViewportPosition(i)
            rect = QRect(section_rect+4, 0, self.sectionSize(i)-8, self.height())
            line_edit.setGeometry(rect)

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.setWindowTitle("LineEdit in Header Example")
        self.setGeometry(100, 100, 600, 400)

        self.tree = QTreeView(self)
        self.tree.setModel(DummyModel(self))

        custom_header = CustomHeaderView(self.tree)
        self.tree.setHeader(custom_header)

        custom_header.updateLineEditPositions()


        layout = QVBoxLayout()

        layout.addWidget(self.tree)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        






if __name__ == '__main__':
    import sys
    from theme import theme

    

    app = QApplication(sys.argv)
    theme.set_theme(app, 'dark')
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
