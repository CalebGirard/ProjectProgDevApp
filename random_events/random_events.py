 # Pre-generates and schedules the full list of events before the simulation.
    # Minor events will affect only their stock.
    # Major events will affect their stock and the ones of the same tag(s). 
    # Global events will affect the whole market.
    # Impact coefficients can be positive or negative.

    # Types of minor events :
    # [CEO of x company] publicly supports [x candidate] from [x country].
    # Employees of [x company] have started a strike !
    # {company} beats consensus quarterly earnings by {pct}% and raises full-year forward revenue guidance.
    # Patent office grants {company} exclusive 20-year rights to an unannounced proprietary technology.
    # Billionaire hedge fund manager discloses a {pct}% stake in {company} and demands immediate share buybacks.
    # Regulatory filing reveals {company} inflated subscription renewals and cash reserves for three quarters.
    # [tbd]

    # Types of major events :
    # Donald Trump announces [random %] of tariffs on all countries.
    # [tbd]

    # Types of global events :
    # [major country] attacks [major region]
    # [tbd]

    # Dataframe structure :
    # Turn count - Headline - Scope (Mi/Ma/Gl) - Impact

    # Lists of files : region/countries, ceos of companies, templates of events, list of tags


import json
import random
import pandas as pd
from pathlib import Path

def weighted_choice(weights):
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("Total weight must be greater than zero.")

    roll = random.random() * total
    accumulated = 0.0

    for value, weight in weights.items():
        accumulated += weight
        if roll <= accumulated:
            return value

    return next(reversed(weights))

class random_eventer():

    def __init__(self, chaos):
        self.chaos = chaos
        self.event_list = []

        data_directory = Path(__file__).resolve().parent

        self.state_file = data_directory / "event_state.json"

        with (data_directory / "event_structures.json").open("r", encoding = "utf-8") as template_file:
            self.templates = json.load(template_file)

        with (data_directory / "company_ceos.json").open("r", encoding = "utf-8") as company_file:
            self.companies = json.load(company_file)
        
        self.company_weights = {company_name: 1.0 for company_name in self.companies}

        self.scope_weights = {
            "minor" : 70.0,
            "major" : 25.0,
            "global" : 5.0
        }

        self.template_weights = {}

        for template in self.templates:
            scope = template["scope"]

            if scope not in self.template_weights:
                self.template_weights[scope] = {}

            self.template_weights[scope][template["id"]] = 1.0

        if not self.load_state():
            self.event_list = [self.build_event() for _ in range (5)]
            self.write_state()


    def select_scope(self):
        return weighted_choice(self.scope_weights)


    def select_template(self, scope):
        weights = self.template_weights[scope]
        template_id = weighted_choice(weights)

        template = next(template for template in self.templates if template["id"] == template_id and template["scope"] == scope)
        return template


    def rebalance_template_weights(self,scope, selected_template_id):
        weights = self.template_weights[scope]

        removed_weight = weights[selected_template_id] / 2
        weights[selected_template_id] -= removed_weight

        sibling_ids = [template_id for template_id in weights if template_id != selected_template_id]

        if sibling_ids:
            redistribution = removed_weight / len(sibling_ids)

            for template_id in sibling_ids:
                weights[template_id] += redistribution


    def rebalance_company_weights(self, selected_company):
        removed_weight = self.company_weights[selected_company] / 2
        self.company_weights[selected_company] -= removed_weight

        other_companies = [company for company in self.company_weights if company != selected_company]

        if other_companies:
            redistribution = removed_weight/len(other_companies)

            for company in other_companies:
                self.company_weights[company] += redistribution


    def build_headline(self, template, scope):
        headline = template["headline"]
        company = None
        ceo = None

        if "{company}" in headline:
            company = weighted_choice(self.company_weights)
            self.rebalance_company_weights(company)
            headline = headline.replace("{company}", company)

        if "{ceo}" in headline:
            ceo = self.companies[company]
            headline = headline.replace("{ceo}", ceo)

        return headline, company, ceo


    def generate_impact(self, template):
        return random.uniform(*template["impact_range"]) * self.chaos


    def build_event(self):
        scope = self.select_scope()
        template = self.select_template(scope)

        headline, company, ceo = self.build_headline(template, scope)
        impact = self.generate_impact(template)

        self.rebalance_template_weights(scope, template["id"])


        return {
            "template_id": template["id"],
            "scope": scope,
            "headline": headline,
            "company": company,
            "ceo": ceo,
            "impact": impact,
            "duration_ticks": template["duration_ticks"],
            "target_tag": template.get("target_tag"),
            "play_probability": {
                "minor": 0.70,
                "major": 0.45,
                "global": 0.25
            }[scope],
            "failure_increase": 0.10
        }


    def resolve_targets(self, event, market):
        stocks = market.stocks

        if event["scope"] == "minor":
            return [stock for stock in stocks.values() if stock.name == event["company"]]

        if event["scope"] == "major":
            target_tag = event["target_tag"]

            return [stock for stock in stocks.values() if target_tag in stock.tags]

        return list(stocks.values())


    def apply_event(self, event, market):
        for stock in self.resolve_targets(event, market):
            stock.price = max(0.01, stock.price * (1.0 + event["impact"]))

            stock.history = pd.concat([stock.history, pd.Series([stock.price])], ignore_index = True)


    def write_state(self):
        state = {
            "scope_weights": self.scope_weights,
            "template_weights": self.template_weights,
            "company_weights": self.company_weights,
            "event_queue": self.event_list
        }

        with self.state_file.open("w", encoding = "utf-8") as state_file:
            json.dump(state, state_file, indent = 2, ensure_ascii = False)

    
    def load_state(self):
        if not self.state_file.exists():
            return False

        try:
            with self.state_file.open("r", encoding="utf-8") as state_file:
                state = json.load(state_file)
        except (json.JSONDecodeError, OSError):
            return False

        required_keys = {
            "scope_weights",
            "template_weights",
            "company_weights",
            "event_queue"
        }

        if not required_keys.issubset(state):
            return False

        self.scope_weights = state["scope_weights"]
        self.template_weights = state["template_weights"]
        self.company_weights = state["company_weights"]
        self.event_list = state["event_queue"]

        return True


    def update(self, current_iteration, check_interval, market=None):
        return self.process_event_queue( check_interval = check_interval, current_iteration=current_iteration, market = market)
    

    def process_event_queue(self, check_interval, current_iteration, market = None):
        if current_iteration % check_interval != 0:
            return None

        if not self.event_list:
            self.event_list.append(self.build_event())
            self.write_state()
            return None

        event = self.event_list[0]

        if random.random() <= event["play_probability"]:
            if market is not None:
                self.apply_event(event,market)

            self.event_list.pop(0)
            self.event_list.append(self.build_event())
            self.write_state()
            return event

        event["play_probability"] = min(0.95, event["play_probability"] + event["failure_increase"])

        self.write_state()
        return None
