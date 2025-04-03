import mesa
import numpy as np
import pandas as pd
import random
from .person_agent import PersonAgent


class HouseholdAgent(mesa.Agent):
    def __init__(self, model, num_people, spend_ratio, income_tax_rate=0.15):
        super().__init__(model)

        #self.income_bracket = income_bracket
        self.num_people = num_people
        self.total_household_income = 0
        self.spend_ratio = spend_ratio
        self.income_tax_rate = income_tax_rate # TODO in ChatGPT, search for: "Assign the correct tax rate at creation time", then do something similar to what is says there.
        self.total_income_posttax = 0
        self.total_household_expense = 0
        self.total_household_savings = 0
        self.health_level = 0 # income seviyesine göre değişecek
        self.welfare = 0
        self.num_working_people = 0
        self.num_not_seeking_job = 0
        self.num_seeking_job = self.num_people - self.num_working_people - self.num_not_seeking_job
        # Create person agents for this household
        self.members = []
        
        # Create person agents for each household member
        for i in range(num_people):
            # Create a person agent and add to household members
            person = PersonAgent(self.model, self, job_seeking=True, wage=0, work_hours=40)
            self.members.append(person)


    def step(self):
        # Update household income based on members' wages
        employed_members = [member for member in self.members if member.employer is not None]  
        self.total_household_income = sum(member.wage for member in employed_members)
        
        # Determine income bracket based on total household income
        
        if self.total_household_income < 50000:
            self.income_bracket = "low"
        elif self.total_household_income < 100000:
            self.income_bracket = "middle"
        else:
            self.income_bracket = "high"
            
        # Calculate taxes and expenses
        self.total_income_posttax = self.total_household_income * (1 - self.income_tax_rate)
        self.total_household_expense = self.total_income_posttax * self.spend_ratio
        self.total_household_savings = self.total_income_posttax - self.total_household_expense

        # Set health level based on income bracket
        if self.income_bracket == "low":
            self.health_level = 35
        elif self.income_bracket == "middle":
            self.health_level = 70
        else:
            self.health_level = 100

        # Choose firms to purchase from based on income bracket
        if self.income_bracket == "low":
            firms = [a for a in self.model.agents if hasattr(a, "firm_type") and a.firm_type == "necessity"]
            if firms:
                chosen_firm = random.choice(firms)
                demand_units = int(self.total_household_expense // chosen_firm.product_price)
                chosen_firm.receive_demand(demand_units)
        elif self.income_bracket == "middle":
            firms = [a for a in self.model.agents if hasattr(a, "firm_type")]
            if firms:
                chosen_firm = random.choice(firms)
                demand_units = int(self.total_household_expense // chosen_firm.product_price * 0.75)
                chosen_firm.receive_demand(demand_units)
        else:
            firms = [a for a in self.model.agents if hasattr(a, "firm_type")]
            if firms:
                chosen_firm = random.choice(firms)
                demand_units = int(self.total_household_expense // chosen_firm.product_price)
                chosen_firm.receive_demand(demand_units)
        
        # Calculate welfare
        self.welfare = self.total_income_posttax*0.3 + self.total_household_expense*0.2 + self.total_household_savings*0.2 + self.health_level*0.3
