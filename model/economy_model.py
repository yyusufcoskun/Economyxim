import mesa
import numpy as np
import pandas as pd
from agents import GovernmentAgent

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

    def step(self):
        self.datacollector.collect(self)
        self.agents.do("step")