import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
from typing import List, Union, Optional, Dict, Any
import numpy as np


current_dir = os.path.dirname(os.path.abspath(__file__))

def create_plot(
    df: pd.DataFrame,
    plot_type: str = "line",
    columns: Optional[List[str]] = None,
    groupby_col: Optional[str] = None,
    value_col: Optional[str] = None,
    agg_func: Union[str, callable] = "mean",
    title: Optional[str] = None,
    xlabel: str = "Step",
    ylabel: Optional[str] = None,
    figsize: tuple = (12, 6),
    colors: Optional[List[str]] = None,
    grid: bool = True,
    legend: bool = True,
    show_values: bool = True,
    rotation: int = 0,
    filename: str = "plot.png",
    results_folder: Optional[str] = None,
    **kwargs
) -> None:
    """
    Create a flexible plotting function that supports multiple chart types and customization options.

    Parameters:
    -----------
    df : pd.DataFrame
        Input data to plot
    plot_type : str
        Type of plot to create ('line', 'bar', 'scatter', 'box', 'violin', 'heatmap')
    columns : List[str], optional
        Columns to plot for line/scatter plots
    groupby_col : str, optional
        Column to group by for bar/box/violin plots
    value_col : str, optional
        Column containing values to plot
    agg_func : str or callable
        Aggregation function for grouped data
    title : str, optional
        Plot title
    xlabel : str
        X-axis label
    ylabel : str, optional
        Y-axis label
    figsize : tuple
        Figure size (width, height)
    colors : List[str], optional
        Custom colors for the plot
    grid : bool
        Whether to show grid
    legend : bool
        Whether to show legend
    show_values : bool
        Whether to show value labels on bars
    rotation : int
        Rotation angle for x-axis labels
    filename : str
        Output filename
    results_folder : str, optional
        Folder to save the plot (should be provided from run.py)
    **kwargs
        Additional arguments to pass to the specific plot function
    """
    if df is None or df.empty:
        print("No data provided for plotting.")
        return

    if results_folder is None:
        print("Warning: No results folder provided. Please provide results_folder from run.py")
        return
    
    os.makedirs(results_folder, exist_ok=True)

    # Create figure
    plt.figure(figsize=figsize)

    # Plot based on type
    if plot_type == "line":
        if columns is None:
            raise ValueError("columns parameter is required for line plots")
        
        for i, col in enumerate(columns):
            if col in df.columns:
                color = colors[i] if colors and i < len(colors) else None
                plt.plot(df.index, df[col], label=col, color=color, **kwargs)
            else:
                print(f"⚠ Column '{col}' not found in DataFrame. Skipping.")

        if "xticks" not in kwargs:
            max_step = df.index.max() + 10
            plt.xticks(range(0, max_step + 1, 10))

    elif plot_type == "bar":
        if groupby_col is None or value_col is None:
            raise ValueError("groupby_col and value_col parameters are required for bar plots")
        
        grouped = df.groupby(groupby_col)[value_col].agg(agg_func)
        bars = plt.bar(grouped.index, grouped.values, color=colors[0] if colors else "#69b3a2", **kwargs)
        
        if show_values:
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2, yval, f"{yval:.2f}", 
                        ha="center", va="bottom")

    elif plot_type == "scatter":
        if columns is None or len(columns) != 2:
            raise ValueError("columns parameter must contain exactly 2 columns for scatter plots")
        
        plt.scatter(df[columns[0]], df[columns[1]], 
                   color=colors[0] if colors else None, **kwargs)

    elif plot_type == "box":
        if groupby_col is None or value_col is None:
            raise ValueError("groupby_col and value_col parameters are required for box plots")
        
        sns.boxplot(data=df, x=groupby_col, y=value_col, **kwargs)

    elif plot_type == "violin":
        if groupby_col is None or value_col is None:
            raise ValueError("groupby_col and value_col parameters are required for violin plots")
        
        sns.violinplot(data=df, x=groupby_col, y=value_col, **kwargs)

    elif plot_type == "heatmap":
        if columns is None:
            raise ValueError("columns parameter is required for heatmap plots")
        
        correlation_matrix = df[columns].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', **kwargs)

    # Customize plot
    plt.xlabel(xlabel)
    plt.ylabel(ylabel or "Value")
    plt.title(title)
    
    if grid:
        plt.grid(True)
    
    if legend and plot_type in ["line", "scatter"]:
        plt.legend()
    
    plt.xticks(rotation=rotation)

    # Save plot
    file_path = os.path.join(results_folder, filename)
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {file_path}")

def create_time_series_plot(
    df: pd.DataFrame,
    columns: List[str],
    window: int = 1,
    title: Optional[str] = None,
    xlabel: str = "Step",
    ylabel: Optional[str] = None,
    figsize: tuple = (12, 6),
    colors: Optional[List[str]] = None,
    grid: bool = True,
    legend: bool = True,
    filename: str = "time_series.png",
    results_folder: Optional[str] = None,
    **kwargs
) -> None:
    """
    Create a time series plot with optional moving average.

    Parameters:
    -----------
    df : pd.DataFrame
        Input data with time index
    columns : List[str]
        Columns to plot
    window : int
        Window size for moving average (1 for no smoothing)
    title : str, optional
        Plot title
    xlabel : str
        X-axis label
    ylabel : str, optional
        Y-axis label
    figsize : tuple
        Figure size
    colors : List[str], optional
        Custom colors
    grid : bool
        Whether to show grid
    legend : bool
        Whether to show legend
    filename : str
        Output filename
    results_folder : str, optional
        Folder to save the plot (should be provided from run.py)
    **kwargs
        Additional arguments to pass to create_plot
    """
    if window > 1:
        df = df.rolling(window=window).mean()
    
    create_plot(
        df=df,
        plot_type="line",
        columns=columns,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        figsize=figsize,
        colors=colors,
        grid=grid,
        legend=legend,
        filename=filename,
        results_folder=results_folder,
        **kwargs
    )

def create_distribution_plot(
    df: pd.DataFrame,
    groupby_col: str,
    value_col: str,
    plot_type: str = "box",
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    figsize: tuple = (10, 6),
    colors: Optional[List[str]] = None,
    grid: bool = True,
    filename: str = "distribution.png",
    results_folder: Optional[str] = None,
    **kwargs
) -> None:
    """
    Create a distribution plot (box, violin, or bar) for grouped data.

    Parameters:
    -----------
    df : pd.DataFrame
        Input data
    groupby_col : str
        Column to group by
    value_col : str
        Column containing values
    plot_type : str
        Type of distribution plot ('box', 'violin', or 'bar')
    title : str, optional
        Plot title
    xlabel : str, optional
        X-axis label
    ylabel : str, optional
        Y-axis label
    figsize : tuple
        Figure size
    colors : List[str], optional
        Custom colors
    grid : bool
        Whether to show grid
    filename : str
        Output filename
    results_folder : str, optional
        Folder to save the plot (should be provided from run.py)
    **kwargs
        Additional arguments to pass to create_plot
    """
    if plot_type not in ["box", "violin", "bar"]:
        raise ValueError("plot_type must be one of: box, violin, bar")
    
    create_plot(
        df=df,
        plot_type=plot_type,
        groupby_col=groupby_col,
        value_col=value_col,
        title=title,
        xlabel=xlabel or groupby_col,
        ylabel=ylabel or value_col,
        figsize=figsize,
        colors=colors,
        grid=grid,
        filename=filename,
        results_folder=results_folder,
        **kwargs
    )

def create_correlation_plot(
    df: pd.DataFrame,
    columns: List[str],
    title: Optional[str] = None,
    figsize: tuple = (10, 8),
    filename: str = "correlation.png",
    results_folder: Optional[str] = None,
    **kwargs
) -> None:
    """
    Create a correlation heatmap for specified columns.

    Parameters:
    -----------
    df : pd.DataFrame
        Input data
    columns : List[str]
        Columns to include in correlation matrix
    title : str, optional
        Plot title
    figsize : tuple
        Figure size
    filename : str
        Output filename
    results_folder : str, optional
        Folder to save the plot (should be provided from run.py)
    **kwargs
        Additional arguments to pass to create_plot
    """
    create_plot(
        df=df,
        plot_type="heatmap",
        columns=columns,
        title=title,
        figsize=figsize,
        filename=filename,
        results_folder=results_folder,
        **kwargs
    )

def create_time_series_by_type(
    df: pd.DataFrame,
    value_col: str,
    type_col: str = "FirmType",
    filename: str = "time_series.png",
    results_folder: Optional[str] = None,
    title: Optional[str] = None,
    xlabel: str = "Time Step",
    ylabel: Optional[str] = None,
    figsize: tuple = (12, 6),
    grid: bool = True,
    legend: bool = True,
    **kwargs
) -> None:
    """
    Create a time series plot showing values over time for different types of agents.

    Parameters:
    -----------
    df : pd.DataFrame
        Input data with time index
    value_col : str
        Column containing values to plot
    type_col : str
        Column containing agent types to group by
    filename : str
        Output filename
    results_folder : str, optional
        Folder to save the plot
    title : str, optional
        Plot title
    xlabel : str
        X-axis label
    ylabel : str, optional
        Y-axis label
    figsize : tuple
        Figure size
    grid : bool
        Whether to show grid
    legend : bool
        Whether to show legend
    **kwargs
        Additional arguments to pass to create_plot
    """
    if df is None or df.empty:
        print("No data provided for plotting.")
        return

    if results_folder is None:
        print("Warning: No results folder provided. Please provide results_folder from run.py")
        return

    # Transform data for time series
    df_reset = df.reset_index()
    type_data = df_reset[df_reset[type_col].notnull()]
    values_by_type = type_data.pivot_table(
        values=value_col,
        index="Step",
        columns=type_col,
        aggfunc="mean"
    )

    # Create the plot
    create_plot(
        df=values_by_type,
        plot_type="line",
        columns=values_by_type.columns.tolist(),
        title=title or f"Average {value_col} by {type_col} Over Time",
        xlabel=xlabel,
        ylabel=ylabel or f"Average {value_col}",
        figsize=figsize,
        grid=grid,
        legend=legend,
        filename=filename,
        results_folder=results_folder,
        **kwargs
    )

