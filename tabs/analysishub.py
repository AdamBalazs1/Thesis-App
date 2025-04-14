import customtkinter as ctk
from pathlib import Path

from tools.moveablepopup import MovablePopUp, AnalysisSelect, RemoveGraph
from tools.styles import get_font
from tools.widgets import DarkButton, AnalysisSideMenu, HeaderFrame
import tools.data_import as data_import
from tkinter import messagebox
from tools.appmanager import AppManager

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "databases" / "imported_data.db"


class DataImportManager:
    def __init__(self):
        # App Manager
        self.app_manager = AppManager()

        self.graph_files = {}

        self.load_settings()

    def set_graph_files(self):
        self.app_manager.set_setting("graph_files", self.graph_files)

    def add_top5_file(self, name, table, mat_col, qty_col, cost_col):
        self.graph_files[name] = {
            "type": "top5_inventory_cost",
            "table": table,
            "columns": {
                "mat_id": mat_col,
                "qty": qty_col,
                "cost": cost_col
            }
        }
        self.set_graph_files()

    def add_itr_file(self, name, table, mm_col, cogs_col, aic_col):
        self.graph_files[name] = {
            "type": "inventory_turnover_ratio",
            "table": table,
            "columns": {
                "month": mm_col,
                "cogs": cogs_col,
                "aic": aic_col
            }
        }
        self.set_graph_files()

    def add_bl_file(self, name, table, pl_col, mm_col, bl_col):
        self.graph_files[name] = {
            "type": "backlog",
            "table": table,
            "columns": {
                "production line": pl_col,
                "month": mm_col,
                "backlog": bl_col
            }
        }
        self.set_graph_files()

    def add_graph(self, name, table, g_type, col_1, col_2, col_3):
        self.graph_files[name] = {
            "type": g_type,
            "table": table,
            "columns": {
                "col_1": col_1,
                "col_2": col_2,
                "col_3": col_3
            }
        }
        self.set_graph_files()

    def get_graph_names(self):
        print(self.graph_files)
        graph_names = []
        for key, value in self.graph_files.items():
            graph_names.append(key)

        return graph_names

    def remove_graph(self, graph):
        self.graph_files.pop(graph)
        self.set_graph_files()

    def load_settings(self):
        settings = self.app_manager.settings

        if "graph_files" in settings.keys():
            for key, value in settings['graph_files'].items():
                self.graph_files[key] = value
            else:
                self.set_graph_files()


class AnalysisHubBaseFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         fg_color='transparent',
                         **kwargs)

        self.manager = DataImportManager()
        self.master = master
        self.popup = None

        # Configure grid
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Widgets
        self.side_menu_frame = AnalysisSideMenu(self, 'Saved Files', self.listbox_on_select, self.add_file_on_press, self.remove_file_on_press)

        self.header_frame = HeaderFrame(self, 'Analytics Hub')

        self.utility_frame = self.header_frame.utility_frame

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(column=1, row=1, sticky='nsew', padx=10, pady=10)

        self.refresh_listbox()

    def listbox_on_select(self, event):
        if self.content_frame:
            self.content_frame.destroy()
        self.content_frame = None   # This is not needed??..

        data = self.manager.graph_files[event]
        g_type = data['type']
        table = data["table"]
        columns = data['columns']

        if g_type in ["Pie", "Bar", "Line"]:
            if columns['col_3'] == "":
                columns['col_3'] = "Select Sheet"


        if g_type == "Pie":
            self.content_frame = GraphFrame(self, "event")

            self.content_frame.graph_type_option.set(g_type)
            self.content_frame.on_type_select(g_type)
            self.content_frame.table_option.set(table)
            self.content_frame.on_select(table)
            self.content_frame.column_1_option.set(columns["col_1"])
            self.content_frame.column_2_option.set(columns["col_2"])
        elif g_type == "Bar":
            self.content_frame = GraphFrame(self, "event")

            self.content_frame.graph_type_option.set(g_type)
            self.content_frame.on_type_select(g_type)
            self.content_frame.table_option.set(table)
            self.content_frame.on_select(table)
            self.content_frame.column_1_option.set(columns["col_1"])
            self.content_frame.column_2_option.set(columns["col_2"])
            self.content_frame.column_3_option.set(columns["col_3"])

        elif g_type == "Line":
            self.content_frame = GraphFrame(self, "event")

            self.content_frame.graph_type_option.set(g_type)
            self.content_frame.on_type_select(g_type)
            self.content_frame.table_option.set(table)
            self.content_frame.on_select(table)
            self.content_frame.column_1_option.set(columns["col_1"])
            self.content_frame.column_2_option.set(columns["col_2"])
            self.content_frame.column_3_option.set(columns["col_3"])
        elif g_type == "top5_inventory_cost":
            self.content_frame = TopICFrame(self, "event")

            self.content_frame.table_option.set(table)
            self.content_frame.on_select(table)
            self.content_frame.id_option.set(columns["mat_id"])
            self.content_frame.qty_option.set(columns["qty"])
            self.content_frame.cost_option.set(columns["cost"])

        elif g_type == "inventory_turnover_ratio":
            self.content_frame = InvTRFrame(self, "event")

            self.content_frame.table_option.set(table)
            self.content_frame.on_select(table)
            self.content_frame.month_option.set(columns["month"])
            self.content_frame.cogs_option.set(columns["cogs"])
            self.content_frame.aic_option.set(columns["aic"])

        elif g_type == "backlog":
            self.content_frame = BacklogFrame(self, "event")

            self.content_frame.table_option.set(table)
            self.content_frame.on_select(table)
            self.content_frame.pl_option.set(columns["production line"])
            self.content_frame.month_option.set(columns["month"])
            self.content_frame.backlog_option.set(columns["backlog"])

        else:
            messagebox.showwarning("Warning", "Invalid type!")

    def add_file_on_press(self):
        MovablePopUp(master=self, work_area=AnalysisSelect, title="Create Graph", callback=self.add_file_on_ok)

    def add_file_on_ok(self, name, value):
        pass
        self.content_frame.destroy()
        if value in ["Graph", "Top 5 Inventory cost", "Inventory Turnover Ratio", "Backlog"]:
            if value == "Graph":
                self.content_frame = GraphFrame(self, name)
            elif value == "Top 5 Inventory cost":
                self.content_frame = TopICFrame(self, name)
            elif value == "Inventory Turnover Ratio":
                self.content_frame = InvTRFrame(self, name)
            elif value == "Backlog":
                self.content_frame = BacklogFrame(self, name)
        else:
            messagebox.showwarning("Warning", "No Type selected!")

    def remove_file_on_press(self):
        graph_names = self.manager.get_graph_names()
        MovablePopUp(self, RemoveGraph, self.remove_file_on_ok, title="Select File To Delete:", data=graph_names)

    def remove_file_on_ok(self, graph_to_delete):
        self.manager.remove_graph(graph_to_delete)
        self.refresh_listbox()

    def refresh_listbox(self):
        self.side_menu_frame.listbox.delete("all")
        for i, key in enumerate(self.manager.graph_files):
            self.side_menu_frame.listbox.insert(i, key)


class ContentFrame(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master,
                         **kwargs)

        self.grid(column=1, row=1, sticky='nsew', padx=10, pady=10)

        self.rowconfigure(0, weight=0)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        self.master = master
        self.title = title

        self.path = str(DB_PATH)

        self.tables = data_import.get_tables(self.path)

        self.title_label = ctk.CTkLabel(self, text=title, font=get_font())
        self.title_label.grid(row=0, column = 0, padx=20, pady=20, sticky="w")

        # Header Buttons

        self.utility_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.utility_frame.grid(row=0, column=2)

        self.cancel_button = DarkButton(self.utility_frame, text="Cancel", command=self.on_cancel)
        self.cancel_button.grid(row=0, column=0, padx=20, pady=20, sticky="e")

        self.save_button = DarkButton(self.utility_frame, text="Save")
        self.save_button.grid(row=0, column=1, padx=20, pady=20, sticky="e")

    def on_cancel(self):
        self.destroy()
        self.master.utility_frame = ctk.CTkFrame(self.master)
        self.master.utility_frame.grid(column=1, row=1, sticky='nsew', padx=10, pady=10)


class GraphFrame(ContentFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master,
                         title,
                         **kwargs)

        self.save_button.configure(command=self.on_save)

        self.columns = []

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.rowconfigure(5, weight=0)

        # Graph type
        self.graph_type_label = ctk.CTkLabel(self, text="Graph Type:")
        self.graph_type_label.grid(row=1, column=0, padx=20, pady=10)

        self.graph_type_option = ctk.CTkOptionMenu(self, values=["Bar", "Line", "Pie"], command=self.on_type_select)
        self.graph_type_option.grid(row=1, column=1, padx=20, pady=10)

        # Table

        self.table_label = ctk.CTkLabel(self, text="Select Table:")
        self.table_label.grid(row=2, column=0, padx=20, pady=10)

        self.table_option = ctk.CTkOptionMenu(self, values=self.tables, command=self.on_select)
        self.table_option.grid(row=2, column=1, padx=20, pady=10)

        # Column_1

        self.column_1_label = ctk.CTkLabel(self, text="Column 1 (x):")
        self.column_1_label.grid(row=3, column=0, padx=20, pady=10)

        self.column_1_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.column_1_option.grid(row=3, column=1, padx=20, pady=10)

        # QTY

        self.column_2_label = ctk.CTkLabel(self, text="Column 2 (y):")
        self.column_2_label.grid(row=4, column=0, padx=20, pady=10)

        self.column_2_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.column_2_option.grid(row=4, column=1, padx=20, pady=10)

        # Cost

        self.column_3_label = ctk.CTkLabel(self, text="Column 3 (y):")
        self.column_3_label.grid(row=5, column=0, padx=20, pady=10)

        self.column_3_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.column_3_option.grid(row=5, column=1, padx=20, pady=10)

    def on_save(self):
        g_type = self.graph_type_option.get()
        col_1 = self.column_1_option.get()
        col_2 = self.column_2_option.get()
        if g_type == "Pie":
            col_3 = ""
        else:
            col_3 = self.column_3_option.get()

        if self.column_3_option.get() == "Select Sheet":
            col_3 = ""

        self.master.manager.add_graph(self.title, self.table_option.get(), g_type, col_1, col_2, col_3)
        self.master.refresh_listbox()
        self.on_cancel()

    def on_select(self, table):
        columns = data_import.get_columns(self.path, table)
        self.column_1_option.configure(values=columns)
        self.column_2_option.configure(values=columns)
        if self.column_3_option:
            self.column_3_option.configure(values=columns)

    def on_type_select(self, g_type):
        if g_type == "Pie":
            self.column_3_label.destroy()
            self.column_3_option.destroy()
            self.column_3_label = None
            self.column_3_option = None
        elif not self.column_3_label:
            self.column_3_label = ctk.CTkLabel(self, text="Column 3 (y):")
            self.column_3_label.grid(row=5, column=0, padx=20, pady=10)

            self.column_3_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
            self.column_3_option.grid(row=5, column=1, padx=20, pady=10)


class TopICFrame(ContentFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master,
                         title,
                         **kwargs)

        self.columns = []

        self.save_button.configure(command=self.on_save)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)


        self.table_label = ctk.CTkLabel(self, text="Select Table:")
        self.table_label.grid(row=1, column=0, padx=20, pady=10)

        self.table_option = ctk.CTkOptionMenu(self, values=self.tables, command=self.on_select)
        self.table_option.grid(row=1, column=1, padx=20, pady=10)

        # ID

        self.id_label = ctk.CTkLabel(self, text="Material IDs:")
        self.id_label.grid(row=2, column=0, padx=20, pady=10)

        self.id_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.id_option.grid(row=2, column=1, padx=20, pady=10)

        # QTY

        self.qty_label = ctk.CTkLabel(self, text="Quantity:")
        self.qty_label.grid(row=3, column=0, padx=20, pady=10)

        self.qty_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.qty_option.grid(row=3, column=1, padx=20, pady=10)

        # Cost

        self.cost_label = ctk.CTkLabel(self, text="Quantity:")
        self.cost_label.grid(row=4, column=0, padx=20, pady=10)

        self.cost_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.cost_option.grid(row=4, column=1, padx=20, pady=10)


    def on_save(self):
        col_id = self.id_option.get()
        col_qty = self.qty_option.get()
        col_cost = self.cost_option.get()

        self.master.manager.add_top5_file(self.title, self.table_option.get(), col_id, col_qty, col_cost)
        self.master.refresh_listbox()

        self.on_cancel()

    def on_select(self, table):
        columns = data_import.get_columns(self.path, table)
        self.id_option.configure(values=columns)
        self.qty_option.configure(values=columns)
        self.cost_option.configure(values=columns)


class InvTRFrame(ContentFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master,
                         title,
                         **kwargs)

        self.save_button.configure(command=self.on_save)

        self.columns = []

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)

        self.table_label = ctk.CTkLabel(self, text="Select Table:")
        self.table_label.grid(row=1, column=0, padx=20, pady=10)

        self.table_option = ctk.CTkOptionMenu(self, values=self.tables, command=self.on_select)
        self.table_option.grid(row=1, column=1, padx=20, pady=10)

        # Month

        self.month_label = ctk.CTkLabel(self, text="Month:")
        self.month_label.grid(row=2, column=0, padx=20, pady=10)

        self.month_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.month_option.grid(row=2, column=1, padx=20, pady=10)

        # Cost of goods

        self.cogs_label = ctk.CTkLabel(self, text="Cost of goods:")
        self.cogs_label.grid(row=3, column=0, padx=20, pady=10)

        self.cogs_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.cogs_option.grid(row=3, column=1, padx=20, pady=10)

        # Avg Inventory

        self.aic_label = ctk.CTkLabel(self, text="Average Inventory Cost:")
        self.aic_label.grid(row=4, column=0, padx=20, pady=10)

        self.aic_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.aic_option.grid(row=4, column=1, padx=20, pady=10)

    def on_save(self):
        col_mm = self.month_option.get()
        col_cogs = self.cogs_option.get()
        col_aic = self.aic_option.get()

        self.master.manager.add_itr_file(self.title, self.table_option.get(), col_mm, col_cogs, col_aic)
        self.master.refresh_listbox()

        self.on_cancel()

    def on_select(self, table):
        columns = data_import.get_columns(self.path, table)
        self.month_option.configure(values=columns)
        self.cogs_option.configure(values=columns)
        self.aic_option.configure(values=columns)


class BacklogFrame(ContentFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master,
                         title,
                         **kwargs)

        self.columns = []

        self.save_button.configure(command=self.on_save)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)

        self.table_label = ctk.CTkLabel(self, text="Select Table:")
        self.table_label.grid(row=1, column=0, padx=20, pady=10)

        self.table_option = ctk.CTkOptionMenu(self, values=self.tables, command=self.on_select)
        self.table_option.grid(row=1, column=1, padx=20, pady=10)

        # Production Line

        self.pl_label = ctk.CTkLabel(self, text="Production line:")
        self.pl_label.grid(row=2, column=0, padx=20, pady=10)

        self.pl_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.pl_option.grid(row=2, column=1, padx=20, pady=10)

        # Month

        self.month_label = ctk.CTkLabel(self, text="Month:")
        self.month_label.grid(row=3, column=0, padx=20, pady=10)

        self.month_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.month_option.grid(row=3, column=1, padx=20, pady=10)

        # Backlog

        self.backlog_label = ctk.CTkLabel(self, text="Quantity:")
        self.backlog_label.grid(row=4, column=0, padx=20, pady=10)

        self.backlog_option = ctk.CTkOptionMenu(self, values=['Select Sheet'])
        self.backlog_option.grid(row=4, column=1, padx=20, pady=10)

    def on_save(self):
        col_pl = self.pl_option.get()
        col_mm = self.month_option.get()
        col_bl = self.backlog_option.get()

        self.master.manager.add_bl_file(self.title, self.table_option.get(), col_pl, col_mm, col_bl)
        self.master.refresh_listbox()

        self.on_cancel()

    def on_select(self, table):
        columns = data_import.get_columns(self.path, table)
        self.pl_option.configure(values=columns)
        self.month_option.configure(values=columns)
        self.backlog_option.configure(values=columns)


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title('Test')
    root.geometry('1280x800')

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    base_frame = AnalysisHubBaseFrame(root)
    base_frame.grid(row=0, column=0, sticky='nsew')

    root.mainloop()
