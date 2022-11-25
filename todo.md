# Yaniv's 
1) Output Data Structure:

**Columns:**
- Simulation_unique_ID: unsure
- Timestep: int. The timestep this data is recorded at.
- `node_idx` = Node ID: int
- `cash` = Cash: float. Liquid cash of node at present time (t+0). I guess should be possible to define as max(recievables_(t+0)-payables_(t+0),0).
- `tier` = Tier: int. Shortest path from market node
- Power: int. Power of node.
- `stock` = Inventory: int. Number of stores material units
- Unfilled Orders: int. Stored number of orders that node still has to fill.
- Issued Orders: int. Stored number of orders that node has issued that have not been fulfilled.
- `is_bankrupt` = Bankrupt: bool. Denotes if a node has become bankrupt and hence removed from the simulation. 
--       I presume the system should be declared broken at the timestep
- `receivable` = Receivables: not sure, would need to figure out how to aggregate this.
- `payable` = Payables: not sure, would need to figure out how to aggregate this.
- `invoice_payables` = Invoice Payables
- `debt` = Debt: 
- Nodal Stored Variables (Eg/ cash, inventory, orders, etc.)
- Simulation Parameters (eg/ mean_demand, invoice_repayment_term, medium_company_sale_skew, etc.)

 `node_idx`,
 `tier`,
`is_bankrupt`,
 `stock`,
`cash`,
`receivable`,
`payable`,
`debt`,
`order_from`,
`buy_amount`,
`unfilled`

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
