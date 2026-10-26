# import pandas as pd

import random as rd
import json
import math
import csv


class user:
    def __init__(self, nom, lvl, starting_cash):
        self.nom = nom
        self.lvl = lvl
        self.wallet = {}
        self.holdings = starting_cash

    def make_decision(self):
        return

    def buy_stock(self):
        return

    def sell_stock(self):
        return

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
        with open("./Users/predefined_users.json", "r") as f:
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
        with open("./Users/predefined_users.json", "r") as f:
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
        with open("./Users/adjectives.json", "r") as f:
            data = json.load(f)

        temp = []

        with open("./Users/terminology.csv", "r") as f:
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
        with open("./Users/names.json", "r") as f:
            first_names = json.load(f)
        with open("./Users/last.names.json", "r") as f:
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


ub = userbase(500, 0.1)
print(ub.random_proportions)
ub.build_T1s()
ub.build_T2s()
ub.build_T3s()
ub.build_T4s()
print(ub.userbase)
