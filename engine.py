from Users.userbase import userbase
from market.market import Market
from Database import Database
from random_events.random_events import random_eventer

class Engine:
    def __init__(self, starting_cash_def=50000, market_def=200, chaos_def=1.0, nbusers_def = 500, diff_mul_def = 1.0):
        self.username = "host"
        self.database = Database("host",True)
        self.database.rawMsgCallback = self.rawMsgCallback
        self.database.newConnCallback = self.newPlayer
        self.database.startThread()
        self.config = {
            "num_stocks": market_def,
            "num_users": nbusers_def,
            "chaos": chaos_def,        
            "difficulty": diff_mul_def,
            "starting_cash":starting_cash_def
        }
        self.rebuild()


    def rebuild(self, config_changes=None):
        if config_changes:
            self.config.update(config_changes)

        self.username = "host"
        self.database.setPath("cash:host", self.config["starting_cash"])
        self.database.set("messages",[])
        self.hosting = True
        self.market = Market(self.config["num_stocks"])
        self.eventer = random_eventer(chaos = self.config["chaos"], market = self.market)
        self.iteration = 0
        self.userbase = userbase(self.config["num_users"], self.config["difficulty"])
        self.userbase.build_T1s()
        self.userbase.build_T2s()
        self.userbase.build_T3s()
        self.userbase.build_T4s()

    def newPlayer(self,username):
        self.database.setPath(f"cash:{username}",200)
        messages = list(self.database.get("messages") or [])
        messages.append({"username": "[Notification]", "message": f"{username}, just joined !"})
        if len(messages) >= 40:
            messages.pop[0]
        self.database.set("messages",messages)

    def rawMsgCallback(self,username, msg):
        if msg["data"].startswith("/buy"):
            data = msg["data"].removeprefix("/buy ").split(" ")
            # Finish implementation of buy command
        elif msg["data"].startswith("/sell"):
            data = msg["data"].removeprefix("/sell ").split(" ")
            # Finish implementation of buy command
        else:
            messages = list(self.database.get("messages") or [])
            messages.append({"username": username, "message": msg["data"]})
            if len(messages) >= 40:
                messages.pop[0]
            self.database.set("messages",messages)

    def tick(self):
        """Advances the simulation by 1 time step."""
        if self.hosting:
            self.iteration += 1

            played_event = self.eventer.update(
                current_iteration = self.iteration,
                check_interval = 10,
                market = self.market
            )

            if self.eventer.event_list:
                next_event = self.eventer.event_list[0]
                self.database.set("next_event", {
                    "headline": next_event["headline"],
                    "scope": next_event["scope"],
                    "play_probability": next_event["play_probability"]
                })
            
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
