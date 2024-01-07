import sys, time
from typing import Tuple

from PyQt5 import QtWidgets, QtCore, QtGui
from tablerqicon import TablerQIcon


class TagButton(QtWidgets.QPushButton):
    tag_removed = QtCore.pyqtSignal(str)

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.setStyleSheet('''
            QPushButton {
                background-color: #355;
                border-radius: 10px;
                border: transparent;
                padding: 2px 5px;
                color: #DDD;
            }
            QPushButton:hover {
                background-color: #466;
            }
            QPushButton:pressed {
                background-color: #244;
            }
        ''')

        self.clicked.connect(self.emit_remove)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

    def emit_remove(self):
        self.tag_removed.emit(self.text())

class TagWidget(QtWidgets.QWidget):
    tag_removed = QtCore.pyqtSignal(str)
    tag_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.widget = QtWidgets.QWidget(self)

        self.tag_layout = QtWidgets.QHBoxLayout()
        self.tag_layout.setContentsMargins(0, 0, 0, 0)
        self.tag_layout.addStretch()

        self.widget.setLayout(self.tag_layout)
        self.tags = set()

        # Replace QScrollArea with InertiaScrollArea
        self.scroll_area = InertiaScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.widget)
        self.scroll_area.setFixedHeight(26)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.scroll_area)

        self.tabler_icon = TablerQIcon(opacity=0.6)
        self.copy_button = QtWidgets.QPushButton(self.tabler_icon.copy, '', self)
        self.main_layout.addWidget(self.copy_button)

        self.copy_button.clicked.connect(self.copy_data_to_clipboard)
        self.update_copy_button_state()
        self.tag_changed.connect(self.update_copy_button_state)

    def update_copy_button_state(self):
        self.copy_button.setEnabled(bool(self.tags))

        num_item_str = str(len(self.tags)) if self.tags else str()
        self.copy_button.setText(num_item_str)

    def copy_data_to_clipboard(self):
        full_text = ', '.join(self.tags)

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(full_text)

        # Show tooltip message
        self.show_tool_tip(f'Copied:\n{full_text}', 5000)

    def show_tool_tip(self, text: str, msc_show_time: int = 1000):
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), text, self, QtCore.QRect(), msc_show_time)

    def add_tag(self, text):
        if text not in self.tags:
            self.tags.add(text)
            tag_label = TagButton(text, self)
            tag_label.tag_removed.connect(self.emit_remove_tag)
            tag_label.tag_removed.connect(self.remove_tag)
            self.tag_layout.insertWidget(self.tag_layout.count() - 1, tag_label)

        self.tag_changed.emit()

    def emit_remove_tag(self, tag_name):
        self.tag_removed.emit(tag_name)

    def remove_tag(self, text):
        if text in self.tags:
            self.tags.remove(text)
        for i in reversed(range(self.tag_layout.count())):
            widget = self.tag_layout.itemAt(i).widget()
            if widget is not None and isinstance(widget, TagButton) and widget.text() == text:
                widget.deleteLater()

        self.tag_changed.emit()

class InertiaScrollArea(QtWidgets.QScrollArea):
    def __init__(self, parent=None, max_velocity=15, deceleration_rate=0.9, timer_interval=10):
        super().__init__(parent)
        self.max_velocity = max_velocity
        self.deceleration_rate = deceleration_rate
        self.timer_interval = timer_interval

        self.velocity = 0
        self.last_time = 0
        self.dragging = False

        self.inertia_timer = QtCore.QTimer()
        self.inertia_timer.timeout.connect(self.handle_inertia)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """Handles mouse press events.
        """
        if event.button() in (QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.MouseButton.MiddleButton):
            self.dragging = True
            self.last_pos = event.pos()
            self.last_time = time.time()
            self.velocity = 0
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        """Handles mouse move events.
        """
        if self.dragging:
            current_time = time.time()
            new_pos = event.pos()
            delta = new_pos - self.last_pos
            delta_time = current_time - self.last_time
            if delta_time > 0:
                new_velocity = delta.x() / delta_time
                self.velocity = max(min(new_velocity, self.max_velocity), -self.max_velocity)
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x())
            self.last_pos = new_pos
            self.last_time = current_time
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        """Handles mouse release events.
        """
        if event.button() in (QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.MouseButton.MiddleButton):
            self.dragging = False
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
            self.inertia_timer.start(self.timer_interval)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def handle_inertia(self):
        self.velocity *= self.deceleration_rate
        if abs(self.velocity) < 0.5:
            self.inertia_timer.stop()
            return

        h_scroll_bar = self.horizontalScrollBar()
        h_scroll_bar.setValue(h_scroll_bar.value() - int(self.velocity))

        if (h_scroll_bar.value() == h_scroll_bar.maximum() or
            h_scroll_bar.value() == h_scroll_bar.minimum()):
            self.inertia_timer.stop()
