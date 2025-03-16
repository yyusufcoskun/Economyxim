import mesa
import numpy as np
import pandas as pd
import random
from agents import GovernmentAgent
from agents import FirmAgent

class EconomicSimulationModel(mesa.Model):
    def __init__(self):
        super().__init__()

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Reserves": lambda m: m.government_agent.reserves,
                "Yearly Public Spending": lambda m: m.government_agent.yearly_public_spending,
            }
        )
        self.government_agent = GovernmentAgent.create_agents(model=self, n=1)[0]
        
        # --- Necessity Firms (30) ---
        n_necessity = 30
        FirmAgent.create_agents(
            model=self,
            n=n_necessity,
            firm_type="necessity",
            product=[f"NecessityProduct_{i}" for i in range(n_necessity)],
            production_capacity=[random.randint(5000, 10000) for _ in range(n_necessity)],
            product_price=[random.uniform(10.0, 30.0) for _ in range(n_necessity)],
            production_cost=[random.uniform(2.0, 5.0) for _ in range(n_necessity)],
            average_wage=[random.randint(35000, 45000) for _ in range(n_necessity)],
            num_employees=[random.randint(40, 80) for _ in range(n_necessity)],
            inventory=[random.randint(2000, 10000) for _ in range(n_necessity)],
            production_level=[random.uniform(0.9, 1) for _ in range(n_necessity)]
        )

        # --- Luxury Firms (20) ---
        n_luxury = 20
        FirmAgent.create_agents(
            model=self,
            n=n_luxury,
            firm_type="luxury",
            product=[f"LuxuryProduct_{i}" for i in range(n_luxury)],
            production_capacity=[random.randint(40, 80) for _ in range(n_luxury)],
            product_price=[random.uniform(100.0, 150.0) for _ in range(n_luxury)],
            production_cost=[random.uniform(30.0, 50.0) for _ in range(n_luxury)],
            average_wage=[random.randint(70000, 100000) for _ in range(n_luxury)],
            num_employees=[random.randint(5, 30) for _ in range(n_luxury)],
            inventory=[random.randint(50, 400) for _ in range(n_luxury)],
            production_level=[random.uniform(0.3, 1) for _ in range(n_luxury)]
        )

        

    def step(self):
        self.datacollector.collect(self)
        self.agents.do("step")