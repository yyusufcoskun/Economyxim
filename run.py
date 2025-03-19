import mesa
from model import EconomicSimulationModel
from utils import *
# from utils import save_agent_data
from data import analysis


def main():
    model = EconomicSimulationModel()
    
    # Run the model for 150 steps.
    for _ in range(150):
        model.step()
    

    output_data_folder = create_run_folder("test 1", base_path="data/saved_data")
    output_results_folder = create_run_folder("test_1", base_path="results")


    # model_data = save_model_data(model) 
    # agent_data = save_agent_data(model)

    model_data = save_model_data(model, output_data_folder) # As data grows, you're going to need to change this. Look at ChatGPT's response, search for "single flat CSV"
    agent_data = save_agent_data(model, output_data_folder)
    generate_summary_report(model, output_data_folder)


    analysis.line_chart(
        df=model_data,
        columns=["Reserves", "Yearly Public Spending"],
        title="Reserves and Public Spending Over Time",
        ylabel="Value (Billions)",
        filename="reserves_public_spending.png",
        results_folder = output_results_folder
    )
    
    analysis.bar_chart(
        df=agent_data,
        groupby_col="FirmType",
        value_col="Profit",
        agg_func="mean",
        title="Average Profit by Firm Type",
        xlabel="Firm Type",
        ylabel="Average Profit",
        filename="avg_profit_by_firm_type.png",
        results_folder = output_results_folder

    )

    analysis.bar_chart(
        df=agent_data,
        groupby_col="IncomeBracket",
        value_col="Welfare",
        agg_func="mean",
        title="Average Welfare by Income Bracket",
        xlabel="Income Bracket",
        ylabel="Welfare",
        filename="avg_welfare_by_income_bracket.png",
        results_folder = output_results_folder

    )

if __name__ == "__main__":
    main()