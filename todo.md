# Yaniv's 
1) Output Data Structure:
** File name **
output_simulation_unique_ID.csv
** Columns **
- `timestep`: int. The timestep this data is recorded at.
- `node_idx` = Node ID: int
- `cash` = Cash: float. Liquid cash of node at present time (t+0). I guess should be possible to define as max(recievables_(t+0)-payables_(t+0),0).
- `tier` = Tier: int. Shortest path from market node
- `power`: int. Power of node.
- `stock` = Inventory: int. Number of stores material units
- `unfilled` = Unfilled Orders: int. Stored number of orders that node still has to fill.
- `issued` = Issue orders: int. Stored number of orders that node has issued that have not been fulfilled.
- `buy_amount` = New Orders: int. Number of new orders issued by that node at that given timestep.
- `is_bankrupt` = Bankrupt: bool. Denotes if a node has become bankrupt and hence removed from the simulation.
- `receivable` = Receivables: float. Recievables at timestep t0
- `payable` = Payables: float. Payables at timestep t0
a) Note, payables should be invoice payables + debt + operation fee
- `invoice_payables` = Invoice Payables: float. Invoice payables at time t0
a) note: invoice payable should be payables - debt
- `debt` = Debt: float. Debt payables, which is the principal debt plus interest. Sum of this produces the debt variable, used to check if the node is above the bank mandate.

** Simulation Parameters ** 
(eg/ mean_demand, invoice_repayment_term, medium_company_sale_skew, etc.)

2) Analysis Pipeline:
N/A




# Liming's Update
## To-Do list:
1. create output.py for handling output related business logics;
2. create visualisation.py;
3. batch analysis

## Output
The output for each simulation includes two files: outputs_`sim_id`.csv and configs_`sim_id`.yaml

### Output column header: 
- timestep
- node_idx
- tier
- is_bankrupt
- stock
- cash
- receivable
- payable
- debt
- order_from
- buy_amount
- unfilled
