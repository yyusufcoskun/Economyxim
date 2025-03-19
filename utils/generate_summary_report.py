import os
import pandas as pd

def generate_summary_report(model, output_folder):
    model_df = model.datacollector.get_model_vars_dataframe()
    agent_df = model.datacollector.get_agent_vars_dataframe()

    summary = {}

    # Model-level summary (latest values)
    latest_step = model_df.index.max()
    latest_data = model_df.loc[latest_step]
    summary["Final Reserves"] = latest_data.get("Reserves", None)
    summary["Final Public Spending"] = latest_data.get("Yearly Public Spending", None)

    # Firm-level summary
    agent_df_reset = agent_df.reset_index()
    firm_data = agent_df_reset[agent_df_reset["FirmType"].notnull()]
    if not firm_data.empty:
        summary["Average Firm Profit"] = firm_data["Profit"].mean()

    # Household-level summary
    household_data = agent_df_reset[agent_df_reset["IncomeBracket"].notnull()]
    if not household_data.empty:
        summary["Average Household Welfare"] = household_data["Welfare"].mean()

    summary_path = os.path.join(output_folder, "summary_report.csv")
    pd.Series(summary).to_csv(summary_path)
    print("Summary report saved to:", summary_path)
