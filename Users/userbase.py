#import pandas as pd


import random as rd
import json



class user():
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




class userbase():
    def __init__(self, nb, difficulty_multiplier):
        self.userbase = []
        self.size = nb
        self.difficulty_multiplier = difficulty_multiplier
        self.random_proportions = self.randomize_odds()


    def randomize_odds(self):
        x, y, z, t = 0, 0, 0, 0
        for i in range(self.size):
            temp = rd.randint(1, self.size)
            if temp %50 == 0 and x < 19:
                x += 1
            elif temp %20 == 0 and y < 18:
                y += 1
            elif temp %10 == 0 and z < 259:
                z += 1
            else:
                t += 1
        return [x, y, z, t]

    def build_T1s(self):
        t1_names = {
    "Government Pension Fund Global": 1800000000000,
    "SAFE Investment Company": 2047000000000,
    "China Investment Corporation": 1567000000000,
    "GIC Private Limited": 936000000000,
    "Abu Dhabi Investment Authority": 990000000000,
    "Kuwait Investment Authority": 1072000000000,
    "Public Investment Fund": 909000000000,
    "BlackRock": 15500000000000,
    "Vanguard": 13300000000000,
    "Fidelity Investments": 7800000000000,
    "State Street Global Advisors": 6300000000000,
    "J.P. Morgan Asset Management": 4800000000000,
    "Capital Group": 3600000000000,
    "Amundi": 2720000000000,  # Approximate USD equivalent
    "Bridgewater Associates": 150200000000,
    "Millennium Management": 97000000000,
    "Elliott Investment Management": 80300000000,
    "Citadel LLC": 77000000000,
    "Man Group": 270900000000
}

        users = []
        for i in range(self.random_proportions[0]):
            obj = rd.choice(list(t1_names.keys()))
            users.append(user(obj, 10 * self.difficulty_multiplier ** 2, t1_names[obj]))
            t1_names.pop(obj)
        self.userbase.extend(users)

    def build_T2s(self):
        t2_names = {
    "Warren Buffett": 143500000000,
    "Peter Lynch": 450000000,
    "Benjamin Graham": 50200000,
    "George Soros": 8600000000,
    "Jim Simons": 31400000000,
    "John \"Jack\" Bogle": 80000000,
    "Ray Dalio": 20000000000,
    "Carl Icahn": 16200000000,
    "Elon Musk": 1100000000000,
    "Jeff Bezos": 370000000000,
    "Larry Page": 334100000000,
    "Sergey Brin": 257100000000,
    "Mark Zuckerberg": 250000000000,
    "Bernard Arnaud": 180000000000,
    "Donald Trump": 5500000000,
    "Larry Ellison": 202000000000,
    "Jensen Huang": 200000000000,
    "Peter Thiel": 37700000000,
    "Sam Altman": 4000000000
}
        
        users = []
        for i in range(self.random_proportions[1]):
            obj = rd.choice(list(t2_names.keys()))
            users.append(user(obj, rd.uniform(7, 9.5) * self.difficulty_multiplier ** 2, t2_names[obj]))
            t2_names.pop(obj)
        self.userbase.extend(users)


    def build_T3s(self):
            data = json.load(open("./Users/adjectives.json","r"))
            temp = []
            terminology = [
                "Inc.",
                "Corp.",
                "Co.",
                "Ltd.",
                "LLC",
                "PLC",
                "LLP",
                "LP",
                "GP",
                "Holdings",
                "Group",
                "Capital",
                "Partners",
                "Ventures",
                "Trust"
                ]
            for i in range(self.random_proportions[2]):
                name = ""
                if rd.randint(1,100) % 10 == 0: name += "The "
                obj = rd.choice(data)
                name += obj
                data.remove(obj)
                name += " "
                name += rd.choice(terminology)
                temp.append(user(name, rd.uniform(4, 8) * self.difficulty_multiplier ** 2, rd.randint(1000000000 * self.difficulty_multiplier ** 2, 10000000000 * self.difficulty_multiplier ** 2)))

            self.userbase.extend(temp)

    def build_T4s(self):
        first_names = json.load(open("./Users/names.json","r"))
        last_names = json.load(open("./Users/last.names.json","r"))

        users = []
        for i in range(self.random_proportions[3]):
            users.append(user((rd.choice(first_names) + " " + rd.choice(last_names)), rd.uniform(0, 3), rd.randint(100 * self.difficulty_multiplier ** 2, 10000000 * self.difficulty_multiplier ** 2)))
        self.userbase.extend(users)

ub = userbase(500, 1)
print(ub.random_proportions)
ub.build_T1s()
ub.build_T2s()
ub.build_T3s()
ub.build_T4s()
print(ub.userbase)