import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, controller, engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller

        # Grid configuration
        # Settings :
        #
        # Difficulty multiplier
        # Nombre de players
        # Nombre de stocks
        # Starting cash

        self.engine = engine

        self.ui_builder()

    def ui_builder(self):

        # Titre de la page
        main = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=10, width=500)
        main.pack(pady=40, padx=40, fill="both", expand=True)

        title = ctk.CTkLabel(
            main,
            text="Simulation Parameters",
            font=("Arial", 22, "bold"),
            text_color="#eaecef",
        )
        title.pack(anchor="w", padx=30, pady=(25, 5))

        # chaos
        self.chaos_label = ctk.CTkLabel(
            main,
            text="Chaos level (affects random events) : ",
            font=("Arial", 14, "bold"),
        )
        self.chaos_label.pack(anchor="w", padx=30, pady=(10, 0))

        self.chaos_input = ctk.CTkEntry(main, placeholder_text=f"{self.engine.eventer.chaos}", height=42)
        self.chaos_input.pack(anchor="e", padx=30, pady=(10, 0))

        # Difficulté
        self.difficulty_label = ctk.CTkLabel(
            main,
            text="Difficulty multiplier (affects simulated players' starting amount and plays)",
            font=("Arial", 14, "bold"),
        )
        self.difficulty_label.pack(anchor="w", padx=30, pady=(10, 0))

        self.difficulty_input = ctk.CTkEntry(main, placeholder_text=f"{self.engine.userbase.difficulty_multiplier}", height=42)
        self.difficulty_input.pack(anchor="e", padx=30, pady=(10, 0))

        # Joueurs
        self.number_players_label = ctk.CTkLabel(
            main, text="Number simulated players : ", font=("Arial", 14, "bold")
        )
        self.number_players_label.pack(anchor="w", padx=30, pady=(10, 0))

        self.number_players_input = ctk.CTkEntry(main, placeholder_text=f"{self.engine.userbase.size}", height=42)
        self.number_players_input.pack(anchor="e", padx=30, pady=(10, 0))

        # Stocks
        self.number_stocks_label = ctk.CTkLabel(
            main, text="Number of stocks : ", font=("Arial", 14, "bold")
        )
        self.number_stocks_label.pack(anchor="w", padx=30, pady=(10, 0))


        self.number_stocks_input = ctk.CTkEntry(main, placeholder_text=f"{self.engine.market.size}", height=42)
        self.number_stocks_input.pack(anchor="e", padx=30, pady=(10, 0))

        # Montant de départ
        self.starting_cash_label = ctk.CTkLabel(
            main,
            text="Starting player cash (doesn't affect simulated players) :",
            font=("Arial", 14, "bold"),
        )
        self.starting_cash_label.pack(anchor="w", padx=30, pady=(10, 0))

        self.starting_cash_input = ctk.CTkEntry(main, placeholder_text="Default", height=42)
        self.starting_cash_input.pack(anchor="e", padx=30, pady=(10, 0))
