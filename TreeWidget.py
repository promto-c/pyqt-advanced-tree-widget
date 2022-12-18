import sys
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem

class TreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Customize the widget as desired
        self.setHeaderLabel("Tree Widget")

def main():
    app = QApplication(sys.argv)
    tree_widget = TreeWidget()
    tree_widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()