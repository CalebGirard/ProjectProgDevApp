from Users.userbase import userbase
from market.market import Market


class Engine:
    def __init__(self):
        self.market = Market(200)
        self.userbase = userbase(500, 0.1)
        self.userbase.build_T1s()
        self.userbase.build_T2s()
        self.userbase.build_T3s()
        self.userbase.build_T4s()

    def tick(self):
        """Advances the simulation by 1 time step."""
        # Check if an event triggers
        self.market.update()

    def _apply_event(self, event):
        # E.g., if event affects Tech, modify AAPL/MSFT
        pass
