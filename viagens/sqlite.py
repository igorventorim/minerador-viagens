import sqlite3
import traceback
import sys


class Sqlite():

    def __init__(self, database_name):
        self.database_name = database_name

    def create_database(self):
        try:
            sqliteConnection = sqlite3.connect(self.database_name)
            cursor = sqliteConnection.cursor()
            # print("Database created and Successfully Connected to SQLite")

            sqlite_select_Query = "select sqlite_version();"
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()
            # print("SQLite Database Version is: ", record)
            cursor.close()

        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                # print("The SQLite connection is closed")

    def create_table(self, table_name, struct_table):
        try:
            sqliteConnection = sqlite3.connect(self.database_name)
            sqlite_create_table_query = '''CREATE TABLE {} (
                                        {});'''.format(table_name, struct_table)

            cursor = sqliteConnection.cursor()
            # print("Successfully Connected to SQLite")
            cursor.execute(sqlite_create_table_query)
            sqliteConnection.commit()
            # print("SQLite table created")

            cursor.close()

        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                # print("sqlite connection is closed")

    def execute_script_sql(self, path):
        try:
            sqliteConnection = sqlite3.connect(self.database_name)
            cursor = sqliteConnection.cursor()
            # print("Successfully Connected to SQLite")

            with open(path, 'r') as sqlite_file:
                sql_script = sqlite_file.read()

            cursor.executescript(sql_script)
            # print("SQLite script executed successfully")
            cursor.close()

        except sqlite3.Error as error:
            print("Error while executing sqlite script", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                # print("sqlite connection is closed")

    def read_table(self, tablename, columns='*', column_identify=None, value_column_identify=None):
        try:
            sqliteConnection = sqlite3.connect(self.database_name)
            cursor = sqliteConnection.cursor()
            # print("Connected to SQLite")

            if column_identify:
                sqlite_select_query = """SELECT {} from {} WHERE {} = {}""".format(
                    columns, tablename, column_identify, value_column_identify)
            else:
                sqlite_select_query = """SELECT {} from {}""".format(
                    columns, tablename)
            cursor.execute(sqlite_select_query)
            records = cursor.fetchall()
            # print("Total rows are:  ", len(records))
            # print("Printing each row")
            return records

            cursor.close()

        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                # print("The SQLite connection is closed")

    def insert_element(self, table_name, struct_element, values):
        try:
            sqliteConnection = sqlite3.connect(self.database_name)
            cursor = sqliteConnection.cursor()
            # print("Successfully Connected to SQLite")

            sqlite_insert_query = """INSERT INTO {}({})  VALUES  ({})""".format(table_name,
                                                                                struct_element, values)

            count = cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()
            # print(
            #     "Record inserted successfully", cursor.rowcount)
            cursor.close()

        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table")
            print("Exception class is: ", error.__class__)
            print("Exception is", error.args)
            print('Printing detailed SQLite exception traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                # print("The SQLite connection is closed")

    def delete_element(self, tablename, column_identify, value_column_identify):
        try:
            sqliteConnection = sqlite3.connect(self.database_name)
            cursor = sqliteConnection.cursor()
            # print("Successfully Connected to SQLite")

            sqlite_delete_query = """DELETE FROM {}  WHERE {} = {}""".format(
                tablename, column_identify, value_column_identify)

            count = cursor.execute(sqlite_delete_query)
            sqliteConnection.commit()
            # print(
            # "Delete successfully", cursor.rowcount)
            cursor.close()

        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table")
            print("Exception class is: ", error.__class__)
            print("Exception is", error.args)
            print('Printing detailed SQLite exception traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                # print("The SQLite connection is closed")

    def update_element(self, tablename, column_update, value_column_update, column_identify, value_column_identify):
        try:
            sqliteConnection = sqlite3.connect(self.database_name)
            cursor = sqliteConnection.cursor()
            # print("Successfully Connected to SQLite")

            sqlite_update_query = """UPDATE {} SET {} = {} WHERE {} = {}""".format(
                tablename, column_update, value_column_update, column_identify, value_column_identify)

            count = cursor.execute(sqlite_update_query)
            sqliteConnection.commit()
            # print(
            # "Update successfully ", cursor.rowcount)
            cursor.close()

        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table")
            print("Exception class is: ", error.__class__)
            print("Exception is", error.args)
            print('Printing detailed SQLite exception traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                # print("The SQLite connection is closed")

    def sql_query(self, query):
        try:
            sqliteConnection = sqlite3.connect(self.database_name)
            cursor = sqliteConnection.cursor()
            # print("Successfully Connected to SQLite")

            sqlite_update_query = query

            count = cursor.execute(sqlite_update_query)
            sqliteConnection.commit()
            # print(
            # "Query successfully", cursor.rowcount)
            cursor.close()

        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table")
            print("Exception class is: ", error.__class__)
            print("Exception is", error.args)
            print('Printing detailed SQLite exception traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                # print("The SQLite connection is closed")
