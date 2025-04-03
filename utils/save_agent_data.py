import os

def save_agent_data(model, output_folder):
    agent_data = model.datacollector.get_agent_vars_dataframe()
    agent_data.to_csv(os.path.join(output_folder, "agent_data.csv"), index=True)

    agent_data_reset = agent_data.reset_index()
    firm_data = agent_data_reset[agent_data_reset["FirmType"].notnull()]
    household_data = agent_data_reset[agent_data_reset["IncomeBracket"].notnull()]
    person_data = agent_data_reset[agent_data_reset["SkillLevel"].notnull()]

    firm_data.to_csv(os.path.join(output_folder, "firm_data.csv"), index=False)
    household_data.to_csv(os.path.join(output_folder, "household_data.csv"), index=False)
    person_data.to_csv(os.path.join(output_folder, "person_data.csv"), index=False)

    print("Agent data (firm + household + person) saved to:", output_folder)
    return agent_data