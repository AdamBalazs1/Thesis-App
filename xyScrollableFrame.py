import customtkinter as ctk
import tkinter

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("500x300")

    frame = ctk.CTkFrame(root)
    frame.pack()

    frame.rowconfigure(index=0, weight=0)
    frame.rowconfigure(index=1, weight=0)
    frame.columnconfigure(index=0, weight=0)
    frame.columnconfigure(index=1, weight=1)

    scrollable_textbox = ctk.CTkTextbox(frame, width=200, height=200, fg_color='transparent')
    scrollable_textbox.grid(row=0, column=0)

    scrollbar_y = ctk.CTkScrollbar(frame, command=scrollable_textbox.yview)
    scrollbar_y.grid(row=0, column=1, rowspan=2, sticky='ns')

    scrollbar_x = ctk.CTkScrollbar(frame, orientation='horizontal', command=scrollable_textbox.xview)
    scrollbar_x.grid(row=1, column=0)

    # connect textbox scroll event to CTk scrollbar
    scrollable_textbox.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    for i in range(1, 100):
        scrollable_textbox.insert("0.0", "new text to insert, new text to insert, new text to insert, new text to insert, new text to insert, new text to insert\n")

    scrollable_textbox.configure(state="disabled")

    root.mainloop()
