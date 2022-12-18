import sys
from PyQt5 import QtWidgets, QtCore

COLUMN_NAME_LIST = ["ID", "Name", "Age", "City"]
ID_TO_DATA_DICT = {
    1: {
        "Name": "Alice", 
        "Age": "30", 
        "City": "New York"},
    2: {
        "Name": "Bob", 
        "Age": "25", 
        "City": 
        "Chicago"},
    3: {
        "Name": "Charlie", 
        "Age": "35", 
        "City": "Los Angeles"},
}

class TreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Customize the widget as desired
        self.setHeaderLabel("Tree Widget")
        
        # Set up the context menu for the header
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.on_header_context_menu)
        
        # Create a dictionary to store the groups for each column
        self.groups = {}
        
        # Set up the columns
        self.setColumnCount(len(COLUMN_NAME_LIST))
        self.setHeaderLabels(COLUMN_NAME_LIST)
                
        # Add the data to the widget
        self.add_items( ID_TO_DATA_DICT )
        
    def add_items(self, id_to_data_dict):
        # Iterate through the dictionary of items
        for item_id, item_data in id_to_data_dict.items():
            # Create a list of data for the tree item
            item_data_list = [str(item_id)] + [item_data[column] for column in COLUMN_NAME_LIST[1:]]
            
            # Create a new QTreeWidgetItem with the item data
            tree_item = QtWidgets.QTreeWidgetItem(item_data_list)
            
            # Add the tree item to the tree widget
            self.addTopLevelItem(tree_item)
            
    def on_header_context_menu(self, pos):
        # Get the index of the column where the right click occurred
        column = self.header().logicalIndexAt(pos)
        
        # Create the context menu
        menu = QtWidgets.QMenu(self)
        group_by_action = menu.addAction("Group by this column")
        group_by_action.triggered.connect(lambda: self.group_by_column(column))
        
        # Show the context menu
        menu.popup(self.header().mapToGlobal(pos))
        
    def group_by_column(self, column):
        # Clear any existing groups for this column
        self.clear_groups(column)
        
        # Get the data for each tree item in the column
        data = [self.topLevelItem(row).data(column, QtCore.Qt.DisplayRole) for row in range(self.topLevelItemCount())]
        
        # Group the data and add the tree items to the appropriate group
        groups = self.group_data(data)
        for group_name, items in groups.items():
            group_item = QtWidgets.QTreeWidgetItem(self, [group_name])
            for item in items:
                group_item.addChild(item)
            self.addTopLevelItem(group_item)
            
        # Save the groups for this column
        self.groups[column] = groups
        
    def clear_groups(self, column):
        # Remove the tree items from the widget and delete them
        for group_item in self.groups.get(column, {}).values():
            for item in group_item:
                self.removeItemWidget(item, 0)
                del item
        
        # Clear the groups for this column
        self.groups[column] = {}
        
    def group_data(self, data):
        # Create a dictionary to store the groups
        groups = {}

        # Group the data
        for i, item_data in enumerate(data):
            # If the data is empty, add it to the "_others" group
            if not item_data:
                item_data = "_others"

            # Add the tree item to the appropriate group
            item = self.topLevelItem(i)
            if item_data in groups:
                groups[item_data].append(item)
            else:
                groups[item_data] = [item]

        return groups

def main():
    app = QtWidgets.QApplication(sys.argv)
    tree_widget = TreeWidget()
    tree_widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()