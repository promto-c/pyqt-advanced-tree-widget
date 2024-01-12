from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from PyQt5 import QtCore, QtGui, QtWidgets

def extract_all_items_from_tree(tree_widget: 'QtWidgets.QTreeWidget') -> List['QtWidgets.QTreeWidgetItem']:
    """This function returns all the items in the tree widget as a list.

    The items are sorted based on their order in the tree structure, 
    with children appearing after their parent items for each grouping.

    Returns:
        List[TreeWidgetItem]: A list containing all the items in the tree widget.
    """
    def traverse_items(parent_item: 'QtWidgets.QTreeWidgetItem', 
                       items: List['QtWidgets.QTreeWidgetItem'] = list()) -> List['QtWidgets.QTreeWidgetItem']:
        # Recursively traverse the children of the current item
        for child_index in range(parent_item.childCount()):
            # Get the child item at the current index
            child_item = parent_item.child(child_index)

            # Add the current child item to the list
            items.append(child_item)
            # Recursively traverse the children of the current child item
            items = traverse_items(child_item, items)

        return items

    # Get the root item of the tree widget
    root_item = tree_widget.invisibleRootItem()

    # Traverse the items in a depth-first manner and collect them in a list
    return traverse_items(root_item)
