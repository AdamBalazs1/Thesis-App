import os

import customtkinter as ctk

from tabs.analysishub import AnalysisHubBaseFrame
from tabs.dashboardhub import DashboardBaseFrame
from tabs.dataimporthub import DataImportBaseFrame
from tabs.freighthub import FreightHubBaseFrame
from tools.appmanager import AppManager
from tools.widgets import NavigationMenu

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.geometry("1280x800")
        self.title("Dashboard Demo")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.app_manager = AppManager()
        self.menu_items = ["Dashboard", "Data Hub", "Analysis Hub", "Freight Hub"]

        self.content_frames = {}

        self.navigation_menu = NavigationMenu(self, self.menu_items, self.show_frame)

        self.create_app()



    def show_frame(self, name):
        if name not in self.content_frames:
            print(f"Error: No frame found for {name}")  # Optional error handling
            return

        for frame_value in self.content_frames.values():
            frame_value.grid_remove()

        self.content_frames[name].grid()


    def create_app(self):
        """Creates the layout for the app"""
        for item in self.menu_items:
            if item == "Dashboard":
                self.content_frames[item] = DashboardBaseFrame(self, self.app_manager)
            elif item == "Data Hub":
                self.content_frames[item] = DataImportBaseFrame(self)
                self.content_frames[item].grid(row=0, column=1, sticky="nsew")
            elif item == "Analysis Hub":
                self.content_frames[item] = AnalysisHubBaseFrame(self)
                self.content_frames[item].grid(row=0, column=1, sticky='nsew')
            elif item == "Freight Hub":
                self.content_frames[item] = FreightHubBaseFrame(self)
                self.content_frames[item].grid(row=0, column=1, sticky="nsew")

        self.navigation_menu.grid(row=0, column=0, sticky='nsew')

        # Default setup
        self.show_frame("Dashboard")
        self.navigation_menu.select_default_button()


if __name__ == '__main__':
    app = App()
    app.mainloop()
