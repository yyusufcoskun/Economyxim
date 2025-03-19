import os
from datetime import datetime

def create_run_folder(scenario_name=None, base_path="data/saved_data"):
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
    folder_name = f"run_{timestamp}"
    if scenario_name:
        folder_name += f"_{scenario_name}"
    path = os.path.join(base_path, folder_name)
    os.makedirs(path, exist_ok=True)
    return path
