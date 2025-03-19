import os

def save_agent_data(model):
    agent_data = model.datacollector.get_agent_vars_dataframe()

    output_folder = os.path.join("data", "saved_data")
    os.makedirs(output_folder, exist_ok=True)

    # Save full agent data
    full_path = os.path.join(output_folder, "agent_data.csv")
    agent_data.to_csv(full_path, index=True)
    print(f"Full agent data saved to: {full_path}")

    # Reset index to flat format
    agent_data_reset = agent_data.reset_index()

    # ✅ Filter by FirmType and IncomeBracket — NOT by class
    firm_data = agent_data_reset[agent_data_reset["FirmType"].notnull()]
    household_data = agent_data_reset[agent_data_reset["IncomeBracket"].notnull()]

    # Save separately
    firm_path = os.path.join(output_folder, "firm_data.csv")
    household_path = os.path.join(output_folder, "household_data.csv")

    firm_data.to_csv(firm_path, index=False)
    print(f"Firm data saved to: {firm_path}")

    household_data.to_csv(household_path, index=False)
    print(f"Household data saved to: {household_path}")

    return agent_data
