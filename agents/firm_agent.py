import mesa
import numpy as np
import pandas as pd

class FirmAgent(mesa.Agent):
    def __init__(self, model, product, production_capacity, product_price, production_cost, average_wage, num_employees, inventory, firm_type="necessity", production_level=1):
        super().__init__(model)

        self.product = product
        self.firm_type = firm_type
        self.production_capacity = production_capacity
        self.production_level = production_level
        self.product_price = product_price
        self.production_cost = production_cost
        self.average_wage = average_wage
        self.num_employees = num_employees
        self.inventory = inventory
        self.revenue = 0
        self.costs = 0
        self.profit = 0
        self.demand_received = 0


    def receive_demand(self, units):
        self.demand_received += units
    
    def step(self):
        self.inventory += round(self.production_capacity*self.production_level)
        self.costs = self.num_employees*self.average_wage + self.production_cost

        sold_units = min(self.demand_received, self.inventory)

        if self.inventory <= self.demand_received:
            deficit = self.demand_received - self.inventory
            self.inventory -= self.inventory
            # print(f"SUPPLY DEFICIT OF {deficit}!!" , end=" ")
            if self.production_level < 1:
                if (self.production_level + 0.1) < 1:
                    self.production_level + 0.1
                elif (self.production_level + 0.1) > 1:
                    self.production_level = 1
        else:
            self.inventory -= sold_units

        self.revenue = self.product_price*sold_units
        self.profit = self.revenue - self.costs
        print(f"Demand received: {self.demand_received} ")
        self.demand_received = 0

        



        

    
        # print(f"[{self.unique_id}], Product: {self.product}, Revenue: {self.revenue},  Costs: {self.costs}, Profit: {self.profit}, Inventory: {self.inventory}")

