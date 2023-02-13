import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from typing import Any, List, Tuple

from theme.theme import setTheme

from TablerQIcon import TablerQIcon

from GroupableTreeWidget import GroupableTreeWidget, COLUMN_NAME_LIST, ID_TO_DATA_DICT

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


def extract_model_index_prop_tuple(model_index: QtCore.QModelIndex) -> Tuple[int, int, QtCore.QModelIndex, QtCore.QAbstractItemModel]:
    '''
    Extracts the properties of a QModelIndex and returns a tuple of the row, column, parent, and model.

    Args:
        model_index (QtCore.QModelIndex): The QModelIndex to extract the properties from.

    Returns:
        Tuple : A tuple containing the row, column, parent, and model of the QModelIndex.
    '''
    # Return the row, column, parent, and model of the QModelIndex
    return (model_index.row(), model_index.column(), model_index.parent(), model_index.model())

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
    ''' Custom item delegate class that highlights the rows specified by the `target_model_index_props` list.
    '''
    # List of tuple of target model index properties (row, column, parent, model) for highlighting
    target_model_index_props: List[Tuple[int, int, QtCore.QModelIndex, QtCore.QAbstractItemModel]] = list()
    
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
    
    def paint(self, painter, option, model_index):
        ''' Paint the delegate.
        
        Args:
            painter (QtGui.QPainter): The painter to use for drawing.
            option (QtWidgets.QStyleOptionViewItem): The style option to use for drawing.
            model_index (QtCore.QModelIndex): The model index of the item to be painted.
        '''
        # Get the properties of the model index
        model_index_prop_tuple = extract_model_index_prop_tuple(model_index)

        # Check if the current model index is not in the target list
        if model_index_prop_tuple not in self.target_model_index_props:
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
        headerItem = self.tree_widget.headerItem()

        # Get the list of column names
        self.column_names = [headerItem.text(column_index) for column_index in range(headerItem.columnCount())]

        # Set up combo boxes
        self.column_combo_box.addItems(self.column_names)
        self.condition_combo_box.addItems(self.CONDITION_TO_MATCH_FLAG_DICT.keys())

        # Set up the filter tree widget
        self.setup_filter_tree_widget()
        
        # Add action to keyword line edit
        self.add_action_on_keyword_line_edit()
        
        # Set the icon for the add filter button
        self.add_filter_button.setIcon(self.tabler_button_qicon.filter_add)

    def _setup_signal_connections(self):
        ''' Set up signal connections between widgets and slots.
        '''
        # Connect signals to slots
        self.add_filter_button.clicked.connect(self.add_filter)
        self.keyword_line_edit.returnPressed.connect(self.add_filter)

        # 
        self.matchCaseAction.triggered.connect(self.update_case_sensitive)
        self.negateAction.triggered.connect(self.update_negate)

        # 
        self.keyword_line_edit.textChanged.connect(self.hightlight_search)
        self.column_combo_box.activated.connect(self.hightlight_search)
        self.condition_combo_box.activated.connect(self.hightlight_search)
        self.matchCaseAction.triggered.connect(self.hightlight_search)
        self.negateAction.triggered.connect(self.hightlight_search)

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

        # Resize header sections, with the first three (Column, Condition, Keyword) stretched and the rest fixed
        header = self.filter_tree_widget.header()
        for column_index, _ in enumerate(header_labels):
            stretch = column_index in (0, 1, 2) # stretch the first three columns (Column, Condition, Keyword)
            header.setSectionResizeMode(column_index, QtWidgets.QHeaderView.Stretch if stretch else QtWidgets.QHeaderView.Fixed)

        # Add clear button on header
        self.add_clear_button_on_header()

    def hightlight_items(self, tree_items: List[QtWidgets.QTreeWidgetItem]):
        self.hightlight_item_delegate.target_model_index_props = list()
        for tree_item in tree_items:
            item_index = self.tree_widget.indexFromItem(tree_item).row()
            self.hightlight_item_delegate.target_model_index_props += self.get_model_index_props(tree_item)
            self.tree_widget.setItemDelegateForRow(item_index, self.hightlight_item_delegate)

    def get_model_index_props(self, tree_item: QtWidgets.QTreeWidgetItem) -> List[Tuple[int, int, QtCore.QModelIndex, QtCore.QAbstractItemModel]]:
        shown_column_index_list = self.get_shown_column_index_list()

        model_index_prop_tuple_list = list()

        for column_index in shown_column_index_list:
            model_index = self.tree_widget.indexFromItem(tree_item, column_index)
            model_index_prop_tuple_list.append(extract_model_index_prop_tuple(model_index))

        return model_index_prop_tuple_list

    def get_shown_column_index_list(self) -> List[int]:
        header = self.tree_widget.header()
        column_count = header.count()
        column_index_list = [column_index for column_index in range(column_count) if not header.isSectionHidden(column_index)]
        return  column_index_list
        
    def reset_highlight_all_items(self):
        self.hightlight_item_delegate.target_model_index_props = list()
        all_items = self.get_all_items()
        for tree_item in all_items:
            item_index = self.tree_widget.indexFromItem(tree_item).row()
            self.tree_widget.setItemDelegateForRow(item_index, None)

    def get_all_items(self):
        root = self.tree_widget.invisibleRootItem()
        items = [root]
        queue = [root]
        while queue:
            item = queue.pop(0)
            for i in range(item.childCount()):
                child = item.child(i)
                items.append(child)
                queue.append(child)
        return items
    
    def get_all_items_at_child_level(self, child_level: int = 0):
        if not child_level:
            return [self.tree_widget.topLevelItem(row) for row in range(self.tree_widget.topLevelItemCount())]

        all_items = self.get_all_items()
        return [item for item in all_items if self.get_child_level(item) == child_level]
    
    def hightlight_search(self):

        # NOTE: Should be fix to call this again when grouping by column

        self.reset_highlight_all_items()

        # Get the selected column, condition, and keyword
        column = self.column_combo_box.currentText()
        condition = self.condition_combo_box.currentText()
        keyword = self.keyword_line_edit.text()
        is_negate = self.negateAction.isChecked()
        is_case_sensitive = self.matchCaseAction.isChecked()

        if not keyword:
            return
        
        match_items = self.find_match_items(column, condition, keyword, is_negate, is_case_sensitive)

        self.hightlight_items(match_items)

    def find_match_items(self, column, condition, keyword, is_negate, is_case_sensitive) -> List[QtWidgets.QTreeWidgetItem]:

        flags = self.CONDITION_TO_MATCH_FLAG_DICT[condition]

        if not self.tree_widget.grouped_column_name:
            column_index = self.column_names.index(column)
            child_level = 0
        elif column == self.tree_widget.grouped_column_name:
            column_index = 0
            child_level = 0
        else:
            column_index = self.column_names.index(column)
            child_level = 1
            flags |= QtCore.Qt.MatchFlag.MatchRecursive

        if is_case_sensitive:
            flags |= QtCore.Qt.MatchFlag.MatchCaseSensitive

        all_items_at_child_level = self.get_all_items_at_child_level(child_level)

        match_items = self.tree_widget.findItems(keyword, flags, column_index)
        match_items_at_child_level = intersection(all_items_at_child_level, match_items)

        if is_negate:
            match_items_at_child_level = [item for item in all_items_at_child_level if item not in match_items_at_child_level]

        return match_items_at_child_level
    
    def add_action_on_keyword_line_edit(self):
        self.matchCaseAction = self.keyword_line_edit.addAction(self.tabler_action_qicon.letter_case, QtWidgets.QLineEdit.TrailingPosition)
        self.matchCaseAction.setToolTip('Match Case')
        self.matchCaseAction.setCheckable(True)

        self.negateAction = self.keyword_line_edit.addAction(self.tabler_action_qicon.a_b_off, QtWidgets.QLineEdit.TrailingPosition)
        self.negateAction.setToolTip('Negate Match')
        self.negateAction.setCheckable(True)

    def add_clear_button_on_header(self):
        # Add a clear filters button to the header
        header = self.filter_tree_widget.header()
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
        tabler_qicon = self.tabler_action_checked_qicon if state else self.tabler_action_qicon
        self.matchCaseAction.setIcon( tabler_qicon.letter_case )

    def update_negate(self, state: bool):
        ''' Update the is_negate member variable when the negate action state changes.
            Args:
                state (bool): The state of negate action.
        '''
        tabler_qicon = self.tabler_action_checked_qicon if state else self.tabler_action_qicon
        self.negateAction.setIcon( tabler_qicon.a_b_off )

    @staticmethod
    def get_child_level(item: QtWidgets.QTreeWidgetItem):
        child_level = 0
        while item.parent():
            child_level += 1
            item = item.parent()
        return child_level
    
    def add_filter(self):
        ''' Add a filter to the tree widget. Called when the "Add Filter" button is clicked 
            or when the Enter key is pressed in the keyword_line_edit widget.
        '''
        # Get the selected column, condition, and keyword
        column = self.column_combo_box.currentText()
        condition = self.condition_combo_box.currentText()
        keyword = self.keyword_line_edit.text()
        is_negate = self.negateAction.isChecked()
        is_case_sensitive = self.matchCaseAction.isChecked()

        # Return if the keyword is empty
        if not keyword:
            return

        # Clear the keyword_line_edit widget
        self.keyword_line_edit.clear()

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

        negate_button = QtWidgets.QPushButton(self.tabler_action_qicon.a_b_off, '', self.filter_tree_widget)
        negate_button.setCheckable(True)
        negate_button.setChecked(is_negate)
        negate_button.setDisabled(True)

        match_case_button = QtWidgets.QPushButton(self.tabler_action_qicon.letter_case, '', self.filter_tree_widget)
        match_case_button.setCheckable(True)
        match_case_button.setChecked(is_case_sensitive)
        match_case_button.setDisabled(True)

        # self.filter_tree_widget.setIte
        self.filter_tree_widget.setItemWidget(filter_tree_item, 3, negate_button)
        self.filter_tree_widget.setItemWidget(filter_tree_item, 4, match_case_button)

        self.add_remove_item_button(filter_tree_item)

        self.apply_filters()

    def add_remove_item_button(self, tree_item):
        remove_button = QtWidgets.QPushButton(self.tabler_button_qicon.trash, '', self)
        remove_button.setToolTip('Remove this filter item')
        remove_button.clicked.connect(lambda: self.remove_filter(tree_item))
        self.filter_tree_widget.setItemWidget(tree_item, 5, remove_button)

    def apply_filters(self):
        ''' Slot for the "Apply Filters" button.
        '''

        # NOTE: Should be fix to call this again when grouping by column
        
        all_items = self.get_all_items()

        for item in all_items:
            item.setHidden(True)

        intersect_match_items = all_items

        # Check if the item matches all of the filter criteria
        for column, condition, keyword, is_negate, is_case_sensitive in self.filter_criteria_list:

            match_items = self.find_match_items(column, condition, keyword, is_negate, is_case_sensitive)

            intersect_match_items = intersection(match_items, intersect_match_items)

        for item in intersect_match_items:
            # Set the visibility of the item based on whether it matches the criteria
            item.setHidden(False)

            if item.parent():
                item.parent().setHidden(False)

            for index in range(item.childCount()):
                item.child(index).setHidden(False)

    def remove_filter(self, filter_tree_item):
        ''' Slot for the "Remove Filter" button.
        '''
        # Remove the selected filter criteria from the list
        self.filter_criteria_list.remove(filter_tree_item.data_list)
        # Remove the selected item at index 0
        item = self.filter_tree_widget.takeTopLevelItem(self.filter_tree_widget.indexOfTopLevelItem(filter_tree_item))
        # Delete the item object. This will remove the item from memory and break any references to it.
        del item

        self.apply_filters()

    def clear_filters(self):
        ''' Slot for the "Clear Filters" button.
        '''
        # Clear the list of filter criteria
        self.filter_criteria_list.clear()
        # Clear the tree widget
        self.filter_tree_widget.clear()

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
    widget.column_combo_box.setCurrentText('Name')
    window.setCentralWidget(widget)

    # Add the tree widget to the layout of the widget
    widget.layout().addWidget(tree_widget)

    # Show the window and run the application
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
