import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from flowlayout import FlowLayout

class AssetCard(QtWidgets.QWidget):
    def __init__(self, image_path, title, file_type, tags):
        super().__init__()

        self.size = 200

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.setObjectName("AssetCard")  # Set an object name
        self.setStyleSheet("""
        #AssetCard {
            background-color: #222222;
        }
        """)

        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setFixedSize(self.size, self.size)  # Set fixed square size
        self.image_label.setStyleSheet('''
        QLabel {
            padding: 0px 0px;
        }''')
        pixmap = QtGui.QPixmap(image_path)
        if pixmap.isNull():
            print("Image not loaded!")

        # Smooth scaling
        scaled_pixmap = pixmap.scaled(200, 200, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)

        # Create a pixmap with rounded corners
        rounded_pixmap = QtGui.QPixmap(scaled_pixmap.size())
        rounded_pixmap.fill(QtCore.Qt.transparent)  # Fill with transparent background

        painter = QtGui.QPainter(rounded_pixmap)
        # painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)  # For smooth edges
        path = QtGui.QPainterPath()
        print(scaled_pixmap.width())
        print(scaled_pixmap.height())
        path.addRoundedRect(QtCore.QRectF(scaled_pixmap.rect()), 10, 10)  # 10 is the radius for rounded corners
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()

        self.image_label.setPixmap(rounded_pixmap)
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
        self.container_widget.setObjectName("ContainerWidget")  # Set an object name
        self.container_widget.setStyleSheet("""
        #ContainerWidget {
            background-color: #222222;
        }
        """)
        self.flow_layout = FlowLayout(self.container_widget)

        assets_data = [
            ("image_not_available_placeholder.png", "Marketing Image 1", "JPG", ["Image", "Social"]),
            ("image_not_available_placeholder.png", "Marketing Image 2", "JPG", ["Image"]),
            ("image_not_available_placeholder.png", "Marketing Image 2", "JPG", ["Image"]),
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
