# import pandas as pd

import random as rd
import json
import math
import csv
from assets import Assets

class user:
    def __init__(self, nom, lvl, starting_cash):
        self.nom = nom
        self.lvl = lvl
        self.wallet = {}
        self.holdings = starting_cash

    def make_decision(self, market, good_stocks):
        if rd.random() > 0.30:
            return

        # Essayer stocks
        all_tickers = list(market.stocks.keys())
        sample_tickers = rd.sample(all_tickers, min(5, len(all_tickers)))

        # 
        skill_factor = max(0.05, (10.5 - min(10.0, self.lvl)) / 10.0)
        noise_std = 0.08 * skill_factor

        best_ticker = None
        best_score = -999

        for ticker in sample_tickers:
            perceived = good_stocks.get(ticker, 0.0) + rd.gauss(0, noise_std)
            if perceived > best_score:
                best_score = perceived
                best_ticker = ticker

        if best_ticker and best_score > 0.01:
            stock = market.stocks[best_ticker]
            budget = self.holdings * rd.uniform(0.05, 0.20)
            qty = int(budget // stock.price)
            if qty > 0:
                self.buy_stock(stock, qty)

        for ticker, owned_qty in list(self.wallet.items()):
            if owned_qty <= 0:
                continue
            perceived = good_stocks.get(ticker, 0.0) + rd.gauss(0, noise_std)
            if perceived < -0.01:
                stock = market.stocks[ticker]
                sell_qty = max(1, int(owned_qty * rd.uniform(0.3, 1.0)))
                self.sell_stock(stock, sell_qty)

    def buy_stock(self, stock, qty):
        cost = stock.price * qty
        if self.holdings >= cost and qty > 0:
            self.holdings -= cost
            self.wallet[stock.ticker] = self.wallet.get(stock.ticker, 0) + qty
            stock.buy(qty) 

    def sell_stock(self, stock, qty):
        owned = self.wallet.get(stock.ticker, 0)
        qty = min(qty, owned)
        if qty > 0:
            self.holdings += stock.price * qty
            self.wallet[stock.ticker] -= qty
            if self.wallet[stock.ticker] <= 0:
                del self.wallet[stock.ticker]
            stock.sell(qty)  


    def __gt__(self, other):
        return self.name > other.name

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __ge__(self, other):
        return self.name >= other.name

    def __le__(self, other):
        return self.name <= other.name

    def __repr__(self):
        return f"{self.nom} (holding ${self.holdings})"


class userbase:
    def __init__(self, nb, difficulty_multiplier):
        self.userbase = []
        self.size = nb
        self.difficulty_multiplier = difficulty_multiplier
        self.random_proportions = self.randomize_odds()
        self.assets = Assets("Users")

    def randomize_odds(self):
        x, y, z, t = 0, 0, 0, 0
        for i in range(self.size):
            temp = rd.randint(1, self.size)
            if temp % 50 == 0 and x < 19:
                x += 1
            elif temp % 20 == 0 and y < 19:
                y += 1
            elif temp % 10 == 0 and z < 259:
                z += 1
            else:
                t += 1
        return [x, y, z, t]

    def build_T1s(self):
        with open(self.assets.getAssetPath("predefined_users.json"), "r") as f:
            t1_names = json.load(f)[0]
        users = []
        for i in range(self.random_proportions[0]):
            obj = rd.choice(list(t1_names.keys()))
            users.append(
                user(
                    obj,
                    10 * self.difficulty_multiplier**2,
                    math.ceil(t1_names[obj] * self.difficulty_multiplier**2),
                )
            )
            t1_names.pop(obj)
        self.userbase.extend(users)

    def build_T2s(self):
        with open(self.assets.getAssetPath("predefined_users.json"), "r") as f:
            t2_names = json.load(f)[1]
        users = []
        for i in range(self.random_proportions[1]):
            obj = rd.choice(list(t2_names.keys()))
            users.append(
                user(
                    obj,
                    rd.uniform(7, 9.5) * self.difficulty_multiplier**2,
                    math.ceil(t2_names[obj] * self.difficulty_multiplier**2),
                )
            )
            t2_names.pop(obj)
        self.userbase.extend(users)

    def build_T3s(self):
        with open(self.assets.getAssetPath("adjectives.json"), "r") as f:
            data = json.load(f)

        temp = []

        with open(self.assets.getAssetPath("terminology.csv"), "r") as f:
            terminology = list(csv.reader(f, delimiter=","))[0]

        for i in range(self.random_proportions[2]):
            name = ""
            if rd.randint(1, 100) % 10 == 0:
                name += "The "
            obj = rd.choice(data)
            name += obj
            data.remove(obj)
            name += " "
            name += rd.choice(terminology)
            temp.append(
                user(
                    name,
                    rd.uniform(4, 8) * self.difficulty_multiplier**2,
                    math.ceil(
                        rd.uniform(
                            1000000000 * self.difficulty_multiplier**2,
                            10000000000 * self.difficulty_multiplier**2,
                        )
                    ),
                )
            )

        self.userbase.extend(temp)

    def build_T4s(self):
        with open(self.assets.getAssetPath("names.json"), "r") as f:
            first_names = json.load(f)
        with open(self.assets.getAssetPath("last.names.json"), "r") as f:
            last_names = json.load(f)

        users = []
        for i in range(self.random_proportions[3]):
            users.append(
                user(
                    (rd.choice(first_names) + " " + rd.choice(last_names)),
                    rd.uniform(0, 3),
                    math.ceil(
                        rd.uniform(
                            100 * self.difficulty_multiplier**2,
                            10000000 * self.difficulty_multiplier**2,
                        )
                    ),
                )
            )
        self.userbase.extend(users)

    def good_stock_finder(self, market, active_event=None, eventer=None):
            scores = {}
    
            event_targets = set()
            event_impact = 0.0
            if active_event and eventer:
                affected_stocks = eventer.resolve_targets(active_event, market)
                event_targets = {s.ticker for s in affected_stocks}
                event_impact = active_event.get("impact", 0.0)
    
            for ticker, stock in market.stocks.items():
                if len(stock.history) >= 5 and stock.history[-5] > 0:
                    momentum = (stock.price - stock.history[-5]) / stock.history[-5]
                else:
                    momentum = 0.0
    
                score = (momentum * 0.5) + (stock.drift * 10)
    
                if ticker in event_targets:
                    score += event_impact
    
                scores[ticker] = score
    
            return scores
    
    def update(self, market, active_event=None, eventer=None):
        good_stocks = self.good_stock_finder(market, active_event, eventer)
    
        for bot in self.userbase:
            bot.make_decision(market, good_stocks)

