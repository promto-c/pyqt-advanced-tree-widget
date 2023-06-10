import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from typing import Any, List, Tuple

from theme.theme import set_theme

from TablerQIcon import TablerQIcon

from GroupableTreeWidget import GroupableTreeWidget, COLUMN_NAME_LIST, ID_TO_DATA_DICT
from ScalableView import ScalableView

# Load the .ui file using the uic module
ui_file = os.path.split(__file__)[0] + "/ui/AdvancedFilterSearch.ui"
form_class, base_class = uic.loadUiType(ui_file)

def intersection(item_list_1: List[Any], item_list_2: List[Any]) -> List[Any]:
    ''' Calculates the intersection of two lists.

    Args:
        item_list_1 (List[Any]): The first list.
        item_list_2 (List[Any]): The second list.

    Returns:
        List[Any] : The items that exist in both lists.
    '''
    # Return the items that exist in both lists
    return [item for item in item_list_1 if item in item_list_2]

# NOTE: test
class ColorScaleItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ColorScaleItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        # Get the data for the item
        value = index.data(QtCore.Qt.UserRole)

        # NOTE: test
        # Set the background color based on the item's value
        if int(value) > 29:
            background_color = QtGui.QColor(255, 0, 0)
        else:
            background_color = QtGui.QColor(0, 255, 0)
        # Draw the background
        painter.fillRect(option.rect, background_color)

        # Draw the text
        painter.drawText(option.rect, QtCore.Qt.AlignCenter, str(value))

    # def sizeHint(self, option, index):
    #     return QtCore.QSize(50, 50)

class HighlightItemDelegate(QtWidgets.QStyledItemDelegate):
    ''' Custom item delegate class that highlights the rows specified by the `target_model_indexes` list.
    '''
    # List of tuple of target model index for highlighting
    target_model_indexes: List[QtCore.QModelIndex] = list()
    
    def __init__(self, parent=None, color: QtGui.QColor = QtGui.QColor(165, 165, 144, 128)):
        ''' Initialize the highlight item delegate.
        
        Args:
            parent (QtWidgets.QWidget, optional): The parent widget. Defaults to None.
            color (QtGui.QColor, optional): The color to use for highlighting. Defaults to a light grayish-yellow.
        '''
        # Initialize the super class
        super(HighlightItemDelegate, self).__init__(parent)

        # Set the color attribute
        self.color = color
    
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, model_index: QtCore.QModelIndex):
        ''' Paint the delegate.
        
        Args:
            painter (QtGui.QPainter): The painter to use for drawing.
            option (QtWidgets.QStyleOptionViewItem): The style option to use for drawing.
            model_index (QtCore.QModelIndex): The model index of the item to be painted.
        '''
        # Check if the current model index is not in the target list
        if model_index not in self.target_model_indexes:
            # If not, paint the item normally using the parent implementation
            super().paint(painter, option, model_index)
            return

        # If the current model index is in the target list, set the background color and style
        option.backgroundBrush.setColor(self.color)
        option.backgroundBrush.setStyle(QtCore.Qt.SolidPattern)

        # Fill the rect with the background brush
        painter.fillRect(option.rect, option.backgroundBrush)

        # Paint the item normally using the parent implementation
        super().paint(painter, option, model_index)

class AdvancedFilterSearch(base_class, form_class):
    ''' A PyQt5 widget that allows the user to apply advanced filters to a tree widget.

    Attributes:
        tree_widget (QtWidgets.QTreeWidget): The tree widget to be filtered.
        column_names (List[str]): The list of column names for the tree widget.
        filter_criteria_list (List[str]): The list of filter criteria applied to the tree widget.
    '''
    # Set up type hints for the widgets as used in the .ui file.
    column_combo_box: QtWidgets.QComboBox
    condition_combo_box: QtWidgets.QComboBox
    keyword_line_edit: QtWidgets.QLineEdit
    add_filter_button: QtWidgets.QPushButton
    show_filter_button: QtWidgets.QPushButton
    filter_tree_widget: QtWidgets.QTreeWidget
    
    # Define a dictionary of match flags for each condition
    CONDITION_TO_MATCH_FLAG_DICT = {
        'contains': QtCore.Qt.MatchFlag.MatchContains,
        'starts_with': QtCore.Qt.MatchFlag.MatchStartsWith,
        'ends_with': QtCore.Qt.MatchFlag.MatchEndsWith,
        'exact_match': QtCore.Qt.MatchFlag.MatchExactly,
        'wild_card': QtCore.Qt.MatchFlag.MatchWildcard,
        'reg_exp': QtCore.Qt.MatchFlag.MatchRegExp,
    }

    # Define a signal that will be emitted when the filter count changes
    filter_count_changed = QtCore.pyqtSignal(int)

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
        # Get reference to the current application instance
        app = QtWidgets.QApplication.instance()
        # Get the palette of the application
        palette = app.palette()
        # Get the color of the text from the palette
        icon_color = palette.color(QtGui.QPalette.Text)

        # Initialize an empty list to store the filter criteria
        self.filter_criteria_list = list()

        # Initialize the QIcon objects for use in the UI with specified color and opacity
        self.tabler_action_qicon = TablerQIcon(color=icon_color, opacity=0.6)
        self.tabler_action_checked_qicon = TablerQIcon(color=icon_color)
        self.tabler_button_qicon = TablerQIcon(color=icon_color)

        # Initialize the HighlightItemDelegate object to highlight items in the tree widget.
        self.hightlight_item_delegate = HighlightItemDelegate()

    def _setup_ui(self):
        ''' Set up the UI for the widget, including creating widgets and layouts.
        '''
        # Set up the UI for the widget
        self.setupUi(self)

        # Get a reference to the header item
        header_item = self.tree_widget.headerItem()

        # Get the list of column names
        self.column_names = [header_item.text(column_index) for column_index in range(header_item.columnCount())]

        # Set up combo boxes
        self.column_combo_box.addItems(self.column_names)
        self.condition_combo_box.addItems(self.CONDITION_TO_MATCH_FLAG_DICT.keys())

        # Set up the filter tree widget
        self.setup_filter_tree_widget()
        
        # Add action to keyword line edit
        self.add_action_on_keyword_line_edit()
        
        # Set the icon for the add filter button
        self.add_filter_button.setIcon(self.tabler_button_qicon.filter_add)
        self.show_filter_button.setIcon(self.tabler_button_qicon.box_multiple)

        # Set the visibility of the filter tree widget based on the checked state of the show filter button
        self.filter_tree_widget.setVisible(self.show_filter_button.isChecked())

    def _setup_signal_connections(self):
        ''' Set up signal connections between widgets and slots.
        '''
        # Connect signals to slots
        self.add_filter_button.clicked.connect(self.add_filter)
        self.keyword_line_edit.returnPressed.connect(self.add_filter)

        # Connect match actions to slots
        self.match_case_action.triggered.connect(self.update_case_sensitive)
        self.negate_action.triggered.connect(self.update_negate)

        # Connect match options to slots
        self.keyword_line_edit.textChanged.connect(self.hightlight_search)
        self.column_combo_box.activated.connect(self.hightlight_search)
        self.condition_combo_box.activated.connect(self.hightlight_search)
        self.match_case_action.triggered.connect(self.hightlight_search)
        self.negate_action.triggered.connect(self.hightlight_search)

        # Connect grouping signals to slots
        self.tree_widget.grouped_by_column.connect(self.hightlight_search)
        self.tree_widget.grouped_by_column.connect(self.apply_filters)
        self.tree_widget.ungrouped_all.connect(self.hightlight_search)
        self.tree_widget.ungrouped_all.connect(self.apply_filters)

        # Connect filter count changed signals to slots
        self.filter_count_changed.connect(self.update_show_filter_button)
        self.filter_count_changed.connect(self.apply_filters)

    def setup_filter_tree_widget(self):
        ''' Set up the filter tree widget, including header columns and adding a clear button to the header.

        The labels are:
            "Column"    : The name of the column used for filtering.
            "Condition" : The condition for filtering (e.g. "Contains", "Starts with", etc.).
            "Keyword"   : The keyword used for filtering.
            "Negate"    : A flag indicating whether to negate the filter condition (i.e. filter out items that match the condition).
            "Aa"        : A button to set the case sensitivity of the filter condition.
            ""          : An empty string, used as a placeholder.
        '''
        # List of header labels for the filter tree widget
        header_labels = ['Column', 'Condition', 'Keyword', 'Negate', 'Aa','']

        # Set up filter tree widget header columns
        self.filter_tree_widget.setHeaderLabels(header_labels)

        # Get the header of the filter tree widget
        header = self.filter_tree_widget.header()

        # Resize header sections, with the first three (Column, Condition, Keyword) stretched and the rest fixed
        for column_index, _ in enumerate(header_labels):
            stretch = column_index in (0, 1, 2) # stretch the first three columns (Column, Condition, Keyword)
            header.setSectionResizeMode(column_index, QtWidgets.QHeaderView.Stretch if stretch else QtWidgets.QHeaderView.Fixed)

        # Add clear button on header
        self.add_clear_button_on_header()

    def add_action_on_keyword_line_edit(self):
        ''' Add two actions to the keyword line edit widget: match case and negate match.
        '''
        # Add the match case action to the keyword line edit widget
        self.match_case_action = self.keyword_line_edit.addAction(self.tabler_action_qicon.letter_case, QtWidgets.QLineEdit.TrailingPosition)
        # Set the tool tip to "Match Case"
        self.match_case_action.setToolTip('Match Case')
        # Set the action to be checkable
        self.match_case_action.setCheckable(True)

        # Add the negate match action to the keyword line edit widget
        self.negate_action = self.keyword_line_edit.addAction(self.tabler_action_qicon.a_b_off, QtWidgets.QLineEdit.TrailingPosition)
        # Set the tool tip to "Negate Match"
        self.negate_action.setToolTip('Negate Match')
        # Set the action to be checkable
        self.negate_action.setCheckable(True)

    def add_clear_button_on_header(self):
        ''' Add a clear filters button to the header of the filter tree widget.
        '''
        # Add a clear filters button to the header
        header = self.filter_tree_widget.header()
        viewport = header.viewport()

        # Create a horizontal layout for the viewport
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)

        # Set the layout for the viewport
        viewport.setLayout(layout)

        # Add a horizontal spacer to the layout
        horizontal_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        layout.addItem(horizontal_spacer)

        # Create a clear buttons
        clear_button = QtWidgets.QPushButton(self.tabler_button_qicon.clear_all, '', self)
        clear_button.setToolTip('Clear all filters')
        clear_button.clicked.connect(self.clear_filters)
        clear_button.setFixedSize(27, 16777215)

        # Add a clear button to the layout
        layout.addWidget(clear_button)

    def hightlight_items(self, tree_items: List[QtWidgets.QTreeWidgetItem]):
        ''' Highlight the specified `tree_items` in the tree widget.
        '''
        # Reset the previous target model indexes
        self.hightlight_item_delegate.target_model_indexes = list()

        # Loop through the specified tree items
        for tree_item in tree_items:

            # Get the item index in the tree widget
            item_index = self.tree_widget.indexFromItem(tree_item).row()

            # Add the model indexes of the current tree item to the target properties
            self.hightlight_item_delegate.target_model_indexes += self.get_model_indexes(tree_item)

            # Set the item delegate for the current row to the highlight item delegate
            self.tree_widget.setItemDelegateForRow(item_index, self.hightlight_item_delegate)

    def get_model_indexes(self, tree_item: QtWidgets.QTreeWidgetItem) -> List[QtCore.QModelIndex]:
        ''' Get the properties of the model index for each column in the tree widget.

        Parameters:
            tree_item (QtWidgets.QTreeWidgetItem): The tree item to extract the model index properties from.

        Returns:
            List[QtCore.QModelIndex]: A list of model index for each column in the tree widget.
        '''
        # Get a list of the shown column indices
        shown_column_index_list = self.get_shown_column_index_list()

        # Create a list to store the model index
        model_indexes = list()

        # Loop through each shown column index
        for column_index in shown_column_index_list:
            # Get the model index for the current column
            model_index = self.tree_widget.indexFromItem(tree_item, column_index)

            # Add the model index to the list
            model_indexes.append(model_index)

        # Return the list of model index properties
        return model_indexes

    def get_shown_column_index_list(self) -> List[int]:
        ''' Returns a list of indices for the columns that are shown (i.e., not hidden) in the tree widget.

        Returns:
            List[int]: A list of integers, where each integer is the index of a shown column in the tree widget.
        '''
        # Get the header of the tree widget
        header = self.tree_widget.header()

        # Generate a list of the indices of the columns that are not hidden
        column_index_list = [column_index for column_index in range(header.count()) if not header.isSectionHidden(column_index)]

        # Return the list of the index of a shown column in the tree widget.
        return column_index_list
        
    def reset_highlight_all_items(self):
        ''' Reset the highlight of all items in the tree widget.

            This method resets the highlighting of all items in the tree widget by setting the delegate for each row to `None`.
            The target model index properties stored in `self.hightlight_item_delegate` will also be reset to an empty list.
        '''
        # Reset the target model index properties
        self.hightlight_item_delegate.target_model_indexes = list()

        # Get all items in the tree widget
        all_items = self.get_all_items()

        # Loop through all items
        for tree_item in all_items:
            # Get the row index of the item
            item_index = self.tree_widget.indexFromItem(tree_item).row()
            # Set the delegate for the row to None
            self.tree_widget.setItemDelegateForRow(item_index, None)

    def get_all_items(self):
        ''' This function returns all the items in the tree widget as a list.
        '''
        # Get the root item of the tree widget
        root = self.tree_widget.invisibleRootItem()

        # Create a list to store the items and a queue to store items to be processed
        items = [root]
        queue = [root]

        # Iterate through all items in the queue
        while queue:
            # Get the next item in the queue
            item = queue.pop(0)

            # Loop through all children of the current item
            for child_index in range(item.childCount()):
                # Get the child item
                child = item.child(child_index)

                # Add the child item to the items list and the queue
                items.append(child)
                queue.append(child)

        # Return the list of items
        return items

    def get_all_items_at_child_level(self, child_level: int = 0) -> List[QtWidgets.QTreeWidgetItem]:
        ''' Retrieve all items at a specific child level in the tree widget.

        Args:
            child_level (int): The child level to retrieve items from. Defaults to 0 (top-level items).

        Returns:
            List[QtWidgets.QTreeWidgetItem]: List of `QTreeWidgetItem` objects at the specified child level.
        '''
        # If child level is 0, return top-level items
        if not child_level:
            # return top-level items
            return [self.tree_widget.topLevelItem(row) for row in range(self.tree_widget.topLevelItemCount())]

        # Get all items in the tree widget
        all_items = self.get_all_items()

        # Filter items to only those at the specified child level
        return [item for item in all_items if self.get_child_level(item) == child_level]
    
    def hightlight_search(self):
        ''' Highlight the items in the tree widget that match the search criteria.
        '''
        # Reset the highlight for all items
        self.reset_highlight_all_items()

        # Get the selected column, condition, and keyword
        column = self.column_combo_box.currentText()
        condition = self.condition_combo_box.currentText()
        keyword = self.keyword_line_edit.text()
        is_negate = self.negate_action.isChecked()
        is_case_sensitive = self.match_case_action.isChecked()

        # Return if the keyword is empty
        if not keyword:
            return
        
        # Find the items that match the search criteria
        match_items = self.find_match_items(column, condition, keyword, is_negate, is_case_sensitive)

        # Highlight the matched items
        self.hightlight_items(match_items)

    def find_match_items(self, column, condition, keyword, is_negate, is_case_sensitive) -> List[QtWidgets.QTreeWidgetItem]:
        ''' Find the items that match the given criteria.

        Args:
            column (str): The name of the column to search in.
            condition (str): The type of match condition. Can be one of the following:
                'contains'      : Items containing the keyword will be returned.
                'starts_with'   : Items starting with the keyword will be returned.
                'ends_with'     : Items ending with the keyword will be returned.
                'exact_match'   : Only items exactly matching the keyword will be returned.
                'wild_card'     : Items matching the keyword using wildcard pattern matching will be returned.
                'reg_exp'       : Items matching the keyword using regular expression pattern matching will be returned.
            keyword (str): The string to search for.
            is_negate (bool): If set to True, the returned items will be the ones that do not match the criteria.
            is_case_sensitive (bool): If set to True, the match will be case sensitive.

        Returns:
            list[QtWidgets.QTreeWidgetItem]: The list of items that match the criteria.
        '''
        # Get the match flag based on the given condition
        flags = self.CONDITION_TO_MATCH_FLAG_DICT[condition]

        # Get the name of the grouped column
        grouped_column_name = self.tree_widget.grouped_column_name

        # Determine the column index and child level to search in based on the given column and grouped column
        column_index = 0 if grouped_column_name and column == grouped_column_name else self.column_names.index(column)
        child_level = 1 if grouped_column_name and column != grouped_column_name else 0

        # Set the match flag for search recursively if the tree widget is grouped by column and the column is not the grouped column
        if grouped_column_name and column != grouped_column_name:
            flags |= QtCore.Qt.MatchFlag.MatchRecursive

        # Add the case sensitivity flag if neededs
        if is_case_sensitive:
            flags |= QtCore.Qt.MatchFlag.MatchCaseSensitive

        # Get all items at the specified child level
        all_items_at_child_level = self.get_all_items_at_child_level(child_level)

        # Find all items matching the given keyword in the specified column and child level
        match_items = self.tree_widget.findItems(keyword, flags, column_index)
        match_items_at_child_level = intersection(all_items_at_child_level, match_items)

        # Negate the match results if is_negate is set to True
        if is_negate:
            match_items_at_child_level = [item for item in all_items_at_child_level if item not in match_items_at_child_level]
        
        # Return the list of items that match the criteria.
        return match_items_at_child_level

    def update_case_sensitive(self, state: bool):
        ''' Update the is_case_sensitive member variable when the match case action state changes.
            Args:
                state (bool): The state of match case action.
        '''
        # Update the tabler_qicon based on the state of the match case action
        tabler_qicon = self.tabler_action_checked_qicon if state else self.tabler_action_qicon
        self.match_case_action.setIcon(tabler_qicon.letter_case)

    def update_negate(self, state: bool):
        ''' Update the is_negate member variable when the negate action state changes.
            Args:
                state (bool): The state of negate action.
        '''
        # Update the tabler_qicon based on the state of the negate action
        tabler_qicon = self.tabler_action_checked_qicon if state else self.tabler_action_qicon
        self.negate_action.setIcon(tabler_qicon.a_b_off)

    @staticmethod
    def get_child_level(item: QtWidgets.QTreeWidgetItem) -> int:
        ''' Get the child level of a given QTreeWidgetItem

        Args:
            item (QtWidgets.QTreeWidgetItem): The QTreeWidgetItem to get the child level of

        Returns:
            int: The child level of the given QTreeWidgetItem
        '''
        # Initialize child level
        child_level = 0

        # Iterate through the parent items to determine the child level
        while item.parent():
            # Increment child level for each parent
            child_level += 1
            # Update item to be its parent
            item = item.parent()

        # Return the final child level
        return child_level
    
    def add_filter(self):
        ''' Add a filter to the tree widget. Called when the "Add Filter" button is clicked 
            or when the Enter key is pressed in the keyword_line_edit widget.
        '''
        # Get the selected column, condition, and keyword
        column = self.column_combo_box.currentText()
        condition = self.condition_combo_box.currentText()
        keyword = self.keyword_line_edit.text()
        is_negate = self.negate_action.isChecked()
        is_case_sensitive = self.match_case_action.isChecked()

        # Return if the keyword is empty
        if not keyword:
            return

        # Clear the keyword_line_edit widget
        self.keyword_line_edit.clear()

        # Store the filter criteria in a list
        filter_criteria = [column, condition, keyword, is_negate, is_case_sensitive]

        # Return if the filter criteria (column, is_negate, condition, keyword, is_case_sensitive) is already in the filter criteria list
        if filter_criteria in self.filter_criteria_list:
            return

        # Add the filter criteria to the list
        self.filter_criteria_list.append(filter_criteria)

        # Create a new tree widget item with the column, condition, and keyword
        filter_tree_item = QtWidgets.QTreeWidgetItem(self.filter_tree_widget, map(str, filter_criteria))
        # Store the filter criteria in a data_list attribute of the tree widget item
        filter_tree_item.data_list = filter_criteria

        # Add the "Negate", "Match Case" and "Remove" buttons to the tree widget item
        self.add_negate_button(filter_tree_item, check_state=is_negate)
        self.add_match_case_button(filter_tree_item, check_state=is_case_sensitive)
        self.add_remove_item_button(filter_tree_item)

        # Emit signal indicating the number of filter criteria has changed
        self.filter_count_changed.emit(len(self.filter_criteria_list))

    def add_negate_button(self, tree_item: QtWidgets.QTreeWidgetItem, check_state: bool = False):
        ''' Add a negate button to the specified tree widget item.
    
        Args:
            tree_item (QtWidgets.QTreeWidgetItem): The tree widget item to add the negate button to.
            check_state (bool, optional): The initial check state of the button. Defaults to False.
        '''
        # Create a negate button
        negate_button = QtWidgets.QPushButton(self.tabler_action_qicon.a_b_off, '', self.filter_tree_widget)

        # Set the button as checkable and its initial check state
        negate_button.setCheckable(True)
        negate_button.setChecked(check_state)
        # Disable the button so it cannot be interacted with
        negate_button.setDisabled(True)

        # Add the negate button to the specified tree item in the filter tree widget
        self.filter_tree_widget.setItemWidget(tree_item, 3, negate_button)

    def add_match_case_button(self, tree_item: QtWidgets.QTreeWidgetItem, check_state: bool = False):
        ''' Add a match case button to the specified tree widget item.
    
        Args:
            tree_item (QtWidgets.QTreeWidgetItem): The tree widget item to add the match case button to.
            check_state (bool, optional): The initial check state of the button. Defaults to False.
        '''
        # Create a match case button
        match_case_button = QtWidgets.QPushButton(self.tabler_action_qicon.letter_case, '', self.filter_tree_widget)

        # Set the button as checkable and its initial check state
        match_case_button.setCheckable(True)
        match_case_button.setChecked(check_state)
        # Disable the button so it cannot be interacted with
        match_case_button.setDisabled(True)

        # Add the match case button to the specified tree item in the filter tree widget
        self.filter_tree_widget.setItemWidget(tree_item, 4, match_case_button)
        
    def add_remove_item_button(self, tree_item: QtWidgets.QTreeWidgetItem):
        ''' Add a remove button to the given tree item.

        Args:
            tree_item (QtWidgets.QTreeWidgetItem): The tree item to add the button to.
        '''
        # Create a push button for removing the filter item
        remove_button = QtWidgets.QPushButton(self.tabler_button_qicon.trash, '', self)
        
        # Set the tool tip for the remove button
        remove_button.setToolTip('Remove this filter item')
        
        # Connect the remove button to the remove_filter function
        remove_button.clicked.connect(lambda: self.remove_filter(tree_item))
        
        # Add the remove button as a widget to the specified column (5th column) of the filter tree widget
        self.filter_tree_widget.setItemWidget(tree_item, 5, remove_button)

    def apply_filters(self):
        ''' Apply the filters specified by the user to the tree widget.
        '''
        # Get a list of all items in the tree widget
        all_items = self.get_all_items()

        # Hide all items
        for item in all_items:
            item.setHidden(True)

        # Initial the intersection items list as all items
        intersect_match_items = all_items

        # Iterate through each filter criteria in the list, then intersect the match items for each filter criteria
        for column, condition, keyword, is_negate, is_case_sensitive in self.filter_criteria_list:
            # Get the items that match the filter criteria
            match_items = self.find_match_items(column, condition, keyword, is_negate, is_case_sensitive)

            # Update the intersected match items list
            intersect_match_items = intersection(match_items, intersect_match_items)

        # Show the items that match all filter criteria and their parent and children
        self.show_matching_items(intersect_match_items)
        
    def update_show_filter_button(self, filter_count: int = 0):
        ''' Updates the text of the show filter button to reflect the number of active filters.

        Args:
            filter_count (int): The number of active filters. Defaults to 0.
        '''
        # Convert the filter count to a string, or an empty string if it's zero
        filter_count = str(filter_count) if filter_count else str()
        # Set the text of the show filter button to the filter count
        self.show_filter_button.setText(filter_count)

    def show_matching_items(self, match_items: List[QtWidgets.QTreeWidgetItem]):
        ''' Show the items and their parent and children.
        '''
        # Show the items that match all filter criteria
        for item in match_items:
            item.setHidden(False)

            # Show the parent of the item if it exists
            if item.parent():
                item.parent().setHidden(False)

            # Show all children of the item
            for index in range(item.childCount()):
                item.child(index).setHidden(False)

    def remove_filter(self, filter_tree_item: QtWidgets.QTreeWidgetItem):
        ''' Slot for the "Remove Filter" button.
        '''
        # Remove the selected filter criteria from the list
        self.filter_criteria_list.remove(filter_tree_item.data_list)
        # Remove the selected item at index 0
        item = self.filter_tree_widget.takeTopLevelItem(self.filter_tree_widget.indexOfTopLevelItem(filter_tree_item))
        # Delete the item object. This will remove the item from memory and break any references to it.
        del item

        # Emit signal indicating the number of filter criteria has changed
        self.filter_count_changed.emit(len(self.filter_criteria_list))

    def clear_filters(self):
        ''' Slot for the "Clear Filters" button.
        '''
        # Clear the list of filter criteria
        self.filter_criteria_list.clear()
        # Clear the tree widget
        self.filter_tree_widget.clear()

        # Emit signal indicating the number of filter criteria has changed (now 0)
        self.filter_count_changed.emit(len(self.filter_criteria_list))

    def set_column_filter(self, column_name: str):
        self.column_combo_box.setCurrentText(column_name)

def main():
    ''' Create the application and main window, and show the widget.
    '''
    # Create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    # Set theme of QApplication to the dark theme
    set_theme(app, 'dark')

    # Create the tree widget with example data
    tree_widget = GroupableTreeWidget(column_name_list=COLUMN_NAME_LIST, id_to_data_dict=ID_TO_DATA_DICT)

    # Create an instance of the widget and set it as the central widget
    widget = AdvancedFilterSearch(tree_widget)
    widget.set_column_filter('Name')
    window.setCentralWidget(widget)
    
    # Create the scalable view and set the tree widget as its central widget
    scalable_tree_widget_view = ScalableView(widget=tree_widget)

    # Add the tree widget to the layout of the widget
    widget.layout().addWidget(scalable_tree_widget_view)

    # Show the window
    window.show()

    # Run the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
