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
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir", menu=file_menu)
        file_menu.add_command(label="Enregistrer", menu=file_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", menu=file_menu)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()