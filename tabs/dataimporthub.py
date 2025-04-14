import sqlite3
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
import tksheet
from CTkListbox import *

from tools.appmanager import AppManager
from tools.jointool import JoinTool
from tools.moveablepopup import MovablePopUp, ImportTable, RemoveTable, SaveJoin, RemoveInstruction, LoadInstruction, \
    TableJoin
from tools.styles import DarkButton, get_font
from tools.widgets import HeaderFrame, DataSideMenu, TableOptionMenu, ColumnOptionMenu, \
    JoinTypeOptionMenu
import tools.data_import as data_import

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "databases" / "imported_data.db"
TEMP_PATH = BASE_DIR / "databases" / "temporarydb.db"


class DataImportManager:
    def __init__(self):
        # App Manager
        self.app_manager = AppManager()

        # Fields
        self.selected_table = ""
        self.tables = {}
        self.join_instructions = {}
        self.column_headers = []
        self.app_table_path = str(DB_PATH)
        self.rows = None

        self.load_settings()

    def add_table(self, name, path, table):
        self.tables[name] = {"path": path,
                             "table": table}
        self.set_tables()

    def remove_table(self, name):
        self.tables.pop(name)
        self.set_tables()

    def add_join_instruction(self, name, columns, steps):
        self.join_instructions[name] = {"columns": columns,
                                        "steps": steps}
        self.set_join_instructions()

    def remove_join_instruction(self, name):
        self.join_instructions.pop(name)
        self.set_join_instructions()

    def get_table_data(self, selected_item):
        self.selected_table = selected_item

        connection = sqlite3.connect(self.app_table_path)
        cursor = connection.cursor()
        sql_select = "SELECT * FROM " + self.selected_table

        cursor.execute(sql_select)
        self.rows = cursor.fetchall()
        self.column_headers = [description[0] for description in cursor.description]

        connection.close()

    def set_tables(self):
        self.app_manager.set_setting("tables", self.tables)

    def set_join_instructions(self):
        self.app_manager.set_setting("join_instructions", self.join_instructions)

    # ------------------------------------------------------------------------------------------------------------------

    def load_settings(self):
        settings = self.app_manager.settings

        if "tables" in settings.keys():
            for key, value in settings['tables'].items():
                self.tables[key] = value
            else:
                self.set_tables()

        if "join_instructions" in settings.keys():
            for key, value in settings["join_instructions"].items():
                self.join_instructions[key] = value
            else:
                self.set_join_instructions()


class DataImportBaseFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         fg_color='transparent',
                         **kwargs)

        self.master = master
        self.manager = DataImportManager()

        # configure grid
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=2)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Widgets

        # Side Menu Frame
        self.side_frame = DataSideMenu(self, 'Tables:', self.add_on_press, self.remove_on_press, self.listbox_on_select)

        # Header Frame
        self.header_frame = HeaderFrame(self, 'Database Manager Hub')

        self.refresh_listbox()

        self.utility_frame = self.header_frame.utility_frame

        self.combine_button = DarkButton(self.utility_frame, command=self.combine_button_on_press, text="Join tables")
        self.combine_button.grid()

        # Content Frame
        self.content_frame = SheetFrame(self)
        self.content_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)

    def add_on_press(self):
        MovablePopUp(self, ImportTable, self.import_callback, title="Import Table", geometry="400x250")

    def import_callback(self, name, path, table):
        if name not in self.manager.tables.keys():
            # Import data to temporary DB
            data_import.import_data(path, TEMP_PATH)

            # Save table to settings
            self.manager.add_table(name, path, table)

            # Move table to local database
            data_import.copy_table_and_rename(TEMP_PATH, self.manager.app_table_path, table, name)

            # Reset temporary database
            data_import.delete_all_tables(TEMP_PATH)

            # Refresh listbox
            self.refresh_listbox()

        else:
            messagebox.showwarning("Warning", "Name already exists! Please select a valid name for the table.")

    def refresh_listbox(self):
        self.side_frame.listbox.delete("all")
        for i, key in enumerate(self.manager.tables):
            self.side_frame.listbox.insert(i, key)

    def remove_on_press(self):
        MovablePopUp(self, RemoveTable, self.remove_table, data=data_import.get_tables(DB_PATH),title="Remove Table")

    def remove_table(self, table):
        if table in self.manager.tables:
            data_import.delete_table(self.manager.app_table_path, table)
            self.manager.remove_table(table)
        self.refresh_listbox()

    def remove_instruction(self, instruction):
        self.manager.remove_join_instruction(instruction)
        self.refresh_listbox()

    def listbox_on_select(self, selected_item):
        self.content_frame = SheetFrame(self)
        self.content_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)

        self.manager.get_table_data(selected_item)
        self.content_frame.load_sheet(self.manager.rows, self.manager.column_headers)

    def combine_button_on_press(self):
        self.content_frame = JoinTableFrame(self)
        self.content_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)


class SheetFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         **kwargs)

        self.sheet = None

    def load_sheet(self, rows, column_headers):
        for widget in self.winfo_children():
            widget.destroy()

        self.sheet = tksheet.Sheet(
            self,
            data=rows,
            show_row_index=False,
            show_top_left=False
        )

        self.sheet.change_theme("dark")

        self.sheet.set_options(table_bg="#2A2D2E")

        self.sheet.headers(column_headers)

        self.sheet.enable_bindings((
            "single_select", "drag_select", "column_select",
            "row_select", "row_height_resize", "column_width_resize",
            "arrowkeys", "right_click_popup_menu", "edit_cell"
        ))

        self.sheet.pack(fill="both", expand=True)


class JoinTableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         **kwargs)

        # Fields
        self.row_counter = 1
        self.frames = []
        self.master = master
        self.manager = self.master.manager
        self.tables = data_import.get_tables(self.manager.app_table_path)
        self.join_tables = []

        # Grid configure
        self.rowconfigure(0, weight=0)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Widgets
        self.title = ctk.CTkLabel(self, text="Join tables", font=get_font())
        self.title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="we", )

        self.save_button = DarkButton(self.button_frame, text="Save", command=self.save_on_press)
        self.save_button.grid(row=0, column=0, padx=(10, 0))

        self.load_button = DarkButton(self.button_frame, text="Load", command=self.load_on_press)
        self.load_button.grid(row=0, column=1, padx=(10, 0))

        self.delete_button = DarkButton(self.button_frame, text="Delete", command=self.delete_on_press)
        self.delete_button.grid(row=0, column=2, sticky="e", padx=(10, 0))

        self.table_create_button = DarkButton(self.button_frame, text="Create Table", command=self.table_create_on_press)
        self.table_create_button.grid(row=0, column=3, sticky="e", padx=(10, 0))

        self.add_step = DarkButton(self.button_frame, text="Add Join", command=self.add_frame_on_press)
        self.add_step.grid(row=0, column=4, sticky="e", padx=(10, 0))

        self.remove_step = DarkButton(self.button_frame, text="Remove Join", command=self.remove_frame_on_press)
        self.remove_step.grid(row=0, column=5, sticky="e", padx=(10, 0))

    def add_frame_on_press(self):
        self.rowconfigure(self.row_counter, weight=1)
        self.frames.append(TableFrame(self, self.row_counter, self.tables))
        self.row_counter += 1

    def remove_frame_on_press(self):
        if self.frames:
            self.frames.pop().destroy()
            self.row_counter -= 1

    def save_on_press(self):
        self.join_tables = []
        for frame in self.frames:
            if frame.table_1.get() not in self.join_tables:
                self.join_tables.append(frame.table_1.get())
            if frame.table_2.get() not in self.join_tables:
                self.join_tables.append(frame.table_2.get())


        MovablePopUp(self, SaveJoin, self.save_on_ok, title="Save template", geometry="400x400", root_ref=self.master)

    def save_on_ok(self, instruction_name, columns):
        steps = {}
        step_counter = 1

        if self.frames:
            for frame in self.frames:
                step_name = f"step_{step_counter}"
                table_1 = frame.table_1.get()
                table_2 = frame.table_2.get()
                key_1 = frame.table_1_key.get()
                key_2 = frame.table_2_key.get()
                join_1 = frame.table_1_join_type.get()
                join_2 = frame.table_2_join_type.get()
                join_type = self.get_join_type(join_1, join_2)

                if table_1 != table_2:
                    steps[step_name] = {"table_1": table_1,
                                        "table_2": table_2,
                                        "key_1": key_1,
                                        "key_2": key_2,
                                        "join_type": join_type,
                                        }
                    step_counter += 1
                else:
                    messagebox.showwarning("Warning", "Same table selected twice!")

            self.manager.add_join_instruction(instruction_name, columns, steps)
        else:
            messagebox.showwarning("Warning", "No connections selected.")

    def load_on_press(self):
        MovablePopUp(self,
                     work_area=LoadInstruction,
                     callback=self.load_on_ok,
                     title="Select Instruction",
                     root_ref=self.master,
                     data=self.manager.join_instructions)

    def load_on_ok(self, name):
        for frame in self.frames:
            self.remove_frame_on_press()

        for step in self.manager.join_instructions[name]["steps"]:
            table_1 = self.manager.join_instructions[name]["steps"][step]["table_1"]
            table_2 = self.manager.join_instructions[name]["steps"][step]["table_2"]
            key_1 = self.manager.join_instructions[name]["steps"][step]["key_1"]
            key_2 = self.manager.join_instructions[name]["steps"][step]["key_2"]
            join_type = self.manager.join_instructions[name]["steps"][step]["join_type"]
            self.rowconfigure(self.row_counter, weight=1)
            frame = TableFrame(self, self.row_counter, self.tables)
            frame.load_settings(table_1, table_2, key_1, key_2, join_type)
            self.frames.append(frame)
            self.row_counter += 1

    def table_create_on_press(self):
        MovablePopUp(self,
                     work_area=TableJoin,
                     callback=self.table_create_on_ok,
                     title="Select Instruction",
                     root_ref=self.master,
                     data=self.manager.join_instructions)

    def table_create_on_ok(self, name):
        table_name = "JOIN_" + name
        #
        instruction = self.manager.join_instructions[name]
        path = self.manager.app_table_path

        join_tool = JoinTool(name, instruction, path)

        join_tool.unpack_instruction()
        join_tool.join_tables()

        # Save table to settings
        self.manager.add_table(table_name, path, table_name)

        # Refresh listbox
        self.master.refresh_listbox()

    def delete_on_press(self):
        MovablePopUp(self,
                     RemoveInstruction,
                     self.delete_on_ok,
                     title="Delete Instruction",
                     geometry="400x250",
                     root_ref=self.master,
                     data=self.manager.join_instructions.keys())

    def delete_on_ok(self, event):
        self.manager.remove_join_instruction(event)

    @staticmethod
    def get_join_type(join_1, join_2):
        join_types = ["INNER", "LEFT", "RIGHT", "FULL"]
        if join_1 == join_2:
            if join_1 == "Show Only Matches":
                join_type = join_types[0]
            else:
                join_type = join_types[3]
        else:
            if join_1 == "Show Only Matches":
                join_type = join_types[2]
            else:
                join_type = join_types[1]

        return join_type


class TableFrame(ctk.CTkFrame):
    def __init__(self, master, row, tables, **kwargs):
        super().__init__(master, fg_color="#333333", **kwargs)
        self.grid_propagate(False)

        self.master = master
        self.manager = self.master.manager
        self.database = self.manager.app_table_path
        self.tables = tables

        self.grid(row=row, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)

        self.join_types = ['Show Only Matches', 'Show All']

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Labels

        self.table_label = ctk.CTkLabel(self, text="Table", font=get_font())
        self.table_label.grid(row=0, column=0)

        self.key_label = ctk.CTkLabel(self, text="Key", font=get_font())
        self.key_label.grid(row=0, column=1)

        self.join_type_label = ctk.CTkLabel(self, text="Join type", font=get_font())
        self.join_type_label.grid(row=0, column=2)

        # Table 1

        self.table_1 = TableOptionMenu(self, self.database, width=160)
        self.table_1.grid(row=1, column=0)
        self.table_1.refresh_values(self.tables)

        self.table_1_key = ColumnOptionMenu(self, width=160)
        self.table_1_key.grid(row=1, column=1)

        self.table_1_join_type = JoinTypeOptionMenu(self, values=self.join_types, width=160)
        self.table_1_join_type.grid(row=1, column=2)

        # Create connection:
        self.table_1.set_connection(self.table_1_key)

        # Table 2

        self.table_2 = TableOptionMenu(self, self.database, width=160)
        self.table_2.grid(row=2, column=0)
        self.table_2.refresh_values(self.tables)

        self.table_2_key = ColumnOptionMenu(self, width=160)
        self.table_2_key.grid(row=2, column=1)

        self.table_2_join_type = JoinTypeOptionMenu(self, values=self.join_types, width=160)
        self.table_2_join_type.grid(row=2, column=2)

        # Create connection:
        self.table_2.set_connection(self.table_2_key)

    def load_settings(self, table_1, table_2, key_1, key_2, join_type):
        self.table_1.set(table_1)
        self.table_2.set(table_2)

        self.table_1_key.set(key_1)
        self.table_2_key.set(key_2)



        if join_type == "INNER":
            self.table_1_join_type.set('Show Only Matches')
            self.table_2_join_type.set('Show Only Matches')
        elif join_type == "LEFT":
            self.table_1_join_type.set('Show All')
            self.table_2_join_type.set('Show Only Matches')
        elif join_type == "RIGHT":
            self.table_1_join_type.set('Show Only Matches')
            self.table_2_join_type.set('Show All')
        elif join_type == "FULL":
            self.table_1_join_type.set('Show All')
            self.table_2_join_type.set('Show All')


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title('Test')
    root.geometry('1280x800')

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    base_frame = DataImportBaseFrame(root)
    base_frame.grid(row=0, column=0, sticky='nsew')

    root.mainloop()
