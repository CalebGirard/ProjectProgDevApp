import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class BankView(ctk.CTkFrame):
    def __init__(self, master, controller, engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=3)  # Chart + News
        self.grid_columnconfigure(1, weight=1)  # Order execution panel
        self.grid_rowconfigure(1, weight=3)     # Main chart row
        self.grid_rowconfigure(2, weight=1)     # News / bottom tabs row