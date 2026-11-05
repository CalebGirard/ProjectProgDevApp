from Users.userbase import userbase
from market.market import Market
from Database import Database
from random_events.random_events import random_eventer

class Engine:
    def __init__(self):
        self.username = "host"
        self.database = Database("host",True)
        self.database.rawMsgCallback = self.rawMsgCallback
        self.database.newConnCallback = self.newPlayer
        self.database.startThread()
        self.database.setPath("cash:host",200)
        self.hosting = True
        self.market = Market(200)
        self.eventer = random_eventer(chaos = 1.0)
        self.iteration = 0
        self.userbase = userbase(500, 0.1)
        self.userbase.build_T1s()
        self.userbase.build_T2s()
        self.userbase.build_T3s()
        self.userbase.build_T4s()

    def rebuild(self):
        self.username = "host"
        self.database.setPath("cash:host",200)
        self.hosting = True
        self.market = Market(200)
        self.eventer = random_eventer(chaos = 1.0)
        self.iteration = 0
        self.userbase = userbase(500, 0.1)
        self.userbase.build_T1s()
        self.userbase.build_T2s()
        self.userbase.build_T3s()
        self.userbase.build_T4s()

    def newPlayer(self,username):
        self.database.setPath(f"cash:{username}",200)

    def rawMsgCallback(self,msg):
        if msg["data"].startswith("/buy"):
            data = msg["data"].removeprefix("/buy ").split(" ")
            # Finish implementation of buy command
        elif msg["data"].startswith("/sell"):
            data = msg["data"].removeprefix("/sell ").split(" ")
            # Finish implementation of buy command
        else:
            # Implement chat function
            pass

    def tick(self):
        """Advances the simulation by 1 time step."""
        if self.hosting:
            self.iteration += 1

            #played_event = self.eventer.update(current_iteration = self.iteration, check_interval = 10, market = self.market)

            #if played_event is not None:
            #    self.database.broadcast(played_event["headline"])
            
            self.market.update()
            prices = {t: s.price for t, s in self.market.stocks.items()}
            history = {t: s.history[-1] for t, s in self.market.stocks.items()}
            self.database.set("lastHist",history)
            self.database.set("prices", prices)
        else:
            prices = self.database.get("prices")
            lastHist = self.database.get("lastHist")
            if prices:
                self.market.setPrices(prices)
            if lastHist:
                self.market.addHist(lastHist)

    def _apply_event(self, event):
        if self.hosting:
            # E.g., if event affects Tech, modify AAPL/MSFT
            pass
