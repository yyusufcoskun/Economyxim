import mesa
from model import EconomicSimulationModel
from utils import *
from data import analysis


def main():
    model = EconomicSimulationModel()
    
    # Run the model for 150 steps.
    for _ in range(150):
        model.step()
    

    output_data_folder = create_run_folder("testing_demand", base_path="data/saved_data")
    output_results_folder = create_run_folder("testing_demand", base_path="results")

    model_data = save_model_data(model, output_data_folder) # As data grows, you're going to need to change this. Look at ChatGPT's response, search for "single flat CSV"
    agent_data = save_agent_data(model, output_data_folder)
    generate_summary_report(model, output_data_folder)

    analysis.create_distribution_plot(
        df=agent_data,
        groupby_col="FirmType",
        value_col="Profit",
        plot_type="box",
        title="Distribution of Firm Profits by Type",
        xlabel="Firm Type",
        ylabel="Profit",
        figsize=(10, 6),
        grid=True,
        filename="firm_profits_distribution.png",
        results_folder=output_results_folder
    )

    analysis.create_plot(
        df=model_data,
        plot_type="line", 
        columns=["Reserves", "Yearly Public Spending"],
        title="Government Reserves and Public Spending Over Time",
        xlabel="Time Step",
        ylabel="Amount",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="government_finances.png",
        results_folder=output_results_folder
    )

    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="Inventory",
        title="Average Inventory Levels by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Average Inventory",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_inventory_levels.png",
        results_folder=output_results_folder
    )

    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="Profit",
        title="Average Profit Levels by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Average Profit",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_profit_levels.png",
        results_folder=output_results_folder
    )

    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="ProductPrice",
        title="Average Product Price Levels by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Average Product Price",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_product_price_levels.png",
        results_folder=output_results_folder
    )

    
if __name__ == "__main__":
    main()