import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class MultiView(ctk.CTkFrame):
    def __init__(self, master, controller, engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller

        self.grid_columnconfigure(0, weight=2)  
        self.grid_columnconfigure(1, weight=2)  
        self.grid_rowconfigure(0, weight=3)     
        self.grid_rowconfigure(1, weight=3)
        
        self.connectedView = ConnectedFrame(self)
        self.connectedView.lower()

        self.createInitMenu()

    def connectGame(self):
        pass

    def hostGame(self):
        self.connectedView.tkraise()

    def createInitMenu(self):
        self.initframe = ctk.CTkFrame(self, fg_color="black")
        self.initframe.pack(fill="both", expand=True)

class ConnectedFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#0b0e11")

        self.grid_columnconfigure(0, weight=3)  # Chart + News
        self.grid_columnconfigure(1, weight=1)  # Order execution panel
        self.grid_rowconfigure(1, weight=3)     # Main chart row
        self.grid_rowconfigure(2, weight=1)     # News / bottom tabs row
