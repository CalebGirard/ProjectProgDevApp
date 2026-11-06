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
        self.onMarketLoaded = None
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
        self.database.set("playerlist",[self.username])
        self.database.setPath("cash:host", self.config["starting_cash"])
        self.database.set("messages",[])
        self.hosting = True
        self.market = Market(self.config["num_stocks"])
        self.eventer = random_eventer(chaos = self.config["chaos"], market = self.market)
        self.iteration = 0
        self.userbase = userbase(self.config["num_users"], self.config["difficulty"])
        self.snapshot_id = None
        self.needSnapshot = True
        self.userbase.build_T1s()
        self.userbase.build_T2s()
        self.userbase.build_T3s()
        self.userbase.build_T4s()
        self.bank = Bank()
        self.bank.add_player(self.username)

    def sell(self,username,ticker,x):
        current_stock = self.market.get_stock_by_ticker(ticker)
        user_cash = self.database.getPath(f"cash:{username}")
        spending = user_cash + x * current_stock.price
        self.database.setPath(f"cash:{username}", spending)
        current_stock.sell(x)

    def buy(self,username,ticker,x):
            current_stock = self.market.get_stock_by_ticker(ticker)
            user_cash = self.database.getPath(f"cash:{username}")
            spending = user_cash - x * current_stock.price
    
            if user_cash > spending:
                return
            
            self.database.setPath(f"cash:{username}", spending)
            current_stock.buy(x)

    def newPlayer(self,username):
        self.database.setPath(f"cash:{username}", self.config["starting_cash"])
        if self.market and self.market.stocks:
            self.database.set("market", {
                "id": time.time(),
                "iteration": self.iteration,
                "stocks": self.market.snapshot(),
            })

        playerlist = list(self.database.get("playerlist") or [])
        playerlist.append(username)
        self.database.set("playerlist",playerlist)

        messages = list(self.database.get("messages") or [])
        messages.append({"username": "[Notification]", "message": f"{username} just joined !"})
        if len(messages) >= 40:
            messages.pop(0)
        self.database.set("messages",messages)

    def rawMsgCallback(self,username, msg):
        if msg["data"].startswith("/buy"):
            data = msg["data"].removeprefix("/buy ").split(" ")
            self.buy(username,data[0],int(data[1]))
        elif msg["data"].startswith("/sell"):
            data = msg["data"].removeprefix("/sell ").split(" ")
            self.sell(username,data[0],int(data[1]))
        else:
            messages = list(self.database.get("messages") or [])
            messages.append({"username": username, "message": msg["data"]})
            if len(messages) >= 40:
                messages.pop(0)
            self.database.set("messages",messages)

    def tick(self):
        """Advances the simulation by 1 time step."""
        if self.hosting:
            self.iteration += 1

            if self.iteration % self.bank.mandatory_payment_interval == 0:
                for player_id in list(self.bank.player_loans):
                    self.bank.update_loans(player_id)

                self.bank.update_bank_stock()

            self.database.set("bank_state", {
                "stock_value": self.bank.stock_value,
                "stock_change_percent": self.bank.stock_change_percent,
                "player_loans": self.bank.player_loans
                })

            bank_state = self.database.get("bank_state")

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
            if self.needSnapshot:
                self.needSnapshot = False
                self.database.set("market", {
                    "id": time.time(),
                    "iteration": self.iteration,
                    "stocks": self.market.snapshot(),
                })
            self.database.set("tick", {
                "iteration": self.iteration,
                "prices": {t: s.price for t, s in self.market.stocks.items()},
            })
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
