1) Output Data Structure:
Columns:
- Simulation_unique_ID
- Node_ID
- Tier
- Nodal Stored Variables (Eg/ cash, inventory, orders, etc.)
- Simulation Parameters (eg/ mean_demand, invoice_repayment_term, medium_company_sale_skew, etc.)

2) Analysis Pipeline:
N/A


# Liming's Update
## To-Do list:
1. create output.py for handling output related business logics;
2. create visualisation.py;
3. batch analysis

The output for each simulation includes two files: outputs_`sim_id`.csv and configs_`sim_id`.yaml

## column header: 
- timestep
- node_idx
- tier
- stock
- cash
- receivable
- payable
- debt
- order_from
- buy_amount
- unfilled
