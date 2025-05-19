# Economyxim: Agent-Based Economic Simulation

## Overview

Economyxim is an agent-based model (ABM) that simulates a mixed economy with interactions between firms, households, and government. The simulation focuses on emergent market behaviors such as price adjustments, inventory management, employment decisions, and consumer spending patterns. By modeling microeconomic behaviors of individual agents, the simulation explores how these lead to macroeconomic outcomes like market equilibrium, price adjustments, and inventory dynamics.

## Features
- **Firm Agents**: Simulate individual firms that:
  - Produce goods based on market demand
  - Adjust prices in response to inventory levels and market trends
  - Manage inventory levels based on demand history
  - Make staffing decisions based on efficiency metrics
  - Track and respond to both short-term and long-term demand trends

- **Market Dynamics**:
  - Price adjustments based on inventory levels and demand trends
  - Production level optimization using weighted moving averages
  - Employee management based on revenue per employee
  - Different behaviors for necessity vs. luxury goods

- **Data Analysis**:
  - Time series analysis of inventory levels
  - Distribution analysis of firm metrics
  - Correlation analysis between different economic indicators
  - Visualization tools for key metrics

## Project Structure
```
economyxim/
├── agents/
│   ├── __init__.py
│   ├── firm_agent.py           # Defines firm behavior (production, pricing, employment)
│   ├── household_agent.py      # Defines household behavior (consumption, labor supply)
│   ├── government_agent.py     # Defines government behavior (taxes, subsidies, public goods)
│   ├── intermediary_firm_agent.py # Defines intermediary firm behavior (e.g. wholesale)
│   └── person_agent.py         # Defines individual person agents, forming parts of households
├── data/
│   ├── analysis.py             # Scripts for data analysis and visualization
│   └── saved_data/             # Directory for storing simulation output data
├── model/
│   ├── __init__.py
│   └── economy_model.py        # Core Mesa model definition, orchestrates agent interactions
├── results/                    # Default output directory for analysis, plots, reports
├── utils/
│   ├── __init__.py
│   ├── compute_gini.py         # Utility for Gini coefficient calculation
│   ├── create_run_folder.py    # Utility to create output folders for runs
│   ├── generate_summary_report.py # Utility to generate summary reports
│   ├── save_agent_data.py      # Utility to save agent-specific data
│   └── save_model_data.py      # Utility to save model-level data
├── .git/                       # Git version control files
├── .cursor/                    # Cursor IDE specific files
├── venv/                       # Python virtual environment (if used and checked in)
├── .gitignore                  # Specifies intentionally untracked files that Git should ignore
├── mesa-readthedocs-io-en-latest.pdf # Mesa framework documentation
├── prompts.md                  # Contains prompts (likely for LLM interactions or experiments)
├── README.md                   # This file
├── requirements.txt            # Project dependencies
├── run.py                      # Main script to run the simulation
└── TODO.md                     # To-do list for project development
```

## Key Components

Firms use a sophisticated decision-making process that includes:

- **Production Management**:
  - Adjusts production levels based on inventory and demand
  - Uses weighted moving averages to predict future demand
  - Different inventory targets for necessity vs. luxury goods

- **Pricing Strategy**:
  - Dynamic price adjustments based on market conditions
  - Considers inventory levels, sell-through rates, and demand trends
  - Different profit margin ranges for necessity vs. luxury goods

- **Employee Management**:
  - Adjusts staffing based on revenue per employee
  - Maintains minimum staffing levels
  - Responds to efficiency metrics

### Data Analysis
The simulation includes comprehensive data analysis tools:

- **Time Series Analysis**:
  - Tracks inventory levels over time
  - Analyzes demand trends
  - Visualizes key metrics

- **Distribution Analysis**:
  - Examines firm size distribution
  - Analyzes profit margin distributions
  - Studies employee count patterns

- **Correlation Analysis**:
  - Identifies relationships between different metrics
  - Analyzes market dynamics
  - Studies firm performance patterns

## Usage

### Requirements
- Python 3.12 or higher

### Running the Simulation
When you run the simulation, you will be prompted to enter a name for the run. This name will be used to create folders in `data/saved_data/` and `results/` for storing the output.
```python
python run.py
```

### Configuration
The primary simulation parameters are currently defined within the `EconomicSimulationModel` class in `model/economy_model.py`. Key configurable aspects (hardcoded for now) include:
- **Simulation Duration**: Fixed at 60 steps in `run.py`.
- **Number and Types of Agents**:
    - `num_persons`: Initial pool of person agents (e.g., 30000).
    - `n_households`: Number of household agents (e.g., 1000).
    - Number of firms by type (e.g., `n_physical`, `n_service`) and their specific parameters (production capacity, markup, etc.).
    - Number of `IntermediaryFirmAgent` and `GovernmentAgent` (currently 1 each).
- **Initial Conditions**:
    - Household income tax rate.
    - Initial employee targets, entry wages, production costs for firms.
    - Number of people per household (randomized within a range).

To change these, you would currently need to modify `model/economy_model.py` or `run.py` for the duration. Future development could involve moving these to a configuration file or command-line arguments.

### Output
The simulation generates:
- CSV files with detailed metrics
- Visualization plots in the results folder
- Analysis reports

## Dependencies
The project relies on several Python libraries. Key dependencies include:
- Mesa (Agent-Based Modeling framework)
- NumPy (Numerical computing)
- Pandas (Data analysis)
- Matplotlib (Visualization)
- Seaborn (Statistical visualization)

For a full list of dependencies and their versions, please see `requirements.txt`.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
[Your chosen license - e.g., MIT License, Apache 2.0. If you need help choosing, visit https://choosealicense.com/]

## Acknowledgments
- Built using the Mesa framework for agent-based modeling
- Inspired by economic theory and market dynamics

