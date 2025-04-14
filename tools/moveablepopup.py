import sqlite3
from tkinter import filedialog, messagebox
from pathlib import Path

import customtkinter as ctk
import tools.data_import as data_import
from tools.freighttool import create_freight_record, update_freight_status

from tools.styles import TransparentButton, get_font
from tools.widgets import DarkAddButton, DataOptionMenu

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "databases" / "imported_data.db"
TEMP_PATH = BASE_DIR / "databases" / "temporarydb.db"
FREIGHT_PATH = BASE_DIR / "databases" / "freight.db"


class MovablePopUp(ctk.CTkToplevel):
    def __init__(self, master, work_area, callback=None, title="Popup Window", geometry='400x200', root_ref=None, data=None, **kwargs):
        super().__init__(master,
                         **kwargs)
        self.master = master
        self.title(title)
        self.geometry(geometry)
        self.overrideredirect(True)
        self.work_area = work_area

        self.root_ref = root_ref

        # Center the popup in the middle of the master (root) window

        if self.root_ref:
            self.center_popup(root_ref, geometry)
        else:
            self.center_popup(master, geometry)

        self.x = None
        self.y = None

        self.header = ctk.CTkFrame(self, corner_radius=0, border_width=1)
        self.header.pack(fill="both", expand=True)

        self.header.rowconfigure(0, weight=0)
        self.header.rowconfigure(1, weight=1)

        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=0)

        self.title_label = ctk.CTkLabel(self.header, text=title, font=("Arial", 14, "bold"))
        self.title_label.grid(row=0, column=0, sticky='n', pady=2, columnspan=2)

        self.close_button = TransparentButton(self.header, text="X", width=30, command=self.destroy)
        self.close_button.grid(row=0, column=1, padx=2, pady=2)

        self.work_area = work_area(self.header, callback, data=data, popup_instance=self)
        self.work_area.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=1, pady=1)

        # Bindings
        self.header.bind("<ButtonPress-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.on_move)

        for widget in self.header.winfo_children():
            widget.bind("<ButtonPress-1>", self.start_move)
            widget.bind("<B1-Motion>", self.on_move)

        self.bind("<Escape>", lambda event: self.destroy())

        # Focus
        self.focus()
        self.grab_set()

    def start_move(self, event):
        """
        Initializes the window movement by storing the mouse's absolute position.

        Args:
            event (tkinter.Event): The event object containing the mouse coordinates.
        """
        self.x = event.x_root
        self.y = event.y_root

    def on_move(self, event):
        """
        Moves the window based on the mouse's movement.

        Args:
            event (tkinter.Event): The event object containing the updated mouse coordinates.
        """
        try:
            dx = event.x_root - self.x
            dy = event.y_root - self.y
            self.geometry(f"+{self.winfo_x() + dx}+{self.winfo_y() + dy}")
            self.x = event.x_root
            self.y = event.y_root
        except:
            pass

    def center_popup(self, master, geometry):
        """
        Centers the popup window in relation to the master window.

        Args:
            master (ctk.CTk): The main application window to center the popup within.
            geometry (str): The size of the popup in the format 'width x height', e.g., '400x200'.
        """
        popup_width, popup_height = map(int, geometry.split('x'))

        master.update_idletasks()  # Ensure correct size before fetching dimensions
        master_width = master.winfo_width()
        master_height = master.winfo_height()
        master_x = master.winfo_x()
        master_y = master.winfo_y()

        # Calculate the position for centering
        x = master_x + (master_width // 2) - (popup_width // 2)
        y = master_y + (master_height // 2) - (popup_height // 2)

        # Apply the position
        self.geometry(f"{popup_width}x{popup_height}+{x}+{y}")


class WorkArea(ctk.CTkFrame):
    def __init__(self, master, callback, popup_instance, data=None, **kwargs):
        super().__init__(master,
                         corner_radius=0,
                         fg_color='transparent',
                         **kwargs)

        self.callback = callback
        self.pop_up_instance = popup_instance
        self.data = data


class EditLayoutPopup(WorkArea):
    def __init__(self, master, callback, popup_instance, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         **kwargs)

        self.validate_cmd = self.register(self.validate_input)

        # Grid configure
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Row widgets
        self.row_label = ctk.CTkLabel(self, text='Number of Rows 1 - 6:')
        self.row_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='w')

        self.row_entry = ctk.CTkEntry(self, border_width=1, corner_radius=0, fg_color='transparent', validate="key",
                                      validatecommand=(self.validate_cmd, "%P"))
        self.row_entry.grid(row=0, column=1, sticky='ew', padx=(10, 50), pady=(10, 0))

        # Col widgets
        self.col_label = ctk.CTkLabel(self, text='Number of Columns 1 - 6:')
        self.col_label.grid(row=1, column=0, padx=10, pady=(20, 0), sticky='w')

        self.column_entry = ctk.CTkEntry(self, border_width=1, corner_radius=0, fg_color='transparent', validate="key",
                                         validatecommand=(self.validate_cmd, "%P"))
        self.column_entry.grid(row=1, column=1, sticky='ew', padx=(10, 50), pady=(20, 0))

        # utility buttons

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    @staticmethod
    def validate_input(value):
        """ Only allow numbers between 1 and 8 """
        if value == "":
            return True
        if value.isdigit():
            num = int(value)
            return 1 <= num <= 6
        return False

    def ok_press(self):
        if self.row_entry.get() and self.column_entry.get():
            dimensions = (int(self.row_entry.get()), int(self.column_entry.get()))
            self.callback(dimensions)
            self.pop_up_instance.destroy()
        else:
            pass

    def cancel_press(self):
        self.pop_up_instance.destroy()


class WidgetSize(WorkArea):
    def __init__(self, master, callback, popup_instance, data, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         **kwargs)

        self.validate_cmd = self.register(self.validate_input)

        self.data = data

        # Grid configure
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Widget Select
        self.widget_select_label = ctk.CTkLabel(self, text="Widget select:")
        self.widget_select_label.grid(row=0, column=0, padx=10, pady=(30, 0), sticky='w')

        self.widget_select = ctk.CTkOptionMenu(self, corner_radius=0, values=self.data)
        self.widget_select.grid(row=0, column=1, sticky='ew', padx=(10, 50), pady=(30, 0))

        # Row widgets
        self.width_label = ctk.CTkLabel(self, text='Widget width 1 - 3:')
        self.width_label.grid(row=1, column=0, padx=10, pady=(20, 0), sticky='w')

        self.width_entry = ctk.CTkEntry(self, border_width=1, corner_radius=0, fg_color='transparent', validate="key",
                                      validatecommand=(self.validate_cmd, "%P"))
        self.width_entry.grid(row=1, column=1, sticky='ew', padx=(10, 50), pady=(20, 0))

        # Col widgets
        self.height_label = ctk.CTkLabel(self, text='Widget height 1 - 3:')
        self.height_label.grid(row=2, column=0, padx=10, pady=(20, 0), sticky='w')

        self.height_entry = ctk.CTkEntry(self, border_width=1, corner_radius=0, fg_color='transparent', validate="key",
                                         validatecommand=(self.validate_cmd, "%P"))
        self.height_entry.grid(row=2, column=1, sticky='ew', padx=(10, 50), pady=(20, 0))

        # utility buttons

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    @staticmethod
    def validate_input(value):
        """ Only allow numbers between 1 and 3 """
        if value == "":
            return True
        if value.isdigit():
            num = int(value)
            return 1 <= num <= 3
        return False

    def ok_press(self):
        if self.width_entry.get() and self.height_entry.get():
            self.callback(int(self.width_entry.get()), int(self.height_entry.get()), self.widget_select.get())
            self.pop_up_instance.destroy()
        else:
            pass

    def cancel_press(self):
        self.callback(-1, -1, -1)
        self.pop_up_instance.destroy()


class ImportTable(WorkArea):
    def __init__(self, master, callback, popup_instance, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         **kwargs)

        self.validate_cmd = self.register(self.on_validate_input)

        # Grid configure
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Save as
        self.name_label = ctk.CTkLabel(self, text='Save As:')
        self.name_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='e')

        self.name_entry = ctk.CTkEntry(self, border_width=1, corner_radius=0, fg_color='transparent', validate="key")
        self.name_entry.grid(row=0, column=1, sticky='ew', padx=(10, 50), pady=(10, 0))

        self.name_entry.configure(validate="key", validatecommand=(self.validate_cmd, "%S"))

        # File select
        self.path_label = ctk.CTkLabel(self, text='Select File:')
        self.path_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky='e')

        self.path_entry = ctk.CTkEntry(self, border_width=1, corner_radius=0, fg_color='transparent', validate="key",
                                         placeholder_text="Select File")
        self.path_entry.grid(row=1, column=1, sticky='ew', padx=(10, 80), pady=(10, 0))


        self.add_button = DarkAddButton(self, command=self.file_select)
        self.add_button.grid(row=1, column=1, padx=(0, 50), pady=(10, 0), sticky="e")

        self.table_label = ctk.CTkLabel(self, text='Table:')
        self.table_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky='e')

        self.table_option_menu = DataOptionMenu(self, corner_radius=0)
        self.table_option_menu.grid(row=2, column=1, padx=(10, 50), pady=(10, 0), sticky="ew")

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    def ok_press(self):
        self.callback(self.name_entry.get(), self.path_entry.get(), self.table_option_menu.get())
        self.pop_up_instance.destroy()

    def cancel_press(self):
        self.pop_up_instance.destroy()

    def file_select(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("All Files", "*.*"),
            ("CSV Files", "*.csv"),
            ("Excel Files", "*.xlsx *.xls"),
            ("SQLite Files", "*.db *.sqlite"),
            ("SQL Files", "*.sql")
        ])

        # Validate selection
        if file_path:
            data_import.import_data(file_path, TEMP_PATH)
            tables = data_import.get_tables(TEMP_PATH)
            data_import.delete_all_tables(TEMP_PATH)

            self.table_option_menu.refresh_values(tables)
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, file_path)
        else:
            messagebox.showwarning("Warning", "No file selected! Please select a valid database file.")

    @staticmethod
    def validate_input(char, current_text):
        """ Dont allow invalid characters. """
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

        if char not in valid_chars:
            return False

        # Ensure the first character is not a number
        if char.isdigit() and len(current_text) == 0:
            return False

        return True

    def on_validate_input(self, p):
        """ Wrapper function to integrate with CTkEntry validation. """
        print(p, self.path_entry.get())
        return self.validate_input(p, self.name_entry.get())


class RemoveTable(WorkArea):
    def __init__(self, master, callback, popup_instance, data, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         **kwargs)

        self.master = master

        self.table_to_delete = None

        self.options = []


        self.tables = data

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.label = ctk.CTkLabel(self, text="Table to delete: ")
        self.label.grid(row=0, column=0)

        self.option_menu = ctk.CTkOptionMenu(self, values=self.tables)
        self.option_menu.grid(row=0, column=1)

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    def ok_press(self):
        self.table_to_delete = self.option_menu.get()
        self.callback(self.table_to_delete)
        self.pop_up_instance.destroy()

    def cancel_press(self):
        self.pop_up_instance.destroy()


class RemoveInstruction(WorkArea):
    def __init__(self, master, callback, popup_instance, data, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         data,
                         **kwargs)

        self.master = master

        self.instruction_to_delete = None

        self.instructions = []

        for instruction in data:
            self.instructions.append(instruction)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.label = ctk.CTkLabel(self, text="Instruction to delete: ")
        self.label.grid(row=0, column=0)

        self.option_menu = ctk.CTkOptionMenu(self, values=self.instructions)
        self.option_menu.grid(row=0, column=1)

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    def ok_press(self):
        self.instruction_to_delete = self.option_menu.get()
        self.callback(self.instruction_to_delete)
        self.pop_up_instance.destroy()

    def cancel_press(self):
        self.pop_up_instance.destroy()


class LoadInstruction(WorkArea):
    def __init__(self, master, callback, popup_instance, data, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         data,
                         **kwargs)

        self.master = master

        self.instructions = []

        for instruction in data:
            self.instructions.append(instruction)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.label = ctk.CTkLabel(self, text="Load instruction: ")
        self.label.grid(row=0, column=0)

        self.option_menu = ctk.CTkOptionMenu(self, values=self.instructions)
        self.option_menu.grid(row=0, column=1)

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    def ok_press(self):
        name = self.option_menu.get()
        self.callback(name)
        self.pop_up_instance.destroy()

    def cancel_press(self):
        self.pop_up_instance.destroy()


class TableJoin(WorkArea):
    def __init__(self, master, callback, popup_instance, data, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         data,
                         **kwargs)

        self.master = master

        self.instructions = []

        for instruction in data:
            self.instructions.append(instruction)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.label = ctk.CTkLabel(self, text="Select Instruction: ")
        self.label.grid(row=0, column=0)

        self.option_menu = ctk.CTkOptionMenu(self, values=self.instructions)
        self.option_menu.grid(row=0, column=1)

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    def ok_press(self):
        name = self.option_menu.get()
        self.callback(name)
        self.pop_up_instance.destroy()

    def cancel_press(self):
        self.pop_up_instance.destroy()


class SaveJoin(WorkArea):
    def __init__(self, master, callback, popup_instance, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         **kwargs)

        self.master = master

        self.tables = self.pop_up_instance.master.join_tables

        self.path = DB_PATH

        self.columns = []

        self.checkbox_vars = {}

        self.selected_columns = []

        print(self.tables)

        # Grid Configure
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.name_label = ctk.CTkLabel(self, text='Name:')
        self.name_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='w')

        self.name_entry = ctk.CTkEntry(self, border_width=1, corner_radius=0, fg_color='transparent', placeholder_text="Template Name")
        self.name_entry.grid(row=0, column=1, sticky='ew', padx=(10, 50), pady=(10, 0))

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="gray")
        self.scroll_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nsew")

        self.tables.sort()
        self.get_column_names()
        print(self.columns)

        for col in self.columns:
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(self.scroll_frame, text=col, variable=var)
            checkbox.pack(anchor="w", padx=10, pady=2)
            self.checkbox_vars[col] = var

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    def ok_press(self):
        selected = [col for col, var in self.checkbox_vars.items() if var.get()]

        if self.name_entry.get() and selected:
            self.callback(self.name_entry.get(), selected)
            self.pop_up_instance.destroy()

    def cancel_press(self):
        self.pop_up_instance.destroy()

    def get_column_names(self):
        for table in self.tables:
            cols = data_import.get_columns(self.path, table)
            for c in cols:
                table_column = f"{table}/{c}"
                self.columns.append(table_column)


class FreightCreate(WorkArea):
    def __init__(self, master, callback, popup_instance, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         **kwargs)

        self.master = master

        self.material_rows = []

        self.materials = []

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.rowconfigure(5, weight=0)
        self.rowconfigure(6, weight=0)
        self.rowconfigure(7, weight=0)
        self.rowconfigure(8, weight=1)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.pady = 10

    # ------------------------------------------------------------------------------------------------------------------
        self.from_label = ctk.CTkLabel(self, text="From: ", font=get_font())
        self.from_label.grid(row=0, column=0, sticky="wn", padx=20, pady=self.pady)

        self.from_location_label = ctk.CTkLabel(self, text="From Location:")
        self.from_location_label.grid(row=0, column=1, sticky="en", padx=20, pady=self.pady)

        self.from_location_entry = ctk.CTkEntry(self, placeholder_text="Location ID")
        self.from_location_entry.grid(row=0, column=2, sticky="wn", padx=20, pady=self.pady)

        self.from_warehouse_label = ctk.CTkLabel(self, text="From Warehouse:")
        self.from_warehouse_label.grid(row=1, column=1, sticky="en", padx=20, pady=self.pady)

        self.from_warehouse_entry = ctk.CTkEntry(self, placeholder_text="Warehouse ID")
        self.from_warehouse_entry.grid(row=1, column=2, sticky="nw", padx=20, pady=self.pady)

        self.pickup_date_label = ctk.CTkLabel(self, text="Pickup Date:")
        self.pickup_date_label.grid(row=2, column=1, sticky="en", padx=20, pady=self.pady)

        self.pickup_date_entry = ctk.CTkEntry(self, placeholder_text="dd/mm/yyyy")
        self.pickup_date_entry.grid(row=2, column=2, sticky="nw", padx=20, pady=self.pady)

        # Contact

        self.from_name_label = ctk.CTkLabel(self, text="Responsible Person:")
        self.from_name_label.grid(row=0, column=3, sticky="en", padx=20, pady=self.pady)

        self.from_name_entry = ctk.CTkEntry(self, placeholder_text="Name")
        self.from_name_entry.grid(row=0, column=4, sticky="wn", padx=20, pady=self.pady)

        self.from_email_label = ctk.CTkLabel(self, text="Email Address:")
        self.from_email_label.grid(row=1, column=3, sticky="en", padx=20, pady=self.pady)

        self.from_email_entry = ctk.CTkEntry(self, placeholder_text="example@email.com")
        self.from_email_entry.grid(row=1, column=4, sticky="wn", padx=20, pady=self.pady)

        self.from_phone_label = ctk.CTkLabel(self, text="Phone Number:")
        self.from_phone_label.grid(row=2, column=3, sticky="en", padx=20, pady=self.pady)

        self.from_phone_entry = ctk.CTkEntry(self, placeholder_text="Phone Number")
        self.from_phone_entry.grid(row=2, column=4, sticky="wn", padx=20, pady=self.pady)


        # ------------------------------------------------------------------------------------------------------------------


        self.to_label = ctk.CTkLabel(self, text="To: ", font=get_font())
        self.to_label.grid(row=3, column=0, sticky="wn", padx=20, pady=self.pady)

        self.from_location_label = ctk.CTkLabel(self, text="To Location:")
        self.from_location_label.grid(row=3, column=1, sticky="en", padx=20, pady=self.pady)

        self.to_location_entry = ctk.CTkEntry(self, placeholder_text="Location ID")
        self.to_location_entry.grid(row=3, column=2, sticky="nw", padx=20, pady=self.pady)

        self.to_warehouse_label = ctk.CTkLabel(self, text="To Warehouse:")
        self.to_warehouse_label.grid(row=4, column=1, sticky="en", padx=20, pady=self.pady)

        self.to_warehouse_entry = ctk.CTkEntry(self, placeholder_text="Warehouse ID")
        self.to_warehouse_entry.grid(row=4, column=2, sticky="nw", padx=20, pady=self.pady)

        self.delivery_date_label = ctk.CTkLabel(self, text="Delivery Date:")
        self.delivery_date_label.grid(row=5, column=1, sticky="en", padx=20, pady=self.pady)

        self.delivery_date_entry = ctk.CTkEntry(self, placeholder_text="dd/mm/yyyy")
        self.delivery_date_entry.grid(row=5, column=2, sticky="nw", padx=20, pady=self.pady)

        # Contact

        self.to_name_label = ctk.CTkLabel(self, text="Responsible Person:")
        self.to_name_label.grid(row=3, column=3, sticky="en", padx=20, pady=self.pady)

        self.to_name_entry = ctk.CTkEntry(self, placeholder_text="Name")
        self.to_name_entry.grid(row=3, column=4, sticky="wn", padx=20, pady=self.pady)

        self.to_email_label = ctk.CTkLabel(self, text="Email Address:")
        self.to_email_label.grid(row=4, column=3, sticky="en", padx=20, pady=self.pady)

        self.to_email_entry = ctk.CTkEntry(self, placeholder_text="example@email.com")
        self.to_email_entry.grid(row=4, column=4, sticky="wn", padx=20, pady=self.pady)

        self.to_phone_label = ctk.CTkLabel(self, text="Phone Number:")
        self.to_phone_label.grid(row=5, column=3, sticky="en", padx=20, pady=self.pady)

        self.to_phone_entry = ctk.CTkEntry(self, placeholder_text="Phone Number")
        self.to_phone_entry.grid(row=5, column=4, sticky="wn", padx=20, pady=self.pady)

        # ------------------------------------------------------------------------------------------------------------------

        self.materials_label = ctk.CTkLabel(self, text="Materials:", font=get_font())
        self.materials_label.grid(row=6, column=0, sticky="wn", padx=20, pady=self.pady)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="#444444")
        self.scrollable_frame.grid(row=6, column=1, columnspan=4, sticky="nsew", padx=10, pady=self.pady)

        self.add_button = DarkAddButton(self, command=self.add_material_row)
        self.add_button.grid(row=6, column=0)

        # ------------------------------------------------------------------------------------------------------------------

        self.comment_label = ctk.CTkLabel(self, text="Comment:", font=get_font())
        self.comment_label.grid(row=7, column=0, sticky="wn", padx=20, pady=self.pady)

        self.comment_entry = ctk.CTkEntry(self)
        self.comment_entry.grid(row=7, column=1, columnspan=4, sticky="nsew", padx=10, pady=self.pady)

        # ------------------------------------------------------------------------------------------------------------------

        self.priority_label = ctk.CTkLabel(self, text="Priority:")
        self.priority_label.grid(row=8, column=1, sticky="e", padx=20, pady=self.pady)

        self.priority_entry = ctk.CTkComboBox(self, values=["Standard", "Priority", "Right on Time"])
        self.priority_entry.grid(row=8, column=2, sticky="w", padx=20, pady=self.pady)

        # ------------------------------------------------------------------------------------------------------------------

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=9, column=0, columnspan=5, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    def ok_press(self):
        # Update materials
        self.get_materials()

        # Create Freight Data
        freight_data = {
            "from_location": self.from_location_entry.get(),
            "to_location": self.to_location_entry.get(),
            "from_warehouse": self.from_warehouse_entry.get(),
            "to_warehouse": self.to_warehouse_entry.get(),
            "pickup_date": self.pickup_date_entry.get(),
            "delivery_date": self.delivery_date_entry.get(),
            "priority": self.priority_entry.get(),
            "comment": self.comment_entry.get(),

            "contacts": [
                {"name": self.from_name_entry.get(), "email": self.from_email_entry.get(),
                 "phone": self.from_phone_entry.get()},
                {"name": self.to_name_entry.get(), "email": self.to_email_entry.get(),
                 "phone": self.to_phone_entry.get()}
            ],

            "packages": self.materials
        }

        conn = sqlite3.connect(FREIGHT_PATH)
        create_freight_record(conn, freight_data)
        conn.close()
        self.pop_up_instance.destroy()

    def cancel_press(self):
        self.pop_up_instance.destroy()

    def add_material_row(self):
        row_frame = ctk.CTkFrame(self.scrollable_frame)
        row_frame.pack(pady=5, fill="x")

        mat_id_entry = ctk.CTkEntry(row_frame, placeholder_text="Material ID")
        mat_id_b_entry = ctk.CTkEntry(row_frame, placeholder_text="Material ID B")
        qty_entry = ctk.CTkEntry(row_frame, placeholder_text="Quantity")

        mat_id_entry.pack(side="left", padx=5, expand=True)
        mat_id_b_entry.pack(side="left", padx=5, expand=True)
        qty_entry.pack(side="left", padx=5, expand=True)

        remove_btn = ctk.CTkButton(row_frame, text="✖", width=30, command=lambda: self.remove_material_row(row_frame))
        remove_btn.pack(side="left", padx=5)

        self.material_rows.append({
            "frame": row_frame,
            "mat_id": mat_id_entry,
            "mat_id_b": mat_id_b_entry,
            "qty": qty_entry
        })

    def remove_material_row(self, row_frame):
        for row in self.material_rows:
            if row["frame"] == row_frame:
                row_frame.destroy()
                self.material_rows.remove(row)
                break

    def get_materials(self):
        for row in self.material_rows:
            mat_id = row["mat_id"].get()
            mat_id_b = row["mat_id_b"].get()
            qty = row["qty"].get()
            if mat_id and qty:
                self.materials.append({
                    "mat_id": mat_id,
                    "mat_id_b": mat_id_b,
                    "qty": qty
                })


class FreightEdit(WorkArea):
    def __init__(self, master, callback, popup_instance, data, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         **kwargs)

        self.master = master

        self.data = data

        self.rowconfigure(0, weight=1)

        self.option = ctk.CTkOptionMenu(self, values=["Live", "Ready", "In Transit", "Delivered"])
        self.option.grid(row=0, column=0, columnspan=2, padx=20, pady=10)

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    def ok_press(self):
        value = self.option.get()
        self.callback(self.data, value)
        self.pop_up_instance.destroy()


    def cancel_press(self):
        self.pop_up_instance.destroy()


class AnalysisSelect(WorkArea):
    def __init__(self, master, callback, popup_instance, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         **kwargs)

        self.master = master

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)


        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.name_label = ctk.CTkLabel(self, text="Save as:")
        self.name_label.grid(row=0, column=0, padx=10, pady=10)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Name", width=200)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        self.type_label = ctk.CTkLabel(self, text="Type: ")
        self.type_label.grid(row=1, column=0)

        self.type_entry = ctk.CTkOptionMenu(self, values=["-", "Graph", "Top 5 Inventory cost", "Inventory Turnover Ratio", "Backlog"], width=200)
        self.type_entry.grid(row=1, column=1, padx=10)

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    def ok_press(self):
        if self.name_entry.get():
            name = self.name_entry.get()
            graph_type = self.type_entry.get()
            print(name, graph_type)
            self.callback(name, graph_type)
            self.pop_up_instance.destroy()

    def cancel_press(self):
        self.pop_up_instance.destroy()


class RemoveGraph(WorkArea):
    def __init__(self, master, callback, popup_instance, data, **kwargs):
        super().__init__(master,
                         callback,
                         popup_instance,
                         data,
                         **kwargs)

        self.master = master

        self.graph_to_delete = None

        self.graphs = data

        # for instruction in data:
        #     self.instructions.append(instruction)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.label = ctk.CTkLabel(self, text="Graph to delete: ")
        self.label.grid(row=0, column=0)

        self.option_menu = ctk.CTkOptionMenu(self, values=self.graphs)
        self.option_menu.grid(row=0, column=1)

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_ok = TransparentButton(self.button_frame, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=0, column=0, sticky='s', padx=30)

        self.button_cancel = TransparentButton(self.button_frame, text='Cancel', border_width=1,
                                               command=self.cancel_press)
        self.button_cancel.grid(row=0, column=1, sticky='s', padx=30)

    def ok_press(self):
        self.graph_to_delete = self.option_menu.get()
        self.callback(self.graph_to_delete)
        self.pop_up_instance.destroy()

    def cancel_press(self):
        self.pop_up_instance.destroy()

if __name__ == '__main__':
    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.geometry('400x400')
    root.title('test')


    def on_press():
        # pop_up = MovablePopUp(root, StepSelect, 'Create Step')

        MovablePopUp(master=root, work_area=RemoveGraph, title="Create Graph")

    def n():
        pass


    button = ctk.CTkButton(root, command=on_press)
    button.pack()

    root.mainloop()
