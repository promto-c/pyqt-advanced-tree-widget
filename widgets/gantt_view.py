import sys, datetime

from PyQt5 import QtCore, QtGui, QtWidgets


class TimelineHeader(QtWidgets.QHeaderView):
    """A custom header view with a dynamic timeline drawn based on the tasks' dates."""

    def __init__(self, parent=None, start_date=None, end_date=None):
        """Initializes the timeline header with an optional date range.

        Args:
            parent: The parent widget.
            start_date: The start date of the timeline.
            end_date: The end date of the timeline.
        """
        super().__init__(QtCore.Qt.Orientation.Horizontal, parent)
        self.start_date = start_date
        self.end_date = end_date
        self._initialize_header()

    def _initialize_header(self):
        """Sets initial configuration for the header."""
        self.setSectionsClickable(False)

    def paintSection(self, painter, rect, logical_index):
        """Paints the header section.

        Overrides the method to draw a custom timeline for the second column.

        Args:
            painter: QPainter object used for drawing.
            rect: The rectangle area of the header section.
            logical_index: The logical index of the header section.
        """
        # super().paintSection(painter, rect, logical_index)
        if logical_index == 1:  # Targeting the second column for the timeline.
            self._draw_timeline(painter, rect)
    def set_date_range(self, start_date, end_date):
        """Sets the date range for the timeline and updates the header.

        Args:
            start_date: The start date of the timeline.
            end_date: The end date of the timeline.
        """
        self.start_date = start_date
        self.end_date = end_date
        self.viewport().update()

    def paintSection(self, painter, rect, logical_index):
        """Paints the header section with the timeline if it's the designated timeline column."""
        
        if logical_index == 1 and self.start_date and self.end_date:  # Assuming the second column is for the timeline.
            self._draw_timeline(painter, rect)
        else:
            super().paintSection(painter, rect, logical_index)

    def _draw_timeline(self, painter, rect):
        """Draws a dynamic timeline based on the set date range."""
        # painter.save()
        self._configure_painter_for_timeline(painter)

        total_days = (self.end_date - self.start_date).days + 1
        day_width = rect.width() / total_days

        for day_offset in range(total_days):
            current_date = self.start_date + datetime.timedelta(days=day_offset)
            x_pos = rect.left() + day_width * day_offset
            if day_offset % 5 == 0:  # Example: Label every 5 days
                self._draw_tick(painter, x_pos, rect)
                self._draw_tick_label(painter, x_pos, rect, current_date.strftime('%d %b'))

        # painter.restore()

    def _configure_painter_for_timeline(self, painter):
        """Configures the painter settings for timeline drawing.

        Args:
            painter: QPainter object used for drawing.
        """
        painter.setPen(QtGui.QPen(QtGui.QColor("black"), 1))

    def _calculate_tick_position(self, rect, tick_count, tick_index):
        """Calculates the x position of a tick based on its index.

        Args:
            rect: The rectangle area where the timeline is drawn.
            tick_count: The total number of ticks on the timeline.
            tick_index: The index of the current tick.

        Returns:
            The x position of the tick.
        """
        return rect.left() + (rect.width() / tick_count) * tick_index

    def _draw_tick(self, painter, x_pos, rect):
        """Draws a tick mark at the specified position.

        Args:
            painter: QPainter object used for drawing.
            x_pos: The x position where the tick should be drawn.
            rect: The rectangle area where the timeline is drawn.
        """
        painter.drawLine(int(x_pos), rect.top(), int(x_pos), rect.bottom())

    def _draw_tick_label(self, painter, x_pos, rect, label):
        """Draws the label for a tick at the specified position.

        Args:
            painter: QPainter object used for drawing.
            x_pos: The x position where the label should be drawn.
            rect: The rectangle area where the timeline is drawn.
            label: The text of the label to draw.
        """
        text_pos = QtCore.QPointF(x_pos, rect.bottom() - 5)
        painter.drawText(text_pos, label)

class GanttTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, data):
        super().__init__()
        self.start_date = data['start']
        self.end_date = data['end']
        self.setText(0, data['name'])  # Set the name of the task

    def get_duration(self):
        return self.start_date, self.end_date
    
class GanttTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent=None, timeline_column=1):
        """Initializes the GanttTreeWidget with a specified parent and timeline column."""
        super().__init__(parent)
        self.header_labels = ['Tasks', 'Timeline']
        self.setColumnCount(len(self.header_labels))
        self.setHeaderLabels(self.header_labels)

        self.timeline_column = timeline_column
        self.timeline_header = TimelineHeader(self)
        self.setHeader(self.timeline_header)

        self.setUniformRowHeights(True)
        self.items = []

    def set_data_dict(self, data_dict):
        """Populates the tree widget with items based on the provided data dictionary."""
        for data in data_dict:
            item = GanttTreeWidgetItem(data)
            self.addTopLevelItem(item)
            self.items.append(item)

    def update_timeline_range(self):
        """Updates the timeline header based on the overall range of task dates."""
        if not self.items:
            return  # No items to determine the range from

        start_dates = [item.start_date for item in self.items]
        end_dates = [item.end_date for item in self.items]
        overall_start = min(start_dates)
        overall_end = max(end_dates)

        self.timeline_header.set_date_range(overall_start, overall_end)

    def paintEvent(self, event):
        """Custom paint event to draw the timeline for each item in the Gantt chart."""
        super().paintEvent(event)
        painter = QtGui.QPainter(self.viewport())

        if self.items:
            total_days = (self.items[-1].get_duration()[1] - self.items[0].get_duration()[0]).days
        else:
            total_days = 1

        for item in self.items:
            start, end = item.get_duration()
            start_pos = self.visualItemRect(item).topLeft()
            end_pos = self.visualItemRect(item).bottomRight()

            start_days = (start - self.items[0].get_duration()[0]).days
            duration_days = (end - start).days

            y_margin = 1

            x =  sum(self.columnWidth(i) for i in range(self.timeline_column)) + \
                (self.columnWidth(self.timeline_column) * start_days / total_days)
            y = start_pos.y() + y_margin
            # print(self.columnWidth(self.timeline_column))
            width = self.columnWidth(self.timeline_column) * duration_days / total_days
            height = end_pos.y() - start_pos.y() - (y_margin*2)

            rect = QtCore.QRectF(x, y, width, height)
            color = QtGui.QColor("skyblue")
            border_radius = 2

            # painter.save()
            painter.setPen(QtGui.QPen(color))  # Set the color for the border of the Gantt bar
            painter.setBrush(QtGui.QBrush(color))  # Set the fill color for the Gantt bar
            painter.drawRoundedRect(rect, border_radius, border_radius)  # Draw a rounded rectangle as the Gantt bar
            # painter.restore()

            # painter.fillRect(rect)

    def resizeEvent(self, event):
        """Updates the viewport and propagates the resize event."""
        self.viewport().update()
        super().resizeEvent(event)

# Example usage
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    data_dict = [
        {'name': 'Task 1', 'start': datetime.date(2024, 1, 1), 'end': datetime.date(2024, 1, 10)},
        {'name': 'Task 2', 'start': datetime.date(2024, 1, 5), 'end': datetime.date(2024, 1, 15)},
        {'name': 'Task 3', 'start': datetime.date(2024, 1, 10), 'end': datetime.date(2024, 1, 20)}
    ]

    gantt_view = GanttTreeWidget()
    gantt_view.set_data_dict(data_dict)
    gantt_view.update_timeline_range()
    gantt_view.show()
    sys.exit(app.exec_())
