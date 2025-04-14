import customtkinter as ctk
from pathlib import Path

from tools.appmanager import AppManager
from tools.moveablepopup import MovablePopUp, EditLayoutPopup, WidgetSize
from tools.plottool import PlotTool
from tools.widgets import HeaderFrame, DarkButton

from tkinter import messagebox

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "databases" / "imported_data.db"

class DashboardManager:
    def __init__(self, app_manager):
        self.app_manager = app_manager

        self.grid_size = ()
        self.occupied_cells = {}
        self.widgets = {}

        self.dashboard_rows = 1
        self.dashboard_columns = 1

        self.selected_widget = None

        self.selected_widget_row = 0
        self.selected_widget_col = 0

        self.selected_widget_row_span = 0
        self.selected_widget_col_span = 0

        self.graph_files = {}

        self.load_settings()


    def set_layout(self, geometry=(6, 6)):
        self.app_manager.set_setting("grid_dimensions", {"rows":geometry[0], "columns":geometry[1]})

    def set_occupied_cells(self):
        formatted_dict = {}
        for key, value in self.occupied_cells.items():
            formatted_dict[str(key)] = value

        self.app_manager.set_setting("occupied_cells", formatted_dict)

    def set_widgets(self):
        self.app_manager.set_setting("widgets", self.widgets)

    def set_graph_files(self):
        self.app_manager.set_setting("graph_files", self.widgets)

    # ------------------------------------------------------------------------------------------------------------------

    def save_widget(self, row, column, row_span, column_span, widget_type="Widget_type1"):
        # Add Widget to self.widgets
        widget_name = self.get_widget_name()
        widget_settings = {"row": row, "column": column, "row_span": row_span, "column_span": column_span,
                           "widget_type": widget_type}

        self.widgets[widget_name] = widget_settings

        # Save into JSON
        self.set_widgets()

    def add_occupied_cell(self, key, value):
        # Add occupied cell
        self.occupied_cells[key] = value

    def add_layout(self, geometry=(6, 6)):
        # Reset to default
        self.widgets = {}
        self.occupied_cells = {}

        self.set_widgets()
        self.set_occupied_cells()

        # Set new layout
        self.dashboard_rows, self.dashboard_columns = geometry

        # Save to JSON
        self.set_layout(geometry)

    # ------------------------------------------------------------------------------------------------------------------

    def get_widget_name(self):
        i = 1
        while f"widget_{i}" in self.widgets:
            i += 1
            if i > 40:
                break

        return "widget_{}".format(i)

    # ------------------------------------------------------------------------------------------------------------------

    def load_settings(self):
        settings = self.app_manager.settings

        # dashboard dimensions:
        if "grid_dimensions" in settings.keys():
            self.dashboard_rows, self.dashboard_columns = (settings['grid_dimensions'][key] for key in ("rows", "columns"))
        else:
            self.set_layout()

        if "occupied_cells" in settings.keys():
            for key, value in settings['occupied_cells'].items():
                self.occupied_cells[eval(key)] = value
        else:
            self.set_occupied_cells()

        if "widgets" in settings.keys():
            for key, value in settings['widgets'].items():
                self.widgets[key] = value
        else:
            self.set_widgets()

        if "graph_files" in settings.keys():
            for key, value in settings['graph_files'].items():
                self.graph_files[key] = value
        else:
            self.set_graph_files()

        print(self.graph_files)


class DashboardBaseFrame(ctk.CTkFrame):
    def __init__(self, master, app_manager, **kwargs):
        super().__init__(master,
                         fg_color='transparent',
                         **kwargs)

        self.master = master
        self.manager = DashboardManager(app_manager)
        self.popup = None

        self.grid(row=0, column=1, sticky='nsew')

        # configure grid
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=2)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Widgets
        self.header_frame = HeaderFrame(self, 'Dashboard')
        self.utility_frame = self.header_frame.utility_frame

        self.add_widget_button = DarkButton(self.utility_frame, text='Add Widget', command=self.add_on_press)
        self.add_widget_button.grid(row=0, column=0, padx=10, ipady=1)

        self.remove_widget_button = DarkButton(self.utility_frame, text='Remove Widget', command=self.remove_on_press)
        self.remove_widget_button.grid(row=0, column=1, padx=(0, 10), ipadx=2, ipady=1)

        self.edit_layout_button = DarkButton(self.utility_frame, text='Edit Layout', command=self.edit_layout_on_press)
        self.edit_layout_button.grid(row = 0, column=2)

        self.content_frame = DashBoardContentFrame(self, self.placeholder_callback, self.placeable_callback)
        self.content_frame.grid(column=1, row=1, sticky='nsew', padx=10, pady=10)

    def edit_layout_on_press(self):
        MovablePopUp(self, EditLayoutPopup, self.edit_layout_on_ok, title="Dashboard Geometry")

    def edit_layout_on_ok(self, geometry):
        # Save changes
        self.manager.add_layout(geometry)

        # Reload Frame
        self.content_frame.destroy()
        self.content_frame = DashBoardContentFrame(self, self.placeholder_callback, self.placeable_callback)
        self.content_frame.grid(column=1, row=1, sticky='nsew', padx=10, pady=10)

        # self.content_frame.create_layout()

    def add_on_press(self):
        self.content_frame.enable_placement_mode()

    def remove_on_press(self):
        self.content_frame.enable_remove_mode()

    def placeholder_callback(self, row, col):
        self.manager.selected_widget_row = row
        self.manager.selected_widget_col = col

        data = [key for key in self.manager.graph_files.keys()]

        MovablePopUp(self, WidgetSize, self.popup_callback, title="Widget Geometry", geometry="400x300", data=data)

    def placeable_callback(self, widget):
        pass
        self.manager.widgets.pop(widget.name, None)
        self.manager.set_widgets()

        for r in range(widget.row, widget.row + widget.row_span):
            for c in range(widget.col, widget.col + widget.col_span):
                if (r, c) in self.manager.occupied_cells.keys():
                    self.manager.occupied_cells.pop((r, c), None)

        self.manager.set_occupied_cells()

        widget.master.create_layout()


    def popup_callback(self, width, height, widget):
        print("Widget selected", widget)
        if width == -1:
            self.content_frame.create_layout()
        else:
            self.manager.selected_widget_row_span = height
            self.manager.selected_widget_col_span = width

            self.manager.selected_widget = widget

            self.content_frame.place_widget()


class DashBoardContentFrame(ctk.CTkFrame):
    def __init__(self, master, placeholder_callback, placeable_callback, **kwargs):
        super().__init__(master,
                         fg_color='transparent',
                         **kwargs)
        self.master = master
        self.manager = self.master.manager
        self.frames = []
        self.widgets = self.master.manager.widgets

        self.placeholder_callback = placeholder_callback
        self.placeable_callback = placeable_callback

        self.create_layout()

    def create_layout(self):
        dashboard_rows = self.master.manager.dashboard_rows
        dashboard_columns = self.master.manager.dashboard_columns

        self.delete_layout()

        # Configure grid
        for row in range(0, dashboard_rows):
            self.rowconfigure(row, weight=1)
            for column in range(0, dashboard_columns):
                self.columnconfigure(column, weight=1)

        # Create widgets
        for widget in self.widgets.keys():
            row, col, row_span, col_span, widget_type = self.widgets[widget].values()
            self.create_widget(row, col, row_span, col_span, widget, widget_type)

        # Create placeholders
        for row in range(0, dashboard_rows):
            for column in range(0, dashboard_columns):
                if (row, column) not in self.master.manager.occupied_cells:
                    self.frames.append(Placeholder(self, row, column, self.placeholder_callback))

    def enable_placement_mode(self):
        for frame in self.frames:
            if (frame.row, frame.col) not in self.master.manager.occupied_cells:
                frame.enable_selection()

    def enable_remove_mode(self):
        for frame in self.frames:
            if (frame.row, frame.col) in self.master.manager.occupied_cells:
                frame.enable_selection()

    def delete_layout(self):
        for widget in self.winfo_children():
            self.frames = []
            widget.destroy()

    def create_widget(self, row, col, row_span, col_span, name, widget_type=None):
        widget = PlaceableFrame(self, row, col, row_span, col_span, self.placeable_callback, name, widget_type, fg_color="blue")

        self.frames.append(widget)

    def place_widget(self):
        row = self.master.manager.selected_widget_row
        col = self.master.manager.selected_widget_col

        row_span = self.master.manager.selected_widget_row_span
        col_span = self.master.manager.selected_widget_col_span

        widget = self.master.manager.selected_widget

        occupied_cells = self.master.manager.occupied_cells

        # Check if cells are occupied
        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                if (r, c) in occupied_cells.keys() or r >= self.master.manager.dashboard_rows or c >= self.master.manager.dashboard_columns:
                    messagebox.showerror("Error", "Invalid placement!")
                    self.create_layout()
                    return

        # Mark cells as occupied
        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                self.master.manager.add_occupied_cell((r, c), True)

        self.master.manager.set_occupied_cells()

        # Place widget
        self.master.manager.save_widget(row, col, row_span, col_span, widget_type=widget)

        self.create_layout()


class Placeholder(ctk.CTkFrame):
    def __init__(self, master, row, column, callback, **kwargs):
        super().__init__(master,
                         **kwargs)

        self.bind("<Button-1>", self.on_click)
        self.active = False
        self.callback = callback
        self.row = row
        self.col = column

        self.grid(row=row, column=column, sticky='nsew', padx=5, pady=5)

    def enable_selection(self):
        self.configure(fg_color="lightgreen")
        self.active = True

    def on_click(self, event):
        if self.active:
            self.callback(self.row, self.col)
            self.configure(fg_color='blue')


class PlaceableFrame(ctk.CTkFrame):
    def __init__(self, master, row, column, row_span, col_span, callback, name, widget_type, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.manager = self.master.manager

        self.graph_files =self.manager.graph_files

        self.graph_type = widget_type

        self.path = str(DB_PATH)

        self.bind("<Button-1>", self.on_click)
        self.active = False

        self.name = name

        self.row = row
        self.col = column

        self.row_span = row_span
        self.col_span = col_span

        self.callback = callback


        self.plot = PlotTool(
            frame=self,
            db_path=self.path,
            instruction_dict=self.graph_files[self.graph_type]
        )
        self.plot.build()

        self.grid(row=row, column=column, sticky="nsew", padx=5, pady=5, rowspan=row_span, columnspan=col_span)

    def enable_selection(self):
        self.configure(fg_color="red")
        self.plot.destroy()
        self.active = True

    def on_click(self, event):
        if self.active:
            self.callback(self)
            self.master.create_layout()


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title('Test')
    root.geometry('1280x800')

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    base_frame = DashboardBaseFrame(root, AppManager())
    base_frame.grid(row=0, column=0, sticky='nsew')

    root.mainloop()
