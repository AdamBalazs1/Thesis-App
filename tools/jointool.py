import sqlite3
from tkinter import messagebox


class JoinTool:
    def __init__(self, name, instruction, path):
        self.instruction = instruction

        self.name = f"JOIN_{name}"

        # Steps from instruction
        self.steps = None

        # DB_path
        self.path = path

        # SQL formatted column names
        self.table_columns = []

        self.table_1 = None
        self.table_2 = None
        self.key_1 = None
        self.key_2 = None
        self.join_type = None

    def unpack_instruction(self):
        # Columns
        self.unpack_columns()

        # Steps
        self.steps = self.instruction["steps"]

    def unpack_columns(self):
        for column in self.instruction["columns"]:
            table, col = column.split("/")
            self.table_columns.append([table, col])

        print(self.table_columns)

    def unpack_step(self, step):
        self.table_1 = self.steps[step]["table_1"]
        self.table_2 = self.steps[step]["table_2"]
        self.key_1 = self.steps[step]["key_1"]
        self.key_2 = self.steps[step]["key_2"]
        self.join_type = self.steps[step]["join_type"]

    def join_tables(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        column_string = ", ".join([f"{table}.{col}" for table, col in self.table_columns])

        sql_join_line = ""
        sql_from = ""

        count = 1

        sql_create = f"CREATE TABLE {self.name} AS"
        sql_select = f"SELECT {column_string}"


        for step in self.steps:
            self.unpack_step(step)
            if self.join_type not in ["INNER", "LEFT", "RIGHT", "FULL"]:
                messagebox.showerror(title="Error", message="Invalid join type. Use INNER, LEFT, RIGHT, or FULL.")
                return

            # FIXME SQLite doesn't support RIGHT or FULL JOIN natively...
            if self.join_type in ["RIGHT", "FULL"]:
                messagebox.showerror(title="Not Supported", message=f"{self.join_type} JOIN is not supported in SQLite.")
                return
            if count == 1:
                sql_from = f"FROM {self.table_1}"

            sql_join_line += f"JOIN {self.table_2} ON {self.table_1}.{self.key_1} = {self.table_2}.{self.key_2}\n"

        query = sql_create + "\n" + sql_select + "\n" + sql_from + "\n" + sql_join_line

        try:
            cursor.execute(query)
            conn.commit()
            messagebox.showinfo(title="Success", message=f"Joined table saved as '{self.name}'")
        except sqlite3.Error as e:
            messagebox.showerror(title="SQLite Error", message=f"{e}")
        finally:
            conn.close()
