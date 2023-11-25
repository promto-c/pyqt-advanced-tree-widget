import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QApplication
import dbml_sqlite

def create_schema(ddl: str, dbname: str, dbtype='QSQLITE'):
    db = QSqlDatabase.addDatabase(dbtype)
    db.setDatabaseName(dbname)
    
    if not db.open():
        print(f"Error: connection to database failed")
        sys.exit(1)
    
    query = QSqlQuery(db)
    statements = ddl.strip().split(';')
    for statement in statements:
        if not statement:
            continue

        if not query.exec_(statement):
            print(f"Error: Unable to execute statement: {query.lastError().text()}")
            db.close()
            sys.exit(1)

    db.close()
    sys.exit(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ddl = dbml_sqlite.toSQLite('dbdiagram.dbml')
    create_schema(ddl, dbname='./example.db')
    sys.exit(app.exec_())
