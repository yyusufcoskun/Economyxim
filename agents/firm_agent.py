import mesa
import numpy as np
import pandas as pd
import random
from .intermediary_firm_agent import IntermediaryFirmAgent


class FirmAgent(mesa.Agent):
    '''
    Represents a business entity that produces and sells products in the economy.
    
    This agent is responsible for managing production, pricing, inventory, and workforce.
    It responds to market conditions by adjusting production levels, prices, and employee count.
    The agent interacts with household agents (as consumers and workers) and the government agent.
    '''
    
    def __init__(self, model, product, firm_type, firm_area, 
                 production_capacity, production_cost, markup,
                 entry_wage, initial_employee_target, production_level=1):

        '''
        Initialize a new firm with production capabilities and financial parameters.
        
        Parameters:
        - model: Mesa model instance the agent belongs to
        - product: Type of product the firm produces
        - firm_type: Category of firm (e.g., "luxury" or "necessity")
        - firm_area: Area of expertise/industry (e.g., "technical", "creative")
        - production_capacity: Base production capacity (units per step)
        - production_cost: Base cost per unit produced
        - markup: Initial profit margin percentage
        - entry_wage: Starting wage for entry-level employees
        - initial_employee_target: Target number of initial employees
        - production_level: Initial production level (0.0-1.0)
        '''
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
        self.capital = 1000000 
        self.markup = markup
        self.price_one_step_ago = 0
        self.price_two_steps_ago = 0
        self.min_price = 0
        self.revenue = 0
        self.costs = 0
        self.profit = 0
        self.last_step_profit = None  
        self.units_sold_this_step = 0 
        self.total_requested_this_step = 0 
        self.profit_history = [] 
        self.profit_history_length = 4 
        self.tax_paid_this_step = 0.0 
        
        # Inventory and demand tracking
        self.inventory = self.production_capacity*2 
        self.unmet_demand = 0
        self.demand_history = []
        self.demand_history_length = 5 
        self.average_demand = 0  # Track average demand
        
        # Employee related parameters
        self.employees = []
        self.num_employees = 0
        self.entry_wage = entry_wage # REVERT to using original entry_wage
        self.wage_multipliers = {"entry": 1.0, "mid": 1.4, "senior": 2.0}
        self.revenue_per_employee = 0
        self.last_step_revenue_per_emp = None        

        # Configurations for hiring logic

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

        # Populate initial workforce first to determine initial labor costs
        self._populate_initial_workforce(initial_employee_target)

        # Calculate initial costs and price based on the initial workforce
        initial_wage_costs = self.calculate_total_wage_cost()
        initial_added_labor = self._calculate_total_labor()
        
        # Estimate initial production based on initial labor and production level
        initial_labor_added_capacity = self.production_capacity + initial_added_labor
        initial_produced_units = round(initial_labor_added_capacity * self.production_level)
        
        initial_material_costs = self.production_cost * initial_produced_units
        initial_total_costs = initial_wage_costs + initial_material_costs
        
        if initial_produced_units > 0:
            initial_cost_per_unit = initial_total_costs / initial_produced_units
        else:
            initial_cost_per_unit = self.production_cost 

        self.product_price = initial_cost_per_unit * (1 + self.markup)
        self.min_price = initial_cost_per_unit * 1.05 # Min price based on initial cost per unit

        # Now set historical prices based on the calculated initial product_price
        self.price_one_step_ago = self.product_price
        self.price_two_steps_ago = self.product_price

        # Add employee adjustment cooldown - only adjust every 2 steps
        self.employee_adjustment_cooldown = 0  # 0 means can adjust this step

        # Debug output
        print(f"[DEBUG] Firm {self.unique_id} ({firm_type}/{firm_area}) initialized with price: {self.product_price:.2f}, initial_cost_per_unit: {initial_cost_per_unit:.2f}")
    
    def _populate_initial_workforce(self, target_count):
        '''
        Hires the initial set of employees for the firm based on skill mix requirements.
        
        This method is called during initialization to establish the firm's starting workforce.
        It selects appropriate employees from the available pool based on the firm's industry
        requirements and assigns them appropriate job levels and wages.
        
        Parameters:
        - target_count: Desired number of employees to hire
        '''
        
        # print(f"[DEBUG] Firm {self.unique_id} ({self.firm_area}): Populating initial workforce. Target: {target_count}")
        if not hasattr(self.model, 'available_persons') or not self.model.available_persons:
            print(f"[WARNING] Firm {self.unique_id}: No available persons in model to hire from for initial workforce.")
            return

        firm_skill_mix = self.skill_mix_config.get(self.firm_area)
        if not firm_skill_mix:
            print(f"[WARNING] Firm {self.unique_id}: No skill mix config found for firm area {self.firm_area}.")
            return

        target_skill_type = self.skill_type_matching_config.get(self.firm_area)
        if not target_skill_type:
            print(f"[WARNING] Firm {self.unique_id}: No skill type matching config for firm area {self.firm_area}.")
            return

        min_skill_levels_for_area = self.min_skill_levels_config.get(self.firm_area)
        if not min_skill_levels_for_area:
            print(f"[WARNING] Firm {self.unique_id}: No min skill levels config for firm area {self.firm_area}.")
            return
            
        total_hired_count = 0

        for job_level, percentage_for_level in firm_skill_mix.items():
            if total_hired_count >= target_count:
                break 

            # Calculate target number to hire for this job level
            num_to_hire_for_level = round(target_count * percentage_for_level)
            # print(f"[DEBUG] Firm {self.unique_id}: Targeting {num_to_hire_for_level} for job level '{job_level}'.")
            if num_to_hire_for_level == 0:
                continue
                
            hired_for_level_count = 0
            min_skill_for_job_level = min_skill_levels_for_area.get(job_level)
            if min_skill_for_job_level is None:
                print(f"[WARNING] Firm {self.unique_id}: No min skill level for job '{job_level}' in area {self.firm_area}.")
                continue

            # Find candidates with appropriate skills
            possible_hires = []
            for p_idx, p in enumerate(list(self.model.available_persons)): # Iterate over a copy for safe removal
                if p.job_seeking is True and \
                   p.employer is None and \
                   p.skill_type == target_skill_type and \
                   p.skill_level >= min_skill_for_job_level:
                    possible_hires.append(p)
            
            # Randomize candidate order for fair selection
            random.shuffle(possible_hires)

            # Hire candidates until target for this level is reached
            for candidate in possible_hires:
                if hired_for_level_count >= num_to_hire_for_level or total_hired_count >= target_count:
                    break
                
                # Double check availability before hiring, in case another firm hired this person
                # This can happen if not removing immediately from global list in this function
                if candidate.employer is None and candidate.job_seeking is True:
                    candidate.employer = self
                    candidate.job_seeking = False
                    candidate.job_level = job_level
                    wage_multiplier_for_level = self.wage_multipliers.get(job_level, 1.0)
                    candidate.wage = self.entry_wage * wage_multiplier_for_level
                    
                    self.employees.append(candidate)
                    self.num_employees += 1
                    total_hired_count += 1
                    hired_for_level_count += 1
                    
                    # print(f"[DEBUG] Firm {self.unique_id}: Hired Person {candidate.unique_id} (Skill: {candidate.skill_level}) as '{job_level}'. Wage: {candidate.wage:.0f}")
            # print(f"[DEBUG] Firm {self.unique_id}: Hired {hired_for_level_count} for job level '{job_level}'. Total firm employees: {self.num_employees}")

        print(f"[INFO] Firm {self.unique_id} ({self.firm_area}): Initial workforce population complete. Target: {target_count}, Actual Hired: {self.num_employees}")

    def fulfill_demand_request(self, units_requested):
        '''
        Attempts to fulfill a demand request from current inventory.
        
        This method is called by household and government agents when they want to purchase
        products from this firm. It updates inventory and tracks sales metrics.
        
        Parameters:
        - units_requested: Number of units the customer wants to buy
        
        Returns:
        - Number of units actually sold/fulfilled (may be less than requested if inventory is low)
        '''

        can_fulfill = min(units_requested, self.inventory)
        
        if can_fulfill > 0:
            self.inventory -= can_fulfill
            self.units_sold_this_step += can_fulfill
            # print(f"[DEBUG] Firm {self.unique_id} fulfilled {can_fulfill} units. Inventory now: {self.inventory}. Requested: {units_requested}")
        # else:
            # print(f"[DEBUG] Firm {self.unique_id} could not fulfill. Requested: {units_requested}, Inventory: {self.inventory}")

        self.total_requested_this_step += units_requested
        return can_fulfill

    def adjust_production(self, sold_units):
        '''
        Adjust production level based on market conditions and firm performance.
        
        This method prevents the vicious cycle that can affect luxury goods by maintaining
        minimum viable production levels. It considers demand-to-inventory ratio and
        sell-through rate to make appropriate adjustments to production capacity utilization.
        
        Parameters:
        - sold_units: Number of units sold in the current step
        '''
        
        # Handle cases with no capacity first
        if self.labor_added_production_capacity <= 0:
            self.production_level = 0.0
            return
            
        # Calculate key market metrics
        demand_to_inventory_ratio = self.average_demand / (self.inventory + 1e-6) # how much demand compared to inventory
        sell_through_rate = sold_units / (self.produced_units + 1e-6) # what percentage of new products are sold
        
        # Set minimum production levels based on firm type to prevent death spiral
        if self.firm_type == "luxury":
            min_production_level = 0.3  # Luxury firms need economies of scale
        else:
            min_production_level = 0.2  # Necessity firms can operate lower
            
        # If we have no demand history yet
        if not self.demand_history or self.average_demand == 0:
            if self.inventory < self.production_capacity * 0.3:
                self.production_level = max(0.7, min_production_level)
            else:
                self.production_level = max(0.5, min_production_level)
            return

        # Main production adjustment logic
        if demand_to_inventory_ratio > 1.5:  # High demand relative to inventory
            self.production_level = min(1.0, self.production_level + 0.1)
        elif demand_to_inventory_ratio > 1.0:  # Moderate demand, but still have some inventory
            self.production_level = min(1.0, self.production_level + 0.05)
        elif sell_through_rate > 0.8:  # Good sales performance
            self.production_level = min(1.0, self.production_level + 0.03)
        elif sell_through_rate < 0.3 and self.inventory > self.average_demand * 2:
            # Poor sales AND high inventory - reduce 
            new_level = self.production_level - 0.3
            self.production_level = max(new_level, min_production_level)
        elif self.inventory > self.average_demand * 3:
            # Very high inventory - more aggressive reduction
            new_level = self.production_level - 0.5
            self.production_level = max(new_level, min_production_level)
            
        # Special handling for luxury firms in crisis
        if (self.firm_type == "luxury" and 
            self.average_demand < self.production_capacity * 0.1 and 
            self.production_level < 0.5):
            # Force minimum viable production to maintain cost structure
            self.production_level = 0.4
            
        # Ensure production level does not exceed 1.0 and does not fall below min_production_level
        self.production_level = min(max(self.production_level, min_production_level), 1.0)

    def adjust_price(self, sold_units, produced_units, cost_per_unit):
        '''
        Adjust product price based on market conditions, demand trends, and costs.
        
        This method implements sophisticated pricing logic that considers inventory levels,
        sales performance, and both short-term and long-term demand trends. It has special
        handling for luxury goods to prevent price spirals during market downturns.
        
        Parameters:
        - sold_units: Number of units sold in the current step
        - produced_units: Number of units produced in the current step
        - cost_per_unit: Current production cost per unit
        '''
        
        if produced_units == 0:
            return
        
        # Key market indicators
        inventory_demand_ratio = self.inventory / (self.total_requested_this_step + 1e-6)  # how much inventory compared to demand
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

        # Enhanced inventory-based pricing for luxury goods
        if self.firm_type == "luxury":
            if inventory_demand_ratio > 3.0:  # Severe oversupply
                market_pressure -= 0.7
            elif inventory_demand_ratio > 2.0:
                market_pressure -= 0.6
            elif inventory_demand_ratio > 1.5:
                market_pressure -= 0.5
            elif inventory_demand_ratio < 0.3:
                market_pressure += 0.6
            elif inventory_demand_ratio < 0.5:
                market_pressure += 0.4
        else:
            # For necessity goods
            if inventory_demand_ratio > 2.0:
                market_pressure -= 0.4
            elif inventory_demand_ratio > 1.5:
                market_pressure -= 0.2
            elif inventory_demand_ratio < 0.5:
                market_pressure += 0.5
            elif inventory_demand_ratio < 0.2:
                market_pressure += 1

        # Sales performance adjustments
        if sell_through_rate < 0.2:  # Very poor sales
            market_pressure -= 0.5
        elif sell_through_rate < 0.4:  # Poor sales
            market_pressure -= 0.3
        elif sell_through_rate > 0.9:
            market_pressure += 0.4

        # Demand trend adjustments
        if short_term_trend < -0.3:  # Sharp recent decline
            market_pressure -= 0.2
        elif short_term_trend < -0.2:
            market_pressure -= 0.1
        elif short_term_trend > 0.2:  # Sharp recent increase
            market_pressure += 0.15

        if long_term_trend < -0.2:  # Sustained significant decline
            market_pressure -= 0.1
        elif long_term_trend < -0.1:  # Sustained decline
            market_pressure -= 0.05
        elif long_term_trend > 0.1:  # Sustained growth
            market_pressure += 0.05

        # Special crisis intervention for luxury goods
        if (self.firm_type == "luxury" and 
            self.average_demand < self.production_capacity * 0.15 and
            sell_through_rate < 0.3):
            market_pressure -= 0.6  # Aggressive price cutting to stimulate demand

        # Cap market_pressure between -1 and 1
        market_pressure = max(-1.0, min(market_pressure, 1.0))

        # Apply more aggressive markup changes for luxury goods in crisis
        if self.firm_type == "luxury" and market_pressure < -0.5:
            markup_change = market_pressure * 0.8  # More aggressive for luxury in crisis
        else:
            markup_change = market_pressure * 0.5  # Original logic

        self.markup += markup_change
        self.markup = max(0.5, self.markup)  # Allow very low markup to break price spirals

        # Update product price
        calculated_price = cost_per_unit * (1 + self.markup)
        
        # More flexible minimum price for luxury goods in crisis
        if (self.firm_type == "luxury" and 
            self.average_demand < self.production_capacity * 0.2):
            # Allow pricing closer to cost during crisis
            flexible_min_price = self.production_cost * 1.02
        else:
            flexible_min_price = self.min_price
            
        self.product_price = max(calculated_price, flexible_min_price)

    def adjust_employees(self):
        '''
        Adjust the number of employees based on profit trends.
        
        This method analyzes the firm's recent profit history to determine whether to hire
        or fire employees. It implements a cooldown mechanism to prevent rapid fluctuations
        in workforce size, and makes decisions based on whether the firm is profitable and
        whether profits are stable, increasing, or decreasing.
        '''
        # Check cooldown - only adjust employees every 2 steps
        if self.employee_adjustment_cooldown > 0:
            self.employee_adjustment_cooldown -= 1
            return

        if len(self.profit_history) < self.profit_history_length:
            # Not enough data to make a decision (need p0, p1, p2, p3)
            return

        # p0 is current profit, p1 is one step ago, p2 is two steps ago, p3 is three steps ago
        p0 = self.profit_history[-1]
        p1 = self.profit_history[-2]
        p2 = self.profit_history[-3]
        p3 = self.profit_history[-4]

        # Use average of the three *past* steps as the reference for current profit p0
        avg_past_3_steps_profit = (p1 + p2 + p3) / 3.0
        
        is_stable = False
        # Handle case where avg_past_3_steps_profit is zero 
        if avg_past_3_steps_profit == 0:
            is_stable = abs(p0) < 1e-6 # Stable if p0 is also near zero
        else:
            # Stable if current profit is within 5% of the average of the *past three* steps' profit
            is_stable = abs(p0 - avg_past_3_steps_profit) < (0.05 * abs(avg_past_3_steps_profit))

        at_a_loss = p0 < 0

        action_taken = "none" # For debugging
        adjustment_made = False  # Track if we made an adjustment

        # Decision tree for employee adjustments
        if at_a_loss:
            # Company is currently losing money
            if p0 < avg_past_3_steps_profit and not is_stable: # Losses are worsening compared to past 3 steps avg
                # print(f"[DEBUG] Firm {self.unique_id} ({self.firm_type}/{self.firm_area}): At a loss. Losses increasing (P0: {p0:.2f}, AvgP1P2P3: {avg_past_3_steps_profit:.2f}). Firing.")
                if self.fire_least_productive():
                    action_taken = "fired (losses increasing)"
                    adjustment_made = True
            elif is_stable: # Losses are stable compared to past 3 steps avg
                # print(f"[DEBUG] Firm {self.unique_id} ({self.firm_type}/{self.firm_area}): At a loss. Losses stable (P0: {p0:.2f}, AvgP1P2P3: {avg_past_3_steps_profit:.2f}). Firing.")
                if self.fire_least_productive():
                     action_taken = "fired (losses stable)"
                     adjustment_made = True
            else: # Losses are improving compared to past 3 steps avg (p0 > avg_past_3_steps_profit), but still p0 < 0
                # print(f"[DEBUG] Firm {self.unique_id} ({self.firm_type}/{self.firm_area}): At a loss, but losses decreasing or turned to profit (P0: {p0:.2f}, AvgP1P2P3: {avg_past_3_steps_profit:.2f}). No change.")
                action_taken = "monitoring (losses decreasing)"
                pass # Do nothing, monitor situation
        else: # Profiting (p0 >= 0)
            if p0 > avg_past_3_steps_profit and not is_stable: # Profits are improving compared to past 3 steps avg
                # print(f"[DEBUG] Firm {self.unique_id} ({self.firm_type}/{self.firm_area}): Profiting. Profits increasing (P0: {p0:.2f}, AvgP1P2P3: {avg_past_3_steps_profit:.2f}). Hiring.")
                if self.hire_new_employee():
                    action_taken = "hired (profits increasing)"
                    adjustment_made = True
            elif is_stable: # Profits are stable compared to past 3 steps avg
                # print(f"[DEBUG] Firm {self.unique_id} ({self.firm_type}/{self.firm_area}): Profiting. Profits stable (P0: {p0:.2f}, AvgP1P2P3: {avg_past_3_steps_profit:.2f}). Hiring.")
                if self.hire_new_employee():
                    action_taken = "hired (profits stable)"
                    adjustment_made = True
            else: # Profits are falling compared to past 3 steps avg (p0 < avg_past_3_steps_profit, but p0 still >= 0)
                # print(f"[DEBUG] Firm {self.unique_id} ({self.firm_type}/{self.firm_area}): Profiting. Profits falling (P0: {p0:.2f}, AvgP1P2P3: {avg_past_3_steps_profit:.2f}). Firing.")
                # This is where you might consider firing if profits are falling, even if positive.
                pass

        # Set cooldown if we made an adjustment - wait 2 steps before next adjustment
        if adjustment_made:
            self.employee_adjustment_cooldown = 1  # Will be decremented next step, so adjustment possible in 2 steps
        
        # if action_taken != "none" and action_taken != "monitoring (losses decreasing)":
        #     print(f"[INFO] Firm {self.unique_id} ({self.firm_type}/{self.firm_area}) - Employee Adjustment: {action_taken}. Profit P0: {p0:.2f}, AvgP1P2P3: {avg_past_3_steps_profit:.2f}, Stable: {is_stable}, Num Employees: {self.num_employees}")
        # elif action_taken == "monitoring (losses decreasing)":
        #     print(f"[INFO] Firm {self.unique_id} ({self.firm_type}/{self.firm_area}) - Employee Adjustment: {action_taken}. Profit P0: {p0:.2f}, AvgP1P2P3: {avg_past_3_steps_profit:.2f}, Num Employees: {self.num_employees}")

    def fire_least_productive(self):
        '''
        Fire the least productive employee from the firm.
        
        This method calculates productivity (skill * labor / wage) for each employee,
        identifies the least productive worker, and terminates their employment.
        The person's status is updated to reflect their unemployment.
        
        Returns:
        - Boolean indicating whether an employee was successfully fired
        '''
        if not self.employees or self.num_employees <= 1: # Cannot fire if no employees or only one left (assuming min 1 employee)
            # print(f"[DEBUG] Firm {self.unique_id}: Cannot fire. Employees: {self.num_employees}")
            return False
        
        # Calculate productivity for each employee in self.employees list
        employee_productivity = []
        for person in self.employees:
            skill_level = person.skill_level
            labor = person.labor
            productivity = (skill_level * labor) / (person.wage + 1e-6)
            employee_productivity.append((productivity, person))
        
        if not employee_productivity:
            # print(f"[DEBUG] Firm {self.unique_id}: No employee productivity list generated from self.employees.")
            return False

        employee_productivity.sort(key=lambda x: x[0]) # Sort by productivity (lowest first)
        
        productivity_score, person_to_fire = employee_productivity[0]
        
        # Update person's employment status
        person_to_fire.employer = None
        person_to_fire.wage = 0
        person_to_fire.job_seeking = True
        
        # Remove from firm's list of employees and update count
        self.employees.remove(person_to_fire)
        self.num_employees -= 1
        
        job_level = person_to_fire.job_level if hasattr(person_to_fire, 'job_level') else "unknown"
        # print(f"[INFO] Firm {self.unique_id} fired Person {person_to_fire.unique_id} (Job: {job_level}, Prod: {productivity_score:.2f}). Remaining employees: {self.num_employees}")
        return True

    def hire_new_employee(self):
        '''
        Hire a new employee with appropriate skills for the firm's area.
        
        This method analyzes the current workforce composition, determines which job level
        is most needed, and then finds and hires the most suitable candidate from the
        available job seekers. It updates the hired person's employment status and the
        firm's employee records.
        
        Returns:
        - Boolean indicating whether an employee was successfully hired
        '''
        
        # Get current employees and their levels from self.employees
        current_mix = {"senior": 0, "mid": 0, "entry": 0}
        
        # Keep track of previously employed people to avoid rehiring them
        if not hasattr(self, 'previous_employees'):
            self.previous_employees = set()
            
        firm_levels = self.min_skill_levels_config.get(self.firm_area, self.min_skill_levels_config["physical"])
        
        # Calculate current workforce composition by job level
        for emp in self.employees: # Iterate over self.employees
            if hasattr(emp, 'job_level') and emp.job_level is not None:
                current_mix[emp.job_level] += 1
            else:
                if emp.skill_level >= firm_levels["senior"]:
                    current_mix["senior"] += 1
                elif emp.skill_level >= firm_levels["mid"]:
                    current_mix["mid"] += 1
                else:
                    current_mix["entry"] += 1
                
        total_current_employees = self.num_employees # Use self.num_employees
        target_mix = self.skill_mix_config.get(self.firm_area, self.skill_mix_config["physical"])
        
        # Determine which job level needs more employees
        differences = {}
        for level in ["senior", "mid", "entry"]:
            current_pct = current_mix[level] / (total_current_employees + 1) if (total_current_employees + 1) > 0 else 0 # Consider new hire
            target_pct = target_mix[level]
            differences[level] = target_pct - current_pct
            
        job_level = max(differences, key=differences.get)
        min_skill_level = firm_levels[job_level]
        matching_skill_type = self.skill_type_matching_config.get(self.firm_area, "physical")
        
        # Find candidates from self.model.available_persons or a similar global list
        # Assuming self.model.available_persons exists and is the source of truth for unemployed persons
        if not hasattr(self.model, 'available_persons'):
            # print(f"[WARNING] Firm {self.unique_id}: model.available_persons not found. Cannot hire.")
            return False

        # Find job seekers from all agents
        available_job_seekers = [p for p in self.model.agents if hasattr(p, 'job_seeking') and p.job_seeking and p.employer is None]

        # Find candidates with matching skills
        matching_candidates = [p for p in available_job_seekers
                               if p.skill_level >= min_skill_level and
                               p.skill_type == matching_skill_type and
                               p.unique_id not in self.previous_employees]
        
        # If no exact matches, relax skill requirements
        candidates_to_consider = matching_candidates
        if not matching_candidates:
            candidates_to_consider = [p for p in available_job_seekers
                                      if p.skill_level >= min_skill_level - 10 and # Relaxed skill level
                                      p.unique_id not in self.previous_employees]
            
        if not candidates_to_consider:
            # print(f"[DEBUG] Firm {self.unique_id}: No suitable candidates found to hire for {job_level} in {self.firm_area}.")
            return False

        # Select from top half of candidates by skill level
        candidates_to_consider.sort(key=lambda p: p.skill_level, reverse=True)
        top_candidate_count = max(1, len(candidates_to_consider) // 2)
        person_to_hire = random.choice(candidates_to_consider[:top_candidate_count])
            
        # Calculate wage based on job level and skill bonus
        base_wage = self.entry_wage * self.wage_multipliers[job_level]
        skill_bonus = person_to_hire.skill_level * 0.03 * base_wage
        offered_wage = base_wage + skill_bonus
            
        # Update person's employment status
        person_to_hire.employer = self
        person_to_hire.wage = offered_wage
        person_to_hire.job_seeking = False
        person_to_hire.job_level = job_level
        
        # Update firm's records
        self.employees.append(person_to_hire) # Add to firm's list
        self.num_employees += 1 # Increment count
        
        # Track previously hired employees to avoid rehiring
        self.previous_employees.add(person_to_hire.unique_id)
        if len(self.previous_employees) > 100: # Keep the set from growing too large
            for _ in range(10):
                if self.previous_employees: # Ensure it's not empty before popping
                    self.previous_employees.pop()
            
        # print(f"[INFO] Firm {self.unique_id} hired Person {person_to_hire.unique_id} as {job_level} (Skill: {person_to_hire.skill_level:.2f}). Total employees: {self.num_employees}")
        return True


    def calculate_total_wage_cost(self):
        '''
        Calculate the total wage costs for all employees.
        
        This method aggregates the wages of all employees currently employed by the firm.
        It is used for financial calculations and production cost determination.
        
        Returns:
        - Total wage cost (float)
        '''
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
        '''
        Calculate the total labor value contributed by all employees.
        
        This internal method determines the additional production capacity provided
        by the firm's workforce. The labor value of each employee contributes to the
        firm's overall production capacity.
        
        Returns:
        - Total labor value (float)
        '''
        employees = [agent for agent in self.model.agents 
                    if hasattr(agent, 'employer') and agent.employer == self]
        
        self.total_labor = 0
        if employees:
            self.total_labor = sum(emp.labor for emp in employees)
        return self.total_labor

    def step(self):
        '''
        Execute one step of the firm's operations in the simulation.
        
        This method handles the firm's complete operational cycle including:
        - Production of goods
        - Calculation of costs and prices
        - Selling products (already handled by fulfill_demand_request)
        - Calculating revenue and profit
        - Paying taxes to government
        - Updating demand and performance metrics
        - Making adjustments to production, pricing, and workforce
        
        The step method is called by the model scheduler at each simulation step.
        '''
        # Update historical prices for 2-step inflation calculation
        self.price_two_steps_ago = self.price_one_step_ago
        self.price_one_step_ago = self.product_price # This product_price is from end of previous step

        # Producing goods and adding them to the inventory
        added_labor = self._calculate_total_labor()
        
        self.labor_added_production_capacity = self.production_capacity + added_labor
        
        self.produced_units = round(self.labor_added_production_capacity * self.production_level)
        self.inventory += self.produced_units

        # Calculate production costs
        wage_costs = self.calculate_total_wage_cost()
        production_costs = self.production_cost * self.produced_units
        self.costs = wage_costs + production_costs
        # print(f"[DEBUG] Firm {self.unique_id} costs: {production_costs}")
        
        # Send demand to intermediary firm 
        intermediary_firm = [a for a in self.model.agents if isinstance(a, IntermediaryFirmAgent)][0]
        # Send demand to intermediary firm
        intermediary_firm.receive_firm_demand(production_costs)

        # Calculate cost per unit for pricing decisions
        cost_per_unit = self.costs / (self.produced_units + 1e-6)

        # Sales have already happened via fulfill_demand_request by Government and Households.
        # self.inventory is already updated.
        # self.units_sold_this_step reflects total sales for this step.
        sold_units = self.units_sold_this_step 
        
        # Calculate revenue from sales
        self.revenue = self.product_price * sold_units

        # Calculate pre-tax profit for the current step
        pre_tax_profit = self.revenue - self.costs
        self.tax_paid_this_step = 0.0 # Reset for the current step's calculation

        # Handle taxes on profitable operations
        if pre_tax_profit > 0:
            # Get amount of revenue from government purchases THIS step
            # GovernmentAgent populates this dict in its step, which runs before FirmAgent's step
            amount_from_gov = self.model.government_agent.government_purchases_from_firms_step.get(self.unique_id, 0)
            
            # Determine the actual taxable profit by excluding direct government revenue
            true_taxable_profit = pre_tax_profit - amount_from_gov
            
            if true_taxable_profit > 0:
                tax_due_this_step = true_taxable_profit * self.model.government_agent.corporate_tax_rate
                self.tax_paid_this_step = tax_due_this_step
                self.profit = pre_tax_profit - tax_due_this_step # Net profit after specific tax
            else:
                # Profit was solely from (or offset by) government purchases, or became a loss after adjustment
                self.profit = pre_tax_profit # No corporate tax due on this
        else:
            # Firm made a loss initially
            self.profit = pre_tax_profit

        # Update firm's capital with profit or loss
        self.capital += self.profit # Add net profit (or loss) to capital
        
        # Calculate unmet demand
        #self.unmet_demand = self.total_requested_this_step - self.units_sold_this_step
        
        # Update the revenue per employee
        self.revenue_per_employee = self.revenue / max(self.num_employees, 1) # Avoid division by zero
        
        # The first step, initialize last_step_revenue_per_emp with current value
        if self.last_step_revenue_per_emp is None:
            self.last_step_revenue_per_emp = self.revenue_per_employee
        
        # Update demand history with actual units sold
        self.demand_history.append(self.total_requested_this_step)
        if len(self.demand_history) > self.demand_history_length:
            self.demand_history.pop(0)  # remove oldest entry
        
        # Calculate moving average with weights (more recent demand counts more)
        if self.demand_history: # Check if not empty
            if len(self.demand_history) == self.demand_history_length:
                self.average_demand = sum(d * w for d, w in zip(self.demand_history, self.demand_averaging_weights))
            else:
                # If we don't have enough history yet, use simple average
                self.average_demand = sum(self.demand_history) / len(self.demand_history)
        else:
            self.average_demand = 0 # No history, no average demand

        # Make adjustments to business operations based on performance
        self.adjust_price(sold_units, self.produced_units, cost_per_unit)
        self.adjust_production(sold_units)
        self.adjust_employees()

        # Update historical metrics
        self.last_step_revenue_per_emp = self.revenue_per_employee
        
        # Reset step-specific counters
        self.demand_for_tracking = self.total_requested_this_step # Storing for data collection if needed
        self.units_sold_this_step = 0
        self.total_requested_this_step = 0
        
        # Update profit history
        self.profit_history.append(self.profit)
        if len(self.profit_history) > self.profit_history_length:
            self.profit_history.pop(0)
