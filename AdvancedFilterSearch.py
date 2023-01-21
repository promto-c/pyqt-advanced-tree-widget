import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtSvg import QSvgRenderer
from theme.theme import setTheme

from TablerQIcon import TablerQIcon

from GroupableTreeWidget import GroupableTreeWidget, COLUMN_NAME_LIST, ID_TO_DATA_DICT

# Load the .ui file using the uic module
ui_file = "ui/AdvancedFilterSearch.ui"
form_class, base_class = uic.loadUiType(ui_file)

class AdvancedFilterSearch(base_class, form_class):
    ''' A PyQt5 widget that allows the user to apply advanced filters to a tree widget.

    Attributes:
        tree_widget (QtWidgets.QTreeWidget): The tree widget to be filtered.
        column_names (List[str]): The list of column names for the tree widget.
        filter_criteria_list (List[str]): The list of filter criteria applied to the tree widget.
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
        self.filter_criteria_list = list()
        self.is_case_sensitive = False
        self.tabler_action_qicon = TablerQIcon()
        self.tabler_button_qicon = TablerQIcon(color='#aaaaaa')

    def _setup_type_hints(self):
        ''' Set up type hints for the widgets in the .ui file.
        '''
        # Set up type hints for the widgets
        self.columnComboBox: QtWidgets.QComboBox
        self.conditionComboBox: QtWidgets.QComboBox
        self.keywordLineEdit: QtWidgets.QLineEdit
        self.addFilterButton: QtWidgets.QPushButton
        self.filterTreeWidget: QtWidgets.QTreeWidget
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

        self.setup_filter_tree_widget()

        self.add_action_on_keyword_line_edit()

        self.addFilterButton.setIcon( self.tabler_button_qicon.filter )
        self.addFilterButton.setIcon( self.tabler_button_qicon.filter_add )
        
    def add_action_on_keyword_line_edit(self):
        self.matchCaseAction = self.keywordLineEdit.addAction(self.tabler_action_qicon.letter_case, QtWidgets.QLineEdit.TrailingPosition)
        self.matchCaseAction.setCheckable(True)

        self.negateAction = self.keywordLineEdit.addAction(self.tabler_action_qicon.zoom_cancel, QtWidgets.QLineEdit.TrailingPosition)
    
    def _setup_signal_connections(self):
        ''' Set up signal connections between widgets and slots.
        '''
        # Connect signals to slots
        self.addFilterButton.clicked.connect(self.add_filter)
        self.keywordLineEdit.returnPressed.connect(self.add_filter)
        self.matchCaseAction.triggered.connect(self.update_case_sensitive)

    def setup_filter_tree_widget(self):

        # Set up filter tree widget header columns
        self.filterTreeWidget.setHeaderLabels(['Column', 'Condition', 'Keyword', ''])

        self.filterTreeWidget.setMinimumWidth(32)
        self.filterTreeWidget.setColumnWidth(3, 32)
        
        self.filterTreeWidget.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.filterTreeWidget.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.filterTreeWidget.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.add_clear_button_on_header()

    def add_clear_button_on_header(self):
        # Add a clear filters button to the header
        header = self.filterTreeWidget.header()
        viewport = header.viewport()

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        viewport.setLayout( layout )

        horizontal_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        layout.addItem(horizontal_spacer)

        clear_button = QtWidgets.QPushButton(self.tabler_button_qicon.clear_all, '', self)
        clear_button.setToolTip('Clear all filter')
        clear_button.clicked.connect(self.clear_filters)
        clear_button.setMinimumSize(QtCore.QSize(27, 16777215))
        layout.addWidget(clear_button)

    def update_case_sensitive(self, state: bool):
        ''' Update the is_case_sensitive member variable when the match case action state changes.
            Args:
                state (bool): The state of match case action.
        '''
        self.is_case_sensitive = state

    def add_filter(self):
        ''' Add a filter to the tree widget. Called when the "Add Filter" button is clicked 
            or when the Enter key is pressed in the keywordLineEdit widget.
        '''
        # Get the selected column, condition, and keyword
        column = self.columnComboBox.currentText()
        condition = self.conditionComboBox.currentText()
        keyword = self.keywordLineEdit.text()

        # Return if the keyword is empty
        if not keyword:
            return

        # Clear the keywordLineEdit widget
        self.keywordLineEdit.clear()

        filter_criteria = [column, condition, keyword]

        # Return if the filter criteria (column, condition, keyword) is already in the filter criteria list
        if filter_criteria in self.filter_criteria_list:
            return

        # Add the filter criteria to the list
        self.filter_criteria_list.append(filter_criteria)

        # Create a new tree widget item with the column, condition, and keyword
        filter_tree_item = QtWidgets.QTreeWidgetItem(self.filterTreeWidget, filter_criteria)
        # Store the filter criteria in a data_list attribute of the tree widget item
        filter_tree_item.data_list = filter_criteria

        self.add_remove_item_button(filter_tree_item)

        self.apply_filters()

    def add_remove_item_button(self, tree_item):
        remove_button = QtWidgets.QPushButton(self.tabler_button_qicon.trash, '', self)
        remove_button.setToolTip('Remove this filter item')
        remove_button.clicked.connect(lambda: self.remove_filter(tree_item))
        self.filterTreeWidget.setItemWidget(tree_item, 3, remove_button)

    def apply_filters(self):
        ''' Slot for the "Apply Filters" button.
        '''
        # Filter the tree widget based on the given criteria
        for row in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(row)

            # Assign a default value to matches_criteria
            matches_criteria = True  

            # Check if the item matches all of the filter criteria
            for column, condition, keyword in self.filter_criteria_list:

                # Get the value of the item in the specified column
                value = item.text(self.column_names.index(column))

                # If the search is not case sensitive, convert the keyword and value to lowercase
                if not self.is_case_sensitive:
                    keyword = keyword.lower()
                    value = value.lower()

                # Check if the value matches the condition and keyword
                matches_criteria = self.CONDITION_TO_FUNCTION_DICT[condition](value, keyword)
                if not matches_criteria:
                    break

            # Set the visibility of the item based on whether it matches the criteria
            item.setHidden(not matches_criteria)

    def remove_filter(self, filter_tree_item):
        ''' Slot for the "Remove Filter" button.
        '''

        # Remove the selected filter criteria from the list
        self.filter_criteria_list.remove(filter_tree_item.data_list)
        # Remove the selected item at index 0
        item = self.filterTreeWidget.takeTopLevelItem(self.filterTreeWidget.indexOfTopLevelItem(filter_tree_item))
        # Delete the item object. This will remove the item from memory and break any references to it.
        del item

        self.apply_filters()

    def clear_filters(self):
        ''' Slot for the "Clear Filters" button.
        '''
        # Clear the list of filter criteria
        self.filter_criteria_list.clear()
        # Clear the tree widget
        self.filterTreeWidget.clear()

        self.apply_filters()

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
