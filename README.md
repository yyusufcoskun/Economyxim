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
│   ├── firm_agent.py      # Firm behavior implementation
│   └── household_agent.py # Household behavior implementation
├── data/
│   ├── analysis.py        # Data analysis and visualization
│   └── data_collector.py  # Data collection and processing
├── run.py                 # Main simulation runner
└── README.md             # This file
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
```python
python run.py
```

### Configuration
The simulation can be configured through various parameters in `run.py`:
- Number of firms
- Firm types (necessity vs. luxury)
- Initial conditions
- Simulation duration

### Output
The simulation generates:
- CSV files with detailed metrics
- Visualization plots in the results folder
- Analysis reports

## Dependencies
- Mesa (Agent-Based Modeling framework)
- NumPy (Numerical computing)
- Pandas (Data analysis)
- Matplotlib (Visualization)
- Seaborn (Statistical visualization)

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
[Your chosen license]

## Acknowledgments
- Built using the Mesa framework for agent-based modeling
- Inspired by economic theory and market dynamics

