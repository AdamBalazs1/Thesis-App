import customtkinter as ctk
import tksheet
import sqlite3


if __name__ == "__main__":
    connection = sqlite3.connect('music.sqlite')
    cursor = connection.cursor()
    table = "albums"
    sql_select = "SELECT * FROM " + table
    data = cursor.execute(sql_select)
    rows = cursor.fetchall()

    column_names = [description[0] for description in cursor.description]

    # Tkinter:

    window = ctk.CTk()

    window.title("CustomTkinter")
    window.geometry("600x400")

    # Create a frame for the sheet
    table_frame = ctk.CTkFrame(window)
    table_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Create the sheet widget
    sheet = tksheet.Sheet(
        table_frame,
        data=rows,
        show_row_index=False,
        show_top_left=False
    )

    sheet.headers(column_names)

    # Configure table settings
    sheet.enable_bindings((
        "single_select", "drag_select", "column_select",
        "row_select", "row_height_resize", "column_width_resize",
        "arrowkeys", "right_click_popup_menu", "edit_cell"
    ))

    sheet.pack(fill="both", expand=True)

    window.mainloop()

    connection.close()
