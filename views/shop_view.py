import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class ShopView(ctk.CTkFrame):
    def __init__(self, master, controller, engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller

        # Configuration de la grille
        self.grid_columnconfigure(0, weight=3)          # Graphique + actualités
        self.grid_columnconfigure(1, weight=1)          # Panneau de passation des ordres
        self.grid_rowconfigure(1, weight=3)             # Ligne du graphique principal
        self.grid_rowconfigure(2, weight=1)             # Ligne des actualités / onglets inférieurs

        ctk.CTkLabel(self,text="COMMING SOON",font=("Arial",20,"bold")).pack(padx=20, pady=20)