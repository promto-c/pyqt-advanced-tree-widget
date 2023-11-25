from typing import Any, Dict, List, Union

from PyQt5 import QtCore, QtGui, QtWidgets, QtSql

import sys

class DynamicModels(QtSql.QSqlDatabase):
    def __init__(self, db_file: str = None, db_type: str = 'QSQLITE'):
        super().__init__(db_type)

        self.model = QtSql.QSqlTableModel(db=self)
        self.query = QtSql.QSqlQuery(db=self)

        if db_file:
            self.setDatabaseName(db_file)
            if not self.open():
                print(f"Error: connection to database failed")

    def get_table_names(self):

        self.query.exec_("SELECT name FROM sqlite_master WHERE type='table';")
        tables = []

        while self.query.next():

            tables.append(self.query.value(0))
    
        return tables

    def set_model(self, table_name, fields: Union[str, List[str]] = '*') -> None:
        column_names = self.get_column_names(table_name)

        fields_str = ', '.join([field for field in fields if field in column_names]) if isinstance(fields, list) else fields

        self.query.exec_(f'SELECT {fields_str} FROM {table_name}')
        self.model.setTable(table_name)
        self.model.setQuery(self.query)
        self.model.select()
    
    def get_column_names(self, table_name) -> List[str]:
        query_string = f"SELECT * FROM {table_name} LIMIT 0"
        
        self.query.exec_(query_string)  # Query with LIMIT 0 to fetch only structure, no data
        record = self.query.record()  # Get the QSqlRecord object
        column_names = [record.fieldName(i) for i in range(record.count())]  # Extract column names
        return column_names

    def get_ddl(self, table_name):
        query_string = f"SELECT sql FROM sqlite_schema WHERE name = '{table_name}'"

        self.query.exec_(query_string)

        

        if self.query.next():
            schema = self.query.value(0)
            print( schema)
        else:
            print(f"No schema found for table {table_name}")
            return None

    def execute_and_fetch(self, query_string) -> List[Dict[Any, Any]]:
        self.query.exec_(query_string)
        row_dicts = list()
        while self.query.next():
            row_dict = {self.query.record().fieldName(i): self.query.value(i) for i in range(self.query.record().count())}
            row_dicts.append(row_dict)
        return row_dicts

    def get_schema_info(self, table_name):
        query_string = f"PRAGMA table_info({table_name})"
        
        return self.execute_and_fetch(query_string)
    
    def get_index_info(self, table_name):
        # unique
        query_string = f"PRAGMA index_list({table_name})"
        
        return self.execute_and_fetch(query_string)
    
    def get_relation_info(self, table_name):
        query_string = f"PRAGMA foreign_key_list({table_name})"
        return self.execute_and_fetch(query_string)

class TableSelector(QtWidgets.QTreeWidget):
    def __init__(self, database: DynamicModels, parent=None):
        super(TableSelector, self).__init__(parent)
        # self.db_conn = db_conn
        self.database = database
        self.initUI()

    def initUI(self):
        tables = self.database.get_table_names()
        
        for table in tables:
            item = QtWidgets.QTreeWidgetItem(self, [table])
            self.addTopLevelItem(item)

class DatabaseTreeView(QtWidgets.QTreeView):
    def __init__(self, database: DynamicModels, parent=None):
        super().__init__(parent)
        self.database = database

        self.setModel(self.database.model)

        self.setSortingEnabled(True)

    def display_table(self, table_name):
        self.database.set_model(table_name)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db_file, parent=None):
        super(MainWindow, self).__init__(parent)
        self.db_file = db_file

        self.database = DynamicModels(db_file)
        
        self.tableSelector = TableSelector(self.database)
        self.dockWidget = QtWidgets.QDockWidget("Tables", self)
        self.dockWidget.setWidget(self.tableSelector)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)
        
        self.database_tree_view = DatabaseTreeView(self.database)
        self.setCentralWidget(self.database_tree_view)
        
        self.tableSelector.itemClicked.connect(self.on_table_selected)

    def on_table_selected(self, item):
        table_name = item.text(0)
        
        # print(self.database.get_relation_info(table_name))
        print(self.database.get_index_info(table_name))

        self.database_tree_view.display_table(table_name)


if __name__ == '__main__':
    from theme import theme

    app = QtWidgets.QApplication(sys.argv)
    theme.set_theme(app, 'dark')

    mainWin = MainWindow('example.db')
    mainWin.show()

    app.exec_()
