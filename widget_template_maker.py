import customtkinter as ctk

ctk.set_default_color_theme("dark-blue")
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title('Widget Maker')

root.geometry("420x220")

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# Frame

frame = ctk.CTkFrame(root,width=400, height=200, corner_radius=0, border_width=1)
frame.grid(row=0, column=0, padx=10, pady=10)
# frame.pack_propagate(False)
frame.grid_propagate(False)

pop_up_label = ctk.CTkLabel(frame, text='New Analytics file', font=("Arial", 14, "bold"))
pop_up_label.grid(row=0, column=0, padx=2, pady=2, )

# o_box = ctk.CTkOptionMenu(frame, values=('Default',))
# o_box.grid(row=1, column=0, padx=20, pady=20)
#
# entry = ctk.CTkEntry(frame, placeholder_text="Name")
# entry.grid(row=2, column=0, padx=20, pady=20)

root.mainloop()
