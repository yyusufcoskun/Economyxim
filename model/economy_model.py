import mesa
import numpy as np
import pandas as pd
from agents import GovernmentAgent

class EconomicSimulationModel(mesa.Model):
    def __init__(self):
        super().__init__()
        GovernmentAgent.create_agents(model=self, n=1)

    def step(self):
        self.agents.do("step")