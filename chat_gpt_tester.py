import os
import sqlite3
from tkinter import filedialog, messagebox

import customtkinter as ctk
import tksheet
from CTkListbox import *

from styles import DarkButton


class SideMenuFrame(ctk.CTkFrame):
    def __init__(self, parent, callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_propagate(False)
        self.update_callback = callback

        # configure grid
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # variables
        self.file_paths = {}
        self.selected_path = None
        self.tables = []

        self.menu_label = ctk.CTkLabel(self, text="Stored Files:", font=('Arial', 14, "bold"), anchor='w')
        self.menu_label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        button = FileDialogButton(self, self.add_file, font=('Arial', 20))

        button.grid(column=0, row=1, sticky='w', padx=10)

        self.file_listbox = CTkListbox(self, command=self.on_select)
        self.file_listbox.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)


    def add_file(self, filepath):
        if filepath not in self.file_paths.values():
            file_name = os.path.basename(filepath)
            self.file_paths[file_name] = filepath
            self.file_listbox.insert(ctk.END, file_name)
        else:
            messagebox.showwarning("Warning", "Database already exists! Please select a valid database file.")

    def on_select(self, selected_value):
        """Command in case the user selects an item in the listbox"""
        self.selected_path = self.file_paths[selected_value]
        self.get_tables()
        self.update_callback(self.tables)

    def get_tables(self):
        conn = sqlite3.connect(self.selected_path)
        cursor = conn.cursor()

        cursor.execute("SELECT NAME FROM sqlite_master WHERE type='table';")

        self.tables = [table[0] for table in cursor.fetchall()]

        conn.close()


class FileDialogButton(DarkButton):
    def __init__(self, parent, menu_callback, **kwargs):
        super().__init__(parent, command=self.select_file, text="+", width=30, height=30, **kwargs)
        self.menu_callback = menu_callback
        self.file_path = ''
        self.tables = []

    def select_file(self):
        """Open file dialog with filtering for .sql and .db files"""
        self.file_path = filedialog.askopenfilename(
            title="Select a Database File",
            filetypes=[("Database Files", "*.sql;*.db")]
        )

        # Validate selection
        if self.file_path:
            self.menu_callback(self.file_path)
        else:
            messagebox.showwarning("Warning", "No file selected! Please select a valid database file.")


class TableDropDown(ctk.CTkOptionMenu):
    def __init__(self,
                 parent,
                 **kwargs):

        super().__init__(parent,
                         values=["Select a table"],
                         command=self.option_selected,
                         **kwargs)


        self.set("Select a table")


    def option_selected(self, choice):
        self.callback(choice, )

    def refresh_values(self, new_values):
        if new_values:
            self.configure(values=new_values)
        else:
            self.configure(values=['Select a table'])
        self.set("Select a table")


class DisplayFrame(ctk.CTkFrame):
    def __init__(self, master, db_path, table, **kwargs):
        super().__init__(master, **kwargs)
        self.db_path = db_path
        self.table = table

    def load_table(self):
        pass
        # cursor = sqlite3.connect(self.db_path).cursor()
        # sql_select = "SELECT * FROM " + self.table
        # data = cursor.execute(sql_select)
        # rows = cursor.fetchall()
        #
        # column_names = [description[0] for description in cursor.description]
        #
        # sheet = tksheet.Sheet(
        #     self,
        #     data=rows,
        #     show_row_index=False,
        #     show_top_left=False
        # )
        #
        # sheet.headers(column_names)
        #
        # sheet.enable_bindings((
        #     "single_select", "drag_select", "column_select",
        #     "row_select", "row_height_resize", "column_width_resize",
        #     "arrowkeys", "right_click_popup_menu", "edit_cell"
        # ))
        #
        # sheet.pack(fill="both", expand=True)


class DataManager:
    def __init__(self, master):
        pass
        self.side_menu_frame = SideMenuFrame(master, )
        self.drop_down_menu = TableDropDown(master)
        self.display_frame = DisplayFrame(master, )
        self.selected_db_path = ""
        self.selected_table = ""


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.geometry("1280x800")
    root.title('test')

    frame = ctk.CTkFrame(root)
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Grid configure
    frame.rowconfigure(0, weight=0)
    frame.rowconfigure(1, weight=1)

    frame.columnconfigure(0, weight=0)
    frame.columnconfigure(1, weight=1)

    # Database manager header
    menu_frame = ctk.CTkFrame(frame, height=50)
    menu_frame.grid(column=1, row=0, sticky='ew', padx=10, pady=10)
    menu_frame.pack_propagate(False)

    # Database manager dropdown menu for tables
    menu_drop_down = TableDropDown(menu_frame)
    menu_drop_down.pack(padx=10, pady=10, side='right')

    # Database manager sidebar
    side_bar = SideMenuFrame(frame, menu_drop_down.refresh_values, width=175)
    side_bar.grid(column=0, row=0, rowspan=2, sticky='ns', padx=10, pady=10)

    # Database manager Label
    menu_label = ctk.CTkLabel(menu_frame, text='Data Manager Hub', font=("Arial", 16, "bold"))
    menu_label.pack(padx=10, pady=10, side='left')



    display_frame = ctk.CTkFrame(frame)
    display_frame.grid(column=1, row=1, rowspan=1, sticky='nsew', padx=10, pady=10)


    root.mainloop()
