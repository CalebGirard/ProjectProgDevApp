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
        state = "normal"
        if self.engine.hosting == False:
            state = "disabled"

        # Titre de la page
        main = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=10, width=500)
        main.pack(pady=40, padx=40, fill="both", expand=True)

        
        self.host_warning_label = ctk.CTkLabel(
            main,
            text="",
            font=("Arial", 12, "italic"),
            text_color="#f6465d",
        )
        self.host_warning_label.pack(anchor="w", padx=30, pady=(0, 5))

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

        self.chaos_input = ctk.CTkEntry(main, placeholder_text=f"{self.engine.config["chaos"]}", height=42, state=state)
        self.chaos_input.pack(anchor="e", padx=30, pady=(10, 0))

        # Difficulté
        self.difficulty_label = ctk.CTkLabel(
            main,
            text="Difficulty multiplier (affects simulated players' starting amount and plays)",
            font=("Arial", 14, "bold"),
        )
        self.difficulty_label.pack(anchor="w", padx=30, pady=(10, 0))

        self.difficulty_input = ctk.CTkEntry(main, placeholder_text=f"{self.engine.config["difficulty"]}", height=42, state=state)
        self.difficulty_input.pack(anchor="e", padx=30, pady=(10, 0))

        # Joueurs
        self.number_players_label = ctk.CTkLabel(
            main, text="Number simulated players : ", font=("Arial", 14, "bold")
        )
        self.number_players_label.pack(anchor="w", padx=30, pady=(10, 0))

        self.number_players_input = ctk.CTkEntry(main, placeholder_text=f"{self.engine.config["num_users"]}", height=42, state=state)
        self.number_players_input.pack(anchor="e", padx=30, pady=(10, 0))

        # Stocks
        self.number_stocks_label = ctk.CTkLabel(
            main, text="Number of stocks : ", font=("Arial", 14, "bold")
        )
        self.number_stocks_label.pack(anchor="w", padx=30, pady=(10, 0))


        self.number_stocks_input = ctk.CTkEntry(main, placeholder_text=f"{self.engine.config["num_stocks"]}", height=42, state=state)
        self.number_stocks_input.pack(anchor="e", padx=30, pady=(10, 0))

        # Montant de départ
        self.starting_cash_label = ctk.CTkLabel(
            main,
            text="Starting player cash (doesn't affect simulated players) :",
            font=("Arial", 14, "bold"),
        )
        self.starting_cash_label.pack(anchor="w", padx=30, pady=(10, 0))

        self.starting_cash_input = ctk.CTkEntry(main, placeholder_text=f"{self.engine.config["starting_cash"]}", height=42, state=state)
        self.starting_cash_input.pack(anchor="e", padx=30, pady=(10, 0))

        # Appliquer les settings

        self.apply_btn = ctk.CTkButton(
            main,
            text="Apply & Restart Simulation",
            fg_color="#0ecb81",
            hover_color="#0ba367",
            font=("Arial", 14, "bold"),
            height=42,
            command=self._apply_settings
        )
        self.apply_btn.pack(anchor="se", padx=30, pady=48)
        

    def _apply_settings(self):
                
        new_config = {
            "num_stocks": int(self.number_stocks_input.get().strip() or self.engine.config["num_stocks"]),
            "num_users": int(self.number_players_input.get().strip() or self.engine.config["num_users"]),
            "chaos": float(self.chaos_input.get().strip() or self.engine.config["chaos"]),
            "difficulty": float(self.difficulty_input.get().strip() or self.engine.config["difficulty"]),
            "starting_cash": float(self.starting_cash_input.get().strip() or self.engine.config["starting_cash"]),
        }
        self.engine.rebuild(new_config)

        market_view = self.controller.frames.get("Market")
        if market_view:
            market_view.reset()

    
