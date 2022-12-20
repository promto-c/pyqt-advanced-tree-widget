# pyqt-widget-example
## PyQt TreeWidget
This repository contains a PyQt5 implementation of a TreeWidget class that displays data in a tree structure with the ability to group data by a specific column.

### Example usage
Here is an example of how to use the TreeWidget class:

```python
import sys
from PyQt5 import QtWidgets

# Define example data
COLUMN_NAME_LIST = ["ID", "Name", "Age", "City"]
ID_TO_DATA_DICT = {
    1: {
        "Name": "Alice", 
        "Age": "30", 
        "City": "New York"},
    2: {
        "Name": "Bob", 
        "Age": "25", 
        "City": "Chicago"},
    3: {
        "Name": "Charlie", 
        "Age": "35", 
        "City": "Los Angeles"},
}

# Create the application and tree widget
app = QtWidgets.QApplication(sys.argv)
tree_widget = TreeWidget(column_name_list=COLUMN_NAME_LIST, 
                         id_to_data_dict=ID_TO_DATA_DICT)

# Show the tree widget
tree_widget.show()

# Run the application
sys.exit(app.exec_())
```
### Features
The TreeWidget class has the following features:

Ability to set the column names and data to be displayed in the tree widget.
Context menu for the header that allows the user to group the data by a specific column.
Option to expand or collapse all groups.
## Requirements
The TreeWidget class requires PyQt5 to be installed. You can install PyQt5 using pip:

```
pip install PyQt5
```
