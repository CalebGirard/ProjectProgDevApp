import pandas as pd
import random
import json
from assets import Assets

class Stock:
    def __init__(
        self,
        name,
        ticker,
        shares,
        price,
        history,
        impact,
        currency="USD",
        tags=None,
        volatility=0.02,
        drift=0.0003,
    ):
        self.name = name
        self.ticker = ticker
        self.tags = tags
        self.currency = currency
        self.price = float(price)
        self.shares = shares
        self.volatility = volatility
        self.drift = drift
        self.impact = impact

        self.history = history

        if isinstance(history, pd.Series):
            self.history = history.dropna().tolist()
        else:
            self.history = list(history)

        self.bought = 0
        self.sold = 0

    def buy(self, qty):
        self.bought += qty

    def sell(self, qty):
        self.sold += qty

    def update(self):
        self.price = max(
            0.01,
            self.price
            * (
                1
                + random.gauss(self.drift, self.volatility)
                + self.impact * (self.bought - self.sold) / self.shares
            ),
        )
        self.history.append(self.price)
        self.bought = self.sold = 0

    @property
    def market_cap(self):
        return self.price * self.shares

    def __repr__(self):
        return f"Stock(name={self.name}, price={self.price} {self.currency}, shares={self.shares}, market_cap={self.market_cap})"


class Market:
    def __init__(self, size, impact=10):
        self.size = size
        self.assets = Assets("market")
        self.stocks = self.create_stocks(self.size, impact)  # dictionnary of stocks
        

    def create_stocks(self, size, impact):
        with open(self.assets.getAssetPath("stocks.json"), "r") as f:
            stocks = json.load(f)
        with open(self.assets.getAssetPath("prices.csv")) as f:
            prices = pd.read_csv(f)

        iter = random.sample(stocks, k=size)

        data = {}

        for i in iter:
            data[i["ticker"]] = Stock(
                i["name"],
                i["ticker"],
                i["shares"],
                i["price"],
                prices[i["ticker"]],
                impact,
                i["currency"],
                i["tags"],
                i["volatility"],
                i["drift"],
            )

        return data

    def update(self):
        for stock in self.stocks.values():
            stock.update()

    def setPrices(self,prices):
        if not prices:
            return

        for t, price in prices.items():
            self.stocks[t].price = price

    def addHist(self,lastHist):
        if not lastHist:
            return

        for t, price in lastHist.items():
            self.stocks[t].history.append(price)

    def snapshot(self):
        return {
            t: {
                "name": s.name, "shares": s.shares, "currency": s.currency,
                "tags": s.tags, "volatility": s.volatility, "drift": s.drift,
                "impact": s.impact, "price": s.price,
                "history": [round(p, 4) for p in s.history],
            }
            for t, s in self.stocks.items()
        }

    def load_snapshot(self, stocks):
        self.stocks = {
            t: Stock(d["name"], t, d["shares"], d["price"], d["history"], d["impact"],
                    d["currency"], d["tags"], d["volatility"], d["drift"])
            for t, d in stocks.items()
        }

    def apply_tick(self, prices):
        for t, price in prices.items():
            stock = self.stocks.get(t)
            if stock:
                stock.price = price
                stock.history.append(price)

    def __repr__(self):
        return str(self.stocks)

    def get_tickers(self):
        return sorted(list(self.stocks.keys()))

    def get_names(self):
        return sorted([stock.name for stock in self.stocks.values()])

    def get_stock_by_ticker(self, ticker):
        return self.stocks.get(ticker, None)

    def find_stock_by_long_name(self, name):
        # format : A (A)

        index = name.find("(")
        ticker = name[index + 1 : -1]

        return self.get_stock_by_ticker(ticker)
