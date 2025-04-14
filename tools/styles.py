import customtkinter as ctk


class DarkButton(ctk.CTkButton):
    def __init__(self, master, font=("Arial", 14, "bold"), **kwargs):
        super().__init__(master,
                         fg_color=("#333333", "#222222"),  # Dark gray shades
                         hover_color=("#444444"),  # Slightly lighter hover effect
                         text_color="white",
                         corner_radius=5,
                         font=font,
                         border_width=1,
                         **kwargs)


class TransparentButton(ctk.CTkButton):
    def __init__(self, master, font=("Arial", 14, "bold"), **kwargs):
        super().__init__(master,
                         font=font,
                         fg_color='transparent',
                         hover_color="#444444",
                         text_color='White',
                         corner_radius=0,
                         **kwargs)

def get_font():
    font = ("Arial", 16, "bold")
    return font
