import mesa
import numpy as np
import pandas as pd
import random
from .person_agent import PersonAgent


class HouseholdAgent(mesa.Agent):
    '''
    Represents a household in the economy simulation.
    
    A household contains multiple people who can work and earn income.
    The household makes consumption decisions based on total income, wealth,
    and preferences, spending on necessities first and luxuries if affordable.
    It interacts with firm agents to purchase goods and tracks financial metrics.
    '''
    
    def __init__(self, model, num_people, income_tax_rate=0.15):
        '''
        Initialize a new household with financial parameters and member tracking.
        
        Parameters:
        - model: The model instance this household belongs to
        - num_people: Target number of people for this household
        - income_tax_rate: Initial rate of income tax applied to household income
        '''
        super().__init__(model)

        # Basic household attributes
        self.num_people = num_people # Target population for this household
        self.income_tax_rate = income_tax_rate
        
        # Financial metrics 
        self.household_step_income = 0
        self.household_step_income_posttax = 0
        self.household_step_expense = 0
        self.household_step_savings = 0
        self.wealth_bracket = None
        self.debt_level = 0
        self.necessity_spend_per_person = 57750
        self.total_household_savings = self.necessity_spend_per_person * self.num_people
        
        # Welfare and employment tracking
        self.health_level = 0
        self.welfare = 0
        self.num_working_people = 0 # This will be updated based on actual members
        self.num_not_seeking_job = 0 # This will be updated based on actual members
        self.num_seeking_job = 0 # This will be updated based on actual members
        
        # Store household members
        self.members = []
        self.current_population = 0 # Actual number of members added

    def _update_employment_counts(self):
        '''
        Update employment statistics for the household.
        
        Calculates how many household members are employed, job-seeking,
        or not participating in the labor market. These counts are used for
        household financial calculations and economic indicators.
        '''

        self.num_working_people = 0
        self.num_not_seeking_job = 0
        self.num_seeking_job = 0
        
        for member in self.members:
            if member.employer is not None:
                self.num_working_people += 1
            elif not member.job_seeking:
                self.num_not_seeking_job += 1
            else: 
                self.num_seeking_job += 1

    def _get_cheapest_firm(self, firm_category, candidate_firms=None):
        '''
        Find the cheapest firms in a category and select one randomly.
        
        This simulates households looking for good deals but not always finding
        the absolute cheapest option. The method selects from the cheapest 25% 
        of firms in the specified category that have inventory available.
        
        Parameters:
        - firm_category: The type of firm (e.g., "physical", "service", "technical")
        - candidate_firms: Optional list of firms to consider. If None, searches all model agents.
            
        Returns:
        - A randomly chosen firm from the cheapest 25% in that category with inventory,
          or None if no suitable firms available.
        '''
        
        if candidate_firms is None:
            # Find all firms of the specified category with price > 0 and inventory > 0
            firms_to_consider = [
                a for a in self.model.agents
                if hasattr(a, "firm_type") and a.firm_area == firm_category
                and hasattr(a, "product_price") and a.product_price > 0
                and hasattr(a, "inventory") and a.inventory > 0
            ]
        else:
            # Filter the provided candidates to ensure they still meet criteria
            firms_to_consider = [
                f for f in candidate_firms
                if hasattr(f, "firm_type") and f.firm_area == firm_category
                and hasattr(f, "product_price") and f.product_price > 0
                and hasattr(f, "inventory") and f.inventory > 0
            ]
        
        if not firms_to_consider:
            return None
            
        # Sort by price (cheapest first)
        firms_to_consider.sort(key=lambda f: f.product_price)
        
        # Take cheapest 25% of firms
        top_25_percent_count = max(1, int(len(firms_to_consider) * 0.25))
        cheapest_firms = firms_to_consider[:top_25_percent_count]
        
        # Choose one randomly from the cheapest firms
        return random.choice(cheapest_firms) if cheapest_firms else None

    def _calculate_cost_and_buy(self, firm_category, target_spend):
        '''
        Purchase goods from firms in a category, attempting to meet a spending target.
        
        This method implements the purchasing behavior of households, trying multiple 
        firms if necessary to reach the target spending amount. The selection of firms
        depends on the household's wealth bracket - low-wealth households prioritize
        cheaper options, while middle/high-wealth households are less price-sensitive.
        
        Parameters:
        - firm_category: The type of firm to buy from (e.g., "physical", "service")
        - target_spend: The target amount to spend in this category
            
        Returns:
        - The actual total amount spent in this category
        '''
        
        total_spent_for_category = 0.0
        remaining_spend_target = target_spend

        # Get a list of all firms initially eligible (price > 0, inventory > 0)
        potential_purchase_candidates = [
            a for a in self.model.agents
            if hasattr(a, "firm_type") and a.firm_area == firm_category
            and hasattr(a, "product_price") and a.product_price > 0
            and hasattr(a, "inventory") and a.inventory > 0
        ]
        
        random.shuffle(potential_purchase_candidates) # Shuffle to vary order for random picks

        # Attempt purchases while there's still budget and available firms
        while remaining_spend_target > 0.01 and potential_purchase_candidates:
            chosen_firm = None
            
            # Filter for candidates that still have inventory
            currently_available_firms = [f for f in potential_purchase_candidates if f.inventory > 0]
            if not currently_available_firms:
                break # No firms with inventory left in our candidate list

            # Firm selection based on wealth bracket
            if hasattr(self, 'wealth_bracket') and self.wealth_bracket in ["middle", "high"]:
                chosen_firm = random.choice(currently_available_firms)
            else: # Low wealth or wealth_bracket not set
                # Pass the currently_available_firms to _get_cheapest_firm
                # _get_cheapest_firm itself will sort them by price and pick from the cheapest 25%
                chosen_firm = self._get_cheapest_firm(firm_category, candidate_firms=currently_available_firms)
            
            if chosen_firm is None:
                break 

            # Calculate how many units to buy
            desired_units = 0
            if chosen_firm.product_price > 0:
                desired_units = int(remaining_spend_target / chosen_firm.product_price)
            
            if desired_units > 0:
                # Request goods from the firm
                actually_bought_units = chosen_firm.fulfill_demand_request(desired_units)
                
                if actually_bought_units > 0:
                    cost_this_transaction = actually_bought_units * chosen_firm.product_price
                    total_spent_for_category += cost_this_transaction
                    remaining_spend_target -= cost_this_transaction
            
            # Remove the chosen firm from candidates
            potential_purchase_candidates.remove(chosen_firm)

        return total_spent_for_category
    
    def _spend_on_luxuries(self, remaining_budget, percentage_range):
        '''
        Spend on luxury goods using a portion of the remaining budget.
        
        Middle and high-income households spend on luxury goods after meeting
        necessity needs. This method selects two random luxury categories and
        attempts to purchase from firms in those categories based on the specified
        percentage of the remaining budget.
        
        Parameters:
        - remaining_budget: The amount of money available after necessities
        - percentage_range: Tuple of (min_percent, max_percent) to spend
            
        Returns:
        - The total amount spent on luxuries
        '''
        
        if remaining_budget <= 0:
            return 0.0
            
        min_percent, max_percent = percentage_range
        spend_percent = random.uniform(min_percent, max_percent)
        total_luxury_budget_to_spend = remaining_budget * spend_percent
        
        # Define luxury categories
        luxury_types = ["technical", "social", "analytical", "creative"]
        if len(luxury_types) < 2:
            return 0.0 # Not enough types to choose from

        # Choose two luxury types to spend on
        chosen_luxury_types = random.sample(luxury_types, 2)
        
        if not chosen_luxury_types:
            return 0.0

        budget_per_luxury_type = total_luxury_budget_to_spend / len(chosen_luxury_types)
        total_actual_luxury_spent = 0.0
        
        # Try to spend on each chosen luxury type
        for l_type in chosen_luxury_types:
            spent_for_this_type = 0.0
            remaining_budget_for_this_type = budget_per_luxury_type

            # Find eligible firms for this luxury type
            potential_firms_for_type = [
                firm for firm in self.model.agents 
                if hasattr(firm, 'firm_area') and firm.firm_area == l_type
                and hasattr(firm, 'product_price') and firm.product_price > 0
                and hasattr(firm, 'inventory') and firm.inventory > 0
            ]
            random.shuffle(potential_firms_for_type)

            # Attempt purchases while budget and firms remain
            while remaining_budget_for_this_type > 0.01 and potential_firms_for_type:
                currently_available_firms = [f for f in potential_firms_for_type if f.inventory > 0]
                if not currently_available_firms:
                    break

                chosen_firm = random.choice(currently_available_firms)
                # chosen_firm is guaranteed to have product_price > 0 and inventory > 0 here

                desired_units = 0
                if chosen_firm.product_price > 0:
                    desired_units = int(remaining_budget_for_this_type / chosen_firm.product_price)
                
                if desired_units > 0:
                    actually_bought_units = chosen_firm.fulfill_demand_request(desired_units)

                    if actually_bought_units > 0:
                        actual_cost_this_transaction = actually_bought_units * chosen_firm.product_price
                        spent_for_this_type += actual_cost_this_transaction
                        remaining_budget_for_this_type -= actual_cost_this_transaction
                
                # Remove the chosen firm from candidates
                potential_firms_for_type.remove(chosen_firm)
            
            total_actual_luxury_spent += spent_for_this_type
                
        return total_actual_luxury_spent

    def step(self):
        '''
        Execute one simulation step for this household.
        
        This method handles the household's complete economic cycle:
        1. Updates income from employed household members
        2. Determines income and wealth brackets
        3. Allocates spending on necessities (physical and service goods)
        4. Allocates spending on luxuries based on wealth bracket
        5. Updates financial metrics and welfare indicators
        
        The step method is called by the model scheduler at each simulation step.
        '''

        # Update household income based on members' wages
        employed_members = [member for member in self.members if member.employer is not None]  
        self.household_step_income = sum(member.wage for member in employed_members)
          
        # Every household must attempt to spend the target amount on necessities
        total_necessity_target = self.necessity_spend_per_person * self.num_people

        # Determine income bracket based on multiples of the necessity threshold
        if self.household_step_income < total_necessity_target:
            self.income_bracket = "low"
        elif self.household_step_income < total_necessity_target*3:
            self.income_bracket = "middle"
        else:
            self.income_bracket = "high"

        # Calculate after-tax income
        self.household_step_income_posttax = self.household_step_income * (1 - self.income_tax_rate)

        # Determine wealth bracket based on total household savings and post tax income
        if self.total_household_savings + self.household_step_income_posttax < total_necessity_target*1.2:
            self.wealth_bracket = "low"
        elif self.total_household_savings + self.household_step_income_posttax < total_necessity_target*4:
            self.wealth_bracket = "middle"
        else:
            self.wealth_bracket = "high"
            

        # ---------- NECESSITY SPENDING ----------
        
        # Calculate total available funds (post-tax income + savings)
        available_funds = self.household_step_income_posttax + self.total_household_savings
        
        # Households attempt to spend up to their necessity target using all available funds
        attemptable_necessity_budget = min(total_necessity_target, available_funds)

        physical_spent = 0
        service_spent = 0

        # Target for physical goods is roughly half of what they can attempt to spend.
        physical_target_for_attempt = max(0.0, attemptable_necessity_budget * 0.5)
        
        if physical_target_for_attempt > 0.01: # Only attempt if target is meaningful
            physical_spent = self._calculate_cost_and_buy("physical", physical_target_for_attempt)

        # Target for service goods is whatever is left of their attemptable budget
        service_target_for_attempt = max(0.0, attemptable_necessity_budget - physical_spent)
        
        if service_target_for_attempt > 0.01: # Only attempt if target is meaningful
            service_spent = self._calculate_cost_and_buy("service", service_target_for_attempt)
        
        total_necessity_spent = physical_spent + service_spent
        
        # ---------- LUXURY SPENDING ----------
        # Calculate remaining funds after necessity spending
        remaining_funds = available_funds - total_necessity_spent
        
        # Initialize luxury spending amount
        luxury_spent = 0.0
        
        # Determine luxury spending based on wealth bracket
        if self.wealth_bracket == "low":
            # Low income households don't buy luxury items
            pass
        elif self.wealth_bracket == "middle" and remaining_funds > 0:
            # Middle income: spend 60-100% of remaining budget on luxuries
            luxury_spent = self._spend_on_luxuries(remaining_funds, (0.6, 1.0))
        elif self.wealth_bracket == "high" and remaining_funds > 0:
            # High income: spend 80-100% of remaining budget on luxuries
            luxury_spent = self._spend_on_luxuries(remaining_funds, (0.8, 1.0))
        
        # ---------- UPDATE FINANCIAL METRICS ----------
        # Total expenses = necessities + luxuries
        self.household_step_expense = total_necessity_spent + luxury_spent
        
        # Update savings: available funds minus all spending
        self.total_household_savings = available_funds - self.household_step_expense

        # Monitor debt levels
        if self.total_household_savings < 0:
            self.debt_level = abs(self.total_household_savings)
        else:
            self.debt_level = 0

        #   print(f"[DEBUG] Household {self.unique_id} - Total household savings: {self.total_household_savings}, Debt level: {self.debt_level}")

        # Calculate necessity fulfillment percentage
        necessity_fulfillment = min(1.0, total_necessity_spent / (total_necessity_target - 5000)) if total_necessity_target > 0 else 1.0
        
        # Increment model counter if necessity goal not met
        if total_necessity_target > 0 and necessity_fulfillment < 1.0:
            self.model.unmet_necessity_households_count += 1

        if total_necessity_target > 0.01 and necessity_fulfillment < 0.999: # using 0.999 to account for potential small float inaccuracies
            print(f"[INFO] Household {self.unique_id} (Income: {self.income_bracket}, Wealth: {self.wealth_bracket}) did NOT meet necessity target. Target: {total_necessity_target:.2f}, Spent: {total_necessity_spent:.2f}, Shortfall: {total_necessity_target - total_necessity_spent:.2f}")
            
        # Set base health level based on wealth bracket
        if self.wealth_bracket == "low":
            base_health = 35
        elif self.wealth_bracket == "middle":
            base_health = 70
        else:
            base_health = 100
            
        # Adjust health level based on necessity fulfillment
        self.health_level = base_health * necessity_fulfillment
        
        # Calculate overall welfare with necessity fulfillment impact
        self.welfare = (self.household_step_income_posttax * 0.3 + 
                        self.household_step_expense * 0.2 + 
                        self.total_household_savings * 0.2 + 
                        self.health_level * 0.3)
