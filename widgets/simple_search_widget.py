import sys, os, re
from pathlib import Path
from typing import Callable, Any, List, Union, Optional

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from tablerqicon import TablerQIcon

from theme.theme import set_theme

# from widgets.filter_widget import MultiSelectFilterWidget
from widgets.groupable_tree_widget import GroupableTreeWidget
from widgets.scalable_view import ScalableView

from utils.text_utils import TextExtraction


# Class Definitions
# -----------------
class SimpleSearchEdit(QtWidgets.QComboBox):
    """

    Attributes:
        ...
    """
    # Initialization and Setup
    # ------------------------
    def __init__(self, tree_widget: 'GroupableTreeWidget', parent: QtWidgets.QWidget = None):
        """Initialize the widget and set up the UI, signal connections, and icon.

        Args:
            parent (QtWidgets.QWidget): The parent widget.
            some_arg (Any): An argument that will be used in the widget.
        """
        # Initialize the super class
        super().__init__(parent)

        # Store the arguments
        self.tree_widget = tree_widget

        # Initialize setup
        self.__setup_attributes()
        self.__setup_ui()
        self.__setup_signal_connections()

    def __setup_attributes(self):
        """Set up the initial values for the widget.
        """
        # Attributes
        # ----------
        self.is_active = False

        # Private Attributes
        # ------------------
        self._all_match_items = set()

    def __setup_ui(self):
        """Set up the UI for the widget, including creating widgets, layouts, and setting the icons for the widgets.
        """
        self.setEditable(True)
        self.setProperty('widget-style', 'round')

        self.lineEdit().setPlaceholderText('Type to Search')
        self.setFixedHeight(24)
        self.tabler_icon = TablerQIcon(opacity=0.6)

        # Add search icon
        self.lineEdit().addAction(self.tabler_icon.search, QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
        self.lineEdit().setProperty('has-placeholder', True)
        self.lineEdit().textChanged.connect(self.update_style)

        self.__setup_match_count_action()

    def __setup_match_count_action(self):
        # Create and add the label for showing the total match count
        self.match_count_label = QtWidgets.QLabel("0")
        self.match_count_label.setStyleSheet('''
            QLabel {
                border-radius: 8;
                font-size: 8pt;
                color: #EEE;
                background-color: #566;
            }
        ''')
        self.match_count_label.setFixedHeight(16)
        self.match_count_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.match_count_action = QtWidgets.QWidgetAction(self)
        self.match_count_action.setDefaultWidget(self.match_count_label)
        self.lineEdit().addAction(self.match_count_action, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
        self.match_count_label.setVisible(False)

    def __setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect signals to slots
        self.editTextChanged.connect(self.set_inactive)
        self.editTextChanged.connect(self._highlight_search)
        self.bind_key('Enter', self.set_active)
        self.bind_key('Return', self.set_active)

    # Private Methods
    # ---------------
    def _update_total_matches(self, total_matches: Optional[int] = None):
        """Update the text of the match count label with the total number of matches."""
        total_matches = total_matches or len(self._all_match_items)
        self.match_count_label.setVisible(bool(total_matches))
        self.match_count_label.setText(str(total_matches))

    def _highlight_search(self):
        """Highlight the items in the tree widget that match the search criteria.
        """
        # Reset the highlight for all items
        self.tree_widget.clear_highlight()

        # Clear any previously matched items
        self._all_match_items.clear()
        self._update_total_matches()

        # Get the selected column, condition, and keyword
        keyword = self.currentText().strip()

        # Return if the keyword is empty
        if not keyword:
            return

        # Match terms enclosed in either double or single quotes for fixed string match
        quoted_terms = TextExtraction.extract_quoted_terms(keyword)

        # Split the string at parts enclosed in either double or single quotes for contains match
        unquoted_terms = TextExtraction.extract_unquoted_terms(keyword)

        fixed_string_match_flags = QtCore.Qt.MatchFlag.MatchRecursive | QtCore.Qt.MatchFlag.MatchFixedString
        contains_match_flags = QtCore.Qt.MatchFlag.MatchRecursive | QtCore.Qt.MatchFlag.MatchContains
        wildcard_match_flags = QtCore.Qt.MatchFlag.MatchRecursive | QtCore.Qt.MatchFlag.MatchWildcard

        for column_index in range(self.tree_widget.columnCount()):
            match_items = list()

            # Handle fixed string match terms with case-insensitive matching
            for term in quoted_terms:
                match_items.extend(self.tree_widget.findItems(term, fixed_string_match_flags, column_index))

            # Handle contains match terms
            for term in unquoted_terms:
                flags = wildcard_match_flags if TextExtraction.is_contains_wildcard(term) else contains_match_flags

                # Find items that contain the term, regardless of its position in the string
                match_items.extend(self.tree_widget.findItems(term, flags, column_index))
            
            # Highlight the matched items
            self.tree_widget.highlight_items(match_items, column_index)

            # Store all matched items
            self._all_match_items.update(match_items)

        self._update_total_matches()

    def _set_property_active(self, state: bool = True):
        """Set the active state of the button.
        """
        self.is_active = state
        self.setProperty('active', self.is_active)
        self.update_style()

    def _apply_search(self):
        """Apply the filters specified by the user to the tree widget.
        """
        self.tree_widget.clear_highlight()

        # Hide all items
        self.tree_widget.hide_all_items()
        # Show match items
        self.tree_widget.show_items(self._all_match_items)

    def _reset_search(self):
        # Show all items
        self.tree_widget.show_all_items()

        self._highlight_search()

    @property
    def matched_items(self):
        return self._all_match_items

    # Public Methods
    # --------------

    # Extended Methods
    # ----------------
    def set_text_as_selection(self):
        model_indexes = self.tree_widget.selectedIndexes()
        keywords = set()

        for model_index in model_indexes:
            tree_item = self.tree_widget.itemFromIndex(model_index)
            keyword = tree_item.text(model_index.column())

            keywords.add(f'"{keyword}"')

        self.setCurrentText('|'.join(keywords))
        self.setFocus()

    def set_active(self):
        if not self._all_match_items:
            return

        self._set_property_active(True)
        self._apply_search()

    def set_inactive(self):
        if not self.is_active:
            return

        self._set_property_active(False)
        self._reset_search()

    def update(self):
        self._highlight_search()

        if self.is_active:
            self._apply_search()

    def update_style(self):
        """ Update the button's style based on its state.
        """
        self.style().unpolish(self)
        self.style().polish(self)

    def bind_key(self, key_sequence: str, function: Callable):
        """Binds a given key sequence to a function.

        Args:
            key_sequence (str): The key sequence as a string, e.g., "Ctrl+C".
            function (Callable): The function to be called when the key sequence is activated.
        """
        # Create a shortcut with the specified key sequence
        shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(key_sequence), self)
        # Connect the activated signal of the shortcut to the given function
        shortcut.activated.connect(function)

    # Special Methods
    # ---------------

    # Event Handling or Override Methods
    # ----------------------------------

def main():
    """Create the application and main window, and show the widget.
    """
    # Create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    # Set theme of QApplication to the dark theme
    set_theme(app, 'dark')

    from example_data_dict import COLUMN_NAME_LIST, ID_TO_DATA_DICT

    # Create the tree widget with example data
    tree_widget = GroupableTreeWidget(column_name_list=COLUMN_NAME_LIST, id_to_data_dict=ID_TO_DATA_DICT)

    # Create an instance of the widget and set it as the central widget
    search_edit = SimpleSearchEdit(tree_widget, parent=window)

    main_widget = QtWidgets.QWidget()
    main_layout = QtWidgets.QVBoxLayout(main_widget)

    main_layout.addWidget(search_edit)
    main_layout.addWidget(tree_widget)

    # search_edit.set_search_column('Name')
    shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+F'), main_widget)
    shortcut.activated.connect(search_edit.set_text_as_selection)

    # Create the scalable view and set the tree widget as its central widget
    scalable_view = ScalableView(widget=main_widget)

    # Add the tree widget to the layout of the widget
    window.setCentralWidget(scalable_view)

    # Show the window
    window.show()

    # Run the application
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
