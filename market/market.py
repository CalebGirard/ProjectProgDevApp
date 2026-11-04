import pandas as pd
import random
import json
from Database import Database

class Stock:
    def __init__(
        self,
        name,
        ticker,
        shares,
        price,
        history,
        impact,
        database:Database,
        currency="USD",
        tags=None,
        volatility=0.02,
        drift=0.0003,
    ):
        self.database = database
        self.name = name
        self.database.setPath(f"stocks:{name}:name",name)
        self.database.setPath(f"stocks:{name}:ticker",ticker)
        self.database.setPath(f"stocks:{name}:tags",tags)
        self.database.setPath(f"stocks:{name}:currency",currency)
        self.database.setPath(f"stocks:{name}:price",price)
        self.database.setPath(f"stocks:{name}:shares",shares)
        self.database.setPath(f"stocks:{name}:volatility",volatility)
        self.database.setPath(f"stocks:{name}:drift",drift)
        self.database.setPath(f"stocks:{name}:impact",impact)
        if isinstance(history, pd.Series):
            self.database.setPath(f"stocks:{name}:history",history.dropna().tolist())
        else:
            self.database.setPath(f"stocks:{name}:history",list(history))
        self.database.setPath(f"stocks:{name}:bought",0)
        self.database.setPath(f"stocks:{name}:sold",0)
        self.database.setPath(f"stocks:{self.name}:marketCap",self.database.getPath(f"stock:{self.name}:price") * self.database.getPath(f"stock:{self.name}:shares"))

    def buy(self, qty):
        self.database.setPath(f"stocks:{self.name}:bought",self.database.getPath(f"stocks:{self.name}:sold")+qty)

    def sell(self, qty):
        self.database.setPath(f"stocks:{self.name}:sold",self.database.getPath(f"stocks:{self.name}:sold")+qty)

    def update(self):
        self.database.setPath(f"stocks:{self.name}:price",max(
            0.01,
            self.database.getPath(f"stocks:{self.name}:price")
            * (
                1
                + random.gauss(self.database.getPath(f"stocks:{self.name}:drift"), self.database.getPath(f"stocks:{self.name}:volatility"))
                + self.database.getPath(f"stocks:{self.name}:impact") * (self.database.getPath(f"stocks:{self.name}:bought") - self.database.getPath(f"stocks:{self.name}:sold")) / self.database.getPath(f"stocks:{self.name}:shares")
            ),
        ))
        self.database.setPath(f"stocks:{self.name}:history",self.database.getPath(f"stocks:{self.name}:history").append(self.database.getPath(f"stocks:{self.name}:price")))
        self.database.setPath(f"stocks:{self.name}:buys",0)
        self.database.setPath(f"stocks:{self.name}:sells",0)
        self.database.setPath(f"stocks:{self.name}:marketCap",self.database.getPath(f"stock:{self.name}:price") * self.database.getPath(f"stock:{self.name}:shares"))

    @property
    def market_cap(self):
        return self.database.getPath(f"stock:{self.name}:price") * self.database.getPath(f"stock:{self.name}:shares")

    def __repr__(self):
        return f"Stock(name={self.name}, price={self.database.getPath(f"stock:{self.name}:price")} {self.database.getPath(f"stock:{self.name}:currency")}, shares={self.database.getPath(f"stock:{self.name}:shares")}, market_cap={self.market_cap})"


class Market:
    def __init__(self, size, database:Database, impact=10):
        self.database = database
        self.stocks = self.create_stocks(size, impact)

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
                self.database,
                i["currency"],
                i["tags"],
                i["volatility"],
                i["drift"],
            )

        return data

    def update(self):
        for stock in self.stocks.values():
            stock.update()

    def __repr__(self):
        return str(self.database.get("stocks"))

    def get_tickers(self):
        return sorted(list(self.database.get("stocks").keys()))

    def get_names(self):
        return sorted([stock["name"] for stock in self.database.get("stocks").values()])

    def get_stock_by_ticker(self, ticker):
        return self.database.get("stocks").get(ticker, None)

    def find_stock_by_long_name(self, name):
        # format : A (A)

        index = name.find("(")
        ticker = name[index + 1 : -1]

        return self.get_stock_by_ticker(ticker)
