import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from flowlayout import FlowLayout

class AssetCard(QtWidgets.QWidget):
    def __init__(self, image_path, title, file_type, tags):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.image_label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap(image_path)
        # pixmap = QtGui.QPixmap("/path/to/your/image.png")
        if pixmap.isNull():
            print("Image not loaded!")

        self.image_label.setPixmap(pixmap.scaledToWidth(200))  # Adjust the width as necessary
        layout.addWidget(self.image_label)

        self.title_label = QtWidgets.QLabel(title, self)
        layout.addWidget(self.title_label)

        self.file_type_label = QtWidgets.QLabel(file_type, self)
        layout.addWidget(self.file_type_label)

        self.tags_layout = QtWidgets.QHBoxLayout()
        for tag in tags:
            tag_button = QtWidgets.QPushButton(tag, self)
            self.tags_layout.addWidget(tag_button)
        layout.addLayout(self.tags_layout)

class Window(QtWidgets.QMainWindow):  # Change to QMainWindow
    def __init__(self):
        super().__init__()

        # Create a QScrollArea and set its properties
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # Create a QWidget that will contain the FlowLayout
        self.container_widget = QtWidgets.QWidget(self.scroll_area)
        self.flow_layout = FlowLayout(self.container_widget)

        assets_data = [
            ("path_to_image1.jpg", "Marketing Image 1", "JPG", ["Image", "Social"]),
            ("path_to_image2.jpg", "Marketing Image 2", "JPG", ["Image"]),
            # ... add more assets data as needed
        ]

        for image_path, title, file_type, tags in assets_data:
            asset_card = AssetCard(image_path, title, file_type, tags)
            self.flow_layout.addWidget(asset_card)

        # Set the widget for the scroll area and set the scroll area as the central widget
        self.scroll_area.setWidget(self.container_widget)
        self.setCentralWidget(self.scroll_area)

        self.setWindowTitle("Flow Layout Gallery View")


if __name__ == "__main__":
    from theme import theme

    
    app = QtWidgets.QApplication([])

    theme.set_theme(app, 'dark')
    main_win = Window()
    main_win.show()
    app.exec_()
