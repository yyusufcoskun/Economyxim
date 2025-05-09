import mesa
import numpy as np
import pandas as pd
import random


class FirmAgent(mesa.Agent):
    def __init__(self, model, product, firm_type, firm_area, 
                 production_capacity, production_cost, markup,
                 entry_wage, num_employees, production_level=1):
        super().__init__(model)
        # print(f"[DEBUG] Assigned production_level for {self.unique_id}: {production_level}")

        # Basic firm identity and characteristics
        self.product = product
        self.firm_type = firm_type
        self.firm_area = firm_area
        
        # Production parameters
        self.production_capacity = production_capacity
        self.production_level = production_level
        self.production_cost = max(1.0, production_cost)  # Ensure minimum production cost
        self.produced_units = 0  # Track units produced
        
        # Pricing and financial parameters
        self.capital = 0 # TODO give initial capital to all firms
        self.markup = markup
        self.product_price = self.production_cost * (1 + markup)  # Initialize with a non-zero price
        self.min_price = self.production_cost * 1.05  # Minimum 5% above production cost
        self.revenue = 0
        self.costs = 0
        self.profit = 0
        self.last_step_profit = None  # Profit from the previous step
        
        # Inventory and demand tracking
        self.inventory = self.production_capacity * 0.1  # Initialize with some inventory
        self.demand_received = 0  # Demand received from households
        self.unmet_demand = 0
        self.demand_history = []
        self.demand_history_length = 5  # How many steps to track
        self.average_demand = 0  # Track average demand (will be calculated)
        
        # Employee related parameters
        self.num_employees = num_employees
        self.entry_wage = entry_wage
        self.wage_multipliers = {"entry": 1.0, "mid": 1.4, "senior": 2.0}
        self.revenue_per_employee = 0
        self.last_step_revenue_per_emp = None        

        # Configurations for hiring logic (moved from hire_new_employee)

        # Skill mix ratios for each firm area
        self.skill_mix_config = {
            "technical": {"senior": 0.25, "mid": 0.60, "entry": 0.15},  # Engineering, IT, technical roles need more senior expertise
            "creative": {"senior": 0.25, "mid": 0.45, "entry": 0.30},   # Design/arts benefit from fresh perspectives but need experienced guidance
            "physical": {"senior": 0.10, "mid": 0.35, "entry": 0.55},   # Manufacturing/construction has more entry-level positions
            "social": {"senior": 0.20, "mid": 0.50, "entry": 0.30},     # Management/teaching needs experienced leaders
            "analytical": {"senior": 0.25, "mid": 0.55, "entry": 0.20}, # Finance/data analysis requires more expertise
            "service": {"senior": 0.10, "mid": 0.40, "entry": 0.50},    # Service industry has more entry-level positions
        }

        # Skill matching for each firm area
        self.skill_type_matching_config = {
            "technical": "technical",
            "creative": "creative",
            "physical": "physical", 
            "social": "social",
            "analytical": "analytical",
            "service": "service",
        }

        # Minimum skill levels for each area and job level
        self.min_skill_levels_config = {
            "technical": {"senior": 80, "mid": 60, "entry": 40},
            "creative": {"senior": 70, "mid": 50, "entry": 30}, 
            "physical": {"senior": 60, "mid": 40, "entry": 10},
            "social": {"senior": 70, "mid": 50, "entry": 30},
            "analytical": {"senior": 80, "mid": 60, "entry": 30},
            "service": {"senior": 60, "mid": 40, "entry": 20},
        }

        # Weights for demand averaging
        # Must correspond to self.demand_history_length
        self.demand_averaging_weights = [0.1, 0.15, 0.2, 0.25, 0.3]

        # Debug output
        print(f"[DEBUG] Firm {self.unique_id} ({firm_type}/{firm_area}) initialized with price: {self.product_price:.2f}")
    

    def receive_demand(self, units):
        """Record demand received from households."""
        #print(f"[DEBUG] Firm {self.unique_id} ({self.firm_type}/{self.firm_area}) received demand for {units} units, price: {self.product_price:.2f}")
        self.demand_received += units  # used by household

    def adjust_production(self, sold_units):
        """Adjust production level based on inventory and demand trends."""
        if len(self.demand_history) == 0:
            return  # Not enough history yet
        
        # Target inventory is just the average demand
        target_inventory = self.average_demand * 1.3
        
        # Calculate how much we need to produce
        inventory_gap = target_inventory - self.inventory
        
        # If gap is positive, we need to produce more
        # If gap is negative, we don't produce
        if inventory_gap > 0:
            # Calculate how much of capacity to use
            needed_production = inventory_gap
            self.production_level = min(needed_production / self.labor_added_production_capacity, 1.0)
        else:
            # Don't produce if we already have enough inventory
            self.production_level = 0.1
        
        # Ensure production level stays within bounds (allowing 0.0 now)
        self.production_level = min(max(self.production_level, 0.1), 1.0)

    def adjust_price(self, sold_units, produced_units, cost_per_unit):
        """Adjust price based on market conditions and demand trends."""
        if produced_units == 0:
            return
        
        # Key market indicators
        inventory_demand_ratio = self.inventory / (self.demand_received + 1e-6)  # how much inventory compared to demand
        sell_through_rate = sold_units / (produced_units + 1e-6)  # what percentage of new products are sold

        # Calculate demand trend from history
        if len(self.demand_history) >= 2:
            # Last 2 steps trend
            short_term_trend = self.demand_history[-1] / (self.demand_history[-2] + 1e-6) - 1
            
            # Full history trend
            if len(self.demand_history) == self.demand_history_length:
                earliest_demand = sum(self.demand_history[:2]) / 2  # average of first two entries
                latest_demand = sum(self.demand_history[-2:]) / 2   # average of last two entries
                long_term_trend = (latest_demand / (earliest_demand + 1e-6)) - 1
            else:
                long_term_trend = 0
        else:
            short_term_trend = 0
            long_term_trend = 0

        market_pressure = 0.0  # -1 to 1 ----- negative means downward price pressure, price drops

        # Adjust market pressure based on inventory levels
        if inventory_demand_ratio > 2.0:  # inventory is more than 2 times of demand
            market_pressure -= 0.6  # price wants to drop
        elif inventory_demand_ratio > 1.5:
            market_pressure -= 0.4
        elif inventory_demand_ratio < 0.5:  # demand is twice as much as inventory
            market_pressure += 0.2  # price wants to rise so that stock lasts
        elif inventory_demand_ratio < 0.2:  # demand is 5 times as much as inventory
            market_pressure += 0.4

        # Adjust market pressure based on sales performance
        if sell_through_rate < 0.4:  # poor sales
            market_pressure -= 0.6
        elif sell_through_rate > 0.9:
            market_pressure += 0.3

        # Adjust market pressure based on demand trends
        if short_term_trend < -0.2:  # Sharp recent decline
            market_pressure -= 0.15
        elif short_term_trend > 0.2:  # Sharp recent increase
            market_pressure += 0.15

        if long_term_trend < -0.1:  # Sustained decline
            market_pressure -= 0.1
        elif long_term_trend > 0.1:  # Sustained growth
            market_pressure += 0.1

        # Cap market_pressure between -1 and 1
        market_pressure = max(-1.0, min(market_pressure, 1.0))

        markup_change = market_pressure*0.5
        
        self.markup += markup_change
        self.markup = max(0.01, self.markup)
        
        ''' # make sure profit margin stays realistic
        if self.firm_type == "necessity":
            self.markup = max(min(self.markup, 0.1), 0.35) # 10-35% margin
        '''
        '''
        else:  # necessity
            self.markup = max(min(self.markup, 0.25), 0.05)  # 5-25% margin
        '''

        # Update product price
        old_price = self.product_price
        calculated_price = self.production_cost * (1 + self.markup)
        self.product_price = max(calculated_price, self.min_price)
        #print(f"[DEBUG] Firm {self.unique_id} price calculation in adjust_price: costs: {self.costs:.2f}, produced: {produced_units}, " + 
              #f"cost_per_unit: {cost_per_unit:.2f}, markup: {self.markup:.2f}, " +
              #f"old price: {old_price:.2f}, new price: {self.product_price:.2f}")

    def adjust_employees(self):
        """Adjust number of employees based on revenue per employee."""

        # TODO make this last 2 steps instead of just last step
        if self.last_step_revenue_per_emp is None:
            return

        # Print debug values to see why firing isn't happening
        #print(f"[DEBUG] Firm {self.unique_id}: Last step rev/emp: {self.last_step_revenue_per_emp:.2f}, Current rev/emp: {self.revenue_per_employee:.2f}")
        #print(f"[DEBUG] Firm {self.unique_id}: Should fire? {self.last_step_revenue_per_emp > self.revenue_per_employee}")

        if self.last_step_revenue_per_emp > self.revenue_per_employee:
            # FIRING: fires least productive employee (hours*skill)
            #print(f"[DEBUG] Firm {self.unique_id} attempting to fire employee...")
            self.fire_least_productive()
            self.num_employees = max(1, self.num_employees - 1)
        else:
            # HIRING
            self.hire_new_employee()
            self.num_employees += 1

    

    def fire_least_productive(self):
        """Fire the employee with lowest productivity (skill * work_hours / wage)."""
        # Get all person agents that work for this firm
        employees = [agent for agent in self.model.agents 
                    if hasattr(agent, 'employer') and agent.employer == self]
        
        if not employees:
            #print(f"[DEBUG] Firm {self.unique_id}: No employees to fire.")
            return  # No employees to fire
        
       # print(f"[DEBUG] Firm {self.unique_id}: Found {len(employees)} employees")
        
        # Calculate productivity for each employee
        employee_productivity = []
        
        for person in employees:
            # All employees in this firm will have the same skill type matching the firm type
            # So we can directly use their skill_level
            
            # Get skill level   
            skill_level = person.skill_level
            labor = person.labor
            
            # Calculate productivity score
            productivity = (skill_level * labor) / (person.wage + 1e-6)
            employee_productivity.append((productivity, person))
        
        # Sort by productivity (lowest first), using only the first element of each tuple
        employee_productivity.sort(key=lambda x: x[0])
        
        # Fire the least productive employee
        if employee_productivity:
            _, person_to_fire = employee_productivity[0]
            
            # Get their job level for reporting
            job_level = person_to_fire.job_level if hasattr(person_to_fire, 'job_level') else "unknown"
            
            # Update person's employment status
            person_to_fire.employer = None
            person_to_fire.wage = 0
            person_to_fire.job_seeking = True
            
            #print(f"Firm {self.unique_id} fired Person {person_to_fire.unique_id} with job level {job_level} and productivity {employee_productivity[0][0]:.2f}")
        else:
            #print(f"[DEBUG] Firm {self.unique_id}: No employee productivity list generated.")
            pass

    

    def hire_new_employee(self):
        """Hire a new employee with appropriate skills for this firm area."""
        
        # Get current employees and their levels
        employees = [agent for agent in self.model.agents 
                    if hasattr(agent, 'employer') and agent.employer == self]
        
        current_mix = {
            "senior": 0,
            "mid": 0, 
            "entry": 0
        }
        
        # Keep track of previously employed people to avoid rehiring them
        if not hasattr(self, 'previous_employees'):
            self.previous_employees = set()
            
        # Get thresholds for this firm area
        # Example: if self.firm_area is "tech" and job_level is "senior":
        # firm_levels = min_skill_levels["tech"] = {"senior": 0.8, "mid": 0.6, "entry": 0.4}
        firm_levels = self.min_skill_levels_config.get(self.firm_area, self.min_skill_levels_config["physical"])
        
        # Count current employees at each level using area-specific thresholds
        for emp in employees:
            if hasattr(emp, 'job_level') and emp.job_level is not None:
                current_mix[emp.job_level] += 1
            else:
                # Categorize based on skill thresholds for this area
                if emp.skill_level >= firm_levels["senior"]:
                    current_mix["senior"] += 1
                elif emp.skill_level >= firm_levels["mid"]:
                    current_mix["mid"] += 1
                else:
                    current_mix["entry"] += 1
                
        # Calculate percentages
        total = len(employees) + 1  # Add 1 for new hire
        target_mix = self.skill_mix_config.get(self.firm_area, self.skill_mix_config["physical"])
        
        # Determine which level needs hiring to get closer to target mix
        differences = {}
        # Calculate the difference between target and current percentage for each level
        for level in ["senior", "mid", "entry"]:
            # Get current percentage of employees at this level (or 0 if no employees)
            current_pct = current_mix[level] / total if total > 0 else 0
            # Get target percentage for this level from skill_mix
            target_pct = target_mix[level]
            # Store how far we are from target (positive means we need more at this level)
            differences[level] = target_pct - current_pct
            
        # Choose the level with the highest difference (most needed)
        job_level = max(differences, key=differences.get)
        
        # Get minimum skill level for this level from firm area
        min_skill_level = firm_levels[job_level]
        
        # Get the matching skill type for this firm area
        matching_skill_type = self.skill_type_matching_config.get(self.firm_area, "physical")
        
        # Find candidates with matching skill type
        matching_candidates = [agent for agent in self.model.agents 
                      if hasattr(agent, 'job_seeking') and agent.job_seeking 
                      and agent.skill_level >= min_skill_level
                      and hasattr(agent, 'skill_type') and agent.skill_type == matching_skill_type
                      and agent.unique_id not in self.previous_employees]
        
        # If no matching candidates, look for any job-seeking agent with sufficient skill
        candidates = matching_candidates
        if not matching_candidates:
            candidates = [agent for agent in self.model.agents 
                        if hasattr(agent, 'job_seeking') and agent.job_seeking
                        and agent.skill_level >= min_skill_level - 10
                        and agent.unique_id not in self.previous_employees]
            
        # Hire one of the most qualified candidates
        if candidates:
            # Sort by skill level
            candidates.sort(key=lambda p: p.skill_level, reverse=True)
            
            # Consider the top half of candidates (with a minimum of at least one person)
            top_candidate_count = max(1, len(candidates) // 2)
            top_candidates = candidates[:top_candidate_count]
            
            # Randomly select from top candidates
            person_to_hire = random.choice(top_candidates)
            
            # Determine wage based on skill level and job level
            base_wage = self.entry_wage * self.wage_multipliers[job_level]
            skill_bonus = person_to_hire.skill_level * 0.03 * base_wage
            offered_wage = base_wage + skill_bonus
            
            # Update person's employment status
            person_to_hire.employer = self
            person_to_hire.wage = offered_wage
            person_to_hire.job_seeking = False
            
            # Add to previous employees set to avoid rehiring
            self.previous_employees.add(person_to_hire.unique_id)
            
            # Keep the set from growing too large
            if len(self.previous_employees) > 100:
                # Remove oldest entries
                for _ in range(10):
                    if self.previous_employees:
                        self.previous_employees.pop()
            
            # Set the job level
            person_to_hire.job_level = job_level
            
            #print(f"Firm {self.unique_id} hired Person {person_to_hire.unique_id} as {job_level} level with skill {person_to_hire.skill_level:.2f}")


    def calculate_total_wage_cost(self):
        """Calculate the total wage costs by summing individual wages of all employees."""
        # Get all employees
        employees = [agent for agent in self.model.agents 
                    if hasattr(agent, 'employer') and agent.employer == self]
        
        # Sum all wages
        if employees:
            total_wages = sum(emp.wage for emp in employees)
            return total_wages
        else:
            # If no employees found, estimate based on entry wage and num_employees
            return self.entry_wage * self.num_employees


    def _calculate_total_labor(self):
        """Calculate the total labor value from all employees."""
        employees = [agent for agent in self.model.agents 
                    if hasattr(agent, 'employer') and agent.employer == self]
        
        self.total_labor = 0
        if employees:
            self.total_labor = sum(emp.labor for emp in employees)
        return self.total_labor

    def step(self):
        """Execute one step of the firm's operations."""
        # Producing goods and adding them to the inventory
        added_labor = self._calculate_total_labor()
        
        self.labor_added_production_capacity = self.production_capacity + added_labor
        
        self.produced_units = round(self.labor_added_production_capacity * self.production_level)
        self.inventory += self.produced_units

        wage_costs = self.calculate_total_wage_cost()
        production_costs = self.production_cost * self.produced_units
        self.costs = wage_costs + production_costs
        
        # Ensure cost_per_unit is not zero to avoid zero prices
        cost_per_unit = self.costs / (self.produced_units + 1e-6)

        # Sell products
        sold_units = min(self.demand_received, self.inventory)
        self.revenue = self.product_price * sold_units
        self.inventory -= sold_units

        # Profit
        self.profit = self.revenue - self.costs
        self.capital += self.profit
        
        # Calculate unmet demand
        self.unmet_demand = self.demand_received - sold_units # Demand received this step MINUS what was sold
        
        # Update the revenue per employee
        self.revenue_per_employee = self.revenue / max(self.num_employees, 1) # Avoid division by zero
        
        
        # The first step, initialize last_step_revenue_per_emp with current value
        if self.last_step_revenue_per_emp is None:
            self.last_step_revenue_per_emp = self.revenue_per_employee
        
        # Make adjustments
        self.adjust_price(sold_units, self.produced_units, cost_per_unit)
        self.adjust_production(sold_units)
        self.adjust_employees()

        # Update historical metrics
        self.last_step_revenue_per_emp = self.revenue_per_employee

        # Update demand history
        self.demand_history.append(self.demand_received)
        if len(self.demand_history) > self.demand_history_length:
            self.demand_history.pop(0)  # remove oldest entry
        
        # Calculate moving average with weights (more recent demand counts more)
        if len(self.demand_history) == self.demand_history_length:
            self.average_demand = sum(d * w for d, w in zip(self.demand_history, self.demand_averaging_weights))
        else:
            # If we don't have enough history yet, use simple average
            self.average_demand = sum(self.demand_history) / len(self.demand_history)
        
        # Reset demand for next step
        self.demand_received = 0
