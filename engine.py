from Users.userbase import userbase
from market.market import Market
from Database import Database
from random_events.random_events import random_eventer
import time

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

    def sell(self,username,ticker,x):
        current_stock = self.market.get_stock_by_ticker(ticker)
        if current_stock is None or x <= 0:
            return False

        user_cash = self.database.getPath(f"cash:{username}")
        if user_cash is None:
            return False

        portfolios = dict(self.database.get("portfolios") or {})
        positions = dict(portfolios.get(username, {}))
        owned = positions.get(ticker, 0)
        if x > owned:
            return False

        spending = user_cash + x * current_stock.price
        self.database.setPath(f"cash:{username}", spending)
        positions[ticker] = owned - x
        if positions[ticker] == 0:
            del positions[ticker]
        portfolios[username] = positions
        self.database.set("portfolios", portfolios)
        current_stock.sell(x)
        return True

    def buy(self,username,ticker,x):
        current_stock = self.market.get_stock_by_ticker(ticker)
        if current_stock is None or x <= 0:
            return False

        user_cash = self.database.getPath(f"cash:{username}")
        cost = x * current_stock.price
        if user_cash is None or user_cash < cost:
            return False

        self.database.setPath(f"cash:{username}", user_cash - cost)
        portfolios = dict(self.database.get("portfolios") or {})
        positions = dict(portfolios.get(username, {}))
        positions[ticker] = positions.get(ticker, 0) + x
        portfolios[username] = positions
        self.database.set("portfolios", portfolios)
        current_stock.buy(x)
        return True

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
        self.database.set("messages", messages)
        self.needSnapshot = True

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

            self.userbase.update(
                market=self.market, 
                active_event=played_event, 
                eventer=self.eventer
            )
            
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
            snap = self.database.get("market")
            if snap and snap.get("id") != self.snapshot_id:
                if not self.market:
                    self.market = Market(len(snap["stocks"]))
                self.market.load_snapshot(snap["stocks"])
                self.snapshot_id = snap["id"]
                self.iteration = snap["iteration"]
                if self.onMarketLoaded:
                    self.onMarketLoaded()
            
            td = self.database.get("tick")
            if td and td.get("iteration", 0) > self.iteration and self.market:
                self.iteration = td["iteration"]
                self.market.apply_tick(td["prices"])
