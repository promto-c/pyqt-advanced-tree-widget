
# Type Checking Imports
# ---------------------
from typing import Any, Union, Callable, Dict, Iterable

# Standard Library Imports
# ------------------------
import sys

# Third Party Imports
# -------------------
from PyQt5 import QtWidgets, QtCore, QtGui
from tablerqicon import TablerQIcon

# Local Imports
# -------------
from widgets.filter_widget import (
    FilterBarWidget, FilterWidget,
    DateRangeFilterWidget,
    MultiSelectFilterWidget,
    FileTypeFilterWidget,
)
from widgets.simple_search_widget import SimpleSearchEdit
from widgets.groupable_tree_widget import GroupableTreeWidget
from widgets.scalable_view import ScalableView
from theme import set_theme

class DatabaseViewWidget(QtWidgets.QWidget):
    """
    """

    # Initialization and Setup
    # ------------------------
    def __init__(self, parent: QtWidgets.QWidget = None):
        """Initialize the widget and set up the UI, signal connections.
        """
        # Initialize the super class
        super().__init__(parent)

        # Initialize setup
        self.__setup_ui()
        self.__setup_signal_connections()

    def __setup_ui(self):
        """Set up the UI for the widget, including creating widgets, layouts.

        UI Wireframe:

            |--[W1]: filter_bar_widget--|

            +---------------------------------------------------+ -+
            | [Filter 1][Filter 2][+]       [[W2]: search_edit] |  | -> [L1]: top_bar_area_layout
            +---------------------------------------------------+ -+
            |                                                   |  |
            |                                                   |  |
            |               [[W3]: tree_widget]                 |  | -> [L2]: main_tree_layout
            |                                                   |  |
            |                                                   |  |
            +---------------------------------------------------+ -+
        """
        # Create Layouts
        # --------------
        # [L0]: Set main layout as vertical layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # [L1]: Add top bar layout as horizontal layout
        self.top_bar_area_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.top_bar_area_layout)

        # [L2]: Add main tree layout
        self.main_tree_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.main_tree_layout)

        # Create Widgets
        # --------------
        # [W1]: Create top left filter bar
        self.filter_bar_widget = FilterBarWidget(self)

        # [W3]: Create asset tree widget
        self.tree_widget = GroupableTreeWidget(parent=self)

        # [W2]: Search field
        self.search_edit = SimpleSearchEdit(tree_widget=self.tree_widget, parent=self)
        self.search_edit.setMinimumWidth(200)

        # Add Widgets to Layouts
        # ----------------------
        # Add [W1], [W2] to [L1]
        # Add left filter bar and right search edit to top bar layout
        self.top_bar_area_layout.addWidget(self.filter_bar_widget)
        self.top_bar_area_layout.addStretch()
        self.top_bar_area_layout.addWidget(self.search_edit)

        # Add [W3] to [L2]
        # Add tree widget to main tree widget
        self.main_tree_layout.addWidget(self.tree_widget)

    def __setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect signals to slots
        self.bind_key('Ctrl+F', self.search_edit.set_text_as_selection)

    def bind_key(self, key_sequence: Union[str, QtGui.QKeySequence], function: Callable):
        """Binds a given key sequence to a function.

        Args:
            key_sequence (Union[str, QtGui.QKeySequence]): The key sequence as a string, e.g., "Ctrl+C".
            function (Callable): The function to be called when the key sequence is activated.
        """
        # Create a shortcut with the specified key sequence
        shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(key_sequence), self)
        # Connect the activated signal of the shortcut to the given function
        shortcut.activated.connect(function)

    def add_filter_widget(self, filter_widget: 'FilterWidget'):
        self.filter_bar_widget.add_filter_widget(filter_widget)
        filter_widget.activated.connect(self.populate)

    def populate(self, id_to_data_dict: Dict[Iterable, Dict[str, Any]]):
        # Clear old items
        self.tree_widget.clear()

        # Add items to tree
        self.tree_widget.add_items(id_to_data_dict)

        self.search_edit.update()

def main():
    """Create the application and main window, and show the widget.
    """
    # Create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    # Set theme of QApplication to the dark theme
    set_theme(app, 'dark')

    from example_data_dict import COLUMN_NAME_LIST, ID_TO_DATA_DICT

    # Create an instance of the widget
    database_view_widget = DatabaseViewWidget()
    database_view_widget.tree_widget.set_column_name_list(COLUMN_NAME_LIST)
    database_view_widget.populate(ID_TO_DATA_DICT)

    # Date Filter Setup
    date_filter_widget = DateRangeFilterWidget(filter_name="Date")
    date_filter_widget.activated.connect(print)
    # Shot Filter Setup
    shot_filter_widget = MultiSelectFilterWidget(filter_name="Shot")
    sequence_to_shots = {
        "100": [
            "100_010_001", 
            "100_020_050",
        ],
        "101": [
            "101_022_232", 
            "101_023_200",
        ],
    }
    shot_filter_widget.add_items(sequence_to_shots)
    shot_filter_widget.activated.connect(print)

    # File Type Filter Setup
    file_type_filter_widget = FileTypeFilterWidget(filter_name="File Type")
    file_type_filter_widget.activated.connect(print)

    # Search edit
    search_edit = QtWidgets.QLineEdit()
    search_edit.setPlaceholderText('Type to Search')
    search_edit.setProperty('widget-style', 'round')
    search_edit.setFixedHeight(24)
    tabler_icon = TablerQIcon(opacity=0.6)
    search_edit.addAction(tabler_icon.search, QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
    search_edit.setProperty('has-placeholder', True)
    search_edit.textChanged.connect(lambda: (search_edit.style().unpolish(search_edit), search_edit.style().polish(search_edit)))

    # Filter bar
    database_view_widget.filter_bar_widget.add_filter_widget(date_filter_widget)
    database_view_widget.filter_bar_widget.add_filter_widget(shot_filter_widget)
    database_view_widget.filter_bar_widget.add_filter_widget(file_type_filter_widget)

    # Create the scalable view and set the tree widget as its central widget
    scalable_view = ScalableView(widget=database_view_widget)

    # Show the widget
    scalable_view.show()

    # Run the application
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
