# Transport Optimization - Gurobi + PyQt6

Desktop application to solve the classic transportation problem in operations research, using the Gurobi optimizer and a PyQt6 graphical interface.

## Description

The **transportation problem** is a linear optimization problem that consists of minimizing the total cost of transporting products from multiple factories to multiple warehouses, while respecting capacity and demand constraints.

This application allows you to:
- Define the number of factories and warehouses
- Enter the production capacity of each factory
- Enter the demand for each warehouse
- Define the unit transportation cost matrix
- Solve the optimization problem
- Visualize the optimal solution
- Export results to CSV

## Features

-  Intuitive and professional graphical interface
-  Flexible configuration (1-10 factories and warehouses)
-  Optimal resolution with Gurobi
-  Supply/demand balance verification
-  Detailed display of optimal flows
-  Minimum total cost calculation
-  Export results to CSV format
-  Tables with scroll areas for large instances

## Prerequisites

### Required Software
- **Python 3.8+**
- **Gurobi Optimizer** (academic or commercial license)
- **PyQt6**

### Installation

1. **Clone the project**
```bash
git clone https://github.com/your-username/transport-optimizer.git
cd transport-optimizer
```

2. **Install Python dependencies**
```bash
pip install PyQt6 gurobipy
```

3. **Gurobi Configuration**

You must have a valid Gurobi license. To obtain a free academic license:
- Visit [Gurobi Academic License](https://www.gurobi.com/academia/academic-program-and-licenses/)
- Download and install Gurobi
- Activate your license with `grbgetkey`

## Usage

### Launch the application
```bash
python transport_app.py
```

### User Guide

1. **Problem Configuration**
   - Define the number of factories (sources)
   - Define the number of warehouses (destinations)
   - Click on "Create Tables"

2. **Data Entry**
   - Enter the production capacity of each factory (supply)
   - Enter the demand for each warehouse
   - Fill in the unit transportation cost matrix

3. **Resolution**
   - Click on "Solve Problem"
   - The application verifies that the problem is balanced (total supply = total demand)
   - The optimal solution is displayed automatically

4. **Results Review**
   - View the optimal transportation flows
   - Check the minimum total cost
   - Export results to CSV if needed

## Technologies Used

- **Python**: Programming language
- **PyQt6**: Framework for graphical interface
- **Gurobi**: Linear optimization solver
- **CSV**: Results export format


