# pyqt-advanced-tree-widget

<p align="center">
    <img src="screenshots\screenshot1.png" width="350" />
    <img src="screenshots\screenshot2.png" width="350" /> 
    <img src="screenshots\screenshot3.png" width="350" />
    <img src="screenshots\screenshot4.png" width="350" />
</p>

## GroupableTreeWidget
---
This repository contains a PyQt5 implementation of a GroupableTreeWidget class that displays data in a tree structure with the ability to group data by a specific column.

### Example usage
Here is an example of how to use the GroupableTreeWidget class:

```python
import sys
from PyQt5 import QtWidgets

from GroupableTreeWidget import GroupableTreeWidget

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
tree_widget = GroupableTreeWidget(column_name_list=COLUMN_NAME_LIST, 
                         id_to_data_dict=ID_TO_DATA_DICT)

# Show the tree widget
tree_widget.show()

# Run the application
sys.exit(app.exec_())
```
### Features
The GroupableTreeWidget class has the following features:

Ability to set the column names and data to be displayed in the tree widget.
Context menu for the header that allows the user to group the data by a specific column.
Option to expand or collapse all groups.

## ScalableView
___

The ScalableView class is a PyQt5 widget that extends the QGraphicsView class and provides the ability to scale the contents of the view using the mouse wheel. The ScalableView class takes a parent widget and a widget to be displayed in the view as arguments in its constructor.

### Example usage
Here is an example of how to use the ScalableView class:

```python
import sys
from PyQt5 import QtWidgets

from GroupableTreeWidget import GroupableTreeWidget
from ScalableView import ScalableView

# Create the application and tree widget
app = QtWidgets.QApplication(sys.argv)
tree_widget = GroupableTreeWidget(column_name_list=COLUMN_NAME_LIST, 
                         id_to_data_dict=ID_TO_DATA_DICT)

# Create the scalable view widget and set the tree widget as the widget to be displayed in the view
scalable_view = ScalableView(widget=tree_widget)

# Show the scalable view widget
scalable_view.show()

# Run the application
sys.exit(app.exec_())
```

### Features
The ScalableView class has the following features:

- The ability to scale the contents of the view using the mouse wheel while pressing the Ctrl key.
- Minimum and maximum zoom levels that can be set to limit the amount of scaling.
- The ability to reset the zoom level to the default value (1.0 or no zoom) by pressing "F".

### Setting up the Context Menu (QMenu)
When setting up the context menu (QMenu) in the widget class that is used with ScalableView, follow these steps to ensure proper display within the view:

1. In the `ScalableView` class, a reference to the `ScalableView` object is already assigned to the widget using the following line of code:

    ```python
    self.widget.scalable_view = self
    ```

    This assignment establishes a reference from the widget to the `ScalableView` object.

    The purpose of this reference is to enable the widget to access and utilize functionalities or properties of the `ScalableView` object. By having this reference, the widget can interact with the `ScalableView` object when necessary, such as when creating context menus (QMenu) within the widget.

    To access the `ScalableView` object from the widget, you can use `self.scalable_view`.

2. When creating instances of `QMenu` within the widget class, use `self.scalable_view` as the parent argument if it is available and an instance of `QtWidgets.QGraphicsView`. Otherwise, use `self` as the parent argument. This ensures that the context menu is associated with the `ScalableView` object and displayed correctly within the view.

    ```python
    if hasattr(self, 'scalable_view') and isinstance(self.scalable_view, QtWidgets.QGraphicsView):
        menu = QtWidgets.QMenu(self.scalable_view)
    else:
        menu = QtWidgets.QMenu(self)
    ```

    Replace `self` with `self.scalable_view` in any relevant places where `QMenu` instances are created.

Following these steps will ensure that the context menu is properly displayed within the ScalableView, preventing cutoff issues.

## AdvancedFilterSearch
___

The AdvancedFilterSearch module is a PyQt5 widget that extends the GroupableTreeWidget class with additional filter and search functionality. It allows the user to filter and search the data in the tree structure based on specific criteria.
### Example usage
Here is an example of how to use the AdvancedFilterSearch class:

```python
import sys
from PyQt5 import QtWidgets

from GroupableTreeWidget import GroupableTreeWidget
from AdvancedFilterSearch import AdvancedFilterSearch

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

# Create the application and the main window
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()

# Create the tree widget with example data
tree_widget = GroupableTreeWidget(column_name_list=COLUMN_NAME_LIST, id_to_data_dict=ID_TO_DATA_DICT)

# Create an instance of the widget and set it as the central widget
widget = AdvancedFilterSearch(tree_widget)
widget.set_column_filter('Name')
window.setCentralWidget(widget)

# Add the tree widget to the layout of the widget
widget.layout().addWidget(tree_widget)

# Show the window
window.show()

# Run the application
sys.exit(app.exec_())
```

### Features
The AdvancedFilterSearch class has the following features:

- Filter the data in the tree structure based on specific criteria.
- Search for the data in the tree structure based on specific criteria, and highlight the matching items.
- Ability to add multiple filters and search criteria.
- Option to clear all filters and search criteria.

## Requirements
___
The GroupableTreeWidget class requires PyQt5 to be installed. You can install PyQt5 using pip:

```
pip install PyQt5
```
___
**Note:** This README file was generated by ChatGPT.
