import mesa
import numpy as np
import pandas as pd
import random

class IntermediaryFirmAgent(mesa.Agent):
    def __init__(self, model, num_employees):
        super().__init__(model)
        self.num_employees = num_employees
        self.demand_received_from_firms = 0
        self.revenue = 0
        self.capital = 0

    def receive_firm_demand(self, cost):
        """Record demand received from firms."""
        self.demand_received_from_firms += cost



    def step(self):
        print(f"[INTERMEDIARY] Demand received from firms: {self.demand_received_from_firms}")
        self.revenue = self.demand_received_from_firms
        wage_per_employee = self.revenue / self.num_employees

        #TODO after fixing employees initialization, money should be payed as wage to employees
