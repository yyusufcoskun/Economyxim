import mesa
import numpy as np
import pandas as pd
import random
from agents import GovernmentAgent
from agents import FirmAgent
from agents import HouseholdAgent

class EconomicSimulationModel(mesa.Model):
    def __init__(self):
        super().__init__()

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Reserves": lambda m: m.government_agent.reserves,
                "Yearly Public Spending": lambda m: m.government_agent.yearly_public_spending,
            },
            agent_reporters= {
                 # Firm agent fields
                "FirmType": lambda a: getattr(a, "firm_type", None),
                "Profit": lambda a: getattr(a, "profit", None),

                # Household agent fields
                "IncomeBracket": lambda a: getattr(a, "income_bracket", None),
                "NumPeople": lambda a: getattr(a, "num_people", None),
                "SpendRatio": lambda a: getattr(a, "spend_ratio", None),
                "IncomeTaxRate": lambda a: getattr(a, "income_tax_rate", None),
                "PostTaxIncome": lambda a: getattr(a, "total_income_posttax", None),
                "HouseholdExpense": lambda a: getattr(a, "total_household_expense", None),
                "HouseholdSavings": lambda a: getattr(a, "total_household_savings", None),
                "HealthLevel": lambda a: getattr(a, "health_level", None),
                "Welfare": lambda a: getattr(a, "welfare", None)
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
            profit_margin=0.1,
            production_cost=[random.uniform(2.0, 5.0) for _ in range(n_necessity)],
            average_wage=[random.randint(20000, 35000) for _ in range(n_necessity)],
            num_employees=[random.randint(40, 80) for _ in range(n_necessity)],
            # inventory=[random.randint(1000, 50000) for _ in range(n_necessity)],
            production_level=[random.uniform(0.7, 1) for _ in range(n_necessity)]
        )

        # --- Luxury Firms (20) ---
        n_luxury = 20
        FirmAgent.create_agents(
            model=self,
            n=n_luxury,
            firm_type="luxury",
            product=[f"LuxuryProduct_{i}" for i in range(n_luxury)],
            production_capacity=[random.randint(400, 800) for _ in range(n_luxury)],
            profit_margin=0.4,
            production_cost=[random.uniform(30.0, 50.0) for _ in range(n_luxury)],
            average_wage=[random.randint(70000, 100000) for _ in range(n_luxury)],
            num_employees=[random.randint(5, 30) for _ in range(n_luxury)],
            # inventory=[random.randint(50, 400) for _ in range(n_luxury)],
            production_level=[random.uniform(0.5, 1) for _ in range(n_luxury)]
        )


        n_households = 1000
        HouseholdAgent.create_agents(
            model=self,
            n=n_households,
            income_bracket=[random.choice(["low", "middle", "high"]) for _ in range(n_households)],
            num_people=[random.randint(1, 5) for _ in range(n_households)],
            spend_ratio=[round(random.uniform(0.4, 1.0), 2) for _ in range(n_households)],
            income_tax_rate=0.15  # Same for all for now, so one value is fine
        )

        

    def step(self):
        self.datacollector.collect(self)
        self.agents.do("step")