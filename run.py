import mesa
from model import EconomicSimulationModel
from utils import save_model_data
from data import analysis  # import your analysis function



def main():
    model = EconomicSimulationModel()
    
    # Run the model for 150 steps.
    for _ in range(150):
        model.step()
    
    data = save_model_data(model) # As data grows, you're going to need to change this. Look at ChatGPT's response, search for "single flat CSV"

    analysis.reserves_public_graph(data)

if __name__ == "__main__":
    main()