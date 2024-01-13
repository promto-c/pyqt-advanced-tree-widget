import sys, os, re
from pathlib import Path
from typing import Any, List, Union

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from tablerqicon import TablerQIcon

from theme.theme import set_theme

from widgets.filter_widget import MultiSelectFilterWidget
from widgets.groupable_tree_widget import GroupableTreeWidget, COLUMN_NAME_LIST, ID_TO_DATA_DICT
from widgets.scalable_view import ScalableView
from widgets.item_delegate import HighlightItemDelegate


# Class Definitions
# -----------------
class SimpleSearchEdit(QtWidgets.QComboBox):
    """

    Attributes:
        ...
    """
    # Initialization and Setup
    # ------------------------
    def __init__(self, tree_widget: QtWidgets.QTreeWidget, parent: QtWidgets.QWidget= None):
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
        # Initialize the HighlightItemDelegate object to highlight items in the tree widget.
        self.highlight_item_delegate = HighlightItemDelegate()

        # Private Attributes
        # ------------------
        ...

    def __setup_ui(self):
        """Set up the UI for the widget, including creating widgets, layouts, and setting the icons for the widgets.
        """
        self.setEditable(True)
        self.setProperty('widget-style', 'round')

        self.lineEdit().setPlaceholderText('Type to Search')
        self.setFixedHeight(24)
        self.tabler_icon = TablerQIcon(opacity=0.6)
        self.l = QtWidgets.QHBoxLayout(self)
        self.l.setContentsMargins(0, 0, 0, 0)

        self.lineEdit().addAction(self.tabler_icon.search, QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
        self.lineEdit().setProperty('has-placeholder', True)
        # self.setProperty('active', True)
        # self.lineEdit().textChanged.connect(lambda text: self.setProperty('active', bool(text)))
        self.lineEdit().textChanged.connect(lambda: (self.style().unpolish(self), self.style().polish(self)))

        # Create widgets and layouts
        ...
        # Set the layout for the widget
        ...

    def __setup_signal_connections(self):
        """Set up signal connections between widgets and slots.
        """
        # Connect signals to slots
        self.editTextChanged.connect(self._highlight_search)

    # Private Methods
    # ---------------
    def _highlight_search(self):
        """Highlight the items in the tree widget that match the search criteria.
        """
        # Reset the highlight for all items
        self._reset_highlight_all_items()

        # Get the selected column, condition, and keyword
        keyword = self.currentText()

        # Return if the keyword is empty
        if not keyword:
            return
        
        flags = QtCore.Qt.MatchFlag.MatchRecursive

        if self.is_contains_wildcard(keyword):
            flags |= QtCore.Qt.MatchFlag.MatchWildcard
        else:
            flags |= QtCore.Qt.MatchFlag.MatchContains
        
        # match_items = list()
        for column_index in range(self.tree_widget.columnCount()):
            match_items = self.tree_widget.findItems(keyword, flags, column_index)
        # match_items = self.tree_widget.findItems(keyword, flags, 0)
            # print(len(match_items))
        # Find the items that match the search criteria
        # match_items = self.find_match_items(column, condition, keyword, is_negate, is_case_sensitive)

            # Highlight the matched items
            self._highlight_items(match_items, column_index)

    def _highlight_items(self, tree_items: List[QtWidgets.QTreeWidgetItem], focused_column_index = None):
        """Highlight the specified `tree_items` in the tree widget.
        """
        # Reset the previous target model indexes
        # self.highlight_item_delegate.target_model_indexes = list()

        # Loop through the specified tree items
        for tree_item in tree_items:

            # Add the model indexes of the current tree item to the target properties
            self.highlight_item_delegate.target_model_indexes.extend(tree_item.get_model_indexes())

            if focused_column_index is None:
                continue

            focused_model_index = self.tree_widget.indexFromItem(tree_item, focused_column_index)
            self.highlight_item_delegate.target_focused_model_indexes.append(focused_model_index)

        # Set the item delegate for the current row to the highlight item delegate
        self.tree_widget.setItemDelegate(self.highlight_item_delegate)

    def _reset_highlight_all_items(self):
        """Reset the highlight of all items in the tree widget.

            This method resets the highlighting of all items in the tree widget by setting the delegate for each row to `None`.
            The target model index properties stored in `self.highlight_item_delegate` will also be reset to an empty list.
        """
        # Reset the target model index properties
        self.highlight_item_delegate.clear()

        # Get all items in the tree widget
        all_items = self.tree_widget.get_all_items()

        # Loop through all items
        for tree_item in all_items:
            # Get the row index of the item
            item_index = self.tree_widget.indexFromItem(tree_item).row()
            # Set the delegate for the row to None
            self.tree_widget.setItemDelegateForRow(item_index, None)

    # Public Methods
    # --------------
    @staticmethod
    def split_keyswords(text):
        return re.split('[\t\n,|]+', text)

    @staticmethod
    def is_contains_wildcard(text):
        return '*' in text or '?' in text

    # Extended Methods
    # ----------------

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

    # Create the tree widget with example data
    tree_widget = GroupableTreeWidget(column_name_list=COLUMN_NAME_LIST, id_to_data_dict=ID_TO_DATA_DICT)

    # Create an instance of the widget and set it as the central widget
    search_edit = SimpleSearchEdit(tree_widget, parent=window)

    main_widget = QtWidgets.QWidget()
    main_layout = QtWidgets.QVBoxLayout(main_widget)

    main_layout.addWidget(search_edit)
    main_layout.addWidget(tree_widget)

    # search_edit.set_search_column('Name')

    
    

    
    # Create the scalable view and set the tree widget as its central widget
    scalable_view = ScalableView(widget=main_widget)

    # multi_select_filter_widget = MultiSelectFilterWidget('multi', scalable_view)
    # multi_select_filter_widget.add_items('aaa', ['sgfg', 'aaa'])
    # multi_select_filter_widget.update_completer()
    # main_layout.addWidget(multi_select_filter_widget.button)

    # Add the tree widget to the layout of the widget
    window.setCentralWidget(scalable_view)

    # Show the window
    window.show()

    # Run the application
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
