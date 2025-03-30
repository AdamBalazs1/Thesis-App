import customtkinter as ctk

# ToDo Base layout ---
# ToDO Filter - side menu - apply filter button
# ToDo Live/Archive view
# ToDo Popup to add new freight
# ToDo Buttons to add/remove freight
# ToDo Implement limitations per role and state of delivery

class FreightHubBaseFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         **kwargs)

        self.master = master

        # configure grid
        self.rowconfigure(0, weight=0)
        self.columnconfigure(0, weight=0)
