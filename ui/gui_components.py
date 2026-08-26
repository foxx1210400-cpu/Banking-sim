import tkinter as tk

# Shared button style creator
def make_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        fg="white",
        bg="#333333",
        activebackground="#444444",
        font=("Segoe UI", 12),
        bd=0,
        pady=4
    )

# Shared textbox writer
def write_to_textbox(textbox, text):
    textbox.config(state="normal")
    textbox.delete("1.0", tk.END)
    textbox.insert(tk.END, text)
    textbox.config(state="disabled")
