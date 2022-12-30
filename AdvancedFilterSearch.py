import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from theme.theme import setTheme

from GroupableTreeWidget import GroupableTreeWidget, COLUMN_NAME_LIST, ID_TO_DATA_DICT

# Load the .ui file using the uic module
ui_file = "ui/AdvancedFilterSearch.ui"
form_class, base_class = uic.loadUiType(ui_file)

class AdvancedFilterSearch(base_class, form_class):
    ''' A PyQt5 widget that allows the user to apply advanced filters to a tree widget.

    Attributes:
        tree_widget (QtWidgets.QTreeWidget): The tree widget to be filtered.
        column_names (List[str]): The list of column names for the tree widget.
        filter_criteria (List[str]): The list of filter criteria applied to the tree widget.
    '''

    # Define a dictionary of functions for each condition
    CONDITION_TO_FUNCTION_DICT = {
        'contains': lambda value, keyword: keyword in value,
        'starts_with': lambda value, keyword: value.startswith(keyword),
        'ends_with': lambda value, keyword: value.endswith(keyword),
        'exact_match': lambda value, keyword: value == keyword,
    }

    def __init__(self, tree_widget: QtWidgets.QTreeWidget, parent=None):
        ''' Initialize the widget and set up the UI, signal connections, and icon.
            Args:
                tree_widget (QtWidgets.QTreeWidget): The tree widget to be filtered.
                parent (QtWidgets.QWidget): The parent widget.
        '''
        # Initialize the super class
        super(AdvancedFilterSearch, self).__init__(parent)

        # Store the tree widget
        self.tree_widget = tree_widget

        # Set up the initial values
        self._setup_initial_values()
        # Set up type hints for the widgets
        self._setup_type_hints()
        # Set up the UI
        self._setup_ui()
        # Set up signal connections
        self._setup_signal_connections()

    def _setup_initial_values(self):
        ''' Set up the initial values for the widget.
        '''
        self.filter_criteria = []
        self.case_sensitive = False  # Set the initial value to False

    def _setup_type_hints(self):
        ''' Set up type hints for the widgets in the .ui file.
        '''
        # Set up type hints for the widgets
        self.columnComboBox: QtWidgets.QComboBox
        self.conditionComboBox: QtWidgets.QComboBox
        self.keywordLineEdit: QtWidgets.QLineEdit
        self.addFilterButton: QtWidgets.QPushButton
        self.filterListWidget: QtWidgets.QListWidget
        self.applyFiltersButton: QtWidgets.QPushButton
        self.removeFilterButton: QtWidgets.QPushButton
        self.clearFiltersButton: QtWidgets.QPushButton
        self.caseSensitiveCheckBox: QtWidgets.QCheckBox

    def _setup_ui(self):
        ''' Set up the UI for the widget, including creating widgets and layouts.
        '''
        # Set up the UI for the widget
        self.setupUi(self)

        # Get a reference to the header item
        headerItem = self.tree_widget.headerItem()

        # Get the list of column names
        self.column_names = [headerItem.text(i) for i in range(headerItem.columnCount())]

        # Set up combo boxes
        self.columnComboBox.addItems(self.column_names)
        self.conditionComboBox.addItems(self.CONDITION_TO_FUNCTION_DICT.keys())

        # Set up list widget
        self.filterListWidget.addItems(self.filter_criteria)

    def _setup_signal_connections(self):
        ''' Set up signal connections between widgets and slots.
        '''
        # Connect signals to slots
        self.addFilterButton.clicked.connect(self.add_filter)
        self.applyFiltersButton.clicked.connect(self.apply_filters)
        self.removeFilterButton.clicked.connect(self.remove_filter)
        self.clearFiltersButton.clicked.connect(self.clear_filters)
        self.caseSensitiveCheckBox.stateChanged.connect(self.update_case_sensitive)

    def update_case_sensitive(self, state: int):
        ''' Update the case_sensitive member variable when the checkbox state changes.
            Args:
                state (int): The state of the checkbox (0 for unchecked, 2 for checked).
        '''
        self.case_sensitive = state == 2

    def add_filter(self):
        ''' Slot for the "Add Filter" button.
        '''
        # Get the selected column, condition, and keyword
        column = self.columnComboBox.currentText()
        condition = self.conditionComboBox.currentText()
        keyword = self.keywordLineEdit.text()

        # Add the filter criteria to the list
        self.filter_criteria.append(f'{column} {condition} {keyword}')

        # Update the list widget
        self.filterListWidget.clear()
        self.filterListWidget.addItems(self.filter_criteria)

    def apply_filters(self):
        ''' Slot for the "Apply Filters" button.
        '''
        # Filter the tree widget based on the given criteria
        for row in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(row)
            # Check if the item matches all of the filter criteria
            matches_criteria = True  # Assign a default value to matches_criteria
            for criteria in self.filter_criteria:
                # Split the criteria into column, condition, and keyword
                parts = criteria.split()
                column = parts[0]
                condition = parts[1]
                keyword = parts[2]

                # Get the value of the item in the specified column
                value = item.text(self.column_names.index(column))

                # If the search is not case sensitive, convert the keyword and value to lowercase
                if not self.case_sensitive:
                    keyword = keyword.lower()
                    value = value.lower()

                # Check if the value matches the condition and keyword
                matches_criteria = self.CONDITION_TO_FUNCTION_DICT[condition](value, keyword)
                if not matches_criteria:
                    break
            # Set the visibility of the item based on whether it matches the criteria
            item.setHidden(not matches_criteria)

    def remove_filter(self):
        ''' Slot for the "Remove Filter" button.
        '''
        # Get the selected item in the list widget
        selected_items = self.filterListWidget.selectedItems()
        if selected_items:
            # Remove the selected filter criteria from the list
            self.filter_criteria.remove(selected_items[0].text())
            # Update the list widget
            self.filterListWidget.clear()
            self.filterListWidget.addItems(self.filter_criteria)

    def clear_filters(self):
        ''' Slot for the "Clear Filters" button.
        '''
        # Clear the list of filter criteria
        self.filter_criteria.clear()
        # Update the list widget
        self.filterListWidget.clear()

def main():
    ''' Create the application and main window, and show the widget.
    '''
    # Create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    # Set theme of QApplication to the dark theme
    setTheme(app, 'dark')

    # Create the tree widget with example data
    tree_widget = GroupableTreeWidget(column_name_list=COLUMN_NAME_LIST, id_to_data_dict=ID_TO_DATA_DICT)

    # Create an instance of the widget and set it as the central widget
    widget = AdvancedFilterSearch(tree_widget)
    window.setCentralWidget(widget)

    # Add the tree widget to the layout of the widget
    widget.layout().addWidget(tree_widget)

    # Show the window and run the application
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
