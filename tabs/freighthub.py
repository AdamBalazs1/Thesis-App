import sqlite3
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

from tools.freighttool import filter_freights, delete_freight_record, update_freight_status, auto_archive
from tools.moveablepopup import MovablePopUp, FreightCreate, FreightEdit
from tools.widgets import HeaderFrame, SideFrame, DarkAddButton, DarkRemoveButton, DarkButton


BASE_DIR = Path(__file__).resolve().parent.parent
FREIGHT_PATH = BASE_DIR / "databases" / "freight.db"


class FreightHubBaseFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         fg_color='transparent',
                         **kwargs)

        self.master = master

        # configure grid
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=2)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Widgets

        # Side Menu Frame
        self.filter_frame = FilterSideFrame(self, 'Filter Settings', self.display_data_connector)

        # Header Frame
        self.header_frame = HeaderFrame(self, 'Freight Hub')

        self.utility_frame = self.header_frame.utility_frame

        self.add_button = DarkAddButton(self.utility_frame, command=self.add_on_press)
        self.add_button.grid(row=0, column=0, padx=5)

        self.remove_button = DarkRemoveButton(self.utility_frame, command=self.remove_on_press)
        self.remove_button.grid(row=0, column=1, padx=5)

        self.edit_button = DarkButton(self.utility_frame, text="Edit", width=50, command=self.edit_on_press)
        self.edit_button.grid(row=0, column=2, padx=5)

        # Content Frame
        self.content_frame = FreightContentFrame(self)
        self.content_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)

        self.filter_frame.apply_filters()

    def add_on_press(self):
        """ Opens a new window that prompts the user to create a new freight. """
        MovablePopUp(master=self, work_area=FreightCreate, title="Create Delivery", geometry="800x800")

    def remove_on_press(self):
        """ Allows the user to select an existing freight and remove it if possible. """
        for frame in self.content_frame.frames:
            if frame.select_box.get() == 1:
                conn = sqlite3.connect(FREIGHT_PATH)
                delete_freight_record(conn, frame.id)
                print(frame.id)
                self.filter_frame.apply_filters()


    def edit_on_press(self):
        x = 0
        unique_id = ""

        for frame in self.content_frame.frames:
            if frame.select_box.get() == 1:
                unique_id = frame.id
                x += 1
        if x == 0:
            messagebox.showwarning("Warning", "No table selected!")
        elif x > 1:
            messagebox.showwarning("Warning", "More than one table selected!")
        else:
            MovablePopUp(self, work_area=FreightEdit, callback=self.edit_on_ok, title="Change Transport Status", data=unique_id)

        self.filter_frame.apply_filters()

    def edit_on_ok(self, unique_id, value):
        conn = sqlite3.connect(FREIGHT_PATH)
        update_freight_status(conn, unique_id, value)
        auto_archive(conn)
        self.filter_frame.apply_filters()
        conn.close()

    def display_data_connector(self, filters):

        print(filters)
        conn = sqlite3.connect(FREIGHT_PATH)

        rows = filter_freights(conn, filters)

        conn.close()

        print(rows)

        self.content_frame.load_data(rows)

class FilterSideFrame(SideFrame):
    def __init__(self, master, title, apply_callback, **kwargs):
        super().__init__(master,
                         title,
                         **kwargs)

        self.apply_callback = apply_callback

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)

        self.apply_button = DarkButton(self.button_frame, text='Apply Filter', command=self.apply_filters)
        self.apply_button.grid(row=0, column=0, sticky='ew')
        #
        self.reset_button = DarkButton(self.button_frame, text='Reset Filter', command=self.reset_filters)
        self.reset_button.grid(row=1, column=0, sticky='ew', pady=(10, 0))

        self.settings_frame = SettingsFrame(self)
        self.settings_frame.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

        self.settings_frame.pack_propagate(False)

        self.create_filter_widgets()

    def create_filter_widgets(self):
        self.status_label = ctk.CTkLabel(self.settings_frame, text="Status:")
        self.status_label.pack(fill="x", padx=10, pady=(5, 0))

        self.status_live_var = ctk.BooleanVar(value=True)
        self.status_archived_var = ctk.BooleanVar(value=False)

        self.status_checkbox_live = ctk.CTkCheckBox(self.settings_frame, text="Live", variable=self.status_live_var,
                                                    command=self.on_status_checkbox_change)
        self.status_checkbox_live.pack(padx=10, pady=5)

        self.status_checkbox_archived = ctk.CTkCheckBox(self.settings_frame, text="Archived",
                                                        variable=self.status_archived_var,
                                                        command=self.on_status_checkbox_change)
        self.status_checkbox_archived.pack(padx=10, pady=5)

        # --------------------------------------------------------------------------------------------------------------

        self.unique_id_label = ctk.CTkLabel(self.settings_frame, text="Unique ID:")
        self.unique_id_label.pack(fill="x", padx=10, pady=(5, 0))

        self.unique_id_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="Unique ID")
        self.unique_id_entry.pack(fill="x", padx=10, pady=(5, 0))

        # --------------------------------------------------------------------------------------------------------------

        self.delivery_from_label = ctk.CTkLabel(self.settings_frame, text="Delivery From:")
        self.delivery_from_label.pack(fill="x", padx=10, pady=(5, 0))

        self.delivery_from_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="Delivery From")
        self.delivery_from_entry.pack(fill="x", padx=10, pady=(5, 0))

        # --------------------------------------------------------------------------------------------------------------

        self.delivery_to_label = ctk.CTkLabel(self.settings_frame, text="Delivery To:")
        self.delivery_to_label.pack(fill="x", padx=10, pady=5)

        self.delivery_to_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="Delivery To")
        self.delivery_to_entry.pack(fill="x", padx=10, pady=5)

        # --------------------------------------------------------------------------------------------------------------

        self.priority_label = ctk.CTkLabel(self.settings_frame, text="Priority:")
        self.priority_label.pack(fill="x", padx=10, pady=5)

        self.priority_dropdown = ctk.CTkOptionMenu(self.settings_frame,
                                                   values=["-", "Standard", "Priority", "Right on Time"])
        self.priority_dropdown.pack(fill="x", padx=10, pady=5)

        self.transport_status_label = ctk.CTkLabel(self.settings_frame, text="Delivery Status:")
        self.transport_status_label.pack(fill="x", padx=10, pady=5)

        self.transport_status_dropdown = ctk.CTkOptionMenu(self.settings_frame,
                                                           values=["-", "Live", "Ready", "In Transit", "Delivered"])
        self.transport_status_dropdown.pack(fill="x", padx=10, pady=5)

        # --------------------------------------------------------------------------------------------------------------

        self.pickup_date_label = ctk.CTkLabel(self.settings_frame, text="Pickup Date:")
        self.pickup_date_label.pack(fill="x", padx=10, pady=5)

        self.pickup_date_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="dd/mm/yyyy")
        self.pickup_date_entry.pack(fill="x", padx=10, pady=5)

        self.delivery_date_label = ctk.CTkLabel(self.settings_frame, text="Delivery Date:")
        self.delivery_date_label.pack(fill="x", padx=10, pady=5)

        self.delivery_date_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="dd/mm/yyyy")
        self.delivery_date_entry.pack(fill="x", padx=10, pady=5)

        # --------------------------------------------------------------------------------------------------------------

    def apply_filters(self):
        filters = {}

        # Status checkboxes
        if self.status_live_var.get():
            filters["live_status"] = "Live"
        if self.status_archived_var.get():
            filters["archived_status"] = "Archived"

        # Unique ID
        unique_id = self.unique_id_entry.get().strip()
        if unique_id:
            filters["unique_id"] = unique_id

        # Delivery From
        delivery_from = self.delivery_from_entry.get().strip()
        if delivery_from:
            filters["from_location"] = delivery_from

        # Delivery To
        delivery_to = self.delivery_to_entry.get().strip()
        if delivery_to:
            filters["to_location"] = delivery_to

        # Priority
        priority = self.priority_dropdown.get()
        if priority in ["Standard", "Priority", "Right on Time"]:
            filters["priority"] = priority

        # Delivery Status
        transport_status = self.transport_status_dropdown.get()
        print(transport_status)
        if transport_status in ["Live", "Ready", "In Transit", "Delivered"]:
            filters["transport_status"] = transport_status

        # Pickup Date
        pickup_date = self.pickup_date_entry.get().strip()
        if pickup_date:
            filters["pickup_date"] = pickup_date

        # Delivery Date
        delivery_date = self.delivery_date_entry.get().strip()
        if delivery_date:
            filters["delivery_date"] = delivery_date

        self.apply_callback(filters)

    def on_status_checkbox_change(self):
        if not self.status_live_var.get() and not self.status_archived_var.get():
            # If both checkboxes are unchecked, recheck the Live checkbox by default
            self.status_live_var.set(True)

    def reset_filters(self):
        # Reset checkboxes
        self.status_live_var.set(True)
        self.status_archived_var.set(False)

        # Reset text entries
        self.unique_id_entry.delete(0, "end")
        self.delivery_from_entry.delete(0, "end")
        self.delivery_to_entry.delete(0, "end")
        self.pickup_date_entry.delete(0, "end")
        self.delivery_date_entry.delete(0, "end")

        # Reset dropdowns
        self.priority_dropdown.set("-")
        self.transport_status_dropdown.set("-")


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         **kwargs)

        self.filters = {}


class FreightContentFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         **kwargs)

        self.master = master

        self.frames = []

        self.columns = ["ID", "Status", "From", "To", "From Warehouse", "To Warehouse", "Pickup date",
                        "delivery date", "priority"]

        self.header = ctk.CTkFrame(self, height=50)
        self.header.pack(fill="x", padx=(10, 52), pady=5)

        self.data_frame = ctk.CTkScrollableFrame(self)
        self.data_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.data_frame.columnconfigure(0, weight=1)

        for index, col in enumerate(self.columns):
            self.header.columnconfigure(index, weight=1)

            column = ctk.CTkEntry(self.header, width=110, corner_radius=0)
            column.insert(0, col)
            column.configure(state="disabled")
            column.grid(row=0, column=index, sticky="ew")

    def load_data(self, rows):
        for i in range(len(self.frames) - 1, -1, -1):
            self.frames[i].destroy()
            del self.frames[i]

        for r_index, row in enumerate(rows):
            print(r_index)
            self.frames.append(ItemFrame(self.data_frame, row, r_index))
            print(self.frames)


class ItemFrame(ctk.CTkFrame):
    def __init__(self, master, data, row_index, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.row_index = row_index
        self.data = data
        self.id = data[0]
        self.columns = []

        self.grid(row=row_index, column=0, sticky="ew")

        self.create_columns()

        self.cb_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cb_frame.grid(row=0, column=10)
        self.select_box = ctk.CTkCheckBox(self.cb_frame, text="", width=10, corner_radius=0, border_width=1)
        self.select_box.pack(side="right")

    def create_columns(self):
        for index, item in enumerate(self.data):
            self.columnconfigure(index, weight=1)
            field = ctk.CTkEntry(self, corner_radius=0, width=110)
            field.insert(0, item)
            field.configure(state="disabled")
            field.grid(row=0, column=index, sticky="ew")

if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title('Test')
    root.geometry('1280x800')

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    base_frame = FreightHubBaseFrame(root)
    base_frame.grid(row=0, column=0, sticky='nsew')

    root.mainloop()
