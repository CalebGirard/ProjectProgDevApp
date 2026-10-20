from logging import root

import customtkinter as ctk
import tkinter as tk

class MainApp(ctk.CTk): 
    def __init__(self):
        super().__init__()
        self.geometry("800x600+0+0")
        self.after(0, lambda:self.state('zoomed'))
        self.title("Application Principale")
        self.menu_bar()

    def menu_bar(self):
        print()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()