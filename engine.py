from Users.userbase import userbase
from market.market import Market
from Database import Database
from random_events.random_events import random_eventer

class Engine:
    def __init__(self):
        self.database = Database("host",True)
        self.database.startThread()
        self.hosting = True
        self.market = Market(200)
        self.eventer = random_eventer(chaos = 1.0)
        self.userbase = userbase(500, 0.1)
        self.userbase.build_T1s()
        self.userbase.build_T2s()
        self.userbase.build_T3s()
        self.userbase.build_T4s()
        

    def tick(self):
        """Advances the simulation by 1 time step."""
        if self.hosting:
            self.market.update()
            prices = {t: s.price for t, s in self.market.stocks.items()}
            self.database.set("prices", prices)
        else:
            pass

    def _apply_event(self, event):
        if self.hosting:
            # E.g., if event affects Tech, modify AAPL/MSFT
            pass
