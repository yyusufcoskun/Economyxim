import mesa
import numpy as np
import pandas as pd
import random
from .person_agent import PersonAgent


class HouseholdAgent(mesa.Agent):
    """
    Represents a household in the economy simulation.
    
    A household contains multiple people who can work and earn income.
    The household makes consumption decisions based on total income and preferences.
    """
    
    def __init__(self, model, num_people, income_tax_rate=0.15):
        """
        Initialize a new household.
        
        Args:
            model: The model instance this household belongs to
            num_people: Number of people in this household
            income_tax_rate: Rate of income tax applied to household income
        """
        super().__init__(model)

        # Basic household attributes
        self.num_people = num_people
        self.total_household_income = 0
        self.income_tax_rate = income_tax_rate # TODO: Assign correct tax rate at creation time
        
        # Financial metrics 
        self.total_income_posttax = 0
        self.total_household_expense = 0
        self.total_household_savings = 0
        
        # Welfare and employment tracking
        self.health_level = 0
        self.welfare = 0
        self.num_working_people = 0
        self.num_not_seeking_job = 0
        self.num_seeking_job = self.num_people - self.num_working_people - self.num_not_seeking_job
        
        # Create and store household members
        self.members = []
        for i in range(num_people):
            person = PersonAgent(self.model, self, job_seeking=True, wage=0, work_hours=40)
            self.members.append(person)

    def _get_cheapest_firm(self, firm_category):
        """
        Find the cheapest 20% of firms in a category and randomly select one.
        
        This simulates households looking for good deals but not always finding
        the absolute cheapest option.
        
        Args:
            firm_category: The type of firm (e.g., "physical", "service", "technical")
            
        Returns:
            A randomly chosen firm from the cheapest 20% in that category, or None if no firms available
        """
        # Find all firms of the specified category
        firms_in_category = [
            a for a in self.model.agents
            if hasattr(a, "firm_type") and a.firm_area == firm_category
            and hasattr(a, "product_price") and a.product_price > 0
        ]
        
        if not firms_in_category:
            return None
            
        # Sort by price (cheapest first)
        firms_in_category.sort(key=lambda f: f.product_price)
        
        # Take cheapest 20% of firms
        top_20_percent_count = max(1, int(len(firms_in_category) * 0.2))
        cheapest_firms = firms_in_category[:top_20_percent_count]
        
        # Choose one randomly from the cheapest firms
        return random.choice(cheapest_firms)

    def _calculate_cost_and_buy(self, firm_category, target_spend):
        """
        Calculate cost and buy goods from a firm in a category.
        
        Used for MANDATORY necessity spending that households must make regardless
        of their financial situation.
        - All households look for the cheapest firms for necessities
        
        Args:
            firm_category: The type of firm to buy from
            target_spend: The target amount to spend
            
        Returns:
            The actual amount spent
        """
        # Debug how many firms are available with prices > 0
        firms_in_category = [
            a for a in self.model.agents
            if hasattr(a, "firm_type") and a.firm_area == firm_category
            and hasattr(a, "product_price") and a.product_price > 0
        ]
        print(f"[DEBUG] Household {self.unique_id} found {len(firms_in_category)} {firm_category} firms with price > 0")
        
        # All households look for the cheapest options for necessities
        chosen_firm = self._get_cheapest_firm(firm_category)
        
        if chosen_firm is None:
            print(f"[DEBUG] Household {self.unique_id} couldn't find any {firm_category} firms to buy from")
            return 0.0
            
        # Calculate how many units to buy based on the target spend
        if chosen_firm.product_price > 0:
            units_to_buy = int(target_spend / chosen_firm.product_price)
            print(f"[DEBUG] Household {self.unique_id} buying {units_to_buy} units from {firm_category} firm {chosen_firm.unique_id} at price {chosen_firm.product_price:.2f}")
        else:
            units_to_buy = 0
            print(f"[DEBUG] Household {self.unique_id} found {firm_category} firm {chosen_firm.unique_id} with zero price")
            
        if units_to_buy > 0:
            actual_cost = units_to_buy * chosen_firm.product_price
            chosen_firm.receive_demand(units_to_buy)
            return actual_cost
        else:
            return 0.0
    
    def _spend_on_luxuries(self, remaining_budget, percentage_range):
        """
        Spend on luxury items using a percentage of the remaining budget.
        
        Middle and high income households spend on 2 randomly selected types of
        luxury goods with a variable portion of their income.
        
        Args:
            remaining_budget: The amount of money available after necessities
            percentage_range: Tuple of (min_percent, max_percent) to spend
            
        Returns:
            The total amount spent on luxuries
        """
        if remaining_budget <= 0:
            return 0.0
            
        # Determine percentage of remaining budget to spend on luxuries
        min_percent, max_percent = percentage_range
        spend_percent = random.uniform(min_percent, max_percent)
        luxury_budget = remaining_budget * spend_percent
        
        luxury_types = ["technical", "social", "analytical", "creative"]
            
        # Randomly select 2 luxury types to purchase from
        chosen_luxury_types = random.sample(luxury_types, 2)
        
        # Split luxury budget equally between the two types
        budget_per_luxury = luxury_budget / 2
        total_luxury_spent = 0.0
        
        # Spend on each chosen luxury type
        for l_type in chosen_luxury_types:
            '''
            # Previous approach: Get cheapest firm
            chosen_firm = self._get_cheapest_firm(l_type)
            '''
            matching_firms = [firm for firm in self.model.agents 
                            if hasattr(firm, 'firm_area') and firm.firm_area == l_type]
            
            if not matching_firms:
                continue
                
            chosen_firm = random.choice(matching_firms)
            
            if chosen_firm is None:
                continue
                
            # Calculate units to buy based on allocated budget
            if chosen_firm.product_price > 0:
                units_to_buy = int(budget_per_luxury / chosen_firm.product_price)
            else:
                units_to_buy = 0
                
            if units_to_buy > 0:
                actual_cost = units_to_buy * chosen_firm.product_price
                chosen_firm.receive_demand(units_to_buy)
                total_luxury_spent += actual_cost
                
        return total_luxury_spent

    def step(self):
        """
        Execute one simulation step for this household.
        
        This method:
        1. Updates income from employed household members
        2. Determines income bracket
        3. Spends on necessities (physical and service goods)
        4. Spends on luxuries depending on income bracket
        5. Updates financial metrics and welfare
        """
        # Update household income based on members' wages
        employed_members = [member for member in self.members if member.employer is not None]  
        self.total_household_income = sum(member.wage for member in employed_members)

        # Each person requires 19250 in necessity spending a month, split 50/50 between physical and service
        necessity_spend_per_person = 57750  

        # Determine income bracket based on multiples of the necessity threshold
        if self.total_household_income < necessity_spend_per_person*self.num_people:
            self.income_bracket = "low"
        elif self.total_household_income < necessity_spend_per_person*self.num_people*3:
            self.income_bracket = "middle"
        else:
            self.income_bracket = "high"
            
        # Calculate after-tax income
        self.total_income_posttax = self.total_household_income * (1 - self.income_tax_rate)
        
        # ---------- NECESSITY SPENDING ----------
        # Every household must attempt to spend the target amount on necessities
        total_necessity_target = necessity_spend_per_person * self.num_people
        
        # Split necessity budget between physical goods and services (50/50)
        physical_target = total_necessity_target * 0.5
        service_target = total_necessity_target * 0.5
        
        # Make mandatory purchases for necessities
        physical_spent = self._calculate_cost_and_buy("physical", physical_target)
        service_spent = self._calculate_cost_and_buy("service", service_target)
        
        # Total necessity spending
        total_necessity_spent = physical_spent + service_spent
        
        # ---------- LUXURY SPENDING ----------
        # Calculate remaining budget after necessity spending (can be negative)
        remaining_budget = self.total_income_posttax - total_necessity_spent
        
        # Initialize luxury spending amount
        luxury_spent = 0.0
        
        # Determine luxury spending based on income bracket
        if self.income_bracket == "low":
            # Low income households don't buy luxury items
            pass
        elif self.income_bracket == "middle" and remaining_budget > 0:
            # Middle income: spend 50-100% of remaining budget on luxuries
            luxury_spent = self._spend_on_luxuries(remaining_budget, (1.0, 1.0))
        elif self.income_bracket == "high" and remaining_budget > 0:
            # High income: spend 80-100% of remaining budget on luxuries
            luxury_spent = self._spend_on_luxuries(remaining_budget, (1.0, 1.0))
        
        # ---------- UPDATE FINANCIAL METRICS ----------
        # Total expenses = necessities + luxuries
        self.total_household_expense = total_necessity_spent + luxury_spent
        
        # Savings can be negative if spending exceeds income
        self.total_household_savings = self.total_income_posttax - self.total_household_expense
        
        # Set health level based on income bracket
        if self.income_bracket == "low":
            self.health_level = 35
        elif self.income_bracket == "middle":
            self.health_level = 70
        else:
            self.health_level = 100
        
        # Calculate overall welfare (weighted combination of factors)
        self.welfare = (self.total_income_posttax * 0.3 + 
                        self.total_household_expense * 0.2 + 
                        self.total_household_savings * 0.2 + 
                        self.health_level * 0.3)
