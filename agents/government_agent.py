import mesa
import numpy as np
import pandas as pd
from .person_agent import PersonAgent
from .household_agent import HouseholdAgent
from .firm_agent import FirmAgent
import random


class GovernmentAgent(mesa.Agent):
    '''
    Represents the government entity in the economic simulation.
    
    This agent is responsible for fiscal policy, taxation, welfare programs, 
    and economic monitoring. It collects taxes from households and firms,
    distributes unemployment benefits, provides support to low-income households,
    purchases goods from firms, and calculates key economic indicators.
    '''
    def __init__(self, model):
        '''
        Initialize a new government agent with financial parameters and tax policies.
        
        Sets up the government's initial reserves, tax rates for different income brackets,
        corporate tax rate, and initializes economic indicators tracking.
        
        Parameters:
        - model: Mesa model instance the agent belongs to
        '''
        
        super().__init__(model)

        self.reserves = 100000000
        self.previous_reserves = self.reserves  
        self.inflation_rate = None
        self.unemployment_rate = None
        self.GDP = 0
        self.step_tax_revenue = 0
        self.step_public_spending = 0 
        self.gini_coefficient = 0
        self.government_purchases_from_firms_step = {} # Stores {firm_id: amount_spent_by_gov}
        
        # Define tax brackets
        self.tax_rates = {
            "low": 0.15,    # 15% tax for low income
            "middle": 0.20, # 20% tax for middle income
            "high": 0.27    # 27% tax for high income
        }
        self.corporate_tax_rate = 0.22
        self.step_tax_revenue = 0
        self.step_corporate_tax_revenue = 0

    def _calculate_inflation_rate(self):
        '''
        Calculate inflation rate based on price changes across all firms.
        
        Inflation is computed as the weighted average of price changes over a 2-step period,
        with necessity goods having 80% weight and luxury goods 20% weight. During an initial
        burn-in period, a fixed inflation rate is used. After that, inflation is calculated
        from actual price changes observed in the market.
        '''
        BURN_IN_PERIOD = 5  # Number of initial steps to report fixed inflation
        NECESSITY_WEIGHT = 0.80
        LUXURY_WEIGHT = 0.20

        if self.model.current_step < BURN_IN_PERIOD:
            self.inflation_rate = 5.0 
            return

        necessity_price_changes = []
        luxury_price_changes = []
        
        firm_agents = [agent for agent in self.model.agents if isinstance(agent, FirmAgent)]

        if not firm_agents:
            self.inflation_rate = 0.0
            return

        # Collect price changes by firm type
        for agent in firm_agents:
            if hasattr(agent, 'price_two_steps_ago') and \
               agent.price_two_steps_ago is not None and \
               agent.price_two_steps_ago > 0 and \
               agent.product_price is not None and \
               hasattr(agent, 'firm_type'):
                
                price_change = (agent.product_price - agent.price_two_steps_ago) / agent.price_two_steps_ago
                
                if agent.firm_type == "necessity":
                    necessity_price_changes.append(price_change)
                elif agent.firm_type == "luxury":
                    luxury_price_changes.append(price_change)
        
        # Calculate average inflation for each product category
        avg_necessity_inflation = 0.0
        if necessity_price_changes:
            avg_necessity_inflation = np.mean(necessity_price_changes)

        avg_luxury_inflation = 0.0
        if luxury_price_changes:
            avg_luxury_inflation = np.mean(luxury_price_changes)

        # Calculate weighted inflation based on available data
        if not necessity_price_changes and not luxury_price_changes:
            self.inflation_rate = 0.0
        elif not necessity_price_changes: # Only luxury firms with price changes
            self.inflation_rate = avg_luxury_inflation * 100
        elif not luxury_price_changes: # Only necessity firms with price changes
            self.inflation_rate = avg_necessity_inflation * 100
        else: # Both categories have firms with price changes
            self.inflation_rate = (avg_necessity_inflation * NECESSITY_WEIGHT + 
                                   avg_luxury_inflation * LUXURY_WEIGHT) * 100
        
        # print(f"[INFLATION DEBUG] Step: {self.model.current_step}, Nec Changes: {len(necessity_price_changes)}, Lux Changes: {len(luxury_price_changes)}")
        # print(f"[INFLATION DEBUG] Avg Nec: {avg_necessity_inflation:.4f}, Avg Lux: {avg_luxury_inflation:.4f}, Weighted Infl: {self.inflation_rate:.2f}%")

    def _collect_taxes(self):
        '''
        Collect income taxes from all households based on their income bracket.
        
        Applies the appropriate tax rate to each household's income and adds
        the collected taxes to government reserves. Updates households with
        their applicable tax rate for future calculations.
        
        Returns:
        - Total tax revenue collected in this step
        '''
        
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
        
        #print(f"[TAX] Collected ₺{self.step_tax_revenue:.2f} in taxes from {len(households)} households")

        return self.step_tax_revenue
    
    def _collect_corporate_taxes(self):
        '''
        Collect corporate taxes from profitable firms.
        
        Firms calculate their own tax liability in their step method, excluding revenue
        from direct government purchases. This method aggregates all firm tax payments
        for the current step.
        
        Returns:
        - Total corporate tax revenue collected in this step
        '''
        
        self.step_corporate_tax_revenue = 0
        firm_agents = [agent for agent in self.model.agents if isinstance(agent, FirmAgent)]
        for firm in firm_agents:
            self.step_corporate_tax_revenue += getattr(firm, 'tax_paid_this_step', 0)
        
        #print(f"[CORP TAX] Collected   ₺{self.step_corporate_tax_revenue:.2f} in corporate taxes from {len(firm_agents)} firms")

        return self.step_corporate_tax_revenue
        
    def _calculate_and_distribute_unemployment_payments(self):
        '''
        Calculate and distribute unemployment benefits to jobless individuals.
        
        Identifies persons who are unemployed and actively seeking work, and provides
        them with a fixed unemployment payment. This serves as a social safety net
        and provides income to those without employment.
        
        Returns:
        - Total amount of unemployment payments distributed
        '''
        
        total_unemployment_payments = 0
        person_agents = [p for p in self.model.agents if isinstance(p, PersonAgent)]
        unemployed_persons = [p for p in person_agents if p.employer is None and p.job_seeking]
        
        payment_per_person = 10000 
        
        if unemployed_persons:
            for person in unemployed_persons:
                person.wage = payment_per_person
                total_unemployment_payments += payment_per_person
                # print(f"[GOV] Unemployment payment ₺{payment_per_person:.2f} to person {person.unique_id}")
        return total_unemployment_payments

    def _calculate_and_distribute_low_income_transfers(self):
        '''
        Calculate and distribute financial assistance to low-income households.
        
        Identifies households unable to meet their basic necessity spending targets,
        and provides them with transfers to cover the deficit plus a small buffer.
        This ensures all households can afford essential goods and services.
        
        Returns:
        - Total amount of low-income transfers distributed
        '''
        
        total_low_income_transfers = 0
        households = [h for h in self.model.agents if isinstance(h, HouseholdAgent)]
        
        for household in households:
            total_necessity_target = household.necessity_spend_per_person * household.num_people

            available_funds = household.household_step_income_posttax + household.total_household_savings

            if available_funds < total_necessity_target:
                deficit = total_necessity_target - available_funds
                transfer_amount = deficit + 5000 
                
                household.total_household_savings += transfer_amount
                total_low_income_transfers += transfer_amount
                # print(f"[GOV] Low-income transfer ₺{transfer_amount:.2f} to household {household.unique_id}")
        return total_low_income_transfers

    def _execute_government_necessity_spending(self, budget):
        '''
        Execute government spending on necessity goods from firms.
        
        The government purchases necessity goods from firms to stimulate the economy
        and provide public services. The budget is divided equally between physical
        and service goods. Purchases are distributed across multiple firms to avoid
        market concentration.
        
        Parameters:
        - budget: Amount allocated for government spending on necessity goods
        
        Returns:
        - Total amount actually spent on necessity goods
        '''
        
        total_spent_on_necessities = 0
        
        spending_for_necessity_goods = budget
        
        # Split budget for necessity types (physical and service)
        necessity_categories_to_spend_on = ["physical", "service"]
        if not necessity_categories_to_spend_on:
            return 0.0
            
        budget_per_category = spending_for_necessity_goods / len(necessity_categories_to_spend_on)

        # Spend on each necessity category
        for category_area in necessity_categories_to_spend_on:
            remaining_budget_for_this_category = budget_per_category
            
            # Find firms that match this category and have inventory to sell
            potential_firms_for_category = [
                f for f in self.model.agents 
                if hasattr(f, 'firm_type') and f.firm_type == "necessity" 
                and hasattr(f, 'firm_area') and f.firm_area == category_area
                and hasattr(f, 'product_price') and f.product_price > 0
                and hasattr(f, 'inventory') and f.inventory > 0
            ]
            random.shuffle(potential_firms_for_category)

            # print(f"[GOV DEBUG] Attempting to spend ₺{remaining_budget_for_this_category:.2f} on {category_area}. Found {len(potential_firms_for_category)} firms.")

            while remaining_budget_for_this_category > 0.01 and potential_firms_for_category:
                chosen_firm = potential_firms_for_category.pop(0) # Get and remove first firm

                if chosen_firm.product_price <= 0:
                    continue

                # Calculate how many units can be purchased with remaining budget
                desired_units = int(remaining_budget_for_this_category / chosen_firm.product_price)

                if desired_units <= 0:
                    continue 
                
                # Request goods from the firm
                actually_bought_units = chosen_firm.fulfill_demand_request(desired_units)

                if actually_bought_units > 0:
                    actual_cost_this_transaction = actually_bought_units * chosen_firm.product_price
                    total_spent_on_necessities += actual_cost_this_transaction
                    remaining_budget_for_this_category -= actual_cost_this_transaction
                    
                    # Track government purchases from this firm
                    self.government_purchases_from_firms_step[chosen_firm.unique_id] = \
                        self.government_purchases_from_firms_step.get(chosen_firm.unique_id, 0) + actual_cost_this_transaction

        return total_spent_on_necessities
        
    def _calculate_unemployment_rate(self):
        '''
        Calculate the current unemployment rate in the economy.
        
        Identifies the labor force (employed persons plus job seekers) and determines
        what percentage are actively seeking work but unemployed. This is a key
        economic indicator used to assess the health of the labor market.
        
        Updates:
        - self.unemployment_rate with the percentage of unemployed in the labor force
        '''
        
        person_agents = [
            agent for agent in self.model.agents
            if hasattr(agent, 'job_seeking') and hasattr(agent, 'employer')
        ]

        # Labor force includes employed persons and job seekers
        current_labor_force = [
            p for p in person_agents
            if p.employer is not None or p.job_seeking 
        ]

        # Unemployed people are those in the labor force who do not have an employer
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
        Calculate the Gross Domestic Product (GDP) for the current step.
        
        GDP is calculated by summing the value of all production (production * price)
        across all firms. This provides a measure of the total economic output and
        is a key indicator of economic health.
        
        Returns:
        - GDP value for the current step
        '''
        
        firms = [agent for agent in self.model.agents if hasattr(agent, 'produced_units')]
        
        # Sum the value of all production (production * price)
        total_production_value = sum(firm.produced_units * firm.product_price for firm in firms)
        
        # GDP based on firm production
        step_gdp = total_production_value
        
        return step_gdp

    def calculate_gini_coefficient(self):
        '''
        Calculate the Gini coefficient to measure income inequality.
        
        The Gini coefficient ranges from 0 (perfect equality) to 1 (perfect inequality).
        This implementation uses person wages to compute the coefficient, providing
        a measure of income distribution across the population.
        
        Returns:
        - Gini coefficient as a float between 0 and 1
        '''
        persons = [agent for agent in self.model.agents if isinstance(agent, PersonAgent)]
        incomes = [max(0, p.wage) for p in persons]  # Use max(0, wage) to avoid negative incomes
        
        if not incomes or sum(incomes) == 0:
            return 0.0
            
        x = sorted(incomes)
        n = len(x)
        B = sum(xi * (n - i) for i, xi in enumerate(x)) / (n * sum(x))
        return 1 + (1 / n) - 2 * B
                    
    def step(self):
        '''
        Execute one step of the government's operations in the simulation.
        
        This method handles the government's complete fiscal cycle including:
        - Calculating economic indicators like inflation
        - Distributing welfare payments and transfers
        - Making government purchases from firms
        - Collecting taxes from households and corporations
        - Updating economic metrics like unemployment and GDP
        
        The step method is called by the model scheduler at each simulation step.
        '''
        # Reset tracking for current step
        self.government_purchases_from_firms_step = {}
        self._calculate_inflation_rate()
        
        # Calculate and distribute welfare payments
        unemployment_payments_total = self._calculate_and_distribute_unemployment_payments()
        low_income_transfers_total = self._calculate_and_distribute_low_income_transfers()
        
        # Set initial public spending
        self.step_public_spending = unemployment_payments_total + low_income_transfers_total

        # Reduce reserves based on initial spending
        self.reserves -= self.step_public_spending

        # Calculate government necessity spending from remaining reserves (skip on first step)
        necessity_goods_spent_total = 0
        if self.model.current_step > 1:
            government_necessity_spending_budget = self.reserves * 0.1
            
            # Execute government spending on necessity goods
            necessity_goods_spent_total = self._execute_government_necessity_spending(government_necessity_spending_budget)
        
        # Update reserves and total public spending
        self.reserves -= necessity_goods_spent_total
        self.step_public_spending += necessity_goods_spent_total

        # Collect taxes for the next step
        self.step_tax_revenue = self._collect_taxes()
        self.step_corporate_tax_revenue = self._collect_corporate_taxes()

        # Add tax revenue to reserves for next step's spending
        self.reserves += self.step_tax_revenue + self.step_corporate_tax_revenue
        
        # Calculate other economic indicators
        self._calculate_unemployment_rate()
        self.GDP = self._calculate_gdp()
        self.gini_coefficient = self.calculate_gini_coefficient()
        
        # Store current reserves for reference in next step
        self.previous_reserves = self.reserves
        
    





