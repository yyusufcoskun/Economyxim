import os

def save_agent_data(model):
    data = model.datacollector.get_agent_vars_dataframe()
    
    output_path = os.path.join("data", "saved_data", "agent_data.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data.to_csv(output_path, index=True)
    print("Simulation complete. Data saved to", output_path)
    return data
