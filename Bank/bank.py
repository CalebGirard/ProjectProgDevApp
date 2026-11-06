import math
import random


class Bank:

    # initialisation de tous les paramètres/variables qui seront utilisés ici.

    def __init__(self):
        self.stock_value = 100.0
        self.stock_change_percent = 0.0
        self.player_loans = {}
        self.stock_history = [self.stock_value]
        self.stock_drift = 0.0015
        self.stock_volatility = 0.025

    max_loans = 10
    base_interest_rate = 0.10
    interest_increase = 0.005
    mandatory_payment_interval = 100

    # crée le "compte bancaire" initial d'un joueur si celui-ci n'existe pas encore

    def add_player(self, player_id):
        if player_id in self.player_loans:
            return

        self.player_loans[player_id] = {
            "loans": [],
            "interest_rates": [],
            "credit_score": 50,
            "paid_interest_multiples": [],
            "is_vip": False,
        }

    # retourne l'état bancaire du joueur, en créant automatiquement cet état
    # lorsqu'il n'existe pas encore

    def get_player_state(self, player_id):
        if player_id not in self.player_loans:
            self.add_player(player_id)

        return self.player_loans[player_id]

    # calcule le montant maximal que le joueur peut emprunter à partir de la
    # valeur actuelle de la banque et de la cote de crédit du joueur.

    def get_max_loan(self, player_id):
        state = self.get_player_state(player_id)

        credit_score = state["credit_score"]

        return self.stock_value * credit_score * 1000

    # valide puis ajoute un nouveau prêt au joueur. vérifie aussi les paramètres bancaires
    # (montant, limite de prêt, dette totale et crédit)

    def take_loan(self, player_id, amount):
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            return False

        amount = float(amount)

        if not math.isfinite(amount) or (amount <= 0):
            return False

        state = self.get_player_state(player_id)

        if len(state["loans"]) >= self.max_loans:
            return False

        self.update_vip_status(player_id)

        loan_count = len(state["loans"])
        interest_rate = self.base_interest_rate + loan_count * 0.10

        if state["is_vip"]:
            interest_rate *= 0.80

        maximum_loan = self.get_max_loan(player_id)

        if amount + self.get_total_loans(player_id) > maximum_loan:
            return False

        state["loans"].append(float(amount))
        state["interest_rates"].append(interest_rate)
        state["paid_interest_multiples"].append(0)

        return True

    # retourne la dette totale actuelle du joueur (la somme de tous ses prêts)

    def get_total_loans(self, player_id):
        state = self.get_player_state(player_id)
        return sum(state["loans"])

    # mise à jour du pointage de crédit selon le nombre de prêts en cours.
    # le fait de n'avoir aucun prêt améliore la cote alors qu'en avoir la diminue.

    def update_credit_score(self, player_id):
        state = self.get_player_state(player_id)

        if len(state["loans"]) == 0:
            state["credit_score"] = min(100, state["credit_score"] + 2)
            return

        elif len(state["loans"]) <= 3:
            state["credit_score"] = max(0, state["credit_score"] - 1)
            return

        state["credit_score"] = max(0, state["credit_score"] - 3)

     # active le statut VIP lorsque le pointage de crédit du joueur atteint 80.

    def update_vip_status(self, player_id):
        state = self.get_player_state(player_id)
        state["is_vip"] = state["credit_score"] >= 80

    # fait évoluer aléatoirement la valeur de l'action de la banque
    # puis mémorise sa nouvelle valeur et sa variation en pourcentage.

    def update_bank_stock(self):
        previous_value = self.stock_value
        market_move = random.gauss(self.stock_drift, self.stock_volatility)
        self.stock_value = max(0.01, self.stock_value * (1.0 + market_move))
        self.stock_history.append(self.stock_value)

        if len(self.stock_history) > 240:
            self.stock_history.pop(0)

        if previous_value > 0:
            self.stock_change_percent = (
                (self.stock_value - previous_value) / previous_value
            ) * 100

    # mise à jour des prêts du joueur en appliquant les intérêts sur les prêts du joueur, 
    # en augmentant progressivement le taux d'intérêt ainsi qu'en déterminant si le joueur doit
    # automatiquement repayer ses prêts

    def update_loans(self, player_id):
        state = self.get_player_state(player_id)

        for i in range(len(state["loans"])):
            current_rate = state["interest_rates"][i]

            state["loans"][i] *= 1 + current_rate

            state["interest_rates"][i] += self.interest_increase

            while True:
                next_threshold = state["paid_interest_multiples"][i] + 1

                if state["interest_rates"][i] < next_threshold:
                    break

                for j in range(len(state["loans"])):
                    payment = state["loans"][j] / 10
                    state["loans"][j] -= payment

                state["paid_interest_multiples"][i] = next_threshold

        self.update_credit_score(player_id)
        self.update_vip_status(player_id)

    # rembourse intégralement tous les prêts du joueur et retourne le montant total remboursé.

    def repay_loans(self, player_id):
        state = self.get_player_state(player_id)

        total_loans = sum(state["loans"])

        state["loans"].clear()
        state["interest_rates"].clear()
        state["paid_interest_multiples"].clear()

        self.update_credit_score(player_id)
        self.update_vip_status(player_id)

        return total_loans

    # rembourse une partie ou la totalité des prêts du joueur s'il n'en a qu'un, en commençant
    # par les prêts les plus anciens. retourne le montant réellement payé.

    def repay_loan(self, player_id, amount):
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            return 0.0

        amount = float(amount)

        if not math.isfinite(amount) or amount <= 0:
            return 0.0

        state = self.get_player_state(player_id)
        remaining_payment = min(amount, sum(state["loans"]))

        if remaining_payment <= 0:
            return 0.0

        paid_amount = remaining_payment

        for i in range(len(state["loans"])):
            if remaining_payment >= state["loans"][i]:
                remaining_payment -= state["loans"][i]
                state["loans"][i] = 0.0
            else:
                state["loans"][i] -= remaining_payment
                remaining_payment = 0.0
                break

        indices_to_keep = [
            i for i, loan_amount in enumerate(state["loans"]) if loan_amount > 0.000001
        ]

        state["loans"] = [state["loans"][i] for i in indices_to_keep]
        state["interest_rates"] = [state["interest_rates"][i] for i in indices_to_keep]
        state["paid_interest_multiples"] = [
            state["paid_interest_multiples"][i] for i in indices_to_keep
        ]

        self.update_credit_score(player_id)
        self.update_vip_status(player_id)

        return paid_amount
