import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import math

class BankView(ctk.CTkFrame):
    def __init__(self, master, controller, engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller
        self.engine = engine

        # Grid configuration
        self.grid_columnconfigure(0, weight=3)  # Chart + News
        self.grid_columnconfigure(1, weight=1)  # Order execution panel
        self.grid_rowconfigure(1, weight=3)     # Main chart row
        self.grid_rowconfigure(2, weight=1)     # News / bottom tabs row

        self.bank_value_label = ctk.CTkLabel(self, text = "Valeur de la banque : 100.00", font = ("Arial", 20, "bold"))
        self.bank_value_label.pack(padx = 20, pady = 10)

        self.change_label = ctk.CTkLabel(self, text = "Variation : +0.00%")
        self.change_label.pack(pady = 5)

        self.credit_label = ctk.CTkLabel(self, text = "score de crédit:50")
        self.credit_label.pack(pady = 5)

        self.loans_label = ctk.CTkLabel(self,text="Aucun prêt",justify="left",)
        self.loans_label.pack(padx=20, pady=10, fill="x")

        self.loan_amount_entry = ctk.CTkEntry(self, placeholder_text = "Montant du prêt",)
        self.loan_amount_entry.pack(padx = 20, pady = 5)

        self.take_loan_button = ctk.CTkButton(self, text = "Prendre un prêt", command = self.take_loan)
        self.take_loan_button.pack(padx = 20, pady = 10)

        self.repay_amount_entry = ctk.CTkEntry(self, placeholder_text = "Montant du remboursement")
        self.repay_amount_entry.pack(padx=20, pady=5)

        self.repay_button = ctk.CTkButton(self, text = "Rembourser tous les prêts", command = self.repay_loans)
        self.repay_button.pack(padx=20, pady=10)

        self.repay_partial_button = ctk.CTkButton(self, text = "Rembourser une partie", command = self.repay_loan)
        self.repay_partial_button.pack(padx=20, pady=10)

        self.refresh_job = None

        self.refresh_bank()

    def refresh_bank(self):
        if self.refresh_job is not None:
            self.after_cancel(self.refresh_job)

        state = self.engine.bank.get_player_state(self.engine.username)

        total_loans = sum(state["loans"])

        vip_status = "VIP" if state["is_vip"] else "Standard"

        self.bank_value_label.configure(text = f"Valeur de la banque : {self.engine.bank.stock_value:.2f}")
        self.change_label.configure(text = f"Variation : {self.engine.bank.stock_change_percent:+.2f}%")
        self.credit_label.configure(text = f"Score de crédit : {state['credit_score']} - {vip_status}")

        maximum_loan = self.engine.bank.get_max_loan(self.engine.username)
        maximum_loan_line = f"prêt maximal : {maximum_loan:.2f}$"

        lines = []

        for amount, rate in zip(state["loans"], state["interest_rates"]):
            lines.append(f"Prêt : {amount:.2f}$ — Intérêt : {rate:.2%}")

        if state["loans"]:
            self.loans_label.configure(
                text = f"Dette totale : {total_loans:.2f}$\n{maximum_loan_line}\n" + "\n".join(lines)
            )    

        else:
            self.loans_label.configure(text = f"Aucun prêt\n{maximum_loan_line}")

        self.refresh_job = self.after(1000, self.refresh_bank)

    def take_loan(self):
        try:
            amount = float(self.loan_amount_entry.get())
        except ValueError:
            return

        player_id = self.engine.username

        if amount <= 0 or not math.isfifinite(amount):
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

        if amount <= 0:
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

    