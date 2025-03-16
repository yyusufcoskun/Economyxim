import mesa
import numpy as np
import pandas as pd


class GovernmentAgent(mesa.Agent):
    def __init__(self, model, reserves=170000000000, inflation_rate=39.05, unemployment_rate=8.4, GDP=118000000000000, yearly_tax_revenue=32828976453, yearly_public_spending=125367000000, interest_rate=0.425):
        super().__init__(model)

        # TODO I will model inflation after I do firm, because inflation occurs when aggregate demand exceeds aggregate supply. Then I can calculate the average price increase from firms to calculate inflation.
        # TODO Copied from ChatGPT: If unemployment is very low, rising wages might push up production costs.If unemployment is high, the government might consider lowering interest rates to boost spending and hiring. Which will change inflation too.

        self.reserves = reserves
        self.inflation_rate = inflation_rate
        self.unemployment_rate = unemployment_rate
        self.GDP = GDP
        self.yearly_tax_revenue = yearly_tax_revenue
        self.yearly_public_spending = yearly_public_spending
        self.interest_rate = interest_rate



    def step(self):
        step_public_spending = self.yearly_public_spending/20
        step_tax_revenue = self.yearly_tax_revenue/12
        self.reserves -= step_public_spending
        self.reserves += step_tax_revenue
        if self.reserves < 160000000000:
            self.yearly_public_spending -= step_public_spending
            # print(f"RESERVES LOW: {str(self.reserves)} ----- Tax Revenue: {str(self.yearly_tax_revenue)} ----- DROPPING Public Spending Level: {str(self.yearly_public_spending)}.")
        else:
            # print(f"RESERVES GOOD: {self.reserves} ----- Tax Revenue: {self.yearly_tax_revenue} ----- CURRENT Public Spending Level: {self.yearly_public_spending}" , end=" ")
            self.yearly_public_spending += step_public_spending 
            # print(f"----- NEW Public Spending Level: {self.yearly_public_spending}")

        






