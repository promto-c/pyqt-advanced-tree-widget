import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from typing import List

from theme.theme import setTheme

from TablerQIcon import TablerQIcon

from GroupableTreeWidget import GroupableTreeWidget, COLUMN_NAME_LIST, ID_TO_DATA_DICT

# Load the .ui file using the uic module
ui_file = "ui/AdvancedFilterSearch.ui"
form_class, base_class = uic.loadUiType(ui_file)

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
    def paint(self, painter, option, index):
        option.backgroundBrush.setColor(QtGui.QColor(165, 165, 144, 128))
        option.backgroundBrush.setStyle(QtCore.Qt.SolidPattern)
        painter.fillRect(option.rect, option.backgroundBrush)

        super().paint(painter, option, index)

class AdvancedFilterSearch(base_class, form_class):
    ''' A PyQt5 widget that allows the user to apply advanced filters to a tree widget.

    Attributes:
        tree_widget (QtWidgets.QTreeWidget): The tree widget to be filtered.
        column_names (List[str]): The list of column names for the tree widget.
        filter_criteria_list (List[str]): The list of filter criteria applied to the tree widget.
    '''
    # Set up type hints for the widgets as use in the .ui file.
    column_combo_box: QtWidgets.QComboBox
    condition_combo_box: QtWidgets.QComboBox
    keyword_line_edit: QtWidgets.QLineEdit
    add_filter_button: QtWidgets.QPushButton
    filter_tree_widget: QtWidgets.QTreeWidget
    
    # Define a dictionary of match flags for each condition
    CONDITION_TO_MATCH_FLAG_DICT = {
        'contains': QtCore.Qt.MatchContains,
        'starts_with': QtCore.Qt.MatchStartsWith,
        'ends_with': QtCore.Qt.MatchEndsWith,
        'exact_match': QtCore.Qt.MatchExactly,
        'wild_card': QtCore.Qt.MatchWildcard,
        'reg_exp': QtCore.Qt.MatchRegExp,
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
        # self.palette = QtGui.QPalette()
        app = QtWidgets.QApplication.instance()
        palette = app.palette()
        icon_color = palette.color(QtGui.QPalette.Text)

        self.filter_criteria_list = list()
        self.tabler_action_qicon = TablerQIcon(color=icon_color, opacity=0.6)
        self.tabler_action_checked_qicon = TablerQIcon(color=icon_color)
        self.tabler_button_qicon = TablerQIcon(color=icon_color)

        self.hightlight_item_delegate = HighlightItemDelegate()

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
        self.column_combo_box.addItems(self.column_names)
        self.condition_combo_box.addItems(self.CONDITION_TO_MATCH_FLAG_DICT.keys())

        self.setup_filter_tree_widget()

        self.add_action_on_keyword_line_edit()

        self.add_filter_button.setIcon( self.tabler_button_qicon.filter )

    def hightlight_items(self, tree_items: List[QtWidgets.QTreeWidgetItem]):

        for tree_item in tree_items:
            item_index = self.tree_widget.indexFromItem(tree_item).row()
            self.tree_widget.setItemDelegateForRow(item_index, self.hightlight_item_delegate)
        
    def reset_highlight_all_items(self):

        for row in range(self.tree_widget.topLevelItemCount()):
            self.tree_widget.setItemDelegateForRow(row, None)
            
    def hightlight_search(self):
        self.reset_highlight_all_items()

        # Get the selected column, condition, and keyword
        column = self.column_combo_box.currentText()
        condition = self.condition_combo_box.currentText()
        keyword = self.keyword_line_edit.text()
        is_negate = self.negateAction.isChecked()
        is_case_sensitive = self.matchCaseAction.isChecked()

        if not keyword:
            return

        flags = self.CONDITION_TO_MATCH_FLAG_DICT[condition]

        if is_case_sensitive:
            flags |= QtCore.Qt.MatchCaseSensitive

        match_items = self.tree_widget.findItems(keyword, flags, self.column_names.index(column))

        if is_negate:
            all_items = [self.tree_widget.topLevelItem(row) for row in range(self.tree_widget.topLevelItemCount())]
            match_items = [item for item in all_items if item not in match_items]

        self.hightlight_items(match_items)

    def add_action_on_keyword_line_edit(self):
        self.matchCaseAction = self.keyword_line_edit.addAction(self.tabler_action_qicon.letter_case, QtWidgets.QLineEdit.TrailingPosition)
        self.matchCaseAction.setToolTip('Match case')
        self.matchCaseAction.setCheckable(True)

        self.negateAction = self.keyword_line_edit.addAction(self.tabler_action_qicon.a_b_off, QtWidgets.QLineEdit.TrailingPosition)
        self.negateAction.setToolTip('Match negate')
        self.negateAction.setCheckable(True)
    
    def _setup_signal_connections(self):
        ''' Set up signal connections between widgets and slots.
        '''
        # Connect signals to slots
        self.add_filter_button.clicked.connect(self.add_filter)
        self.keyword_line_edit.returnPressed.connect(self.add_filter)
        self.matchCaseAction.triggered.connect(self.update_case_sensitive)
        self.negateAction.triggered.connect(self.update_negate)

        self.keyword_line_edit.textChanged.connect(self.hightlight_search)
        self.column_combo_box.activated.connect(self.hightlight_search)
        self.condition_combo_box.activated.connect(self.hightlight_search)
        self.matchCaseAction.triggered.connect(self.hightlight_search)
        self.negateAction.triggered.connect(self.hightlight_search)

    def setup_filter_tree_widget(self):
        # Set up filter tree widget header columns
        self.filter_tree_widget.setHeaderLabels(['Column', 'Condition', 'Keyword', 'Negate', 'Aa',''])

        self.filter_tree_widget.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.filter_tree_widget.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.filter_tree_widget.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.filter_tree_widget.header().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        self.filter_tree_widget.header().setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        self.filter_tree_widget.header().setSectionResizeMode(5, QtWidgets.QHeaderView.Fixed)

        self.add_clear_button_on_header()

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
        all_items = [self.tree_widget.topLevelItem(row) for row in range(self.tree_widget.topLevelItemCount())]
        for item in all_items:
            item.setHidden(True)

        intersect_match_items = all_items

        # Check if the item matches all of the filter criteria
        for column, condition, keyword, is_negate, is_case_sensitive in self.filter_criteria_list:

            flags = self.CONDITION_TO_MATCH_FLAG_DICT[condition]

            if is_case_sensitive:
                flags |= QtCore.Qt.MatchCaseSensitive

            match_items = self.tree_widget.findItems(keyword, flags, self.column_names.index(column))

            if is_negate:
                all_items = [self.tree_widget.topLevelItem(row) for row in range(self.tree_widget.topLevelItemCount())]
                match_items = [item for item in all_items if item not in match_items]

            intersect_match_items = [item for item in match_items if item in intersect_match_items]

        for item in intersect_match_items:
            # Set the visibility of the item based on whether it matches the criteria
            item.setHidden(False)

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
