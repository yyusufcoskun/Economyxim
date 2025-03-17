import mesa
from model import EconomicSimulationModel
from utils import save_model_data
from utils import save_agent_data
from data import analysis


def main():
    model = EconomicSimulationModel()
    
    # Run the model for 150 steps.
    for _ in range(150):
        model.step()
    
    model_data = save_model_data(model) # As data grows, you're going to need to change this. Look at ChatGPT's response, search for "single flat CSV"
    agent_data = save_agent_data(model)

    analysis.line_chart(
        df=model_data,
        columns=["Reserves", "Yearly Public Spending"],
        title="Reserves and Public Spending Over Time",
        ylabel="Value (Billions)",
        filename="reserves_public_spending.png"
    )
    
    analysis.bar_chart(
        df=agent_data,
        groupby_col="FirmType",
        value_col="Profit",
        agg_func="mean",
        title="Average Profit by Firm Type",
        xlabel="Firm Type",
        ylabel="Average Profit",
        filename="avg_profit_by_firm_type.png"
    )

if __name__ == "__main__":
    main()