import os

def save_model_data(model):
    # Retrieve data from the model's data collector
    data = model.datacollector.get_model_vars_dataframe()
    
    # Define the output path relative to the project root.
    output_path = os.path.join("data", "saved_data", "model_data.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data.to_csv(output_path, index=True)
    print("Simulation complete. Data saved to", output_path)
    return data
