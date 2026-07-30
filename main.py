import customtkinter as ctk
from gui import App

if __name__ == "__main__":
    root = ctk.CTk()
    ctk.set_appearance_mode("light")
    app = App(root)
    root.mainloop()