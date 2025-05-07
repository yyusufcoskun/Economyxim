import mesa
import numpy as np
import pandas as pd


class GovernmentAgent(mesa.Agent):
    def __init__(self, model, reserves=5439372030600, inflation_rate=39.05, unemployment_rate=8.4, yearly_public_spending=439372030600, interest_rate=42.5):
        super().__init__(model)

        # TODO I will model inflation after I do firm, because inflation occurs when aggregate demand exceeds aggregate supply. Then I can calculate the average price increase from firms to calculate inflation.
        # TODO Copied from ChatGPT: If unemployment is very low, rising wages might push up production costs.If unemployment is high, the government might consider lowering interest rates to boost spending and hiring. Which will change inflation too.

        self.reserves = reserves
        self.inflation_rate = inflation_rate
        self.unemployment_rate = unemployment_rate
        self.GDP = 0
        self.step_tax_revenue = 0
        self.yearly_public_spending = yearly_public_spending
        self.step_public_spending = yearly_public_spending/4
        self.interest_rate = interest_rate
        
        # Define tax brackets
        self.tax_rates = {
            "low": 0.15,    # 15% tax for low income
            "middle": 0.20, # 20% tax for middle income
            "high": 0.27    # 27% tax for high income
        }
        
        # Track tax collection per step
        self.step_tax_revenue = 0


    def _collect_taxes(self):
        """
        Apply the appropriate tax rate to each household based on their income bracket
        and collect taxes into government reserves
        """
        self.step_tax_revenue = 0
        
        # Find all household agents
        households = [agent for agent in self.model.agents if hasattr(agent, 'income_bracket')]
        
        for household in households:
            # Set the appropriate tax rate based on income bracket
            if hasattr(household, 'income_bracket'):
                # Get the correct tax rate based on income bracket
                tax_rate = self.tax_rates[household.income_bracket]
                
                # Calculate tax amount based on total income
                tax_amount = household.household_step_income * tax_rate
                
                # Update household's tax rate for future income calculations
                household.income_tax_rate = tax_rate
                
                # Collect taxes for government
                self.step_tax_revenue += tax_amount
        
        # Debug tax collection
        #print(f"[TAX] Collected ₺{self.step_tax_revenue:.2f} in taxes from {len(households)} households")

        return self.step_tax_revenue
        
    def _calculate_unemployment_rate(self):
        """
        Calculate the unemployment rate based on the number of unemployed persons
        Returns the unemployment rate as a percentage
        """

        all_persons = [agent for agent in self.model.agents if hasattr(agent, 'employer')]
        unemployed_persons = [person for person in all_persons if person.employer is None]
        
        if all_persons:
            self.unemployment_rate = (len(unemployed_persons) / len(all_persons)) * 100


    def _calculate_gdp(self):
        '''
        Calculate GDP by summing the value of all production (production * price)
        '''

        # Calculate production by firms
        firms = [agent for agent in self.model.agents if hasattr(agent, 'produced_units')]
        
        # Sum the value of all production (production * price)
        total_production_value = sum(firm.produced_units * firm.product_price for firm in firms)
        
        # Quarterly GDP based on firm production
        step_gdp = total_production_value
        #print(f"DEBUG: ----- GDP: {step_gdp}")
        # Yearly GDP estimation (multiplying quarterly by 4)
        # yearly_gdp = step_gdp * 4
        
        return step_gdp

        """
        Calculate GDP using the expenditure approach: GDP = C + I + G + (X - M)
        Returns the yearly GDP value
        
        # Get consumer spending from household agents
        consumer_spending = sum([agent.total_household_expense for agent in self.model.agents 
                               if hasattr(agent, 'total_household_expense')])
        investment = 0 # TODO: Make firms invest 
        step_public_spending = self.yearly_public_spending/4  # Quarterly government spending
        net_exports = 0 # TODO: Model trade
        
        calculated_gdp = consumer_spending + investment + step_public_spending + net_exports

        yearly_gdp = calculated_gdp * 4
        """

    def step(self):
        # Apply tax rates and collect taxes
        self.step_tax_revenue = self._collect_taxes()
        self.reserves += self.step_tax_revenue
        self.reserves -= self.step_public_spending
        
        if self.reserves < 160000000000:
            self.step_public_spending *= 0.8
            # print(f"RESERVES LOW: {str(self.reserves)} ----- Tax Revenue: {str(self.yearly_tax_revenue)} ----- DROPPING Public Spending Level: {str(self.yearly_public_spending)}.")
        else:
            # print(f"RESERVES GOOD: {self.reserves} ----- Tax Revenue: {self.yearly_tax_revenue} ----- CURRENT Public Spending Level: {self.yearly_public_spending}" , end=" ")
            self.step_public_spending *= 1.1
            # print(f"----- NEW Public Spending Level: {self.yearly_public_spending}")
        
        self._calculate_unemployment_rate()
        self.GDP = self._calculate_gdp()
        
   






