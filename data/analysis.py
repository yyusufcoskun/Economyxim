import pandas as pd
import matplotlib.pyplot as plt
import os


current_dir = os.path.dirname(os.path.abspath(__file__))

def reserves_public_graph(df): 
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    results_folder = os.path.join(project_root, "results")
    os.makedirs(results_folder, exist_ok=True)


    plt.figure(figsize=(12, 6))

    plt.plot(df.index, df["Reserves"], label="Reserves")
    plt.plot(df.index, df["Yearly Public Spending"], label="Yearly Public Spending")

    max_step = df.index.max() + 10
    plt.xticks(range(0, max_step + 1, 10))

    plt.xlabel("Step")
    plt.ylabel("Value (Billions)")
    plt.title("Yearly Public Spending and Reserves Over Time")
    plt.legend()
    plt.grid(True)
    
    file_path = os.path.join(results_folder, "reserves-public spending graph.png")
    plt.savefig(file_path)
    print(f"Plot saved to {file_path}")


