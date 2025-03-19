import mesa
import numpy as np
import pandas as pd


class HouseholdAgent(mesa.Agent):
    def __init__(self, model, income_bracket, num_people, spend_ratio, income_tax_rate=0.15):
        super().__init__(model)

        self.income_bracket = income_bracket
        self.num_people = num_people
        self.total_household_income = 0
        self.spend_ratio = spend_ratio
        self.income_tax_rate = income_tax_rate ## TODO in ChatGPT, search for: "Assign the correct tax rate at creation time", then do something similar to what is says there.
        self.total_income_posttax = 0
        self.total_household_expense = 0
        self.total_household_savings = 0
        self.health_level = 0 # income seviyesine göre değişecek
        self.welfare = 0



    def step(self):

        default_income_per_person = 10000
        self.total_household_income = default_income_per_person*self.num_people
        self.total_income_posttax = self.total_household_income*self.income_tax_rate

        self.total_household_expense = self.total_household_income*self.spend_ratio

        self.total_household_savings = self.total_household_income - self.total_household_expense

        if self.income_bracket == "low":
            self.health_level = 35
        elif self.income_bracket == "middle":
            self.health_level = 70
        else:
            self.health_level = 100


        self.welfare = self.total_household_income*0.3 + self.total_household_expense*0.2 + self.total_household_savings*0.2 + self.health_level*0.3
        print(f"Welfare: {self.welfare}")