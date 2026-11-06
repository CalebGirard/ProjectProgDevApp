import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import math

class BankView(ctk.CTkFrame):
    def __init__(self, master, controller, engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller
        self.engine = engine

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=8)
        header.grid(row=0, column=0, columnspan=3, padx=18, pady=(18, 10), sticky="ew")
        ctk.CTkLabel(
            header,
            text="BANQUE",
            text_color="#0ecb81",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=18, pady=(12, 2))
        ctk.CTkLabel(
            header,
            text="Gérez vos prêts et votre crédit",
            text_color="#eaecef",
            font=("Arial", 24, "bold"),
        ).pack(anchor="w", padx=18, pady=(0, 12))

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.grid(row=1, column=0, columnspan=3, padx=12, pady=(0, 10), sticky="ew")
        for column in range(3):
            stats.grid_columnconfigure(column, weight=1)

        stat_cards = []
        for column, title in enumerate(("Valeur de la banque", "Variation", "Crédit")):
            card = ctk.CTkFrame(stats, fg_color="#181a20", corner_radius=8)
            card.grid(row=0, column=column, padx=6, sticky="ew")
            ctk.CTkLabel(
                card, text=title, text_color="#848e9c", font=("Arial", 12, "bold")
            ).pack(anchor="w", padx=14, pady=(12, 2))
            value = ctk.CTkLabel(
                card, text="", text_color="#eaecef", font=("Arial", 18, "bold")
            )
            value.pack(anchor="w", padx=14, pady=(0, 12))
            stat_cards.append(value)

        self.bank_value_label, self.change_label, self.credit_label = stat_cards

        loans_panel = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=8)
        loans_panel.grid(row=2, column=0, padx=(18, 6), pady=(0, 18), sticky="nsew")
        ctk.CTkLabel(
            loans_panel,
            text="VOS PRÊTS",
            text_color="#eaecef",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))
        self.loans_label = ctk.CTkLabel(
            loans_panel,
            text="Aucun prêt",
            text_color="#848e9c",
            justify="left",
            anchor="nw",
            font=("Arial", 13),
        )
        self.loans_label.pack(anchor="w", padx=16, pady=(0, 16))

        actions_panel = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=8)
        actions_panel.grid(row=2, column=1, columnspan=2, padx=(6, 18), pady=(0, 18), sticky="nsew")
        ctk.CTkLabel(
            actions_panel,
            text="OPÉRATIONS",
            text_color="#eaecef",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        self.loan_amount_entry = ctk.CTkEntry(
            actions_panel, placeholder_text="Montant du prêt"
        )
        self.loan_amount_entry.pack(fill="x", padx=16, pady=(4, 6))
        self.take_loan_button = ctk.CTkButton(
            actions_panel, text="Prendre un prêt", command=self.take_loan
        )
        self.take_loan_button.pack(fill="x", padx=16, pady=(0, 14))

        self.repay_amount_entry = ctk.CTkEntry(
            actions_panel, placeholder_text="Montant du remboursement"
        )
        self.repay_amount_entry.pack(fill="x", padx=16, pady=(4, 6))
        self.repay_partial_button = ctk.CTkButton(
            actions_panel, text="Rembourser une partie", command=self.repay_loan
        )
        self.repay_partial_button.pack(fill="x", padx=16, pady=(0, 8))
        self.repay_button = ctk.CTkButton(
            actions_panel,
            text="Rembourser tous les prêts",
            command=self.repay_loans,
            fg_color="#2b313a",
            hover_color="#363c4e",
        )
        self.repay_button.pack(fill="x", padx=16, pady=(0, 16))

        chart_panel = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=8)
        chart_panel.grid(row=3, column=0, columnspan=3, padx=18, pady=(0, 18), sticky="nsew")

        ctk.CTkLabel(
            chart_panel,
            text="ÉVOLUTION SIMULÉE DE LA VALEUR",
            text_color="#848e9c",
            font=("Arial", 11, "bold"),
        ).pack(anchor="w", padx=14, pady=(10, 4))

        figure, self.bank_chart_axis = plt.subplots(figsize=(7, 1.8), facecolor="#181a20")
        figure.subplots_adjust(left=0.05, right=0.99, top=0.92, bottom=0.18)
        self.bank_chart_axis.set_facecolor("#181a20")
        self.bank_chart_axis.tick_params(colors="#848e9c", labelsize=8)
        for spine in self.bank_chart_axis.spines.values():
            spine.set_visible(False)

        self.bank_chart_canvas = FigureCanvasTkAgg(figure, master=chart_panel)
        self.bank_chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.refresh_job = None

        self.refresh_bank()

    def refresh_bank(self):
        if self.refresh_job is not None:
            self.after_cancel(self.refresh_job)

        state = self.engine.bank.get_player_state(self.engine.username)

        total_loans = sum(state["loans"])

        vip_status = "VIP" if state["is_vip"] else "Standard"

        self.bank_value_label.configure(
            text=f"${self.engine.bank.stock_value:.2f}",
            text_color="#0ecb81" if self.engine.bank.stock_change_percent >= 0 else "#f6465d",
        )
        
        self.change_label.configure(
            text=f"{self.engine.bank.stock_change_percent:+.2f}%",
            text_color="#0ecb81" if self.engine.bank.stock_change_percent >= 0 else "#f6465d",
        )
        self.credit_label.configure(
            text=f"{state['credit_score']} / 100 · {vip_status}"
        )

        maximum_loan = self.engine.bank.get_max_loan(self.engine.username)
        maximum_loan_line = f"Prêt maximal : ${maximum_loan:.2f}"

        lines = []

        for amount, rate in zip(state["loans"], state["interest_rates"]):
            lines.append(f"${amount:.2f}  ·  Intérêt : {rate:.2%}")

        if state["loans"]:
            self.loans_label.configure(
                text=f"Dette totale : ${total_loans:.2f}\n{maximum_loan_line}\n\n"
                + "\n".join(lines),
                text_color="#eaecef",
            )    

        else:
            self.loans_label.configure(
                text=f"Aucun prêt en cours\n{maximum_loan_line}",
                text_color="#848e9c",
            )

        history = [
            float(value)
            for value in self.engine.bank.stock_history
            if isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
            and float(value) > 0
        ][-240:]
        self.bank_chart_axis.clear()
        self.bank_chart_axis.set_facecolor("#181a20")
        self.bank_chart_axis.tick_params(colors="#848e9c", labelsize=8)
        for spine in self.bank_chart_axis.spines.values():
            spine.set_visible(False)

        if history:
            chart_color = "#0ecb81" if self.engine.bank.stock_change_percent >= 0 else "#f6465d"
            self.bank_chart_axis.plot(history, color=chart_color, linewidth=1.8)
            self.bank_chart_axis.set_ylim(
                max(0.01, min(history) * 0.98),
                max(history) * 1.02,
            )
        self.bank_chart_canvas.draw_idle()


        self.refresh_job = self.after(1000, self.refresh_bank)

    def take_loan(self):
        try:
            amount = float(self.loan_amount_entry.get())
        except ValueError:
            return

        player_id = self.engine.username

        if amount <= 0 or not math.isfinite(amount):
            return

        total_loans = self.engine.bank.get_total_loans(player_id)
        maximum_loan = self.engine.bank.get_max_loan(player_id)

        if amount + total_loans > maximum_loan:
            return

        self.engine.request_bank_action("take_loan", amount)

        self.refresh_bank()

    def repay_loan(self):
        try:
            amount = float(self.repay_amount_entry.get())
        except ValueError:
            return

        if amount <= 0 or not math.isfinite(amount):
            return

        player_id = self.engine.username
        total_loans = self.engine.bank.get_total_loans(player_id)

        if amount > total_loans:
            return

        cash_path = f"cash:{player_id}"
        current_cash = self.engine.database.getPath(cash_path)

        if isinstance(current_cash, bool) or not isinstance(current_cash, (int, float)):
            return

        current_cash = float(current_cash)

        if not math.isfinite(current_cash) or current_cash < amount:
            return

        self.engine.request_bank_action("repay_loan", amount)

        self.refresh_bank()

    def repay_loans(self):
        player_id = self.engine.username
        state = self.engine.bank.get_player_state(player_id)
        total_loans = sum(state["loans"])

        cash_path = f"cash:{player_id}"
        current_cash = self.engine.database.getPath(cash_path)

        if isinstance(current_cash, bool) or not isinstance(current_cash, (int, float)):
            return

        current_cash = float(current_cash)

        if not math.isfinite(current_cash) or current_cash < total_loans:
            return

        self.engine.request_bank_action("repay_all")
        self.refresh_bank()

    