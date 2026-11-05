class Bank:
    def __init__(self):
        self.stock_value = 100.0
        self.stock_change_percent = 0.0
        self.player_loans = {}


    MAX_LOANS = 10
    BASE_INTEREST_RATE = 0.10
    INTEREST_INCREASE = 0.005
    MANDATORY_PAYMENT_INTERVAL = 100


    def add_player(self,player_id):
        if player_id in self.player_loans:
            return

        self.player_loans[player_id] = {
            "loans": [],
            "interest_rates": [],
            "credit_score": 50
        }


    def get_player_state(self,player_id):
        if player_id not in self.player_loans:
            self.add_player(player_id)

        return self.player_loans[player_id]


   



        

        

