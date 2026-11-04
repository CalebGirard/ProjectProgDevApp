from Users.userbase import userbase
from market.market import Market
from Database import Database

class Engine:
    def __init__(self):
        self.database = Database("host",True)
        self.database.startThread()
        self.market = Market(200)
        self.userbase = userbase(500, 0.1)
        self.userbase.build_T1s()
        self.userbase.build_T2s()
        self.userbase.build_T3s()
        self.userbase.build_T4s()

    def tick(self):
        """Advances the simulation by 1 time step."""
        self.market.update()
        prices = {t: s.price for t, s in self.market.stocks.items()}
        self.database.set("prices", prices)

    def _apply_event(self, event):
        # E.g., if event affects Tech, modify AAPL/MSFT
        pass
