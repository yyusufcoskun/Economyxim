import pandas as pd
import matplotlib.pyplot as plt
import os


current_dir = os.path.dirname(os.path.abspath(__file__))

def line_chart(df, columns, title=None, xlabel="Step", ylabel=None, filename="line_chart.png", results_folder=None):
    """
    General-purpose line chart function.

    Parameters:
    - df (DataFrame): The model-level data to plot.
    - columns (list): List of column names to plot (e.g., ["Reserves", "Yearly Public Spending"]).
    - title (str): Title of the chart.
    - xlabel (str): Label for x-axis (default: "Step").
    - ylabel (str): Label for y-axis (default: "Value").
    - filename (str): File name to save the plot (saved in 'results/' folder).
    """
    if df is None or df.empty:
        print("No model data available for analysis.")
        return

    if results_folder is None:
        results_folder = os.path.join(os.path.abspath(os.path.join(current_dir, "..")), "results")
    
    os.makedirs(results_folder, exist_ok=True)

    plt.figure(figsize=(12, 6))
    for col in columns:
        if col in df.columns:
            plt.plot(df.index, df[col], label=col)
        else:
            print(f"⚠ Column '{col}' not found in DataFrame. Skipping.")

    max_step = df.index.max() + 10
    plt.xticks(range(0, max_step + 1, 10))

    plt.xlabel(xlabel)
    plt.ylabel(ylabel if ylabel else "Value")
    plt.title(title if title else f"{', '.join(columns)} Over Time")
    plt.legend()
    plt.grid(True)

    file_path = os.path.join(results_folder, "reserves-public spending graph.png")
    plt.savefig(file_path)
    print(f"Plot saved to {file_path}")


def bar_chart(df, groupby_col, value_col, agg_func="mean", title=None, xlabel=None, ylabel=None, filename="bar_chart.png", results_folder=None):
    """
    General bar chart function for grouped data.

    Parameters:
    - df (DataFrame): Data.
    - groupby_col (str): Column name to group by (e.g., 'FirmType').
    - value_col (str): Column to aggregate and plot (e.g., 'Profit').
    - agg_func (str or callable): Aggregation function ('mean', 'sum', 'count', etc. or a custom lambda).
    - title (str): Chart title.
    - xlabel (str): X-axis label.
    - ylabel (str): Y-axis label.
    - filename (str): Name of file to save chart to (saved in 'results/' folder).
    """
    if df is None or df.empty:
        print("No data provided for bar chart.")
        return
    
    if results_folder is None:
        results_folder = os.path.join(os.path.abspath(os.path.join(current_dir, "..")), "results")

    os.makedirs(results_folder, exist_ok=True)

    grouped = df.groupby(groupby_col)[value_col].agg(agg_func)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(grouped.index, grouped.values, color="#69b3a2")
    plt.title(title or f"{agg_func.title()} of {value_col} by {groupby_col}")
    plt.xlabel(xlabel or groupby_col)
    plt.ylabel(ylabel or f"{agg_func.title()} of {value_col}")
    plt.grid(axis="y")

    # Adding value labels
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f"{yval:.2f}", ha="center", va="bottom")

    file_path = os.path.join(results_folder, filename)
    plt.savefig(file_path)
    print(f"Bar chart saved to {file_path}")

