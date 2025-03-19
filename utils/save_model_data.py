import os

# def save_model_data(model):
#     data = model.datacollector.get_model_vars_dataframe()
    
#     output_path = os.path.join("data", "saved_data", "model_data.csv")
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
#     data.to_csv(output_path, index=True)
#     print("Simulation complete. Data saved to", output_path)
#     return data


def save_model_data(model, output_folder):
    data = model.datacollector.get_model_vars_dataframe()
    path = os.path.join(output_folder, "model_data.csv")
    data.to_csv(path, index=True)
    print("Model data saved to:", path)
    return data