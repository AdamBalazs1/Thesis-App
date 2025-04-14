from tkinter import filedialog, messagebox

import customtkinter as ctk
import tksheet
from CTkListbox import *

from tools.styles import DarkButton, get_font
import tools.data_import as data_import


# Frames


class NavigationMenu(ctk.CTkFrame):
    """Main Navigation Menu Container for storing Menu Buttons"""
    def __init__(self, parent, menu_items: list, switch_callback):
        super().__init__(parent, width=200, corner_radius=0)
        self.switch_callback = switch_callback
        self.buttons = []
        self.menu_items = menu_items
        self.selected_button = None  # Track selected button

        self.create_menu()

    def create_menu(self, font=get_font()):
        """Create and store buttons"""
        frame = ctk.CTkFrame(self, height=50, fg_color='transparent', corner_radius=0)
        frame.pack_propagate(False)
        frame.pack()

        ctk.CTkLabel(frame, text='Menu', font=font).pack(pady=10, padx=10)

        for i in range(0, len(self.menu_items)):
            self.buttons.append(MenuButton(self, self.menu_items[i], self.on_button_click))

    def select_default_button(self):
        if self.buttons:
            self.on_button_click(self.buttons[0])

    def on_button_click(self, clicked_button):
        """ Handles button selection, ensures only one button is highlighted. """
        if self.selected_button:
            self.selected_button.highlight(False)

        self.selected_button = clicked_button
        self.selected_button.highlight(True)

        self.switch_callback(clicked_button.cget("text"))


class HeaderFrame(ctk.CTkFrame):
    def __init__(self, master, title, font=get_font(), **kwargs):
        super().__init__(master,
                         height=60,
                         **kwargs)

        self.grid_propagate(False)
        self.label = None
        self.utility_frame = None
        self.title = title
        self.font = font

        # Grid Configure
        self.grid(row=0, column=1, sticky='ew', padx=10, pady=(10, 0))

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Widgets
        self.create_label()
        self.create_utility_frame()

    def create_label(self):
        self.label = ctk.CTkLabel(self, text=self.title, font=self.font)
        self.label.grid(row=0, column=0, sticky='w', padx=20)

    def create_utility_frame(self):
        self.utility_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.utility_frame.grid(row=0, column=1, pady=10, padx=10)

        # Grid Configure - In case you use one widget column span = 2
        self.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)


class SideFrame(ctk.CTkFrame):
    def __init__(self, master, title, width=200, **kwargs):
        super().__init__(master,
                         width=width,
                         **kwargs)

        self.grid_propagate(False)

        self.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(10, 0), pady=10)

        # Configure Grid
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(self, text=title, font=get_font())
        self.title.grid(row=0, column=0, pady=16)


class AnalysisSideMenu(SideFrame):
    def __init__(self, master, title, list_callback, add_callback, remove_callback, **kwargs):
        super().__init__(master,
                         title,
                         **kwargs)

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        # Configure Grid
        self.button_frame.rowconfigure(0, weight=0)
        self.button_frame.columnconfigure(0, weight=0)

        # Configure Buttons
        self.add_button = DarkAddButton(self.button_frame, command=add_callback)
        self.add_button.grid(row=0, column=0, padx=(0, 10))

        self.remove_button = DarkRemoveButton(self.button_frame, command=remove_callback)
        self.remove_button.grid(row=0, column=1)

        # Configure Listbox
        self.listbox = CTkListbox(self, command=list_callback)
        self.listbox.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)


class DataSideMenu(SideFrame):
    def __init__(self, master, title, add_callback, remove_callback, list_callback, **kwargs):
        super().__init__(master,
                         title,
                         **kwargs)

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        # Configure Grid
        self.button_frame.rowconfigure(0, weight=0)
        self.button_frame.columnconfigure(0, weight=0)

        # Configure Buttons
        self.add_button = DarkAddButton(self.button_frame, command=add_callback)
        self.add_button.grid(row=0, column=0, padx=(0, 10))

        self.remove_button = DarkRemoveButton(self.button_frame, command=remove_callback)
        self.remove_button.grid(row=0, column=1)

        # Configure Listbox
        self.listbox = CTkListbox(self, command=list_callback)
        self.listbox.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)


# Buttons


class MenuButton(ctk.CTkButton):
    """Main Menu Button for selecting tabs"""
    def __init__(self, parent, text, click_callback, **kwargs):
        super().__init__(parent,
                         text=text,
                         fg_color="transparent",
                         command=self.on_click,
                         **kwargs)
        self.click_callback = click_callback
        self.is_selected = False
        self.pack(fill="x", padx=5, pady=5)

    def on_click(self):
        """Handles button click and notifies the menu"""
        self.click_callback(self)

    def highlight(self, selected=True):
        """Change button color based on selection state"""
        self.is_selected = selected
        self.configure(fg_color="gray" if selected else "transparent")


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


class DarkAddButton(DarkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         width=30,
                         height=30,
                         text='+',
                         **kwargs)


class DarkRemoveButton(DarkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         width=30,
                         height=30,
                         text='-',
                         **kwargs)


# Option Menus


class DataOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, values=["Select a table"], **kwargs)

    def refresh_values(self, new_values):
        if new_values:
            self.configure(values=new_values)
        else:
            self.configure(values=["Select a table"])
        self.set("Select a table")


class TableOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, master, database, **kwargs):
        super().__init__(master, values=["Select a table"], **kwargs, command=self.refresh_connection_values)

        self.master = master

        self.widget = None

        self.database = database


    def refresh_values(self, new_values):
        if new_values:
            self.configure(values=new_values)
        else:
            self.configure(values=["Select a table"])
        self.set("Select a table")

    def set_connection(self, widget):
        self.widget = widget

    def refresh_connection_values(self, table):
        print(table)
        columns = data_import.get_columns(self.database, table)
        print(columns)
        self.widget.configure(values=columns)


class ColumnOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, values=["Select a column"], **kwargs)

    def refresh_values(self, new_values):
        if new_values:
            self.configure(values=new_values)
        else:
            self.configure(values=["Select a column"])
        self.set("Select a column")


class JoinTypeOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, parent, values, **kwargs):
        super().__init__(parent, **kwargs)

        self.values = values
        self.set(values[0])


        self.configure(values=self.values)
