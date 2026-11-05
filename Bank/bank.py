class Bank:
    def __init__(self):
        self.stock_value = 100.0
        self.stock_change_percent = 0.0
        self.player_loans = {
            "loans": [],
            "interest_rates": [],
            "credit_score": 50
        }

        MAX_LOANS = 10
        BASE_INTEREST_RATE = 0.10
        INTEREST_INCREASE = 0.005
        MANDATORY_PAYMENT_INTERVAL = 100

        

        

