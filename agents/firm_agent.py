import mesa
import numpy as np
import pandas as pd
import random


class FirmAgent(mesa.Agent):
    def __init__(self, model, product, production_capacity, profit_margin, production_cost, average_wage, num_employees, firm_type="necessity", production_level=1):
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
        self.inventory = 0 # CHECK
        self.revenue = 0
        self.costs = 0
        self.profit = 0
        self.revenue_per_employee = 0
        

        self.last_step_profit =  None # Profit from the previous step
        self.demand_received = 0 # Demand received from households
        self.last_step_revenue_per_emp = None

        self.production_aggressiveness = random.uniform(0.05, 0.2) # How aggressively the firm will change it's production level multiplier
        self.pricing_aggressiveness = random.uniform(0.05, 0.2) # How aggressively the firm will change it's price level multiplier




    def receive_demand(self, units):
        self.demand_received += units # Used by household
    


    def adjust_production(self):
        '''
        if self.last_step_profit is None:
            self.last_step_profit = self.profit
            return
        profit_delta = self.profit - self.last_step_profit # Calculate profit change from previous step
        # print(f"[{self.unique_id}] Before Adj Prod Level: {self.production_level:.2f}, Profit Δ: {profit_delta:.2f}")
        adjustment = (profit_delta / (abs(self.last_step_profit) + 1e-6)) * self.production_aggressiveness # Percentage profit change * production change aggressivenes = production level increase percentage
        adjustment = max(adjustment, -0.05)  # No more than 5% reduction per step
        self.production_level *= (1 + adjustment)
        self.production_level = min(max(self.production_level, 0.1), 1.0) # Cap production level between 0.1 and 1.0 
        '''

        inventory_ratio = self.inventory / (self.production_capacity + 1e-6)

        if inventory_ratio > 2.0:
            self.production_level *= 0.93  # Reduce 
        elif inventory_ratio < 0.5:
            self.production_level *= 1.07  # Increase 

        self.production_level = min(max(self.production_level, 0.1), 1.0)
    

    def adjust_price(self, sold_units, produced_units):
        '''
        if self.last_step_profit is None:
            return
        profit_delta = self.profit - self.last_step_profit
        adjustment = (profit_delta / (abs(self.last_step_profit) + 1e-6)) * self.pricing_aggressiveness
        self.product_price *= (1 + adjustment)
        self.product_price = max(self.product_price, 1.0) # Cap price floor
        '''

        if produced_units == 0:
            return

        sell_ratio = sold_units / produced_units

        if sell_ratio < 0.4:
            self.profit_margin *= 0.95  # Lower price
        elif sell_ratio > 0.9:
            self.profit_margin *= 1.05  # Raise price

        self.product_price = max(self.product_price, 1.0)

    def adjust_employees(self):
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
        
        # Producing goods and adding them to the inventory
        produced_units = round(self.production_capacity*self.production_level)
        self.inventory += produced_units

        # Calculate costs
        self.costs = self.num_employees*self.average_wage + self.production_cost*produced_units
        cost_per_unit = (self.costs/produced_units)
        self.product_price = cost_per_unit*(1 + self.profit_margin)

        # Sell products
        sold_units = min(self.demand_received, self.inventory)
        self.revenue = self.product_price*sold_units
        self.inventory -= sold_units

        # Profit
        self.profit = self.revenue - self.costs
        self.revenue_per_employee = self.revenue/self.num_employees
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


        self.adjust_production()
        self.adjust_price(sold_units, produced_units)
        self.adjust_employees()

        self.last_step_revenue_per_emp = self.revenue_per_employee
        self.demand_received = 0 # Reset household demand for this step
        


        # print(f"[Firm {self.unique_id}] Price: {self.product_price:.2f}, Prod Level: {self.production_level:.2f}, Employees: {self.num_employees}, Profit: {self.profit:.2f}")


    
        print(f"[Firm {self.unique_id}], Units Produced: {produced_units}, Units Sold: {sold_units}, Inventory: {self.inventory}, Cost Per Unit: {cost_per_unit}, Price: {self.product_price}, Revenue: {self.revenue},  Costs: {self.costs}, Profit: {self.profit}, ")

