import customtkinter as ctk
from styles import TransparentButton


class MovablePopUp(ctk.CTkToplevel):
    def __init__(self, master, work_area, title="Popup Window", geometry='400x200', **kwargs):
        super().__init__(master,
                         **kwargs)
        self.title(title)
        self.geometry(geometry)
        self.overrideredirect(True)
        self.work_area = work_area

        # Center the popup in the middle of the master (root) window

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
        self.close_button.grid(row=0, column=1,padx=2, pady=2)

        self.work_area = work_area(self.header, self)
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
        dx = event.x_root - self.x
        dy = event.y_root - self.y
        self.geometry(f"+{self.winfo_x() + dx}+{self.winfo_y() + dy}")
        self.x = event.x_root
        self.y = event.y_root

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
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         corner_radius=0,
                         fg_color='transparent',
                         **kwargs)


class StepSelect(WorkArea):
    def __init__(self, master, popup_instance, **kwargs):
        super().__init__(master,
                         **kwargs)


        self.types = ['Custom View', 'Graph']     # TODO add types

        self.pop_up_instance = popup_instance

        # Grid configure
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.name_entry = ctk.CTkEntry(self, border_width=1, corner_radius=0, fg_color='transparent', placeholder_text='Name')
        self.name_entry.grid(row=0, column=0, sticky='wes', padx=10, pady=10)

        self.type_select = ctk.CTkOptionMenu(self, corner_radius=0, values=self.types)
        self.type_select.set('Select Type')
        self.type_select.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        self.button_ok = TransparentButton(self, text='Ok', border_width=1, command=self.ok_press)
        self.button_ok.grid(row=2, column=0, sticky='s', pady=15)

        self.button_cancel = TransparentButton(self, text='Cancel', border_width=1, command=self.cancel_press)
        self.button_cancel.grid(row=2, column=1, sticky='s', pady=15)

    def ok_press(self):
        print('Ok Pressed')        # TODO

    def cancel_press(self):
        self.pop_up_instance.destroy()




if __name__ == '__main__':
    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.geometry('400x400')
    root.title('test')

    def on_press():
        pop_up = MovablePopUp(root, StepSelect, 'Create Step')

    button = ctk.CTkButton(root, command=on_press)
    button.pack()

    root.mainloop()
