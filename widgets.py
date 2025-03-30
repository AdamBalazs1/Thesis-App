import os
import sqlite3
from tkinter import filedialog, messagebox

import customtkinter as ctk
import tksheet
from CTkListbox import *

from styles import DarkButton


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

    def create_menu(self):
        """Create and store buttons"""
        frame = ctk.CTkFrame(self, height=50, fg_color='transparent', corner_radius=0)
        frame.pack_propagate(False)
        frame.pack()

        ctk.CTkLabel(frame, text='Menu', font=('Arial', 20)).pack(pady=10, padx=10)

        for item in self.menu_items:
            button = MenuButton(self, item, self.on_button_click)
            button.pack(fill="x", padx=5, pady=5)
            self.buttons.append(button)

    def select_default_button(self):
        if self.buttons:
            self.on_button_click(self.buttons[0])

    def on_button_click(self, clicked_button):
        """Handles button selection, ensures only one button is highlighted"""
        if self.selected_button:
            self.selected_button.highlight(False)  # Unselect previous button

        self.selected_button = clicked_button
        self.selected_button.highlight(True)  # Highlight new button

        self.switch_callback(clicked_button.cget("text"))  # Update content frame


class ContentFrame(ctk.CTkFrame):
    """Temporary implementation for menu tabs not yet implemented"""
    def __init__(self, parent, text: str):
        super().__init__(parent, corner_radius=0)
        self.text = text + ' Content'
        self.create_label()

    def create_label(self, font=('Arial', 20)):
        ctk.CTkLabel(self, text=self.text, font=font).pack(pady=10)


class DashboardFrame(ctk.CTkFrame):
    """Main dashboard container, holding the menu and widget area."""
    def __init__(self, parent):
        super().__init__(parent, fg_color='transparent')
        self.grid(row=0, column=1, sticky="nsew")

        # Configure layout
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Initialize Widget Container
        self.widget_container = WidgetContainer(self)
        self.widget_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Initialize Dashboard Menu
        self.menu = DashboardMenu(self, self.widget_container)
        self.menu.grid(row=0, column=0, sticky="new")


class DashboardMenu(ctk.CTkFrame):
    """Top menu bar inside the dashboard (for future buttons, title, etc.)."""
    def __init__(self, parent, widget_container):
        super().__init__(parent, height=50, corner_radius=0)
        self.pack_propagate(False)
        self.widget_container = widget_container

        ctk.CTkLabel(self, text="Dashboard", font=("Arial", 20)).pack(side='left', pady=10, padx=10)

        # Remove Widget Button
        self.remove_button = ctk.CTkButton(self, text="Remove Widget", command=self.remove_widget)
        self.remove_button.pack(side="right", padx=10)

        # Add Widget Button
        self.add_button = ctk.CTkButton(self, text="Add Widget", command=self.add_widget)
        self.add_button.pack(side="right", padx=10)



    def add_widget(self):
        """Calls the widget container's method to add a new widget."""
        self.widget_container.add_widget()

    def remove_widget(self):
        """Calls the widget container's method to remove the last added widget."""
        self.widget_container.remove_widget()


class WidgetContainer(ctk.CTkFrame):
    """Area where widgets will be placed dynamically."""
    def __init__(self, parent):
        super().__init__(parent, fg_color='transparent')
        self.pack_propagate(False)
        self.widgets = []

    def add_widget(self):
        """Adds a simple widget (e.g., a label) to the container."""
        new_widget = ctk.CTkLabel(self, text=f"Widget {len(self.widgets) + 1}", font=("Arial", 14))
        new_widget.pack(pady=5)
        self.widgets.append(new_widget)  # Store reference

    def remove_widget(self):
        """Removes the last added widget from the container."""
        if self.widgets:
            widget_to_remove = self.widgets.pop()  # Get the last widget
            widget_to_remove.destroy()  # Destroy the widget


class DataImportFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color='transparent')
        self.grid(row=0, column=1, sticky='nsew')


class SideMenuFrame(ctk.CTkFrame):
    def __init__(self, master, add_button, remove_button, on_select_callback, add_callback, remove_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_propagate(False)

        # Configure grid
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Callbacks
        # self.button_callback = button_callback
        self.on_select_callback = on_select_callback

        # Configure widgets
        self.menu_label = ctk.CTkLabel(self, text="Stored Files:", font=('Arial', 14, "bold"), anchor='w')
        self.menu_label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.button_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.button_frame.grid(column=0, row=1, padx=10, sticky="w")

        self.add_button = add_button(self.button_frame, command=add_callback, **kwargs)    # TODO dont forget this!!
        self.add_button.grid(column=0, row=0)

        self.remove_button = remove_button(self.button_frame, command=remove_callback, **kwargs)  # TODO dont forget this!!
        self.remove_button.grid(column=1, row=0, padx=5)

        self.listbox = CTkListbox(self, command=self.on_select)
        self.listbox.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)

    def on_select(self, selected_value):
        """ Callback to refresh the dropdown menu """
        self.on_select_callback(selected_value)


# Buttons


class MenuButton(ctk.CTkButton):
    """Main Menu Button for selecting tabs"""
    def __init__(self, parent, text, click_callback):
        super().__init__(parent, text=text, fg_color="transparent", command=self.on_click)
        self.click_callback = click_callback
        self.is_selected = False

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

    def select_file(self):      # TODO Change this so you can pass filetypes!!
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
