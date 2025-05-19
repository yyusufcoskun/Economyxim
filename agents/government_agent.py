import mesa
import numpy as np
import pandas as pd
from .person_agent import PersonAgent
from .household_agent import HouseholdAgent
from .firm_agent import FirmAgent


class GovernmentAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)


        self.reserves = 1000000
        self.previous_reserves = self.reserves  
        self.inflation_rate = None
        self.unemployment_rate = None
        self.GDP = 0
        self.step_tax_revenue = 0
        self.step_public_spending = 0 
        self.gini_coefficient = 0
        
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
        """
        Calculate the average inflation rate based on price changes of all firms over a 2-step period,
        weighted by firm type (70% for necessity, 30% for luxury).
        Inflation for each firm is (current_price - price_two_steps_ago) / price_two_steps_ago.
        Overall inflation is the weighted average of individual firm inflations.
        During an initial burn-in period, inflation is reported as a fixed value (e.g., 3.0).
        """
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
        
        avg_necessity_inflation = 0.0
        if necessity_price_changes:
            avg_necessity_inflation = np.mean(necessity_price_changes)

        avg_luxury_inflation = 0.0
        if luxury_price_changes:
            avg_luxury_inflation = np.mean(luxury_price_changes)

        # If one category has firms but the other doesn't, we should still calculate inflation.
        # If a category has no firms, its contribution to weighted inflation is 0.
        # If both have no firms (already handled by `if not firm_agents`), inflation is 0.

        if not necessity_price_changes and not luxury_price_changes:
             # This case implies firms exist but none are 'necessity' or 'luxury' type, 
             # or they don't have valid price histories.
            self.inflation_rate = 0.0
        elif not necessity_price_changes: # Only luxury firms with price changes
            self.inflation_rate = avg_luxury_inflation * 100 # Effectively 100% weight to luxury if no necessity
        elif not luxury_price_changes: # Only necessity firms with price changes
            self.inflation_rate = avg_necessity_inflation * 100 # Effectively 100% weight to necessity if no luxury
        else: # Both categories have firms with price changes
            self.inflation_rate = (avg_necessity_inflation * NECESSITY_WEIGHT + 
                                   avg_luxury_inflation * LUXURY_WEIGHT) * 100
        
        # print(f"[INFLATION DEBUG] Step: {self.model.current_step}, Nec Changes: {len(necessity_price_changes)}, Lux Changes: {len(luxury_price_changes)}")
        # print(f"[INFLATION DEBUG] Avg Nec: {avg_necessity_inflation:.4f}, Avg Lux: {avg_luxury_inflation:.4f}, Weighted Infl: {self.inflation_rate:.2f}%")

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
        
        #print(f"[TAX] Collected ₺{self.step_tax_revenue:.2f} in taxes from {len(households)} households")

        return self.step_tax_revenue
    
    def _collect_corporate_taxes(self):
        """
        Collect corporate taxes from firms
        """
        firms = [agent for agent in self.model.agents if hasattr(agent, 'profit')]

        for firm in firms:
            if firm.profit > 0:
                corporate_tax_amount = firm.profit * self.corporate_tax_rate
                self.step_corporate_tax_revenue += corporate_tax_amount
        
        return self.step_corporate_tax_revenue
        

    def _calculate_and_distribute_unemployment_payments(self):
        """
        Calculate and distribute unemployment payments.
        Each unemployed person receives a fixed amount.
        Returns the total amount paid.
        """
        total_unemployment_payments = 0
        person_agents = [p for p in self.model.agents if isinstance(p, PersonAgent)]
        unemployed_persons = [p for p in person_agents if p.employer is None and p.job_seeking]
        
        payment_per_person = 10000 # REVERT to hardcoded value
        
        if unemployed_persons:
            for person in unemployed_persons:
                person.wage = payment_per_person
                total_unemployment_payments += payment_per_person
                # print(f"[GOV] Unemployment payment ₺{payment_per_person:.2f} to person {person.unique_id}")
        return total_unemployment_payments

    def _calculate_and_distribute_low_income_transfers(self):
        """
        Calculate and distribute transfers to low-income households.
        Households unable to meet necessity targets receive deficit + 5000.
        Returns the total amount transferred.
        """
        total_low_income_transfers = 0
        households = [h for h in self.model.agents if isinstance(h, HouseholdAgent)]
        
        necessity_spend_per_person = 57750 # REVERT to hardcoded value
        # transfer_top_up = self.current_low_income_transfer_top_up # This was part of adjustment, user reverted the usage already

        for household in households:
            total_necessity_target = necessity_spend_per_person * household.num_people

            available_funds = household.household_step_income_posttax + household.total_household_savings

            if available_funds < total_necessity_target:
                deficit = total_necessity_target - available_funds
                transfer_amount = deficit + 5000 # User already manually set this to 5000
                
                household.total_household_savings += transfer_amount
                total_low_income_transfers += transfer_amount
                # print(f"[GOV] Low-income transfer ₺{transfer_amount:.2f} to household {household.unique_id}")
        return total_low_income_transfers

    def _execute_government_necessity_spending(self, budget):
        """
        Government purchases necessity goods from firms.
        Budget is provided, split 50/50 between physical and service goods.
        Returns the total amount spent.
        """
        total_spent_on_necessities = 0
        
        spending_for_necessity_goods = budget
        
        # Split budget for necessity types (e.g., physical and service)
        spending_per_necessity_type = spending_for_necessity_goods / 2

        necessity_firms_physical = [
            f for f in self.model.agents 
            if hasattr(f, 'firm_type') and f.firm_type == "necessity" 
            and hasattr(f, 'firm_area') and f.firm_area == "physical"
            and hasattr(f, 'product_price') and f.product_price > 0
        ]
        necessity_firms_service = [
            f for f in self.model.agents 
            if hasattr(f, 'firm_type') and f.firm_type == "necessity" 
            and hasattr(f, 'firm_area') and f.firm_area == "service"
            and hasattr(f, 'product_price') and f.product_price > 0
        ]

        # Buy from physical necessity firms
        if necessity_firms_physical and spending_per_necessity_type > 0:
            budget_per_physical_firm = spending_per_necessity_type / len(necessity_firms_physical)
            for firm in necessity_firms_physical:
                if firm.product_price > 0 and budget_per_physical_firm > 0:
                    units_to_buy = int(budget_per_physical_firm / firm.product_price)
                    if units_to_buy > 0:
                        actual_cost = units_to_buy * firm.product_price
                        firm.receive_demand(units_to_buy)
                        total_spent_on_necessities += actual_cost
                        # print(f"[GOV] Purchased {units_to_buy} units from physical necessity firm {firm.unique_id} for ₺{actual_cost:.2f}")

        # Buy from service necessity firms
        if necessity_firms_service and spending_per_necessity_type > 0:
            budget_per_service_firm = spending_per_necessity_type / len(necessity_firms_service)
            for firm in necessity_firms_service:
                if firm.product_price > 0 and budget_per_service_firm > 0:
                    units_to_buy = int(budget_per_service_firm / firm.product_price)
                    if units_to_buy > 0:
                        actual_cost = units_to_buy * firm.product_price
                        firm.receive_demand(units_to_buy)
                        total_spent_on_necessities += actual_cost
                        # print(f"[GOV] Purchased {units_to_buy} units from service necessity firm {firm.unique_id} for ₺{actual_cost:.2f}")
                        
        return total_spent_on_necessities
        
    def _calculate_unemployment_rate(self):
        """
        Calculate the unemployment rate based on the number of unemployed persons
        Returns the unemployment rate as a percentage
        """
        person_agents = [
            agent for agent in self.model.agents
            if hasattr(agent, 'job_seeking') and hasattr(agent, 'employer')
        ]


        current_labor_force = [
            p for p in person_agents
            if p.employer is not None or p.job_seeking 
        ]

        # Unemployed people are those in the labor force who do not have an employer.
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


    def calculate_gini_coefficient(self):
        """
        Calculate the Gini coefficient for person income (wage).
        Returns the Gini coefficient (float between 0 and 1).
        """
        persons = [agent for agent in self.model.agents if isinstance(agent, PersonAgent)]
        incomes = [max(0, p.wage) for p in persons]  # Use max(0, wage) to avoid negative incomes
        if not incomes or sum(incomes) == 0:
            return 0.0
        x = sorted(incomes)
        n = len(x)
        B = sum(xi * (n - i) for i, xi in enumerate(x)) / (n * sum(x))
        return 1 + (1 / n) - 2 * B

                    
        
    def step(self):
        """Execute one step of the government's operations."""
        self._calculate_inflation_rate() # Calculate inflation first
        self._collect_taxes()
        # Use previous reserves for current spending
        
        # Calculate and distribute unemployment payments
        unemployment_payments_total = self._calculate_and_distribute_unemployment_payments()

        # Calculate and distribute low-income transfers
        low_income_transfers_total = self._calculate_and_distribute_low_income_transfers()
        
        # Set initial public spending
        self.step_public_spending = unemployment_payments_total + low_income_transfers_total

        # Reduce reserves based on initial spending
        self.reserves -= self.step_public_spending

        # Calculate government necessity spending from remaining reserves
        government_necessity_spending_budget = self.reserves * 0.05
        
        # Execute government spending on necessity goods
        necessity_goods_spent_total = self._execute_government_necessity_spending(government_necessity_spending_budget)
        
        # Update reserves and total public spending
        self.reserves -= necessity_goods_spent_total
        self.step_public_spending += necessity_goods_spent_total

        # Now collect taxes for the next step
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
        
    





