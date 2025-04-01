import mesa
import numpy as np
import pandas as pd
import random


class FirmAgent(mesa.Agent):
    def __init__(self, model, product, production_capacity, profit_margin, 
                 production_cost, average_wage, num_employees, 
                 firm_type="necessity", production_level=1):
        super().__init__(model)
        # print(f"[DEBUG] Assigned production_level for {self.unique_id}: {production_level}")

        self.product = product
        self.firm_type = firm_type
        self.production_capacity = production_capacity
        self.profit_margin = profit_margin
        self.production_level = production_level
        self.product_price = 0 # CHECK
        self.production_cost = production_cost
        self.average_wage = average_wage
        self.num_employees = num_employees
        self.inventory = 0  # CHECK
        
        self.revenue = 0
        self.costs = 0
        self.profit = 0
        self.revenue_per_employee = 0
        

        self.last_step_profit =  None # profit from the previous step
        self.demand_received = 0 # demand received from households
        self.last_step_revenue_per_emp = None

        self.demand_history = []
        self.demand_history_length = 5  # how many steps to track
        self.average_demand = 0 # track average demand (will be calculated)
    

    def receive_demand(self, units):
        """Record demand received from households."""
        self.demand_received += units  # used by household

    def adjust_production(self, sold_units):
        """Adjust production level based on inventory and demand trends."""
        if len(self.demand_history) == 0:
            return  # Not enough history yet
        
        # Are sales increasing or decreasing?
        if len(self.demand_history) >= 2:
            recent_trend = self.demand_history[-1] / (self.demand_history[-2] + 1e-6) - 1  # percentage change
        else:
            recent_trend = 0

        # Target inventory based on weighted average demand
        if self.firm_type == "necessity":
            # Necessity firms keep more inventory
            target_inventory = self.average_demand * 1.5
        else:
            # Luxury firms keep less inventory
            target_inventory = self.average_demand * 1.1

        # Adjust target based on trend
        if recent_trend > 0.1:  # Growing demand
            target_inventory *= 1.2
        elif recent_trend < -0.1:  # Shrinking demand
            target_inventory *= 0.8

        # Calculate how far we are from target
        inventory_gap = target_inventory - self.inventory
        
        # Adjust production level based on gap
        if inventory_gap > 0:  # Need more inventory
            if self.inventory < self.average_demand:  # Very low inventory
                self.production_level *= 1.3
            else:  # Moderate increase
                self.production_level *= 1.1
        else:  # Too much inventory
            if self.inventory > target_inventory * 1.5:  # Way too much
                self.production_level *= 0.3
            else:  # Moderate decrease
                self.production_level *= 0.7

        # Keep production level within bounds
        self.production_level = min(max(self.production_level, 0.1), 1.0)

    def adjust_price(self, sold_units, produced_units):
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
            market_pressure -= 0.3  # price wants to drop
        elif inventory_demand_ratio > 1.5:
            market_pressure -= 0.2
        elif inventory_demand_ratio < 0.5:  # demand is twice as much as inventory
            market_pressure += 0.2  # price wants to rise so that stock lasts
        elif inventory_demand_ratio < 0.2:  # demand is 5 times as much as inventory
            market_pressure += 0.3

        # Adjust market pressure based on sales performance
        if sell_through_rate < 0.4:  # poor sales
            market_pressure -= 0.2
        elif sell_through_rate > 0.9:
            market_pressure += 0.2

        # Adjust market pressure based on demand trends
        if short_term_trend < -0.2:  # Sharp recent decline
            market_pressure -= 0.15
        elif short_term_trend > 0.2:  # Sharp recent increase
            market_pressure += 0.15

        if long_term_trend < -0.1:  # Sustained decline
            market_pressure -= 0.1
        elif long_term_trend > 0.1:  # Sustained growth
            market_pressure += 0.1

        # Apply market pressure to profit margin
        price_adjustment = 1.0 + market_pressure
        self.profit_margin *= price_adjustment  # so if market pressure is 1, profit margin will be profit margin * 2

        '''
        # make sure profit margin stays realistic
        if self.firm_type == "luxury":
            self.profit_margin = max(min(self.profit_margin, 0.5), 0.2)  # 20-50% margin
        else:  # necessity
            self.profit_margin = max(min(self.profit_margin, 0.25), 0.05)  # 5-25% margin
        '''

        # Update product price
        cost_per_unit = self.costs / (produced_units + 1e-6)
        self.product_price = max(cost_per_unit * (1 + self.profit_margin), 1.0)  # make sure price isn't lower than cost

    def adjust_employees(self):
        """Adjust number of employees based on revenue per employee."""
        '''
        if self.last_step_profit is None:
            return
        profit_delta = self.profit - self.last_step_profit
        change = int(self.num_employees * profit_delta * 0.00001)
        self.num_employees = max(1, self.num_employees + change) # Prevent employees dropping down to 0
        '''

        if self.last_step_revenue_per_emp is None:
            return

        if self.last_step_revenue_per_emp > self.revenue_per_employee:
            self.num_employees -= 1
        else:
            self.num_employees += 1

        self.num_employees = max(1, self.num_employees)

    def step(self):
        """Execute one step of the firm's operations."""
        # Producing goods and adding them to the inventory
        produced_units = round(self.production_capacity * self.production_level)
        self.inventory += produced_units

        # Calculate costs
        self.costs = self.num_employees * self.average_wage + self.production_cost * produced_units
        cost_per_unit = (self.costs / produced_units)
        self.product_price = cost_per_unit * (1 + self.profit_margin)

        # Sell products
        sold_units = min(self.demand_received, self.inventory)
        self.revenue = self.product_price * sold_units
        self.inventory -= sold_units

        # Profit
        self.profit = self.revenue - self.costs
        self.revenue_per_employee = self.revenue / self.num_employees

        '''
        if self.last_step_profit is None:
            self.last_step_profit = self.profit
            
        # Take action based on profit change
        if self.last_step_profit < self.profit:
            # Deciding which action to take
            if self.inventory > self.demand_received:
                self.adjust_production()  # Reduce oversupply
            elif self.product_price > 1.5 * self.production_cost:
                self.adjust_price()  # Price is too high, drop it
            else:
                self.adjust_employees()  # Last resort: layoff
        else: # Profit is growing, increase 
            if self.demand_received > self.inventory:
                self.adjust_production()
            elif self.product_price < 1.5 * self.production_cost:
                self.adjust_price()
            else:
                self.adjust_employees()
        '''
        

        # self.last_step_profit = self.profit # Save this step's profit

        # Make adjustments
        self.adjust_price(sold_units, produced_units)
        self.adjust_production(sold_units)
        self.adjust_employees()

        # Update historical metrics
        self.last_step_revenue_per_emp = self.revenue_per_employee

        # Update demand history
        self.demand_history.append(self.demand_received)
        if len(self.demand_history) > self.demand_history_length:
            self.demand_history.pop(0)  # remove oldest entry
        
        # Calculate moving average with weights (more recent demand counts more)
        weights = [0.1, 0.15, 0.2, 0.25, 0.3]  # weights sum to 1, more recent = higher weight
        if len(self.demand_history) == self.demand_history_length:
            self.average_demand = sum(d * w for d, w in zip(self.demand_history, weights))
        else:
            # If we don't have enough history yet, use simple average
            self.average_demand = sum(self.demand_history) / len(self.demand_history)

        # Reset demand for next step
        self.demand_received = 0
        
        # Print debug information
        print(f"[Firm {self.unique_id}], Units Produced: {produced_units}, "
              f"Units Sold: {sold_units}, Inventory: {self.inventory}, "
              f"Cost Per Unit: {cost_per_unit}, Price: {self.product_price}, "
              f"Revenue: {self.revenue}, Costs: {self.costs}, "
              f"Profit: {self.profit}")

