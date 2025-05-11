import mesa
from model import EconomicSimulationModel
from utils import *
from data import analysis
import pandas as pd
import os


def main():
    model = EconomicSimulationModel()
    run_name = input("Enter a name for this simulation run: ")
    # Run the model for 60 steps.
    for _ in range(60):
        model.step()
    
    output_data_folder = create_run_folder(run_name, base_path="data/saved_data")
    output_results_folder = create_run_folder(run_name, base_path="results")

    model_data = save_model_data(model, output_data_folder) # TODO As data grows, you're going to need to change this. Look at ChatGPT's response, search for "single flat CSV"
    agent_data = save_agent_data(model, output_data_folder)
    generate_summary_report(model, output_data_folder)

    # Create income bracket distribution chart
    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="AgentID",
        type_col="IncomeBracket",
        title="Number of Households by Income Bracket Over Time",
        xlabel="Time Step",
        ylabel="Number of Households",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="household_income-brackets.png",
        results_folder=output_results_folder,
        aggfunc="count"
    )

    # Create wealth bracket distribution chart
    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="AgentID", # Counting households
        type_col="WealthBracket", # Grouping by wealth bracket
        title="Number of Households by Wealth Bracket Over Time",
        xlabel="Time Step",
        ylabel="Number of Households",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="household_wealth-brackets.png",
        results_folder=output_results_folder,
        aggfunc="count"
    )

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
        filename="firm_profits-distribution.png",
        results_folder=output_results_folder
    )

    analysis.create_plot(
        df=model_data,
        plot_type="line", 
        columns=["Reserves", "Step Public Spending"],
        title="Government Reserves and Public Spending Over Time",
        xlabel="Time Step",
        ylabel="Amount",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="government_finances.png",
        results_folder=output_results_folder
    )

    # Add GDP graph
    analysis.create_plot(
        df=model_data,
        plot_type="line", 
        columns=["GDP"],
        title="Gross Domestic Product (GDP) Over Time",
        xlabel="Time Step",
        ylabel="GDP",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="government_gdp.png",
        results_folder=output_results_folder
    )

    # Add unemployment rate graph
    analysis.create_plot(
        df=model_data,
        plot_type="line", 
        columns=["Unemployment Rate"],
        title="Unemployment Rate Over Time",
        xlabel="Time Step",
        ylabel="Unemployment Rate (%)",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="government_unemployment-rate.png",
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
        filename="firm_inventory-levels.png",
        results_folder=output_results_folder
    )

    # Add new graph for total inventory
    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="Inventory",
        title="Total Inventory by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Total Inventory",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_total-inventory-levels.png",
        results_folder=output_results_folder,
        aggfunc="sum"
    )

    # Add new graph for average unmet demand
    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="UnmetDemand",
        title="Average Unmet Demand by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Average Unmet Demand",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_average-unmet-demand.png",
        results_folder=output_results_folder,
        aggfunc="mean"  # Explicitly using mean, though it's the default
    )

    # Add new graph for total unmet demand
    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="UnmetDemand",
        title="Total Unmet Demand by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Total Unmet Demand",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_total-unmet-demand.png",
        results_folder=output_results_folder,
        aggfunc="sum"
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
        filename="firm_profit-levels.png",
        results_folder=output_results_folder
    )

    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="Revenue",
        title="Average Revenue Levels by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Average Revenue",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_revenue-levels.png",
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
        filename="firm_product-price-levels.png",
        results_folder=output_results_folder
    )
    
    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="SkillLevel",
        type_col="SkillType",  
        title="Average Skill Level by Skill Type Over Time",
        xlabel="Time Step",
        ylabel="Average Skill Level",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="person_skill-level-by-type.png",
        results_folder=output_results_folder
    )

    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="IsEmployed",  # 1 if employed, 0 if not
        type_col="JobLevel",     
        title="Employment by Job Level Over Time",
        xlabel="Time Step",
        ylabel="Number Employed",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="person_job-level-employment.png",
        results_folder=output_results_folder,
        aggfunc="sum"
    )

    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="Markup",  
        type_col="FirmType",    
        title="Average Markup by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Markup",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_markup-by-type.png",
        results_folder=output_results_folder
    )

    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="ProducedUnits",  
        type_col="FirmType",    
        title="Units Produced by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Units Produced",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_units-produced-by-type.png",
        results_folder=output_results_folder
    )

    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="ProductionLevel",  
        type_col="FirmType",    
        title="Production Level by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Production Level",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_production-level-by-type.png",
        results_folder=output_results_folder
    )

    # Add new graph for average demand over time
    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="DemandReceived",  
        type_col="FirmType",    
        title="Average Demand Received by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Average Demand",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_average-demand-by-type.png",
        results_folder=output_results_folder
    )

    # Add new graph for average capital by firm type
    analysis.create_time_series_by_type(
        df=agent_data,
        value_col="Capital",  
        type_col="FirmType",    
        title="Average Capital by Firm Type Over Time",
        xlabel="Time Step",
        ylabel="Average Capital",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="firm_average-capital-by-type.png",
        results_folder=output_results_folder,
        aggfunc="mean" 
    )

    # Add new graph for average total household savings
    household_data = agent_data.reset_index()[agent_data.reset_index()["TotalHouseholdSavings"].notnull()]
    analysis.create_plot(
        df=household_data,
        plot_type="line",
        columns=["TotalHouseholdSavings"],
        title="Average Total Household Savings Over Time",
        xlabel="Time Step",
        ylabel="Average Savings",
        figsize=(12, 6),
        grid=True,
        legend=True,
        filename="household_average-savings.png",
        results_folder=output_results_folder
    )


    
if __name__ == "__main__":
    main()