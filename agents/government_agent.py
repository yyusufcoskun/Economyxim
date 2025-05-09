import mesa
import numpy as np
import pandas as pd


class GovernmentAgent(mesa.Agent):
    def __init__(self, model, inflation_rate=39.05, unemployment_rate=8.4, interest_rate=42.5):
        super().__init__(model)

        # TODO I will model inflation after I do firm, because inflation occurs when aggregate demand exceeds aggregate supply. Then I can calculate the average price increase from firms to calculate inflation.
        # TODO Copied from ChatGPT: If unemployment is very low, rising wages might push up production costs.If unemployment is high, the government might consider lowering interest rates to boost spending and hiring. Which will change inflation too.

        self.reserves = 1000000
        self.previous_reserves = self.reserves  # Track previous step's reserves
        self.inflation_rate = inflation_rate
        self.unemployment_rate = unemployment_rate
        self.GDP = 0
        self.step_tax_revenue = 0
        self.yearly_public_spending = 0
        self.step_public_spending = self.reserves * 0.2
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
        
    def _distribute_public_spending(self):
        spending_per_category = self.step_public_spending / 3
        
        # 1. Transfer payments to low-income households
        low_income_households = [h for h in self.model.agents if hasattr(h, 'wealth_bracket') and h.wealth_bracket == "low"]
        if low_income_households:
            transfer_per_household = spending_per_category / len(low_income_households)
            for household in low_income_households:
                if hasattr(household, 'total_household_savings'): # Check before adding
                    household.total_household_savings += transfer_per_household
                # print(f"[GOV] Transfer payment ₺{transfer_per_household:.2f} to low-income household {household.unique_id}")

        # 2. Unemployment wages
        person_agents = [p for p in self.model.agents if hasattr(p, 'employer') and hasattr(p, 'job_seeking')]
        unemployed_persons = [p for p in person_agents if p.employer is None and p.job_seeking]
        
        if unemployed_persons:
            wage_per_unemployed = spending_per_category / len(unemployed_persons)
            for person in unemployed_persons:
                person.wage = wage_per_unemployed # This will be overridden if they get a job
                print(f"[GOV] Unemployment wage ₺{wage_per_unemployed:.2f} to person {person.unique_id}")

        # 3. Government spending on necessity goods
        necessity_firms_physical = [
            f for f in self.model.agents 
            if hasattr(f, 'firm_type') and f.firm_type == "necessity" 
            and hasattr(f, 'firm_area') and f.firm_area == "physical"
            and hasattr(f, 'product_price') and f.product_price > 0 # Ensure firm can sell
        ]
        necessity_firms_service = [
            f for f in self.model.agents 
            if hasattr(f, 'firm_type') and f.firm_type == "necessity" 
            and hasattr(f, 'firm_area') and f.firm_area == "service"
            and hasattr(f, 'product_price') and f.product_price > 0 # Ensure firm can sell
        ]

        spending_for_necessity_goods = spending_per_category
        spending_per_necessity_type = spending_for_necessity_goods / 2

        # Buy from physical necessity firms
        if necessity_firms_physical:
            # Distribute spending somewhat evenly among available firms
            spending_per_physical_firm = spending_per_necessity_type / len(necessity_firms_physical)
            for firm in necessity_firms_physical:
                if firm.product_price > 0:
                    units_to_buy = int(spending_per_physical_firm / firm.product_price)
                    if units_to_buy > 0:
                        firm.receive_demand(units_to_buy)
                        # print(f"[GOV] Purchased {units_to_buy} units from physical necessity firm {firm.unique_id} for ₺{units_to_buy * firm.product_price:.2f}")

        # Buy from service necessity firms
        if necessity_firms_service:
            spending_per_service_firm = spending_per_necessity_type / len(necessity_firms_service)
            for firm in necessity_firms_service:
                if firm.product_price > 0:
                    units_to_buy = int(spending_per_service_firm / firm.product_price)
                    if units_to_buy > 0:
                        firm.receive_demand(units_to_buy)
                        # print(f"[GOV] Purchased {units_to_buy} units from service necessity firm {firm.unique_id} for ₺{units_to_buy * firm.product_price:.2f}")
                        
    def _calculate_unemployment_rate(self):
        """
        Calculate the unemployment rate based on the number of unemployed persons
        Returns the unemployment rate as a percentage
        """
        # Identify all agents who could potentially be in the labor force (e.g., "Person" agents)
        person_agents = [
            agent for agent in self.model.agents
            if hasattr(agent, 'job_seeking') and hasattr(agent, 'employer')
        ]

        # Define the labor force: employed people + unemployed people actively seeking jobs.
        # An agent is in the labor force if they have an employer OR they are job_seeking.
        current_labor_force = [
            p for p in person_agents
            if p.employer is not None or p.job_seeking  # p.job_seeking is True for unemployed seekers
        ]

        # Unemployed people are those in the labor force who do not have an employer.
        # (Given the labor force definition, if employer is None, job_seeking must be True for them to be in current_labor_force)
        actively_unemployed_persons = [
            p for p in current_labor_force
            if p.employer is None
        ]
        
        if current_labor_force:
            self.unemployment_rate = (len(actively_unemployed_persons) / len(current_labor_force)) * 100
        else:
            self.unemployment_rate = 0.0 # Labor force is empty, so unemployment is 0%


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
        
        # Check if reserves have increased by 20% or more since last step
        reserve_growth_ratio = self.reserves / self.previous_reserves if self.previous_reserves > 0 else 1
        temp_spending_boost = 1.0  # Default no boost
        
        if reserve_growth_ratio >= 1.2:  # 20% or more increase
            temp_spending_boost = 1.03  # 3% increase for this step only
            self.step_public_spending *= temp_spending_boost
        
        # New public spending distribution
        self._distribute_public_spending() # Call the new method
        
        # Government spending is now handled by _distribute_public_spending, 
        # but we still need to subtract the total from reserves.
        self.reserves -= self.step_public_spending 
        
        self._calculate_unemployment_rate()
        self.GDP = self._calculate_gdp()
        
        # Update previous_reserves for next step comparison
        self.previous_reserves = self.reserves
        
   






