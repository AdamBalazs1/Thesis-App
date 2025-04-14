import pandas as pd
import sqlite3
import os
import sqlite3



def import_data(file_path, db_name, table_name=None):
    """
    Imports a data file (CSV, Excel, SQL, DB, SQLite) into an SQLite database.
    If table_name is provided, only that specific table will be imported (for .db and .sqlite files).
    """
    file_ext = os.path.splitext(file_path)[-1].lower()
    conn = sqlite3.connect(db_name)  # Connect to SQLite database

    if file_ext == ".csv":
        df = pd.read_csv(file_path)
        df.to_sql("imported_table", conn, if_exists="replace", index=False)

    elif file_ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
        df.to_sql("imported_table", conn, if_exists="replace", index=False)

    elif file_ext == ".sql":
        with open(file_path, "r", encoding="utf-8") as sql_file:
            sql_script = sql_file.read()
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()

    elif file_ext in [".db", ".sqlite"]:
        src_conn = sqlite3.connect(file_path)
        src_cursor = src_conn.cursor()

        if table_name:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", src_conn)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        else:
            src_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = src_cursor.fetchall()
            for table in tables:
                table_name = table[0]
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", src_conn)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"Imported SQLite Table: {table_name}")
            src_conn.close()

        src_conn.close()

    conn.close()
    print("Import completed successfully!")

def get_tables(file_path):
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    cursor.execute("SELECT NAME FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    conn.close()

    return tables

def delete_all_tables(db_path):
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Query to get all the table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Drop each table
    for table in tables:
        table_name = table[0]
        print(f"Dropping table: {table_name}")
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    # Commit changes and close the connection
    connection.commit()
    connection.close()
    print("All tables have been deleted.")

def delete_table(db_path, table):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    print(f"Dropping table: {table}")
    cursor.execute(f"DROP TABLE IF EXISTS {table}")

    connection.close()

def copy_table_and_rename(source_db, target_db, old_table_name, new_table_name):
    # Connect to the source database (where the table is located)
    source_conn = sqlite3.connect(source_db)
    source_cursor = source_conn.cursor()

    # Connect to the target database (where the table will be moved)
    target_conn = sqlite3.connect(target_db)
    target_cursor = target_conn.cursor()

    # Step 1: Get the schema of the table in the source database
    source_cursor.execute(f"PRAGMA table_info({old_table_name})")
    columns = source_cursor.fetchall()

    print(columns)

    # Step 2: Create a new table in the target database with the new name
    column_definitions = ", ".join(
        [f"{column[1]} {column[2]}" for column in columns])  # Create column definitions from schema
    target_cursor.execute(f"CREATE TABLE {new_table_name} ({column_definitions})")

    # Step 3: Copy the data from the source table to the new table in the target database
    source_cursor.execute(f"SELECT * FROM {old_table_name}")
    rows = source_cursor.fetchall()

    # Insert the data into the new table
    target_cursor.executemany(f"INSERT INTO {new_table_name} VALUES ({', '.join(['?'] * len(columns))})", rows)

    # Step 4: Commit the changes to both databases
    source_conn.commit()
    target_conn.commit()

    # Close both database connections
    source_conn.close()
    target_conn.close()

    print(f"Table '{old_table_name}' has been moved to '{target_db}' as '{new_table_name}'.")

def get_columns(file_path, table):
    connection = sqlite3.connect(file_path)
    cursor = connection.cursor()

    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    connection.close()
    return column_names


if __name__ == '__main__':
    pass
    # import_data("two_tables_sample.sql", "my_database.db")
    # import_data("existing_data.db", "my_database.db", table_name="orders")
    # delete_all_tables("imported_data.db")

    # copy_table_and_rename('music.sqlite', 'my_database.db', 'songs', 'new_songs')

