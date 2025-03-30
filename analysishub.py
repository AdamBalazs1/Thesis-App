import customtkinter as ctk
from widgets import SideMenuFrame
from moveablepopup import MovablePopUp, StepSelect
from widgets import DarkAddButton, DarkRemoveButton, DarkButton

class AnalysisHubBaseFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         fg_color='transparent',
                         **kwargs)

        self.master = master

        # Configure grid
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Widgets
        side_menu_frame = SideMenuFrame(self, DarkAddButton, DarkRemoveButton, self.on_select, self.add_on_press, self.remove_on_press)
        side_menu_frame.grid(column=0, row=0, rowspan=2, sticky='ns', padx=10, pady=10)

        self.header_frame = ctk.CTkFrame(self, height=70)
        self.header_frame.grid(column=1, row=0, sticky='nsew', padx=10, pady=10)
        self.header_frame.grid_propagate(False)

        self.header_frame.rowconfigure(0, weight=1)
        self.header_frame.columnconfigure(0, weight=1)
        self.header_frame.columnconfigure(1, weight=1)

        self.header_label = ctk.CTkLabel(self.header_frame, text='Data Analysis Hub', font=("Arial", 16, "bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')


        # TODO expand on this
        self.header_button_frame = ctk.CTkFrame(self.header_frame, fg_color='transparent')
        self.header_button_frame.grid(row=0, column=1, sticky='e', padx=20)

        self.header_add_step = DarkButton(self.header_button_frame, text='Add Step')
        self.header_add_step.grid(row=0, column=0, padx=10, ipady=1)

        self.header_remove_step = DarkButton(self.header_button_frame, text='Remove Step')
        self.header_remove_step.grid(row=0, column=1, ipadx=2, ipady=1)

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(column=1, row=1, sticky='nsew', padx=10, pady=10)

    def on_select(self, event):
        print('Option selected: {}'.format(event))

    def add_on_press(self):
        pop_up = MovablePopUp(self.master, StepSelect, 'Create Step')

    def remove_on_press(self):
        print('remove button pressed')      # TODO implement this


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title('Test')
    root.geometry('1280x800')

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    base_frame = AnalysisHubBaseFrame(root)
    base_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

    root.mainloop()
