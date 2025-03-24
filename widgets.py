import customtkinter as ctk


class NavigationMenu(ctk.CTkFrame):
    def __init__(self, parent, menu_items: list, switch_callback):
        super().__init__(parent, width=200, corner_radius=0)
        self.switch_callback = switch_callback
        self.buttons = []
        self.menu_items = menu_items
        self.selected_button = None  # Track selected button

        self.create_menu()

    def create_menu(self):
        """Create and store buttons"""
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


class MenuButton(ctk.CTkButton):
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


class ContentFrame(ctk.CTkFrame):
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

        # Create and place menu and widget container
        self.menu = DashboardMenu(self)
        self.menu.grid(row=0, column=0, sticky="new")

        self.widget_container = WidgetContainer(self)
        self.widget_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Allow widget_container to expand
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)


class DashboardMenu(ctk.CTkFrame):
    """Top menu bar inside the dashboard (for future buttons, title, etc.)."""
    def __init__(self, parent):
        super().__init__(parent, height=50, corner_radius=0)
        self.pack_propagate(False)
        ctk.CTkLabel(self, text="Dashboard", font=("Arial", 16)).pack(pady=10)


class WidgetContainer(ctk.CTkFrame):
    """Area where widgets will be placed dynamically."""
    def __init__(self, parent):
        super().__init__(parent)
        self.pack_propagate(False)