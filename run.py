import mesa
from model import EconomicSimulationModel


def main():
    # Create an instance of the model with 100 agents.
    model = EconomicSimulationModel()
    
    # Run the model for 50 steps.
    for _ in range(150):
        model.step()
    
    # Optionally, display some of the collected data.
    # data = model.datacollector.get_agent_vars_dataframe()
    # print(data.head())

if __name__ == "__main__":
    main()