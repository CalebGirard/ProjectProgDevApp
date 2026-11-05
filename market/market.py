import pandas as pd
import random
import json


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
        self.buys = self.sells = 0

    @property
    def market_cap(self):
        return self.price * self.shares

    def __repr__(self):
        return f"Stock(name={self.name}, price={self.price} {self.currency}, shares={self.shares}, market_cap={self.market_cap})"


class Market:
    def __init__(self, size, impact=10):
        self.stocks = self.create_stocks(size, impact)  # dictionnary of stocks

    def create_stocks(self, size, impact):
        with open("./market/stocks.json", "r") as f:
            stocks = json.load(f)
        with open("./market/prices.csv") as f:
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
        for t,price in prices:
            self.stocks[t].price = price

    def addHist(self,lastHist):
        for t,price in lastHist:
            self.stocks[t].history.append(price)

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
