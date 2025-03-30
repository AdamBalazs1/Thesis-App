import customtkinter as ctk

root = ctk.CTk()
root.geometry('600x400')

# Create a parent frame and set grid propagation to False
parent_frame = ctk.CTkFrame(root)
parent_frame.grid(row=0, column=0, sticky='nsew')

parent_frame.grid_propagate(False)  # Prevent the frame from resizing automatically

# Configure row and column weights so the frame can expand
parent_frame.grid_rowconfigure(0, weight=1)  # Row 0 will expand
parent_frame.grid_columnconfigure(0, weight=1)  # Column 0 will expand

# Create a label inside the frame
label = ctk.CTkLabel(parent_frame, text="This label will scale with the frame", font=("Arial", 14))
label.grid(row=0, column=0, sticky="nsew")  # Make sure label also expands to fill the space

root.mainloop()
