import os
from PyQt5.QtWidgets import QApplication, QTreeView, QStyledItemDelegate, QComboBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


class ComboBoxDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(["Not Started", "In Progress", "Completed"])
        return editor

    def setEditorData(self, editor, index):
        value = index.data()
        idx = editor.findText(value)
        editor.setCurrentIndex(idx)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value)

        # Update the status in the database
        asset_name = model.sibling(index.row(), 0, index).data()
        update_query = QSqlQuery()
        update_query.prepare("UPDATE assets SET status = ? WHERE name = ?")
        update_query.addBindValue(value)
        update_query.addBindValue(asset_name)
        update_query.exec_()


def initialize_db():
    db_file = "asset.db"
    db_exists = os.path.exists(db_file)

    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_file)

    if not db.open():
        print("Error: connection with database failed")
        return False

    if not db_exists:
        # Create tables and insert mock-up data if the database does not exist
        create_and_populate_tables()

    return True


def create_and_populate_tables():
    query = QSqlQuery()

    # Create asset_types table
    query.exec_("""
    CREATE TABLE asset_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL
    )""")

    # Insert asset types
    query.exec_("INSERT INTO asset_types (type) VALUES ('3D Models')")

    # Create assets table
    query.exec_("""
    CREATE TABLE assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        version TEXT NOT NULL,
        description TEXT NOT NULL,
        type_id INTEGER,
        FOREIGN KEY (type_id) REFERENCES asset_types(id)
    )""")



    # Insert assets
    query.exec_("""INSERT INTO assets (name, status, version, description, type_id)
                    VALUES ('Car_Model', 'Not Started', 'v1.0', 'A 3D car model', 1)""")
    query.exec_("""INSERT INTO assets (name, status, version, description, type_id)
                    VALUES ('Tree_Model', 'Completed', 'v2.1', 'A 3D tree model', 1)""")


def build_model():
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Asset Type/Name", "Status", "Version", "Description"])

    query = QSqlQuery("SELECT * FROM asset_types")
    while query.next():
        type_id = query.value(0)
        type_name = query.value(1)

        # Asset Type Item
        asset_type_item = QStandardItem(type_name)

        asset_query = QSqlQuery(f"SELECT * FROM assets WHERE type_id = {type_id}")
        while asset_query.next():
            name = asset_query.value(1)
            status = asset_query.value(2)
            version = asset_query.value(3)
            description = asset_query.value(4)

            # Child Items for each Asset
            name_item = QStandardItem(name)
            status_item = QStandardItem(status)
            version_item = QStandardItem(version)
            description_item = QStandardItem(description)

            # Appending Child Items to the Asset Type Item
            asset_type_item.appendRow([name_item, status_item, version_item, description_item])

        # Append the Asset Type Item to the model
        model.appendRow(asset_type_item)

    return model

app = QApplication([])

if not initialize_db():
    exit(1)

tree_view = QTreeView()
model = build_model()
tree_view.setModel(model)
tree_view.expandAll()

# Set the ComboBox delegate for the Status column
tree_view.setItemDelegateForColumn(1, ComboBoxDelegate())
# tree_view.setItemDelegateForColumn(1, None)

tree_view.show()
app.exec_()
