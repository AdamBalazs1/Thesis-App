import os
import sqlite3
from tkinter import filedialog, messagebox

import customtkinter as ctk
import tksheet
from CTkListbox import *

from styles import DarkButton


class SideMenuFrame(ctk.CTkFrame):
    def __init__(self, parent, on_select_callback, button_callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_propagate(False)


        # Configure grid
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Callbacks
        self.button_callback = button_callback
        self.on_select_callback = on_select_callback

        # Configure widgets
        self.menu_label = ctk.CTkLabel(self, text="Stored Files:", font=('Arial', 14, "bold"), anchor='w')
        self.menu_label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.button = FileDialogButton(self, self.button_callback, font=('Arial', 20))
        self.button.grid(column=0, row=1, sticky='w', padx=10)

        self.listbox = CTkListbox(self, command=self.on_select)
        self.listbox.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)

    def on_select(self, selected_value):
        """ Callback to refresh the dropdown menu """
        self.on_select_callback(selected_value)


class FileDialogButton(DarkButton):
    def __init__(self, parent, callback, **kwargs):
        super().__init__(parent, command=self.select_file, text="+", width=30, height=30, **kwargs)
        self.callback = callback
        self.file_path = ''

    def select_file(self):
        """Open file dialog with filtering for .sql and .db files"""
        self.file_path = filedialog.askopenfilename(
            title="Select a Database File",
            filetypes=[("Database Files", "*.sql;*.db")]
        )

        # Validate selection
        if self.file_path:
            self.callback(self.file_path)
        else:
            messagebox.showwarning("Warning", "No file selected! Please select a valid database file.")


class TableOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, parent, callback, **kwargs):
        super().__init__(parent, values=["Select a table"], command=self.option_selected, **kwargs)
        self.callback = callback
        self.set("Select a table")


    def option_selected(self, choice):
        self.callback(choice)

    def refresh_values(self, new_values):
        if new_values:
            self.configure(values=new_values)
        else:
            self.configure(values=['Select a table'])
        self.set("Select a table")


class DisplayFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.rows = None
        self.sheet = None
        self.column_names = []

    def load_table(self, table, file_path):

        if self.sheet:
            for widget in self.winfo_children():
                widget.destroy()

        # Load table data and info
        self.get_data(table, file_path)

        # Create the sheet widget
        self.sheet = tksheet.Sheet(
            self,
            data=self.rows,
            show_row_index=False,
            show_top_left=False
        )

        self.sheet.headers(self.column_names)

        self.sheet.enable_bindings((
            "single_select", "drag_select", "column_select",
            "row_select", "row_height_resize", "column_width_resize",
            "arrowkeys", "right_click_popup_menu", "edit_cell"
        ))

        self.sheet.pack(fill="both", expand=True)

    def get_data(self, table, file_path):
        connection = sqlite3.connect(file_path)
        cursor = connection.cursor()
        sql_select = "SELECT * FROM " + table

        cursor.execute(sql_select)
        self.rows = cursor.fetchall()
        self.column_names = [description[0] for description in cursor.description]

        connection.close()


class DataManagerFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color='transparent', **kwargs)

        # Variables
        self.selected_db_path = ""

        self.file_paths = {}
        self.tables = []

        # Configure grid
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Configure widgets

        # Header Frame
        self.header_frame = ctk.CTkFrame(self, height=500)
        self.header_frame.grid_propagate(False)
        self.header_frame.grid(column=1, row=0, sticky='ew', padx=10, pady=10)


        self.option_menu = TableOptionMenu(self.header_frame, self.refresh_display)
        self.option_menu.pack(padx=10, pady=10, side='right')

        self.header_label = ctk.CTkLabel(self.header_frame, text='Data Manager Hub', font=("Arial", 16, "bold"))
        self.header_label.pack(padx=10, pady=10, side='left')

        # Side Menu Frame
        self.side_menu_frame = SideMenuFrame(self, self.refresh_drop_down_menu, self.refresh_list_box, width=200)
        self.side_menu_frame.grid(column=0, row=0, rowspan=2, sticky='ns', padx=10, pady=10)

        # Display Frame
        self.display_frame = DisplayFrame(self)
        self.display_frame.grid(column=1, row=1, rowspan=1, sticky='nsew', padx=10, pady=10)

    def refresh_list_box(self, file_path):
        """ Adds a new DB file to `self.file_paths` and displays it in a listbox. """
        if file_path not in self.file_paths.values():
            file_name = os.path.basename(file_path)
            self.file_paths[file_name] = file_path
            self.side_menu_frame.listbox.insert(ctk.END, file_name)
        else:
            messagebox.showwarning("Warning", "Database already exists! Please select a valid database file.")

    def refresh_drop_down_menu(self, file_name):
        self.selected_db_path = self.file_paths[file_name]
        self.get_tables()
        self.option_menu.refresh_values(self.tables)

    def refresh_display(self, table):
        # TODO validation
        self.display_frame.load_table(table, self.selected_db_path)

    def get_tables(self):
        """ Get the Tables of currently selected Database. """
        conn = sqlite3.connect(self.selected_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT NAME FROM sqlite_master WHERE type='table';")

        self.tables = [table[0] for table in cursor.fetchall()]

        conn.close()


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.geometry("1280x800")
    root.title('test')

    frame = DataManagerFrame(root)
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    root.mainloop()
