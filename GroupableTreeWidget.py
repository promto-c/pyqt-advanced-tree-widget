import sys
from typing import Any, Dict, List, Union

from PyQt5 import QtWidgets, QtCore, QtGui

from theme.theme import setTheme

# Define example data
COLUMN_NAME_LIST = ['ID', 'Name', 'Age', 'City']
ID_TO_DATA_DICT = {
    1: {
        'Name': 'Alice',
        'Age': 30,
        'City': 'New York'},
    2: {
        'Name': 'Bob',
        'Age': 25,
        'City': 'Chicago'},
    3: {
        'Name': 'Charlie',
        'Age': 35,
        'City': 'Los Angeles'},
    4: {
        'Name': 'David',
        'Age': 40,
        'City': 'San Francisco'},
    5: {
        'Name': 'Emily',
        'Age': 28,
        'City': 'Boston'},
    6: {
        'Name': 'Frank',
        'Age': 32,
        'City': 'New York'},
    7: {
        'Name': 'Gina',
        'Age': 27,
        'City': 'Chicago'},
    8: {
        'Name': 'Henry',
        'Age': 38,
        'City': 'Los Angeles'},
    9: {
        'Name': 'Irene',
        'Age': 29,
        'City': 'San Francisco'},
    10: {
        'Name': 'Jack',
        'Age': 33,
        'City': 'Boston'},
    }

class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    ''' A custom `QTreeWidgetItem` that can handle different data formats and store additional data in the user role.

    Attributes:
        id (int): The ID of the item.
    '''

    def __init__(self, parent: QtWidgets.QTreeWidget = None, 
                 item_data: Union[Dict[str, Any], List[str]] = None, 
                 item_id: int = None):
        ''' Initialize the `TreeWidgetItem` with the given parent and item data.
        
        Args:
            parent (QtWidgets.QTreeWidget, optional): The parent `QTreeWidget`. Defaults to `None`.
            item_data (Union[Dict[str, Any], List[str]], optional): The data for the item. Can be a list of strings or a dictionary with keys matching the headers of the parent `QTreeWidget`. Defaults to `None`.
            item_id (int, optional): The ID of the item. Defaults to `None`.
        '''
        # Set the item's ID
        self.id = item_id

        # If the data for the item is in list form
        if isinstance(item_data, list):
            item_data_list = item_data

        # If the data for the item is in dictionary form
        if isinstance(item_data, dict):
            # Get the header item from the parent tree widget
            header_item = parent.headerItem()
            # Get the column names from the header item
            column_names = [header_item.text(i) for i in range(header_item.columnCount())]

            # Create a list of data for the tree item
            item_data_list = [item_id] + [item_data[column] if column in item_data.keys()
                                                                 else str() 
                                                                 for column in column_names[1:]]
            
        # Call the superclass's constructor to set the item's data
        super(TreeWidgetItem, self).__init__(parent, map(str, item_data_list))

        # Set the UserRole data for the item.
        self.set_user_role_data(item_data_list)

    def set_user_role_data(self, item_data_list: List[Any]):
        ''' Set the UserRole data for the item.

        Args:
            item_data_list (List[Any]): The list of data to set as the item's data.
        '''
        # Iterate through each column in the item
        for column_index, value in enumerate(item_data_list):
            # Set the value for the column in the UserRole data
            self.setData(column_index, QtCore.Qt.UserRole, value)
            
    def __lt__(self, other_item: QtWidgets.QTreeWidgetItem) -> bool:
        ''' Sort the items in the tree widget based on their data.

        Args:
            other_item (QtWidgets.QTreeWidgetItem): The item to compare with.

        Returns:
            bool: Whether this item is less than the other item.
        '''
        # Get the column that is currently being sorted
        column = self.treeWidget().sortColumn()

        # Get the UserRole data for the column for both this item and the other item
        data_a = self.data(column, QtCore.Qt.UserRole)
        data_b = other_item.data(column, QtCore.Qt.UserRole)

        # If both UserRole data are None, compare their texts
        if not data_a and not data_b:
            return self.text(column) < other_item.text(column)
        # If this item's UserRole data is None, it is considered greater
        elif not data_a:
            return True
        # If the other item's UserRole data is None, this item is considered greater
        elif not data_b:
            return False

        try:
            # Try to compare the UserRole data directly
            return data_a < data_b
        except TypeError:
            # If the comparison fails, compare their string representations
            return (str(data_a) < str(data_b))

class GroupableTreeWidget(QtWidgets.QTreeWidget):
    ''' A QTreeWidget subclass that displays data in a tree structure with the ability to group data by a specific column.

    Attributes:
        column_name_list (List[str]): The list of column names to be displayed in the tree widget.
        id_to_data_dict (Dict[int, Dict[str, str]]): A dictionary mapping item IDs to their data as a dictionary.
        groups (Dict[str, QtWidgets.QTreeWidgetItem]): A dictionary mapping group names to their tree widget items.
    '''
    def __init__(self, parent: QtWidgets.QWidget = None, 
                       column_name_list: List[str] = list(), 
                       id_to_data_dict: Dict[int, Dict[str, str]] = dict() ):
        # Call the parent class constructor
        super(GroupableTreeWidget, self).__init__(parent)

        # Store the column names and data dictionary for later use
        self.column_name_list = column_name_list
        self.id_to_data_dict = id_to_data_dict
        
        # Set up the initial values
        self._setup_initial_values()
        # Set up the UI
        self._setup_ui()
        # Set up signal connections
        self._setup_signal_connections()

    def _setup_initial_values(self):
        ''' Set up the initial values for the widget.
        '''
        # Store the current grouped column name
        self.grouped_column_name = str()

    def _setup_ui(self):
        ''' Set up the UI for the widget, including creating widgets and layouts.
        '''
        # Set up the context menu for the header
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # Set up the columns
        self.set_column_name_list(self.column_name_list)
        # Add the data to the widget
        self.add_items(self.id_to_data_dict)

        # Enable sorting in the tree widget
        self.setSortingEnabled(True)

        # Enable uniform row heights
        self.setUniformRowHeights(True)

    def _setup_signal_connections(self):
        ''' Set up signal connections between widgets and slots.
        '''
        # Connect signal of header
        self.header().customContextMenuRequested.connect(self.on_header_context_menu)

    def set_column_name_list(self, column_name_list: List[str]) -> None:
        ''' Set the names of the columns in the tree widget.

        Args:
            column_name_list (List[str]): The list of column names to be set.
        '''
        # Store the column names for later use
        self.column_name_list = column_name_list

        # Set the number of columns and the column labels
        self.setColumnCount(len(self.column_name_list))
        self.setHeaderLabels(self.column_name_list)

    def add_items(self, id_to_data_dict: Dict[int, Dict[str, str]]) -> None:
        ''' Add items to the tree widget.

        Args:
            id_to_data_dict (Dict[int, Dict[str, str]]): A dictionary mapping item IDs to their data as a dictionary.
        '''
        # Store the data dictionary for later use
        self.id_to_data_dict = id_to_data_dict

        # Iterate through the dictionary of items
        for item_id, item_data in self.id_to_data_dict.items():
            # Create a new custom QTreeWidgetItem for sorting by type of the item data, and add to the self tree widget
            tree_item = TreeWidgetItem(self, item_data=item_data, item_id=item_id)

        # Resize all columns to fit their contents
        self.resize_to_contents()

    def on_header_context_menu(self, pos: QtCore.QPoint) -> None:
        ''' Show a context menu for the header of the tree widget.

        Context Menu:
            +-------------------------------+
            | Group by this column          |
            | Ungroup all                   |
            | ----------------------------- |
            | Fit in View                   |
            +-------------------------------+

        Args:
            pos (QtCore.QPoint): The position where the right click occurred.
        '''
        # Get the index of the column where the right click occurred
        column = self.header().logicalIndexAt(pos)
        
        # Create the context menu
        menu = QtWidgets.QMenu(self)
        
        # Create the 'Group by this column' action and connect it to the 'group_by_column' method. Pass in the selected column as an argument.
        group_by_action = menu.addAction('Group by this column')
        group_by_action.triggered.connect(lambda: self.group_by_column(column))
        
        # Create the 'Ungroup all' action and connect it to the 'ungroup_all' method.
        ungroup_all_action = menu.addAction('Ungroup all')
        ungroup_all_action.triggered.connect(self.ungroup_all)

        # Add a separator
        menu.addSeparator()
        
        # Add the 'Fit in View' action and connect it to the 'fit_column_in_view' method.
        fit_column_in_view_action = menu.addAction('Fit in View')
        fit_column_in_view_action.triggered.connect(self.fit_column_in_view)
                
        # Disable 'Group by this column' on first column
        if not column:
            group_by_action.setDisabled(True)

        # Show the context menu
        menu.popup(self.header().mapToGlobal(pos))
        
    def group_by_column(self, column: int) -> None:
        ''' Group the items in the tree widget by the values in the specified column.

        Args:
            column (int): The index of the column to group by.
        '''
        # Ungroup all items in the tree widget
        self.ungroup_all()

        # Hide the grouped column
        self.setColumnHidden(column, True)

        # Get the label for the column that we want to group by and the label for the first column 
        self.grouped_column_name = self.headerItem().text(column)
        first_column_label = self.headerItem().text(0)
        
        # Rename the first column
        self.setHeaderLabel(f'{self.grouped_column_name} / {first_column_label}')
        
        # Get the data for each tree item in the column
        data = [self.topLevelItem(row).data(column, QtCore.Qt.DisplayRole) for row in range(self.topLevelItemCount())]
        
        # Group the data and add the tree items to the appropriate group
        groups = self.group_data(data)

        # Iterate through each group and its items
        for group_name, items in groups.items():
            # Create a new QTreeWidgetItem for the group
            group_item = TreeWidgetItem(self, [group_name])
            
            # Add the items to the group item as children
            for item in items:
                # Save the original parent and position of the tree item
                original_parent = item.parent()
                original_row = original_parent.indexOfChild(item) if original_parent else self.indexOfTopLevelItem(item)

                # Remove the tree item from its original parent
                if original_parent:
                    original_parent.takeChild(original_row)
                else:
                    self.takeTopLevelItem(original_row)

                # Add the tree item to the group item as a child and restore its original position
                group_item.addChild(item)
            
        # Expand all items
        self.expandAll()

        # Resize all columns to fit their contents
        self.resize_to_contents()
        
    def fit_column_in_view(self) -> None:
        ''' Adjust the width of all columns to fit the entire view.
    
            This method resizes columns so that their sum is equal to the width of the view minus the width of the vertical scroll bar. 
            It starts by reducing the width of the column with the largest width by 10% until all columns fit within the expected width.
        '''
        # Get the expected width of the columns (the width of the view minus the width of the scroll bar)
        expect_column_width = self.size().width() - self.verticalScrollBar().width()
        # Calculate the sum of the current column widths
        column_width_sum = sum(self.columnWidth(column) for column in range(self.columnCount()))
        
        # Loop until all columns fit within the expected width
        while column_width_sum > expect_column_width:
            # Find the column with the largest width
            largest_column = max(range(self.columnCount()), key=lambda x: self.columnWidth(x))
            # Reduce the width of the largest column by 10%
            new_width = max(self.columnWidth(largest_column) - expect_column_width // 10, 0)
            self.setColumnWidth(largest_column, new_width)
            # Update the sum of the column widths
            column_width_sum -= self.columnWidth(largest_column) - new_width

    def resize_to_contents(self) -> None:
        ''' Resize all columns in the object to fit their contents.
        '''
        # Iterate through all columns
        for column_index in range(self.columnCount()):  
            # Resize the column to fit its contents
            self.resizeColumnToContents(column_index) 

    def ungroup_all(self) -> None:
        ''' Ungroup all the items in the tree widget.
        '''
        # Return if there are no groups to ungroup
        if not self.grouped_column_name:
            return

        # Reset the header label
        self.setHeaderLabel(self.column_name_list[0])
        
        # Show hidden column
        column_index = self.column_name_list.index(self.grouped_column_name)
        self.setColumnHidden(column_index, False)

        # Get a list of all the top-level items in the tree widget
        group_item_list = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]

        # Iterate through all the top-level items in the tree widget
        for group_item in group_item_list:

            # Remove all of its children and add them as top-level items
            child_items = group_item.takeChildren()
            self.addTopLevelItems(child_items)

            # Remove the group item from the top-level items
            self.takeTopLevelItem(self.indexOfTopLevelItem(group_item))

        # Clear the grouped column label
        self.grouped_column_name = str()

        # Resize all columns to fit their contents
        self.resize_to_contents()
        
    def group_data(self, data: List[str]) -> Dict[str, List[QtWidgets.QTreeWidgetItem]]:
        ''' Group the data into a dictionary mapping group names to lists of tree items.

        Args:
            data (List[str]): The data to be grouped.

        Returns:
            Dict[str, List[QtWidgets.QTreeWidgetItem]]: A dictionary mapping group names to lists of tree items.
        '''
        # Create a dictionary to store the groups
        groups = {}

        # Group the data
        for i, item_data in enumerate(data):
            # If the data is empty, add it to the '_others' group
            if not item_data:
                item_data = '_others'

            # Add the tree item to the appropriate group
            item = self.topLevelItem(i)
            if item_data in groups:
                groups[item_data].append(item)
            else:
                groups[item_data] = [item]

        return groups

def main():
    ''' Create the application and main window, and show the widget.
    '''
    # Create the application and the main window
    app = QtWidgets.QApplication(sys.argv)

    # Set theme of QApplication to the dark theme
    setTheme(app, 'dark')

    # Create an instance of the widget and set it as the central widget
    tree_widget = GroupableTreeWidget(
        column_name_list=COLUMN_NAME_LIST,
        id_to_data_dict=ID_TO_DATA_DICT
    )

    # Show the window and run the application
    tree_widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
