class stocks():
    def __init__(self, name, shares, tags, history=None,):
        self.price_history = history # dataframe ?
        self.name = name
        self.shares = shares
        self.tags = tags # list of tags for grouping purposes

    def update(self):
        return



class market():
    def __init__(self, size):
        self.stocks = None # array of stocks

    def create_stocks(self, size):
        return