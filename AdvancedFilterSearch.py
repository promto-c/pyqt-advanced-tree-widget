import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from GroupableTreeWidget import GroupableTreeWidget, COLUMN_NAME_LIST, ID_TO_DATA_DICT

# Load the .ui file using the uic module
ui_file = "ui/AdvancedFilterSearch.ui"
form_class, base_class = uic.loadUiType(ui_file)

class AdvancedFilterSearch(base_class, form_class):
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
        # Set up the UI
        self._setup_ui()
        # Set up signal connections
        self._setup_signal_connections()

    def _setup_initial_values(self):
        ''' Set up the initial values for the widget.
        '''
        self.filter_criteria = []

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
        self.conditionComboBox.addItems(['contains', 'starts with', 'ends with', 'exact match'])

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
            matches_criteria = True
            for criteria in self.filter_criteria:
                # Split the criteria into column, condition, and keyword
                parts = criteria.split()
                column = parts[0]
                condition = parts[1]
                keyword = parts[2]
                # Get the value of the item in the specified column
                value = item.text(self.column_names.index(column))
                # Check if the value matches the condition and keyword
                if condition == 'contains':
                    if keyword not in value:
                        matches_criteria = False
                elif condition == 'starts with':
                    if not value.startswith(keyword):
                        matches_criteria = False
                elif condition == 'ends with':
                    if not value.endswith(keyword):
                        matches_criteria = False
                elif condition == 'exact match':
                    if value != keyword:
                        matches_criteria = False
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

    # Create the tree widget with example data
    tree_widget = GroupableTreeWidget(column_name_list=COLUMN_NAME_LIST, id_to_data_dict=ID_TO_DATA_DICT)

    # Create an instance of the widget and set it as the central widget
    widget = AdvancedFilterSearch(tree_widget)
    window.setCentralWidget(widget)

    # Show the window and run the application
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
