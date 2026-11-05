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
import csv
import re
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

        if isinstance(self.companies, list):
            self.company_records = {
                record["company"]: record
                for record in self.companies
            }
            self.companies = {
                record["company"]: record["ceo"]
                for record in self.companies
            }
        else:
            self.company_records = {
                company: {"company": company, "ceo": ceo, "tag": None}
                for company, ceo in self.companies.items()
            }

        with (data_directory / "regions.json").open("r", encoding = "utf-8") as region_file:
            region_data = json.load(region_file)

        regions = []
        for section in region_data:
            if isinstance(section, dict):
                regions.extend(section.keys())
            elif isinstance(section, list):
                regions.extend(section)

        countries = []
        self.country_capitals = {}
        with (data_directory / "country-list.csv").open("r", encoding = "utf-8") as country_file:
            for row in csv.DictReader(country_file):
                countries.append(row["country"])
                self.country_capitals[row["country"]] = row["capital"]

        self.subdivision_capitals = {}
        with (data_directory / "subdivisions.json").open("r", encoding = "utf-8") as subdivision_file:
            subdivision_data = json.load(subdivision_file)

        subdivisions = []
        for subdivision_group in subdivision_data:
            if isinstance(subdivision_group, dict):
                for subdivision, capital in subdivision_group.items():
                    subdivisions.append(subdivision)
                    self.subdivision_capitals[subdivision] = capital

        tags = []
        with (data_directory / "tags.csv").open("r", encoding = "utf-8") as tag_file:
            for row in csv.DictReader(tag_file):
                tags.append(row["tag"])

        self.variable_weights = {
            "company": {company_name: 1.0 for company_name in self.companies},
            "region": {region: 1.0 for region in dict.fromkeys(regions)},
            "country": {country: 1.0 for country in dict.fromkeys(countries)},
            "subdivision": {subdivision: 1.0 for subdivision in dict.fromkeys(subdivisions)},
            "tag": {tag: 1.0 for tag in dict.fromkeys(tags)}
        }

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


    def rebalance_variable(self, variable_name, selected_value):
        weights = self.variable_weights[variable_name]
        removed_weight = weights[selected_value] / 2
        weights[selected_value] -= removed_weight

        other_values = [
            value for value in weights
            if value != selected_value
        ]

        if other_values:
            redistribution = removed_weight / len(other_values)

            for value in other_values:
                weights[value] += redistribution


    def resolve_template_variables(self, template):
        text_fields = [
            template.get("headline", ""),
            template.get("target", ""),
            template.get("target_tag", "")
        ]
        placeholders = set()

        for text in text_fields:
            placeholders.update(re.findall(r"\{([^{}]+)\}", text))

        selected_values = {}

        if (
            "capital" in placeholders
            and "country" in placeholders
            and "country" not in selected_values
        ):
            country = weighted_choice(self.variable_weights["country"])
            self.rebalance_variable("country", country)
            selected_values["country"] = country

        if (
            "capital" in placeholders
            and "subdivision" in placeholders
            and "subdivision" not in selected_values
        ):
            subdivision = weighted_choice(self.variable_weights["subdivision"])
            self.rebalance_variable("subdivision", subdivision)
            selected_values["subdivision"] = subdivision

        for variable_name in placeholders:
            if variable_name == "company_tag":
                if "company" not in selected_values:
                    company = weighted_choice(self.variable_weights["company"])
                    self.rebalance_variable("company", company)
                    selected_values["company"] = company

                selected_values["company_tag"] = self.company_records[
                    selected_values["company"]
                ].get("tag")
                continue

            if variable_name == "capital":
                if "country" in selected_values:
                    selected_values["capital"] = self.country_capitals[
                        selected_values["country"]
                    ]
                elif "subdivision" in selected_values:
                    selected_values["capital"] = self.subdivision_capitals[
                        selected_values["subdivision"]
                    ]
                else:
                    raise ValueError(
                        "{capital} requires {country} or {subdivision} in the template"
                    )
                continue

            if variable_name in ("country-capital", "country_capital"):
                if "country" not in selected_values:
                    country = weighted_choice(self.variable_weights["country"])
                    self.rebalance_variable("country", country)
                    selected_values["country"] = country

                selected_values[variable_name] = self.country_capitals[selected_values["country"]]
                continue

            if variable_name in ("subdivision-capital", "subdivision_capital"):
                if "subdivision" not in selected_values:
                    subdivision = weighted_choice(self.variable_weights["subdivision"])
                    self.rebalance_variable("subdivision", subdivision)
                    selected_values["subdivision"] = subdivision

                selected_values[variable_name] = self.subdivision_capitals[selected_values["subdivision"]]
                continue

            if variable_name == "ceo":
                if "company" not in selected_values:
                    company = weighted_choice(self.variable_weights["company"])
                    self.rebalance_variable("company", company)
                    selected_values["company"] = company

                ceo = self.companies[selected_values["company"]]
                selected_values["ceo"] = ceo
                continue

            if variable_name == "company" and "company" in selected_values:
                continue

            if variable_name == "country" and "country" in selected_values:
                continue

            if variable_name == "subdivision" and "subdivision" in selected_values:
                continue

            if variable_name not in self.variable_weights:
                raise ValueError(
                    "No probability source exists for variable: "
                    + variable_name
                )

            value = weighted_choice(self.variable_weights[variable_name])
            self.rebalance_variable(variable_name, value)
            selected_values[variable_name] = value

        return selected_values


    def resolve_string(self, value, selected_values):
        if not isinstance(value, str):
            return value

        for variable_name, selected_value in selected_values.items():
            value = value.replace(
                "{" + variable_name + "}",
                selected_value
            )

        return value


    def generate_impact(self, template):
        return random.uniform(*template["impact_range"]) * self.chaos


    def build_event(self):
        scope = self.select_scope()
        template = self.select_template(scope)
        selected_values = self.resolve_template_variables(template)
        impact = self.generate_impact(template)

        self.rebalance_template_weights(scope, template["id"])

        return {
            "template_id": template["id"],
            "scope": scope,
            "headline": self.resolve_string(
                template["headline"],
                selected_values
            ),
            "impact": impact,
            "duration_ticks": template["duration_ticks"],
            "target": self.resolve_string(
                template.get("target"),
                selected_values
            ),
            "target_tag": self.resolve_string(
                template.get("target_tag"),
                selected_values
            ),
            "variables": selected_values,
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
            company = event["variables"].get("company")
            return [
                stock for stock in stocks.values()
                if stock.name == company
            ]

        if event["scope"] == "major":
            company = event["variables"].get("company")
            company_tag = event["variables"].get("company_tag")

            if company is not None and company_tag is not None:
                return [
                    stock for stock in stocks.values()
                    if company_tag in getattr(stock, "tags", [])
                    or getattr(stock, "tag", None) == company_tag
                ]

            target_tag = event["target_tag"]

            if target_tag is not None:
                return [
                    stock for stock in stocks.values()
                    if target_tag in getattr(stock, "tags", [])
                    or getattr(stock, "tag", None) == target_tag
                ]

        return list(stocks.values())


    def apply_event(self, event, market):
        for stock in self.resolve_targets(event, market):
            stock.price = max(0.01, stock.price * (1.0 + event["impact"]))

            stock.history = pd.concat([stock.history, pd.Series([stock.price])], ignore_index = True)


    def write_state(self):
        state = {
            "scope_weights": self.scope_weights,
            "template_weights": self.template_weights,
            "variable_weights": self.variable_weights,
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
            "event_queue"
        }

        if not required_keys.issubset(state):
            return False

        self.scope_weights = state["scope_weights"]
        self.template_weights = state["template_weights"]

        if "variable_weights" in state:
            saved_variable_weights = state["variable_weights"]
        else:
            saved_variable_weights = {
                "company": state.get("company_weights", self.variable_weights["company"]),
                "region": state.get("region_weights", self.variable_weights["region"]),
                "country": state.get("country_weights", self.variable_weights["country"])
            }

        for variable_name, default_weights in self.variable_weights.items():
            saved_weights = saved_variable_weights.get(variable_name, {})
            self.variable_weights[variable_name] = {
                value: float(saved_weights.get(value, 1.0))
                for value in default_weights
            }

        for template in self.templates:
            scope = template["scope"]
            template_id = template["id"]
            self.template_weights.setdefault(scope, {})
            self.template_weights[scope].setdefault(template_id, 1.0)

        self.event_list = state["event_queue"]

        for event in self.event_list:
            if "variables" not in event:
                event["variables"] = {}

                for variable_name in (
                    "company",
                    "ceo",
                    "region",
                    "country",
                    "country_capital",
                    "subdivision",
                    "subdivision_capital",
                    "tag",
                    "capital"
                ):
                    if event.get(variable_name) is not None:
                        event["variables"][variable_name] = event[variable_name]

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
